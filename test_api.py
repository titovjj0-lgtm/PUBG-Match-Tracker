from app import app


def test_get_matches():
    with app.test_client() as client:
        response = client.get("/matches")
        assert response.status_code == 200


def test_report():
    with app.test_client() as client:
        response = client.get("/report")
        assert response.status_code == 200


def test_admin_protection():
    with app.test_client() as client:
        response = client.get("/admin/export")
        assert response.status_code == 403


def test_cloudflare_protection():
    with app.test_client() as client:
        response = client.get(
            "/admin/export",
            headers={"CF-Connecting-IP": "203.0.113.10"}
        )
        assert response.status_code == 404


def test_invalid_match():
    with app.test_client() as client:
        response = client.post("/matches", json={})
        assert response.status_code == 400