# TruthLens AI — Repository Guide

TruthLens AI is a fake-news detection platform. Users submit news articles, the
platform analyzes them with a DistilBERT model, verifies claims against official
sources, and produces trust scores, explanations, and dashboards.

Stack: FastAPI (backend) + React/Vite (frontend) + MongoDB + DistilBERT
(pyTorch), deployed with Docker Compose behind nginx. Runs on Windows (PowerShell);
default shell commands below are Windows-compatible.

## Repository layout

- `backend/` — FastAPI app. `app/api/` routers, `app/services/` business logic,
  `app/repositories/` persistence, `app/schemas/` pydantic models,
  `app/monitoring/metrics.py` Prometheus metrics, `app/config.py` settings.
- `frontend/` — React 19 + Vite + Tailwind. Scripts: `dev`, `build`, `lint`
  (oxlint), `test` (vitest).
- `ai-engine/` — training (`training/`), inference (`inference/predict.py`),
  datasets (`datasets/`), evaluation, and model artifacts under `models/`.
- `deployment/` — nginx config and ops scripts: `smoke_test.py`, `backup_db.py`,
  `restore_db.py`.
- `docs/` — `DEPLOYMENT.md`, `MONITORING.md`, `SOFTWARE_DESIGN_DOCUMENT.md`.
- `database/`, `testing/`, `tools/` — seed/config scripts and utilities.

## Configuration

- Root `.env` (gitignored) drives `docker compose` via interpolation. Copy
  `.env.example` first. `backend/.env` and `frontend/.env` are separate per-app.
- `backend/app/config.py` reads `MONGODB_URI` (alias `DATABASE_URL`). In
  production, startup FAILS if `JWT_SECRET` is `change-me` or < 32 chars, or if
  `DATABASE_URL` is a placeholder/local URI. Generate a secret with
  `openssl rand -hex 32`.
- Compose reads `DATABASE_URL` (not `MONGODB_URI`). MongoDB is pinned to
  `mongo:7.0.20` (immutable patch tag) — do not move back to rolling `mongo:7`.

## Commands

Backend (run from `backend\`, venv `.venv\Scripts\python.exe`):
- `..\ai-engine` tests require no DB; app tests need a running MongoDB
  (localhost:27017 or the compose service).
- `pytest -q` — run the suite (152 passing; asyncio auto mode; pytest-asyncio
  session-scoped loops).
- `uvicorn app.main:app --reload` — local dev server.

Frontend (run from `frontend\`):
- `npm run dev` — dev server (port 5173).
- `npm run build` — production build.
- `npm run lint` — oxlint.
- `npm test` — vitest (7 tests).

AI engine:
- `python tools\train_baseline.py` / `python tools\train_distilbert.py` — retrain
  models (reproducible; model artifacts are gitignored).

Docker (from repo root):
- `docker compose config` / `docker compose up -d` / `docker compose down`.
- Ops: `deployment\scripts\smoke_test.py --base http://localhost`,
  `backup_db.py`, `restore_db.py` (see `docs/DEPLOYMENT.md`).

## Conventions

- Backend: routers → services → repositories layering; pydantic schemas for
  request/response; errors returned as HTTPException with `detail`.
- Auth: bcrypt password hashes, JWT (HS256) in `Authorization: Bearer`.
- Observability: every router request is counted by the `metrics` middleware;
  keep `/health`, `/api/health`, `/api/health/db`, `/api/metrics` working.
- Tests: pytest-asyncio with `asyncio_mode = auto`; API tests use httpx
  AsyncClient; mark mongo-dependent tests to hit `truthlens_test` DB.
- Commits: short scope message, e.g. `P10: production deployment, monitoring,
  CI/CD, backup & docs`. Do not commit `.env` files or secrets.

## Gotchas

- Email validator rejects reserved TLDs such as `.local` — use `example.com`.
- Rolling `mongo:7`/`mongo:7.0` images were corrupt on this host; never revert
  the `mongo:7.0.20` pin without a fresh pull test.
- Health/`ai.loaded` reflects whether the transformer finished loading; on
  container start it is false until the model mounts and loads.
- CI requires `deployment-checks` (compose config validation) to pass before
  images build; workflow lives in `.github/workflows/ci.yml`.
