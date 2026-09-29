"""End-to-end SQL flow check against the real Judge0 container.

Exercises the full production path (no mocks):
  sql_grader.build_sql_source -> grader.grade_code -> judge0.submit

For every SQL seed problem:
  1. reference_solution must grade ACCEPTED (all visible + hidden cases),
  2. a deliberately wrong query must NOT be accepted,
  3. a write query must be rejected before any Judge0 call.

Usage (from backend/):
  DATABASE_URL="postgresql+psycopg://dsa_user:dsa_pass@localhost:5432/dsa_platform" \\
      .venv/bin/python scripts/e2e_sql_flow.py
"""

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.models.enums import SubmissionStatus
from app.seeds import PROBLEMS
from app.services.sql_grader import (
    SQLValidationError,
    build_sql_source,
    grade_sql,
)

WRONG_QUERY = "SELECT 'wrong' AS nope;"


async def check_problem(problem: dict) -> bool:
    slug = problem["slug"]
    cases = [dict(tc) for tc in problem["test_cases"]]
    reference = problem["reference_solution"]
    ok = True

    result = await grade_sql(reference, cases)
    passed = [t.index for t in result.test_results if t.passed]
    print(f"[{'ok' if result.status == SubmissionStatus.ACCEPTED else 'FAIL'}] {slug}: "
          f"reference -> {result.status.value} "
          f"({len(passed)}/{len(cases)} cases passed)")
    if result.status != SubmissionStatus.ACCEPTED:
        ok = False
        for t in result.test_results:
            if not t.passed:
                print(f"    case {t.index} hidden={t.hidden} "
                      f"key={t.status_key} actual={t.actual_output!r} err={t.stderr!r}")

    wrong = await grade_sql(WRONG_QUERY, cases)
    wrong_ok = wrong.status != SubmissionStatus.ACCEPTED
    print(f"[{'ok' if wrong_ok else 'FAIL'}] {slug}: "
          f"wrong query -> {wrong.status.value} (must not be ACCEPTED)")
    ok = ok and wrong_ok
    return ok


async def main() -> None:
    sql_problems = [p for p in PROBLEMS if p["topic"] == "SQL"]
    print(f"SQL problems in catalog: {len(sql_problems)}")
    all_ok = True
    for problem in sql_problems:
        n_visible = sum(1 for c in problem["test_cases"] if not c["is_hidden"])
        n_hidden = sum(1 for c in problem["test_cases"] if c["is_hidden"])
        print(f"-- {problem['slug']} [{problem['difficulty']}] "
              f"visible={n_visible} hidden={n_hidden}")
        try:
            all_ok = await check_problem(problem) and all_ok
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"[FAIL] {problem['slug']}: raised {type(exc).__name__}: {exc}")
            all_ok = False

    try:
        build_sql_source("DROP TABLE employees;")
        print("[FAIL] write query was not rejected")
        all_ok = False
    except SQLValidationError as exc:
        print(f"[ok] write query rejected pre-Judge0: {exc}")

    print("E2E RESULT:", "PASS" if all_ok else "FAIL")
    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
