import storage
from contextlib import closing

storage.init()

with closing(storage.connect()) as conn, conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    columns = [
        row[1] for row in
        conn.execute("PRAGMA table_info(matches)")
    ]

    if "user_id" not in columns:
        conn.execute("""
            ALTER TABLE matches
            ADD COLUMN user_id INTEGER
            REFERENCES users(id)
        """)

    columns = [
        row[1] for row in
        conn.execute("PRAGMA table_info(audit_log)")
    ]

    if "user_id" not in columns:
        conn.execute("""
            ALTER TABLE audit_log
            ADD COLUMN user_id INTEGER
            REFERENCES users(id)
        """)

print("USERS MIGRATION SUCCESS")
