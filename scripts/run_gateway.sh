#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate
export PYTHONPATH=.
API_PORT="${API_PORT:-8000}"
python scripts/migrate.py
uvicorn api_gateway.app.main:app --host 0.0.0.0 --port "$API_PORT" --reload
