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


def ensure_badge_catalog(db: Session) -> None:
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


def _earned_conditions(db: Session, user: User) -> set[str]:
    solved_rows = (
        db.query(Submission.problem_id, Problem.topic, Submission.language)
        .join(Problem, Problem.id == Submission.problem_id)
        .filter(
            Submission.user_id == user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
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
        db.query(Problem.topic, func.count(Problem.id)).group_by(Problem.topic).all()
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
    ensure_badge_catalog(db)
    earned = {
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
            "earned": definition["criteria"] in earned,
            "earned_at": earned.get(definition["criteria"]),
        }
        for definition in BADGE_DEFINITIONS
    ]
