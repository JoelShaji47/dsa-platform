# Agent Instructions: DSA Platform

## Operational Gotchas (CRITICAL)

### Judge0 + Apple Silicon (Rosetta)
The Judge0 CE amd64 image runs under Rosetta 2. Standard `isolate` per-process sandboxing fails here.
- **Fix**: `enable_per_process_and_thread_time_limit` and `enable_per_process_and_thread_memory_limit` **MUST** remain `False` in `backend/app/services/judge0.py`. Setting them to `True` causes immediate `mmap` crashes (status 12).
- **Cgroup v1**: Docker Desktop on macOS must be forced to Cgroup v1. In `~/Library/Group Containers/group.com.docker/settings-store.json`, set `"DeprecatedCgroupv1": true` and restart Docker.
- **Permissions**: The `judge0` service in `docker-compose.yml` must run with `privileged: true` and `user: "0:0"`.

### Database & Environment
- **Supabase**: The `DATABASE_URL` in `.env` typically points to a Supabase pooler. The local `db` container in `docker-compose.yml` is an alternative/standby.
- **Judge0 DB**: Judge0 uses its own dedicated local Postgres and Redis instances defined in `docker-compose.yml`.

## Key Commands

### Backend (from `backend/`)
- **Start**: `.venv/bin/python -m uvicorn app.main:app --reload`
- **Test**: `DATABASE_URL="postgresql+psycopg://dsa_user:dsa_pass@localhost:5432/dsa_platform" .venv/bin/python -m pytest` (58 tests, mocks external services; needs local Postgres — `brew services start postgresql@15` — seeded via the two commands below, NOT Supabase)
- **Migrate (local + Supabase)**: `.venv/bin/python -m alembic upgrade head` (local needs `DATABASE_URL` override; Supabase uses `.env`)
- **Seed**: `.venv/bin/python scripts/seed.py` (idempotent, populates problems and badges)
- **Verify Catalog**: `python scripts/verify_seeds.py` (checks test cases against reference solutions)
- **Check Starters**: `python scripts/check_starters.py` (lints/compiles all starter code scaffolds; needs `g++`/`javac` locally, no Judge0)
- **Train Recommender**: `python scripts/train_recommender.py` (exit 2 = not enough data, heuristic stays live; needs `brew install libomp` on macOS)

### Frontend (from `frontend/`)
- **Start**: `npm run dev` (Next.js 16 + TypeScript on :3000, rewrites `/api` to port 8000)
- **Typecheck**: `npx tsc --noEmit` — **Build**: `npm run build`

## Problem Catalog
- **Count**: 587 problems (deduplicated NeetCode 150 + NeetCode 250 delta + Striver A2Z + custom).
- **Authorship**: Problems are defined in `backend/app/seeds/`. `data_*.py` authored sources win on overlap (deduped by slug in `seeds/__init__.py`); `neetcode_authoring.py` enriches catalog entries. New catalog-only entries land in `data_neetcode250.py` / `data_tuf_a2z.py` with `sources` + `pattern_key`; shared rows carry both source tags (merged in `scripts/seed.py`).
- **Provenance columns**: `sources`, `pattern_key`, `companies`, `editorial_url`, `video_url` (migration `9d4e5f6a7b8c`).
- **Languages**: Python (71), C++ (54), Java (62).

## Architecture Notes
- **Grading**: `backend/app/services/grader.py` handles batching test cases to Judge0.
- **AI Tutor**: Gemini hints and failure reviews are cached in the database.
- **Starters**: Scaffolds are "parse-only" — they handle stdin parsing so the user only writes the core logic.
