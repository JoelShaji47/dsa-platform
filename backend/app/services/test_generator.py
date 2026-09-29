import random

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.enums import Difficulty, Topic
from app.models.problem import Problem

SLOTS: tuple[Difficulty, ...] = (Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD)


class TopicPoolEmptyError(Exception):
    def __init__(self, topic: Topic, difficulty: Difficulty) -> None:
        self.topic = topic
        self.difficulty = difficulty
        super().__init__(f"No solvable {difficulty.value} problems for {topic.value}")


def solvable_pool(db: Session, topics: list[Topic]) -> list[Problem]:
    """Problems with real starter code and real test cases, in the given topics."""
    stmt = (
        select(Problem)
        .where(
            Problem.topic.in_(topics),
            Problem.starter_code != text("'{}'::jsonb"),
            Problem.test_cases != text("'[]'::jsonb"),
        )
        .order_by(Problem.id)
    )
    return list(db.execute(stmt).scalars())


def choose_slot_categories(
    topics: list[Topic], rng: random.SystemRandom
) -> dict[Difficulty, Topic]:
    """Map each difficulty slot to a category.

    Three or more selected: three distinct categories, one per slot.
    Two selected: one category covers two randomly chosen slots, the other the rest.
    One selected: that category covers all three.
    """
    if len(topics) >= 3:
        return dict(zip(SLOTS, rng.sample(topics, 3)))
    if len(topics) == 2:
        doubled, single = rng.sample(topics, 2)
        doubled_slots = rng.sample(SLOTS, 2)
        return {
            slot: (doubled if slot in doubled_slots else single) for slot in SLOTS
        }
    return {slot: topics[0] for slot in SLOTS}


def pick_test_problems(
    db: Session,
    topics: list[Topic],
    rng: random.SystemRandom | None = None,
) -> list[tuple[Difficulty, Topic, Problem]]:
    """One Easy, one Medium and one Hard problem. Slots never repeat a problem
    because a problem carries exactly one difficulty."""
    rng = rng or random.SystemRandom()
    pool = solvable_pool(db, topics)

    buckets: dict[tuple[Difficulty, Topic], list[Problem]] = {
        (difficulty, topic): [
            p for p in pool if p.difficulty == difficulty and p.topic == topic
        ]
        for difficulty in SLOTS
        for topic in topics
    }

    slot_categories = choose_slot_categories(topics, rng)
    picks: list[tuple[Difficulty, Topic, Problem]] = []
    for difficulty in SLOTS:
        category = slot_categories[difficulty]
        candidates = buckets[(difficulty, category)]
        if not candidates:
            raise TopicPoolEmptyError(category, difficulty)
        picks.append((difficulty, category, rng.choice(candidates)))
    return picks
