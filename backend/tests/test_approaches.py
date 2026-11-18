"""Solution ladders: seed shape, API exposure, and admin round-trip.

The ladder is the "graded on approach" surface — it must stay ordered
(cheapest rung first), carry both complexities, and only point at traces that
actually exist so the visualizer handoff can never dangle.
"""

import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.models.problem import Problem
from app.seeds import PROBLEMS
from app.seeds.data_approaches import APPROACHES
from app.seeds.schema import ProblemSeed
from tests.conftest import make_test_user

client = TestClient(app)


def make_user_and_token():
    headers, _ = make_test_user()
    return headers


def make_admin(user_id):
    from app.db.session import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.is_admin = True
        db.commit()


# --- seed-level invariants (no DB) ---


def test_every_problem_seed_validates():
    """A malformed rung would blow up scripts/seed.py; catch it here first."""
    for raw in PROBLEMS:
        ProblemSeed.model_validate(raw)


def test_ladders_are_ordered_and_fully_described():
    slugs = {p["slug"] for p in PROBLEMS}
    for slug, ladder in APPROACHES.items():
        assert slug in slugs, f"ladder for unknown slug: {slug}"
        assert len(ladder) >= 2, f"{slug}: a ladder needs at least a slower and a faster rung"
        for rung in ladder:
            assert rung.name and rung.idea
            assert rung.time_complexity and rung.space_complexity
            if rung.trace_key:
                assert rung.trace_key in slugs, (
                    f"{slug}: trace_key {rung.trace_key!r} is not a seeded problem"
                )


def test_brute_force_never_carries_a_trace():
    """The player animates the intended solution; a brute-force rung should not
    advertise a trace it does not have."""
    for slug, ladder in APPROACHES.items():
        assert ladder[0].trace_key is None, f"{slug}: first rung should be the naive one"


# --- API exposure ---


def test_detail_exposes_the_ladder_cheapest_first():
    headers = make_user_and_token()
    body = client.get("/api/v1/problems/two-sum", headers=headers).json()

    ladder = body["approaches"]
    assert [rung["name"] for rung in ladder] == [
        "Brute force pairs",
        "Sort + two pointers",
        "One-pass hash map",
    ]
    assert all(rung["time_complexity"] and rung["space_complexity"] for rung in ladder)
    # Only the rung with a step-by-step trace carries the visualizer key.
    assert [rung["trace_key"] for rung in ladder] == [None, None, "two-sum"]


def test_problem_without_a_ladder_returns_empty_list():
    headers = make_user_and_token()
    body = client.get("/api/v1/problems/reverse-linked-list", headers=headers).json()
    assert body["approaches"] == []


def test_approaches_are_not_leaked_by_the_list_endpoint():
    """The ladder is detail-page content; the library list stays lean."""
    headers = make_user_and_token()
    body = client.get("/api/v1/problems", headers=headers).json()
    assert all("approaches" not in item for item in body)


# --- admin round-trip ---


def test_admin_can_replace_a_ladder():
    admin_headers, admin_id = make_test_user(domain="admintest.com")
    make_admin(admin_id)
    slug = f"ladder-probe-{uuid.uuid4().hex[:6]}"

    created = client.post(
        "/api/v1/admin/problems",
        json={
            "title": "Ladder Probe",
            "slug": slug,
            "difficulty": "EASY",
            "topic": "ARRAY",
            "approaches": [
                {
                    "name": "Naive",
                    "idea": "Try everything and hope.",
                    "time_complexity": "O(n^2)",
                    "space_complexity": "O(1)",
                }
            ],
        },
        headers=admin_headers,
    )
    assert created.status_code == 201
    assert created.json()["approaches"][0]["name"] == "Naive"

    patched = client.patch(
        f"/api/v1/admin/problems/{slug}",
        json={
            "approaches": [
                {
                    "name": "Linear",
                    "idea": "One pass with a hash map.",
                    "time_complexity": "O(n)",
                    "space_complexity": "O(n)",
                    "trace_key": "two-sum",
                }
            ]
        },
        headers=admin_headers,
    )
    assert patched.status_code == 200
    ladder = patched.json()["approaches"]
    assert len(ladder) == 1
    assert ladder[0]["name"] == "Linear"
    assert ladder[0]["trace_key"] == "two-sum"

    from app.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.query(Problem).filter(Problem.slug == slug).one()
        assert row.approaches[0]["time_complexity"] == "O(n)"
        db.delete(row)
        db.commit()
