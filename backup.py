import datetime
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "matches.db")
BACKUPS = os.path.join(BASE, "backups")

os.makedirs(BACKUPS, exist_ok=True)

target = os.path.join(
    BACKUPS, f"matches-{datetime.date.today()}.db"
)

src = sqlite3.connect(DB)
dst = sqlite3.connect(target)

src.backup(dst)

dst.close()
src.close()

print("Backup saved:", target)