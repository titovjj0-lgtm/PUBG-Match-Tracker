import pytest
import storage
from contextlib import closing
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    monkeypatch.setitem(app.config, "TESTING", True)
    monkeypatch.setitem(app.config, "SECRET_KEY", "test-only-key")

    from prepare_db import prepare_database
    prepare_database()

    return app.test_client()


def register(client, login="player"):
    return client.post("/register", json={
        "login": login,
        "password": "TestPassword123"
    })


def add_match(client):
    return client.post("/matches", json={
        "date": "2026-11-26",
        "result": "win",
        "kills": 5,
        "duration": 20,
        "note": "Test match"
    })


def test_register(client):
    assert register(client).status_code == 201


def test_duplicate_login(client):
    register(client)
    assert register(client).status_code == 409


def test_password_hash(client):
    register(client)
    with closing(storage.connect()) as conn:
        row = conn.execute(
            "SELECT password_hash FROM users"
        ).fetchone()
        assert row["password_hash"] != "TestPassword123"


def test_wrong_password(client):
    register(client)
    client.post("/logout")
    response = client.post("/login", json={
        "login": "player",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login(client):
    register(client)
    client.post("/logout")
    response = client.post("/login", json={
        "login": "player",
        "password": "TestPassword123"
    })
    assert response.status_code == 200


def test_without_session(client):
    assert client.get("/matches").status_code == 401


def test_add_match(client):
    register(client)
    assert add_match(client).status_code == 201
    assert len(client.get("/matches").get_json()) == 1


def test_user_isolation(client):
    register(client, "player1")
    match_id = add_match(client).get_json()["id"]

    client.post("/logout")
    register(client, "player2")

    assert client.get("/matches").get_json() == []
    assert client.delete(
        f"/matches/{match_id}"
    ).status_code == 404


def test_admin_forbidden(client):
    register(client)
    assert client.get("/admin/log").status_code == 403


def test_cloudflare_block(client):
    register(client)
    assert client.get(
        "/admin/log",
        headers={"CF-Connecting-IP": "203.0.113.10"}
    ).status_code == 404


def test_admin_access(client):
    register(client)

    with closing(storage.connect()) as conn, conn:
        conn.execute(
            "UPDATE users SET is_admin = 1 WHERE login = ?",
            ("player",)
        )

    assert client.get("/admin/log").status_code == 200


def test_logout(client):
    register(client)
    client.post("/logout")
    assert client.get("/matches").status_code == 401


def test_report(client):
    register(client)
    add_match(client)
    report = client.get("/report").get_json()
    assert report["statistics"]["matches"] == 1


def test_audit(client):
    register(client)
    match_id = add_match(client).get_json()["id"]
    client.delete(f"/matches/{match_id}")

    with closing(storage.connect()) as conn:
        rows = conn.execute(
            "SELECT action, user_id FROM audit_log"
        ).fetchall()

    assert len(rows) == 2
    assert rows[0]["action"] == "add"
    assert rows[1]["action"] == "delete"
    assert all(row["user_id"] is not None for row in rows)


def test_admin_import_export(client):
    register(client)

    with closing(storage.connect()) as conn, conn:
        conn.execute("UPDATE users SET is_admin = 1")

    response = client.post("/admin/import", json=[{
        "date": "2026-11-26",
        "result": "win",
        "kills": 10,
        "duration": 25,
        "note": "Import test"
    }])

    assert response.status_code == 201
    assert response.get_json()["imported"] == 1

    response = client.get("/admin/export")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_import_forbidden(client):
    register(client)
    assert client.post("/admin/import", json=[]).status_code == 403
