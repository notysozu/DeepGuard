# DeepGuard

> A microservice-based deepfake detection platform for authenticated media analysis, auditability, and local demo environments.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#installation)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb.svg)](#tech-stack)

DeepGuard is a production-style deepfake detection system built around a FastAPI gateway, independent model services, ensemble fusion, persistent detection history, and a React web UI. It is designed as a strong reference project for media authenticity workflows, service orchestration, and developer onboarding.

## Overview

DeepGuard helps teams evaluate uploaded media through an authenticated API and a lightweight browser UI. It exists to show how a deepfake detection workflow can be structured with clear service boundaries, deterministic verdict handling, duplicate detection, and auditable request history.

This repository is best suited for:

- learning or demonstrating a microservice-based AI detection architecture
- prototyping authenticated image or video analysis workflows
- experimenting with ensemble inference and audit logging patterns

## Features

- Authenticated FastAPI gateway with JWT login, request validation, rate limiting, and request logging
- Parallel model-service orchestration with voting, averaging, and stacking ensemble strategies
- SHA-256 media fingerprinting to detect duplicates and reuse cached verdicts
- Persistent audit history backed by SQLAlchemy
- Role-based access control with default `admin` and `viewer` users
- React + Vite web UI for token-based uploads and verdict display
- Docker Compose and Kubernetes manifests for deployment experiments
- Cross-platform installer scripts for local setup on Linux, macOS, and Windows

## Demo / Preview

Local development endpoints:

| Surface | URL |
| --- | --- |
| Web UI | `http://127.0.0.1:5173` |
| API | `http://127.0.0.1:8000` |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| Health check | `http://127.0.0.1:8000/health` |

Repository assets:

- Sample media asset for testing: [`sample.png`](sample.png)
- Screenshot placeholder path: `docs/screenshots/dashboard.png`
- Demo GIF placeholder path: `docs/screenshots/prediction-flow.gif`

If you plan to share the project publicly, adding a short screen recording of the upload-to-verdict flow would make this repository much easier to evaluate at a glance.

## Installation

### Requirements

- Git
- Python 3.10+
- Node.js 18+
- One of: `apt`, `dnf`, `pacman`, `brew`, `winget`, or `choco` for the install scripts

### Option 1: One-command install

The installer prepares the Python environment, installs frontend dependencies, creates local config files, starts the API and model services, and launches the Vite dev server.

Linux / macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/notysozu/DeepGuard/main/install.sh | bash
```

Alternative:

```bash
wget -qO- https://raw.githubusercontent.com/notysozu/DeepGuard/main/install.sh | bash
```

Windows PowerShell:

```powershell
iwr https://raw.githubusercontent.com/notysozu/DeepGuard/main/install.ps1 -UseBasicParsing | iex
```

Security note:

- Review installer scripts before using pipe-to-shell commands.
- The installers do not write secrets into tracked files.
- `sudo` is only used when a supported package manager needs elevated access to install missing dependencies.

### Option 2: Manual local setup

1. Clone the repository and enter the project directory.

```bash
git clone https://github.com/notysozu/DeepGuard.git
cd DeepGuard
```

2. Create the Python environment and local `.env`.

```bash
./scripts/bootstrap.sh
cp -n .env.example .env
```

3. Create a localhost model registry for development.

```bash
cat > configs/models.local.yaml <<'EOF'
models:
  - name: model_a
    url: http://127.0.0.1:8001/predict
  - name: model_b
    url: http://127.0.0.1:8002/predict
EOF
```

4. Point the frontend and gateway to local services.

```bash
printf 'VITE_API_BASE=http://127.0.0.1:8000\n' > web_ui/.env.local
```

5. Install frontend dependencies and build the UI.

```bash
npm --prefix web_ui ci
npm --prefix web_ui run build
```

6. Start the model services, API gateway, and frontend dev server in separate terminals.

```bash
MODEL_REGISTRY_PATH=configs/models.local.yaml ./scripts/run_services.sh
```

```bash
MODEL_REGISTRY_PATH=configs/models.local.yaml ./scripts/run_gateway.sh
```

```bash
npm --prefix web_ui run dev -- --host 127.0.0.1 --port 5173
```

### Default local credentials

The gateway seeds default users on startup from [`.env.example`](.env.example):

- Admin: `admin` / `admin123`
- Viewer: `viewer` / `viewer123`

Change these values before using the project outside local demos.

## Usage

### 1. Get an access token

```bash
curl -X POST "http://127.0.0.1:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 2. Submit a prediction request

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@sample.png"
```

Example response:

```json
{
  "request_id": "uuid",
  "media_type": "image",
  "verdict": "fake",
  "confidence": 0.91,
  "ensemble_method": "stacking",
  "model_count": 2,
  "inference_time": 0.24,
  "duplicate_cache_hit": false
}
```

### 3. Create and list users

Create a viewer user:

```bash
curl -X POST "http://127.0.0.1:8000/auth/users" \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst1","password":"analyst123","role":"viewer","is_active":true}'
```

List users:

```bash
curl -X GET "http://127.0.0.1:8000/auth/users" \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

### 4. Inspect health and history

```bash
curl http://127.0.0.1:8000/health
curl -H "Authorization: Bearer <ADMIN_TOKEN>" http://127.0.0.1:8000/history
```

### Supported media

- API routes currently accept authenticated image and video uploads
- MIME validation helpers in the repository also include audio types for future expansion
- The default local quickstart runs `model_a` and `model_b`, which are sample model services used for demonstration

## Tech Stack

| Area | Technologies |
| --- | --- |
| Backend API | Python, FastAPI, Uvicorn |
| Data & persistence | SQLAlchemy, SQLite, PostgreSQL |
| Model orchestration | HTTPX, Joblib, scikit-learn, NumPy |
| Frontend | React, Vite, lucide-react |
| Config & tooling | Bash, PowerShell, PyYAML, Docker Compose, Kubernetes manifests |

## Project Structure

```text
.
├── api_gateway/        # FastAPI gateway, routes, middleware, tests
├── model_services/     # Independent inference services and test scaffolds
├── ensemble_engine/    # Fusion strategies and serialized ensemble artifacts
├── database/           # ORM models, migrations, session management
├── shared/             # Shared schemas, validation, security helpers
├── web_ui/             # React + Vite frontend
├── configs/            # Runtime settings and model registry definitions
├── deployments/        # Docker and Kubernetes deployment assets
├── scripts/            # Bootstrap, run, migration, and dataset helpers
└── docs/               # API, architecture, workflow, and training-data docs
```

## Roadmap / Status

Current state:

- Active prototype and portfolio-ready reference implementation
- Strong local developer workflow with API, UI, and deployment assets
- Best used for demos, experimentation, and architecture learning rather than unattended production use

Near-term improvement areas:

- add real screenshots or GIF walkthroughs
- expand multimodal model coverage beyond the default sample services
- harden deployment defaults, secrets handling, and production security posture
- add CI badges and release metadata

## Development

Run database migrations:

```bash
source .venv/bin/activate
python scripts/migrate.py
```

Run tests:

```bash
source .venv/bin/activate
python -m pytest
```

Run with Docker Compose:

```bash
cd deployments/docker
docker compose up --build
```

More documentation:

- [`docs/api.md`](docs/api.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/training_data.md`](docs/training_data.md)
- [`docs/workflow_validation.md`](docs/workflow_validation.md)
- [`SECURITY.md`](SECURITY.md)

Kubernetes manifests are available in `deployments/k8s/`.

Training data reference:

- Kaggle dataset slug: `shivamardeshna/real-and-fake-images-dataset-for-image-forensics`
- Dataset helper: `scripts/download_kaggle_dataset.sh`
- Details: [`docs/training_data.md`](docs/training_data.md)

## Contributing

Contributions are welcome. Start with the setup and testing flow above, keep pull requests focused, and update tests when behavior changes.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contributor workflow, coding standards, and commit conventions.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.
