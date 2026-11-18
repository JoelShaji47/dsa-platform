"""Layer 1 student model: pure update rule, persistence and replay."""

import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.db.session import SessionLocal
from app.models.enums import Difficulty, SubmissionStatus
from app.models.hint import HintUsage
from app.models.problem import Problem
from app.models.skill_estimate import SkillEstimate
from app.models.submission import Submission
from app.services import skill_model
from tests.conftest import make_test_user

NOW = datetime.now(timezone.utc)


# --------------------------------------------------------------------------
# Pure model
# --------------------------------------------------------------------------


def test_p_solve_is_monotone_and_centred():
    assert skill_model.p_solve(0.0, 0.0) == pytest.approx(0.5)
    assert skill_model.p_solve(1.0, 0.0) > skill_model.p_solve(0.0, 0.0)
    assert skill_model.p_solve(0.0, 1.0) < skill_model.p_solve(0.0, 0.0)
    # Same gap in ability => same probability, wherever it sits on the scale.
    assert skill_model.p_solve(2.0, 1.0) == pytest.approx(skill_model.p_solve(1.0, 0.0))
    assert 0.0 < skill_model.p_solve(-50.0, 0.0) < 1e-6


def test_prior_b_orders_difficulty_bands():
    easy = skill_model.prior_b(Difficulty.EASY)
    medium = skill_model.prior_b("MEDIUM")
    hard = skill_model.prior_b(Difficulty.HARD)
    assert easy < medium < hard


def test_solve_raises_theta_and_lowers_difficulty():
    theta, b = skill_model.apply_observation(0.0, 0, 0.0, 0, y=1.0)
    assert theta > 0.0
    assert b < 0.0
    # Failure moves both the other way.
    theta2, b2 = skill_model.apply_observation(0.0, 0, 0.0, 0, y=0.0)
    assert theta2 < 0.0
    assert b2 > 0.0


def test_hinted_solve_earns_partial_credit():
    clean, _ = skill_model.apply_observation(0.0, 0, 0.0, 0, y=1.0)
    hinted, _ = skill_model.apply_observation(0.0, 0, 0.0, 0, y=skill_model.HINT_CREDIT)
    failed, _ = skill_model.apply_observation(0.0, 0, 0.0, 0, y=0.0)
    assert failed < hinted < clean


def test_learning_rate_decays_with_evidence():
    fresh = skill_model.k_factor(0, skill_model.K_USER, skill_model.MIN_K_USER)
    seasoned = skill_model.k_factor(100, skill_model.K_USER, skill_model.MIN_K_USER)
    assert seasoned < fresh
    assert seasoned >= skill_model.MIN_K_USER


def test_confidence_never_inflated():
    assert skill_model.confidence(0) == 0.0
    assert skill_model.confidence(3) == pytest.approx(0.5)
    assert skill_model.confidence(10_000) < 1.0


def test_repeated_success_converges_and_saturates():
    theta, b, n = 0.0, 0.0, 0
    for n in range(40):
        theta, b = skill_model.apply_observation(theta, n, b, n, y=1.0)
        assert -1.0 < theta < 10.0
    assert skill_model.p_solve(theta, b) > 0.9
    # Gains shrink: the last step is smaller than the first.
    first = skill_model.apply_observation(0.0, 0, 0.0, 0, y=1.0)[0]
    last = skill_model.apply_observation(theta, 39, b, 39, y=1.0)[0] - theta
    assert last < first


def test_pattern_prediction_ignores_catalog_placeholders():
    def problem(pattern_key, difficulty, solvable):
        return SimpleNamespace(
            pattern_key=pattern_key,
            difficulty=difficulty,
            difficulty_b=None,
            starter_code={"python": "x"} if solvable else {},
            test_cases=[{"input": "1"}] if solvable else [],
        )

    problems = [
        problem("graphs", Difficulty.EASY, True),
        problem("graphs", Difficulty.MEDIUM, True),
        # Ten unsolvable catalog entries must not change the average.
        *[problem("graphs", Difficulty.HARD, False) for _ in range(10)],
    ]
    by_pattern = skill_model.solvable_difficulties(problems)
    assert len(by_pattern["graphs"]) == 2

    prediction = skill_model.pattern_prediction(0.0, 5, by_pattern["graphs"])
    expected = (skill_model.p_solve(0.0, -1.0) + skill_model.p_solve(0.0, 0.0)) / 2
    assert prediction["solve_rate"] == pytest.approx(expected, abs=1e-4)
    assert prediction["solvable_total"] == 2
    # An empty pattern cannot claim mastery.
    assert skill_model.pattern_prediction(3.0, 9, [])["solve_rate"] == 0.0


def test_zone_fit_peaks_at_target():
    target = skill_model.TARGET_SOLVE_RATE
    assert skill_model.zone_fit(target) == pytest.approx(1.0)
    assert skill_model.zone_fit(0.65) > skill_model.zone_fit(0.2)
    assert skill_model.zone_fit(-1.0) == 0.0


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------


def _problem(slug="two-sum"):
    with SessionLocal() as db:
        return db.query(Problem).filter(Problem.slug == slug).one()


def _cleanup(user_id):
    with SessionLocal() as db:
        db.query(SkillEstimate).filter(SkillEstimate.user_id == user_id).delete()
        db.query(Submission).filter(Submission.user_id == user_id).delete()
        db.query(HintUsage).filter(HintUsage.user_id == user_id).delete()
        db.commit()


def test_record_outcome_persists_theta_and_difficulty():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            from app.models.user import User

            problem = db.query(Problem).filter(Problem.slug == "two-sum").one()
            user = db.get(User, uid)
            before_b = problem.difficulty_b
            before_n = problem.difficulty_n

            skill_model.record_outcome(db, user, problem, solved=True, hinted=False)
            assert problem.difficulty_n == before_n + 1
            assert problem.difficulty_b is not None

            est = (
                db.query(SkillEstimate)
                .filter(SkillEstimate.user_id == uid)
                .one()
            )
            first_theta = est.theta
            assert est.n == 1
            assert est.pattern_key == "arrays-hashing"
            assert first_theta > 0.0

            skill_model.record_outcome(db, user, problem, solved=True, hinted=False)
            est = db.query(SkillEstimate).filter(SkillEstimate.user_id == uid).one()
            assert est.n == 2
            assert est.theta > first_theta  # still climbing, but by less
            assert problem.difficulty_n == before_n + 2
    finally:
        with SessionLocal() as db:
            db.query(Problem).filter(Problem.slug == "two-sum").update(
                {Problem.difficulty_b: before_b, Problem.difficulty_n: before_n}
            )
            db.commit()
        _cleanup(uid)


def test_record_outcome_is_a_noop_without_a_pattern():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            from app.models.user import User

            user = db.get(User, uid)
            stubbed = SimpleNamespace(pattern_key=None, difficulty=Difficulty.EASY)
            skill_model.record_outcome(db, user, stubbed, solved=True, hinted=False)
            assert db.query(SkillEstimate).filter(SkillEstimate.user_id == uid).count() == 0
    finally:
        _cleanup(uid)


# --------------------------------------------------------------------------
# Replay
# --------------------------------------------------------------------------


def _add_submission(user_id, problem_id, status, when):
    with SessionLocal() as db:
        db.add(
            Submission(
                user_id=user_id,
                problem_id=problem_id,
                code="x",
                language="python",
                status=status,
                submitted_at=when,
            )
        )
        db.commit()


def test_replay_reproduces_online_state_and_is_idempotent():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            problem = db.query(Problem).filter(Problem.slug == "two-sum").one()
            pid = problem.id

        # Two clean solves -> a positive ability estimate.
        _add_submission(uid, pid, SubmissionStatus.ACCEPTED, NOW - timedelta(days=2))
        _add_submission(uid, pid, SubmissionStatus.ACCEPTED, NOW - timedelta(days=1))

        with SessionLocal() as db:
            first = skill_model.replay(db)
        with SessionLocal() as db:
            est = db.query(SkillEstimate).filter(SkillEstimate.user_id == uid).one()
            theta, n = est.theta, est.n
            second = skill_model.replay(db)
            again = db.query(SkillEstimate).filter(SkillEstimate.user_id == uid).one()

        assert first["graded_submissions"] >= 2
        assert n == 2
        assert theta > 0.0
        # Idempotent: replay is a pure function of the event log.
        assert again.theta == pytest.approx(theta)
        assert again.n == n
        assert second["skill_estimates"] == first["skill_estimates"]
    finally:
        with SessionLocal() as db:
            db.query(Problem).filter(Problem.slug == "two-sum").update(
                {Problem.difficulty_b: None, Problem.difficulty_n: 0}
            )
            db.commit()
        _cleanup(uid)


def test_replay_orders_events_and_respects_difficulty():
    """An EASY failure costs more than a later EASY solve earns (it is a bigger
    surprise), so the estimate must not simply count solves."""
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            pid = db.query(Problem).filter(Problem.slug == "two-sum").one().id

        _add_submission(uid, pid, SubmissionStatus.WRONG_ANSWER, NOW - timedelta(days=2))
        _add_submission(uid, pid, SubmissionStatus.ACCEPTED, NOW - timedelta(days=1))

        with SessionLocal() as db:
            skill_model.replay(db)
            est = db.query(SkillEstimate).filter(SkillEstimate.user_id == uid).one()

        easy_b = skill_model.prior_b(Difficulty.EASY)
        fail_theta, fail_b = skill_model.apply_observation(0.0, 0, easy_b, 0, y=0.0)
        solve_theta, _ = skill_model.apply_observation(
            fail_theta, 1, fail_b, 1, y=1.0
        )
        assert est.theta == pytest.approx(solve_theta)
        assert est.theta < 0.0
    finally:
        with SessionLocal() as db:
            db.query(Problem).filter(Problem.slug == "two-sum").update(
                {Problem.difficulty_b: None, Problem.difficulty_n: 0}
            )
            db.commit()
        _cleanup(uid)


def test_replay_treats_hinted_solve_as_partial_credit():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        with SessionLocal() as db:
            problem = db.query(Problem).filter(Problem.slug == "valid-anagram").one()
            pid = problem.id
            difficulty = problem.difficulty
            db.add(
                HintUsage(
                    user_id=uid,
                    problem_id=pid,
                    level=1,
                    used_at=NOW - timedelta(days=3),
                )
            )
            db.commit()

        _add_submission(uid, pid, SubmissionStatus.ACCEPTED, NOW - timedelta(days=2))

        with SessionLocal() as db:
            skill_model.replay(db)
            hinted_theta = (
                db.query(SkillEstimate).filter(SkillEstimate.user_id == uid).one().theta
            )
            # Same setup, three credit levels: a hinted solve must land between
            # a failure and a clean solve for the very same problem.
            b = skill_model.prior_b(difficulty)
            clean_theta, _ = skill_model.apply_observation(0.0, 0, b, 0, y=1.0)
            fail_theta, _ = skill_model.apply_observation(0.0, 0, b, 0, y=0.0)
        assert fail_theta < hinted_theta < clean_theta
    finally:
        with SessionLocal() as db:
            db.query(Problem).filter(Problem.slug == "valid-anagram").update(
                {Problem.difficulty_b: None, Problem.difficulty_n: 0}
            )
            db.commit()
        _cleanup(uid)


# --------------------------------------------------------------------------
# Roadmap integration
# --------------------------------------------------------------------------


def test_unlock_uses_evidence_not_only_a_solve():
    from app.services.roadmap import (
        PATTERNS,
        PatternProgress,
        _prerequisite_ready,
        _unlocked_patterns,
    )

    cold = PatternProgress(key="arrays-hashing", solved=0, skill_n=0, solve_rate=0.0)
    assert _prerequisite_ready(cold) is False

    thin = PatternProgress(key="arrays-hashing", solved=0, skill_n=2, solve_rate=0.9)
    assert _prerequisite_ready(thin) is False  # not enough evidence yet

    ready = PatternProgress(key="arrays-hashing", solved=0, skill_n=5, solve_rate=0.62)
    assert _prerequisite_ready(ready) is True

    progress = {p["key"]: PatternProgress(key=p["key"]) for p in PATTERNS}
    progress["arrays-hashing"] = ready  # prerequisite of several patterns
    unlocked = _unlocked_patterns(progress)
    assert "arrays-hashing" in unlocked
    assert any(
        "arrays-hashing" in p["prerequisites"] and p["key"] in unlocked
        for p in PATTERNS
    )


def test_roadmap_exposes_skill_state():
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    try:
        from fastapi.testclient import TestClient
        from app.main import app

        body = TestClient(app).get("/api/v1/roadmap", headers=headers).json()
        pattern = next(p for p in body["patterns"] if p["key"] == "arrays-hashing")
        assert {"theta", "n", "solve_rate", "confidence"} <= set(pattern["skill"])
        assert pattern["skill"]["n"] == 0
        assert pattern["skill"]["confidence"] == 0.0
        assert pattern["solvable_total"] < pattern["total"]  # catalog placeholders exist
        assert pattern["mastery"] == 0.0
    finally:
        _cleanup(uid)
