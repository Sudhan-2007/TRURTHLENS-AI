async def test_health_endpoint_reports_components(client):
    res = await client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["environment"] in ("development", "testing", "production")
    assert body["version"]
    assert body["uptime_seconds"] >= 0
    assert body["database"]["connected"] is True
    assert body["database"]["status"] == "healthy"
    assert body["database"]["mode"] in ("local", "atlas")
    assert "distilbert_trained" in body["ai"]
    assert "backend" in body["ai"]
    assert "model_version" in body["ai"]


async def test_health_alias(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


async def test_health_db_reports_latency(client):
    res = await client.get("/api/health/db")
    assert res.status_code == 200
    body = res.json()
    assert body["connected"] is True
    assert body["ping_latency_ms"] >= 0
    assert body["mode"] in ("local", "atlas")


async def test_metrics_endpoint_exposes_prometheus_text(client):
    res = await client.get("/api/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    text = res.text
    assert "truthlens_http_requests_total" in text
    assert "truthlens_http_request_duration_seconds" in text
    assert "truthlens_database_up" in text
    assert "truthlens_uptime_seconds" in text
    assert "truthlens_ai_inferences_total" in text


async def test_metrics_tracks_requests(client):
    await client.get("/api/health")
    res = await client.get("/api/metrics")
    assert 'path="/api/health"' in res.text
    assert 'status="200"' in res.text


async def test_ai_metrics_recorded_after_inference(client):
    from .conftest import auth_headers, register_user
    from .test_news import submit_text

    await register_user(client)
    headers = await auth_headers(client)
    await submit_text(client, headers, content=(
        "Global average temperatures have increased by more than one degree "
        "Fahrenheit since the late 19th century. Scientists at NASA have "
        "confirmed the planet is getting warmer every decade."
    ))

    res = await client.get("/api/metrics")
    assert "truthlens_ai_inferences_total" in res.text
    assert 'prediction="REAL"' in res.text or 'prediction="FAKE"' in res.text
