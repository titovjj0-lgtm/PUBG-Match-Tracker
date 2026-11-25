from datetime import date


def add_record(records, match_date, result, kills, duration, note):
    date.fromisoformat(match_date)

    kills = int(kills)
    duration = float(duration)
    result = result.lower().strip()

    if kills < 0:
        raise ValueError("Кількість вбивств не може бути від'ємною")

    if duration <= 0:
        raise ValueError("Тривалість має бути більше нуля")

    if result not in ("win", "loss"):
        raise ValueError("Введіть win або loss")

    record = {
        "date": match_date,
        "result": result,
        "kills": kills,
        "duration": duration,
        "note": note
    }

    records.append(record)
    return record


def find_records(records, result):
    return [
        record for record in records
        if record["result"] == result.lower().strip()
    ]


def report(records):
    total = len(records)
    wins = sum(1 for r in records if r["result"] == "win")
    kills = sum(r["kills"] for r in records)

    return {
        "matches": total,
        "wins": wins,
        "losses": total - wins,
        "total_kills": kills,
        "average_kills": round(kills / total, 2) if total else 0,
        "win_rate": round(wins / total * 100, 2) if total else 0
    }
