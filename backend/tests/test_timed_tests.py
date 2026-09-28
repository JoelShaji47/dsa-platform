import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import SessionLocal
from app.main import app
from app.models.enums import Difficulty, SubmissionStatus, TestStatus, Topic
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.test_session import TestProblem, TestSession
from app.models.user import User
from app.services.grader import GradeResult
from app.services.grader import TestOutcome as Outcome

client = TestClient(app)

ROUTES = [
    ("get", "/api/v1/tests/config"),
    ("post", "/api/v1/tests"),
    ("get", "/api/v1/tests/{sid}"),
    ("get", "/api/v1/tests/{sid}/results"),
    ("post", "/api/v1/tests/{sid}/end"),
    ("post", "/api/v1/tests/{sid}/abandon"),
]


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


def stub_grader(monkeypatch, *, status=SubmissionStatus.ACCEPTED, target="app.api.v1.tests.grade_code"):
    """Patch a router's grader and record every call."""
    calls: list[list[dict]] = []

    async def fake(source_code, language, test_cases):
        calls.append(list(test_cases))
        results = []
        for i, case in enumerate(test_cases):
            ok = status == SubmissionStatus.ACCEPTED
            results.append(
                Outcome(
                    index=i,
                    hidden=bool(case.get("is_hidden", False)),
                    passed=ok,
                    status=None,
                    status_key="ACCEPTED" if ok else "WRONG_ANSWER",
                    runtime_ms=1.5 * (i + 1),
                    memory_kb=1024 * (i + 1),
                )
            )
        return GradeResult(status=status, test_results=results)

    monkeypatch.setattr(target, fake)
    return calls


def create_test(headers, topics=None, **kwargs):
    payload = {"topics": topics or [Topic.ARRAY.value, Topic.TREE.value, Topic.DP.value]}
    payload.update(kwargs)
    response = client.post("/api/v1/tests", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def force_deadline(session_id, seconds_from_now):
    with SessionLocal() as db:
        db.query(TestSession).filter(TestSession.id == session_id).update(
            {"deadline_at": datetime.now(timezone.utc) + timedelta(seconds=seconds_from_now)}
        )
        db.commit()


def visible_count(problem_id):
    with SessionLocal() as db:
        problem = db.get(Problem, uuid.UUID(problem_id))
        return sum(1 for c in problem.test_cases if not c.get("is_hidden", False))


def all_case_count(problem_id):
    with SessionLocal() as db:
        problem = db.get(Problem, uuid.UUID(problem_id))
        return len(problem.test_cases)


def submissions_for(user_id):
    with SessionLocal() as db:
        return (
            db.query(Submission)
            .filter(Submission.user_id == user_id)
            .all()
        )


def user_xp(user_id):
    with SessionLocal() as db:
        return db.get(User, user_id).xp


# ---------------------------------------------------------------- auth


@pytest.mark.parametrize("method,path", ROUTES)
def test_routes_require_auth(method, path):
    path = path.format(sid=uuid.uuid4())
    call = getattr(client, method)
    if method == "get":
        response = call(path)
    else:
        response = call(path, json={} if path.endswith("/tests") else None)
    assert response.status_code == 401


# ---------------------------------------------------------------- config


def test_config_scans_topics_from_database():
    headers, _ = register_and_login()
    body = client.get("/api/v1/tests/config", headers=headers).json()

    listed = {row["topic"]: row for row in body["topics"]}
    assert set(listed) == {t.value for t in Topic}

    with SessionLocal() as db:
        solvable = (
            db.query(Problem)
            .filter(
                Problem.starter_code != text("'{}'::jsonb"),
                Problem.test_cases != text("'[]'::jsonb"),
            )
            .all()
        )
    assert sum(row["total"] for row in body["topics"]) == len(solvable)

    for row in body["topics"]:
        assert row["easy"] >= 1, row
        assert row["medium"] >= 1, row
        assert row["hard"] >= 1, row


# ---------------------------------------------------------------- generation


def test_create_returns_one_of_each_difficulty():
    headers, _ = register_and_login()
    body = create_test(headers)

    assert len(body["problems"]) == 3
    assert {p["difficulty"] for p in body["problems"]} == {
        Difficulty.EASY.value,
        Difficulty.MEDIUM.value,
        Difficulty.HARD.value,
    }
    assert [p["position"] for p in body["problems"]] == [1, 2, 3]


def test_created_problems_are_solvable_and_distinct():
    headers, _ = register_and_login()
    body = create_test(headers)

    ids = {p["problem_id"] for p in body["problems"]}
    assert len(ids) == 3, "slots must never repeat a problem"

    for problem in body["problems"]:
        assert problem["starter_code"], problem["slug"]
        assert problem["test_cases"], problem["slug"]
        with SessionLocal() as db:
            stored = db.get(Problem, uuid.UUID(problem["problem_id"]))
            assert stored.starter_code and stored.test_cases


def test_three_or_more_topics_guarantee_three_distinct_categories():
    headers, _ = register_and_login()
    selection = [Topic.ARRAY.value, Topic.TREE.value, Topic.GRAPH.value, Topic.DP.value]
    body = create_test(headers, topics=selection)

    assigned = body["assigned_topics"]
    assert len(set(assigned)) == 3, assigned
    assert set(assigned).issubset(set(selection))
    for problem in body["problems"]:
        assert problem["category"] in selection


def test_two_topics_use_every_selected_category():
    headers, _ = register_and_login()
    selection = [Topic.TREE.value, Topic.GRAPH.value]
    body = create_test(headers, topics=selection)

    assert set(body["assigned_topics"]) == set(selection)


def test_single_topic_is_used_for_all_three_slots():
    headers, _ = register_and_login()
    body = create_test(headers, topics=[Topic.STACK.value])

    assert body["assigned_topics"] == [Topic.STACK.value] * 3
    assert {p["category"] for p in body["problems"]} == {Topic.STACK.value}


def test_deadline_is_server_side():
    headers, _ = register_and_login()
    body = create_test(headers, duration_seconds=1800)

    started = datetime.fromisoformat(body["started_at"])
    deadline = datetime.fromisoformat(body["deadline_at"])
    assert abs((deadline - started).total_seconds() - 1800) < 2
    assert 1790 <= body["time_remaining_seconds"] <= 1800


def test_create_abandons_a_live_session():
    headers, _ = register_and_login()
    first = create_test(headers)
    second = create_test(headers)

    with SessionLocal() as db:
        old = db.get(TestSession, uuid.UUID(first["id"]))
        assert old.status == TestStatus.ABANDONED
        assert second["id"] != first["id"]


def test_create_rejects_empty_topics():
    headers, _ = register_and_login()
    response = client.post("/api/v1/tests", json={"topics": []}, headers=headers)
    assert response.status_code == 422


def test_another_users_session_is_not_found():
    headers_a, _ = register_and_login()
    headers_b, _ = register_and_login()
    body = create_test(headers_a)

    response = client.get(f"/api/v1/tests/{body['id']}", headers=headers_b)
    assert response.status_code == 404


# ---------------------------------------------------------------- drafts


def test_draft_persists_across_reload():
    headers, _ = register_and_login()
    body = create_test(headers)
    question = body["problems"][0]

    client.put(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/draft",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    reloaded = client.get(f"/api/v1/tests/{body['id']}", headers=headers).json()
    saved = next(p for p in reloaded["problems"] if p["id"] == question["id"])
    assert saved["code"] == "print(1)"
    assert saved["language"] == "python"


# ---------------------------------------------------------------- run


def test_run_uses_visible_cases_only(monkeypatch):
    headers, _ = register_and_login()
    calls = stub_grader(monkeypatch)
    body = create_test(headers)
    question = body["problems"][0]

    response = client.post(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/run",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    assert response.status_code == 200
    assert len(calls) == 1
    assert len(calls[0]) == visible_count(question["problem_id"])
    assert not any(c.get("is_hidden") for c in calls[0])


def test_run_does_not_record_an_attempt(monkeypatch):
    headers, user_id = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    question = body["problems"][0]

    client.post(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/run",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    assert submissions_for(user_id) == []
    reloaded = client.get(f"/api/v1/tests/{body['id']}", headers=headers).json()
    saved = next(p for p in reloaded["problems"] if p["id"] == question["id"])
    assert saved["attempts"] == 0


# ---------------------------------------------------------------- submit


def test_submit_grades_every_case_including_hidden(monkeypatch):
    headers, _ = register_and_login()
    calls = stub_grader(monkeypatch)
    body = create_test(headers)
    question = body["problems"][0]

    client.post(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    assert len(calls) == 1
    assert len(calls[0]) == all_case_count(question["problem_id"])
    assert any(c.get("is_hidden") for c in calls[0])


def test_submit_records_the_attempt(monkeypatch):
    headers, user_id = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    question = body["problems"][0]

    response = client.post(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["passed"] is True
    assert response.json()["attempts"] == 1

    rows = submissions_for(user_id)
    assert len(rows) == 1
    assert rows[0].test_session_id is not None
    assert rows[0].test_problem_id is not None
    assert rows[0].status == SubmissionStatus.ACCEPTED


def test_last_submit_wins(monkeypatch):
    headers, user_id = register_and_login()
    body = create_test(headers)
    question = body["problems"][0]
    url = f"/api/v1/tests/{body['id']}/questions/{question['id']}/submit"

    stub_grader(monkeypatch, status=SubmissionStatus.ACCEPTED)
    first = client.post(
        url, json={"language": "python", "source_code": "print(1)"}, headers=headers
    ).json()
    assert first["passed"] is True

    stub_grader(monkeypatch, status=SubmissionStatus.WRONG_ANSWER)
    second = client.post(
        url, json={"language": "python", "source_code": "print(2)"}, headers=headers
    ).json()
    assert second["passed"] is False
    assert second["attempts"] == 2

    with SessionLocal() as db:
        stored = db.get(TestProblem, uuid.UUID(question["id"]))
        assert stored.passed is False
        assert stored.attempts == 2
    assert len(submissions_for(user_id)) == 2


def test_submit_awards_no_xp_or_streak(monkeypatch):
    headers, user_id = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    question = body["problems"][0]

    client.post(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    with SessionLocal() as db:
        user = db.get(User, user_id)
        assert user.xp == 0
        assert user.current_streak == 0


def test_test_solve_does_not_mark_the_problem_solved(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    question = body["problems"][0]

    client.post(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    detail = client.get(f"/api/v1/problems/{question['slug']}", headers=headers).json()
    assert detail["solved"] is False

    stats = client.get("/api/v1/stats/me", headers=headers).json()
    assert stats["total_solved"] == 0
    assert stats["total_submissions"] == 0
    assert stats["recent_submissions"] == []

    problems = client.get("/api/v1/problems", headers=headers).json()
    listed = next(p for p in problems if p["slug"] == question["slug"])
    assert listed["solved"] is False


def test_later_solo_solve_still_earns_xp_after_a_test_solve(monkeypatch):
    headers, user_id = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    question = body["problems"][0]

    client.post(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    stub_grader(
        monkeypatch,
        status=SubmissionStatus.ACCEPTED,
        target="app.api.v1.problems.grade_code",
    )
    result = client.post(
        f"/api/v1/problems/{question['slug']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    assert result.json()["xp_awarded"] > 0
    assert user_xp(user_id) > 0


# ---------------------------------------------------------------- end / timeout


def test_end_tallies_without_grading(monkeypatch):
    headers, _ = register_and_login()
    calls = stub_grader(monkeypatch)
    body = create_test(headers)
    question = body["problems"][0]
    client.post(
        f"/api/v1/tests/{body['id']}/questions/{question['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    before = len(calls)

    response = client.post(f"/api/v1/tests/{body['id']}/end", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == TestStatus.SUBMITTED.value
    assert len(calls) == before, "end must never call the grader"


def test_unsubmitted_questions_score_zero(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    client.post(
        f"/api/v1/tests/{body['id']}/questions/{body['problems'][0]['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    client.post(f"/api/v1/tests/{body['id']}/end", headers=headers)

    results = client.get(f"/api/v1/tests/{body['id']}/results", headers=headers).json()
    assert results["score"] == 1
    assert results["passed_count"] == 1
    assert results["total"] == 3
    assert [r["passed"] for r in results["results"]] == [True, False, False]
    assert results["results"][1]["attempts"] == 0
    assert results["results"][1]["status"] is None


def test_end_is_idempotent(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    first = client.post(f"/api/v1/tests/{body['id']}/end", headers=headers).json()
    second = client.post(f"/api/v1/tests/{body['id']}/end", headers=headers).json()
    assert first["status"] == TestStatus.SUBMITTED.value
    assert second["status"] == TestStatus.SUBMITTED.value


def test_past_deadline_expires_lazily(monkeypatch):
    headers, _ = register_and_login()
    calls = stub_grader(monkeypatch)
    body = create_test(headers)
    force_deadline(body["id"], -60)

    state = client.get(f"/api/v1/tests/{body['id']}", headers=headers).json()
    assert state["status"] == TestStatus.EXPIRED.value
    assert state["time_remaining_seconds"] == 0
    assert calls == []


def test_submit_after_deadline_is_rejected(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    force_deadline(body["id"], -60)

    response = client.post(
        f"/api/v1/tests/{body['id']}/questions/{body['problems'][0]['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    assert response.status_code == 409
    with SessionLocal() as db:
        assert db.get(TestSession, uuid.UUID(body["id"])).status == TestStatus.EXPIRED


def test_expired_session_still_produces_results(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    client.post(
        f"/api/v1/tests/{body['id']}/questions/{body['problems'][0]['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    force_deadline(body["id"], -60)

    results = client.get(f"/api/v1/tests/{body['id']}/results", headers=headers).json()
    assert results["status"] == TestStatus.EXPIRED.value
    assert results["score"] == 1
    assert results["time_taken_seconds"] <= results["score"] * 0 + 3600


# ---------------------------------------------------------------- abandon


def test_abandon_marks_the_session(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)

    assert client.post(f"/api/v1/tests/{body['id']}/abandon", headers=headers).status_code == 204
    state = client.get(f"/api/v1/tests/{body['id']}", headers=headers).json()
    assert state["status"] == TestStatus.ABANDONED.value

    response = client.get(f"/api/v1/tests/{body['id']}/results", headers=headers)
    assert response.status_code == 409


def test_abandoned_session_rejects_submissions(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    client.post(f"/api/v1/tests/{body['id']}/abandon", headers=headers)

    response = client.post(
        f"/api/v1/tests/{body['id']}/questions/{body['problems'][0]['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    assert response.status_code == 409


# ---------------------------------------------------------------- results


def test_results_are_refetchable_after_end(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    client.post(
        f"/api/v1/tests/{body['id']}/questions/{body['problems'][0]['id']}/submit",
        json={"language": "python", "source_code": "print(1)"},
        headers=headers,
    )
    client.post(f"/api/v1/tests/{body['id']}/end", headers=headers)

    first = client.get(f"/api/v1/tests/{body['id']}/results", headers=headers).json()
    second = client.get(f"/api/v1/tests/{body['id']}/results", headers=headers).json()
    assert first == second
    assert first["assigned_topics"] == body["assigned_topics"]
    assert first["results"][0]["category"] == body["problems"][0]["category"]


def test_results_unavailable_while_in_progress(monkeypatch):
    headers, _ = register_and_login()
    stub_grader(monkeypatch)
    body = create_test(headers)
    response = client.get(f"/api/v1/tests/{body['id']}/results", headers=headers)
    assert response.status_code == 409
