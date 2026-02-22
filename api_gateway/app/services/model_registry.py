from __future__ import annotations

from pathlib import Path

import yaml


class ModelRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load_models(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("models", [])
