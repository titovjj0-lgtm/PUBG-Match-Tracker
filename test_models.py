from models import Match


def test_match_creation():
    match = Match("2026-11-26", 5, 20, "win")
    assert match.kills == 5
    assert match.duration == 20


def test_win():
    match = Match("2026-11-26", 5, 20, "win")
    assert match.is_win() is True


def test_loss():
    match = Match("2026-11-26", 2, 15, "loss")
    assert match.is_win() is False


def test_to_dict():
    match = Match("2026-11-26", 5, 20, "win")
    assert match.to_dict()["kills"] == 5


def test_number_conversion():
    match = Match("2026-11-26", "5", "20", "win")
    assert match.kills == 5
    assert match.duration == 20