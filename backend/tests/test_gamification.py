import uuid
from collections import Counter
from datetime import date

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.enums import SubmissionStatus
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.seeds import PROBLEMS
from app.services.grader import GradeResult, TestOutcome as Outcome

client = TestClient(app)


def _seed_totals():
    difficulties: Counter = Counter()
    topics: Counter = Counter()
    for p in PROBLEMS:
        difficulties[p["difficulty"]] += 1
        topics[p["topic"]] += 1
    return dict(difficulties), dict(topics)


# Derived from the seed catalog so the suite survives catalog growth
# (NeetCode 250 delta, TUF A2Z, ...).
EXPECTED_DIFFICULTY_TOTALS, EXPECTED_TOPIC_TOTALS = _seed_totals()


def register_and_login():
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
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = client.get("/api/v1/auth/me", headers=headers).json()["id"]
    return headers, uuid.UUID(user_id)


def stub_accept(monkeypatch):
    async def fake(source_code, language, test_cases):
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                Outcome(index=i, hidden=False, passed=True, status_key="ACCEPTED")
                for i in range(len(test_cases))
            ],
        )

    monkeypatch.setattr("app.api.v1.problems.grade_code", fake)


def submit_accepted(headers, slug="two-sum"):
    return client.post(
        f"/api/v1/problems/{slug}/submit",
        json={"language": "python", "source_code": "sol"},
        headers=headers,
    ).json()


def insert_accepted(user_id, slug, language="python"):
    with SessionLocal() as db:
        problem = db.query(Problem).filter(Problem.slug == slug).one()
        db.add(
            Submission(
                user_id=user_id,
                problem_id=problem.id,
                code="x",
                language=language,
                status=SubmissionStatus.ACCEPTED,
                runtime_ms=1.0,
                memory_kb=1024.0,
            )
        )
        db.commit()


def test_endpoints_require_auth():
    assert client.get("/api/v1/stats/me").status_code == 401
    assert client.get("/api/v1/badges/me").status_code == 401


def test_stats_empty_state():
    headers, _ = register_and_login()
    res = client.get("/api/v1/stats/me", headers=headers)
    assert res.status_code == 200
    body = res.json()

    assert body["xp"] == 0
    assert body["current_streak"] == 0
    assert body["total_solved"] == 0
    assert body["total_submissions"] == 0
    assert body["acceptance_rate"] == 0.0
    assert body["recent_submissions"] == []

    by_difficulty = body["solved_by_difficulty"]
    assert set(by_difficulty.keys()) == set(EXPECTED_DIFFICULTY_TOTALS.keys())
    for key, total in EXPECTED_DIFFICULTY_TOTALS.items():
        assert by_difficulty[key] == {"solved": 0, "total": total}

    by_topic = body["solved_by_topic"]
    assert set(by_topic.keys()) == set(EXPECTED_TOPIC_TOTALS.keys())
    for key, total in EXPECTED_TOPIC_TOTALS.items():
        assert by_topic[key] == {"solved": 0, "total": total}


def test_first_blood_awarded_once_and_stats_update(monkeypatch):
    stub_accept(monkeypatch)
    headers, _ = register_and_login()

    first = submit_accepted(headers)
    assert first["new_badges"] == ["First Blood"]

    second = submit_accepted(headers)
    assert second["new_badges"] == []

    stats = client.get("/api/v1/stats/me", headers=headers).json()
    assert stats["xp"] == 10
    assert stats["total_solved"] == 1
    assert stats["total_submissions"] == 2
    assert stats["acceptance_rate"] == 100.0
    assert stats["solved_by_difficulty"]["EASY"] == {
        "solved": 1,
        "total": EXPECTED_DIFFICULTY_TOTALS["EASY"],
    }
    assert stats["solved_by_topic"]["ARRAY"] == {
        "solved": 1,
        "total": EXPECTED_TOPIC_TOTALS["ARRAY"],
    }
    assert len(stats["recent_submissions"]) == 2
    latest = stats["recent_submissions"][0]
    assert latest["problem_slug"] == "two-sum"
    assert latest["status"] == "ACCEPTED"
    assert latest["language"] == "python"


def test_ten_club_awarded_on_tenth_distinct_solve(monkeypatch):
    stub_accept(monkeypatch)
    headers, user_id = register_and_login()

    nine_others = [
        "move-zeroes",
        "maximum-subarray",
        "valid-anagram",
        "valid-parentheses",
        "climbing-stairs",
        "flood-fill",
        "reverse-linked-list",
        "invert-binary-tree",
        "coin-change",
    ]
    for slug in nine_others:
        insert_accepted(user_id, slug)

    result = submit_accepted(headers)
    assert "Ten Club" in result["new_badges"]

    badges = client.get("/api/v1/badges/me", headers=headers).json()
    ten_club = next(b for b in badges if b["criteria"] == "TEN_CLUB")
    assert ten_club["earned"] is True
    assert ten_club["earned_at"] is not None


def test_polyglot_requires_three_languages_same_problem(monkeypatch):
    stub_accept(monkeypatch)
    headers, user_id = register_and_login()

    insert_accepted(user_id, "two-sum", language="python")
    insert_accepted(user_id, "two-sum", language="cpp")

    partial = client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "cpp", "source_code": "again"},
        headers=headers,
    ).json()
    assert "Polyglot" not in partial["new_badges"]

    final = client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "java", "source_code": "third"},
        headers=headers,
    ).json()
    assert "Polyglot" in final["new_badges"]


def test_streak_week_awarded_at_seven_days(monkeypatch):
    stub_accept(monkeypatch)
    headers, user_id = register_and_login()

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.current_streak = 7
        user.last_active_date = date.today()
        db.commit()

    result = submit_accepted(headers)
    assert "Streak Week" in result["new_badges"]


def test_topic_mastery_on_full_topic_clear(monkeypatch):
    stub_accept(monkeypatch)
    headers, user_id = register_and_login()

    # Solve every STRING-topic problem in the catalog (derived live so the
    # test survives catalog growth), submitting the last one via the API.
    string_slugs = [
        p["slug"]
        for p in client.get(
            "/api/v1/problems", params={"topic": "STRING"}, headers=headers
        ).json()
    ]
    assert len(string_slugs) >= 2
    for slug in string_slugs[:-1]:
        insert_accepted(user_id, slug)

    result = submit_accepted(headers, slug=string_slugs[-1])
    assert "String Sage" in result["new_badges"]


def test_badges_endpoint_returns_full_catalog(monkeypatch):
    stub_accept(monkeypatch)
    headers, _ = register_and_login()

    res = client.get("/api/v1/badges/me", headers=headers)
    assert res.status_code == 200
    badges = res.json()
    assert len(badges) == 12
    assert all(set(b.keys()) == {"criteria", "name", "description", "earned", "earned_at"} for b in badges)
    assert all(b["earned"] is False for b in badges)

    criteria_values = {b["criteria"] for b in badges}
    assert {
        "FIRST_BLOOD",
        "TEN_CLUB",
        "POLYGLOT",
        "STREAK_WEEK",
        "TOPIC_ARRAY",
        "TOPIC_QUEUE",
    }.issubset(criteria_values)
