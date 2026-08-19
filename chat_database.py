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
                role TEXT NOT NULL
                    CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()


def save_message(session_id: str, role: str, content: str):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO conversations (
                session_id,
                role,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                content,
                datetime.now().isoformat()
            )
        )

        connection.commit()


def load_messages(session_id: str):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM conversations
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,)
        ).fetchall()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in rows
    ]
#   فهرست گفتگوهای ذخیره‌ شده در پایگاه داده و خروجی به ترتیب جدیدترین به قدیمی‌ ترین است
def list_sessions():
    
    with get_connection() as connection:
        rows = connection.execute(
            """
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
            GROUP BY session_id
            ORDER BY last_activity DESC
            """
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

# حذف کامل یک گفتگو از پایگاه داده
def delete_session(session_id: str):

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM conversations WHERE session_id = ?",
            (session_id,)
        )

        connection.commit()