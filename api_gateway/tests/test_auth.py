from fastapi.testclient import TestClient

from api_gateway.app.main import app


client = TestClient(app)



def test_auth_token_success() -> None:
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"



def test_auth_token_failure() -> None:
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
