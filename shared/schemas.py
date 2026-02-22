from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    role: Literal["admin", "viewer"] = "viewer"
    is_active: bool = True


class UserPublic(BaseModel):
    id: str
    username: str
    role: Literal["admin", "viewer"]
    is_active: bool
    created_at: datetime


class UsersResponse(BaseModel):
    items: list[UserPublic]


class ModelRequest(BaseModel):
    media_base64: str


class ModelResponse(BaseModel):
    probability: float = Field(ge=0.0, le=1.0)
    prediction: Literal[0, 1]
    class_name: Literal["real", "fake"] = Field(alias="class")
    inference_time: float = Field(ge=0.0)

    class Config:
        populate_by_name = True


class PredictionResponse(BaseModel):
    request_id: str
    media_type: Literal["image", "video", "audio"]
    verdict: Literal["fake", "real"]
    confidence: float = Field(ge=0.0, le=1.0)
    ensemble_method: str
    model_count: int = Field(ge=0)
    inference_time: float = Field(ge=0.0)
    duplicate_cache_hit: bool


class HistoryItem(BaseModel):
    id: str
    media_type: str
    sha256_hash: str
    verdict: str
    confidence: float
    ensemble_method: str
    inference_time: float
    created_at: datetime


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
