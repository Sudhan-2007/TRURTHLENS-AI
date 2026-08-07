from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import auth as auth_router
from .api import news as news_router
from .api import users as users_router
from .config import settings
from .db import close_db, connect_db, init_indexes

MAX_REQUEST_BODY_BYTES = 64 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    try:
        await init_indexes()
    except Exception:
        pass
    yield
    close_db()


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
