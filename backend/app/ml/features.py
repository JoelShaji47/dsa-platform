"""Feature engineering for the learning-to-rank recommender.

One training row per (user, problem) pair with at least one submission:

relevance label (target)
    2 = engaged solve: ACCEPTED with hints_used <= 1 and attempts <= 3
    1 = solve with more friction (many hints / attempts)
    0 = attempted but never accepted

Features fall back to neutral priors when history is missing so inference can
score cold (user, problem) pairs the heuristic surfaces.
"""

from collections import defaultdict

import pandas as pd
from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.interaction import InteractionEvent
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.services.activity import REVIEW, RUN
from app.services.roadmap import PATTERN_BY_KEY

FEATURE_COLUMNS = [
    # user side
    "u_solved_total",
    "u_xp",
    "u_streak",
    "u_mastery_pattern",
    "u_solved_in_pattern",
    "u_attempts_in_pattern",
    "u_hints_in_pattern",
    "u_solved_at_difficulty",
    # interaction side
    "i_attempts",
    "i_hints",
    "i_runs",
    "i_ever_solved",
    "i_reject_ratio",
    "i_time_to_accept_min",
    "i_revisits",
    "i_reviews",
    # problem side
    "p_diff_ord",
    "p_pattern_order",
    "p_solvable",
    "p_accept_rate",
    "p_popularity",
]

LABEL_COLUMN = "relevance"
GROUP_COLUMN = "user_id"
CUTOFF_COLUMN = "cutoff_at"

DIFF_ORD = {"EASY": 0, "MEDIUM": 1, "HARD": 2}


def _pattern_mastery(solved: int, total: int, hints: int) -> float:
    if solved <= 0 or total <= 0:
        return 0.0
    resolved = min(solved / total, 1.0)
    penalty = min(hints / (solved + hints), 0.35)
    return round(resolved * 100 * (1 - penalty), 1)


def build_training_frame(db: Session) -> pd.DataFrame:
    problems: dict = {p.id: p for p in db.query(Problem).all()}
    if not problems:
        return pd.DataFrame(columns=FEATURE_COLUMNS + [LABEL_COLUMN, GROUP_COLUMN, CUTOFF_COLUMN, "slug"])

    users: dict = {u.id: u for u in db.query(User).all()}

    submissions = (
        db.query(Submission)
        .filter(Submission.test_session_id.is_(None))
        .order_by(Submission.submitted_at)
        .all()
    )
    hint_rows = db.query(HintUsage).all()
    events = db.query(InteractionEvent).all()

    hints_by_pair: dict[tuple, int] = defaultdict(int)
    for h in hint_rows:
        hints_by_pair[(h.user_id, h.problem_id)] += 1

    runs_by_pair: dict[tuple, int] = defaultdict(int)
    reviews_by_pair: dict[tuple, int] = defaultdict(int)
    for e in events:
        if e.event == RUN:
            runs_by_pair[(e.user_id, e.problem_id)] += 1
        elif e.event == REVIEW:
            reviews_by_pair[(e.user_id, e.problem_id)] += 1

    subs_by_pair: dict[tuple, list] = defaultdict(list)
    for s in submissions:
        subs_by_pair[(s.user_id, s.problem_id)].append(s)

    solved_ids_by_user: dict = defaultdict(set)
    attempts_by_pattern: dict[tuple, int] = defaultdict(int)
    hints_by_pattern: dict[tuple, int] = defaultdict(int)
    solved_by_pattern: dict[tuple, int] = defaultdict(int)
    solved_by_diff: dict[tuple, int] = defaultdict(int)
    for (uid, pid), subs in subs_by_pair.items():
        p = problems.get(pid)
        if p is None:
            continue
        pattern = p.pattern_key or ""
        attempts_by_pattern[(uid, pattern)] += len(subs)
        hints_by_pattern[(uid, pattern)] += hints_by_pair.get((uid, pid), 0)
        if any(s.status == SubmissionStatus.ACCEPTED for s in subs):
            solved_ids_by_user[uid].add(pid)
            solved_by_pattern[(uid, pattern)] += 1
            solved_by_diff[(uid, p.difficulty.value)] += 1

    # global problem stats (popularity + acceptance priors)
    sub_count: dict = defaultdict(int)
    accept_count: dict = defaultdict(int)
    for (uid, pid), subs in subs_by_pair.items():
        sub_count[pid] += len(subs)
        if any(s.status == SubmissionStatus.ACCEPTED for s in subs):
            accept_count[pid] += 1
    user_count: dict = defaultdict(set)
    for (uid, pid) in subs_by_pair:
        user_count[pid].add(uid)

    pattern_totals: dict[str, int] = defaultdict(int)
    for p in problems.values():
        if p.pattern_key:
            pattern_totals[p.pattern_key] += 1

    rows = []
    for (uid, pid), subs in subs_by_pair.items():
        problem = problems.get(pid)
        user = users.get(uid)
        if problem is None or user is None:
            continue
        pattern = problem.pattern_key or ""
        accepted = [s for s in subs if s.status == SubmissionStatus.ACCEPTED]
        ever_solved = 1 if accepted else 0
        attempts = len(subs)
        hints = hints_by_pair.get((uid, pid), 0)
        rejects = sum(1 for s in subs if s.status != SubmissionStatus.ACCEPTED)
        first_accept = min((s.submitted_at for s in accepted), default=None)
        if first_accept is not None:
            first_sub = min(s.submitted_at for s in subs)
            minutes = (first_accept - first_sub).total_seconds() / 60.0
            revisits = sum(1 for s in subs if s.submitted_at > first_accept)
        else:
            minutes = -1.0
            revisits = 0

        if ever_solved and hints <= 1 and attempts <= 3:
            relevance = 2
        elif ever_solved:
            relevance = 1
        else:
            relevance = 0

        total_in_pattern = pattern_totals.get(pattern, 0)
        mastery = _pattern_mastery(
            solved_by_pattern.get((uid, pattern), 0),
            total_in_pattern,
            hints_by_pattern.get((uid, pattern), 0),
        )
        order = PATTERN_BY_KEY.get(pattern, {}).get("order", 99) if pattern else 99
        n_users = len(user_count.get(pid, ()))
        accept_rate = (accept_count[pid] / n_users) if n_users else 0.5

        rows.append(
            {
                "user_id": str(uid),
                "slug": problem.slug,
                "u_solved_total": len(solved_ids_by_user.get(uid, ())),
                "u_xp": user.xp or 0,
                "u_streak": user.current_streak or 0,
                "u_mastery_pattern": mastery,
                "u_solved_in_pattern": solved_by_pattern.get((uid, pattern), 0),
                "u_attempts_in_pattern": attempts_by_pattern.get((uid, pattern), 0),
                "u_hints_in_pattern": hints_by_pattern.get((uid, pattern), 0),
                "u_solved_at_difficulty": solved_by_diff.get(
                    (uid, problem.difficulty.value), 0
                ),
                "i_attempts": attempts,
                "i_hints": hints,
                "i_runs": runs_by_pair.get((uid, pid), 0),
                "i_ever_solved": ever_solved,
                "i_reject_ratio": (rejects / attempts) if attempts else 0.0,
                "i_time_to_accept_min": minutes,
                "i_revisits": revisits,
                "i_reviews": reviews_by_pair.get((uid, pid), 0),
                "p_diff_ord": DIFF_ORD.get(problem.difficulty.value, 1),
                "p_pattern_order": order,
                "p_solvable": 1
                if (problem.starter_code and problem.test_cases)
                else 0,
                "p_accept_rate": accept_rate,
                "p_popularity": float(n_users),
                LABEL_COLUMN: relevance,
                CUTOFF_COLUMN: max(s.submitted_at for s in subs),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=FEATURE_COLUMNS + [LABEL_COLUMN, GROUP_COLUMN, CUTOFF_COLUMN, "slug"]
        )
    return pd.DataFrame(rows)
