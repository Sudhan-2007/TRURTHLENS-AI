# TruthLens AI — Monitoring and Maintenance Guide

Operational monitoring for the TruthLens AI platform: Prometheus metrics,
health endpoints, alerting guidance, and the maintenance schedule from the
system specification.

## Endpoints

| Endpoint | Purpose | Auth |
| --- | --- | --- |
| `/health` | Liveness/readiness (JSON: status, DB, AI availability) | none |
| `/api/health` | Full health payload (environment, version, uptime, DB, AI) | none |
| `/api/health/db` | Database connectivity + ping latency | none |
| `/api/metrics` | Prometheus text exposition format | none |

Example:

```json
{
  "status": "ok",
  "environment": "production",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "database": { "status": "healthy", "connected": true, "mode": "local", "name": "truthlens" },
  "ai": { "loaded": true, "backend": "distilbert", "distilbert_trained": true, "model_version": "1.0.0" }
}
```

## Metrics Catalog

Exposed via `backend/app/monitoring/metrics.py` and the `/api/metrics` endpoint
(same-origin; Prometheus can scrape the Nginx proxy directly).

### HTTP / service

| Metric | Type | Labels | Meaning |
| --- | --- | --- | --- |
| `truthlens_http_requests_total` | counter | `method`, `path`, `status` | Requests handled |
| `truthlens_http_request_duration_seconds` | histogram | `method`, `path` | Request latency |
| `truthlens_http_errors_total` | counter | `method`, `path` | 4xx/5xx responses |
| `truthlens_database_up` | gauge | — | 1 if MongoDB reachable, else 0 |
| `truthlens_database_ping_latency_seconds` | gauge | — | Last ping round-trip |
| `truthlens_uptime_seconds` | gauge | — | Process uptime |
| `truthlens_environment` | gauge | — | 0=dev, 1=test, 2=prod |

### AI inference

| Metric | Type | Labels | Meaning |
| --- | --- | --- | --- |
| `truthlens_ai_inferences_total` | counter | `prediction`, `model_name` | Completed inferences |
| `truthlens_ai_inference_duration_seconds` | histogram | — | Inference latency |
| `truthlens_ai_low_confidence_total` | counter | — | Low-confidence results flagged |
| `truthlens_ai_errors_total` | counter | — | Inference failures |
| `truthlens_ai_model_info` | gauge | `backend`, `distilbert_trained`, `model_version` | Active model metadata |

## Prometheus / Grafana Setup

The monitoring stack ships in the repo under `deployment/monitoring/`
(Prometheus config, alert rules, and Grafana provisioning with a pre-built
TruthLens dashboard) and runs alongside the main stack with a second compose
file:

```bash
# from deployment\
docker compose -f docker-compose.monitoring.yml up -d
```

- Prometheus: `http://localhost:9090` (scrapes `frontend:80/api/metrics`).
- Grafana: `http://localhost:3000` (default `admin`/`admin`; set
  `GRAFANA_ADMIN_PASSWORD` in `.env` next to the monitoring compose file on
  shared deployments). The datasource is auto-provisioned and the
  "TruthLens AI — Platform Overview" dashboard loads under the TruthLens
  folder.
- Alertmanager: `http://localhost:9093`. Alerts route to the `default`
  receiver; set your destination URL in
  `deployment/monitoring/alertmanager.yml` (e.g. Slack/PagerDuty/email
  webhook) and restart the container.

Files:

- `deployment/monitoring/prometheus.yml` — scrape config + alertmanager
  wiring.
- `deployment/monitoring/rules/alerts.yml` — the alert rules below.
- `deployment/monitoring/alertmanager.yml` — routing/receiver config.
- `deployment/monitoring/grafana/provisioning/` — datasource + dashboard
  provisioning.
- `deployment/monitoring/grafana/dashboards/truthlens.json` — dashboard.

The dashboard surfaces: request rate and error rate by path, p95/p99 latency,
database up/latency, inference rate by prediction, low-confidence rate, and
model version changes (`truthlens_ai_model_info` value flip).

## Recommended Alerts

| Alert | Condition | Severity |
| --- | --- | --- |
| Backend down | `up{job="truthlens"} == 0` | critical |
| Database unreachable | `truthlens_database_up == 0` | critical |
| Elevated error rate | `rate(truthlens_http_errors_total[5m]) / rate(truthlens_http_requests_total[5m]) > 0.05` | warning |
| High latency | `histogram_quantile(0.95, rate(truthlens_http_request_duration_seconds_bucket[5m])) > 3` | warning |
| Model failures | `rate(truthlens_ai_errors_total[5m]) > 0` | warning |
| Low-confidence spike | `rate(truthlens_ai_low_confidence_total[5m]) > 10` | info |
| Model version change | `changes(truthlens_ai_model_info[1h]) > 0` | info |

## Maintenance Schedule

### Daily

- Run the database backup (see `docs/DEPLOYMENT.md` → Backup and Restore):
  `docker compose exec backend python deployment/scripts/backup_db.py --out /backups`
- Check the health dashboard; confirm `truthlens_database_up == 1` and the AI
  backend is loaded (`ai.loaded == true` in `/api/health`).
- Review any new `warning`-level alerts.

### Weekly

- Review error rates, p95 latency, and low-confidence trends.
- Confirm backups succeeded each day and spot-check a backup manifest
  (`manifest.json`) for expected collection counts.

### Monthly

- Restore-test the latest backup into a scratch database:
  `python deployment/scripts/restore_db.py --backup ./deployment/backups/<latest> --db truthlens_restore_test`
- Review the AI model's confusion metrics from the evaluation suite
  (`ai-engine/evaluation/`) and decide whether to retrain (see model lifecycle
  below).
- Rotate the `JWT_SECRET` and re-run the smoke test
  (`deployment/scripts/smoke_test.py`).

## Model Maintenance Lifecycle

1. **Evaluate** — run the evaluation harness; capture accuracy/precision/
   recall/F1.
2. **Retrain** — train on an updated dataset in `ai-engine/`.
3. **Stage** — mount the new model directory and set `AI_MODEL_PATH` on a
   staging environment; verify `ai.model_version` and inference health.
4. **Promote** — update `AI_MODEL_PATH` in production; confirm
   `truthlens_ai_model_info` flips to the new version and error rate stays flat.
5. **Rollback** — revert `AI_MODEL_PATH` to the previous model directory.

The `truthlens_ai_model_info` change alert makes unintended model swaps visible.

## Incident Response

1. Smoke test: `python deployment/scripts/smoke_test.py --base http://localhost`.
2. If the backend is down: `docker compose restart backend`, check logs with
   `docker compose logs --tail=200 backend`.
3. If the database is down: check the MongoDB container health, then restore
   from the latest backup (see `docs/DEPLOYMENT.md` → Rollback).
4. If the AI model fails: confirm the model directory exists and is readable;
   the backend falls back to the baseline backend automatically, which should
   be visible in `ai.backend` in `/api/health`.
