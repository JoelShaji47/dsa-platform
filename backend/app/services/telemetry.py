"""Privacy-conscious telemetry writes (Phase B).

All functions fail safe: telemetry must never corrupt a successful
submission or fail a core request. Callers wrap these in try/except with a
rollback; functions themselves also roll back on error and return a safe
default instead of raising (except validation errors the API maps to 4xx).
No source code, keystrokes, secrets or personal data are ever stored.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.hint import HintUsage
from app.models.interaction import InteractionEvent
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.telemetry import (
    IDLE_TIMEOUT_SECONDS,
    RecommendationImpression,
    RecommendationOpportunity,
    SolveSession,
    estimate_active_seconds,
)
from app.models.user import User
from app.services.activity import REVIEW, RUN

logger = logging.getLogger(__name__)

# Actions the client may report on an exposed recommendation.
FEEDBACK_ACTIONS = ("click", "dismiss")


def create_opportunity(
    db: Session,
    user: User,
    model_version: str,
    candidate_count: int,
    feature_schema_version: int = 2,
) -> UUID | None:
    """Log one recommendation opportunity. Returns id or None (never raises)."""
    try:
        opp = RecommendationOpportunity(
            user_id=user.id,
            model_version=model_version,
            feature_schema_version=feature_schema_version,
            candidate_count=candidate_count,
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)
        return opp.id
    except Exception:
        db.rollback()
        logger.debug("opportunity logging failed", exc_info=True)
        return None


def record_impressions(
    db: Session,
    user: User,
    opportunity_id: UUID,
    items: list[dict],
) -> int:
    """Record actually-rendered impressions for one opportunity.

    Validates opportunity ownership; unknown slugs are skipped; duplicate
    (opportunity, problem) pairs are ignored (idempotent retries).
    Returns the number of newly recorded impressions.
    """
    opp = db.get(RecommendationOpportunity, opportunity_id)
    if opp is None or opp.user_id != user.id:
        raise PermissionError("opportunity not found")
    problems = {p.slug: p for p in db.query(Problem).all()}
    recorded = 0
    for item in items:
        problem = problems.get(item.get("slug", ""))
        if problem is None:
            continue
        try:
            rank = int(item.get("rank", 0))
        except (TypeError, ValueError):
            continue
        imp = RecommendationImpression(
            opportunity_id=opp.id,
            user_id=user.id,
            problem_id=problem.id,
            rank=rank,
            source=str(item.get("source", "roadmap"))[:30],
            model_version=opp.model_version,
            feature_schema_version=opp.feature_schema_version,
            rendered=bool(item.get("rendered", True)),
        )
        db.add(imp)
        try:
            db.commit()
            recorded += 1
        except IntegrityError:
            db.rollback()  # duplicate retry: idempotent, not an error
        except Exception:
            db.rollback()
            logger.debug("impression logging failed", exc_info=True)
    return recorded


def record_feedback(
    db: Session, user: User, opportunity_id: UUID, problem_slug: str, action: str
) -> dict:
    """Record explicit feedback on one exposed recommendation.

    ``action`` is ``"click"`` or ``"dismiss"``. The first action wins: a
    dismissed card can never later become a click (and vice versa), so the
    label is unambiguous. Idempotent retries report ``applied=False`` instead
    of raising or double-writing.

    Raises PermissionError (wrong owner), LookupError (unknown slug or no
    impression for that opportunity/problem) and ValueError (bad action) —
    the API maps those to 404/400.
    """
    if action not in FEEDBACK_ACTIONS:
        raise ValueError(f"action must be one of {FEEDBACK_ACTIONS}")
    opp = db.get(RecommendationOpportunity, opportunity_id)
    if opp is None or opp.user_id != user.id:
        raise PermissionError("opportunity not found")
    problem = db.query(Problem).filter(Problem.slug == problem_slug).first()
    if problem is None:
        raise LookupError("problem not found")
    imp = (
        db.query(RecommendationImpression)
        .filter(
            RecommendationImpression.opportunity_id == opp.id,
            RecommendationImpression.problem_id == problem.id,
        )
        .first()
    )
    if imp is None:
        # Feedback on something never exposed: refuse rather than invent an
        # impression, otherwise click-through rate gets a free denominator.
        raise LookupError("impression not found")

    applied = False
    if imp.clicked_at is None and imp.dismissed_at is None:
        now = datetime.now(timezone.utc)
        if action == "click":
            imp.clicked_at = now
        else:
            imp.dismissed_at = now
        try:
            db.commit()
            applied = True
        except Exception:
            db.rollback()
            logger.debug("impression feedback write failed", exc_info=True)
        db.refresh(imp)

    return {
        "slug": problem.slug,
        "action": action,
        "applied": applied,
        "clicked": imp.clicked_at is not None,
        "dismissed": imp.dismissed_at is not None,
    }


def start_session(
    db: Session,
    user: User,
    problem_slug: str,
    client_session_id: str,
    opportunity_id: UUID | None = None,
) -> SolveSession:
    """Open (or idempotently re-open) a solve session. Raises 4xx-mappable."""
    problem = db.query(Problem).filter(Problem.slug == problem_slug).first()
    if problem is None:
        raise LookupError("problem not found")
    if opportunity_id is not None:
        opp = db.get(RecommendationOpportunity, opportunity_id)
        if opp is None or opp.user_id != user.id:
            raise PermissionError("opportunity not found")
    existing = (
        db.query(SolveSession)
        .filter(
            SolveSession.user_id == user.id,
            SolveSession.client_session_id == client_session_id[:60],
        )
        .first()
    )
    if existing is not None:
        return existing  # idempotent retry
    session = SolveSession(
        client_session_id=client_session_id[:60],
        user_id=user.id,
        problem_id=problem.id,
        opportunity_id=opportunity_id,
        last_heartbeat_at=datetime.now(timezone.utc),
        heartbeat_count=1,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def heartbeat_session(
    db: Session, user: User, session_id: UUID, at: datetime | None = None
) -> SolveSession:
    """Record one heartbeat; active_seconds grows by the capped gap."""
    session = db.get(SolveSession, session_id)
    if session is None or session.user_id != user.id:
        raise PermissionError("session not found")
    now = at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    last = session.last_heartbeat_at
    if last is not None:
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        gap = (now - last).total_seconds()
        if 0 <= gap:
            session.active_seconds = round(
                (session.active_seconds or 0.0) + min(gap, IDLE_TIMEOUT_SECONDS), 1
            )
    session.last_heartbeat_at = now
    session.heartbeat_count = (session.heartbeat_count or 0) + 1
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.debug("heartbeat write failed", exc_info=True)
    db.refresh(session)
    return session


def _reconcile_counters(db: Session, session: SolveSession) -> None:
    """Reconcile session counters against canonical records (no divergence)."""
    since = session.started_at
    subs = (
        db.query(Submission)
        .filter(
            Submission.user_id == session.user_id,
            Submission.problem_id == session.problem_id,
            Submission.test_session_id.is_(None),
            Submission.submitted_at >= since,
        )
        .all()
    )
    session.attempt_count = len(subs)
    accepted = [s for s in subs if s.status == SubmissionStatus.ACCEPTED]
    if accepted:
        first = min(s.submitted_at for s in accepted)
        session.first_accepted_at = first
        session.status = "solved"
    elif subs:
        session.status = "attempted"
    session.hint_count = (
        db.query(HintUsage)
        .filter(
            HintUsage.user_id == session.user_id,
            HintUsage.problem_id == session.problem_id,
            HintUsage.used_at >= since,
        )
        .count()
    )
    ev_rows = (
        db.query(InteractionEvent.event)
        .filter(
            InteractionEvent.user_id == session.user_id,
            InteractionEvent.problem_id == session.problem_id,
            InteractionEvent.created_at >= since,
        )
        .all()
    )
    session.run_count = sum(1 for (e,) in ev_rows if e == RUN)
    session.review_count = sum(1 for (e,) in ev_rows if e == REVIEW)
    if any(e == REVIEW for (e,) in ev_rows):
        session.editorial_revealed = True


def finish_session(
    db: Session,
    user: User,
    session_id: UUID,
    claimed_time_complexity: str | None = None,
    claimed_space_complexity: str | None = None,
) -> SolveSession:
    """Close a session; counters reconcile from canonical records."""
    session = db.get(SolveSession, session_id)
    if session is None or session.user_id != user.id:
        raise PermissionError("session not found")
    now = datetime.now(timezone.utc)
    session.ended_at = now
    if claimed_time_complexity:
        session.claimed_time_complexity = claimed_time_complexity[:20]
    if claimed_space_complexity:
        session.claimed_space_complexity = claimed_space_complexity[:20]
    # Verified complexity intentionally stays NULL (no reliable assessment
    # mechanism; self-reported and verified must remain separate).
    try:
        _reconcile_counters(db, session)
        if session.status == "active":
            session.status = "abandoned" if not session.attempt_count else "attempted"
        db.commit()
    except Exception:
        db.rollback()
        logger.debug("session finish failed", exc_info=True)
    db.refresh(session)
    return session
