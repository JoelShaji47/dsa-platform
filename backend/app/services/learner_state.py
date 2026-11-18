"""Topic-level learner-state engine (Phase C).

Transparent, well-tested baseline estimating per-(user, pattern) learning
state from submission/hint/review telemetry. No neural models: a graded,
recency-decayed evidence accumulator in the spirit of Performance Factors
Analysis, with explicit uncertainty when evidence is thin.

Evidence grading (never treat all accepts as equal):
    independent : ACCEPTED with no hints and no editorial/solution review
    hinted      : ACCEPTED after hint(s) but no editorial review
    editorial   : ACCEPTED after a solution/editorial review event
    fail        : attempted but never accepted (or only failures so far)

Weights: independent=1.0, hinted=0.5, editorial=0.2, fail contributes only
to the failure pool. All evidence decays with a 30-day half-life so recent
performance dominates and old mastery fades (retention signal).

If event data cannot support a metric the field carries a documented
conservative prior (mastery 0.0, uncertainty 1.0, trend 0.0) — certainty is
never manufactured.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.interaction import InteractionEvent
from app.models.submission import Submission
from app.services.activity import REVIEW

# Grading weights for successful evidence by independence level.
EVIDENCE_WEIGHTS = {
    "independent": 1.0,
    "hinted": 0.5,
    "editorial": 0.2,
}

# Recency half-life (days) for evidence decay.
HALF_LIFE_DAYS = 30.0
# Strength of the zero-mastery prior (in pseudo-evidence units).
PRIOR_STRENGTH = 2.0
# Failure penalty relative to one unit of success evidence.
FAIL_PENALTY = 0.7
# Windows (days) for recent-trend comparison.
TREND_RECENT_DAYS = 14.0
TREND_PRIOR_DAYS = 28.0
# Review queue thresholds.
REVIEW_MIN_DAYS_SINCE_SUCCESS = 7
REVIEW_PRIORITY_THRESHOLD = 0.5


@dataclass
class TopicEvidence:
    """One graded learning observation in a pattern."""

    pattern_key: str
    outcome: str  # independent | hinted | editorial | fail
    at: datetime
    active_seconds: float | None = None
    attempts: int = 1


@dataclass
class TopicState:
    pattern_key: str
    mastery: float = 0.0  # 0..100
    uncertainty: float = 1.0  # 0..1 (1 = no evidence)
    retention_risk: float = 0.0  # 0..1
    friction: float = 0.0  # 0..1
    trend: float = 0.0  # -1..1
    transfer: float = 0.0  # 0..1
    evidence_success: float = 0.0  # decayed weighted successes
    evidence_fail: float = 0.0  # decayed failures
    n_independent: int = 0
    n_hinted: int = 0
    n_editorial: int = 0
    n_fail: int = 0
    last_independent_success_at: datetime | None = None
    review_priority: float = 0.0
    review_due: bool = False


def _ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _decay(at: datetime, now: datetime) -> float:
    days = max(0.0, (now - _ensure_aware(at)).total_seconds() / 86400.0)
    return 0.5 ** (days / HALF_LIFE_DAYS)


def build_topic_state(
    pattern_key: str,
    evidence: list[TopicEvidence],
    now: datetime | None = None,
    transfer_evidence: list[TopicEvidence] | None = None,
) -> TopicState:
    """Pure, deterministic reducer: evidence list -> TopicState.

    Idempotent: processing the same evidence twice is the caller's
    responsibility to avoid (dedupe by event id upstream); given the same
    input list the output is always identical.
    """
    now = _ensure_aware(now or datetime.now(timezone.utc))
    state = TopicState(pattern_key=pattern_key)
    if not evidence:
        return state  # conservative prior: mastery 0, uncertainty 1

    ev = sorted(evidence, key=lambda e: _ensure_aware(e.at))
    success = 0.0
    fail = 0.0
    hint_hits = 0
    reject_mass = 0.0
    attempt_mass = 0.0
    for e in ev:
        w_decay = _decay(e.at, now)
        if e.outcome == "fail":
            fail += w_decay
            state.n_fail += 1
            reject_mass += 1.0
            attempt_mass += max(1, e.attempts)
        else:
            w = EVIDENCE_WEIGHTS.get(e.outcome, 0.0)
            success += w * w_decay
            attempt_mass += max(1, e.attempts)
            if e.outcome == "independent":
                state.n_independent += 1
                state.last_independent_success_at = _ensure_aware(e.at)
            elif e.outcome == "hinted":
                state.n_hinted += 1
                hint_hits += 1
            elif e.outcome == "editorial":
                state.n_editorial += 1
                hint_hits += 1

    state.evidence_success = round(success, 4)
    state.evidence_fail = round(fail, 4)
    total_evidence = success + fail
    state.mastery = round(
        100.0 * success / (success + FAIL_PENALTY * fail + PRIOR_STRENGTH), 1
    )
    state.uncertainty = round(
        PRIOR_STRENGTH / (PRIOR_STRENGTH + total_evidence), 3
    )

    # Retention: risk grows with days since last *independent* success.
    if state.last_independent_success_at is not None:
        days = (now - state.last_independent_success_at).total_seconds() / 86400.0
        state.retention_risk = round(1.0 - math.exp(-max(0.0, days) / 30.0), 3)
    else:
        state.retention_risk = 0.0  # no success to retain; uncertainty says so

    # Friction: hint dependence blended with failure rate, capped at 1.
    n_outcomes = state.n_independent + state.n_hinted + state.n_editorial + state.n_fail
    hint_rate = (hint_hits / max(1, n_outcomes - state.n_fail)) if n_outcomes else 0.0
    fail_rate = state.n_fail / max(1, n_outcomes)
    state.friction = round(min(1.0, 0.5 * min(1.0, hint_rate) + 0.5 * fail_rate), 3)

    # Trend: recent-window vs prior-window weighted success share.
    def _share(items: list[TopicEvidence]) -> float | None:
        if not items:
            return None
        s = sum(EVIDENCE_WEIGHTS.get(e.outcome, 0.0) for e in items if e.outcome != "fail")
        f = sum(1 for e in items if e.outcome == "fail")
        denom = s + f
        return (s / denom) if denom else None

    recent = [
        e for e in ev
        if (now - _ensure_aware(e.at)).total_seconds() / 86400.0 <= TREND_RECENT_DAYS
    ]
    prior = [
        e for e in ev
        if TREND_RECENT_DAYS < (now - _ensure_aware(e.at)).total_seconds() / 86400.0
        <= TREND_RECENT_DAYS + TREND_PRIOR_DAYS
    ]
    r_share, p_share = _share(recent), _share(prior)
    if r_share is not None and p_share is not None:
        state.trend = round(max(-1.0, min(1.0, r_share - p_share)), 3)
    else:
        state.trend = 0.0  # documented prior when a window is empty

    # Transfer: independent-solve share on *first-touch* related evidence.
    # Related = prerequisite-pattern evidence passed in by the caller; when
    # unavailable the prior is 0.0 (uncertainty already flags thin evidence).
    if transfer_evidence:
        t_share = _share(transfer_evidence)
        state.transfer = round(t_share or 0.0, 3)
    else:
        state.transfer = 0.0

    # Review priority: retention risk + friction + remaining mastery gap.
    state.review_priority = round(
        min(
            1.0,
            0.5 * state.retention_risk
            + 0.3 * state.friction
            + 0.2 * (1.0 - state.mastery / 100.0),
        ),
        3,
    )
    days_since = (
        (now - state.last_independent_success_at).total_seconds() / 86400.0
        if state.last_independent_success_at is not None
        else None
    )
    state.review_due = bool(
        state.review_priority >= REVIEW_PRIORITY_THRESHOLD
        and days_since is not None
        and days_since >= REVIEW_MIN_DAYS_SINCE_SUCCESS
    )
    return state


def classify_outcome(
    accepted: bool,
    hints_used: int,
    had_editorial_review: bool,
) -> str:
    """Grade one (user, problem) outcome by independence level."""
    if not accepted:
        return "fail"
    if had_editorial_review:
        return "editorial"
    if hints_used > 0:
        return "hinted"
    return "independent"


def collect_evidence(
    db: Session,
    user_id: UUID,
    pattern_of_pid: dict,
    as_of: datetime | None = None,
) -> dict[str, list[TopicEvidence]]:
    """Build graded per-pattern evidence for a user from canonical records.

    When ``as_of`` is given, only events with timestamp <= as_of are used
    (historical snapshot for training; ties broken deterministically by id
    ordering upstream). Otherwise the full history is used (serving).
    """
    as_of = _ensure_aware(as_of) if as_of is not None else None

    subs = (
        db.query(Submission)
        .filter(
            Submission.user_id == user_id,
            Submission.test_session_id.is_(None),
        )
        .order_by(Submission.submitted_at, Submission.id)
        .all()
    )
    hint_rows = (
        db.query(HintUsage)
        .filter(HintUsage.user_id == user_id)
        .order_by(HintUsage.used_at, HintUsage.id)
        .all()
    )
    review_pids = {
        row[0]
        for row in db.query(InteractionEvent.problem_id)
        .filter(
            InteractionEvent.user_id == user_id,
            InteractionEvent.event == REVIEW,
        )
        .all()
    }

    hints_by_pid: dict = {}
    for h in hint_rows:
        if as_of is not None and _ensure_aware(h.used_at) > as_of:
            continue
        hints_by_pid.setdefault(h.problem_id, 0)
        hints_by_pid[h.problem_id] += 1

    subs_by_pid: dict = {}
    for s in subs:
        if as_of is not None and _ensure_aware(s.submitted_at) > as_of:
            continue
        subs_by_pid.setdefault(s.problem_id, []).append(s)

    # Review events are timestamped; without per-event timestamps in this
    # query path we approximate "had review" only from events <= as_of by
    # re-checking created_at here.
    review_pids_asof: set = set()
    if review_pids:
        q = db.query(InteractionEvent.problem_id, InteractionEvent.created_at).filter(
            InteractionEvent.user_id == user_id,
            InteractionEvent.event == REVIEW,
        )
        for pid, created in q.all():
            if as_of is not None and _ensure_aware(created) > as_of:
                continue
            review_pids_asof.add(pid)

    by_pattern: dict[str, list[TopicEvidence]] = {}
    for pid, group in subs_by_pid.items():
        pattern = pattern_of_pid.get(pid)
        if not pattern:
            continue
        accepted = any(s.status == SubmissionStatus.ACCEPTED for s in group)
        outcome = classify_outcome(
            accepted,
            hints_by_pid.get(pid, 0),
            pid in review_pids_asof,
        )
        # Evidence timestamp = first touch (deterministic); recency uses it.
        first_at = min(_ensure_aware(s.submitted_at) for s in group)
        by_pattern.setdefault(pattern, []).append(
            TopicEvidence(
                pattern_key=pattern,
                outcome=outcome,
                at=first_at,
                attempts=len(group),
            )
        )
    return by_pattern


def topic_states_for_user(
    db: Session,
    user_id: UUID,
    pattern_keys: list[str] | None = None,
    pattern_of_pid: dict | None = None,
    prerequisites_of: dict[str, list[str]] | None = None,
    as_of: datetime | None = None,
    now: datetime | None = None,
) -> dict[str, TopicState]:
    """Convenience wrapper: query evidence and reduce to per-pattern states."""
    from app.services.roadmap import PATTERN_BY_KEY
    from app.models.problem import Problem

    if pattern_of_pid is None:
        pattern_of_pid = {
            p.id: p.pattern_key
            for p in db.query(Problem.id, Problem.pattern_key)
            .filter(Problem.pattern_key.is_not(None))
            .all()
        }
    keys = pattern_keys or list(PATTERN_BY_KEY.keys())
    prereqs = prerequisites_of or {
        k: list(v.get("prerequisites", [])) for k, v in PATTERN_BY_KEY.items()
    }
    by_pattern = collect_evidence(db, user_id, pattern_of_pid, as_of=as_of)
    now_aware = _ensure_aware(now or datetime.now(timezone.utc))
    states: dict[str, TopicState] = {}
    for key in keys:
        transfer_ev: list[TopicEvidence] = []
        for pre in prereqs.get(key, []):
            transfer_ev.extend(by_pattern.get(pre, []))
        states[key] = build_topic_state(
            key, by_pattern.get(key, []), now=now_aware,
            transfer_evidence=transfer_ev,
        )
    return states


def state_feature_row(state: TopicState) -> dict[str, float]:
    """Project a TopicState onto the six learner-state feature columns."""
    from app.ml.features import LEARNER_STATE_COLUMNS

    row = {
        "ls_mastery": state.mastery / 100.0,
        "ls_uncertainty": state.uncertainty,
        "ls_retention_risk": state.retention_risk,
        "ls_friction": state.friction,
        "ls_trend": state.trend,
        "ls_review_priority": state.review_priority,
    }
    return {c: float(row[c]) for c in LEARNER_STATE_COLUMNS}
