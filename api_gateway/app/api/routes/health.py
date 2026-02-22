from fastapi import APIRouter
from sqlalchemy import text

from api_gateway.app.core.config import settings
from api_gateway.app.services.model_registry import ModelRegistry
from database.session import engine
from ensemble_engine.app.engine import ensemble_engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "api_gateway"}


@router.get("/health/details")
def health_details() -> dict:
    db_ok = True
    db_error = ""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_ok = False
        db_error = str(exc)

    models = ModelRegistry(settings.model_registry_file).load_models()
    ensemble = ensemble_engine.artifact_status()

    status = "ok" if db_ok else "degraded"
    return {
        "status": status,
        "service": "api_gateway",
        "database": {"ok": db_ok, "error": db_error},
        "model_registry": {
            "path": str(settings.model_registry_file),
            "count": len(models),
            "models": [m.get("name", "unknown") for m in models],
        },
        "ensemble_artifacts": ensemble,
        "policy": {
            "fail_open_on_model_error": settings.fail_open_on_model_error,
            "model_timeout": settings.model_timeout,
        },
    }
