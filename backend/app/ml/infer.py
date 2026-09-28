"""Serving: score recommendation candidates with the trained ranker.

Cold paths fall back to the heuristic (return {} = "no model opinion"):
- no artifact on disk, or artifact unreadable / feature mismatch,
- the user has fewer than MIN_INTERACTIONS logged submissions (nothing
  personal to rank with yet).

Inference features reuse the same columns as training; unseen (user, problem)
pairs get neutral priors (zeros + problem-side stats).
"""

from functools import lru_cache

import lightgbm as lgb
import pandas as pd
from sqlalchemy.orm import Session

from app.ml.features import DIFF_ORD, FEATURE_COLUMNS
from app.ml.train import META_PATH, MODEL_PATH, load_meta
from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.interaction import InteractionEvent
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.services.activity import REVIEW, RUN
from app.services.roadmap import PATTERN_BY_KEY, get_user_progress

MIN_INTERACTIONS = 3


@lru_cache(maxsize=1)
def _load_booster() -> lgb.Booster | None:
    try:
        if not MODEL_PATH.exists():
            return None
        return lgb.Booster(model_file=str(MODEL_PATH))
    except Exception:
        return None


def model_version() -> str | None:
    meta = load_meta()
    return meta.get("version") if meta else None


def _candidate_frame(
    db: Session, user: User, slugs: list[str]
) -> tuple[pd.DataFrame, list[str]]:
    problems = {p.slug: p for p in db.query(Problem).all()}
    subs = (
        db.query(Submission)
        .filter(Submission.user_id == user.id)
        .all()
    )
    hints = (
        db.query(HintUsage.problem_id)
        .filter(HintUsage.user_id == user.id)
        .all()
    )
    hint_counts: dict = {}
    for (pid,) in hints:
        hint_counts[pid] = hint_counts.get(pid, 0) + 1
    runs: dict = {}
    reviews: dict = {}
    for (pid, event) in (
        db.query(InteractionEvent.problem_id, InteractionEvent.event)
        .filter(InteractionEvent.user_id == user.id)
        .all()
    ):
        if event == RUN:
            runs[pid] = runs.get(pid, 0) + 1
        elif event == REVIEW:
            reviews[pid] = reviews.get(pid, 0) + 1

    subs_by_pid: dict = {}
    for s in subs:
        subs_by_pid.setdefault(s.problem_id, []).append(s)

    diff_of_pid = {p.id: p.difficulty.value for p in problems.values()}
    solved_by_diff: dict = {}
    for pid, group in subs_by_pid.items():
        if any(s.status == SubmissionStatus.ACCEPTED for s in group):
            d = diff_of_pid.get(pid)
            if d:
                solved_by_diff[d] = solved_by_diff.get(d, 0) + 1

    solved_total = sum(
        1
        for group in subs_by_pid.values()
        if any(s.status == SubmissionStatus.ACCEPTED for s in group)
    )

    # pattern context (same mastery formula as the roadmap heuristic)
    progress = get_user_progress(db, user)
    mastery_by_pattern = {k: v.mastery for k, v in progress.items()}
    solved_in_pattern = {k: v.solved for k, v in progress.items()}
    attempts_in_pattern = {k: v.attempts for k, v in progress.items()}
    hints_in_pattern = {k: v.hints_used for k, v in progress.items()}

    # global problem priors
    pop: dict = {}
    acc: dict = {}
    all_subs = db.query(Submission).all()
    by_pid: dict = {}
    for s in all_subs:
        by_pid.setdefault(s.problem_id, []).append(s)
    for pid, group in by_pid.items():
        users = {s.user_id for s in group}
        pop[pid] = float(len(users))
        acc[pid] = sum(
            1
            for uid in users
            if any(
                x.status == SubmissionStatus.ACCEPTED
                for x in by_pid[pid]
                if x.user_id == uid
            )
        ) / len(users)

    rows = []
    ordered_slugs = []
    for slug in slugs:
        problem = problems.get(slug)
        if problem is None:
            continue
        pattern = problem.pattern_key or ""
        group = subs_by_pid.get(problem.id, [])
        attempts = len(group)
        ever = (
            1
            if any(s.status == SubmissionStatus.ACCEPTED for s in group)
            else 0
        )
        rejects = sum(1 for s in group if s.status != SubmissionStatus.ACCEPTED)
        accepted = [s for s in group if s.status == SubmissionStatus.ACCEPTED]
        if accepted:
            first_accept = min(s.submitted_at for s in accepted)
            first_sub = min(s.submitted_at for s in group)
            minutes = (first_accept - first_sub).total_seconds() / 60.0
            revisits = sum(1 for s in group if s.submitted_at > first_accept)
        else:
            minutes = -1.0
            revisits = 0
        order = PATTERN_BY_KEY.get(pattern, {}).get("order", 99) if pattern else 99
        rows.append(
            {
                "u_solved_total": solved_total,
                "u_xp": user.xp or 0,
                "u_streak": user.current_streak or 0,
                "u_mastery_pattern": mastery_by_pattern.get(pattern, 0.0),
                "u_solved_in_pattern": solved_in_pattern.get(pattern, 0),
                "u_attempts_in_pattern": attempts_in_pattern.get(pattern, 0),
                "u_hints_in_pattern": hints_in_pattern.get(pattern, 0),
                "u_solved_at_difficulty": solved_by_diff.get(
                    problem.difficulty.value, 0
                ),
                "i_attempts": attempts,
                "i_hints": hint_counts.get(problem.id, 0),
                "i_runs": runs.get(problem.id, 0),
                "i_ever_solved": ever,
                "i_reject_ratio": (rejects / attempts) if attempts else 0.0,
                "i_time_to_accept_min": minutes,
                "i_revisits": revisits,
                "i_reviews": reviews.get(problem.id, 0),
                "p_diff_ord": DIFF_ORD.get(problem.difficulty.value, 1),
                "p_pattern_order": order,
                "p_solvable": 1
                if (problem.starter_code and problem.test_cases)
                else 0,
                "p_accept_rate": acc.get(problem.id, 0.5),
                "p_popularity": pop.get(problem.id, 0.0),
            }
        )
        ordered_slugs.append(slug)

    if not rows:
        return pd.DataFrame(columns=FEATURE_COLUMNS), []
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS), ordered_slugs


def score_candidates(
    db: Session, user: User, slugs: list[str]
) -> dict[str, float]:
    """Return {slug: model_score}; empty dict when the model abstains."""
    booster = _load_booster()
    if booster is None or not slugs:
        return {}
    n_subs = (
        db.query(Submission.id).filter(Submission.user_id == user.id).count()
    )
    if n_subs < MIN_INTERACTIONS:
        return {}
    meta = load_meta()
    if meta and meta.get("features") != FEATURE_COLUMNS:
        return {}
    frame, ordered = _candidate_frame(db, user, slugs)
    if frame.empty:
        return {}
    try:
        scores = booster.predict(frame.to_numpy(dtype=float))
    except Exception:
        return {}
    return {slug: float(score) for slug, score in zip(ordered, scores)}


def clear_cache() -> None:
    _load_booster.cache_clear()
