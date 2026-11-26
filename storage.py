from models import Match
import sqlite3
from pathlib import Path
from contextlib import closing

DB = Path(__file__).with_name("matches.db")


def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    with closing(connect()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                result TEXT NOT NULL,
                kills INTEGER NOT NULL,
                duration REAL NOT NULL,
                note TEXT
            )
        """)


def load_records():
    init()
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM matches ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]


def add_match(record):
    init()
    with closing(connect()) as conn, conn:
        cursor = conn.execute("""
            INSERT INTO matches
            (date, result, kills, duration, note)
            VALUES (?, ?, ?, ?, ?)
        """, (
            record["date"],
            record["result"],
            record["kills"],
            record["duration"],
            record["note"]
        ))
        return cursor.lastrowid


def delete_match(match_id):
    init()
    with closing(connect()) as conn, conn:
        cursor = conn.execute(
            "DELETE FROM matches WHERE id = ?",
            (match_id,)
        )
        return cursor.rowcount > 0
