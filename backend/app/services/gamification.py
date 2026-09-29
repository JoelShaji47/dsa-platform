from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.badge import Badge, UserBadge
from app.models.enums import Difficulty, Language, SubmissionStatus, Topic
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User

TOPIC_BADGE_META = {
    Topic.ARRAY: ("Array Adept", "Solve every Array problem"),
    Topic.STRING: ("String Sage", "Solve every String problem"),
    Topic.LINKED_LIST: ("Pointer Wrangler", "Solve every Linked List problem"),
    Topic.STACK: ("Stack Master", "Solve every Stack problem"),
    Topic.QUEUE: ("Deque Driver", "Solve every Queue problem"),
    Topic.TREE: ("Tree Climber", "Solve every Tree problem"),
    Topic.GRAPH: ("Graph Navigator", "Solve every Graph problem"),
    Topic.DP: ("DP Dynamo", "Solve every Dynamic Programming problem"),
}

BADGE_DEFINITIONS = [
    {
        "criteria": "FIRST_BLOOD",
        "name": "First Blood",
        "description": "Solve your very first problem",
    },
    {
        "criteria": "TEN_CLUB",
        "name": "Ten Club",
        "description": "Solve 10 distinct problems",
    },
    {
        "criteria": "POLYGLOT",
        "name": "Polyglot",
        "description": "Accept the same problem in Python, C++ and Java",
    },
    {
        "criteria": "STREAK_WEEK",
        "name": "Streak Week",
        "description": "Reach a 7-day solving streak",
    },
    {
        "criteria": "WEEKLY_CHAMPION",
        "name": "Weekly Champion",
        "description": "Finish rank 1 in your weekly league",
    },
] + [
    {
        "criteria": f"TOPIC_{topic.value}",
        "name": name,
        "description": description,
    }
    for topic, (name, description) in TOPIC_BADGE_META.items()
]

MASTERY_SIZE = 10

XP_BY_DIFFICULTY = {
    Difficulty.EASY: 10,
    Difficulty.MEDIUM: 20,
    Difficulty.HARD: 40,
}

# ── Solve scoring (explainable multipliers, shown in the UI) ──
STREAK_STEP = 0.05  # +5% per streak day, capped
STREAK_CAP_DAYS = 10
CLEAN_MULT = 1.25  # no hints + first-try accept
WEAK_MULT = 1.25  # pattern mastery below threshold
WEAK_MASTERY = 40.0


def award_xp(user: User, difficulty: Difficulty) -> int:
    return XP_BY_DIFFICULTY[difficulty]


def score_solve(
    db: Session,
    user: User,
    problem,
    hints_used: bool,
    prior_attempts: int,
) -> tuple[int, dict]:
    """XP total + breakdown. Multipliers reward consistency (streak),
    precision (clean first-try, no hints) and courage (weak patterns)."""
    from app.models.problem import Problem as ProblemModel

    base = XP_BY_DIFFICULTY[problem.difficulty]
    streak_days = user.current_streak or 0
    streak_mult = round(1 + min(streak_days, STREAK_CAP_DAYS) * STREAK_STEP, 3)
    clean_mult = 1.0 if (hints_used or prior_attempts > 0) else CLEAN_MULT

    weak_mult = 1.0
    pattern = problem.pattern_key
    if pattern:
        total = (
            db.query(ProblemModel.id).filter(ProblemModel.pattern_key == pattern).count()
        )
        if total:
            from app.models.enums import SubmissionStatus as _Status
            from app.models.submission import Submission as _Submission

            solved = (
                db.query(_Submission.problem_id)
                .join(ProblemModel, ProblemModel.id == _Submission.problem_id)
                .filter(
                    _Submission.user_id == user.id,
                    _Submission.status == _Status.ACCEPTED,
                    ProblemModel.pattern_key == pattern,
                )
                .distinct()
                .count()
            )
            if (solved / total * 100) < WEAK_MASTERY:
                weak_mult = WEAK_MULT

    total_xp = int(round(base * streak_mult * clean_mult * weak_mult))
    return total_xp, {
        "base": base,
        "streak_mult": streak_mult,
        "clean_mult": clean_mult,
        "weak_mult": weak_mult,
        "total": total_xp,
    }

# ── XP shop ──────────────────────────────────────────────────
FREEZE_COST = 100
MAX_FREEZES = 3


class InsufficientXP(Exception):
    pass


def log_xp(
    db: Session,
    user: User,
    amount: int,
    reason: str,
    problem_id=None,
    created_at=None,
) -> None:
    """Append to the ledger and keep users.xp in sync (single writer)."""
    from app.models.xp_event import XpEvent

    row: dict = {
        "user_id": user.id,
        "amount": amount,
        "reason": reason,
        "problem_id": problem_id,
    }
    if created_at is not None:
        row["created_at"] = created_at
    db.add(XpEvent(**row))
    user.xp = (user.xp or 0) + amount


def xp_balance(db: Session, user: User) -> int:
    return int(user.xp or 0)


def buy_streak_freeze(db: Session, user: User) -> dict:
    """Spend XP on a streak freeze. Raises InsufficientXP / ValueError (cap)."""
    if (user.streak_freezes or 0) >= MAX_FREEZES:
        raise ValueError(f"Freeze holder is full (max {MAX_FREEZES})")
    if xp_balance(db, user) < FREEZE_COST:
        raise InsufficientXP(f"Need {FREEZE_COST} XP for a streak freeze")
    log_xp(db, user, -FREEZE_COST, "freeze_buy")
    user.streak_freezes = (user.streak_freezes or 0) + 1
    db.commit()
    db.refresh(user)
    return {"freezes": user.streak_freezes, "xp": user.xp, "cost": FREEZE_COST}


def xp_earned_between(db: Session, user_id, start, end) -> int:
    """Sum of positive XP events in [start, end) — league scoring."""
    from app.models.xp_event import XpEvent

    total = (
        db.query(func.coalesce(func.sum(XpEvent.amount), 0))
        .filter(
            XpEvent.user_id == user_id,
            XpEvent.amount > 0,
            XpEvent.created_at >= start,
            XpEvent.created_at < end,
        )
        .scalar()
    )
    return int(total or 0)


def update_streak(user: User, today: date | None = None) -> None:
    today = today or date.today()
    if user.last_active_date == today:
        return
    if user.last_active_date == today - timedelta(days=1):
        user.current_streak += 1
    else:
        # Streak freeze: each held freeze covers one missed day.
        missed = (
            (today - user.last_active_date).days - 1
            if user.last_active_date is not None
            else 0
        )
        freezes = user.streak_freezes or 0
        if missed > 0 and freezes >= missed and user.current_streak > 0:
            user.streak_freezes = freezes - missed
        else:
            user.current_streak = 1
    user.last_active_date = today


_catalog_synced = False


def ensure_badge_catalog(db: Session) -> None:
    global _catalog_synced
    if _catalog_synced:
        return
    for definition in BADGE_DEFINITIONS:
        badge = (
            db.query(Badge).filter(Badge.criteria == definition["criteria"]).first()
        )
        if badge is None:
            db.add(Badge(**definition))
        else:
            badge.name = definition["name"]
            badge.description = definition["description"]
    db.commit()
    _catalog_synced = True


def _earned_conditions(db: Session, user: User) -> set[str]:
    solved_rows = (
        db.query(Submission.problem_id, Problem.topic, Submission.language)
        .join(Problem, Problem.id == Submission.problem_id)
        .filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
        )
        .all()
    )

    topics_by_problem: dict = {}
    languages_by_problem: dict = defaultdict(set)
    for problem_id, topic, language in solved_rows:
        topics_by_problem[problem_id] = topic
        languages_by_problem[problem_id].add(language)

    conditions = set()
    if len(topics_by_problem) >= 1:
        conditions.add("FIRST_BLOOD")
    if len(topics_by_problem) >= MASTERY_SIZE:
        conditions.add("TEN_CLUB")
    if any(len(langs) >= 3 for langs in languages_by_problem.values()):
        conditions.add("POLYGLOT")
    if user.current_streak >= 7:
        conditions.add("STREAK_WEEK")

    topic_totals = dict(
        db.query(Problem.topic, func.count(Problem.id))
        .filter(Problem.is_published.is_(True))
        .group_by(Problem.topic)
        .all()
    )
    topic_solved: dict = defaultdict(set)
    for problem_id, topic in topics_by_problem.items():
        topic_solved[topic].add(problem_id)
    for topic, total in topic_totals.items():
        if len(topic_solved.get(topic, set())) >= total > 0:
            conditions.add(f"TOPIC_{topic.value}")

    return conditions


def award_new_badges(db: Session, user: User) -> list[str]:
    ensure_badge_catalog(db)

    conditions = _earned_conditions(db, user)
    if not conditions:
        return []

    owned_criteria = {
        row[0]
        for row in db.query(Badge.criteria)
        .join(UserBadge, UserBadge.badge_id == Badge.id)
        .filter(UserBadge.user_id == user.id)
        .all()
    }

    newly_awarded: list[str] = []
    for criteria in sorted(conditions - owned_criteria):
        badge = db.query(Badge).filter(Badge.criteria == criteria).one()
        db.add(UserBadge(user_id=user.id, badge_id=badge.id))
        newly_awarded.append(badge.name)
    return newly_awarded


def list_user_badges(db: Session, user: User) -> list[dict]:
    owned = {
        row[0]: row[1]
        for row in db.query(Badge.criteria, UserBadge.earned_at)
        .join(UserBadge, UserBadge.badge_id == Badge.id)
        .filter(UserBadge.user_id == user.id)
        .all()
    }
    return [
        {
            "criteria": definition["criteria"],
            "name": definition["name"],
            "description": definition["description"],
            "earned": definition["criteria"] in owned,
            "earned_at": owned.get(definition["criteria"]),
        }
        for definition in BADGE_DEFINITIONS
    ]
