from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import connect_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
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
