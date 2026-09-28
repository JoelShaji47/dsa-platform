# Recommender (ML) — owner guide

Hybrid: heuristic candidates + LightGBM LambdaRank re-rank.
Response shape never changes; only ordering + `model` tag change.

## Files
- `app/ml/features.py` — 21 cols per (user, problem); labels 2/1/0 (engaged solve).
- `app/ml/train.py` — time-split validation, NDCG@10 / Precision@5.
- `app/ml/infer.py` — loads `backend/artifacts/ranker.txt`, abstains → `{}`.
- `app/services/roadmap.py:get_recommendations()` — heuristic pool (top 12) + `infer.score_candidates()` re-rank.
- `app/services/roadmap.py:get_user_progress()` — public progress map (use this, not `_build_user_state`).
- `app/services/activity.py` + `app/models/interaction.py` — `run/submit/hint/review` telemetry. Never breaks requests (rollback + swallow).
- `scripts/train_recommender.py` — ETL → train → save artifact.
- `tests/test_recommender.py` — metrics + trainer + abstain + `model` tag.

## Setup
1. `brew install libomp` (macOS LightGBM), pip install -r requirements.txt.
2. `alembic upgrade head` (creates `interaction_events` via `f1a2b3c4d5e6`).
3. Generate behavior: run/submit/hints/reviews via the app (telemetry is automatic).

## Train
`python scripts/train_recommender.py` from `backend/`
- exit 0 = saved `backend/artifacts/ranker.txt` + `ranker_meta.json` (gitignored, never commit).
- exit 2 = not enough data (need ≥20 rows + ≥2 users with a solve); heuristic stays live, safe on fresh DB.
- After retrain: `infer.clear_cache()` is called by the script; restart/reload API in prod to pick up the new file (lru_cache).

## Serve rules (`infer.py`)
- Abstains when: no artifact, feature-list mismatch, user has < `MIN_INTERACTIONS=3` submissions, or predict throws.
- `GET /roadmap/recommendations` → each item has `model: heuristic-v1 | ml-YYYYMMDD-HHMM`; `?explain=true` adds raw `score`.
- Train/serve parity: same `FEATURE_COLUMNS`, same `RUN`/`REVIEW` constants, same time-to-accept/revisits formula.

## Next work (pick one)
- Content embedding prior for cold problems, epsilon-greedy exploration (§4a/§4c in `docs/ml-recommendation-plan.md`).
- Nightly cron for `train_recommender.py` + artifact versioning.
