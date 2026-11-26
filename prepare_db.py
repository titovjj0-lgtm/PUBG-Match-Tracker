import storage
import runpy
from pathlib import Path

BASE = Path(__file__).resolve().parent

def prepare_database():
    storage.init()

    for filename in (
        "migrate_users.py",
        "migrate_audit.py",
    ):
        runpy.run_path(str(BASE / filename))

    try:
        runpy.run_path(str(BASE / "migrate_ownership.py"))
    except SystemExit as error:
        if error.code != 0:
            raise

if __name__ == "__main__":
    prepare_database()
    print("DATABASE READY")
