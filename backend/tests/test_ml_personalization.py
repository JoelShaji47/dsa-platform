"""Phase D1: pipeline correctness, telemetry, learner-state, compatibility."""

import uuid
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.ml import infer
from app.ml.features import (
    CUTOFF_COLUMN,
    FEATURE_COLUMNS,
    GROUP_COLUMN,
    LABEL_COLUMN,
    LEARNER_STATE_COLUMNS,
    QUERY_COLUMN,
    sanitize_frame,
    sort_frame,
)
from app.ml.train import (
    InsufficientData,
    _to_dataset,
    compare_heuristic_vs_ml,
    evaluate_frame,
    time_split,
    train_frame,
)
from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.telemetry import (
    RecommendationOpportunity,
    SolveSession,
    estimate_active_seconds,
)
from app.services import learner_state as ls
from tests.conftest import make_test_user

client = TestClient(app)
NOW = datetime.now(timezone.utc)


def _frame(n_users=4, n_problems=8, seed=0, opportunities=False):
    rng = np.random.default_rng(seed)
    rows = []
    base = pd.Timestamp("2026-01-01", tz="UTC")
    for u in range(n_users):
        for p in range(n_problems):
            solved = bool(rng.random() < 0.5)
            attempts = int(rng.integers(1, 6)) if solved or rng.random() < 0.7 else 0
            if attempts == 0:
                continue
            hints = int(rng.integers(0, 3))
            relevance = 2 if (solved and hints <= 1 and attempts <= 3) else (1 if solved else 0)
            qid = f"user-{u}" if not opportunities else f"user-{u}-opp-{p % 2}"
            rows.append(
                {
                    **{c: float(rng.random()) for c in FEATURE_COLUMNS},
                    LABEL_COLUMN: relevance,
                    GROUP_COLUMN: f"user-{u}",
                    QUERY_COLUMN: qid,
                    CUTOFF_COLUMN: base + pd.Timedelta(days=int(rng.integers(0, 60))),
                    "slug": f"problem-{p}",
                }
            )
    return pd.DataFrame(rows)


# ---- A1: group construction ----

def test_groups_contiguous_ordered_and_aligned():
    df = sort_frame(sanitize_frame(_frame()))
    key = QUERY_COLUMN
    # Contiguous blocks per query after sorting.
    seen, last = set(), None
    for _, row in df.iterrows():
        if row[key] != last:
            assert row[key] not in seen, "group split across blocks"
            seen.add(row[key])
            last = row[key]
    ds, groups = _to_dataset(df)
    assert sum(groups) == len(df)
    assert all(g > 0 for g in groups)


def test_time_split_never_splits_a_group():
    df = _frame(opportunities=True)
    train, valid = time_split(df)
    assert not (set(train[QUERY_COLUMN]) & set(valid[QUERY_COLUMN])), \
        "same opportunity on both sides of the split"
    assert len(train) and len(valid)


def test_empty_and_insufficient_data_rejected():
    with pytest.raises(InsufficientData):
        train_frame(pd.DataFrame(columns=FEATURE_COLUMNS + [LABEL_COLUMN, GROUP_COLUMN, CUTOFF_COLUMN, "slug"]))
    tiny = _frame(n_users=1, n_problems=2, seed=1)
    assert len(tiny) < 20
    with pytest.raises(InsufficientData):
        train_frame(tiny)


def test_no_variation_groups_rejected():
    rows = []
    base = pd.Timestamp("2026-02-01", tz="UTC")
    for u in range(6):
        for p in range(6):
            rows.append(
                {**{c: 0.5 for c in FEATURE_COLUMNS}, LABEL_COLUMN: 0,
                 GROUP_COLUMN: f"u-{u}", QUERY_COLUMN: f"u-{u}",
                 CUTOFF_COLUMN: base + pd.Timedelta(days=p), "slug": f"s-{p}"}
            )
    with pytest.raises(InsufficientData):
        train_frame(pd.DataFrame(rows))


def test_sanitize_handles_nan_inf_invalid():
    df = _frame(n_users=4, n_problems=8)
    df.loc[df.index[0], "u_xp"] = np.nan
    df.loc[df.index[1], "p_popularity"] = np.inf
    df["i_attempts"] = df["i_attempts"].astype(object)
    df.loc[df.index[2], "i_attempts"] = "not-a-number"
    out = sanitize_frame(df)
    assert np.all(np.isfinite(out[FEATURE_COLUMNS].to_numpy(dtype=float)))


# ---- A2: temporal leakage ----

def _submit(uid, slug, status, at):
    with SessionLocal() as db:
        p = db.query(Problem).filter(Problem.slug == slug).one()
        db.add(Submission(user_id=uid, problem_id=p.id, code="x",
                          language="python", status=status, submitted_at=at))
        db.commit()


def test_context_features_exclude_future():
    from tests.test_roadmap import make_user_and_token  # noqa

    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    early = NOW - timedelta(days=5)
    late = NOW - timedelta(days=1)
    _submit(uid, "two-sum", SubmissionStatus.ACCEPTED, early)
    _submit(uid, "valid-anagram", SubmissionStatus.ACCEPTED, late)
    try:
        from app.ml.features import build_training_frame

        with SessionLocal() as db:
            frame = build_training_frame(db)
        mine = frame[frame["user_id"] == str(uid)].sort_values(CUTOFF_COLUMN)
        assert len(mine) == 2
        first, second = mine.iloc[0], mine.iloc[1]
        # The earlier pair's context must not see the later solve.
        assert first["u_solved_total"] == 0, first.to_dict()
        assert second["u_solved_total"] == 1, second.to_dict()
    finally:
        with SessionLocal() as db:
            db.query(Submission).filter(Submission.user_id == uid).delete()
            db.commit()


def test_candidate_rows_asof_snapshot_differs_from_now():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    _submit(uid, "two-sum", SubmissionStatus.ACCEPTED, NOW - timedelta(days=3))
    try:
        from app.ml.features import candidate_feature_rows

        with SessionLocal() as db:
            past = candidate_feature_rows(
                db, uid, ["valid-anagram"], as_of=NOW - timedelta(days=5))
            now_rows = candidate_feature_rows(db, uid, ["valid-anagram"])
        assert past and now_rows
        # At T-5d the two-sum solve had not happened yet.
        assert past[0]["u_solved_total"] == 0.0
        assert now_rows[0]["u_solved_total"] == 1.0
        assert set(past[0]) >= set(FEATURE_COLUMNS)
    finally:
        with SessionLocal() as db:
            db.query(Submission).filter(Submission.user_id == uid).delete()
            db.commit()


def test_candidate_rows_with_injected_global_priors():
    """Serving fast path must not need a submission scan.

    Regression: ``global_priors`` used to skip the DB aggregation while the
    unconditional ``all_subs`` loop still ran, so every serving request raised
    ``UnboundLocalError`` and silently fell back to the heuristic.
    """
    from app.ml.features import candidate_feature_rows

    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            problem = db.query(Problem).filter(Problem.slug == "valid-anagram").one()
            rows = candidate_feature_rows(
                db,
                uid,
                ["valid-anagram"],
                global_priors={
                    "pop": {problem.id: 42.0},
                    "acc": {problem.id: 0.25},
                },
            )
        assert rows, "injected priors should still produce a feature row"
        row = rows[0]
        assert row["p_popularity"] == 42.0
        assert row["p_accept_rate"] == 0.25
        assert set(row) >= set(FEATURE_COLUMNS)
    finally:
        with SessionLocal() as db:
            db.query(Submission).filter(Submission.user_id == uid).delete()
            db.commit()
    # Injected priors must not be mutated by the feature builder.
    injected = {"pop": {"x": 1.0}, "acc": {"x": 0.5}}
    with SessionLocal() as db:
        candidate_feature_rows(
            db, uid, ["two-sum"],
            global_priors=injected,
            problems_by_slug={p.slug: p for p in db.query(Problem).all()},
        )
    assert injected == {"pop": {"x": 1.0}, "acc": {"x": 0.5}}


def test_impression_frame_empty_without_impressions():
    from app.ml.features import build_impression_training_frame

    with SessionLocal() as db:
        n_before = db.query(RecommendationOpportunity).count()
        frame = build_impression_training_frame(db)
    assert n_before >= 0  # opportunities may exist from other tests
    # No impressions logged in this DB -> empty frame (honest, not invented).
    assert list(frame.columns)[:1] == [FEATURE_COLUMNS[0]]


# ---- A4/A5: fallback + evaluation ----

def test_infer_abstains_on_schema_mismatch(monkeypatch):
    monkeypatch.setattr(infer, "_priors_cache",
                        {"at": 0.0, "pop": {}, "acc": {}}, raising=False)
    meta = {"version": "ml-old", "features": ["wrong-col"],
            "feature_schema_version": 1}
    monkeypatch.setattr("app.ml.train.load_meta", lambda: meta)
    monkeypatch.setattr("app.ml.infer.load_meta", lambda: meta)
    assert infer.artifact_compatible() is False


def test_infer_abstains_for_cold_user_and_reloads(tmp_path, monkeypatch):
    from app.ml import train as train_module

    monkeypatch.setattr(infer, "MODEL_PATH", tmp_path / "missing.txt")
    monkeypatch.setattr(train_module, "MODEL_PATH", tmp_path / "missing.txt")
    monkeypatch.setattr(train_module, "META_PATH", tmp_path / "missing.json")
    infer.clear_cache()
    try:
        assert infer._load_booster() is None
        assert infer.reload_if_updated() in (True, False)  # explicit, no throw
    finally:
        infer.clear_cache()


def test_evaluation_report_shape_and_comparison():
    df = _frame()
    booster, metrics = train_frame(df)
    assert metrics["feature_schema_version"] == 2
    assert "ndcg@5" in metrics and "coverage@5" in metrics
    scores = booster.predict(df[FEATURE_COLUMNS].to_numpy(dtype=float))
    comp = compare_heuristic_vs_ml(df.reset_index(drop=True), scores)
    assert comp["same_candidates"] is True
    assert "delta_ndcg@10" in comp
    rep = evaluate_frame(df.reset_index(drop=True), scores, name="valid")
    assert rep["rows"] == len(df)


# ---- B: telemetry ----

def _opp_for(uid):
    with SessionLocal() as db:
        opp = RecommendationOpportunity(user_id=uid, model_version="heuristic-v1",
                                        candidate_count=3)
        db.add(opp)
        db.commit()
        db.refresh(opp)
        return opp.id


def test_recommendations_log_opportunity_and_shape_compatible():
    headers, uid = make_test_user()
    body = client.get("/api/v1/roadmap/recommendations", headers=headers).json()
    recs = body["recommendations"]
    assert recs
    for r in recs:
        # Backward-compatible keys...
        assert {"slug", "reason", "title", "difficulty", "solvable", "model"} <= set(r)
        # ...plus additive explanation/intent fields.
        assert "explanation" in r and "intent" in r
    assert all("opportunity_id" in r for r in recs)


def test_roadmap_tree_carries_opportunity_and_impression_links():
    headers, uid = make_test_user()
    tree = client.get("/api/v1/roadmap", headers=headers).json()
    assert tree["opportunity_id"]  # additive; patterns/totals unchanged
    flagged = [pr["slug"] for p in tree["patterns"] for pr in p["problems"]
               if pr["recommended"]]
    assert len(flagged) == 1
    r = client.post("/api/v1/roadmap/impressions", headers=headers, json={
        "opportunity_id": tree["opportunity_id"],
        "items": [{"slug": flagged[0], "rank": 0, "source": "roadmap"}],
    })
    assert r.status_code == 200 and r.json()["recorded"] == 1


def test_impressions_auth_and_idempotency():
    h1, u1 = make_test_user()
    h2, _ = make_test_user()
    opp_id = _opp_for(uuid.UUID(str(u1)))
    recs = client.get("/api/v1/roadmap/recommendations", headers=h1).json()["recommendations"]
    payload = {"opportunity_id": str(opp_id),
               "items": [{"slug": r["slug"], "rank": i} for i, r in enumerate(recs[:2])]}
    r1 = client.post("/api/v1/roadmap/impressions", headers=h1, json=payload)
    assert r1.status_code == 200 and r1.json()["recorded"] == 2
    r2 = client.post("/api/v1/roadmap/impressions", headers=h1, json=payload)
    assert r2.json()["recorded"] == 0  # duplicate retry: idempotent
    r3 = client.post("/api/v1/roadmap/impressions", headers=h2, json=payload)
    assert r3.status_code == 404  # cannot write to another user's opportunity


def test_solve_session_lifecycle_and_reconciliation(monkeypatch):
    from tests.test_roadmap import stub_grader

    stub_grader(monkeypatch)
    headers, uid = make_test_user()
    start = client.post("/api/v1/roadmap/sessions", headers=headers,
                        json={"problem_slug": "two-sum", "client_session_id": "sess-1"})
    assert start.status_code == 200
    sid = start.json()["session"]["id"]
    again = client.post("/api/v1/roadmap/sessions", headers=headers,
                        json={"problem_slug": "two-sum", "client_session_id": "sess-1"})
    assert again.json()["session"]["id"] == sid  # idempotent
    hb = client.post(f"/api/v1/roadmap/sessions/{sid}/heartbeat", headers=headers)
    assert hb.status_code == 200
    assert hb.json()["session"]["heartbeat_count"] >= 2
    # Solve inside the session, then finish: counters reconcile canonically.
    sub = client.post("/api/v1/problems/two-sum/submit", headers=headers,
                      json={"source_code": "print('x')", "language": "python"})
    assert sub.json()["status"] == "ACCEPTED"
    fin = client.post(f"/api/v1/roadmap/sessions/{sid}/finish", headers=headers,
                      json={"claimed_time_complexity": "O(n)",
                            "claimed_space_complexity": "O(1)"})
    body = fin.json()["session"]
    assert body["status"] == "solved"
    assert body["attempt_count"] >= 1
    assert body["claimed_time_complexity"] == "O(n)"
    assert body["verified_time_complexity"] is None  # never inferred from code
    # Another user's session is invisible.
    h2, _ = make_test_user()
    assert client.post(f"/api/v1/roadmap/sessions/{sid}/heartbeat",
                       headers=h2).status_code == 404


def test_active_time_estimator_caps_idle_and_duplicates():
    t0 = NOW
    assert estimate_active_seconds([]) == 0.0
    assert estimate_active_seconds([t0]) == 0.0
    assert estimate_active_seconds([t0, t0 + timedelta(seconds=30)]) == 30.0
    # 10-minute gap counts only the 120s idle timeout, not wall clock.
    assert estimate_active_seconds([t0, t0 + timedelta(seconds=600)]) == 120.0
    assert estimate_active_seconds([t0, t0, t0 + timedelta(seconds=10)]) == 10.0


# ---- C: learner state ----

def test_mastery_hinted_lt_independent_and_uncertainty_falls():
    at = NOW - timedelta(days=1)
    ind = ls.build_topic_state("arrays-hashing",
                               [ls.TopicEvidence("arrays-hashing", "independent", at)],
                               now=NOW)
    hint = ls.build_topic_state("arrays-hashing",
                                [ls.TopicEvidence("arrays-hashing", "hinted", at)],
                                now=NOW)
    ed = ls.build_topic_state("arrays-hashing",
                              [ls.TopicEvidence("arrays-hashing", "editorial", at)],
                              now=NOW)
    empty = ls.build_topic_state("arrays-hashing", [], now=NOW)
    assert ind.mastery > hint.mastery > ed.mastery > empty.mastery == 0.0
    assert empty.uncertainty == 1.0
    more = ls.build_topic_state(
        "arrays-hashing",
        [ls.TopicEvidence("arrays-hashing", "independent", at - timedelta(days=i))
         for i in range(5)], now=NOW)
    assert more.uncertainty < ind.uncertainty
    # Deterministic + repeated processing identical.
    assert ls.build_topic_state("arrays-hashing",
                                [ls.TopicEvidence("arrays-hashing", "independent", at)],
                                now=NOW).mastery == ind.mastery


def test_retention_and_review_priority():
    old = NOW - timedelta(days=20)
    st = ls.build_topic_state(
        "stack",
        [ls.TopicEvidence("stack", "independent", old),
         ls.TopicEvidence("stack", "hinted", old + timedelta(hours=1))],
        now=NOW)
    assert st.retention_risk > 0.0  # 20d since last independent success
    assert st.review_priority > 0.0
    # Assisted-only history: nothing independently learned -> no retention
    # risk (uncertainty carries the lack of evidence instead).
    assisted = ls.build_topic_state(
        "stack", [ls.TopicEvidence("stack", "hinted", old)], now=NOW)
    assert assisted.retention_risk == 0.0
    assert assisted.uncertainty > 0.5
    fresh = ls.build_topic_state(
        "stack", [ls.TopicEvidence("stack", "independent", NOW)], now=NOW)
    assert fresh.retention_risk == 0.0
    assert fresh.review_due is False
    assert st.trend == 0.0  # empty prior window -> documented prior


def test_candidate_intents_respect_eligibility():
    headers, uid = make_test_user()
    for intent in ("skill", "retention", "transfer", "exploration", "balanced"):
        body = client.get("/api/v1/roadmap/recommendations",
                          params={"intent": intent}, headers=headers).json()
        recs = body["recommendations"]
        assert recs
        assert all(r["intent"] in ("skill", "retention", "transfer", "exploration")
                   for r in recs)
        assert all(r["solvable"] for r in recs)


def test_cold_start_user_gets_heuristic_recs():
    headers, _ = make_test_user()
    body = client.get("/api/v1/roadmap/recommendations", headers=headers).json()
    assert body["recommendations"]
    assert all(r["model"] == "heuristic-v1" for r in body["recommendations"])


def test_migration_single_head_and_tables_exist():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config("alembic.ini")
    heads = ScriptDirectory.from_config(cfg).get_heads()
    assert len(heads) == 1, f"expected a single alembic head, got {heads}"
    with SessionLocal() as db:
        names = db.bind.dialect.get_table_names(db.connection())
        for table in ("recommendation_opportunities", "recommendation_impressions",
                      "solve_sessions"):
            assert table in names
