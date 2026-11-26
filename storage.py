import os
import sqlite3
from pathlib import Path
from contextlib import closing
from models import Match

DB = Path(__file__).with_name("matches.db")


def connect():
    conn = sqlite3.connect(os.environ.get("DB_PATH", str(DB)))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init():
    with closing(connect()) as conn, conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            INSERT OR IGNORE INTO results (name)
            VALUES ('win'), ('loss');

            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                result TEXT NOT NULL,
                kills INTEGER NOT NULL,
                duration REAL NOT NULL,
                note TEXT,
                result_id INTEGER REFERENCES results(id)
            );

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
            r[1] for r in conn.execute(
                "PRAGMA table_info(matches)"
            )
        ]

        if "result_id" not in columns:
            conn.execute("""
                ALTER TABLE matches ADD COLUMN result_id
                INTEGER REFERENCES results(id)
            """)

        conn.execute("""
            UPDATE matches SET result_id = (
                SELECT id FROM results
                WHERE name = matches.result
            ) WHERE result_id IS NULL
        """)


def load_records():
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM matches ORDER BY id"
        ).fetchall()
        return [Match.from_row(row) for row in rows]


def add_match(record):
    with closing(connect()) as conn, conn:
        cursor = conn.execute("""
            INSERT INTO matches
            (date, result, kills, duration, note, result_id)
            VALUES (?, ?, ?, ?, ?, (
                SELECT id FROM results WHERE name = ?
            ))
        """, (
            record.date,
            record.result,
            record.kills,
            record.duration,
            record.note,
            record.result
        ))
        return cursor.lastrowid


def delete_match(match_id):
    with closing(connect()) as conn, conn:
        cursor = conn.execute(
            "DELETE FROM matches WHERE id = ?",
            (match_id,)
        )
        return cursor.rowcount > 0


def result_report():
    with closing(connect()) as conn:
        rows = conn.execute("""
            SELECT r.name, COUNT(m.id) AS count
            FROM results r
            LEFT JOIN matches m ON m.result_id = r.id
            GROUP BY r.id
        """).fetchall()
        return [dict(row) for row in rows]


def get_log(limit=50):
    with closing(connect()) as conn:
        rows = conn.execute("""
            SELECT * FROM audit_log
            ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]
