# syntax=docker/dockerfile:1
# TruthLens AI backend + embedded ai-engine runtime.
# Build from the repository root:
#   docker build -f backend/Dockerfile -t truthlens-backend .
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# AI inference stack (CPU wheels for torch)
COPY ai-engine/requirements.txt /app/ai-engine/requirements.txt
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r /app/ai-engine/requirements.txt

COPY backend/app ./app
COPY ai-engine /app/ai-engine
COPY tools /app/tools
COPY deployment/scripts ./deployment/scripts

# Non-root runtime user (container must not run as root)
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app \
    && mkdir -p /backups \
    && chown -R appuser:appuser /backups

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
