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