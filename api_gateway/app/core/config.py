from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "DeepGuard API Gateway")
    app_env: str = os.getenv("APP_ENV", "dev")
    secret_key: str = os.getenv("SECRET_KEY", "change-me")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///database/deepguard.db")
    model_timeout: float = float(os.getenv("MODEL_TIMEOUT", "30"))
    max_payload_mb: int = int(os.getenv("MAX_PAYLOAD_MB", "50"))
    ensemble_method: str = os.getenv("ENSEMBLE_METHOD", "stacking")
    fake_threshold: float = float(os.getenv("FAKE_THRESHOLD", "0.5"))
    model_registry_path: str = os.getenv("MODEL_REGISTRY_PATH", "configs/models.yaml")
    max_image_pixels: int = int(os.getenv("MAX_IMAGE_PIXELS", "50000000"))
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    fail_open_on_model_error: bool = _parse_bool(
        os.getenv("FAIL_OPEN_ON_MODEL_ERROR"),
        True,
    )

    @property
    def model_registry_file(self) -> Path:
        return Path(self.model_registry_path)


settings = Settings()
