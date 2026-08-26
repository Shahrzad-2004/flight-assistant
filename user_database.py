import sqlite3
from pathlib import Path
import bcrypt


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



def create_user(email, password):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:

        cursor.execute(
            """
            INSERT INTO users(
                email,
                password_hash
            )
            VALUES (?,?)
            """,
            (
                email,
                password_hash
            )
        )

        conn.commit()

        return True


    except sqlite3.IntegrityError:

        return False


    finally:

        conn.close()



def check_user(email, password):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT password_hash
        FROM users
        WHERE email=?
        """,
        (email,)
    )


    user = cursor.fetchone()

    conn.close()


    if user and user[0]:

        return bcrypt.checkpw(
            password.encode(),
            user[0]
        )


    return False



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

def get_user_by_email(email):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, email, google_id, name, picture
        FROM users
        WHERE email=?
        """,
        (email,)
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