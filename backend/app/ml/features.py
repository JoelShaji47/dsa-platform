"""Feature engineering for the learning-to-rank recommender.

Two training tasks share one serving feature space:

LEGACY ENGAGEMENT TASK (``build_training_frame``)
    One row per (user, problem) pair with at least one submission.
    Label = eventual engagement quality:
        2 = engaged solve: ACCEPTED with hints_used <= 1 and attempts <= 3
        1 = solve with more friction (many hints / attempts)
        0 = attempted but never accepted
    This is a *post-hoc engagement* signal, NOT ground truth for learning
    effectiveness. Limitations (see A2/A3):
    - ``i_*`` pair-interaction features describe the same outcome window the
      label is derived from, so they are outcome-correlated by construction.
      They are kept because the identical formula runs at serving time for
      candidate pairs with prior history, but they must NOT be read as
      pre-exposure predictors.
    - Context features (``u_*``, ``p_*``) and learner-state features
      (``ls_*``) ARE temporal: computed from events strictly before the
      pair's first touch T (``cutoff_at``), with deterministic tie-breaking.
      ``u_xp`` is reconstructed from the append-only xp ledger (``xp_events``)
      <= T, falling back to 0 when the ledger has no rows (documented prior,
      never present-day xp). ``u_streak`` is reconstructed from accepted
      submissions before T.
    - Unattempted problems are NEVER labelled negative (they may never have
      been seen). Rows exist only for pairs with >= 1 submission.
    - Rows are sorted deterministically by (query_id, cutoff_at, slug) so
      group sizes, labels and candidate ids stay aligned.

IMPRESSION TASK (``build_impression_training_frame``)
    The defensible ranking task. One row per actually-exposed recommendation
    (see ``app.models.telemetry``), grouped by recommendation opportunity
    (``query_id = opportunity_id``). Features are computed as-of the
    impression timestamp; labels come from *delayed* outcomes inside an
    outcome window (default 14 days): independent accept = 2, assisted
    accept = 1, no accept = 0 with ``censored`` flag when the window has not
    elapsed. Missing outcomes are unknown/censored, never auto-negative.

SERVING (``candidate_feature_rows``)
    The single shared implementation used by training (as_of=T) and
    inference (as_of=now). Same names, types, ordering, defaults and
    categorical handling. Unseen pairs get neutral priors.
"""

from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.interaction import InteractionEvent
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.models.xp_event import XpEvent
from app.services.activity import REVIEW, RUN

FEATURE_SCHEMA_VERSION = 2

LEGACY_FEATURE_COLUMNS = [
    # user side
    "u_solved_total",
    "u_xp",
    "u_streak",
    "u_mastery_pattern",
    "u_solved_in_pattern",
    "u_attempts_in_pattern",
    "u_hints_in_pattern",
    "u_solved_at_difficulty",
    # interaction side (outcome-window descriptors; see module docstring)
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

LEARNER_STATE_COLUMNS = [
    "ls_mastery",
    "ls_uncertainty",
    "ls_retention_risk",
    "ls_friction",
    "ls_trend",
    "ls_review_priority",
]

FEATURE_COLUMNS = LEGACY_FEATURE_COLUMNS + LEARNER_STATE_COLUMNS

LABEL_COLUMN = "relevance"
GROUP_COLUMN = "user_id"
QUERY_COLUMN = "query_id"
CUTOFF_COLUMN = "cutoff_at"

DIFF_ORD = {"EASY": 0, "MEDIUM": 1, "HARD": 2}

# Neutral defaults for unseen (user, problem) pairs; also the NaN/Inf
# fill values in sanitize_frame. i_time_to_accept_min uses -1.0 (no accept)
# and p_accept_rate 0.5 (uninformed prior) — same as the original pipeline.
DEFAULTS: dict[str, float] = {
    "u_solved_total": 0.0, "u_xp": 0.0, "u_streak": 0.0,
    "u_mastery_pattern": 0.0, "u_solved_in_pattern": 0.0,
    "u_attempts_in_pattern": 0.0, "u_hints_in_pattern": 0.0,
    "u_solved_at_difficulty": 0.0,
    "i_attempts": 0.0, "i_hints": 0.0, "i_runs": 0.0, "i_ever_solved": 0.0,
    "i_reject_ratio": 0.0, "i_time_to_accept_min": -1.0,
    "i_revisits": 0.0, "i_reviews": 0.0,
    "p_diff_ord": 1.0, "p_pattern_order": 99.0, "p_solvable": 0.0,
    "p_accept_rate": 0.5, "p_popularity": 0.0,
    "ls_mastery": 0.0, "ls_uncertainty": 1.0, "ls_retention_risk": 0.0,
    "ls_friction": 0.0, "ls_trend": 0.0, "ls_review_priority": 0.0,
}

OUTCOME_WINDOW_DAYS = 14


def _aware(dt: datetime) -> datetime:
    if dt is None:
        return None  # type: ignore[return-value]
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _pattern_mastery(solved: int, total: int, hints: int) -> float:
    if solved <= 0 or total <= 0:
        return 0.0
    resolved = min(solved / total, 1.0)
    penalty = min(hints / (solved + hints), 0.35)
    return round(resolved * 100 * (1 - penalty), 1)


def sanitize_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce feature columns to finite floats with neutral defaults.

    Handles missing values, NaN/Inf and invalid (non-numeric) entries so a
    corrupt row can never crash training or serving.
    """
    df = df.copy()
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = DEFAULTS[col]
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].where(pd.notna(df[col]), DEFAULTS[col])
        df[col] = df[col].replace([float("inf"), float("-inf")], DEFAULTS[col])
        df[col] = df[col].astype(float)
    if LABEL_COLUMN in df.columns:
        df[LABEL_COLUMN] = (
            pd.to_numeric(df[LABEL_COLUMN], errors="coerce").fillna(0).astype(int).clip(0, 2)
        )
    return df


def sort_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Deterministic ordering so groups, labels and ids stay aligned.

    Primary key: query/group id, then cutoff timestamp, then slug.
    """
    keys = [c for c in (GROUP_COLUMN, CUTOFF_COLUMN, "slug") if c in df.columns]
    if not keys:
        return df.reset_index(drop=True)
    df = df.copy()
    if CUTOFF_COLUMN in df.columns:
        df[CUTOFF_COLUMN] = pd.to_datetime(df[CUTOFF_COLUMN], utc=True, errors="coerce")
    return df.sort_values(keys, kind="mergesort").reset_index(drop=True)


def _snapshot_context(
    submissions: list,
    hint_rows: list,
    events: list,
    problems: dict,
    users: dict,
    xp_rows: list,
    cutoff_of_pair: dict[tuple, datetime],
) -> dict:
    """Precompute temporally-cutoff aggregates.

    For a pair with first touch T, every context aggregate considers only
    events with timestamp <= T (ties broken by id order upstream — all input
    lists MUST be pre-sorted by (timestamp, id)).
    """
    # Per-pair first-touch already in cutoff_of_pair.
    # Sort submissions into before/after buckets lazily per pair via prefix
    # pointers would be O(n^2); instead build per-user time-ordered lists once
    # and binary-search the cutoff. n is small (single DB), linear scan per
    # pair is acceptable and far more auditable.
    subs_by_user: dict = defaultdict(list)
    for s in submissions:
        subs_by_user[s.user_id].append(s)
    hints_by_user: dict = defaultdict(list)
    for h in hint_rows:
        hints_by_user[h.user_id].append(h)
    runs_by_user: dict = defaultdict(list)
    reviews_by_user: dict = defaultdict(list)
    for e in events:
        if e.event == RUN:
            runs_by_user[(e.user_id, e.problem_id)].append(e)
        elif e.event == REVIEW:
            reviews_by_user[(e.user_id, e.problem_id)].append(e)
    xp_by_user: dict = defaultdict(list)
    for x in xp_rows:
        xp_by_user[x.user_id].append(x)

    pattern_totals: dict[str, int] = defaultdict(int)
    for p in problems.values():
        if p.pattern_key:
            pattern_totals[p.pattern_key] += 1

    return {
        "subs_by_user": subs_by_user,
        "hints_by_user": hints_by_user,
        "runs_by_user": runs_by_user,
        "reviews_by_user": reviews_by_user,
        "xp_by_user": xp_by_user,
        "pattern_totals": pattern_totals,
    }


def _streak_before(accepted_dates: list, cutoff) -> int:
    """Consecutive-day streak ending the day before cutoff (reconstructed)."""
    from datetime import timedelta

    days = sorted({_aware(s).date() for s in accepted_dates if _aware(s) <= cutoff})
    if not days:
        return 0
    # Streak ending at the latest active day <= cutoff.
    streak = 1
    for i in range(len(days) - 1, 0, -1):
        if days[i] - days[i - 1] == timedelta(days=1):
            streak += 1
        else:
            break
    return streak


def build_training_frame(db: Session) -> pd.DataFrame:
    """Legacy engagement frame with temporal context features (schema v2).

    See module docstring for task definition and leakage notes.
    """
    from app.services.roadmap import PATTERN_BY_KEY

    problems: dict = {p.id: p for p in db.query(Problem).all()}
    if not problems:
        return pd.DataFrame(
            columns=FEATURE_COLUMNS + [LABEL_COLUMN, GROUP_COLUMN, QUERY_COLUMN, CUTOFF_COLUMN, "slug"]
        )
    users: dict = {u.id: u for u in db.query(User).all()}

    submissions = (
        db.query(Submission)
        .filter(Submission.test_session_id.is_(None))
        .order_by(Submission.submitted_at, Submission.id)
        .all()
    )
    hint_rows = db.query(HintUsage).order_by(HintUsage.used_at, HintUsage.id).all()
    events = db.query(InteractionEvent).order_by(
        InteractionEvent.created_at, InteractionEvent.id
    ).all()
    xp_rows = db.query(XpEvent).order_by(XpEvent.created_at, XpEvent.id).all()

    subs_by_pair: dict[tuple, list] = defaultdict(list)
    for s in submissions:
        subs_by_pair[(s.user_id, s.problem_id)].append(s)
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

    # First-touch cutoff per pair (deterministic: earliest timestamp, id
    # order breaks ties because submissions are pre-sorted).
    cutoff_of_pair: dict[tuple, datetime] = {
        pair: _aware(min(s.submitted_at for s in subs)) for pair, subs in subs_by_pair.items()
    }

    ctx = _snapshot_context(submissions, hint_rows, events, problems, users, xp_rows, cutoff_of_pair)
    pattern_totals = ctx["pattern_totals"]
    pattern_of_pid = {pid: (p.pattern_key or "") for pid, p in problems.items()}

    # Lazy learner-state import (services.learner_state imports roadmap).
    from app.services import learner_state as _ls

    rows = []
    for (uid, pid), subs in subs_by_pair.items():
        problem = problems.get(pid)
        user = users.get(uid)
        if problem is None or user is None:
            continue
        cutoff = cutoff_of_pair[(uid, pid)]
        pattern = problem.pattern_key or ""

        # ---- temporal context: only events with ts <= cutoff ----
        solved_before: set = set()
        att_pat = hints_pat = solved_pat = 0
        solved_diff = 0
        for s in ctx["subs_by_user"].get(uid, []):
            if _aware(s.submitted_at) > cutoff:
                break  # lists are time-ordered
            if (s.user_id, s.problem_id) == (uid, pid):
                continue  # exclude target pair's own history from context
            pp = pattern_of_pid.get(s.problem_id, "")
            att_pat += 1 if pp == pattern else 0
            hints_pat += 0  # hint timestamps joined below
            if s.status == SubmissionStatus.ACCEPTED:
                solved_before.add(s.problem_id)
                if pp == pattern:
                    solved_pat += 1
                p2 = problems.get(s.problem_id)
                if p2 is not None and p2.difficulty.value == problem.difficulty.value:
                    solved_diff += 1
        for h in ctx["hints_by_user"].get(uid, []):
            if _aware(h.used_at) > cutoff:
                break
            if (h.user_id, h.problem_id) == (uid, pid):
                continue
            if pattern_of_pid.get(h.problem_id, "") == pattern:
                hints_pat += 1
        xp_before = sum(
            x.amount for x in ctx["xp_by_user"].get(uid, []) if _aware(x.created_at) <= cutoff
        )
        accepted_dates = [
            s.submitted_at
            for s in ctx["subs_by_user"].get(uid, [])
            if s.status == SubmissionStatus.ACCEPTED and _aware(s.submitted_at) <= cutoff
        ]
        streak_before = _streak_before(accepted_dates, cutoff)

        # ---- problem priors: only other-users' pairs first-touched <= cutoff ----
        pop_users: set = set()
        acc_users = 0
        for (ouid, opid), osubs in subs_by_pair.items():
            if opid != pid or ouid == uid:
                continue
            first = cutoff_of_pair[(ouid, opid)]
            if first <= cutoff:
                pop_users.add(ouid)
                if any(s.status == SubmissionStatus.ACCEPTED for s in osubs):
                    acc_users += 1
        n_users = len(pop_users)
        accept_rate = (acc_users / n_users) if n_users else 0.5

        # ---- outcome window (full history on the pair; outcome-correlated) ----
        accepted = [s for s in subs if s.status == SubmissionStatus.ACCEPTED]
        ever_solved = 1 if accepted else 0
        attempts = len(subs)
        hints = hints_by_pair.get((uid, pid), 0)
        rejects = sum(1 for s in subs if s.status != SubmissionStatus.ACCEPTED)
        first_accept = min((s.submitted_at for s in accepted), default=None)
        if first_accept is not None:
            first_sub = min(s.submitted_at for s in subs)
            minutes = (_aware(first_accept) - _aware(first_sub)).total_seconds() / 60.0
            revisits = sum(1 for s in subs if _aware(s.submitted_at) > _aware(first_accept))
        else:
            minutes = -1.0
            revisits = 0

        if ever_solved and hints <= 1 and attempts <= 3:
            relevance = 2
        elif ever_solved:
            relevance = 1
        else:
            relevance = 0

        mastery = _pattern_mastery(solved_pat, pattern_totals.get(pattern, 0), hints_pat)
        order = PATTERN_BY_KEY.get(pattern, {}).get("order", 99) if pattern else 99

        # ---- learner-state features as-of cutoff ----
        ls_row = _ls_state_row_for_training(db, uid, pattern, cutoff, problems)

        rows.append(
            {
                "user_id": str(uid),
                "query_id": str(uid),  # legacy: one ranking query per user
                "slug": problem.slug,
                "u_solved_total": len(solved_before),
                "u_xp": xp_before,
                "u_streak": streak_before,
                "u_mastery_pattern": mastery,
                "u_solved_in_pattern": solved_pat,
                "u_attempts_in_pattern": att_pat,
                "u_hints_in_pattern": hints_pat,
                "u_solved_at_difficulty": solved_diff,
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
                "p_solvable": 1 if (problem.starter_code and problem.test_cases) else 0,
                "p_accept_rate": accept_rate,
                "p_popularity": float(n_users),
                **ls_row,
                LABEL_COLUMN: relevance,
                CUTOFF_COLUMN: cutoff,
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=FEATURE_COLUMNS + [LABEL_COLUMN, GROUP_COLUMN, QUERY_COLUMN, CUTOFF_COLUMN, "slug"]
        )
    return sanitize_frame(sort_frame(pd.DataFrame(rows)))


def _ls_state_row_for_training(
    db: Session, user_id: UUID, pattern: str, cutoff: datetime, problems: dict
) -> dict[str, float]:
    """Learner-state features for one training row, as-of cutoff."""
    try:
        from app.services import learner_state as _ls

        pattern_of_pid = {pid: (p.pattern_key or "") for pid, p in problems.items()}
        by_pattern = _ls.collect_evidence(db, user_id, pattern_of_pid, as_of=cutoff)
        state = _ls.build_topic_state(pattern, by_pattern.get(pattern, []), now=cutoff)
        return _ls.state_feature_row(state)
    except Exception:
        return {c: DEFAULTS[c] for c in LEARNER_STATE_COLUMNS}


def build_impression_training_frame(
    db: Session,
    outcome_window_days: int = OUTCOME_WINDOW_DAYS,
) -> pd.DataFrame:
    """Leak-free ranking frame from recommendation impressions.

    One row per exposed (opportunity, problem); groups = opportunity_id.
    Features as-of impression time; labels from delayed outcomes within the
    window. Opportunities whose window has not elapsed are marked censored
    (kept with label 0 ONLY when no engagement occurred AND the window
    elapsed; otherwise dropped — missing outcomes are unknown, not negative).
    Returns an empty frame when no usable impressions exist.
    """
    from datetime import timedelta

    from app.models.telemetry import RecommendationImpression
    from app.services.roadmap import PATTERN_BY_KEY

    empty_cols = FEATURE_COLUMNS + [
        LABEL_COLUMN, GROUP_COLUMN, QUERY_COLUMN, CUTOFF_COLUMN, "slug", "censored",
        "clicked", "dismissed",
    ]

    impressions = (
        db.query(RecommendationImpression)
        .order_by(RecommendationImpression.created_at, RecommendationImpression.id)
        .all()
    )
    if not impressions:
        return pd.DataFrame(columns=empty_cols)

    problems: dict = {p.id: p for p in db.query(Problem).all()}
    by_slug: dict = {p.slug: p for p in problems.values()}
    now = datetime.now(timezone.utc)
    window = timedelta(days=outcome_window_days)

    rows = []
    for imp in impressions:
        problem = problems.get(imp.problem_id)
        if problem is None:
            continue
        as_of = _aware(imp.created_at)
        elapsed = (now - as_of) >= window
        # Delayed outcome: submissions on the pair after impression, in-window.
        subs = (
            db.query(Submission)
            .filter(
                Submission.user_id == imp.user_id,
                Submission.problem_id == imp.problem_id,
                Submission.test_session_id.is_(None),
            )
            .order_by(Submission.submitted_at)
            .all()
        )
        in_window = [s for s in subs if as_of < _aware(s.submitted_at) <= as_of + window]
        accepted = [s for s in in_window if s.status == SubmissionStatus.ACCEPTED]
        hints_after = (
            db.query(HintUsage)
            .filter(
                HintUsage.user_id == imp.user_id,
                HintUsage.problem_id == imp.problem_id,
            )
            .all()
        )
        hints_in_window = sum(1 for h in hints_after if as_of < _aware(h.used_at) <= as_of + window)
        clicked = bool(imp.clicked_at)
        dismissed = bool(imp.dismissed_at)

        # Label ladder (highest signal wins). Clicked/dismissed are post-decision
        # signals — valid labels, never features (see FEATURE_COLUMNS).
        if accepted:
            relevance = 2 if (hints_in_window <= 1 and len(in_window) <= 3) else 1
            censored = False
        elif clicked:
            relevance = 1  # engaged with the card but did not solve
            censored = False
        elif dismissed:
            relevance = 0  # explicitly rejected the recommendation
            censored = False
        elif elapsed:
            relevance = 0
            censored = False
        else:
            continue  # window not elapsed and no outcome: unknown, skip

        feat = candidate_feature_rows(
            db, imp.user_id, [problem.slug], as_of=as_of, problems_by_slug=by_slug,
        )
        if not feat:
            continue
        row = feat[0]
        rows.append(
            {
                "user_id": str(imp.user_id),
                "query_id": str(imp.opportunity_id),
                **row,
                LABEL_COLUMN: relevance,
                CUTOFF_COLUMN: as_of,
                "censored": censored,
                "clicked": float(clicked),
                "dismissed": float(dismissed),
            }
        )
    if not rows:
        return pd.DataFrame(columns=empty_cols)
    return sanitize_frame(sort_frame(pd.DataFrame(rows)))


def candidate_feature_rows(
    db: Session,
    user_id: UUID,
    slugs: list[str],
    as_of: datetime | None = None,
    problems_by_slug: dict | None = None,
    global_priors: dict | None = None,
) -> list[dict]:
    """Shared train/serve feature builder (parity-critical).

    ``as_of=None`` means now (serving). Training passes the impression or
    first-touch cutoff. Identical formulas, defaults and column order in
    both paths. Returns one dict per slug (with ``slug`` key), skipping
    unknown slugs.

    ``global_priors`` optionally injects pre-aggregated ``{"pop": ..., "acc":
    ...}`` problem popularity/accept-rate maps (serving fast path). When
    omitted they are computed exactly from submissions <= now.
    """
    from app.services import learner_state as _ls
    from app.services.roadmap import PATTERN_BY_KEY, get_user_progress

    now = _aware(as_of) if as_of is not None else datetime.now(timezone.utc)
    problems = problems_by_slug or {p.slug: p for p in db.query(Problem).all()}
    user = db.get(User, user_id)
    if user is None:
        return []

    # User's own history cut at `now` (serving: full history; training: <= T).
    subs = (
        db.query(Submission)
        .filter(Submission.user_id == user_id, Submission.test_session_id.is_(None))
        .order_by(Submission.submitted_at)
        .all()
    )
    subs = [s for s in subs if _aware(s.submitted_at) <= now]
    hints = (
        db.query(HintUsage)
        .filter(HintUsage.user_id == user_id)
        .all()
    )
    hints = [h for h in hints if _aware(h.used_at) <= now]
    hint_counts: dict = {}
    for h in hints:
        hint_counts[h.problem_id] = hint_counts.get(h.problem_id, 0) + 1
    ev_rows = (
        db.query(InteractionEvent.problem_id, InteractionEvent.event, InteractionEvent.created_at)
        .filter(InteractionEvent.user_id == user_id)
        .all()
    )
    runs: dict = {}
    reviews: dict = {}
    for pid, event, created in ev_rows:
        if _aware(created) > now:
            continue
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
        1 for group in subs_by_pid.values()
        if any(s.status == SubmissionStatus.ACCEPTED for s in group)
    )

    # Pattern context via the same mastery formula as the roadmap heuristic,
    # computed on the as-of snapshot (not present-day state).
    solved_ids = {
        pid for pid, g in subs_by_pid.items()
        if any(s.status == SubmissionStatus.ACCEPTED for s in g)
    }
    attempts_by_pid = {pid: len(g) for pid, g in subs_by_pid.items()}
    pattern_of_pid = {p.id: (p.pattern_key or "") for p in problems.values()}
    mastery_by_pattern: dict = {}
    solved_in_pattern: dict = defaultdict(int)
    attempts_in_pattern: dict = defaultdict(int)
    hints_in_pattern: dict = defaultdict(int)
    pattern_totals: dict = defaultdict(int)
    for p in problems.values():
        if p.pattern_key:
            pattern_totals[p.pattern_key] += 1
    for pid, group in subs_by_pid.items():
        pat = pattern_of_pid.get(pid, "")
        if not pat:
            continue
        attempts_in_pattern[pat] += len(group)
        hints_in_pattern[pat] += hint_counts.get(pid, 0)
        if pid in solved_ids:
            solved_in_pattern[pat] += 1
    for pat, total in pattern_totals.items():
        mastery_by_pattern[pat] = _pattern_mastery(
            solved_in_pattern.get(pat, 0), total, hints_in_pattern.get(pat, 0)
        )

    # Global problem priors cut at `now` (other users only contribute pairs
    # first-touched <= now). Serving may inject pre-aggregated maps, in which
    # case no submission scan happens at all.
    if global_priors is not None:
        pop = dict(global_priors.get("pop", {}))
        acc = dict(global_priors.get("acc", {}))
    else:
        pop = {}
        acc = {}
        all_subs = (
            db.query(Submission)
            .filter(Submission.test_session_id.is_(None))
            .order_by(Submission.submitted_at)
            .all()
        )
        first_touch: dict = {}
        for s in all_subs:
            key = (s.user_id, s.problem_id)
            if key not in first_touch:
                first_touch[key] = _aware(s.submitted_at)
        users_by_pid: dict = defaultdict(set)
        acc_by_pid: dict = defaultdict(set)
        for (ouid, opid), first in first_touch.items():
            if first > now:
                continue
            users_by_pid[opid].add(ouid)
        for s in all_subs:
            if _aware(s.submitted_at) > now:
                continue
            if s.status == SubmissionStatus.ACCEPTED:
                acc_by_pid[s.problem_id].add(s.user_id)
        for pid, us in users_by_pid.items():
            pop[pid] = float(len(us))
            acc[pid] = len(acc_by_pid.get(pid, set())) / len(us) if us else 0.5

    # Learner-state snapshot as-of `now` (same code path as training).
    try:
        by_pattern = _ls.collect_evidence(db, user_id, pattern_of_pid, as_of=now)
        ls_states = {
            pat: _ls.build_topic_state(pat, by_pattern.get(pat, []), now=now)
            for pat in pattern_totals
        }
    except Exception:
        ls_states = {}

    # XP snapshot: ledger <= now, else 0 prior for historical rows (never
    # present-day xp for training). Serving with no ledger uses the live value.
    try:
        xp_q = db.query(XpEvent).filter(XpEvent.user_id == user_id).all()
        xp_snapshot = sum(x.amount for x in xp_q if _aware(x.created_at) <= now)
        has_xp_ledger = True
    except Exception:
        xp_snapshot = 0
        has_xp_ledger = False
    if not has_xp_ledger and as_of is None:
        xp_snapshot = user.xp or 0  # serving with no ledger: live value is correct
    # Streak snapshot from accepted dates <= now.
    accepted_dates = [
        s.submitted_at for g in subs_by_pid.values() for s in g
        if s.status == SubmissionStatus.ACCEPTED
    ]
    streak_snapshot = _streak_before(accepted_dates, now) if accepted_dates else 0
    if as_of is None and not accepted_dates:
        streak_snapshot = user.current_streak or 0

    rows_out = []
    for slug in slugs:
        problem = problems.get(slug)
        if problem is None:
            continue
        pattern = problem.pattern_key or ""
        group = subs_by_pid.get(problem.id, [])
        attempts = len(group)
        ever = 1 if any(s.status == SubmissionStatus.ACCEPTED for s in group) else 0
        rejects = sum(1 for s in group if s.status != SubmissionStatus.ACCEPTED)
        accepted = [s for s in group if s.status == SubmissionStatus.ACCEPTED]
        if accepted:
            first_accept = min(_aware(s.submitted_at) for s in accepted)
            first_sub = min(_aware(s.submitted_at) for s in group)
            minutes = (first_accept - first_sub).total_seconds() / 60.0
            revisits = sum(1 for s in group if _aware(s.submitted_at) > first_accept)
        else:
            minutes = -1.0
            revisits = 0
        order = PATTERN_BY_KEY.get(pattern, {}).get("order", 99) if pattern else 99
        st = ls_states.get(pattern)
        ls_row = _ls.state_feature_row(st) if st is not None else {
            c: DEFAULTS[c] for c in LEARNER_STATE_COLUMNS
        }
        rows_out.append(
            {
                "slug": slug,
                "u_solved_total": float(solved_total),
                "u_xp": float(xp_snapshot),
                "u_streak": float(streak_snapshot),
                "u_mastery_pattern": float(mastery_by_pattern.get(pattern, 0.0)),
                "u_solved_in_pattern": float(solved_in_pattern.get(pattern, 0)),
                "u_attempts_in_pattern": float(attempts_in_pattern.get(pattern, 0)),
                "u_hints_in_pattern": float(hints_in_pattern.get(pattern, 0)),
                "u_solved_at_difficulty": float(solved_by_diff.get(problem.difficulty.value, 0)),
                "i_attempts": float(attempts),
                "i_hints": float(hint_counts.get(problem.id, 0)),
                "i_runs": float(runs.get(problem.id, 0)),
                "i_ever_solved": float(ever),
                "i_reject_ratio": float((rejects / attempts) if attempts else 0.0),
                "i_time_to_accept_min": float(minutes),
                "i_revisits": float(revisits),
                "i_reviews": float(reviews.get(problem.id, 0)),
                "p_diff_ord": float(DIFF_ORD.get(problem.difficulty.value, 1)),
                "p_pattern_order": float(order),
                "p_solvable": float(1 if (problem.starter_code and problem.test_cases) else 0),
                "p_accept_rate": float(acc.get(problem.id, 0.5)),
                "p_popularity": float(pop.get(problem.id, 0.0)),
                **{k: float(v) for k, v in ls_row.items()},
            }
        )
    return rows_out
