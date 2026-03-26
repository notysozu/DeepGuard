import httpx
import pytest


@pytest.mark.anyio
async def test_auth_token_success(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.anyio
async def test_auth_token_failure(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/token",
        data={"username": "admin", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
