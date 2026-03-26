# DeepGuard

DeepGuard is a production-style deepfake detection platform built as a microservice system. It combines a FastAPI gateway, model inference services, an ensemble engine, persistent audit history, and a React web UI for local development and demonstration environments.

## Purpose

DeepGuard is designed to demonstrate how a media authenticity workflow can be structured with:

- service isolation between gateway and model inference
- auditable request handling and persistence
- deterministic verdict generation
- a lightweight web interface for operators and demos

## Features

- FastAPI API gateway with auth, validation, rate limiting, and request logging
- distributed model microservices with ensemble orchestration
- duplicate media detection using SHA-256 fingerprinting
- SQLAlchemy-backed history and audit persistence
- role-based access control with `admin` and `viewer` users
- React + Vite web UI for token-driven uploads and verdict display
- Docker and Kubernetes deployment manifests
- cross-platform one-command installers for local setup

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, Uvicorn
- ML orchestration: ensemble fusion logic with joblib/scikit-learn artifacts
- Frontend: React, Vite
- Data store: SQLite by default, PostgreSQL via container deployment
- Tooling: Bash, PowerShell, Docker Compose, GitHub Actions

## Project Status

Status: active prototype / portfolio-ready system

The repository is structured and documented for production-style workflows, but maintainers should still review security settings, secrets handling, and deployment configuration before using it in a real production environment.

## Repository Layout

```text
.
├── api_gateway/        # FastAPI gateway, middleware, routes, tests
├── model_services/     # Model inference microservices
├── ensemble_engine/    # Fusion logic and serialized artifacts
├── database/           # Models, sessions, migrations
├── shared/             # Shared schemas, utilities, auth helpers
├── web_ui/             # React/Vite frontend
├── configs/            # Registry and runtime settings
├── deployments/        # Docker and Kubernetes manifests
├── scripts/            # Bootstrap, run, and data helper scripts
└── docs/               # Additional project documentation
```

## Architecture Overview

- API Gateway: request validation, auth, orchestration, logging, and history
- Model Services: independently deployed prediction endpoints
- Ensemble Engine: combines model outputs with voting, averaging, or stacking
- Web UI: browser-based upload and result display flow

## Installation

### One-Command Install

Requirements:

- Git
- Python 3.10+
- Node.js 18+
- A supported package manager: `apt`, `dnf`, `pacman`, `brew`, `winget`, or `choco`

Linux / macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/<user>/<repo>/main/install.sh | bash
```

Alternative:

```bash
wget -qO- https://raw.githubusercontent.com/<user>/<repo>/main/install.sh | bash
```

Windows PowerShell:

```powershell
iwr https://raw.githubusercontent.com/<user>/<repo>/main/install.ps1 -UseBasicParsing | iex
```

Security note:

- Review installer scripts before using pipe-to-shell commands.
- The installers avoid writing secrets into version-controlled files.
- `sudo` is only used when a supported package manager requires elevated access for missing dependencies.

### Manual Local Setup

1. Bootstrap the Python environment:

```bash
./scripts/bootstrap.sh
cp -n .env.example .env
```

2. Configure local model discovery:

```bash
cat > configs/models.local.yaml <<'EOF'
models:
  - name: model_a
    url: http://127.0.0.1:8001/predict
  - name: model_b
    url: http://127.0.0.1:8002/predict
EOF
```

3. Build the frontend:

```bash
npm --prefix web_ui ci
printf 'VITE_API_BASE=http://127.0.0.1:8000\n' > web_ui/.env.local
npm --prefix web_ui run build
```

4. Start local services:

```bash
MODEL_REGISTRY_PATH=configs/models.local.yaml ./scripts/run_services.sh
MODEL_REGISTRY_PATH=configs/models.local.yaml ./scripts/run_gateway.sh
npm --prefix web_ui run dev -- --host 127.0.0.1 --port 5173
```

## Usage

### Get an Access Token

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Submit a Prediction Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@sample.jpg"
```

### Manage Users

Create user:

```bash
curl -X POST "http://localhost:8000/auth/users" \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst1","password":"analyst123","role":"viewer","is_active":true}'
```

List users:

```bash
curl -X GET "http://localhost:8000/auth/users" \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### UI Preview

- Screenshot placeholder: `docs/screenshots/dashboard.png`
- Demo GIF placeholder: `docs/screenshots/prediction-flow.gif`

## Development

Run database migrations:

```bash
source .venv/bin/activate
python scripts/migrate.py
```

Run the backend test suite:

```bash
source .venv/bin/activate
python -m pytest
```

`./scripts/run_gateway.sh` runs migrations before starting the API.

## Deployment

Docker Compose:

```bash
cd deployments/docker
docker compose up --build
```

Kubernetes manifests are available in `deployments/k8s/`.

## Training Data

- Image training source: Kaggle
- Dataset slug: `shivamardeshna/real-and-fake-images-dataset-for-image-forensics`
- Dataset link: https://www.kaggle.com/datasets/shivamardeshna/real-and-fake-images-dataset-for-image-forensics
- Dataset helper script: `scripts/download_kaggle_dataset.sh`
- More details: `docs/training_data.md`

## Additional Documentation

- `docs/api.md`
- `docs/architecture.md`
- `docs/training_data.md`
- `docs/workflow_validation.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
