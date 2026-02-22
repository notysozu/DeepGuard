from fastapi.testclient import TestClient

from api_gateway.app.main import app



def _get_token(client: TestClient) -> str:
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]



def test_predict_requires_auth() -> None:
    client = TestClient(app)
    response = client.post("/predict")
    assert response.status_code == 401



def test_predict_success() -> None:
    client = TestClient(app)
    token = _get_token(client)
    files = {"file": ("sample.jpg", b"fake-image-bytes", "image/jpeg")}
    response = client.post(
        "/predict",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] in {"real", "fake"}
    assert "request_id" in body
    assert body["duplicate_cache_hit"] is False



def test_predict_duplicate_cache_hit() -> None:
    client = TestClient(app)
    token = _get_token(client)
    files = {"file": ("sample.jpg", b"same-bytes", "image/jpeg")}
    headers = {"Authorization": f"Bearer {token}"}

    first = client.post("/predict", files=files, headers=headers)
    second = client.post("/predict", files=files, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["duplicate_cache_hit"] is True
