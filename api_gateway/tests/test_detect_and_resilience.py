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



def test_detect_endpoint_matches_predict_contract() -> None:
    client = TestClient(app)
    token = _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("sample.jpg", b"detect-bytes", "image/jpeg")}

    response = client.post("/detect", files=files, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] in {"real", "fake"}
    assert "confidence" in body
    assert "model_count" in body



def test_predict_ignores_invalid_model_payload(monkeypatch) -> None:
    from api_gateway.app.services import model_client, prediction_service

    invalid = {"prediction": "x", "class": "unknown"}
    assert model_client._normalize_model_response(invalid) is None  # noqa: SLF001

    async def fake_query_models_parallel(*args, **kwargs):
        return [
            {"probability": 0.9, "prediction": 1, "class": "fake", "inference_time": 0.1},
        ]

    monkeypatch.setattr(prediction_service, "query_models_parallel", fake_query_models_parallel)

    client = TestClient(app)
    token = _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("sample.jpg", b"predict-resilience", "image/jpeg")}

    response = client.post("/predict", files=files, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["model_count"] >= 1
    assert body["verdict"] in {"real", "fake"}
