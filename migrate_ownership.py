import storage
from contextlib import closing

with closing(storage.connect()) as conn:
    columns = conn.execute("PRAGMA table_info(matches)").fetchall()

    if any(r["name"] == "user_id" and r["notnull"] for r in columns):
        print("MIGRATION ALREADY DONE")
        raise SystemExit(0)

    with conn:
        conn.execute("BEGIN IMMEDIATE")

        missing = conn.execute("""
            SELECT COUNT(*) FROM matches
            WHERE user_id IS NULL
        """).fetchone()[0]

        if missing:
            raise RuntimeError("Matches without owner exist")

        before = conn.execute(
            "SELECT COUNT(*) FROM matches"
        ).fetchone()[0]

        conn.execute("""
            CREATE TABLE matches_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                result TEXT NOT NULL,
                kills INTEGER NOT NULL,
                duration REAL NOT NULL,
                note TEXT,
                result_id INTEGER REFERENCES results(id),
                user_id INTEGER NOT NULL REFERENCES users(id)
            )
        """)

        conn.execute("""
            INSERT INTO matches_new
            (id, date, result, kills, duration, note, result_id, user_id)
            SELECT id, date, result, kills, duration, note, result_id, user_id
            FROM matches
        """)

        conn.execute("DROP TABLE matches")
        conn.execute("ALTER TABLE matches_new RENAME TO matches")

        conn.execute("""
            CREATE TRIGGER audit_add AFTER INSERT ON matches
            BEGIN
                INSERT INTO audit_log(action, item_id, user_id)
                VALUES ('add', NEW.id, NEW.user_id);
            END
        """)

        conn.execute("""
            CREATE TRIGGER audit_delete AFTER DELETE ON matches
            BEGIN
                INSERT INTO audit_log(action, item_id, user_id)
                VALUES ('delete', OLD.id, OLD.user_id);
            END
        """)

        after = conn.execute(
            "SELECT COUNT(*) FROM matches"
        ).fetchone()[0]

        assert before == after
        assert not conn.execute("PRAGMA foreign_key_check").fetchall()

print("MIGRATION SUCCESS")
print("Matches preserved:", after)
