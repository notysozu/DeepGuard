import hashlib
import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_TIMEOUT = float(os.getenv("MODEL_TIMEOUT", "30"))


class ModelInput(BaseModel):
    media_base64: str


app = FastAPI(title="Model A Service")


@app.post("/predict")
def predict(payload: ModelInput) -> dict:
    started = time.perf_counter()
    seed = int(hashlib.sha256(payload.media_base64.encode("utf-8")).hexdigest()[:8], 16)
    prob = (seed % 1000) / 1000.0
    elapsed = time.perf_counter() - started

    if elapsed > MODEL_TIMEOUT:
        raise HTTPException(status_code=504, detail="Inference timeout")

    return {
        "probability": round(prob, 4),
        "prediction": 1 if prob >= 0.5 else 0,
        "class": "fake" if prob >= 0.5 else "real",
        "inference_time": round(elapsed, 4),
    }
