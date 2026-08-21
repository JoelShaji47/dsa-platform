import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from pydantic import ValidationError
from sqlalchemy import text

from app.db.session import SessionLocal
from app.models.enums import Difficulty, Topic
from app.models.problem import Problem
from app.seeds import PROBLEMS
from app.seeds.schema import ProblemSeed
from app.services.gamification import ensure_badge_catalog


def main() -> None:
    validated = []
    for raw in PROBLEMS:
        try:
            validated.append(ProblemSeed.model_validate(raw))
        except ValidationError as exc:
            print(f"[FAIL] {raw.get('slug', 'unknown')}: {exc}")
            raise SystemExit(1)

    created = updated = 0
    with SessionLocal() as db:
        for seed in validated:
            payload = {
                "title": seed.title,
                "difficulty": Difficulty(seed.difficulty),
                "topic": Topic(seed.topic),
                "description": seed.description,
                "starter_code": seed.starter_code,
                "test_cases": [tc.model_dump() for tc in seed.test_cases],
            }
            problem = db.query(Problem).filter(Problem.slug == seed.slug).first()
            if problem is None:
                db.add(Problem(slug=seed.slug, **payload))
                created += 1
            else:
                for field, value in payload.items():
                    setattr(problem, field, value)
                updated += 1
        db.commit()

    with SessionLocal() as db:
        ensure_badge_catalog(db)
        badge_count = db.execute(text("SELECT count(*) FROM badges")).scalar()
    print(f"Badge catalog synced -> {badge_count} badges")
    print(f"Seeded {len(validated)} problems -> created={created} updated={updated}")


if __name__ == "__main__":
    main()
