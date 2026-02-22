from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class DetectionRequest(Base):
    __tablename__ = "detection_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    verdict: Mapped[str] = mapped_column(String(10), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    ensemble_method: Mapped[str] = mapped_column(String(20), nullable=False)
    inference_time: Mapped[float] = mapped_column(Float, nullable=False)
    full_response_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
