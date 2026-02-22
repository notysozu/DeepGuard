from __future__ import annotations

import json
from pathlib import Path

import joblib


class MetaArtifacts:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.model = None
        self.scaler = None
        self.imputer = None
        self.feature_columns: list[str] = []

    def load(self) -> None:
        model_path = self.base_dir / "deepsafe_meta_learner.joblib"
        scaler_path = self.base_dir / "deepsafe_meta_scaler.joblib"
        imputer_path = self.base_dir / "deepsafe_meta_imputer.joblib"
        columns_path = self.base_dir / "feature_columns.json"

        if model_path.exists():
            try:
                self.model = joblib.load(model_path)
            except Exception:
                self.model = None
        if scaler_path.exists():
            try:
                self.scaler = joblib.load(scaler_path)
            except Exception:
                self.scaler = None
        if imputer_path.exists():
            try:
                self.imputer = joblib.load(imputer_path)
            except Exception:
                self.imputer = None
        if columns_path.exists():
            with columns_path.open("r", encoding="utf-8") as f:
                self.feature_columns = json.load(f)
