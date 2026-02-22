from fastapi.testclient import TestClient

from api_gateway.app.main import app


client = TestClient(app)



def _get_token(username: str, password: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]



def test_admin_can_create_and_list_users() -> None:
    token = _get_token("admin", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
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

    listing = client.get("/auth/users", headers=headers)
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert any(i["username"] == "admin" for i in items)



def test_viewer_cannot_manage_users() -> None:
    token = _get_token("viewer", "viewer123")
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
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

    listing = client.get("/auth/users", headers=headers)
    assert listing.status_code == 403
