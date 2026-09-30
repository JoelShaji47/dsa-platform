"""Verify SQL seed content offline (no Judge0, no database).

For every problem in app/seeds/data_sql.py, runs ``reference_solution``
against each test case's seed SQL in a local in-memory SQLite database and
compares the result — serialized with the same function the grading harness
uses — to the authored ``expected_output``.

Usage (from backend/): .venv/bin/python scripts/verify_sql_seeds.py
"""

import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.seeds.data_sql import SQL_PROBLEMS
from app.services.sql_grader import (
    build_sql_source,
    case_order_matters,
    serialize_result,
    validate_query,
)


def run_reference(seed_sql: str, query: str, ordered: bool) -> str:
    con = sqlite3.connect(":memory:")
    con.executescript(seed_sql)
    rows = con.execute(query).fetchall()
    con.close()
    return serialize_result(rows, ordered)


def main() -> None:
    failures = 0
    for problem in SQL_PROBLEMS:
        slug = problem["slug"]
        reference = problem.get("reference_solution")
        if not reference:
            print(f"[FAIL] {slug}: missing reference_solution")
            failures += 1
            continue
        try:
            validate_query(reference)
            build_sql_source(reference)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"[FAIL] {slug}: reference rejected by harness: {exc}")
            failures += 1
            continue
        for i, case in enumerate(problem["test_cases"]):
            try:
                actual = run_reference(
                    case["input"], reference, case_order_matters(case)
                )
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"[FAIL] {slug} case {i}: reference raised {exc}")
                failures += 1
                continue
            if actual != case["expected_output"]:
                failures += 1
                print(f"[FAIL] {slug} case {i} (hidden={case.get('is_hidden')}):")
                print(f"  expected: {case['expected_output']!r}")
                print(f"  actual:   {actual!r}")
            else:
                print(f"[ok] {slug} case {i}")
    print(f"checked {len(SQL_PROBLEMS)} problems -> failures={failures}")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
