# TruthLens AI — How to Run (everything in one place)

Project root: `C:\Users\sudha\OneDrive\Desktop\TRUTHLENS AI 1`.
OS: Windows / PowerShell. See `AGENTS.md` for conventions and gotchas.

## Quick reference (before running)

| Layer | Command | Where | Result |
| --- | --- | --- | --- |
| Full stack | `docker compose up -d` | repo root | App at http://localhost |
| Backend API | `uvicorn app.main:app --reload` | `backend/` | http://localhost:8000 |
| Frontend dev | `npm run dev` | `frontend/` | http://localhost:5173 |
| AI baseline | `python tools\train_baseline.py` | repo root | model artifact |
| AI DistilBERT | `python tools\train_distilbert.py` | repo root | model artifact (GPU) |

Endpoints:
- App (Docker): http://localhost — API health: http://localhost/health —
  metrics: http://localhost/api/metrics
- Seed data (official sources + evidence) loads automatically at backend startup.

## Option A — Full stack (Docker) — recommended for the whole app

```powershell
# from project root
docker compose up -d --build --no-cache   # --no-cache avoids the OneDrive BuildKit stale-cache bug
docker compose ps                          # wait until frontend/backend/mongodb are healthy
```

- `.env` already exists at repo root. Only change `JWT_SECRET` if you want a new
  one: `openssl rand -hex 32`.
- Stop everything: `docker compose down`. Monitoring stack is separate:
  `docker compose -f deployment/docker-compose.monitoring.yml up -d`.
- Validate compose without building: `docker compose config`.

## Option B — Backend local dev

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload             # http://localhost:8000
```

- Backend env: `backend\.env` (`MONGODB_URI=mongodb://localhost:27017`); see
  `backend\.env.example` for all variables.
- Uses `backend/.venv` (Python 3.13).

## Option C — Frontend local dev

```powershell
cd frontend
npm install
npm run dev                                # http://localhost:5173
npm run lint; npm test; npm run build      # lint + tests + prod build
```

- Frontend env: `frontend\.env` (`VITE_API_URL`); see `frontend\.env.example`.
- Add `"proxy": "http://localhost:8000"` to `vite.config.js` to hit the backend
  directly during dev if needed.

## AI engine (retrain models)

```powershell
# from repo root
python tools\train_baseline.py          # fast TF-IDF baseline (reproducible)
python tools\train_distilbert.py        # DistilBERT (GPU recommended)
```

- Model artifacts are gitignored under `ai-engine/models/`.
- If the container serves an old bundle after retraining, rebuild with
  `docker compose build --no-cache <svc>` (OneDrive BuildKit gotcha).

## Tests & quality gates

| Layer | Command | Gate |
| --- | --- | --- |
| Backend tests | `pytest -q` (from `backend/`, needs MongoDB) | 229 tests, 99% cov (CI >= 85%) |
| Backend lint | `ruff check app tests` + `ruff format --check app tests` | clean |
| AI-engine | `pytest ai-engine\tests -q` (from repo root) | 14 tests |
| Frontend tests | `npm run test:coverage` (from `frontend/`) | 107 tests, >= 80% lines / >= 75% branches (93% actual) |
| Frontend lint | `npm run lint` | oxlint clean |
| Smoke test | `python deployment\scripts\smoke_test.py --base http://localhost` | all PASS |

## Troubleshooting

- Backend tests fail to connect: start MongoDB (`docker compose up -d mongodb`
  or run MongoDB on localhost:27017).
- `/health` shows `ai.loaded: false`: DistilBERT artifact not mounted in the
  container — expected until retrained/mounted; TF-IDF baseline is the fallback.
- Email validator rejects reserved TLDs (`.local`) — use `example.com`.
- Mongo is pinned to `mongo:7.0.20` — never revert to rolling `mongo:7`.

## Handoff / next steps

See `docs/HANDOFF-ANTIGRAVITY.md` for status and suggested next steps
(release checkpoint, model loading, or Phase 11 scope).