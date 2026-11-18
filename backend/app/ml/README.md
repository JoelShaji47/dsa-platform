# Recommender (ML) — owner guide

Hybrid: heuristic candidates + LightGBM LambdaRank re-rank.
Response shape is backward compatible (only additive fields); ordering +
`model` tag change when ML is live.

## Files
- `app/ml/features.py` — schema v2, 27 cols (21 legacy + 6 `ls_*`
  learner-state). Two training tasks (below); one shared serving builder.
- `app/ml/train.py` — group-aware time split, NDCG@5/10, Precision@5,
  coverage, diversity, cold-start slices, heuristic-vs-ML comparison,
  atomic artifact save with schema validation + backup.
- `app/ml/infer.py` — loads `backend/artifacts/ranker.txt`, abstains → `{}`.
  mtime-based reload, SQL-aggregated priors (60s cache).
- `app/services/roadmap.py` — `recommend_next()` heuristic pool,
  `generate_candidates()` intents (balanced/skill/retention/transfer/
  exploration), `get_recommendations()` hybrid + opportunity log,
  `explain_recommendation()` supported-signal explanations.
- `app/services/learner_state.py` — PFA-style per-(user, pattern) state:
  mastery, uncertainty, retention_risk, friction, trend, transfer,
  evidence counts, review priority. Graded outcomes
  (independent=1.0 / hinted=0.5 / editorial=0.2 / fail).
- `app/services/telemetry.py` + `app/models/telemetry.py` — opportunities,
  impressions, solve sessions. No source code/keystrokes/secrets stored.
- `app/services/activity.py` + `app/models/interaction.py` — run/submit/
  hint/review telemetry. Never breaks requests (rollback + swallow).
- `scripts/train_recommender.py` — ETL → features → rank → evaluate →
  `eval_report.json`. Prefers the impression task when usable.
- `tests/test_recommender.py` + `tests/test_ml_personalization.py` —
  groups, leakage, eval, fallback, telemetry auth, learner state, compat.

## Data flow
1. `GET /roadmap/recommendations?intent=balanced` → heuristic candidates
   (unlocked, unsolved, solvable) → ML re-rank when artifact schema matches
   and user has ≥3 submissions → items carry `model`, `intent`,
   `explanation`, `opportunity_id` (+`score` with `?explain=true`).
2. Client reports rendered items → `POST /roadmap/impressions`
   (generated ≠ exposed; duplicates idempotent).
3. Solve work → `POST /roadmap/sessions` → heartbeats (120s idle cap) →
   `finish` reconciles counters from submissions/hints/events.
4. Nightly `train_recommender.py`: impression frame (one query per
   opportunity, as-of features, delayed labels, 14d window) preferred;
   legacy engagement frame otherwise.

## Feature semantics (schema v2)
- `u_*`, `p_*`, `ls_*`: temporal — events strictly before the row cutoff
  (first touch for legacy rows, impression time for impression rows,
  request time for serving). `u_xp` from the `xp_events` ledger ≤ cutoff
  (0 prior when empty — never present-day xp in training). `u_streak`
  reconstructed from accepts before cutoff. `p_accept_rate`/`p_popularity`
  from other users' pairs first-touched ≤ cutoff.
- `i_*`: outcome-window descriptors on the pair (same formula train/serve).
  In the legacy task they describe the window the label comes from — the
  legacy label is post-hoc engagement (2/1/0), NOT learning ground truth.
- Unattempted problems are never labelled negative. Censored (window open,
  no outcome) impression rows are dropped, not zero-filled.
- `sanitize_frame` coerces NaN/Inf/invalid → neutral defaults
  (`i_time_to_accept_min=-1`, `p_accept_rate=0.5`, `ls_uncertainty=1`).

## Learner state
`topic_states_for_user(db, user_id, as_of=...)` reduces graded evidence
(submissions + hints + REVIEW events) with 30-day half-life decay:
mastery = 100·S/(S+0.7·F+2.0), uncertainty = 2/(2+S+F).
Retention risk grows with days since last *independent* success;
review_due = priority ≥ 0.5 and ≥ 7 days since. Thin evidence → priors
(mastery 0, uncertainty 1, trend 0), never invented certainty.
Same code path for training (as_of=cutoff) and serving.

## Setup
1. `brew install libomp` (macOS LightGBM), pip install -r requirements.txt.
2. `alembic upgrade head` (adds `recommendation_opportunities`,
   `recommendation_impressions`, `solve_sessions` via `a1b2c3d4e5f6`).
3. Generate behavior: run/submit/hints/reviews via the app (automatic).

## Train
`DATABASE_URL=... .venv/bin/python scripts/train_recommender.py` from `backend/`
- exit 0 = saved `backend/artifacts/ranker.txt` + `ranker_meta.json`
  (gitignored, never commit) + `eval_report.json` with the heuristic-vs-ML
  head-to-head on identical held-out candidates.
- exit 2 = not enough data (≥20 rows, ≥2 queries with a solve and label
  variation); heuristic stays live, safe on fresh DB.
- After retrain: `infer.clear_cache()` is called by the script; the server
  also reloads on mtime change. Last-known-good backup kept as
  `ranker.txt.bak` / `ranker_meta.json.bak`.

## Serve rules (`infer.py`)
- Abstains when: no artifact, feature/schema mismatch (v1 artifacts abstain
  until retrained on v2), user has < `MIN_INTERACTIONS=3` submissions, or
  predict throws. `artifact_compatible()` is the explicit gate.
- Promotion rule: promote a new artifact only when the validation report
  shows ≥3 validation queries, ML delta vs heuristic ≥ 0 on NDCG@10, and
  fallback tests pass. Sparse data → "inconclusive", heuristic serves.

## Verify telemetry (dev)
- `GET /roadmap/recommendations` → items include `opportunity_id`.
- `POST /roadmap/impressions` with that id → `{"recorded": n}`; repeat →
  `{"recorded": 0}` (idempotent); other user's id → 404.
- Sessions: start → heartbeat → submit → finish shows `status: solved`,
  reconciled counts, `verified_*_complexity: null` (never inferred).
- Frontend wiring (shipped): `src/lib/telemetry.ts` — roadmap tree +
  daily card ping impressions on render; solve page runs
  `useSolveSession(slug)` (start on mount, 60s visible-tab heartbeats,
  keepalive finish on unmount). All fire-and-forget, never break UI.

## Known limitations / next
- Legacy labels conflate exposure/engagement/outcome; the impression task
  is the defensible path but needs rendered-impression volume (currently
  zero → legacy task trains when data suffices; prod Supabase has only
  9 engagement rows — heuristic serves until ≥20).
- `alembic check` reports pre-existing model-vs-DB drift (server defaults,
  index naming) on older tables; unrelated to `a1b2c3d4e5f6`, which
  round-trips cleanly (downgrade drops, upgrade recreates).
- Next highest value: impression/session volume now flows from the
  shipped frontend wiring; run `train_recommender.py` on a schedule and
  apply the promotion rule above. Once impression rows exist, the
  impression task trains automatically (preferred when usable).
