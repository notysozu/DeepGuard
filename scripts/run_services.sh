#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate
MODEL_A_PORT="${MODEL_A_PORT:-8001}"
MODEL_B_PORT="${MODEL_B_PORT:-8002}"

uvicorn model_services.model_a.app.main:app --host 0.0.0.0 --port "$MODEL_A_PORT" &
uvicorn model_services.model_b.app.main:app --host 0.0.0.0 --port "$MODEL_B_PORT" &
wait
