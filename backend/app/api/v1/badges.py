from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.stats import BadgeOut
from app.services.gamification import list_user_badges

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("/me", response_model=list[BadgeOut])
def my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BadgeOut]:
    return [BadgeOut(**badge) for badge in list_user_badges(db, current_user)]
