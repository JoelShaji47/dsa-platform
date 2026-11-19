# DSA Platform API — Render Docker runtime.
# Self-contained: Python version pinned here (Render native maxes out below
# 3.14), LightGBM's libgomp included, migrations run on every boot
# (idempotent `upgrade head`, so deploys never run on a stale schema).

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# libgomp1 = LightGBM runtime. No compilers needed (all wheels).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini alembic.ini
COPY alembic/ alembic/
COPY app/ app/
# Trained recommender artifacts are gitignored but force-added for deployment;
# .dockerignore whitelists only the served model files.
COPY artifacts/ artifacts/

EXPOSE 8000

# $PORT is injected by Render. Migrate first so a fresh push can't boot
# against an old schema (Supabase is the target via DATABASE_URL).
CMD ["sh", "-c", "python -m alembic upgrade head && exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
