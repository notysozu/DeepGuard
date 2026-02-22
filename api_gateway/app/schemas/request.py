from typing import Literal

from pydantic import BaseModel, Field


class PredictMetadata(BaseModel):
    media_type: Literal["image", "video", "audio"]
    filename: str
    content_type: str
    size_bytes: int = Field(ge=1)
