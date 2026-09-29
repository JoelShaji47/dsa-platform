# Agent Instructions: DSA Platform

## Operational Gotchas (CRITICAL)

### Judge0 + Apple Silicon (Rosetta) — macOS host only
The Judge0 CE amd64 image runs under Rosetta 2. Standard `isolate` per-process sandboxing fails here.
- **Fix**: on a **macOS/Rosetta host**, `enable_per_process_and_thread_time_limit` and `enable_per_process_and_thread_memory_limit` **MUST** remain `False` in `backend/app/services/judge0.py`. Setting them to `True` causes immediate `mmap` crashes (status 12).
- **Cgroup v1**: Docker Desktop on macOS must be forced to Cgroup v1. In `~/Library/Group Containers/group.com.docker/settings-store.json`, set `"DeprecatedCgroupv1": true` and restart Docker.
- **Permissions**: the `judge0` service in `docker-compose.yml` must run with `privileged: true` and `user: "0:0"`.

### Judge0 + Windows/WSL2 (Cgroup v2) — **current host**
`False` is the wrong value here. With cgroup v2, isolate's `--cg` needs the cgroup v1 paths `/sys/fs/cgroup/{memory,cpu}/`, which do not exist, so every submission dies with `status_id 13` and `Failed to create control group /sys/fs/cgroup/memory/box-N/`.
- **Fix**: both flags are **`True`** in `backend/app/services/judge0.py`. Per `isolate_job.rb`, `False` is the only thing that appends `--cg`, so `True` makes isolate use `-m`/`-t` limits with no cgroup dependency.
- **Cgroup v1 is not reachable on Windows.** Docker Desktop 29.x mounts `cgroup2` read-only in the WSL2 backend and ships no v1 hierarchy. `"DeprecatedCgroupv1": true` is accepted by `settings-store.json` but **silently ignored** — confirm with `mount | grep cgroup` inside any container. Don't spend time on it.
- **Java requires an inflated memory limit.** With `--cg` gone, `-m` is enforced as `RLIMIT_AS` (virtual address space), and the JVM reserves far more address space than its real heap. At 512000 it dies with `Could not reserve enough space for 256000KB object heap`. `MEMORY_LIMITS_KB["java"]` is therefore **`4096000`**, sized above the JVM's default max heap (25% of the RAM it sees) plus ~1 GB of JVM overhead. Judge0's own ceiling must be raised to match with `MAX_MEMORY_LIMIT` in `docker-compose.yml`, or `Submission` validation rejects anything over 512000 with HTTP 422.
- **Trade-off**: Java's real memory usage is no longer tightly capped. Observed usage for typical DSA programs is ~40 MB, but the address-space ceiling is the limit above.
- **To flip back to `False`**: only on a macOS/Rosetta host. Reverting on Windows reintroduces the `status_id 13` cgroup failure for **every** language.
- **Getting execution after a volume reset**: if Judge0 is crash-looping, the image's `db:create` aborts on an existing empty DB and migrations never run. Stop compose, `docker volume rm <project>_judge0_db_data` only, then `docker compose up -d`. Never delete `<project>_postgres_data` or `<project>_judge0_box`.

### Database & Environment
- **Supabase**: The `DATABASE_URL` in `.env` typically points to a Supabase pooler. The local `db` container in `docker-compose.yml` is an alternative/standby.
- **Judge0 DB**: Judge0 uses its own dedicated local Postgres and Redis instances defined in `docker-compose.yml`.

## Key Commands

### Backend (from `backend/`)
- **Start**: `.venv/bin/python -m uvicorn app.main:app --reload`
- **Test**: `DATABASE_URL="postgresql+psycopg://dsa_user:dsa_pass@localhost:5432/dsa_platform" .venv/bin/python -m pytest` (58 tests, mocks external services; needs local Postgres — `brew services start postgresql@15` — seeded via the two commands below, NOT Supabase)
- **Migrate (local + Supabase)**: `.venv/bin/python -m alembic upgrade head` (local needs `DATABASE_URL` override; Supabase uses `.env`)
- **Seed**: `.venv/bin/python scripts/seed.py` (idempotent, populates problems and badges; applies the global arena rules — exactly 3 visible test cases and exactly 2 examples per problem — automatically via `app/seeds/global_arena_rules.py`)
- **Re-apply Arena Rules to an existing DB**: `python scripts/normalize_global_arena_rules.py` (idempotent; also mirrors the normalized descriptions/test cases back into the 5 fully-authored `app/seeds/data_*.py` files)
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
