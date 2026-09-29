import subprocess
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import SubmissionStatus
from app.seeds.data_sql import SQL_PROBLEMS
from app.seeds.schema import ProblemSeed
from app.services.grader import GradeResult
from app.services.grader import TestOutcome as Outcome
from app.services.sql_grader import (
    ORDERED_MARKER,
    SQLValidationError,
    build_sql_source,
    case_order_matters,
    serialize_result,
    serialize_rows,
    validate_query,
)

client = TestClient(app)


# --- harness unit tests (no DB, no network) ---


def test_validate_query_accepts_select_and_with():
    assert validate_query("SELECT 1;").startswith("SELECT")
    assert validate_query("  with x as (select 1) select * from x")
    assert validate_query("-- a comment\nSELECT name FROM t")
    assert validate_query("/* block */\nSeLeCt a FROM t")


def test_validate_query_rejects_writes_and_empty():
    for bad in [
        "",
        "   ",
        "INSERT INTO t VALUES (1)",
        "UPDATE t SET a = 1",
        "DELETE FROM t",
        "DROP TABLE t",
    ]:
        with pytest.raises(SQLValidationError):
            validate_query(bad)
    # Stacked statements start with SELECT, so they pass static validation
    # but are rejected at runtime (sqlite3 executes a single statement).
    assert validate_query("SELECT 1; DROP TABLE t")


def test_serialize_rows_is_sorted_and_stable():
    rows = [(2, "b"), (10, "a"), (None, "x"), (1.0, "y"), (1.5, "z")]
    # Sort is lexicographic on the serialized row (consistent for both
    # sides of the comparison, since both go through this function).
    assert serialize_rows(rows) == "1.5|z\n10|a\n1|y\n2|b\nNULL|x"


def test_harness_executes_locally_end_to_end(tmp_path):
    """The generated harness is plain Python: run it with the test
    interpreter, feeding seed SQL on stdin, and check the printed rows."""
    seed = (
        "CREATE TABLE t (a INTEGER, b TEXT);\n"
        "INSERT INTO t VALUES (2, 'y'), (1, 'x''s'), (3, NULL);\n"
    )
    source = build_sql_source("SELECT a, b FROM t WHERE a > 1")
    proc = subprocess.run(
        [sys.executable, "-c", source],
        input=seed,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == "2|y\n3|NULL"


def test_harness_reports_sql_errors_on_stderr():
    seed = "CREATE TABLE t (a INTEGER);\n"
    for bad_query in ("SELECT nope FROM t", "SELECT 1; DROP TABLE t"):
        source = build_sql_source(bad_query)
        proc = subprocess.run(
            [sys.executable, "-c", source],
            input=seed,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 1
        assert "SQL_ERROR" in proc.stderr


def test_ordered_cases_preserve_database_order():
    ordered_seed = (
        ORDERED_MARKER
        + "\nCREATE TABLE t (a INTEGER);\nINSERT INTO t VALUES (1),(3),(2);\n"
    )
    plain_seed = "CREATE TABLE t (a INTEGER);\nINSERT INTO t VALUES (1),(3),(2);\n"
    assert case_order_matters({"input": ordered_seed}) is True
    assert case_order_matters({"input": plain_seed}) is False
    assert serialize_result([(1,), (3,), (2,)], True) == "1\n3\n2"
    assert serialize_result([(1,), (3,), (2,)], False) == "1\n2\n3"

    source = build_sql_source("SELECT a FROM t ORDER BY a DESC LIMIT 2")
    proc = subprocess.run(
        [sys.executable, "-c", source],
        input=ordered_seed,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == "3\n2"

    # Same rows in the wrong order must NOT match the ordered expectation.
    source_asc = build_sql_source("SELECT a FROM t ORDER BY a ASC LIMIT 2")
    proc_asc = subprocess.run(
        [sys.executable, "-c", source_asc],
        input=ordered_seed,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc_asc.returncode == 0
    assert proc_asc.stdout == "1\n2"
    assert proc_asc.stdout != proc.stdout


# --- seed validation ---


def test_sql_seeds_validate_and_follow_conventions():
    assert len(SQL_PROBLEMS) == 13
    for raw in SQL_PROBLEMS:
        seed = ProblemSeed.model_validate(raw)
        assert seed.topic == "SQL"
        assert set(seed.starter_code.keys()) == {"sql"}
        assert seed.sources == ["sql-topic"]
        assert seed.slug.startswith("sql-")
        assert len(seed.description) >= 50
        assert any(not t.is_hidden for t in seed.test_cases)
        assert any(t.is_hidden for t in seed.test_cases)
        assert raw["reference_solution"]


# --- API tests (need local Postgres, Judge0 mocked) ---


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


def stub_sql_grader(monkeypatch, *, status):
    async def fake(user_query, test_cases):
        assert "SELECT" in user_query.upper()
        return GradeResult(
            status=status,
            test_results=[
                Outcome(
                    index=i,
                    hidden=bool(case.get("is_hidden", False)),
                    passed=status == SubmissionStatus.ACCEPTED,
                    status_key="ACCEPTED"
                    if status == SubmissionStatus.ACCEPTED
                    else "WRONG_ANSWER",
                )
                for i, case in enumerate(test_cases)
            ],
        )

    monkeypatch.setattr("app.api.v1.sql.grade_sql", fake)


def test_sql_routes_require_auth():
    assert client.get("/api/v1/sql").status_code == 401
    assert client.get("/api/v1/sql/sql-select-names").status_code == 401
    payload = {"language": "sql", "source_code": "SELECT 1"}
    assert client.post("/api/v1/sql/sql-select-names/run", json=payload).status_code == 401
    assert (
        client.post("/api/v1/sql/sql-select-names/submit", json=payload).status_code
        == 401
    )


def test_sql_list_only_serves_sql_track():
    headers = make_user_and_token()
    res = client.get("/api/v1/sql", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert {item["slug"] for item in body} == {p["slug"] for p in SQL_PROBLEMS}
    assert all(item["topic"] == "SQL" for item in body)


def test_sql_detail_shows_starter_and_visible_seed_only():
    headers = make_user_and_token()
    res = client.get("/api/v1/sql/sql-select-names", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["starter_code"]["sql"].startswith("--")
    assert len(body["test_cases"]) == 1
    assert "CREATE TABLE employees" in body["test_cases"][0]["input"]
    assert "is_hidden" not in body["test_cases"][0]
    assert body["hidden_test_count"] == 2
    assert body["function_modes"] == []


def test_sql_detail_404_for_dsa_slug_and_unknown_slug():
    headers = make_user_and_token()
    assert client.get("/api/v1/sql/two-sum", headers=headers).status_code == 404
    assert client.get("/api/v1/sql/nope", headers=headers).status_code == 404


def test_dsa_problem_untouched_by_sql_track():
    headers = make_user_and_token()
    res = client.get("/api/v1/problems/two-sum", headers=headers)
    assert res.status_code == 200
    assert res.json()["topic"] == "ARRAY"
    assert "sql" not in res.json()["starter_code"]


def test_sql_run_rejects_non_sql_language_and_writes():
    headers = make_user_and_token()
    bad_lang = client.post(
        "/api/v1/sql/sql-select-names/run",
        json={"language": "python", "source_code": "SELECT 1"},
        headers=headers,
    )
    assert bad_lang.status_code == 400
    bad_query = client.post(
        "/api/v1/sql/sql-select-names/run",
        json={"language": "sql", "source_code": "DROP TABLE employees"},
        headers=headers,
    )
    assert bad_query.status_code == 400


def test_sql_run_and_submit_flow(monkeypatch):
    stub_sql_grader(monkeypatch, status=SubmissionStatus.ACCEPTED)
    headers = make_user_and_token()
    payload = {"language": "sql", "source_code": "SELECT name FROM employees;"}

    run = client.post(
        "/api/v1/sql/sql-select-names/run", json=payload, headers=headers
    )
    assert run.status_code == 200
    assert run.json()["status"] == "ACCEPTED"
    assert len(run.json()["test_results"]) == 1

    submit = client.post(
        "/api/v1/sql/sql-select-names/submit", json=payload, headers=headers
    )
    assert submit.status_code == 200
    body = submit.json()
    assert body["status"] == "ACCEPTED"
    assert body["xp_awarded"] > 0

    history = client.get(
        "/api/v1/problems/sql-select-names/submissions", headers=headers
    )
    assert history.status_code == 200
    assert history.json()[0]["language"] == "sql"


def test_sql_problem_in_timed_test_uses_harness(monkeypatch):
    seen = {}

    async def fake(user_query, test_cases):
        seen["query"] = user_query
        seen["count"] = len(test_cases)
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                Outcome(
                    index=i,
                    hidden=bool(case.get("is_hidden", False)),
                    passed=True,
                    status_key="ACCEPTED",
                )
                for i, case in enumerate(test_cases)
            ],
        )

    monkeypatch.setattr("app.api.v1.tests.grade_sql", fake)
    headers = make_user_and_token()
    res = client.post("/api/v1/tests", json={"topics": ["SQL"]}, headers=headers)
    assert res.status_code == 201, res.text
    session = res.json()
    assert len(session["problems"]) == 3

    question = session["problems"][0]
    run = client.post(
        f"/api/v1/tests/{session['id']}/questions/{question['id']}/run",
        json={"language": "sql", "source_code": "SELECT 1;"},
        headers=headers,
    )
    assert run.status_code == 200
    assert run.json()["status"] == "ACCEPTED"
    assert seen["query"].strip().upper().startswith("SELECT")
