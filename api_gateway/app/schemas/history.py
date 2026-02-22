from pydantic import BaseModel


class HistoryItem(BaseModel):
    request_id: str
    media_type: str
    verdict: str
    confidence: float
    ensemble_method: str
    inference_time: float
    created_at: str
