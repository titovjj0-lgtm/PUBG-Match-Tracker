import json
from pathlib import Path

FILE_NAME = Path(__file__).with_name("matches.txt")


def load_records():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            records = json.load(file)
            if not isinstance(records, list):
                raise ValueError("Invalid data format")
            return records
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as error:
        raise ValueError("Помилка читання файлу") from error


def save_records(records):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

