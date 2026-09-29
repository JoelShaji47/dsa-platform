import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.enums import SubmissionStatus
from app.models.hint import ProblemHint
from app.models.problem import Problem
from app.models.submission import Submission
from app.services.grader import GradeResult, TestOutcome as Outcome

client = TestClient(app)

REVIEW_JSON = json.dumps(
    {
        "verdict": "Your loop never terminates for negative targets.",
        "bug_type": "infinite-loop",
        "explanation": "The `left` pointer never advances when `total > target`.",
        "fix_hint": "Advance the left pointer and shrink the window.",
    }
)


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
    user_id = uuid.UUID(client.get("/api/v1/auth/me", headers=headers).json()["id"])
    return headers, user_id


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


def install_gemini_mock(monkeypatch):
    calls = {"count": 0}

    def fake_generate_sync(prompt, system_instruction=None, json_mode=False):
        calls["count"] += 1
        if json_mode:
            return REVIEW_JSON
        return f"mock hint for prompt: {prompt[:40]}"

    monkeypatch.setattr(
        "app.services.tutor.gemini.generate_sync", fake_generate_sync
    )
    return calls


def purge_hint_cache(slug="two-sum"):
    with SessionLocal() as db:
        problem = db.query(Problem).filter(Problem.slug == slug).one()
        db.query(ProblemHint).filter(ProblemHint.problem_id == problem.id).delete()
        db.commit()


@pytest.fixture(autouse=True)
def clean_hint_cache():
    with SessionLocal() as db:
        db.query(ProblemHint).delete()
        db.commit()
    yield
    with SessionLocal() as db:
        db.query(ProblemHint).delete()
        db.commit()


def reveal_hint(headers, level=1, slug="two-sum"):
    return client.post(
        f"/api/v1/problems/{slug}/hints/{level}", headers=headers
    ).json()


def submit_accepted(headers, slug="two-sum"):
    return client.post(
        f"/api/v1/problems/{slug}/submit",
        json={"language": "python", "source_code": "sol"},
        headers=headers,
    ).json()


def insert_failed(user_id, slug="two-sum", status=SubmissionStatus.WRONG_ANSWER):
    with SessionLocal() as db:
        problem = db.query(Problem).filter(Problem.slug == slug).one()
        submission = Submission(
            user_id=user_id,
            problem_id=problem.id,
            code="print('broken')",
            language="python",
            status=status,
            runtime_ms=5.0,
            memory_kb=2048.0,
            judge_summary=[
                {"index": 0, "passed": True},
                {"index": 1, "passed": False},
            ],
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission.id


def test_hint_reveal_generates_and_caches(monkeypatch):
    headers, _ = register_and_login()
    calls = install_gemini_mock(monkeypatch)
    purge_hint_cache()

    first = reveal_hint(headers, level=1)
    assert calls["count"] == 1
    assert first["level"] == 1
    assert first["label"] == "Nudge"
    assert first["content"].startswith("mock hint")

    second = reveal_hint(headers, level=1)
    assert calls["count"] == 1
    assert second["content"] == first["content"]

    meta = client.get("/api/v1/problems/two-sum/hints", headers=headers).json()
    assert meta["total_levels"] == 3
    assert meta["xp_forfeit_applies"] is True
    revealed = {entry["level"]: entry["revealed"] for entry in meta["levels"]}
    assert revealed == {1: True, 2: False, 3: False}


def test_hint_level_validation(monkeypatch):
    headers, _ = register_and_login()
    install_gemini_mock(monkeypatch)
    response = client.post("/api/v1/problems/two-sum/hints/7", headers=headers)
    assert response.status_code == 400


def test_submit_without_hints_keeps_xp(monkeypatch):
    headers, _ = register_and_login()
    stub_accept(monkeypatch)
    result = submit_accepted(headers)
    assert result["xp_awarded"] == 16
    assert result["xp_forfeited"] is False


def test_submit_after_hint_forfeits_first_solve_xp(monkeypatch):
    headers, _ = register_and_login()
    stub_accept(monkeypatch)
    install_gemini_mock(monkeypatch)
    reveal_hint(headers, level=1)

    result = submit_accepted(headers)
    assert result["status"] == "ACCEPTED"
    assert result["xp_awarded"] == 0
    assert result["xp_forfeited"] is True
    assert result["user_xp"] == 0

    repeat = submit_accepted(headers)
    assert repeat["xp_awarded"] == 0


def test_review_generates_caches_and_guards(monkeypatch):
    owner_headers, owner_id = register_and_login()
    other_headers, _ = register_and_login()
    calls = install_gemini_mock(monkeypatch)
    submission_id = insert_failed(owner_id)

    foreign = client.post(
        f"/api/v1/submissions/{submission_id}/review", headers=other_headers
    )
    assert foreign.status_code == 404

    first = client.post(
        f"/api/v1/submissions/{submission_id}/review", headers=owner_headers
    )
    assert first.status_code == 200
    body = first.json()
    assert body["bug_type"] == "infinite-loop"
    assert "verdict" in body and "fix_hint" in body
    assert calls["count"] == 1

    cached = client.post(
        f"/api/v1/submissions/{submission_id}/review", headers=owner_headers
    )
    assert cached.json() == body
    assert calls["count"] == 1

    stub_accept(monkeypatch)
    accepted = submit_accepted(owner_headers)
    rejected = client.post(
        f"/api/v1/submissions/{accepted['submission_id']}/review",
        headers=owner_headers,
    )
    assert rejected.status_code == 400
