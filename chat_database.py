import sqlite3
from datetime import datetime
from pathlib import Path


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

        connection.commit()


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
                content,
                datetime.now().isoformat()
            )
        )

        connection.commit()


def load_messages(session_id: str, user_id: int | None = None):
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
            "content": content
        }
        for role, content in rows
    ]


#   فهرست گفتگوهای ذخیره‌ شده‌ی همین کاربر (یا مهمان)، از جدیدترین به قدیمی‌ترین
def list_sessions(user_id: int | None = None):

    with get_connection() as connection:

        if user_id is None:
            owner_filter = "WHERE user_id IS NULL"
            params = ()
        else:
            owner_filter = "WHERE user_id = ?"
            params = (user_id,)

        rows = connection.execute(
            f"""
            SELECT
                session_id,
                MAX(created_at) AS last_activity,
                (
                    SELECT content
                    FROM conversations AS first_msg
                    WHERE first_msg.session_id = conversations.session_id
                      AND first_msg.role = 'user'
                    ORDER BY first_msg.id ASC
                    LIMIT 1
                ) AS title
            FROM conversations
            {owner_filter}
            GROUP BY session_id
            ORDER BY last_activity DESC
            """,
            params
        ).fetchall()

    sessions = []

    for session_id, last_activity, title in rows:

        clean_title = (title or "گفتگوی بدون عنوان").strip()

        if len(clean_title) > 28:
            clean_title = clean_title[:28] + "…"

        sessions.append(
            {
                "session_id": session_id,
                "title": clean_title
            }
        )

    return sessions


# حذف کامل یک گفتگو از پایگاه داده (فقط اگر متعلق به همین کاربر/مهمان باشد)
def delete_session(session_id: str, user_id: int | None = None):

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

        connection.commit()