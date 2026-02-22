from fastapi.testclient import TestClient

from api_gateway.app.main import app



def test_health_details_shape() -> None:
    client = TestClient(app)
    response = client.get("/health/details")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "api_gateway"
    assert "database" in body
    assert "model_registry" in body
    assert "ensemble_artifacts" in body
    assert "policy" in body
