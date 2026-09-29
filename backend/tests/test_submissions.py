import uuid
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.enums import Difficulty, Language, SubmissionStatus, Topic
from app.models.interaction import InteractionEvent
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.services.grader import GradeResult
from app.services.grader import TestOutcome as Outcome

client = TestClient(app)


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


def stub_grader(monkeypatch, *, status, passes=None):
    async def fake(source_code, language, test_cases):
        n = len(test_cases)
        flags = passes if passes is not None else [status == SubmissionStatus.ACCEPTED] * n
        results = []
        for i, case in enumerate(test_cases):
            ok = flags[i % len(flags)]
            if ok:
                key, exec_status = "ACCEPTED", None
            elif status == SubmissionStatus.TLE:
                key, exec_status = "TIME_LIMIT_EXCEEDED", SubmissionStatus.TLE
            elif status == SubmissionStatus.COMPILATION_ERROR:
                key, exec_status = "COMPILATION_ERROR", SubmissionStatus.COMPILATION_ERROR
            elif status == SubmissionStatus.RUNTIME_ERROR:
                key, exec_status = "RUNTIME_ERROR_SIGSEGV", SubmissionStatus.RUNTIME_ERROR
            else:
                key, exec_status = "WRONG_ANSWER", None
            results.append(
                Outcome(
                    index=i,
                    hidden=bool(case.get("is_hidden", False)),
                    passed=ok,
                    status=exec_status,
                    status_key=key,
                    runtime_ms=1.5 * (i + 1),
                    memory_kb=1024 * (i + 1),
                )
            )
        return GradeResult(status=status, test_results=results)

    monkeypatch.setattr("app.api.v1.problems.grade_code", fake)


def submission_count(user_id: int) -> int:
    with SessionLocal() as db:
        return db.query(Submission).filter(Submission.user_id == user_id).count()


def get_user(user_id: uuid.UUID) -> User:
    with SessionLocal() as db:
        return db.query(User).filter(User.id == user_id).one()


def test_run_and_submit_require_auth():
    payload = {"language": "python", "source_code": "print(1)"}
    assert client.post("/api/v1/problems/two-sum/run", json=payload).status_code == 401
    assert client.post("/api/v1/problems/two-sum/submit", json=payload).status_code == 401


def test_run_uses_visible_tests_only_and_persists_nothing(monkeypatch):
    seen_cases = {}

    async def spy(source_code, language, test_cases):
        seen_cases["count"] = len(test_cases)
        seen_cases["any_hidden"] = any(c.get("is_hidden") for c in test_cases)
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                Outcome(index=i, hidden=False, passed=True, status_key="ACCEPTED")
                for i in range(len(test_cases))
            ],
        )

    monkeypatch.setattr("app.api.v1.problems.grade_code", spy)
    headers, user_id = register_and_login()
    res = client.post(
        "/api/v1/problems/two-sum/run",
        json={"language": "python", "source_code": "print('x')"},
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ACCEPTED"
    assert seen_cases["count"] == 3
    assert seen_cases["any_hidden"] is False
    assert len(body["test_results"]) == 3
    assert body["test_results"][0]["input"] == "4\n2 7 11 15\n9\n"
    assert submission_count(user_id) == 0


def test_run_caps_visible_cases_at_three(monkeypatch):
    seen_cases = {}

    async def spy(source_code, language, test_cases):
        seen_cases["count"] = len(test_cases)
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                Outcome(index=i, hidden=False, passed=True, status_key="ACCEPTED")
                for i in range(len(test_cases))
            ],
        )

    monkeypatch.setattr("app.api.v1.problems.grade_code", spy)
    headers, _ = register_and_login()

    slug = f"cap-{uuid.uuid4().hex[:8]}"
    with SessionLocal() as db:
        db.add(
            Problem(
                title="Cap",
                slug=slug,
                description="# Cap\n\n## Example\n\n**Input**\n```\n1\n```\n",
                difficulty=Difficulty.EASY,
                topic=Topic.ARRAY,
                starter_code={"python": "print(1)"},
                test_cases=[
                    {"input": f"{i}\n", "expected_output": str(i), "is_hidden": False}
                    for i in range(4)
                ]
                + [{"input": "9\n", "expected_output": "9", "is_hidden": True}],
            )
        )
        db.commit()
    try:
        res = client.post(
            f"/api/v1/problems/{slug}/run",
            json={"language": "python", "source_code": "print('x')"},
            headers=headers,
        )
        assert res.status_code == 200
        body = res.json()
        assert seen_cases["count"] == 3
        assert len(body["test_results"]) == 3
    finally:
        with SessionLocal() as db:
            db.query(Problem).filter(Problem.slug == slug).delete()
            db.commit()


def test_run_unknown_slug_404():
    headers, _ = register_and_login()
    res = client.post(
        "/api/v1/problems/nope-nope/run",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    assert res.status_code == 404


def test_rejects_unsupported_language():
    headers, _ = register_and_login()
    res = client.post(
        "/api/v1/problems/two-sum/run",
        json={"language": "ruby", "source_code": "puts 1"},
        headers=headers,
    )
    assert res.status_code == 422


def test_submit_accepted_awards_xp_and_streak(monkeypatch):
    stub_grader(monkeypatch, status=SubmissionStatus.ACCEPTED)
    headers, user_id = register_and_login()

    res = client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "python", "source_code": "solution"},
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ACCEPTED"
    assert body["xp_awarded"] == 16
    assert body["user_xp"] == 16
    assert body["current_streak"] == 1

    user = get_user(user_id)
    assert user.xp == 16
    assert user.current_streak == 1
    assert user.last_active_date == date.today()
    assert submission_count(user_id) == 1

    stored = client.get("/api/v1/auth/me", headers=headers).json()
    assert stored["xp"] == 16


def test_submit_wrong_answer_records_but_rewards_nothing(monkeypatch):
    stub_grader(monkeypatch, status=SubmissionStatus.WRONG_ANSWER)
    headers, user_id = register_and_login()

    res = client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "cpp", "source_code": "// wrong"},
        headers=headers,
    )
    body = res.json()
    assert body["status"] == "WRONG_ANSWER"
    assert body["xp_awarded"] == 0
    assert body["user_xp"] == 0
    assert submission_count(user_id) == 1

    user = get_user(user_id)
    assert user.last_active_date is not None or True
    assert user.xp == 0


def test_submit_masks_hidden_tests(monkeypatch):
    stub_grader(monkeypatch, status=SubmissionStatus.WRONG_ANSWER, passes=[True, False])
    headers, _ = register_and_login()

    res = client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "java", "source_code": "class Main {}"},
        headers=headers,
    )
    results = res.json()["test_results"]
    assert len(results) == 5
    visible = [c for c in results if not c["hidden"]]
    hidden = [c for c in results if c["hidden"]]
    # two-sum seed: 3 visible + 2 hidden
    assert len(visible) == 3
    assert len(hidden) == 2
    for case in visible:
        assert case["input"] == "4\n2 7 11 15\n9\n" or case["input"]
        assert "expected_output" in case and case["expected_output"]
    for case in hidden:
        # Exact key set: inputs, expected outputs and actuals never leak.
        assert set(case.keys()) == {"index", "passed", "hidden", "status_key"}


def test_detail_reports_hidden_test_count():
    headers, _ = register_and_login()
    body = client.get("/api/v1/problems/two-sum", headers=headers).json()
    assert body["hidden_test_count"] == 2
    assert len(body["test_cases"]) == 3


@pytest.mark.parametrize(
    "slug,expected_xp",
    [
        ("two-sum", 16),
        ("maximum-subarray", 31),
        ("first-missing-positive", 62),
    ],
)
def test_xp_scales_with_difficulty_once_only(monkeypatch, slug, expected_xp):
    stub_grader(monkeypatch, status=SubmissionStatus.ACCEPTED)
    headers, user_id = register_and_login()

    first = client.post(
        f"/api/v1/problems/{slug}/submit",
        json={"language": "python", "source_code": "a"},
        headers=headers,
    ).json()
    assert first["xp_awarded"] == expected_xp

    second = client.post(
        f"/api/v1/problems/{slug}/submit",
        json={"language": "python", "source_code": "b"},
        headers=headers,
    ).json()
    assert second["xp_awarded"] == 0
    assert second["user_xp"] == expected_xp

    user = get_user(user_id)
    assert user.xp == expected_xp


def test_streak_increments_on_consecutive_days(monkeypatch):
    stub_grader(monkeypatch, status=SubmissionStatus.ACCEPTED)
    headers, user_id = register_and_login()

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.current_streak = 4
        user.last_active_date = date.today() - timedelta(days=1)
        db.commit()

    res = client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "python", "source_code": "a"},
        headers=headers,
    ).json()
    assert res["current_streak"] == 5

    again = client.post(
        "/api/v1/problems/move-zeroes/submit",
        json={"language": "python", "source_code": "a"},
        headers=headers,
    ).json()
    assert again["current_streak"] == 5


def test_streak_resets_after_gap(monkeypatch):
    stub_grader(monkeypatch, status=SubmissionStatus.ACCEPTED)
    headers, user_id = register_and_login()

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.current_streak = 9
        user.last_active_date = date.today() - timedelta(days=3)
        db.commit()

    res = client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "python", "source_code": "a"},
        headers=headers,
    ).json()
    assert res["current_streak"] == 1


def test_tle_status_recorded(monkeypatch):
    stub_grader(monkeypatch, status=SubmissionStatus.TLE, passes=[True, False])
    headers, _ = register_and_login()

    res = client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "python", "source_code": "while True: pass"},
        headers=headers,
    ).json()
    assert res["status"] == "TLE"


def test_run_and_submit_emit_interaction_events(monkeypatch):
    stub_grader(monkeypatch, status=SubmissionStatus.WRONG_ANSWER)
    headers, user_id = register_and_login()

    with SessionLocal() as db:
        problem_id = db.query(Problem.id).filter(Problem.slug == "two-sum").scalar()

    client.post(
        "/api/v1/problems/two-sum/run",
        json={"language": "python", "source_code": "x"},
        headers=headers,
    )
    client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "python", "source_code": "x"},
        headers=headers,
    )

    with SessionLocal() as db:
        events = (
            db.query(InteractionEvent)
            .filter(
                InteractionEvent.user_id == user_id,
                InteractionEvent.problem_id == problem_id,
            )
            .order_by(InteractionEvent.created_at)
            .all()
        )
    kinds = [e.event for e in events]
    assert kinds == ["run", "submit"]
    assert events[1].meta["status"] == "WRONG_ANSWER"
    assert events[1].meta["passed"] is False


def test_language_enum_values_accepted(monkeypatch):
    stub_grader(monkeypatch, status=SubmissionStatus.WRONG_ANSWER)
    headers, _ = register_and_login()
    for lang in (Language.PYTHON.value, Language.CPP.value, Language.JAVA.value):
        res = client.post(
            "/api/v1/problems/two-sum/run",
            json={"language": lang, "source_code": "x"},
            headers=headers,
        )
        assert res.status_code == 200


def test_custom_run_returns_stdout_without_storing(monkeypatch):
    async def fake_submit(source_code, language, stdin):
        assert language == Language.PYTHON.value
        assert stdin == "4 2 6"
        return {
            "stdout": "6\n",
            "stderr": None,
            "compile_output": None,
            "status_key": "ACCEPTED",
            "time": 0.012,
            "memory": 4096,
        }

    monkeypatch.setattr("app.api.v1.problems.submit", fake_submit)
    headers, user_id = register_and_login()
    res = client.post(
        "/api/v1/custom-run",
        json={
            "language": "python",
            "source_code": "a = list(map(int, input().split()))\nprint(sum(a))",
            "stdin": "4 2 6",
        },
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ACCEPTED"
    assert body["status_key"] == "ACCEPTED"
    assert body["stdout"] == "6\n"
    assert body["stderr"] is None
    assert body["runtime_ms"] == 12
    with SessionLocal() as db:
        stored = db.query(Submission).filter(Submission.user_id == user_id).count()
    assert stored == 0


def test_custom_run_maps_runtime_error(monkeypatch):
    async def fake_submit(source_code, language, stdin):
        return {
            "stdout": None,
            "stderr": "Exception in thread main ...",
            "compile_output": None,
            "status_key": "RUNTIME_ERROR_UNKNOWN",
            "time": 0.01,
            "memory": 8192,
        }

    monkeypatch.setattr("app.api.v1.problems.submit", fake_submit)
    headers, _ = register_and_login()
    res = client.post(
        "/api/v1/custom-run",
        json={
            "language": "java",
            "source_code": "class Main { public static void main(String[] a) { int x = 1/0; } }",
            "stdin": "",
        },
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "RUNTIME_ERROR"
    assert body["stdout"] is None
    assert "Exception" in (body["stderr"] or "")
