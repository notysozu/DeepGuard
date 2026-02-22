from __future__ import annotations

import numpy as np

from ensemble_engine.app.fusion.averaging import average_probability



def stacking_probability(
    probabilities: list[float],
    *,
    model,
    imputer,
    scaler,
    feature_columns: list[str],
) -> float:
    if not probabilities:
        return 0.0

    if model is None or imputer is None or scaler is None or not feature_columns:
        # Fallback if artifacts are unavailable.
        return average_probability(probabilities)

    features = {col: 0.0 for col in feature_columns}
    for i, prob in enumerate(probabilities):
        key = f"model_{i + 1}_prob"
        if key in features:
            features[key] = prob

    vector = np.array([[features[col] for col in feature_columns]], dtype=float)
    vector = imputer.transform(vector)
    vector = scaler.transform(vector)

    if hasattr(model, "predict_proba"):
        return float(model.predict_proba(vector)[0][1])

    pred = float(model.predict(vector)[0])
    return min(1.0, max(0.0, pred))
