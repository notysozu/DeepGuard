from ensemble_engine.app.engine import ensemble_engine



def classify_binary(model_outputs: list[dict], threshold: float) -> tuple[str, float, str]:
    prob_fake, method = ensemble_engine.predict(model_outputs)
    verdict = "fake" if prob_fake >= threshold else "real"
    confidence = prob_fake if verdict == "fake" else 1.0 - prob_fake
    return verdict, round(confidence, 4), method
