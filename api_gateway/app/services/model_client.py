from __future__ import annotations

import asyncio
import time

import httpx



def _normalize_model_response(body: dict) -> dict | None:
    try:
        prob = float(body["probability"])
        prob = min(1.0, max(0.0, prob))
    except Exception:
        return None

    pred = body.get("prediction")
    if pred not in {0, 1}:
        pred = 1 if prob >= 0.5 else 0

    class_name = body.get("class")
    if class_name not in {"real", "fake"}:
        class_name = "fake" if pred == 1 else "real"

    try:
        inference_time = float(body.get("inference_time", 0.0))
    except Exception:
        inference_time = 0.0

    return {
        "probability": prob,
        "prediction": pred,
        "class": class_name,
        "inference_time": max(0.0, inference_time),
    }


async def _call_with_retry(
    client: httpx.AsyncClient,
    url: str,
    payload: dict,
    timeout: float,
    retries: int = 2,
) -> dict | None:
    for attempt in range(retries + 1):
        try:
            started = time.perf_counter()
            response = await client.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            body = response.json()
            body.setdefault("inference_time", round(time.perf_counter() - started, 4))
            return _normalize_model_response(body)
        except Exception:
            if attempt == retries:
                return None
            await asyncio.sleep(0.15)
    return None


async def query_models_parallel(
    model_urls: list[str],
    media_base64: str,
    timeout: float,
) -> list[dict]:
    payload = {"media_base64": media_base64}
    async with httpx.AsyncClient() as client:
        tasks = [
            _call_with_retry(client=client, url=url, payload=payload, timeout=timeout)
            for url in model_urls
        ]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
