import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from tests.conftest import make_test_user
from app.models.enums import Difficulty, SubmissionStatus, TestStatus, Topic
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.test_session import TestProblem, TestSession
from app.models.user import User
from app.seeds import PROBLEMS

client = TestClient(app)


def register_and_login():
    return make_test_user()


def published_problem(difficulty: Difficulty) -> Problem:
    """Grab a real seeded problem of the given difficulty."""
    for seed in PROBLEMS:
        if seed.get("difficulty") == difficulty.value:
            with SessionLocal() as db:
                problem = (
                    db.query(Problem)
                    .filter(Problem.slug == seed["slug"])
                    .one()
                )
                return problem
    raise AssertionError(f"no seeded {difficulty} problem")


def add_submission(user_id, problem: Problem, status=SubmissionStatus.ACCEPTED):
    with SessionLocal() as db:
        sub = Submission(
            user_id=user_id,
            problem_id=problem.id,
            code="print(1)",
            language="python",
            status=status,
            runtime_ms=12.5,
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(sub)
        db.commit()
        return sub.id


def add_session(user_id, *, problems, violations=0, status=TestStatus.SUBMITTED,
                topics=None, assigned_topics=None):
    with SessionLocal() as db:
        session = TestSession(
            user_id=user_id,
            status=status,
            topics=topics or [Topic.ARRAY.value],
            assigned_topics=assigned_topics or [Topic.ARRAY.value],
            duration_seconds=3600,
            started_at=datetime.now(timezone.utc) - timedelta(hours=2),
            deadline_at=datetime.now(timezone.utc) - timedelta(hours=1),
            ended_at=datetime.now(timezone.utc) - timedelta(hours=1),
            time_taken_seconds=1800,
            violations=violations,
            score=1,
            passed_count=1,
        )
        db.add(session)
        db.flush()
        for index, problem in enumerate(problems):
            db.add(
                TestProblem(
                    session_id=session.id,
                    problem_id=problem.id,
                    position=index,
                    difficulty=problem.difficulty,
                    category=problem.topic,
                    passed=index == 0,
                )
            )
        db.commit()
        return session.id


def test_profile_requires_auth():
    assert client.get("/api/v1/profile").status_code == 401


def test_profile_returns_every_section_for_a_fresh_user():
    headers, user_id = register_and_login()

    res = client.get("/api/v1/profile", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()

    assert body["user"]["username"].startswith("user_")
    assert body["user"]["xp"] == 0
    assert body["user"]["current_streak"] == 0
    assert isinstance(body["user"]["league_name"], str)
    assert body["user"]["league_tier"] == 0
    assert body["user"]["created_at"]

    assert body["solved"] == {"easy": 0, "medium": 0, "hard": 0, "total": 0}
    assert body["total_tests"] == 0
    assert body["submissions"] == []
    assert body["tests"] == []
    assert body["badges"], "badge catalog should always be returned"
    assert all(b["earned"] is False for b in body["badges"])
    # 140-day activity window, UTC calendar dates, today included.
    assert len(body["activity"]) == 140
    assert all(day["count"] == 0 for day in body["activity"])
    assert body["activity"][-1]["date"] == datetime.now(
        timezone.utc
    ).date().isoformat()


def test_profile_counts_solved_by_difficulty():
    headers, user_id = register_and_login()

    easy = published_problem(Difficulty.EASY)
    medium = published_problem(Difficulty.MEDIUM)
    hard = published_problem(Difficulty.HARD)
    add_submission(user_id, easy)
    add_submission(user_id, medium)
    add_submission(user_id, hard)
    # A second accepted run on the same problem must not double-count.
    add_submission(user_id, easy)
    # A failed run must not count at all.
    add_submission(user_id, hard, status=SubmissionStatus.WRONG_ANSWER)

    body = client.get("/api/v1/profile", headers=headers).json()

    assert body["solved"]["easy"] == 1
    assert body["solved"]["medium"] == 1
    assert body["solved"]["hard"] == 1
    assert body["solved"]["total"] == 3
    # 3 accepted + 1 duplicate accepted + 1 wrong answer
    assert len(body["submissions"]) == 5


def test_profile_submissions_expose_navigation_and_difficulty():
    headers, user_id = register_and_login()
    problem = published_problem(Difficulty.HARD)
    sub_id = add_submission(user_id, problem, status=SubmissionStatus.TLE)

    body = client.get("/api/v1/profile", headers=headers).json()

    assert len(body["submissions"]) == 1
    row = body["submissions"][0]
    assert row["id"] == str(sub_id)
    assert row["problem_slug"] == problem.slug
    assert row["problem_title"] == problem.title
    assert row["difficulty"] == Difficulty.HARD.value
    assert row["status"] == SubmissionStatus.TLE.value
    assert row["language"] == "python"
    assert row["runtime_ms"] == 12.5
    assert row["submitted_at"]

    # Same accepted run should show up on today's UTC activity tile.
    add_submission(user_id, problem)
    body = client.get("/api/v1/profile", headers=headers).json()
    today = datetime.now(timezone.utc).date().isoformat()
    tile = next(d for d in body["activity"] if d["date"] == today)
    assert tile["count"] == 1


def test_profile_summarizes_test_sessions_with_problem_counts():
    headers, user_id = register_and_login()
    problems = [
        published_problem(Difficulty.EASY),
        published_problem(Difficulty.MEDIUM),
    ]
    # The user ticks 4 categories but only 2 problems get picked, so `topics`
    # and `assigned_topics` must not be reported interchangeably.
    session_id = add_session(
        user_id,
        problems=problems,
        violations=2,
        topics=[Topic.ARRAY.value, Topic.TREE.value, Topic.GRAPH.value, Topic.DP.value],
        assigned_topics=[Topic.ARRAY.value, Topic.TREE.value],
    )

    body = client.get("/api/v1/profile", headers=headers).json()

    assert len(body["tests"]) == 1
    row = body["tests"][0]
    assert row["id"] == str(session_id)
    assert row["status"] == TestStatus.SUBMITTED.value
    assert row["score"] == 1
    assert row["passed_count"] == 1
    # total comes from the grouped TestProblem count, not a lazy relationship.
    assert row["total"] == 2
    assert row["violations"] == 2
    # Only the categories actually used, never the full requested list.
    assert row["assigned_topics"] == [Topic.ARRAY.value, Topic.TREE.value]
    assert row["time_taken_seconds"] == 1800
    assert row["started_at"] and row["ended_at"]


def test_total_tests_counts_only_submitted_sessions():
    headers, user_id = register_and_login()
    problems = [published_problem(Difficulty.EASY)]

    add_session(user_id, problems=problems)  # SUBMITTED
    add_session(user_id, problems=problems)  # SUBMITTED
    add_session(user_id, problems=problems, status=TestStatus.EXPIRED)
    add_session(user_id, problems=problems, status=TestStatus.ABANDONED)
    add_session(user_id, problems=problems, status=TestStatus.IN_PROGRESS)

    body = client.get("/api/v1/profile", headers=headers).json()

    # All five appear in the history list...
    assert len(body["tests"]) == 5
    # ...but only the submitted ones count as "tests taken".
    assert body["total_tests"] == 2


def test_total_tests_is_not_capped_by_the_history_limit():
    """`tests` is limited to TEST_LIMIT rows; total_tests must not be."""
    from app.api.v1.profile import TEST_LIMIT

    headers, user_id = register_and_login()
    problem = published_problem(Difficulty.EASY)

    for _ in range(TEST_LIMIT + 3):
        add_session(user_id, problems=[problem])

    body = client.get("/api/v1/profile", headers=headers).json()

    assert len(body["tests"]) == TEST_LIMIT
    assert body["total_tests"] == TEST_LIMIT + 3


def test_profile_is_scoped_to_the_current_user():
    headers_a, user_a = register_and_login()
    headers_b, user_b = register_and_login()
    problem = published_problem(Difficulty.EASY)
    add_submission(user_a, problem)

    body_b = client.get("/api/v1/profile", headers=headers_b).json()
    assert body_b["submissions"] == []
    assert body_b["solved"]["total"] == 0

    body_a = client.get("/api/v1/profile", headers=headers_a).json()
    assert len(body_a["submissions"]) == 1


def test_profile_reports_real_violations_on_results_too():
    """The results endpoint used to hard-code violations to 0."""
    headers, user_id = register_and_login()
    problem = published_problem(Difficulty.EASY)
    session_id = add_session(user_id, problems=[problem], violations=3)

    body = client.get(
        f"/api/v1/tests/{session_id}/results", headers=headers
    ).json()
    assert body["violations"] == 3
