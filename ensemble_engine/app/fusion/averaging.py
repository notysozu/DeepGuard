def average_probability(probabilities: list[float]) -> float:
    if not probabilities:
        return 0.0
    return sum(probabilities) / len(probabilities)
