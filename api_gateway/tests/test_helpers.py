import httpx


async def get_token(client: httpx.AsyncClient, username: str, password: str) -> str:
    response = await client.post(
        "/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
