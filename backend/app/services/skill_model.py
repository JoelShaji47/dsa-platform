"""Layer 1 student model: an Elo/IRT estimate of what a learner can solve.

The model is deliberately small and auditable. Two quantities:

``theta``  ability logit for one (user, pattern), persisted in
           ``skill_estimates`` together with the observation count ``n``.
``b``      difficulty logit for one problem, persisted on the problem row
           (``problems.difficulty_b`` / ``difficulty_n``) because it is global.

    P(solve) = sigmoid(theta - b)

Both are updated online, one graded submission at a time::

    k_user    = max(MIN_K_USER, K_USER / sqrt(1 + n))
    theta    += k_user * (y - p)
    k_problem = max(MIN_K_PROBLEM, K_PROBLEM / sqrt(1 + n_problem))
    b        -= k_problem * (y - p)

``y`` is 1.0 for a clean accepted submission, ``HINT_CREDIT`` when the learner
had already taken a hint on that problem, and 0.0 for a rejected submission.
A hinted solve is neither independence nor failure: it moves the estimate as
if most, not all, of the credit were earned.

Because ``k`` shrinks with ``n``, early observations move the estimate a lot
and later ones refine it — the estimate gets more confident, not noisier, as
evidence accumulates. ``confidence(n) = n / (n + PRIOR_N)`` is the display-side
counterpart of that; it is never inflated for a user with no evidence.

Pattern mastery shown to a learner is the *mean* ``P(solve)`` over the
pattern's **solvable** problems (starter code + test cases). Catalog-only
placeholders are excluded, so an incomplete catalog cannot deflate mastery —
the bug that made the old ``solved / len(pattern["problems"])`` ratio tiny.

Nothing here raises into a request path: ``record_outcome`` is fail-safe like
telemetry, and every modelling failure falls back to the previous estimate.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import Difficulty, SubmissionStatus

# Difficulty-band priors on the logit scale (EASY is easier => lower b).
PRIOR_B: dict[str, float] = {
    Difficulty.EASY.value: -1.0,
    Difficulty.MEDIUM.value: 0.0,
    Difficulty.HARD.value: 1.0,
}

# Learning rates and their floors (K decays like 1/sqrt(n)).
K_USER = 0.6
MIN_K_USER = 0.08
K_PROBLEM = 0.3
MIN_K_PROBLEM = 0.02

# Credit for a solve that needed a hint, relative to a clean independent solve.
HINT_CREDIT = 0.7

# Pseudo-observation strength for confidence: n=3 => 0.5 confidence.
PRIOR_N = 3.0

# Prediction band where a problem is challenging but not defeating.
TARGET_SOLVE_RATE = 0.65
TARGET_BAND = 0.35

# Evidence needed before a prediction can unlock a pattern on its own.
MIN_UNLOCK_EVIDENCE = 3
UNLOCK_SOLVE_RATE = 0.5


def sigmoid(x: float) -> float:
    """Numerically stable logistic function."""
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def p_solve(theta: float, b: float) -> float:
    """Probability of solving a problem of difficulty ``b`` at ability ``theta``."""
    return sigmoid(theta - b)


def k_factor(n: int, base: float, floor: float) -> float:
    """Decaying learning rate: large early, never below ``floor``."""
    return max(floor, base / math.sqrt(1 + max(0, n)))


def confidence(n: int) -> float:
    """0..1 trust in theta from ``n`` observations (0 with no evidence)."""
    n = max(0, n)
    return n / (n + PRIOR_N)


def prior_b(difficulty: str | Difficulty) -> float:
    value = difficulty.value if isinstance(difficulty, Difficulty) else difficulty
    return PRIOR_B.get(value, 0.0)


def difficulty_of(problem) -> float:
    """Learned difficulty when available, else the difficulty-band prior."""
    b = getattr(problem, "difficulty_b", None)
    if b is not None:
        return float(b)
    return prior_b(problem.difficulty)


def solve_credit(solved: bool, hinted: bool) -> float:
    """Graded outcome ``y`` for one submission."""
    if not solved:
        return 0.0
    return HINT_CREDIT if hinted else 1.0


def apply_observation(
    theta: float,
    n: int,
    b: float,
    n_problem: int,
    y: float,
) -> tuple[float, float]:
    """One online Elo/IRT step. Returns (new_theta, new_b).

    Pure and deterministic so the nightly replay can reproduce online state
    exactly from the event log.
    """
    p = p_solve(theta, b)
    error = y - p
    new_theta = theta + k_factor(n, K_USER, MIN_K_USER) * error
    new_b = b - k_factor(n_problem, K_PROBLEM, MIN_K_PROBLEM) * error
    return new_theta, new_b


# --------------------------------------------------------------------------
# Reading state
# --------------------------------------------------------------------------


def load_user_skill(db: Session, user_id: UUID) -> dict[str, tuple[float, int]]:
    """``{pattern_key: (theta, n)}`` for one user (one query)."""
    from app.models.skill_estimate import SkillEstimate

    rows = (
        db.query(SkillEstimate.pattern_key, SkillEstimate.theta, SkillEstimate.n)
        .filter(SkillEstimate.user_id == user_id)
        .all()
    )
    return {key: (float(theta), int(n)) for key, theta, n in rows}


def solvable_difficulties(problems) -> dict[str, list[float]]:
    """Per-pattern list of difficulty logits for *solvable* problems only.

    ``problems`` is any iterable of Problem rows. Catalog placeholders (no
    starter code or no test cases) cannot be solved and must not enter the
    mastery average.
    """
    out: dict[str, list[float]] = defaultdict(list)
    for p in problems:
        if not p.pattern_key:
            continue
        if not (p.starter_code and p.test_cases):
            continue
        out[p.pattern_key].append(difficulty_of(p))
    return dict(out)


def pattern_prediction(theta: float, n: int, difficulties: list[float]) -> dict:
    """Predicted solve rate and confidence for one pattern.

    ``rate`` is the mean P(solve) over solvable problems, or 0.0 when the
    pattern has none (an empty pattern has no learnable mastery).
    """
    rate = (
        sum(p_solve(theta, b) for b in difficulties) / len(difficulties)
        if difficulties
        else 0.0
    )
    return {
        "theta": round(theta, 4),
        "n": int(n),
        "solve_rate": round(rate, 4),
        "confidence": round(confidence(n), 4),
        "solvable_total": len(difficulties),
    }


def problem_solve_rate(theta: float, problem) -> float:
    """Per-problem P(solve) for the recommendation zone filter."""
    return p_solve(theta, difficulty_of(problem))


def zone_fit(rate: float) -> float:
    """1.0 at TARGET_SOLVE_RATE, 0.0 at the edge of the band or beyond."""
    return max(0.0, 1.0 - abs(rate - TARGET_SOLVE_RATE) / TARGET_BAND)


# --------------------------------------------------------------------------
# Writing state
# --------------------------------------------------------------------------


def record_outcome(db: Session, user, problem, *, solved: bool, hinted: bool) -> None:
    """Update theta and b for one graded submission. Never raises.

    Callers treat the student model as derived state: a failure here must not
    break a submission that has already been committed.
    """
    pattern_key = getattr(problem, "pattern_key", None)
    if not pattern_key:
        return
    try:
        from app.models.skill_estimate import SkillEstimate

        est = (
            db.query(SkillEstimate)
            .filter(
                SkillEstimate.user_id == user.id,
                SkillEstimate.pattern_key == pattern_key,
            )
            .with_for_update()
            .one_or_none()
        )
        theta, n = (est.theta, est.n) if est is not None else (0.0, 0)
        b = difficulty_of(problem)
        n_problem = int(getattr(problem, "difficulty_n", 0) or 0)
        y = solve_credit(solved, hinted)

        new_theta, new_b = apply_observation(theta, n, b, n_problem, y)

        if est is None:
            db.add(
                SkillEstimate(
                    user_id=user.id,
                    pattern_key=pattern_key,
                    theta=new_theta,
                    n=n + 1,
                )
            )
        else:
            est.theta = new_theta
            est.n = n + 1
            est.updated_at = datetime.now(timezone.utc)
        problem.difficulty_b = new_b
        problem.difficulty_n = n_problem + 1
        db.commit()
    except Exception:  # pragma: no cover - defensive, exercised by tests
        db.rollback()


def replay(db: Session) -> dict:
    """Rebuild all estimates from the submission log, in time order.

    Used by ``scripts/refit_skill_model.py`` and by tests. Timed-test
    submissions are excluded, matching every other learning signal. A
    submission counts as hinted when a hint on that problem was used at or
    before it, so replay is a pure function of the event log.
    """
    from app.models.hint import HintUsage
    from app.models.problem import Problem
    from app.models.skill_estimate import SkillEstimate
    from app.models.submission import Submission

    db.query(SkillEstimate).delete()
    db.query(Problem).update(
        {Problem.difficulty_b: None, Problem.difficulty_n: 0},
        synchronize_session=False,
    )
    db.flush()

    problems = {p.id: p for p in db.query(Problem).all()}

    hint_times: dict[tuple, list[datetime]] = defaultdict(list)
    for user_id, problem_id, used_at in db.query(
        HintUsage.user_id, HintUsage.problem_id, HintUsage.used_at
    ).all():
        hint_times[(user_id, problem_id)].append(_aware(used_at))
    for times in hint_times.values():
        times.sort()

    states: dict[tuple, tuple[float, int]] = {}
    submissions = (
        db.query(Submission)
        .filter(Submission.test_session_id.is_(None))
        .order_by(Submission.submitted_at, Submission.id)
        .all()
    )

    graded = 0
    for s in submissions:
        problem = problems.get(s.problem_id)
        if problem is None or not problem.pattern_key:
            continue
        hinted = _hinted_before(hint_times.get((s.user_id, s.problem_id), []), s.submitted_at)
        key = (s.user_id, problem.pattern_key)
        theta, n = states.get(key, (0.0, 0))
        b = difficulty_of(problem)
        n_problem = int(problem.difficulty_n or 0)
        y = solve_credit(s.status == SubmissionStatus.ACCEPTED, hinted)
        theta, b = apply_observation(theta, n, b, n_problem, y)
        states[key] = (theta, n + 1)
        problem.difficulty_b = b
        problem.difficulty_n = n_problem + 1
        graded += 1

    for (user_id, pattern_key), (theta, n) in states.items():
        db.add(
            SkillEstimate(
                user_id=user_id,
                pattern_key=pattern_key,
                theta=theta,
                n=n,
                updated_at=datetime.now(timezone.utc),
            )
        )
    db.commit()
    return {
        "graded_submissions": graded,
        "skill_estimates": len(states),
        "problems_with_difficulty": sum(
            1 for p in problems.values() if p.difficulty_n
        ),
    }


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _hinted_before(times: list[datetime], when: datetime) -> bool:
    """True when a hint was used at or before ``when`` (times pre-sorted)."""
    if not times:
        return False
    return bisect_right(times, _aware(when)) > 0
