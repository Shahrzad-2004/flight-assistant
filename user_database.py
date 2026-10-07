import sqlite3
from pathlib import Path

from db_crypto import encrypt_text, decrypt_text, is_encrypted


DB_PATH = Path("users.db")


def create_users_table():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        email TEXT UNIQUE NOT NULL,

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

        cursor.execute(
            """
            UPDATE users
            SET email = ?, name = ?, picture = ?
            WHERE id = ?
            """,
            (
                encrypt_text(email),
                encrypt_text(name),
                encrypt_text(picture),
                user_id
            )
        )

        conn.commit()

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
                encrypt_text(email),
                encrypt_text(name),
                encrypt_text(picture)
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
            "email": decrypt_text(user[1]),
            "google_id": user[2],
            "name": decrypt_text(user[3]),
            "picture": decrypt_text(user[4])
        }

    return None


# رمزکردن کاربرانی که قبل از فعال‌شدن رمزنگاری ذخیره شده‌اند (idempotent).
# قبلش از users.db یک نسخه‌ی پشتیبان بگیر.
def encrypt_existing_user_data() -> int:
    changed = 0
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for user_id, email, name, picture in cursor.execute(
        "SELECT id, email, name, picture FROM users"
    ).fetchall():
        if any(v is not None and not is_encrypted(v) for v in (email, name, picture)):
            cursor.execute(
                "UPDATE users SET email = ?, name = ?, picture = ? WHERE id = ?",
                (encrypt_text(email), encrypt_text(name), encrypt_text(picture), user_id)
            )
            changed += 1

    conn.commit()

    if changed:
        # نسخه‌ی متنیِ قدیمی ممکن است در صفحه‌های آزادشده‌ی فایل بماند؛ VACUUM پاکش می‌کند
        conn.execute("VACUUM")

    conn.close()
    return changed