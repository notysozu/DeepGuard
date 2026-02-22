
def verdict_from_probability(prob_fake: float, threshold: float) -> tuple[str, float]:
    verdict = "fake" if prob_fake >= threshold else "real"
    confidence = prob_fake if verdict == "fake" else 1.0 - prob_fake
    return verdict, round(confidence, 4)
