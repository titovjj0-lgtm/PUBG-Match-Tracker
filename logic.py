from datetime import date
from math import isfinite
from models import Match


def add_record(records, match_date, result, kills, duration, note):
    date.fromisoformat(match_date)
    kills = int(kills)
    duration = float(duration)
    result = result.lower().strip()

    if kills < 0:
        raise ValueError("Invalid kills")

    if not isfinite(duration) or duration <= 0:
        raise ValueError("Invalid duration")

    if result not in ("win", "loss"):
        raise ValueError("Expected win or loss")

    record = Match(match_date, kills, duration, result, note)
    records.append(record)
    return record


def find_records(records, result):
    return [
        r for r in records
        if r.result == result.lower().strip()
    ]


def report(records):
    total = len(records)
    wins = sum(1 for r in records if r.is_win())
    kills = sum(r.kills for r in records)

    return {
        "matches": total,
        "wins": wins,
        "losses": total - wins,
        "total_kills": kills,
        "average_kills": round(kills / total, 2) if total else 0,
        "win_rate": round(wins / total * 100, 2) if total else 0
    }
