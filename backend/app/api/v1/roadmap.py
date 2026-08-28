from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.roadmap import get_recommendations

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return {"recommendations": get_recommendations(db, current_user)}
