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



def test_predict_fail_closed_when_no_model_results(monkeypatch) -> None:
    from api_gateway.app.services import prediction_service
    from types import SimpleNamespace

    async def fake_query_models_parallel(*args, **kwargs):
        return []

    monkeypatch.setattr(prediction_service, "query_models_parallel", fake_query_models_parallel)
    current = prediction_service.settings
    patched = SimpleNamespace(
        max_payload_mb=current.max_payload_mb,
        max_image_pixels=current.max_image_pixels,
        model_registry_file=current.model_registry_file,
        model_timeout=current.model_timeout,
        fake_threshold=current.fake_threshold,
        fail_open_on_model_error=False,
    )
    monkeypatch.setattr(prediction_service, "settings", patched)

    client = TestClient(app)
    token = _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("sample.jpg", b"closed-mode-bytes", "image/jpeg")}

    response = client.post("/predict", headers=headers, files=files)
    assert response.status_code == 503
