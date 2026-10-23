"""Resilience of the grader's per-case execution.

A single stalled Judge0 case used to raise and discard the results of every
other case (and the user's whole run). These tests pin the new behaviour: a
case that outlives the deadline degrades to a TLE, while genuine
infrastructure failures still propagate so the route can answer 503.
"""

import asyncio

import pytest

from app.models.enums import SubmissionStatus
from app.services.grader import grade_code
from app.services.judge0 import Judge0Error


def _accepted(stdin: str) -> dict:
    return {"status_key": "ACCEPTED", "stdout": stdin, "time": "0.01", "memory": 100}


def test_timeout_case_becomes_tle_and_others_survive(monkeypatch):
    async def fake_submit(source_code, language, stdin=""):
        if stdin == "slow":
            await asyncio.sleep(10)
        return _accepted(stdin)

    monkeypatch.setattr("app.services.grader.submit", fake_submit)

    cases = [
        {"input": "a", "expected_output": "a"},
        {"input": "slow", "expected_output": "slow"},
        {"input": "c", "expected_output": "c"},
    ]

    result = asyncio.run(grade_code("code", "python", cases, case_timeout=0.05))

    assert [o.status_key for o in result.test_results] == [
        "ACCEPTED",
        "TIME_LIMIT_EXCEEDED",
        "ACCEPTED",
    ]
    # The stalled case alone is blamed; the passing results are not lost.
    assert result.status == SubmissionStatus.TLE
    assert result.test_results[0].passed is True
    assert result.test_results[2].passed is True
    assert "client timeout" in (result.test_results[1].stderr or "")
    # Results stay aligned with the case list so the route can zip them.
    assert [o.index for o in result.test_results] == [0, 1, 2]


def test_timeout_preserves_input_and_hidden_flag(monkeypatch):
    async def fake_submit(source_code, language, stdin=""):
        await asyncio.sleep(10)
        return _accepted(stdin)

    monkeypatch.setattr("app.services.grader.submit", fake_submit)

    hidden_case = {"input": "secret", "expected_output": "secret", "is_hidden": True}
    result = asyncio.run(
        grade_code("code", "python", [hidden_case], case_timeout=0.05)
    )

    outcome = result.test_results[0]
    assert outcome.hidden is True
    assert outcome.input == "secret"
    assert outcome.expected_output == "secret"


def test_all_passing_is_accepted(monkeypatch):
    async def fake_submit(source_code, language, stdin=""):
        return _accepted(stdin)

    monkeypatch.setattr("app.services.grader.submit", fake_submit)

    result = asyncio.run(
        grade_code(
            "code",
            "python",
            [{"input": "a", "expected_output": "a"}],
            case_timeout=1.0,
        )
    )
    assert result.status == SubmissionStatus.ACCEPTED


def test_infrastructure_failure_still_propagates(monkeypatch):
    async def boom(source_code, language, stdin=""):
        raise Judge0Error("judge0 is down")

    monkeypatch.setattr("app.services.grader.submit", boom)

    with pytest.raises(Judge0Error):
        asyncio.run(
            grade_code(
                "code",
                "python",
                [{"input": "a", "expected_output": "a"}],
                case_timeout=1.0,
            )
        )
