from contextlib import closing
import storage
from models import Match


def load_records(user_id):
    with closing(storage.connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM matches WHERE user_id = ? ORDER BY id",
            (user_id,)
        ).fetchall()
        return [Match.from_row(row) for row in rows]


def add_match(record, user_id):
    with closing(storage.connect()) as conn, conn:
        cursor = conn.execute("""
            INSERT INTO matches
            (date, result, kills, duration, note, result_id, user_id)
            VALUES (?, ?, ?, ?, ?,
                (SELECT id FROM results WHERE name = ?), ?)
        """, (
            record.date, record.result, record.kills,
            record.duration, record.note,
            record.result, user_id
        ))
        return cursor.lastrowid


def delete_match(match_id, user_id):
    with closing(storage.connect()) as conn, conn:
        cursor = conn.execute("""
            DELETE FROM matches
            WHERE id = ? AND user_id = ?
        """, (match_id, user_id))
        return cursor.rowcount > 0


def result_report(user_id):
    with closing(storage.connect()) as conn:
        rows = conn.execute("""
            SELECT r.name, COUNT(m.id) AS count
            FROM results r
            LEFT JOIN matches m
            ON m.result_id = r.id AND m.user_id = ?
            GROUP BY r.id
        """, (user_id,)).fetchall()
        return [dict(row) for row in rows]
