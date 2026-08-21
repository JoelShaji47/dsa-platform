from datetime import date, timedelta

from app.models.enums import Difficulty
from app.models.user import User

XP_BY_DIFFICULTY = {
    Difficulty.EASY: 10,
    Difficulty.MEDIUM: 20,
    Difficulty.HARD: 40,
}


def award_xp(user: User, difficulty: Difficulty) -> int:
    return XP_BY_DIFFICULTY[difficulty]


def update_streak(user: User, today: date | None = None) -> None:
    today = today or date.today()
    if user.last_active_date == today:
        return
    if user.last_active_date == today - timedelta(days=1):
        user.current_streak += 1
    else:
        user.current_streak = 1
    user.last_active_date = today
