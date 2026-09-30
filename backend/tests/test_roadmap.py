import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from tests.conftest import make_test_user
from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.seeds import PROBLEMS
from app.services.grader import GradeResult
from app.services.grader import TestOutcome as Outcome
from app.services.roadmap import PATTERNS

client = TestClient(app)


def make_user_and_token():
    headers, _ = make_test_user()
    return headers


def stub_grader(monkeypatch):
    async def fake(source_code, language, test_cases):
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                Outcome(index=i, hidden=False, passed=True, status_key="ACCEPTED")
                for i in range(len(test_cases))
            ],
        )
    monkeypatch.setattr("app.api.v1.problems.grade_code", fake)


def test_roadmap_requires_auth():
    assert client.get("/api/v1/roadmap").status_code == 401
    assert client.get("/api/v1/roadmap/recommendations").status_code == 401
    assert client.get("/api/v1/roadmap/daily").status_code == 401
    assert client.get("/api/v1/roadmap/activity").status_code == 401


def test_roadmap_returns_all_patterns_and_totals():
    headers = make_user_and_token()
    res = client.get("/api/v1/roadmap", headers=headers)
    assert res.status_code == 200
    body = res.json()

    patterns = body["patterns"]
    assert len(patterns) == len(PATTERNS)
    # Roadmap total tracks the DAG membership, which grows with the catalog
    # (NeetCode 250 delta merges into the pattern lists at import).
    assert body["totals"]["total"] == sum(len(p["problems"]) for p in PATTERNS)
    assert body["totals"]["solved"] == 0
    # Every roadmap slug must exist in the seeded catalog.
    catalog_slugs = {p["slug"] for p in PROBLEMS}
    for pattern in patterns:
        for problem in pattern["problems"]:
            assert problem["slug"] in catalog_slugs

    key_order = [p["key"] for p in patterns]
    assert "arrays-hashing" in key_order
    for pattern in patterns:
        assert {"key", "name", "order", "prerequisites", "snippet",
                "solved", "total", "mastery", "complete", "problems"} <= set(pattern)
        for problem in pattern["problems"]:
            assert {"slug", "title", "difficulty", "solved",
                    "attempts", "hints_used", "solvable", "recommended"} <= set(problem)

    # arrays-hashing must be the root (no prerequisites)
    root = next(p for p in patterns if p["key"] == "arrays-hashing")
    assert root["prerequisites"] == []


def test_roadmap_marks_exactly_one_recommended_problem():
    headers = make_user_and_token()
    body = client.get("/api/v1/roadmap", headers=headers).json()

    flagged = [
        (p["key"], pr["slug"])
        for p in body["patterns"]
        for pr in p["problems"]
        if pr["recommended"]
    ]
    # Only the single highest-priority recommendation is flagged.
    assert len(flagged) == 1


def test_recommendations_pick_weak_unsolved_problem():
    headers = make_user_and_token()
    rec = client.get("/api/v1/roadmap/recommendations", headers=headers).json()
    items = rec["recommendations"]
    assert len(items) >= 1
    assert all(item["slug"] for item in items)
    # Every recommendation must carry a human-readable reason.
    assert all(item["reason"] for item in items)

    # The top recommendation is for an unsolved problem in an unlocked pattern.
    top = items[0]
    roadmap = client.get("/api/v1/roadmap", headers=headers).json()
    pattern = next(p for p in roadmap["patterns"] if p["key"] == top["pattern_key"])
    problem = next(pr for pr in pattern["problems"] if pr["slug"] == top["slug"])
    assert problem["solved"] is False


def test_recommendations_advance_after_solving(monkeypatch):
    stub_grader(monkeypatch)
    headers = make_user_and_token()

    # Solve two-sum and valid-anagram (the first two of arrays-hashing).
    for slug in ("two-sum", "valid-anagram"):
        res = client.post(
            f"/api/v1/problems/{slug}/submit",
            headers=headers,
            json={"source_code": "print('x')", "language": "python"},
        )
        assert res.status_code == 200
        assert res.json()["status"] == "ACCEPTED"

    rec = client.get("/api/v1/roadmap/recommendations", headers=headers).json()
    slugs = {item["slug"] for item in rec["recommendations"]}

    # Solved problems are no longer recommended.
    assert "two-sum" not in slugs
    assert "valid-anagram" not in slugs

    # Unlocking two-pointers / sliding-window becomes visibly recommended.
    roadmap = client.get("/api/v1/roadmap", headers=headers).json()
    flagged = [
        pr["slug"]
        for p in roadmap["patterns"]
        for pr in p["problems"]
        if pr["recommended"]
    ]
    assert len(flagged) == 1


def test_daily_question_is_single_unsolved_personalized_problem():
    headers = make_user_and_token()
    res = client.get("/api/v1/roadmap/daily", headers=headers)
    assert res.status_code == 200
    problem = res.json()["problem"]

    # Stable within the day for the same user.
    again = client.get("/api/v1/roadmap/daily", headers=headers).json()["problem"]
    assert problem["slug"] == again["slug"]

    # Must be a real, unsolved problem from an unlocked pattern.
    assert problem["title"]
    assert problem["reason"]
    roadmap = client.get("/api/v1/roadmap", headers=headers).json()
    pattern = next(p for p in roadmap["patterns"] if p["key"] == problem["pattern_key"])
    row = next(pr for pr in pattern["problems"] if pr["slug"] == problem["slug"])
    assert row["solved"] is False


def test_recommendations_pattern_drill_filters_to_pattern():
    headers = make_user_and_token()
    body = client.get(
        "/api/v1/roadmap/recommendations",
        params={"pattern": "arrays-hashing"},
        headers=headers,
    ).json()
    assert body["recommendations"]
    assert all(
        item["pattern_key"] == "arrays-hashing"
        for item in body["recommendations"]
    )


def test_review_due_surfaces_old_friction_solves():
    headers = make_user_and_token()
    user_id = uuid.UUID(
        client.get("/api/v1/auth/me", headers=headers).json()["id"]
    )
    with SessionLocal() as db:
        two_sum = db.query(Problem).filter(Problem.slug == "two-sum").one()
        anagram = db.query(Problem).filter(Problem.slug == "valid-anagram").one()
        old = datetime.now(timezone.utc) - timedelta(days=10)
        # Old solve WITH a hint -> due for review.
        db.add(
            Submission(
                user_id=user_id,
                problem_id=two_sum.id,
                code="x",
                language="python",
                status=SubmissionStatus.ACCEPTED,
                submitted_at=old,
            )
        )
        db.add(HintUsage(user_id=user_id, problem_id=two_sum.id, level=1))
        # Fresh frictionless solve -> not due.
        db.add(
            Submission(
                user_id=user_id,
                problem_id=anagram.id,
                code="x",
                language="python",
                status=SubmissionStatus.ACCEPTED,
            )
        )
        db.commit()

    due = client.get("/api/v1/roadmap/review-due", headers=headers).json()[
        "review_due"
    ]
    slugs = [d["slug"] for d in due]
    assert "two-sum" in slugs
    assert "valid-anagram" not in slugs
    entry = next(d for d in due if d["slug"] == "two-sum")
    assert entry["hints_used"] == 1


def test_activity_returns_chronological_days():
    headers = make_user_and_token()
    res = client.get("/api/v1/roadmap/activity", headers=headers)
    assert res.status_code == 200
    days = res.json()["days"]
    # Trailing window of accepted-submission history, oldest → newest.
    assert len(days) == 140
    dates = [d["date"] for d in days]
    assert dates == sorted(dates)
    assert all(isinstance(d["count"], int) for d in days)


def test_activity_marks_day_after_solving(monkeypatch):
    stub_grader(monkeypatch)
    headers = make_user_and_token()

    res = client.post(
        "/api/v1/problems/two-sum/submit",
        headers=headers,
        json={"source_code": "print('x')", "language": "python"},
    )
    assert res.json()["status"] == "ACCEPTED"

    days = client.get("/api/v1/roadmap/activity", headers=headers).json()["days"]
    # Today must show an accepted submission.
    assert days[-1]["count"] >= 1
