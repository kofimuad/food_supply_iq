# FoodSupply IQ API — production image (FastAPI + uvicorn).
# Build context: the api/ directory (Railway service root = /api).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml ./
COPY app ./app
RUN pip install .

# Migrations + config (not part of the importable package).
COPY alembic ./alembic
COPY alembic.ini ./

EXPOSE 8000

# Alembic runs as Railway's preDeployCommand (see railway.json); this is the
# web process. $PORT is provided by Railway.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
