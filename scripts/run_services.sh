#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate

uvicorn model_services.model_a.app.main:app --host 0.0.0.0 --port 8001 &
uvicorn model_services.model_b.app.main:app --host 0.0.0.0 --port 8002 &
wait
