import pytest
import storage
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "DB_PATH", str(tmp_path / "test.db")
    )
    storage.init()
    app.config["TESTING"] = True
    return app.test_client()


def test_get_matches(client):
    response = client.get("/matches")
    assert response.status_code == 200
    assert response.get_json() == []


def test_report(client):
    assert client.get("/report").status_code == 200


def test_admin_protection(client):
    assert client.get("/admin/export").status_code == 403


def test_cloudflare_protection(client):
    response = client.get(
        "/admin/export",
        headers={"CF-Connecting-IP": "203.0.113.10"}
    )
    assert response.status_code == 404


def test_invalid_match(client):
    response = client.post("/matches", json={})
    assert response.status_code == 400


def test_add_match(client):
    response = client.post("/matches", json={
        "date": "2026-11-26",
        "result": "win",
        "kills": 5,
        "duration": 20.5,
        "note": "Test"
    })
    assert response.status_code == 201

    records = client.get("/matches").get_json()
    assert len(records) == 1
    assert records[0]["kills"] == 5
    assert records[0]["duration"] == 20.5
