def voting_probability(probabilities: list[float]) -> float:
    if not probabilities:
        return 0.0
    votes = sum(1 for p in probabilities if p >= 0.5)
    return votes / len(probabilities)
