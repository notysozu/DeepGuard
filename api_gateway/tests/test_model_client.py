from api_gateway.app.services.model_client import _normalize_model_response


def test_normalize_model_response_rejects_invalid_payload() -> None:
    assert _normalize_model_response({"prediction": "bad"}) is None  # noqa: SLF001


def test_normalize_model_response_fills_missing_fields() -> None:
    normalized = _normalize_model_response({"probability": 0.8})
    assert normalized is not None
    assert normalized["prediction"] == 1
    assert normalized["class"] == "fake"
    assert normalized["inference_time"] == 0.0
