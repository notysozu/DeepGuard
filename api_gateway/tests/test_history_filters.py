import httpx
import pytest

from api_gateway.tests.test_helpers import get_token


@pytest.mark.anyio
async def test_history_supports_pagination_and_verdict_filter(client: httpx.AsyncClient) -> None:
    token = await get_token(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    files1 = {"file": ("a.jpg", b"history-filter-a", "image/jpeg")}
    files2 = {"file": ("b.jpg", b"history-filter-b", "image/jpeg")}
    await client.post("/predict", headers=headers, files=files1)
    await client.post("/predict", headers=headers, files=files2)

    resp = await client.get("/history?limit=1&offset=0&verdict=fake", headers=headers)
    assert resp.status_code == 200
    body = resp.json()

    assert "total" in body
    assert body["offset"] == 0
    assert body["limit"] == 1
    assert isinstance(body["items"], list)
    assert len(body["items"]) <= 1


@pytest.mark.anyio
async def test_history_rejects_invalid_filter_values(client: httpx.AsyncClient) -> None:
    token = await get_token(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/history?verdict=maybe", headers=headers)
    assert resp.status_code == 422
