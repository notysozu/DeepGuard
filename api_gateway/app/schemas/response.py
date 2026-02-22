from typing import Literal

from pydantic import BaseModel


class ModelOutput(BaseModel):
    probability: float
    prediction: int
    class_name: Literal["real", "fake"]
    inference_time: float


class PredictResponse(BaseModel):
    request_id: str
    media_type: Literal["image", "video", "audio"]
    verdict: Literal["real", "fake"]
    confidence: float
    ensemble_method: str
    threshold: float
    model_count: int
    inference_time: float
    probability_fake: float
    duplicate_cache_hit: bool
