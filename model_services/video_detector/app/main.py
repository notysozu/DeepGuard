import hashlib
import time

from fastapi import FastAPI
from pydantic import BaseModel


class ModelRequest(BaseModel):
    media_b64: str
    media_type: str


app = FastAPI(title="Video Detector")


@app.post("/predict")
def predict(req: ModelRequest) -> dict:
    started = time.perf_counter()
    seed = int(hashlib.sha1(req.media_b64.encode("utf-8")).hexdigest()[:6], 16)
    prob = (seed % 1000) / 1000.0
    return {
        "probability": round(prob, 4),
        "prediction": 1 if prob >= 0.5 else 0,
        "class": "fake" if prob >= 0.5 else "real",
        "inference_time": round(time.perf_counter() - started, 4),
    }
