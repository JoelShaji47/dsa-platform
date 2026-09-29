"""SQL execution on top of the existing Judge0 Python runtime.

The SQL track reuses the whole DSA grading pipeline (Judge0 container,
``grade_code``, submissions, XP/badges) without touching it: a user query is
embedded in a generated Python harness that

1. reads the test case's seed SQL (DDL + INSERTs) from stdin,
2. builds an in-memory SQLite database from it,
3. runs the single user query,
4. prints the result rows deterministically (sorted, ``|``-separated).

Grading is therefore order-insensitive by design. Problems whose correctness
depends on row order (``ORDER BY``) are not authored until an order-sensitive
mode exists. Seed data must not contain the ``|`` character.

No Supabase, no extra services: ``sqlite3`` is Python stdlib, executed inside
the Judge0 sandbox exactly like any other Python submission.
"""

import json

from app.services.grader import GradeResult, grade_code

COLUMN_SEP = "|"

# Order-sensitive grading protocol. Grading is order-insensitive by default
# (rows sorted before comparison). A test case whose seed SQL starts with
# this marker line is graded in database order instead, which is what makes
# ORDER BY / LIMIT questions possible. The marker is a plain SQL comment, so
# it executes harmlessly as part of the seed script, and one harness source
# can still serve mixed ordered/unordered cases (the flag travels per-case
# via stdin, since the source is shared across cases).
ORDERED_MARKER = "-- SQLHARNESS:ORDERED"


def case_order_matters(case: dict) -> bool:
    return bool(case.get("order_matters")) or case.get("input", "").lstrip().startswith(
        ORDERED_MARKER
    )


class SQLValidationError(Exception):
    pass


def _strip_leading_comments(text: str) -> str:
    """Remove leading ``--`` line comments and ``/* */`` blocks so the first
    keyword of the statement can be inspected."""
    s = text.lstrip()
    while True:
        if s.startswith("--"):
            nl = s.find("\n")
            s = s[nl + 1 :].lstrip() if nl != -1 else ""
        elif s.startswith("/*"):
            end = s.find("*/")
            s = s[end + 2 :].lstrip() if end != -1 else ""
        else:
            return s


def validate_query(query: str) -> str:
    """Ensure the submission is a single read-only SELECT/WITH query.

    Returns the stripped query. Raises ``SQLValidationError`` otherwise, so
    the API can answer 400 before spending a Judge0 call.
    """
    head = _strip_leading_comments(query).upper()
    if not head.startswith(("SELECT", "WITH")):
        raise SQLValidationError(
            "Only single SELECT/WITH queries are allowed "
            "(no DDL, DML, or stacked statements)."
        )
    return query.strip()


def serialize_value(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else repr(value)
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


def serialize_result(rows: list[tuple], ordered: bool) -> str:
    """Deterministic text form of a result set: ``|``-joined columns, one row
    per line. Rows are sorted unless ``ordered`` (ORDER BY questions), in
    which case database order is preserved. The harness and the seed
    verifier share this."""
    lines = [COLUMN_SEP.join(serialize_value(v) for v in row) for row in rows]
    if not ordered:
        lines = sorted(lines)
    return "\n".join(lines)


def serialize_rows(rows: list[tuple]) -> str:
    """Order-insensitive serialization (the default grading mode)."""
    return serialize_result(rows, False)


_HARNESS_TEMPLATE = """import sqlite3
import sys

# Embedded by build_sql_source via json.dumps, which emits a valid Python
# string literal (double-quoted, escaped) — no further decoding needed.
QUERY = %s

def fail(msg):
    sys.stderr.write("SQL_ERROR: " + msg + "\\n")
    sys.exit(1)

def serialize_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else repr(value)
    if isinstance(value, bytes):
        return value.hex()
    return str(value)

seed_sql = sys.stdin.read()
if not seed_sql.strip():
    fail("empty database setup")
ordered = seed_sql.lstrip().startswith(%s)

con = sqlite3.connect(":memory:")
try:
    con.executescript(seed_sql)
except Exception as exc:
    fail("bad setup: %%s" %% exc)

try:
    cur = con.execute(QUERY)
except Exception as exc:
    fail(str(exc))

rows = cur.fetchall()
lines = [%s.join(serialize_value(v) for v in row) for row in rows]
if not ordered:
    lines = sorted(lines)
sys.stdout.write("\\n".join(lines))
"""


def build_sql_source(user_query: str) -> str:
    """Wrap a validated user query in the SQLite harness.

    The query travels JSON-encoded inside the source (never interpolated
    raw), the seed SQL travels via stdin at grade time.
    """
    query = validate_query(user_query)
    # Positional: QUERY literal, ORDERED marker, column separator — in order
    # of appearance in the template above.
    return _HARNESS_TEMPLATE % (
        json.dumps(query),
        json.dumps(ORDERED_MARKER),
        json.dumps(COLUMN_SEP),
    )


async def grade_sql(user_query: str, test_cases: list[dict]) -> GradeResult:
    """Grade a SQL query against seed-SQL test cases via Judge0 Python.

    Each case is ``{"input": <seed DDL+INSERTs>, "expected_output":
    <serialized rows>, "is_hidden": ...}`` — the exact shape ``grade_code``
    already understands.
    """
    source = build_sql_source(user_query)
    return await grade_code(source, "python", test_cases)
