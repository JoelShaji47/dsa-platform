import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import SubmissionStatus
from app.services.grader import GradeResult
from app.services.grader import TestOutcome as Outcome

client = TestClient(app)


def make_user_and_token():
    suffix = uuid.uuid4().hex[:8]
    data = {
        "username": f"user_{suffix}",
        "email": f"{suffix}@test.com",
        "password": "supersecret1",
    }
    client.post("/api/v1/auth/register", json=data)
    login = client.post(
        "/api/v1/auth/login",
        data={"username": data["email"], "password": data["password"]},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


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


def test_roadmap_returns_all_patterns_and_totals():
    headers = make_user_and_token()
    res = client.get("/api/v1/roadmap", headers=headers)
    assert res.status_code == 200
    body = res.json()

    patterns = body["patterns"]
    assert len(patterns) >= 11
    assert body["totals"]["total"] == 34
    assert body["totals"]["solved"] == 0

    key_order = [p["key"] for p in patterns]
    assert "arrays-hashing" in key_order
    for pattern in patterns:
        assert {"key", "name", "order", "prerequisites", "snippet",
                "solved", "total", "mastery", "complete", "problems"} <= set(pattern)
        for problem in pattern["problems"]:
            assert {"slug", "title", "difficulty", "solved",
                    "attempts", "hints_used", "recommended"} <= set(problem)

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
