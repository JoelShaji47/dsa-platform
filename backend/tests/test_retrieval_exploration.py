"""Layer 4a/4c: collaborative retrieval and epsilon-greedy exploration."""

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.ml import retrieval
from app.services.roadmap import (
    _load_problems,
    _retrieval_recommendations,
    get_user_progress,
)
from tests.conftest import make_test_user

client = TestClient(app)


def _interactions():
    rows = []
    for u in range(3):
        rows.extend([(f"u{u}", "a", 1.0), (f"u{u}", "b", 1.0)])
    for u in range(3, 6):
        rows.extend([(f"u{u}", "c", 1.0), (f"u{u}", "d", 1.0)])
    return rows


def test_fit_factors_ranks_neighbourhood_above_unrelated_items():
    user_ids, slugs, user_f, item_f = retrieval.fit_factors(
        _interactions(), n_components=2
    )
    assert user_ids == ["u0", "u1", "u2", "u3", "u4", "u5"]
    assert slugs == ["a", "b", "c", "d"]
    u0 = user_ids.index("u0")
    b = slugs.index("b")
    c = slugs.index("c")
    assert float(user_f[u0] @ item_f[b]) > float(user_f[u0] @ item_f[c])


def test_retrieval_artifact_roundtrip_and_policy_filters(tmp_path, monkeypatch):
    monkeypatch.setattr(retrieval, "ARTIFACT_DIR", tmp_path)
    monkeypatch.setattr(retrieval, "RETRIEVAL_PATH", tmp_path / "retrieval.npz")
    monkeypatch.setattr(retrieval, "RETRIEVAL_META_PATH", tmp_path / "retrieval_meta.json")
    monkeypatch.setattr(retrieval, "MIN_INTERACTIONS", 4)
    monkeypatch.setattr(retrieval, "build_interactions", lambda db: _interactions())
    retrieval.clear_cache()
    try:
        meta = retrieval.train_and_save(None)
        assert meta is not None
        assert (tmp_path / "retrieval.npz").exists()
        assert retrieval.model_version() == meta["version"]

        hits = retrieval.retrieve_candidates(
            None, "u0", limit=2, eligible_slugs={"c", "d"}
        )
        assert hits and all(slug in {"c", "d"} for slug, _ in hits)
        assert all(slug not in {"a", "b"} for slug, _ in hits)

        excluded = retrieval.retrieve_candidates(
            None, "u0", limit=2, eligible_slugs={"c", "d"}, exclude_slugs={"c"}
        )
        assert all(slug == "d" for slug, _ in excluded)

        # Cold-start user: no factor row -> no candidates, no crash.
        assert retrieval.retrieve_candidates(None, "new-user") == []
    finally:
        retrieval.clear_cache()


def test_maybe_explore_respects_epsilon_and_chosen():
    from types import SimpleNamespace

    from app.services import roadmap as rm

    problems = {
        slug: SimpleNamespace(starter_code="code", test_cases=[1])
        for slug in rm.SLUG_TO_PATTERN
    }
    progress = {
        key: rm.PatternProgress(key=key, total=len(p["problems"]), solved=0)
        for key, p in rm.PATTERN_BY_KEY.items()
    }
    solved = {slug: False for slug in problems}
    user = SimpleNamespace(id="explore-user")

    rec = rm._maybe_explore(
        user, problems, solved, progress, set(), "balanced", epsilon=1.0
    )
    assert rec is not None
    assert rec["candidate_source"] == "exploration"
    assert rec["intent"] == "exploration"
    assert rec["slug"] in rm.SLUG_TO_PATTERN

    assert rm._maybe_explore(
        user, problems, solved, progress, set(), "balanced", epsilon=0.0
    ) is None
    assert rm._maybe_explore(
        user, problems, solved, progress, set(problems), "balanced", epsilon=1.0
    ) is None


def test_retrieval_candidates_pass_roadmap_policy(monkeypatch):
    _, uid = make_test_user()
    calls = {}

    def fake_retrieve(db, user_id, limit=8, eligible_slugs=None, exclude_slugs=None):
        calls["eligible"] = eligible_slugs
        calls["exclude"] = exclude_slugs
        if eligible_slugs and "valid-anagram" in eligible_slugs:
            return [("valid-anagram", 0.9)]
        return []

    monkeypatch.setattr("app.ml.retrieval.retrieve_candidates", fake_retrieve)
    with SessionLocal() as db:
        from app.models.user import User

        user = db.get(User, uid)
        problems = _load_problems(db)
        progress = get_user_progress(db, user)
        solved = {slug: False for slug in problems}
        recs = _retrieval_recommendations(
            db, user, problems, solved, progress, set()
        )
    assert recs and recs[0]["slug"] == "valid-anagram"
    assert recs[0]["candidate_source"] == "cf"
    assert recs[0]["intent"] == "skill"
    assert "valid-anagram" in calls["eligible"]


def test_endpoint_includes_cf_recall_for_cold_user(monkeypatch):
    def fake_retrieve(db, user_id, limit=8, eligible_slugs=None, exclude_slugs=None):
        # Return the first policy-legal slug the heuristic did not already
        # pick. Hard-coding catalogue slugs made this brittle: the heuristic
        # may already contain them, or they may sit behind a locked pattern.
        for slug in sorted(eligible_slugs or ()):
            if exclude_slugs and slug in exclude_slugs:
                continue
            return [(slug, 0.9)]
        return []

    monkeypatch.setattr("app.ml.retrieval.retrieve_candidates", fake_retrieve)
    # Exploration replaces the lowest slot, which can be the single CF item
    # when no ranker is present. Disable it so this test isolates retrieval.
    monkeypatch.setenv("ML_EXPLORATION_EPSILON", "0")
    headers, _ = make_test_user()
    body = client.get("/api/v1/roadmap/recommendations", headers=headers).json()
    cf = [r for r in body["recommendations"] if r.get("candidate_source") == "cf"]
    assert cf, "CF recall should reach the response even without a ranker artifact"
    assert all(r["solvable"] for r in cf)


def test_exploration_epsilon_one_and_zero(monkeypatch):
    headers, _ = make_test_user()
    monkeypatch.setenv("ML_EXPLORATION_EPSILON", "1.0")
    body = client.get("/api/v1/roadmap/recommendations", headers=headers).json()
    explored = [
        r for r in body["recommendations"]
        if r.get("candidate_source") == "exploration"
    ]
    assert len(explored) == 1
    assert explored[0]["intent"] == "exploration"
    assert explored[0]["solvable"]

    monkeypatch.setenv("ML_EXPLORATION_EPSILON", "0")
    body = client.get("/api/v1/roadmap/recommendations", headers=headers).json()
    assert not any(
        r.get("candidate_source") == "exploration"
        for r in body["recommendations"]
    )
