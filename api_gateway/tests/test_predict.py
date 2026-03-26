import httpx
import pytest

from api_gateway.tests.test_helpers import get_token


@pytest.mark.anyio
async def test_predict_requires_auth(client: httpx.AsyncClient) -> None:
    response = await client.post("/predict")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_predict_success(client: httpx.AsyncClient) -> None:
    token = await get_token(client, "admin", "admin123")
    files = {"file": ("sample.jpg", b"fake-image-bytes", "image/jpeg")}
    response = await client.post(
        "/predict",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] in {"real", "fake"}
    assert "request_id" in body
    assert body["duplicate_cache_hit"] is False


@pytest.mark.anyio
async def test_predict_duplicate_cache_hit(client: httpx.AsyncClient) -> None:
    token = await get_token(client, "admin", "admin123")
    files = {"file": ("sample.jpg", b"same-bytes", "image/jpeg")}
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post("/predict", files=files, headers=headers)
    second = await client.post("/predict", files=files, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["duplicate_cache_hit"] is True
