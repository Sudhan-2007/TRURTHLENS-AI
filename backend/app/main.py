import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from .api import ai as ai_router
from .api import auth as auth_router
from .api import dashboard as dashboard_router
from .api import explanation as explanation_router
from .api import history as history_router
from .api import news as news_router
from .api import trust_score as trust_score_router
from .api import users as users_router
from .api import verification as verification_router
from .config import settings
from .db import close_db, connect_db, init_indexes
from .logging_config import configure_logging
from .monitoring import metrics
from .seed import seed_all
from .services import ai_service
from .services.source_service import refresh_approved_domains

configure_logging()

logger = logging.getLogger("truthlens.main")

MAX_REQUEST_BODY_BYTES = 64 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    try:
        await init_indexes()
    except Exception as exc:  # noqa: BLE001 - non-fatal: indexes may already exist
        logger.warning("index initialization skipped: %s", exc)
    try:
        await seed_all()
        await refresh_approved_domains()
    except Exception as exc:  # noqa: BLE001 - non-fatal: seed data may already be present
        logger.warning("seed step failed: %s", exc)
    logger.info(
        "startup complete environment=%s db_mode=%s db=%s",
        settings.ENVIRONMENT,
        settings.db_mode,
        settings.MONGODB_DB,
    )
    yield
    close_db()
    logger.info("shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def observability(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        metrics.record_request(
            request.method, _route_path(request), 500, time.perf_counter() - start
        )
        raise
    duration = time.perf_counter() - start
    metrics.record_request(
        request.method, _route_path(request), response.status_code, duration
    )
    return response


@app.middleware("http")
async def limit_request_body(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if (
        content_length
        and content_length.isdigit()
        and int(content_length) > MAX_REQUEST_BODY_BYTES
    ):
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body is too large"},
        )
    return await call_next(request)


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path or request.url.path


async def _database_health() -> tuple[bool, float | None]:
    from .db import ping_db

    started = time.perf_counter()
    connected = await ping_db()
    return connected, time.perf_counter() - started


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/api/health")
@app.get("/health")
async def health():
    db_up, db_latency = await _database_health()
    metrics.record_database_health(db_up, db_latency)
    ai = ai_service.model_available()
    return {
        "status": "ok",
        "message": f"{settings.APP_NAME} backend is running",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "uptime_seconds": round(time.time() - metrics.START_TIME, 2),
        "database": {
            "status": "healthy" if db_up else "unhealthy",
            "connected": db_up,
            "mode": settings.db_mode,
            "name": settings.MONGODB_DB,
        },
        "ai": ai,
    }


@app.get("/api/health/db")
async def health_db():
    connected, latency = await _database_health()
    metrics.record_database_health(connected, latency)
    return {
        "database": settings.MONGODB_DB,
        "connected": connected,
        "mode": settings.db_mode,
        "ping_latency_ms": round((latency or 0.0) * 1000, 2),
    }


@app.get("/api/metrics")
async def metrics_endpoint():
    connected, latency = await _database_health()
    metrics.record_database_health(connected, latency)
    body, content_type = metrics.render_metrics()
    return Response(content=body, media_type=content_type)


app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(news_router.router)
app.include_router(ai_router.router)
app.include_router(verification_router.router)
app.include_router(verification_router.sources_router)
app.include_router(trust_score_router.router)
app.include_router(explanation_router.router)
app.include_router(dashboard_router.router)
app.include_router(history_router.router)
