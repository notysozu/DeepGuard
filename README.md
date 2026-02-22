<<<<<<< HEAD
# DeepGuard
=======
# DeepGuard

Production-style microservice-orchestrated deepfake detection system.

## Architecture

- FastAPI API Gateway (orchestration, auth, validation, logging)
- Distributed model microservices (`model_a`, `model_b`)
- Ensemble fusion engine (voting, averaging, stacking default)
- SHA-256 duplicate media fingerprinting
- Deterministic binary verdict only: `fake` or `real`
- SQLAlchemy persistence and audit trail
- React web UI with red/green signal

## Project Structure

```
.
├── api_gateway/
├── model_services/
├── ensemble_engine/
├── database/
├── shared/
├── web_ui/
├── configs/
├── deployments/
├── scripts/
├── docs/
├── README.md
├── .env.example
└── .gitignore
```

## Quick Start

1. Create environment and install dependencies:

```bash
./scripts/bootstrap.sh
cp .env.example .env
```

2. Start services locally:

```bash
./scripts/run_services.sh
./scripts/run_gateway.sh
```

3. Get JWT token:

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

4. Run prediction:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@sample.jpg"
```

## Docker Compose

```bash
cd deployments/docker
docker compose up --build
```
>>>>>>> 1e47f72 (Initial commit for DeepGuard)
