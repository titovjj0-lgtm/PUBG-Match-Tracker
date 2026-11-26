import sqlite3

with sqlite3.connect("matches.db") as conn:
    conn.execute("PRAGMA foreign_keys = ON")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        INSERT OR IGNORE INTO results (name)
        VALUES ('win'), ('loss');

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,
            item_id INTEGER,
            details TEXT
        );

        CREATE TRIGGER IF NOT EXISTS audit_add
        AFTER INSERT ON matches
        BEGIN
            INSERT INTO audit_log (action, item_id)
            VALUES ('add', NEW.id);
        END;

        CREATE TRIGGER IF NOT EXISTS audit_delete
        AFTER DELETE ON matches
        BEGIN
            INSERT INTO audit_log (action, item_id)
            VALUES ('delete', OLD.id);
        END;
    """)

    columns = [
        row[1] for row in
        conn.execute("PRAGMA table_info(matches)")
    ]

    if "result_id" not in columns:
        conn.execute("""
            ALTER TABLE matches
            ADD COLUMN result_id INTEGER
            REFERENCES results(id)
        """)

    conn.execute("""
        UPDATE matches
        SET result_id = (
            SELECT id FROM results
            WHERE name = matches.result
        )
    """)

    conn.executescript("""
        CREATE TRIGGER IF NOT EXISTS match_result_link
        AFTER INSERT ON matches
        BEGIN
            UPDATE matches
            SET result_id = (
                SELECT id FROM results
                WHERE name = NEW.result
            )
            WHERE id = NEW.id;
        END;
    """)

print("Migration completed successfully")