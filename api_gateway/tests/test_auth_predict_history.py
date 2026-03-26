import httpx
import pytest

from api_gateway.tests.test_helpers import get_token


@pytest.mark.anyio
async def test_auth_and_predict_and_history_flow(client: httpx.AsyncClient) -> None:
    token = await get_token(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    file_payload = {"file": ("sample.jpg", b"binary-media-content", "image/jpeg")}

    first = await client.post("/predict", headers=headers, files=file_payload)
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["verdict"] in {"fake", "real"}
    assert first_body["duplicate_cache_hit"] is False

    second = await client.post("/predict", headers=headers, files=file_payload)
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["duplicate_cache_hit"] is True

    history = await client.get("/history", headers=headers)
    assert history.status_code == 200
    history_body = history.json()
    assert "total" in history_body
    assert "offset" in history_body
    assert "limit" in history_body
    items = history_body["items"]
    assert isinstance(items, list)
    assert len(items) >= 1

    request_id = first_body["request_id"]
    detail = await client.get(f"/history/{request_id}", headers=headers)
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["request_id"] == request_id


@pytest.mark.anyio
async def test_viewer_cannot_access_history(client: httpx.AsyncClient) -> None:
    token = await get_token(client, "viewer", "viewer123")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/history", headers=headers)
    assert response.status_code == 403
