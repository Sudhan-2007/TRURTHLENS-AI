# TruthLens AI

Fake-news detection platform. Users submit news articles, the platform analyzes
them with a DistilBERT model, verifies claims against official sources, and
produces trust scores, explanations, and dashboards.

## Features

- **AI detection** — DistilBERT classifier (with a TF-IDF+LR baseline fallback)
  labels submissions REAL/FAKE with confidence levels.
- **Claim verification** — official-source matching and evidence collection
  with trust scoring.
- **Trust scores & explanations** — per-submission trust scores with
  machine-readable explanations.
- **Dashboards** — per-user history and analytics dashboards.
- **Production ready** — Docker Compose, nginx SPA/API proxy, Prometheus
  metrics, Grafana dashboards, Alertmanager rules, scheduled backups, and a
  tag-gated CI/CD pipeline with automated smoke tests.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI, Uvicorn, pydantic v2, motor/pymongo |
| Frontend | React 19, Vite, Tailwind CSS |
| AI | PyTorch, Hugging Face transformers (DistilBERT) |
| Database | MongoDB 7.0.20 |
| Ops | Docker Compose, nginx, GitHub Actions, Prometheus/Grafana |

## Repository Layout

```
backend/          FastAPI app (api/ routers, services/, repositories/, schemas/)
frontend/         React 19 + Vite + Tailwind app
ai-engine/        training/, inference/, datasets/, evaluation/, models/
deployment/       nginx config, ops scripts, monitoring stack, Docker compose
docs/             SOFTWARE_DESIGN_DOCUMENT.md, DEPLOYMENT.md, MONITORING.md
tools/            model training entry points
```

## Quickstart (Docker)

Prerequisites: Docker Engine + Compose v2, a strong `JWT_SECRET`.

```bash
cp .env.example .env      # then set JWT_SECRET (openssl rand -hex 32)
docker compose up -d --build
```

- Frontend: http://localhost
- Health: http://localhost/health
- Metrics: http://localhost/api/metrics
- Monitoring (optional): `docker compose -f deployment/docker-compose.monitoring.yml up -d`
  — Prometheus :9090, Alertmanager :9093, Grafana :3000

## Local Development

Backend (Python 3.13, from `backend/`):

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest -q                # requires MongoDB on localhost:27017
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev              # dev server on :5173
npm run lint && npm test && npm run build
```

AI engine (from repo root):

```bash
python tools\train_baseline.py      # fast TF-IDF baseline (reproducible)
python tools\train_distilbert.py    # DistilBERT (GPU recommended)
```

## Documentation

- `docs/SOFTWARE_DESIGN_DOCUMENT.md` — design, architecture, and phase status
  (Phases 1–10 complete).
- `docs/DEPLOYMENT.md` — production deployment, CI/CD, backup/restore,
  rollback.
- `docs/MONITORING.md` — metrics catalog, dashboards, alerts, maintenance
  schedule, model lifecycle.
- `AGENTS.md` — repository conventions for AI tooling.

## Testing

- Backend: 152 tests (`pytest -q` from `backend/`; requires MongoDB).
- AI engine: 14 unit tests (`pytest ai-engine/tests -q`; no DB or model
  artifacts needed).
- Frontend: 7 tests, oxlint, production build (all in CI).
- Ops: `deployment/scripts/smoke_test.py --base http://localhost`.

## License

Private project.
