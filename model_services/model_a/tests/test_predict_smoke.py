from model_services.model_a.app.main import ModelInput, predict


def test_predict_returns_probability_and_class() -> None:
    response = predict(ModelInput(media_base64="c29tZS1iYXNlNjQ="))
    assert 0.0 <= response["probability"] <= 1.0
    assert response["class"] in {"real", "fake"}
