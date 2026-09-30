"""Main vs function grading modes."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_test_user
from app.models.enums import SubmissionStatus
from app.services.grader import (
    GradeResult,
    ModeError,
    TestOutcome,
    build_source,
    function_modes_for,
)
from app.services import grader as grader_module  # noqa: F401 (kept for monkeypatch target clarity)

client = TestClient(app)


class FakeProblem:
    function_starter = {"python": "def solve(a): ..."}
    function_driver = {"python": {"prefix": "HEAD\n", "suffix": "\nTAIL"}}


class BareProblem:
    function_starter = {}
    function_driver = {}


def test_main_mode_passes_through():
    assert build_source(FakeProblem(), "python", "print(1)", "main") == "print(1)"


def test_function_mode_wraps():
    src = build_source(FakeProblem(), "python", "CODE", "function")
    assert src == "HEAD\nCODE\n\nTAIL"


def test_function_modes_for_lists_complete_langs_only():
    assert function_modes_for(FakeProblem()) == ["python"]
    assert function_modes_for(BareProblem()) == []


def test_function_mode_missing_driver_raises():
    with pytest.raises(ModeError):
        build_source(BareProblem(), "python", "x", "function")


def register_and_login():
    suffix = uuid.uuid4().hex[:8]
    headers, _ = make_test_user(username=f"mode_{suffix}")
    return headers


def stub_grade(monkeypatch):
    async def fake(source_code, language, test_cases):
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                TestOutcome(index=0, hidden=False, passed=True, status_key="ACCEPTED")
            ],
        )

    monkeypatch.setattr("app.api.v1.problems.grade_code", fake)


def test_run_function_mode_two_sum(monkeypatch):
    headers = register_and_login()
    captured = {}

    async def fake(source_code, language, test_cases):
        captured["src"] = source_code
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                TestOutcome(index=0, hidden=False, passed=True, status_key="ACCEPTED")
            ],
        )

    monkeypatch.setattr("app.api.v1.problems.grade_code", fake)
    r = client.post(
        "/api/v1/problems/two-sum/run",
        json={"language": "python", "source_code": "def solve(nums, target): return [0, 1]", "mode": "function"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert "ans = solve(nums, target)" in captured["src"]


def test_run_function_mode_rejected_without_driver(monkeypatch):
    headers = register_and_login()
    stub_grade(monkeypatch)
    r = client.post(
        "/api/v1/problems/contains-duplicate/run",
        json={"language": "python", "source_code": "x", "mode": "function"},
        headers=headers,
    )
    assert r.status_code == 400
    assert "not available" in r.json()["detail"]


def test_problem_detail_exposes_function_modes():
    headers = register_and_login()
    body = client.get("/api/v1/problems/two-sum", headers=headers).json()
    assert set(body["function_modes"]) == {"python", "cpp", "java"}
    other = client.get("/api/v1/problems/contains-duplicate", headers=headers).json()
    assert other["function_modes"] == []
