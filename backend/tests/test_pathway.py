"""Layer 2 pathway: ordering, prerequisites, determinism, API surface."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.enums import SubmissionStatus
from app.models.problem import Problem
from app.models.skill_estimate import SkillEstimate
from app.models.submission import Submission
from app.services import pathway, skill_model
from app.services.roadmap import PATTERNS, PATTERN_BY_KEY, get_user_progress
from tests.conftest import make_test_user

NOW = datetime.now(timezone.utc)
client = TestClient(app)


def _solvable_slugs(db, pattern_key, limit=3):
    rows = (
        db.query(Problem)
        .filter(Problem.pattern_key == pattern_key, Problem.is_published.is_(True))
        .all()
    )
    return [p.slug for p in rows if p.starter_code and p.test_cases][:limit]


def _cleanup(user_id, slugs=()):
    with SessionLocal() as db:
        db.query(Submission).filter(Submission.user_id == user_id).delete()
        db.query(SkillEstimate).filter(SkillEstimate.user_id == user_id).delete()
        db.query(Problem).filter(Problem.slug.in_(list(slugs))).update(
            {Problem.difficulty_b: None, Problem.difficulty_n: 0}
        )
        db.commit()


def test_pathway_is_deterministic_and_non_empty_for_a_cold_user():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            from app.models.user import User

            user = db.get(User, uid)
            first = pathway.build_pathway(db, user)
        with SessionLocal() as db:
            from app.models.user import User

            user = db.get(User, uid)
            second = pathway.build_pathway(db, user)

        assert first["objective"] == pathway.OBJECTIVE
        assert first["steps"], "a cold user still gets a plan"
        assert first == second
        assert first["total_hours"] > 0
    finally:
        _cleanup(uid)


def test_pathway_steps_respect_prerequisites_and_are_unique():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            from app.models.user import User

            user = db.get(User, uid)
            plan = pathway.build_pathway(db, user)
            progress = get_user_progress(db, user)

        keys = [s["pattern_key"] for s in plan["steps"]]
        assert len(keys) == len(set(keys))

        # Every prerequisite of a step is either already satisfied for this
        # learner or appears earlier in the plan.
        seen = set()
        for step in plan["steps"]:
            prereqs = PATTERN_BY_KEY[step["pattern_key"]]["prerequisites"]
            for pk in prereqs:
                already = progress[pk].solved > 0 or (
                    progress[pk].skill_n >= skill_model.MIN_UNLOCK_EVIDENCE
                    and progress[pk].solve_rate >= skill_model.UNLOCK_SOLVE_RATE
                )
                assert already or pk in seen, (
                    f"{step['pattern_key']} scheduled before prerequisite {pk}"
                )
            seen.add(step["pattern_key"])

        # Each step is a real amount of remaining work.
        for step in plan["steps"]:
            assert step["problems"] >= 1
            assert 0.0 <= step["predicted_solve_rate"] <= 1.0
            assert step["value_per_hour"] >= 0.0
    finally:
        _cleanup(uid)


def test_pathway_limit_and_step_shape():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            from app.models.user import User

            user = db.get(User, uid)
            plan = pathway.build_pathway(db, user, limit=2)

        assert len(plan["steps"]) <= 2
        step = plan["steps"][0]
        assert {
            "order", "pattern_key", "pattern_name", "problems",
            "predicted_solve_rate", "expected_solves", "expected_hours",
            "value_per_hour", "confidence", "unlocks",
        } <= set(step)
        assert [s["order"] for s in plan["steps"]] == list(
            range(1, len(plan["steps"]) + 1)
        )
    finally:
        _cleanup(uid)


def test_evidence_unlocks_a_dependent_pattern_in_the_plan():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    slugs = []
    try:
        with SessionLocal() as db:
            slugs = _solvable_slugs(db, "arrays-hashing", limit=3)
            pids = [db.query(Problem).filter(Problem.slug == s).one().id for s in slugs]

        for i, pid in enumerate(pids):
            with SessionLocal() as db:
                db.add(
                    Submission(
                        user_id=uid,
                        problem_id=pid,
                        code="x",
                        language="python",
                        status=SubmissionStatus.ACCEPTED,
                        submitted_at=NOW - timedelta(days=10 - i),
                    )
                )
                db.commit()

        with SessionLocal() as db:
            skill_model.replay(db)
            from app.models.user import User

            user = db.get(User, uid)
            progress = get_user_progress(db, user)
            plan = pathway.build_pathway(db, user)

        ah = progress["arrays-hashing"]
        assert ah.skill_n == len(slugs)
        assert ah.solve_rate >= skill_model.UNLOCK_SOLVE_RATE

        # arrays-hashing is a prerequisite of these; the plan must be able to
        # schedule at least one of them because evidence opened the gate.
        dependents = {
            p["key"] for p in PATTERNS if "arrays-hashing" in p["prerequisites"]
        }
        scheduled = {s["pattern_key"] for s in plan["steps"]}
        assert dependents & scheduled, "evidence did not open a dependent pattern"
    finally:
        _cleanup(uid, slugs)


def test_roadmap_payload_includes_pathway():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        body = client.get("/api/v1/roadmap", headers=headers).json()
        assert "pathway" in body
        assert body["pathway"]["objective"] == pathway.OBJECTIVE
        assert isinstance(body["pathway"]["steps"], list)
    finally:
        _cleanup(uid)


def test_pathway_endpoint():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        res = client.get("/api/v1/roadmap/pathway?limit=3", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["objective"] == pathway.OBJECTIVE
        assert len(body["steps"]) <= 3
        first = body["steps"][0]
        assert first["problems"] >= 1
        assert first["expected_hours"] > 0
    finally:
        _cleanup(uid)
