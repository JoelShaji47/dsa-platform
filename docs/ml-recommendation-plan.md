# ML Recommendation Plan — IMPLEMENTED (two-stage hybrid)

Status: live as a two-stage hybrid with exploration.

- **Stage 1 (recall)**: the heuristic generates the policy-legal pool (unlocked,
  unsolved, solvable) and collaborative filtering (truncated SVD over the
  implicit submission matrix) adds neighbourhood candidates the heuristic
  misses. Artifact: `backend/artifacts/retrieval.npz`.
- **Stage 2 (ranking)**: a LightGBM LambdaRank model re-ranks that union when a
  trained artifact exists AND the user has ≥3 logged submissions.
- **Exploration**: epsilon-greedy (`ML_EXPLORATION_EPSILON`, default `0.1`)
  replaces the lowest-ranked slot with one eligible surprise pick, stable per
  learner/day/intent.

Cold users (no submissions / no artifact) still get the heuristic order. The
response shape never changes; each item carries `model`
(`heuristic-v1` | `ml-YYYYMMDD-HHMM`) and, with `explain`, the raw `score` plus
`candidate_source` (`cf` / `exploration` when applicable).

Serving: `GET /roadmap/recommendations?explain=true`. The daily question draws
from the same ranked pool, so it improves automatically once the model is live.

Pipeline: `interaction_events` telemetry → `app/ml/retrieval.py` (CF factors) +
`app/ml/features.py` (32 features) → `scripts/train_recommender.py`
(time-split validation, NDCG@10/Precision@5) → `backend/artifacts/ranker.txt`
and `retrieval.npz` → `app/ml/infer.py` + `app/ml/retrieval.py` (both abstain
safely to the heuristic on missing artifacts, schema mismatch, or errors).

First training (local dev data, 477 rows / 230 users): NDCG@10 0.8,
Precision@5 0.8 on the time-split holdout. Retrain nightly/weekly as real
behavioral data accumulates; the script exits 2 (ranker stays heuristic) when
data is insufficient but still refreshes the retrieval artifact when it can.

Original design notes below are kept for context; §4a, §4b and §4c are built.

---

The roadmap shows a **Daily Question** derived from a per-person adaptive heuristic. This document
is the plan for replacing that heuristic with a real machine-learning recommender once enough
behavioral data has been collected.

---

## 1. Current state (heuristic)

- `backend/app/services/roadmap.py` → `get_recommendations(db, user)` and `get_daily_question(db, user)`.
- Picks from the top-8 most-recommended **unsolved** problems using a rule-based score across:
  - topic mastery (solved/total per coarse topic),
  - difficulty balance,
  - roadmap prerequisites (don't rush advanced patterns),
  - `solvable` flag (prefer authored problems that can actually be run).
- Daily pick is deterministic per user+date (`hash(user.id + date) % len(pool)`).

**Why it's not enough**: no modeling of *how* the user solved (hints? how many attempts? how
long?), no item similarities beyond coarse topic, no personalization beyond mastery breakdown, and
no feedback loop improving over time.

---

## 2. Goal

Given a user and their history, predict a **score for each problem** and recommend the top
unsolved, solvable items. Optimize for a multi-objective target — primarily *learning retention*
and *engagement* — so the "best" problem isn't just "the one most likely to be solved", but the one
most likely to be solved **with effort** and remembered.

---

## 3. Features

### Per-user static
- `solved_total`, `total_xp`, `current_streak`, `level`.
- Per-topic mastery: `solved_by_topic[coarse] / total_by_topic[coarse]`.
- Per-difficulty solved counts.

### Per (user, problem) interaction
From `Submissions`, `Attempts`, and hint logs:

| Feature | Source |
| --- | --- |
| `attempts_before_first_accept` | submissions per problem |
| `hints_revealed` (count) | hint reveal logs |
| `time_to_first_accept` (minutes) | submission timestamps |
| `reject_ratio` | wrong/TLE/RTE per problem |
| `times_revisited` | re-submits after accept |
| `ever_solved` | submissions status == ACCEPTED |
| `review_requested` | AI review calls |

### Per-problem (item) static
- `topic`, `difficulty`, `pattern_key`, `solvable`, `problem_age`.
- Content embedding: title + description + starter code vectorized (e.g. TF-IDF or a small
  sentence encoder) so unseen problems get a semantic prior.

### Derived (session/roadmap context)
- Roadmap `order` and `prerequisites` (DAG position).
- Recency/frequency of the topic.

---

## 4. Model options

### 4a. Collaborative filtering (matrix factorization) — baseline
- **Implemented** in `app/ml/retrieval.py`: implicit user × problem matrix
  (clean accept 1.0, hinted accept 0.7, attempt 0.2) factorised with
  `TruncatedSVD` (32 components, no new dependency).
- Cold-start: unknown users/items get no CF candidates and the heuristic pool
  stands; every retrieved slug is still filtered by the roadmap policy.
- Artifact `retrieval.npz` is trained by `scripts/train_recommender.py`
  independently of the ranker's data gate.

### 4b. Learning-to-rank (gradient boosting) — recommended primary
- `lightgbm` LambdaRank over the (user, problem) feature rows above.
- Target: pairwise ranking loss preferring *engaged solves* (e.g. solved with 0–1 hints, 1–3
  attempts) over solved-with-many-hints or unsolved.
- Naturally consumes all table features + item embeddings.
- Cold-start handled by feature fallback to topic/difficulty averages.

### 4c. Two-stage hybrid (recommended production shape)
1. **Retrieval/coarse**: heuristic policy (topic under-mastery, DAG frontier,
   solvable) **plus** CF neighbourhood recall.
2. **Ranking/fine**: gradient-boosting ranker scores the union with the full
   feature set.
3. **Exploration**: epsilon-greedy mix (`ML_EXPLORATION_EPSILON`, default 0.1)
   so cold items still get surfaced; stable per learner/day/intent.

---

## 5. Training pipeline

1. **ETL**: export `Submissions`, `Attempts`, hint logs, and problem catalog to CSVs/Parquet.
2. **Feature engineering**: compute per (user, problem) rows + item/user side tables.
3. **Labels**: define the target. Proposal:
   - solved with `hints_revealed <= 1` **and** `attempts_before_first_accept <= 3` → positive,
   - otherwise → negative,
   - treat "longest retention / replay" as a secondary offline metric.
4. **Split**: time-based — train on all events before date `T`, validate on `[T, T+2w)`,
   test on `[T+2w, …)` (never random-split, which leaks future behavior).
5. **Train + tune**: `lightgbm` ranker, early stopping on validation NDCG/Precision@k.
6. **Evaluate**: NDCG@10, Precision@k, coverage, diversity (topic/difficulty spread), and
   offline retention proxy (does the pick correlate with later re-engagement?).
7. **Serve**: retrain nightly/weekly from the same Postgres tables; bake model as an artifact the
   API loads.

---

## 6. Serving & cold start

- Endpoint shape unchanged: `get_daily_question` and `get_recommendations` return the same payload;
  the *scoring function* behind them swaps from heuristic → model.
- **Cold-start users** (no submissions): fall back to the current heuristic (topic + solvable), so
  onboarding is immediately usable.
- **Cold-start problems**: rely on content embedding prior + solvable flag; rank them lower until
  labeled interactions accumulate.
- Keep the `solvable` constraint and the "don't repeat the same day" determinism.

---

## 7. Decisions (formerly open questions)

1. **Offline batch** training with artifacts (`ranker.txt`, `retrieval.npz`) —
   simpler, cacheable, and retrained nightly/weekly. No per-request training.
2. Target stays the leak-free **impression task** (engage → accept 2 / 1 / 0),
   with clicked/dismissed as label columns, not features. Legacy engagement rows
   are never shipped because their label leaks through contemporaneous features.
3. Attempt/hint telemetry is already logged (`interaction_events`, `hint_usage`,
   `recommendation_impressions`); the retrain runs once enough impressions exist.
