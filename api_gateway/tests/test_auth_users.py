import httpx
import pytest

from api_gateway.tests.test_helpers import get_token


@pytest.mark.anyio
async def test_admin_can_create_and_list_users(client: httpx.AsyncClient) -> None:
    token = await get_token(client, "admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    create = await client.post(
        "/auth/users",
        headers=headers,
        json={
            "username": "auditor1",
            "password": "auditor123",
            "role": "viewer",
            "is_active": True,
        },
    )
    assert create.status_code in {200, 409}

    listing = await client.get("/auth/users", headers=headers)
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert any(i["username"] == "admin" for i in items)


@pytest.mark.anyio
async def test_viewer_cannot_manage_users(client: httpx.AsyncClient) -> None:
    token = await get_token(client, "viewer", "viewer123")
    headers = {"Authorization": f"Bearer {token}"}

    create = await client.post(
        "/auth/users",
        headers=headers,
        json={
            "username": "blockeduser",
            "password": "blocked123",
            "role": "viewer",
            "is_active": True,
        },
    )
    assert create.status_code == 403

    listing = await client.get("/auth/users", headers=headers)
    assert listing.status_code == 403
