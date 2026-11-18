"""Layer 2: a skill-aware study pathway over the pattern DAG.

Ranks *patterns* by expected learning signal per estimated hour, respecting
prerequisites, and emits an ordered plan the roadmap UI (or the custom roadmap
builder) can follow. It builds on the Layer 1 student model in
``app.services.skill_model`` — no separate state, no second source of truth.

Objective: **information per hour**.

    p_i            = sigmoid(theta_pattern - b_problem)   # Layer 1
    information    = sum 4 * p_i * (1 - p_i)              # 1.0 at p=0.5
    hours          = sum EST_HOURS[difficulty]
    value_per_hour = information / hours

Why not "expected theta gain": under a calibrated model ``E[y - p] = 0``, so
practising at the current estimate does not move theta *in expectation*. What
completing a pattern actually buys is **evidence** — ``n`` and therefore
confidence — and prerequisite satisfaction. The simulation below advances
evidence, not theta, and says so. A pattern of only-trivial problems scores
low because p(1-p) is small there; so does a pattern of impossible ones.

``EST_HOURS`` mirrors ``custom_roadmaps.EST_MINS``: it is a documented prior,
not measured dwell time. Real session durations (``solve_sessions``) should
replace it once there is enough data; until then the plan is an ordering, not
a promise about wall-clock time.
"""

from __future__ import annotations

from statistics import mean
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.submission import Submission
from app.services import skill_model
from app.services.roadmap import (
    PATTERNS,
    PATTERN_BY_KEY,
    PatternProgress,
    _prerequisite_ready,
    _unlocked_patterns,
)

# Documented prior, mirrors custom_roadmaps.EST_MINS / 60.
EST_HOURS: dict[str, float] = {"EASY": 0.5, "MEDIUM": 1.0, "HARD": 1.5}

OBJECTIVE = "information_per_hour"


def _hours(problem) -> float:
    return EST_HOURS.get(problem.difficulty.value, 1.0)


def _solved_slugs(db: Session, user_id: UUID) -> set[str]:
    rows = (
        db.query(Submission.problem_id)
        .filter(
            Submission.user_id == user_id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
        )
        .distinct()
        .all()
    )
    return {pid for (pid,) in rows}


def build_pathway(
    db: Session,
    user,
    *,
    problems: dict | None = None,
    progress: dict[str, PatternProgress] | None = None,
    solved_by_problem: dict[str, bool] | None = None,
    limit: int | None = None,
) -> dict:
    """Return an ordered pattern pathway for one learner.

    Deterministic: ties break on (value_per_hour, pattern order, pattern key),
    so the same learner state always yields the same plan.

    ``problems`` / ``progress`` / ``solved_by_problem`` may be passed in when
    the caller already loaded them (the roadmap endpoint does), avoiding a
    second round trip per request.
    """
    if problems is None:
        from app.models.problem import Problem

        problems = {
            p.slug: p
            for p in db.query(Problem).filter(Problem.is_published.is_(True)).all()
        }
    if progress is None:
        from app.services.roadmap import get_user_progress

        progress = get_user_progress(db, user)
    if solved_by_problem is None:
        solved_ids = _solved_slugs(db, user.id)
        solved_by_problem = {p.slug: (p.id in solved_ids) for p in problems.values()}

    # Unsolved, solvable problems per pattern — the only work a plan can plan.
    remaining: dict[str, list] = {p["key"]: [] for p in PATTERNS}
    for slug, problem in problems.items():
        key = problem.pattern_key
        if not key or key not in remaining:
            continue
        if solved_by_problem.get(slug, False):
            continue
        if not (problem.starter_code and problem.test_cases):
            continue
        remaining[key].append(problem)

    # Simulated evidence per pattern. Completing a pattern adds its problems to
    # n (more confidence, same theta) and satisfies its dependents.
    evidence: dict[str, int] = {k: progress[k].skill_n for k in remaining}
    theta: dict[str, float] = {k: progress[k].skill_theta for k in remaining}
    unlocked = _unlocked_patterns(progress)
    completed: set[str] = set()

    steps: list[dict] = []
    while True:
        candidates = [
            key for key in remaining
            if key in unlocked and key not in completed and remaining[key]
        ]
        if not candidates:
            break

        scored = []
        for key in candidates:
            ps = [
                skill_model.p_solve(theta[key], skill_model.difficulty_of(p))
                for p in remaining[key]
            ]
            information = sum(4.0 * p * (1.0 - p) for p in ps)
            hours = sum(_hours(p) for p in remaining[key]) or 0.5
            scored.append(
                {
                    "key": key,
                    "rate": mean(ps),
                    "information": information,
                    "hours": hours,
                    "value": information / hours,
                    "count": len(ps),
                }
            )
        scored.sort(
            key=lambda s: (
                -round(s["value"], 6),
                PATTERN_BY_KEY.get(s["key"], {}).get("order", 99),
                s["key"],
            )
        )
        best = scored[0]
        key = best["key"]

        before = set(unlocked)
        completed.add(key)
        evidence[key] += best["count"]

        # Evidence, not theta, is what the simulation advances. Re-run the
        # prerequisite gate with the simulated completion so the next step can
        # be a pattern that practice just opened.
        def _ready(pk: str) -> bool:
            return pk in completed or _prerequisite_ready(progress[pk])

        changed = True
        while changed:
            changed = False
            for pattern in PATTERNS:
                if pattern["key"] in unlocked:
                    continue
                if all(_ready(pk) for pk in pattern["prerequisites"]):
                    unlocked.add(pattern["key"])
                    changed = True

        steps.append(
            {
                "order": len(steps) + 1,
                "pattern_key": key,
                "pattern_name": PATTERN_BY_KEY.get(key, {}).get("name", key),
                "problems": best["count"],
                "predicted_solve_rate": round(best["rate"], 4),
                "expected_solves": round(best["rate"] * best["count"], 2),
                "expected_hours": round(best["hours"], 2),
                "value_per_hour": round(best["value"], 4),
                "confidence": round(skill_model.confidence(evidence[key]), 4),
                "unlocks": sorted(unlocked - before),
            }
        )
        if limit is not None and len(steps) >= limit:
            break

    return {
        "objective": OBJECTIVE,
        "steps": steps,
        "total_hours": round(sum(s["expected_hours"] for s in steps), 2),
        "hour_basis": "difficulty prior (EST_HOURS), not measured dwell time",
        "remaining_patterns": sorted(set(remaining) - completed),
    }
