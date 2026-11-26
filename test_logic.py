import pytest
import logic
from models import Match


def test_add_record():
    records = []
    record = logic.add_record(
        records, "2026-11-26", "win", 5, 20.5, ""
    )
    assert isinstance(record, Match)
    assert len(records) == 1


def test_find_records():
    records = [
        Match("2026-11-26", 5, 20, "win"),
        Match("2026-11-26", 2, 15, "loss")
    ]
    assert len(logic.find_records(records, "win")) == 1


def test_report():
    records = [
        Match("2026-11-26", 5, 20, "win"),
        Match("2026-11-26", 3, 15, "loss")
    ]
    result = logic.report(records)
    assert result["matches"] == 2
    assert result["total_kills"] == 8
    assert result["win_rate"] == 50


def test_invalid_kills():
    with pytest.raises(ValueError):
        logic.add_record(
            [], "2026-11-26", "win", -5, 20, ""
        )


def test_empty_report():
    assert logic.report([])["matches"] == 0
