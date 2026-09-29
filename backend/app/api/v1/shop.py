from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.gamification import (
    FREEZE_COST,
    MAX_FREEZES,
    InsufficientXP,
    buy_streak_freeze,
    xp_balance,
)

router = APIRouter(prefix="/shop", tags=["shop"])


@router.get("")
def shop_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return {
        "xp": xp_balance(db, current_user),
        "freezes": current_user.streak_freezes or 0,
        "items": [
            {
                "id": "streak_freeze",
                "name": "Streak Freeze",
                "description": "Skips one missed day without breaking your streak. Auto-used, holds max 3.",
                "cost": FREEZE_COST,
                "max_holding": MAX_FREEZES,
            }
        ],
    }


@router.post("/freeze")
def buy_freeze(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        return buy_streak_freeze(db, current_user)
    except InsufficientXP as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
