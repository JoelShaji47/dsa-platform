from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.telemetry import (
    ImpressionFeedbackIn,
    ImpressionsIn,
    SessionFinishIn,
    SessionStartIn,
    session_out,
)
from app.services.roadmap import (
    get_activity,
    get_daily_question,
    get_recommendations,
    get_review_due,
)

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.get("")
def roadmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    from app.services.roadmap import get_roadmap

    return get_roadmap(db, current_user)


@router.get("/pathway")
def pathway(
    limit: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Layer 2: ordered pattern plan, highest learning signal per hour first."""
    from app.services.pathway import build_pathway

    return build_pathway(db, current_user, limit=limit)


@router.get("/recommendations")
def recommendations(
    explain: bool = False,
    pattern: str | None = None,
    intent: str = "balanced",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    recs = get_recommendations(
        db, current_user, explain=explain, intent=intent, pattern=pattern
    )
    return {"recommendations": recs}


@router.post("/impressions")
def log_impressions(
    body: ImpressionsIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Record which recommendations were actually rendered (B1).

    Only the owning user may log to their opportunity; duplicates from
    client retries are ignored (idempotent).
    """
    from app.services import telemetry as _telemetry

    try:
        n = _telemetry.record_impressions(
            db, current_user, body.opportunity_id,
            [i.model_dump() for i in body.items],
        )
    except PermissionError:
        raise HTTPException(status_code=404, detail="opportunity not found")
    return {"recorded": n}


@router.post("/impressions/feedback")
def log_impression_feedback(
    body: ImpressionFeedbackIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Record a click or dismissal on an already-exposed recommendation.

    First action wins; retries are idempotent (``applied: false``). Feedback
    for a pair that was never impressed is rejected rather than fabricated.
    """
    from app.services import telemetry as _telemetry

    try:
        return _telemetry.record_feedback(
            db, current_user, body.opportunity_id, body.slug, body.action
        )
    except PermissionError:
        raise HTTPException(status_code=404, detail="opportunity not found")
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/sessions")
def start_solve_session(
    body: SessionStartIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    from app.services import telemetry as _telemetry

    try:
        s = _telemetry.start_session(
            db, current_user, body.problem_slug,
            body.client_session_id, body.opportunity_id,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="problem not found")
    except PermissionError:
        raise HTTPException(status_code=404, detail="opportunity not found")
    return {"session": session_out(s)}


@router.post("/sessions/{session_id}/heartbeat")
def heartbeat_solve_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    from app.services import telemetry as _telemetry

    try:
        s = _telemetry.heartbeat_session(db, current_user, session_id)
    except PermissionError:
        raise HTTPException(status_code=404, detail="session not found")
    return {"session": session_out(s)}


@router.post("/sessions/{session_id}/finish")
def finish_solve_session(
    session_id: UUID,
    body: SessionFinishIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    from app.services import telemetry as _telemetry

    try:
        s = _telemetry.finish_session(
            db, current_user, session_id,
            body.claimed_time_complexity, body.claimed_space_complexity,
        )
    except PermissionError:
        raise HTTPException(status_code=404, detail="session not found")
    return {"session": session_out(s)}


@router.get("/review-due")
def review_due(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return {"review_due": get_review_due(db, current_user)}


@router.get("/daily")
def daily_question(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return get_daily_question(db, current_user)


@router.get("/activity")
def roadmap_activity(
    days: int = 140,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return get_activity(db, current_user, days=min(max(days, 1), 400))
