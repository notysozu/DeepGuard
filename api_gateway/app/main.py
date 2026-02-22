import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.app.api.routes.auth import router as auth_router
from api_gateway.app.api.routes.health import router as health_router
from api_gateway.app.api.routes.history import router as history_router
from api_gateway.app.api.routes.predict import router as predict_router
from api_gateway.app.core.config import settings
from api_gateway.app.core.logging import configure_logging
from api_gateway.app.middleware.exception_handler import ExceptionIsolationMiddleware
from api_gateway.app.middleware.payload_limit import PayloadLimitMiddleware
from api_gateway.app.middleware.rate_limit import RateLimitMiddleware
from api_gateway.app.middleware.request_logging import RequestLoggingMiddleware
from database.crud import ensure_default_user
from database.models import Base
from database.session import SessionLocal, engine

configure_logging()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ExceptionIsolationMiddleware)
app.add_middleware(PayloadLimitMiddleware, max_payload_mb=settings.max_payload_mb)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, limit_per_minute=settings.rate_limit_per_minute)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(predict_router)
app.include_router(history_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        ensure_default_user(
            db,
            username=os.getenv("APP_USERNAME", "admin"),
            password=os.getenv("APP_PASSWORD", "admin123"),
        )
    finally:
        db.close()
