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



def test_auth_and_predict_and_history_flow() -> None:
    token = _get_token("admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    file_payload = {"file": ("sample.jpg", b"binary-media-content", "image/jpeg")}

    first = client.post("/predict", headers=headers, files=file_payload)
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["verdict"] in {"fake", "real"}
    assert first_body["duplicate_cache_hit"] is False

    second = client.post("/predict", headers=headers, files=file_payload)
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["duplicate_cache_hit"] is True

    history = client.get("/history", headers=headers)
    assert history.status_code == 200
    items = history.json()["items"]
    assert isinstance(items, list)
    assert len(items) >= 1

    request_id = first_body["request_id"]
    detail = client.get(f"/history/{request_id}", headers=headers)
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["request_id"] == request_id



def test_viewer_cannot_access_history() -> None:
    token = _get_token("viewer", "viewer123")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/history", headers=headers)
    assert response.status_code == 403
