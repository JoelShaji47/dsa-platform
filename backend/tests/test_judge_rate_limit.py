"""Judge endpoints are rate limited.

``/run`` and ``/submit`` fan out to Judge0, which is the most expensive thing
the API does (one Java box reserves ~4 GB). These tests trip the guard
deliberately by shrinking the limit and assert a 429 with a cooldown header.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import SubmissionStatus
from app.services.grader import GradeResult, TestOutcome
from tests.conftest import make_test_user

client = TestClient(app)


def stub_grader(monkeypatch, status=SubmissionStatus.ACCEPTED):
    async def fake(source_code, language, test_cases):
        key = "ACCEPTED" if status == SubmissionStatus.ACCEPTED else status.value
        return GradeResult(
            status=status,
            test_results=[
                TestOutcome(
                    index=i,
                    hidden=bool(case.get("is_hidden", False)),
                    passed=status == SubmissionStatus.ACCEPTED,
                    status=None if status == SubmissionStatus.ACCEPTED else status,
                    status_key=key,
                    input=case.get("input", ""),
                    expected_output=case.get("expected_output", ""),
                    actual_output=case.get("input", ""),
                )
                for i, case in enumerate(test_cases)
            ],
        )

    monkeypatch.setattr("app.api.v1.problems.grade_code", fake)


def test_run_route_is_rate_limited(monkeypatch):
    from app.api.v1 import problems as problems_api

    headers, _ = make_test_user()
    stub_grader(monkeypatch)
    monkeypatch.setattr(problems_api.JUDGE_RUN_LIMITER, "limit", 1)

    payload = {"language": "python", "source_code": "print(1)"}
    url = "/api/v1/problems/two-sum/run"

    assert client.post(url, json=payload, headers=headers).status_code == 200

    blocked = client.post(url, json=payload, headers=headers)
    assert blocked.status_code == 429
    assert blocked.headers["retry-after"] == "60"


def test_submit_route_is_rate_limited(monkeypatch):
    from app.api.v1 import problems as problems_api

    headers, _ = make_test_user()
    # WRONG_ANSWER keeps the submit path off the xp/streak side effects.
    stub_grader(monkeypatch, status=SubmissionStatus.WRONG_ANSWER)
    monkeypatch.setattr(problems_api.JUDGE_SUBMIT_LIMITER, "limit", 1)

    payload = {"language": "python", "source_code": "print(1)"}
    url = "/api/v1/problems/two-sum/submit"

    assert client.post(url, json=payload, headers=headers).status_code == 200

    blocked = client.post(url, json=payload, headers=headers)
    assert blocked.status_code == 429
    assert blocked.headers["retry-after"] == "60"


def test_run_and_submit_have_independent_budgets(monkeypatch):
    """Exhausting runs must not block a submit."""
    from app.api.v1 import problems as problems_api

    headers, _ = make_test_user()
    stub_grader(monkeypatch, status=SubmissionStatus.WRONG_ANSWER)
    monkeypatch.setattr(problems_api.JUDGE_RUN_LIMITER, "limit", 1)

    payload = {"language": "python", "source_code": "print(1)"}
    run_url = "/api/v1/problems/two-sum/run"
    submit_url = "/api/v1/problems/two-sum/submit"

    assert client.post(run_url, json=payload, headers=headers).status_code == 200
    assert client.post(run_url, json=payload, headers=headers).status_code == 429
    # Submit has its own limiter, still untouched.
    assert client.post(submit_url, json=payload, headers=headers).status_code == 200


def stub_sql_grader(monkeypatch):
    async def fake(user_query, test_cases):
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                TestOutcome(
                    index=i,
                    hidden=bool(case.get("is_hidden", False)),
                    passed=True,
                    status_key="ACCEPTED",
                )
                for i, case in enumerate(test_cases)
            ],
        )

    monkeypatch.setattr("app.api.v1.sql.grade_sql", fake)


def test_sql_run_route_shares_the_judge_budget(monkeypatch):
    """The SQL track hits the same Postgres-backed judge, so it is metered too."""
    from app.api.v1 import sql as sql_api

    headers, _ = make_test_user()
    stub_sql_grader(monkeypatch)
    monkeypatch.setattr(sql_api.JUDGE_RUN_LIMITER, "limit", 1)

    payload = {"language": "sql", "source_code": "SELECT 1"}
    url = "/api/v1/sql/sql-select-names/run"

    assert client.post(url, json=payload, headers=headers).status_code == 200
    assert client.post(url, json=payload, headers=headers).status_code == 429

