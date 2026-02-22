from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from passlib.context import CryptContext
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from database.models import DetectionRequest, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_username(db: Session, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return db.scalars(stmt).first()


def list_users(db: Session, limit: int = 100) -> list[User]:
    stmt = select(User).order_by(User.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())


def create_user(
    db: Session,
    username: str,
    password: str,
    role: str = "viewer",
    is_active: bool = True,
) -> User:
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        hashed_password=get_password_hash(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ensure_default_user(db: Session, username: str, password: str, role: str = "viewer") -> User:
    existing = get_user_by_username(db, username)
    if existing:
        return existing
    return create_user(db, username, password, role=role)


def save_detection(db: Session, payload: dict[str, Any]) -> DetectionRequest:
    row = DetectionRequest(
        id=payload["id"],
        media_type=payload["media_type"],
        sha256_hash=payload["sha256_hash"],
        verdict=payload["verdict"],
        confidence=payload["confidence"],
        ensemble_method=payload["ensemble_method"],
        inference_time=payload["inference_time"],
        full_response_json=json.dumps(payload["full_response_json"]),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_history(
    db: Session,
    *,
    limit: int = 100,
    offset: int = 0,
    media_type: str | None = None,
    verdict: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
) -> tuple[list[DetectionRequest], int]:
    stmt = select(DetectionRequest)
    count_stmt = select(func.count(DetectionRequest.id))

    if media_type:
        stmt = stmt.where(DetectionRequest.media_type == media_type)
        count_stmt = count_stmt.where(DetectionRequest.media_type == media_type)
    if verdict:
        stmt = stmt.where(DetectionRequest.verdict == verdict)
        count_stmt = count_stmt.where(DetectionRequest.verdict == verdict)
    if created_after:
        stmt = stmt.where(DetectionRequest.created_at >= created_after)
        count_stmt = count_stmt.where(DetectionRequest.created_at >= created_after)
    if created_before:
        stmt = stmt.where(DetectionRequest.created_at <= created_before)
        count_stmt = count_stmt.where(DetectionRequest.created_at <= created_before)

    total = int(db.scalar(count_stmt) or 0)
    stmt = stmt.order_by(desc(DetectionRequest.created_at)).offset(offset).limit(limit)
    return list(db.scalars(stmt).all()), total


def get_by_request_id(db: Session, request_id: str) -> DetectionRequest | None:
    return db.get(DetectionRequest, request_id)


def check_hash_exists(db: Session, sha256_hash: str) -> DetectionRequest | None:
    stmt = select(DetectionRequest).where(DetectionRequest.sha256_hash == sha256_hash)
    return db.scalars(stmt).first()
