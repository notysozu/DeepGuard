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
- Role-based access control (`admin`, `viewer`)

## Training Data (Highlighted)

- Image training source: Kaggle
- Dataset slug: `shivamardeshna/real-and-fake-images-dataset-for-image-forensics`
- Dataset link: https://www.kaggle.com/datasets/shivamardeshna/real-and-fake-images-dataset-for-image-forensics
- Detailed reference: `docs/training_data.md`

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

3. Get admin JWT token:

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

## Admin User Management

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

## Migrations

```bash
source .venv/bin/activate
python scripts/migrate.py
```

`./scripts/run_gateway.sh` runs migrations before starting the API.

## Docker Compose

```bash
cd deployments/docker
docker compose up --build
```
