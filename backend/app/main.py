import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
from .seed import seed_all
from .services.source_service import refresh_approved_domains

configure_logging()

logger = logging.getLogger("truthlens.main")

MAX_REQUEST_BODY_BYTES = 64 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    try:
        await init_indexes()
    except Exception:
        pass
    try:
        await seed_all()
        await refresh_approved_domains()
    except Exception:
        pass
    logger.info("startup complete db_mode=%s db=%s", settings.db_mode, settings.MONGODB_DB)
    yield
    close_db()
    logger.info("shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
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
async def limit_request_body(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit():
        if int(content_length) > MAX_REQUEST_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body is too large"},
            )
    return await call_next(request)


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": f"{settings.APP_NAME} backend is running"}


@app.get("/api/health/db")
async def health_db():
    from .db import ping_db

    connected = await ping_db()
    return {
        "database": settings.MONGODB_DB,
        "connected": connected,
        "mode": settings.db_mode,
    }


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
