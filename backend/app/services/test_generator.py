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
    return pick_custom_problems(db, topics, num_questions=3, rng=rng)


def _balanced_difficulties(count: int) -> list[Difficulty]:
    """Cycle E/M/H so any count stays balanced (E,M,H,M,E,H,...)."""
    cycle = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
    return [cycle[i % 3] for i in range(count)]


def pick_custom_problems(
    db: Session,
    topics: list[Topic],
    num_questions: int = 3,
    difficulties: list[Difficulty] | None = None,
    problem_slugs: list[str] | None = None,
    rng: random.SystemRandom | None = None,
) -> list[tuple[Difficulty, Topic, Problem]]:
    """Custom test question picker, one building block at a time.

    - problem_slugs: exact problems in the given order (validated solvable).
    - difficulties: per-position difficulty override (len must match count).
    - default: balanced E/M/H cycle across num_questions positions.
    Problems never repeat within one test.
    """
    rng = rng or random.SystemRandom()

    if problem_slugs:
        wanted = list(dict.fromkeys(problem_slugs))
        if len(wanted) != len(problem_slugs):
            raise ValueError("Duplicate problem slugs in custom test")
        rows = db.query(Problem).filter(Problem.slug.in_(wanted)).all()
        by_slug = {p.slug: p for p in rows}
        picks: list[tuple[Difficulty, Topic, Problem]] = []
        for slug in problem_slugs:
            problem = by_slug.get(slug)
            if problem is None:
                raise ValueError(f"Unknown problem slug: {slug}")
            if not problem.starter_code or not problem.test_cases:
                raise TopicPoolEmptyError(problem.topic, problem.difficulty)
            picks.append((problem.difficulty, problem.topic, problem))
        return picks

    if num_questions < 1 or num_questions > 6:
        raise ValueError("num_questions must be between 1 and 6")
    want_diffs = list(difficulties) if difficulties else _balanced_difficulties(num_questions)
    if len(want_diffs) != num_questions:
        raise ValueError("difficulties length must match num_questions")

    # Classic 3-question path keeps the legacy category guarantees (distinct
    # categories for 3+ topics, full coverage for 2, single for 1).
    if difficulties is None and num_questions == 3:
        pool = solvable_pool(db, topics)
        buckets: dict[tuple[Difficulty, Topic], list[Problem]] = {
            (difficulty, topic): [
                p for p in pool if p.difficulty == difficulty and p.topic == topic
            ]
            for difficulty in SLOTS
            for topic in topics
        }
        slot_categories = choose_slot_categories(topics, rng)
        legacy: list[tuple[Difficulty, Topic, Problem]] = []
        for difficulty in SLOTS:
            category = slot_categories[difficulty]
            candidates = buckets[(difficulty, category)]
            if not candidates:
                raise TopicPoolEmptyError(category, difficulty)
            legacy.append((difficulty, category, rng.choice(candidates)))
        return legacy

    pool = solvable_pool(db, topics)
    # Spread positions across the selected topics round-robin so custom counts
    # still touch every chosen area instead of clustering on one.
    spread: list[Topic] = [topics[i % len(topics)] for i in range(num_questions)] if topics else []
    used_ids: set = set()
    out: list[tuple[Difficulty, Topic, Problem]] = []
    for pos, difficulty in enumerate(want_diffs):
        want_topic = spread[pos] if spread else None
        candidates = [
            p
            for p in pool
            if p.difficulty == difficulty
            and (want_topic is None or p.topic == want_topic)
            and p.id not in used_ids
        ]
        if not candidates:
            candidates = [
                p
                for p in pool
                if p.difficulty == difficulty and p.topic in topics and p.id not in used_ids
            ]
        if not candidates:
            # Fall back to any topic for this difficulty before failing, so a
            # narrow topic selection with few Hards still builds a test.
            candidates = [
                p
                for p in pool
                if p.difficulty == difficulty and p.id not in used_ids
            ]
        if not candidates:
            raise TopicPoolEmptyError(topics[0] if topics else Topic.ARRAY, difficulty)
        chosen = rng.choice(candidates)
        used_ids.add(chosen.id)
        out.append((difficulty, chosen.topic, chosen))
    return out
