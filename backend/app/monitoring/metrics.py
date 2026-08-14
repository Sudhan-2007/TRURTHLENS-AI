"""Prometheus metrics for the TruthLens AI backend.

Exposes system/API/AI/database metrics in the standard Prometheus text format
via the /api/metrics endpoint. Metrics are in-process counters/gauges and are
safe to run in any environment.
"""

import time

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

from ..config import settings

START_TIME = time.time()

UPTIME = Gauge("truthlens_uptime_seconds", "Application uptime in seconds")
ENVIRONMENT = Gauge("truthlens_environment", "Current runtime environment (dev=0, test=1, prod=2)")

REQUEST_COUNT = Counter(
    "truthlens_http_requests_total",
    "Total HTTP requests handled",
    ["method", "path", "status"],
)

REQUEST_DURATION = Histogram(
    "truthlens_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

API_ERRORS = Counter(
    "truthlens_http_errors_total",
    "HTTP requests that returned a 5xx status",
    ["method", "path"],
)

DB_STATUS = Gauge("truthlens_database_up", "1 if the database is reachable, else 0")
DB_LATENCY = Gauge(
    "truthlens_database_ping_latency_seconds", "Last database ping latency in seconds"
)

AI_INFERENCE_COUNT = Counter(
    "truthlens_ai_inferences_total",
    "AI inference calls completed",
    ["prediction", "model_name"],
)

AI_LOW_CONFIDENCE = Counter(
    "truthlens_ai_low_confidence_total", "AI predictions below the low-confidence bar"
)

AI_INFERENCE_DURATION = Histogram(
    "truthlens_ai_inference_duration_seconds",
    "AI inference duration in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

AI_ERRORS = Counter("truthlens_ai_errors_total", "AI inference failures")

AI_MODEL_INFO = Info("truthlens_ai_model", "Active AI model metadata")


def record_request(method: str, path: str, status_code: int, duration: float) -> None:
    REQUEST_COUNT.labels(method=method, path=path, status=str(status_code)).inc()
    REQUEST_DURATION.labels(method=method, path=path).observe(duration)
    if status_code >= 500:
        API_ERRORS.labels(method=method, path=path).inc()


def record_database_health(up: bool, latency: float | None = None) -> None:
    DB_STATUS.set(1 if up else 0)
    if latency is not None:
        DB_LATENCY.set(latency)


def record_ai_inference(
    prediction: str,
    model_name: str,
    model_version: str,
    duration_ms: float,
    low_confidence: bool,
    backend: str = "",
) -> None:
    AI_INFERENCE_COUNT.labels(prediction=prediction, model_name=model_name).inc()
    AI_INFERENCE_DURATION.observe(duration_ms / 1000.0)
    if low_confidence:
        AI_LOW_CONFIDENCE.inc()
    AI_MODEL_INFO.info(
        {
            "model_name": model_name,
            "model_version": model_version,
            "backend": backend,
        }
    )


def record_ai_error() -> None:
    AI_ERRORS.inc()


def record_ai_model_info(model_name: str, model_version: str, backend: str) -> None:
    AI_MODEL_INFO.info(
        {"model_name": model_name, "model_version": model_version, "backend": backend}
    )


def render_metrics() -> tuple[bytes, str]:
    UPTIME.set(time.time() - START_TIME)
    ENVIRONMENT.set(("development", "testing", "production").index(settings.ENVIRONMENT))
    return generate_latest(), CONTENT_TYPE_LATEST
