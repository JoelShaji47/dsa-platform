from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services import leagues

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.get("/me")
def my_league(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return leagues.board(db, current_user)


@router.get("/global")
def global_board(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return {"board": leagues.global_board(db)}


@router.get("/monthly")
def monthly_board(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return {"board": leagues.monthly_board(db)}


@router.get("/pattern/{pattern_key}")
def pattern_board(
    pattern_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return {"pattern_key": pattern_key, "board": leagues.pattern_board(db, pattern_key)}
