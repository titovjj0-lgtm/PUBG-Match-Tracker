from logic import add_record, find_records, report

records = []

add_record(records, "2026-11-26", "win", 5, 20, "First match")
add_record(records, "2026-11-26", "loss", 3, 15, "Second match")

assert len(records) == 2
assert len(find_records(records, "win")) == 1
assert len(find_records(records, "loss")) == 1

stats = report(records)

assert stats["matches"] == 2
assert stats["wins"] == 1
assert stats["losses"] == 1
assert stats["total_kills"] == 8
assert stats["average_kills"] == 4
assert stats["win_rate"] == 50

try:
    add_record(records, "2026-11-26", "win", -5, 20, "")
except ValueError:
    pass
else:
    raise AssertionError("Invalid kills accepted")

print("All tests passed!")
