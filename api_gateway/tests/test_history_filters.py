from fastapi.testclient import TestClient

from api_gateway.app.main import app


client = TestClient(app)



def _get_token(username: str, password: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]



def test_history_supports_pagination_and_verdict_filter() -> None:
    token = _get_token("admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    files1 = {"file": ("a.jpg", b"history-filter-a", "image/jpeg")}
    files2 = {"file": ("b.jpg", b"history-filter-b", "image/jpeg")}
    client.post("/predict", headers=headers, files=files1)
    client.post("/predict", headers=headers, files=files2)

    resp = client.get("/history?limit=1&offset=0&verdict=fake", headers=headers)
    assert resp.status_code == 200
    body = resp.json()

    assert "total" in body
    assert body["offset"] == 0
    assert body["limit"] == 1
    assert isinstance(body["items"], list)
    assert len(body["items"]) <= 1



def test_history_rejects_invalid_filter_values() -> None:
    token = _get_token("admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/history?verdict=maybe", headers=headers)
    assert resp.status_code == 422
