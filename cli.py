import argparse
from storage import load_records, add_match
from logic import add_record, find_records, report


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add")
    add.add_argument("date")
    add.add_argument("result")
    add.add_argument("kills", type=int)
    add.add_argument("duration", type=float)
    add.add_argument("note")

    commands.add_parser("list")

    find = commands.add_parser("find")
    find.add_argument("result")

    commands.add_parser("report")

    args = parser.parse_args()

    try:
        records = load_records()

        if args.command == "add":
            record = add_record(
                [], args.date, args.result,
                args.kills, args.duration, args.note
            )
            match_id = add_match(record)
            print(f"Матч додано! ID: {match_id}")

        elif args.command == "list":
            for record in records:
                print(record)

        elif args.command == "find":
            for record in find_records(records, args.result):
                print(record)

        elif args.command == "report":
            for key, value in report(records).items():
                print(f"{key}: {value}")

    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Помилка: {error}")


if __name__ == "__main__":
    main()
