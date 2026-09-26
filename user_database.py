import sqlite3
from pathlib import Path


DB_PATH = Path("users.db")


def create_users_table():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        email TEXT UNIQUE NOT NULL,

        password_hash BLOB,

        google_id TEXT UNIQUE,

        name TEXT,

        picture TEXT

    )
    """)

    conn.commit()
    conn.close()

def create_google_user(
    google_id,
    email,
    name,
    picture
):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE google_id=?
        """,
        (google_id,)
    )


    user = cursor.fetchone()


    if user:

        user_id = user[0]


    else:

        cursor.execute(
            """
            INSERT INTO users(
                google_id,
                email,
                name,
                picture
            )
            VALUES (?,?,?,?)
            """,
            (
                google_id,
                email,
                name,
                picture
            )
        )

        conn.commit()

        user_id = cursor.lastrowid


    conn.close()

    return user_id


def get_user_by_id(user_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,email,google_id,name,picture
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()


    if user:

        return {
            "id": user[0],
            "email": user[1],
            "google_id": user[2],
            "name": user[3],
            "picture": user[4]
        }

    return None