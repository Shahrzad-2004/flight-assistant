import sqlite3
from datetime import datetime
from pathlib import Path

from db_crypto import encrypt_text, decrypt_text, is_encrypted


DATABASE_PATH = Path(__file__).parent / "flight_assistant.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id INTEGER,
                role TEXT NOT NULL
                    CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # مهاجرت برای دیتابیس‌های قدیمی‌تری که ستون user_id را ندارند
        existing_columns = [
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(conversations)"
            ).fetchall()
        ]

        if "user_id" not in existing_columns:
            connection.execute(
                "ALTER TABLE conversations ADD COLUMN user_id INTEGER"
            )

        _migrate_conversation_meta(connection)

        connection.commit()


# وضعیت هر گفتگو (پین / آرشیو / عنوان دلخواه) در جدول جداگانه‌ی
# conversation_meta نگه‌داری می‌شود، نه داخل جدول conversations؛
# چون conversations یک ردیف به‌ازای «هر پیام» دارد و اگر پین/آرشیو
# روی هر پیام ذخیره می‌شد، پیام‌های جدید مقدار پیش‌فرض می‌گرفتند.
# کلید جدول (session_id, owner_id) است تا وضعیت هر کاربر مستقل باشد.
# owner_id برای کاربر لاگین‌شده همان user_id است و برای مهمان 0
# (آی‌دی کاربران از 1 شروع می‌شود، پس تداخلی پیش نمی‌آید).
GUEST_OWNER_ID = 0
MAX_TITLE_LENGTH = 100

_META_COLUMNS = {
    "is_pinned": "INTEGER NOT NULL DEFAULT 0",
    "is_archived": "INTEGER NOT NULL DEFAULT 0",
    "custom_title": "TEXT",
}


def _migrate_conversation_meta(connection):
    """ساخت امن جدول وضعیت گفتگوها؛ چند بار اجرا شدنش بی‌خطر است و
    هیچ داده‌ی قبلی را تغییر یا حذف نمی‌کند."""

    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversation_meta (
            session_id TEXT NOT NULL,
            owner_id INTEGER NOT NULL DEFAULT 0,
            is_pinned INTEGER NOT NULL DEFAULT 0,
            is_archived INTEGER NOT NULL DEFAULT 0,
            custom_title TEXT,
            PRIMARY KEY (session_id, owner_id)
        )
    """)

    # اگر جدول از قبل با ساختار ناقص وجود داشت، فقط ستون‌های کم را اضافه کن
    meta_columns = [
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(conversation_meta)"
        ).fetchall()
    ]

    for column_name, column_definition in _META_COLUMNS.items():
        if column_name not in meta_columns:
            connection.execute(
                f"ALTER TABLE conversation_meta "
                f"ADD COLUMN {column_name} {column_definition}"
            )


def _owner_id(user_id: int | None) -> int:
    return GUEST_OWNER_ID if user_id is None else user_id


def _is_allowed(
    session_id: str,
    user_id: int | None,
    allowed_session_ids
) -> bool:
    """کاربر لاگین‌شده با user_id کنترل می‌شود. مهمان‌ها همگی user_id=NULL
    دارند، پس فقط شناسه‌هایی مجازند که همین نشست خودش ساخته است.
    اگر لیست مجاز داده نشود، دسترسی مهمان بسته است (fail-closed)."""

    if user_id is not None:
        return True

    return (
        allowed_session_ids is not None
        and session_id in allowed_session_ids
    )


def _session_exists(connection, session_id: str, user_id: int | None) -> bool:
    """آیا این گفتگو واقعاً متعلق به همین کاربر (یا مهمان) است؟"""

    if user_id is None:
        row = connection.execute(
            "SELECT 1 FROM conversations "
            "WHERE session_id = ? AND user_id IS NULL LIMIT 1",
            (session_id,)
        ).fetchone()
    else:
        row = connection.execute(
            "SELECT 1 FROM conversations "
            "WHERE session_id = ? AND user_id = ? LIMIT 1",
            (session_id, user_id)
        ).fetchone()

    return row is not None


def _update_meta(
    session_id: str,
    user_id: int | None,
    assignments: str,
    params: tuple,
    allowed_session_ids=None
) -> bool:
    """به‌روزرسانی وضعیت یک گفتگو؛ فقط اگر گفتگو مال همین کاربر باشد."""

    if not _is_allowed(session_id, user_id, allowed_session_ids):
        return False

    with get_connection() as connection:

        if not _session_exists(connection, session_id, user_id):
            return False

        owner_id = _owner_id(user_id)

        connection.execute(
            "INSERT OR IGNORE INTO conversation_meta "
            "(session_id, owner_id) VALUES (?, ?)",
            (session_id, owner_id)
        )

        connection.execute(
            f"UPDATE conversation_meta SET {assignments} "
            f"WHERE session_id = ? AND owner_id = ?",
            (*params, session_id, owner_id)
        )

        connection.commit()

    return True


# پین کردن / برداشتن پین یک گفتگو
def set_session_pinned(
    session_id: str,
    pinned: bool,
    user_id: int | None = None,
    allowed_session_ids=None
) -> bool:
    return _update_meta(
        session_id, user_id, "is_pinned = ?", (1 if pinned else 0,),
        allowed_session_ids
    )


# آرشیو کردن / خارج کردن از آرشیو (پیام‌ها هیچ‌وقت حذف نمی‌شوند).
# گفتگوی آرشیوشده پین هم نمی‌ماند تا بعد از خروج از آرشیو عادی برگردد.
def set_session_archived(
    session_id: str,
    archived: bool,
    user_id: int | None = None,
    allowed_session_ids=None
) -> bool:
    if archived:
        return _update_meta(
            session_id, user_id, "is_archived = 1, is_pinned = 0", (),
            allowed_session_ids
        )

    return _update_meta(
        session_id, user_id, "is_archived = 0", (), allowed_session_ids
    )


# تغییر عنوان گفتگو؛ عنوان خالی پذیرفته نمی‌شود
def rename_session(
    session_id: str,
    new_title: str,
    user_id: int | None = None,
    allowed_session_ids=None
) -> bool:
    clean_title = " ".join((new_title or "").split())[:MAX_TITLE_LENGTH]

    if not clean_title:
        return False

    return _update_meta(
        session_id, user_id, "custom_title = ?", (encrypt_text(clean_title),),
        allowed_session_ids
    )


def save_message(session_id: str, role: str, content: str, user_id: int | None = None):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO conversations (
                session_id,
                user_id,
                role,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                user_id,
                role,
                encrypt_text(content),
                datetime.now().isoformat()
            )
        )

        connection.commit()


def load_messages(
    session_id: str,
    user_id: int | None = None,
    allowed_session_ids=None
):
    if not _is_allowed(session_id, user_id, allowed_session_ids):
        return []

    with get_connection() as connection:

        if user_id is None:
            rows = connection.execute(
                """
                SELECT role, content
                FROM conversations
                WHERE session_id = ? AND user_id IS NULL
                ORDER BY id ASC
                """,
                (session_id,)
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT role, content
                FROM conversations
                WHERE session_id = ? AND user_id = ?
                ORDER BY id ASC
                """,
                (session_id, user_id)
            ).fetchall()

    return [
        {
            "role": role,
            "content": decrypt_text(content)
        }
        for role, content in rows
    ]


#   فهرست گفتگوهای ذخیره‌ شده‌ی همین کاربر (یا مهمان).
#   archived=False (پیش‌فرض): گفتگوهای فعال؛ ابتدا پین‌شده‌ها و بعد بقیه،
#   هر گروه از جدیدترین به قدیمی‌ترین.
#   archived=True: فقط گفتگوهای آرشیوشده.
def list_sessions(
    user_id: int | None = None,
    archived: bool = False,
    allowed_session_ids=None
):

    # مهمان بدون لیست مجاز هیچ گفتگویی نمی‌بیند
    if user_id is None and not allowed_session_ids:
        return []

    with get_connection() as connection:

        if user_id is None:
            owner_filter = "WHERE c.user_id IS NULL"
        else:
            owner_filter = "WHERE c.user_id = ?"

        params = [_owner_id(user_id)]

        if user_id is not None:
            params.append(user_id)

        params.append(1 if archived else 0)

        rows = connection.execute(
            f"""
            SELECT
                c.session_id,
                MAX(c.created_at) AS last_activity,
                (
                    SELECT content
                    FROM conversations AS first_msg
                    WHERE first_msg.session_id = c.session_id
                      AND first_msg.user_id IS c.user_id
                      AND first_msg.role = 'user'
                    ORDER BY first_msg.id ASC
                    LIMIT 1
                ) AS title,
                COALESCE(m.is_pinned, 0) AS is_pinned,
                m.custom_title AS custom_title
            FROM conversations AS c
            LEFT JOIN conversation_meta AS m
                ON m.session_id = c.session_id
               AND m.owner_id = ?
            {owner_filter}
              AND COALESCE(m.is_archived, 0) = ?
            GROUP BY c.session_id
            ORDER BY is_pinned DESC, last_activity DESC
            """,
            params
        ).fetchall()

    sessions = []

    for session_id, last_activity, title, is_pinned, custom_title in rows:

        if not _is_allowed(session_id, user_id, allowed_session_ids):
            continue

        full_title = (
            decrypt_text(custom_title)
            or decrypt_text(title)
            or "گفتگوی بدون عنوان"
        ).strip()

        clean_title = full_title

        if len(clean_title) > 28:
            clean_title = clean_title[:28] + "…"

        sessions.append(
            {
                "session_id": session_id,
                "title": clean_title,
                "full_title": full_title,
                "is_pinned": bool(is_pinned)
            }
        )

    return sessions


# حذف کامل یک گفتگو از پایگاه داده (فقط اگر متعلق به همین کاربر/مهمان باشد)
def delete_session(
    session_id: str,
    user_id: int | None = None,
    allowed_session_ids=None
):

    if not _is_allowed(session_id, user_id, allowed_session_ids):
        return

    with get_connection() as connection:

        if user_id is None:
            connection.execute(
                "DELETE FROM conversations WHERE session_id = ? AND user_id IS NULL",
                (session_id,)
            )
        else:
            connection.execute(
                "DELETE FROM conversations WHERE session_id = ? AND user_id = ?",
                (session_id, user_id)
            )

        # وضعیت پین/آرشیو/عنوان این گفتگو هم همراه آن پاک می‌شود
        connection.execute(
            "DELETE FROM conversation_meta WHERE session_id = ? AND owner_id = ?",
            (session_id, _owner_id(user_id))
        )

        connection.commit()


# رمزکردن داده‌های قدیمی (بدون پیشوند) که قبل از فعال‌شدن رمزنگاری ذخیره شده‌اند.
# چند بار اجرا شدنش بی‌خطر است. قبلش از flight_assistant.db یک نسخه‌ی پشتیبان بگیر.
def encrypt_existing_chat_data() -> int:
    changed = 0

    with get_connection() as connection:

        for row_id, content in connection.execute(
            "SELECT id, content FROM conversations"
        ).fetchall():
            if content is not None and not is_encrypted(content):
                connection.execute(
                    "UPDATE conversations SET content = ? WHERE id = ?",
                    (encrypt_text(content), row_id)
                )
                changed += 1

        for session_id, owner_id, title in connection.execute(
            "SELECT session_id, owner_id, custom_title FROM conversation_meta "
            "WHERE custom_title IS NOT NULL"
        ).fetchall():
            if not is_encrypted(title):
                connection.execute(
                    "UPDATE conversation_meta SET custom_title = ? "
                    "WHERE session_id = ? AND owner_id = ?",
                    (encrypt_text(title), session_id, owner_id)
                )
                changed += 1

        connection.commit()

    if changed:
        # نسخه‌ی متنیِ قدیمی ممکن است در صفحه‌های آزادشده‌ی فایل بماند؛ VACUUM پاکش می‌کند
        vacuum_connection = get_connection()
        vacuum_connection.execute("VACUUM")
        vacuum_connection.close()

    return changed