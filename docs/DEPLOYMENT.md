# TruthLens AI — Deployment Guide

Production deployment for the TruthLens AI platform: backend (FastAPI +
Uvicorn), frontend (Vite + Nginx), MongoDB, and the AI inference engine,
orchestrated with Docker Compose and CI/CD on GitHub Actions.

## Architecture

```text
                 INTERNET
                    |
                    v
            +---------------+
            | Nginx (SPA)   |   frontend/ (port 80)
            |  /api -> backend
            +-------+-------+
                    |  /api, /health
                    v
            +---------------+
            | Uvicorn       |   backend/ (port 8000)
            | FastAPI app   |
            +-------+-------+
                    |  MONGODB_URI
                    v
            +---------------+
            | MongoDB 7     |   mongodb/ (port 27017)
            +---------------+
```

- The frontend image serves the built SPA from Nginx and reverse-proxies
  `/api/`, `/health`, and `/api/metrics` to the backend container.
- The backend image includes the AI inference engine. The DistilBERT and
  baseline model files are **not** baked into the image (see `.dockerignore`);
  the compose setup mounts `./ai-engine/models` from the host read-only.
  `AI_MODEL_PATH` points the engine at that directory. If the DistilBERT
  checkpoint is missing the predictor falls back to the baseline model, and
  inference errors loudly if neither model is present.
- Prometheus scrapes `/api/metrics`; see `docs/MONITORING.md`.

## Prerequisites

- Docker Engine + Docker Compose v2 on the target host.
- A production `JWT_SECRET` of at least 32 characters (generate with
  `python -c "import secrets; print(secrets.token_urlsafe(48))"`).
- Either a reachable MongoDB URI or the compose-managed MongoDB service.

## Environment Variables

See `backend/.env.example`, `frontend/.env.example`, and `.env.example` at the
repo root for the full annotated list. Production values are set in the CI/CD
deploy job or the host environment; **never commit `.env` files**.

| Variable | Required | Purpose |
| --- | --- | --- |
| `ENVIRONMENT` | yes | `development`, `testing`, or `production` |
| `MONGODB_URI` / `DATABASE_URL` | yes | MongoDB connection string; both names are accepted |
| `MONGODB_DB` | yes | Database name |
| `JWT_SECRET` | yes | ≥ 32 chars; production validator rejects `change-me` |
| `JWT_EXPIRE_MINUTES` | no | Token lifetime |
| `AI_MODEL_PATH` | no | Overrides the DistilBERT model directory |
| `TRUTHLENS_MODEL_BACKEND` | no | `distilbert` (default) or `baseline` |
| `SOURCE_API_KEYS` | no | JSON map of optional source API keys |
| `HTTP_PORT` | no | Host port for the frontend (default `80`) |

> The production validator **refuses to start** with a placeholder JWT secret
> or a placeholder/local MongoDB URI when `ENVIRONMENT=production`.

## Run Locally (Docker Compose)

```bash
export JWT_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
docker compose build
docker compose up -d
docker compose ps
```

Then:

- Frontend: `http://localhost` (default `HTTP_PORT`)
- Health: `http://localhost/health`
- Metrics: `http://localhost/api/metrics`

Post-deployment verification:

```bash
docker compose exec backend python deployment/scripts/smoke_test.py --base http://localhost
```

## CI/CD Pipeline (GitHub Actions)

`.github/workflows/ci.yml` implements:

1. **Backend tests** — spins up MongoDB 7 as a service, installs the backend and
   AI-engine requirements (CPU torch wheel), runs the full `pytest -q` suite
   against the `truthlens_test` database, and scans the backend/frontend source
   for accidentally committed secrets.
2. **Frontend checks** — `npm run lint`, `npm run test`, and `npm run build`.
3. **Docker images** — on `main` and `v*` tags, builds and pushes the
   `backend` and `frontend` images to `ghcr.io` (login-only on `main`).
4. **Deploy** — on `v*` tags only, runs in the `production` environment gate.
   Copies `docker-compose.yml` and a rendered `.env` to the host, pulls the
   tagged GHCR images, brings the stack up, and runs the smoke test against the
   public URL.

### Release Process

```bash
git tag v1.0.0
git push origin v1.0.0
```

The deploy job pulls the tagged images onto the production host
(`docker compose pull`), restarts the stack, and runs the post-deployment
smoke test.

### Production Host Setup (one-time)

1. Install Docker Engine + Compose v2 on the target host.
2. Create the release directory: `mkdir -p /opt/truthlens`.
3. Mount or copy the trained models so the backend can reach them, e.g.
   `rsync -av ./ai-engine/models/ root@host:/opt/truthlens/ai-engine/models/`
   (the compose setup mounts them read-only into the container).
4. Configure the GitHub Actions secrets below.

### Required GitHub Secrets

Set these on the `production` environment (Settings → Environments → production):

| Secret | Purpose |
| --- | --- |
| `PROD_HOST` | Production host IP or hostname |
| `PROD_USER` | SSH user with Docker access |
| `PROD_SSH_PRIVATE_KEY` | Deploy SSH private key |
| `PROD_KNOWN_HOSTS` | Host fingerprint (from `ssh-keyscan`) |
| `PROD_URL` | Public base URL for the post-deploy smoke test (e.g. `https://truthlens.example.com`) |
| `PROD_JWT_SECRET` | ≥ 32 chars; never reuse the local secret |
| `PROD_DATABASE_URL` | MongoDB connection string (Atlas or a managed host) |
| `PROD_MONGODB_DB` | Production database name |
| `PROD_CORS_ORIGINS` | Comma-separated allowed browser origins |
| `PROD_VITE_API_BASE_URL` | Usually empty (same-origin nginx proxy) |
| `GHCR_TOKEN` | GitHub PAT with `read:packages` so the host can pull images |

The deploy job interpolates these into the host `.env`; production startup
still refuses a placeholder JWT secret or local database URL.

## Backup and Restore

The backend image ships the ops scripts (`deployment/scripts/`) and the compose
setup mounts a persistent `backup-data` volume at `/backups`, so scheduled
backups run from inside the backend container with its `DATABASE_URL` already
configured:

```bash
# Manual backup (writes to the persistent backup-data volume)
docker compose exec backend python deployment/scripts/backup_db.py --out /backups

# Daily schedule (host crontab, e.g. 02:00 UTC)
0 2 * * * cd /opt/truthlens && docker compose exec -T backend python deployment/scripts/backup_db.py --out /backups >> /var/log/truthlens-backup.log 2>&1
```

Restore reads a local directory (not the container volume):

```bash
# From a machine with the backend venv and access to the database:
python deployment/scripts/restore_db.py --backup ./deployment/backups/truthlens_20260812_000000 --drop
```

Both scripts read `DATABASE_URL` or `MONGODB_URI` and refuse placeholder
connection strings. Backup strategy: daily full export, retained with the
scheduled job; restore is verified at least monthly (see
`docs/MONITORING.md`).

## Rollback

1. Re-tag the previous known-good image and re-run the deploy step:
   ```bash
   docker compose up -d --pull always
   ```
   with the previous tag in the compose/image reference.
2. If a data migration was the cause, restore the last backup:
   ```bash
   python deployment/scripts/restore_db.py --backup ./deployment/backups/<previous> --drop
   ```
3. Run the smoke test to confirm health before re-opening traffic.

## Operational Notes

- The backend healthcheck in `backend/Dockerfile` probes `/health`; the
  compose healthcheck waits for `database` connectivity and the `/health`
  endpoint.
- `/health`, `/api/health`, `/api/health/db`, and `/api/metrics` are public and
  intentionally **not** behind auth so load balancers and Prometheus can reach
  them without credentials.
- TLS termination is expected at the ingress/load balancer in front of the
  Nginx container.
