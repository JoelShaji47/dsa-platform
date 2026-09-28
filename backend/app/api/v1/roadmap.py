from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
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


@router.get("/recommendations")
def recommendations(
    explain: bool = False,
    pattern: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    recs = get_recommendations(db, current_user, explain=explain)
    if pattern is not None:
        # Weak-pattern drill: top picks constrained to one pattern.
        recs = [r for r in recs if r.get("pattern_key") == pattern]
    return {"recommendations": recs}


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
