from __future__ import annotations

import base64
import json
import logging
import time
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from api_gateway.app.core.config import settings
from api_gateway.app.services.classifier import classify_binary
from api_gateway.app.services.model_client import query_models_parallel
from api_gateway.app.services.model_registry import ModelRegistry
from database.crud import check_hash_exists, save_detection
from shared.hash_utils import generate_sha256
from shared.media_validation import validate_media_upload

logger = logging.getLogger("deepguard.predict")



def public_response(payload: dict) -> dict:
    return {
        "request_id": payload["request_id"],
        "media_type": payload["media_type"],
        "verdict": payload["verdict"],
        "confidence": payload["confidence"],
        "ensemble_method": payload["ensemble_method"],
        "model_count": payload["model_count"],
        "inference_time": payload["inference_time"],
        "duplicate_cache_hit": payload["duplicate_cache_hit"],
    }


async def run_prediction(file: UploadFile, db: Session) -> dict:
    request_id = str(uuid.uuid4())
    started = time.perf_counter()

    file_bytes, metadata = await validate_media_upload(
        file,
        max_payload_mb=settings.max_payload_mb,
        max_image_pixels=settings.max_image_pixels,
    )
    sha256_hash = generate_sha256(file_bytes)

    existing = check_hash_exists(db, sha256_hash)
    if existing:
        cached = json.loads(existing.full_response_json)
        cached["duplicate_cache_hit"] = True
        logger.info(
            "request_id=%s media_type=%s sha256=%s verdict=%s cache_hit=true",
            existing.id,
            existing.media_type,
            existing.sha256_hash,
            existing.verdict,
        )
        return public_response(cached)

    media_base64 = base64.b64encode(file_bytes).decode("utf-8")
    model_defs = ModelRegistry(settings.model_registry_file).load_models()
    model_urls = [m["url"] for m in model_defs if "url" in m]

    model_results = await query_models_parallel(
        model_urls=model_urls,
        media_base64=media_base64,
        timeout=settings.model_timeout,
    )

    if not model_results:
        # Fail-open deterministic fallback keeps service available when all model services fail.
        model_results = [
            {"probability": 0.5, "prediction": 1, "class": "fake", "inference_time": 0.0}
        ]

    verdict, confidence, ensemble_method = classify_binary(
        model_outputs=model_results,
        threshold=settings.fake_threshold,
    )

    inference_time = round(time.perf_counter() - started, 4)
    full_response = {
        "request_id": request_id,
        "media_type": metadata["media_type"],
        "verdict": verdict,
        "confidence": confidence,
        "ensemble_method": ensemble_method,
        "model_count": len(model_results),
        "inference_time": inference_time,
        "duplicate_cache_hit": False,
    }

    save_detection(
        db,
        {
            "id": request_id,
            "media_type": metadata["media_type"],
            "sha256_hash": sha256_hash,
            "verdict": verdict,
            "confidence": confidence,
            "ensemble_method": ensemble_method,
            "inference_time": inference_time,
            "full_response_json": full_response,
        },
    )
    logger.info(
        "request_id=%s media_type=%s sha256=%s verdict=%s confidence=%.4f method=%s inference_time=%.4f",
        request_id,
        metadata["media_type"],
        sha256_hash,
        verdict,
        confidence,
        ensemble_method,
        inference_time,
    )

    return public_response(full_response)
