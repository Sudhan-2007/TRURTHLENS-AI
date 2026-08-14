from app.config import settings
from app.db import connect_db
from app.main import app, lifespan


async def test_root_endpoint(client):
    res = await client.get("/")
    assert res.status_code == 200
    body = res.json()
    assert body["app"] == settings.APP_NAME
    assert body["version"] == settings.APP_VERSION


async def test_lifespan_startup_and_shutdown():
    async with lifespan(app):
        pass
    connect_db()


async def test_lifespan_handles_startup_failures(monkeypatch):
    import app.main as main_module

    async def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(main_module, "init_indexes", boom)
    monkeypatch.setattr(main_module, "seed_all", boom)
    monkeypatch.setattr(main_module, "refresh_approved_domains", boom)
    async with lifespan(app):
        pass
    connect_db()
