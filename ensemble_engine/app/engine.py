from __future__ import annotations

from ensemble_engine.app.fusion.averaging import average_probability
from ensemble_engine.app.fusion.stacking import stacking_probability
from ensemble_engine.app.fusion.voting import voting_probability
from ensemble_engine.app.meta.pipeline import load_meta_pipeline


class EnsembleEngine:
    def __init__(self, default_method: str = "stacking") -> None:
        self.default_method = default_method
        self.artifacts = load_meta_pipeline()

    def predict(self, model_outputs: list[dict], method: str | None = None) -> tuple[float, str]:
        strategy = (method or self.default_method or "stacking").lower()
        probabilities = [max(0.0, min(1.0, float(m["probability"]))) for m in model_outputs]

        if strategy == "voting":
            return round(voting_probability(probabilities), 4), "voting"
        if strategy == "averaging":
            return round(average_probability(probabilities), 4), "averaging"

        prob = stacking_probability(
            probabilities,
            model=self.artifacts.model,
            imputer=self.artifacts.imputer,
            scaler=self.artifacts.scaler,
            feature_columns=self.artifacts.feature_columns,
        )
        return round(prob, 4), "stacking"

    def artifact_status(self) -> dict:
        return {
            "model_loaded": self.artifacts.model is not None,
            "scaler_loaded": self.artifacts.scaler is not None,
            "imputer_loaded": self.artifacts.imputer is not None,
            "feature_columns_count": len(self.artifacts.feature_columns),
        }


ensemble_engine = EnsembleEngine(default_method="stacking")
