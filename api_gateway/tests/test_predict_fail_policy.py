from types import SimpleNamespace

import httpx
import pytest

from api_gateway.tests.test_helpers import get_token


@pytest.mark.anyio
async def test_predict_fail_closed_when_no_model_results(
    monkeypatch,
    client: httpx.AsyncClient,
) -> None:
    from api_gateway.app.services import prediction_service

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

    token = await get_token(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("sample.jpg", b"closed-mode-bytes", "image/jpeg")}

    response = await client.post("/predict", headers=headers, files=files)
    assert response.status_code == 503
