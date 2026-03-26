import httpx
import pytest


@pytest.mark.anyio
async def test_health_details_shape(client: httpx.AsyncClient) -> None:
    response = await client.get("/health/details")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "api_gateway"
    assert "database" in body
    assert "model_registry" in body
    assert "ensemble_artifacts" in body
    assert "policy" in body
