import storage
from getpass import getpass
from contextlib import closing
from werkzeug.security import generate_password_hash

login = input("Login: ").strip()
password = getpass("Password: ")

if len(login) < 3 or len(password) < 8:
    raise SystemExit("Login: min 3, password: min 8 characters")

with closing(storage.connect()) as conn, conn:
    user = conn.execute(
        "SELECT id FROM users WHERE login = ?", (login,)
    ).fetchone()

    if user is None:
        cursor = conn.execute("""
            INSERT INTO users (login, password_hash, is_admin)
            VALUES (?, ?, 1)
        """, (login, generate_password_hash(password)))
        user_id = cursor.lastrowid
    else:
        user_id = user["id"]
        conn.execute("""
            UPDATE users SET is_admin = 1, password_hash = ?
            WHERE id = ?
        """, (generate_password_hash(password), user_id))

    conn.execute("""
        UPDATE matches SET user_id = ?
        WHERE user_id IS NULL
    """, (user_id,))

print("ADMIN ACCOUNT READY")
print("OLD MATCHES ASSIGNED")
