
# ---------- base: dependencies + source ----------
FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY cli.py .

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=2)"

# ---------- dev: auto-reload (used by docker-compose.yml) ----------
FROM base AS dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---------- prod: non-root, no reload (used by docker-compose.prod.yml) ----------
# A single worker on purpose: the result cache is in-memory, so /api/cnf/{id}
# must reach the same process that handled the solve. Each solve still runs
# in its own child process, so several solves can run in parallel.
FROM base AS prod
RUN useradd --create-home --uid 10001 appuser
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
