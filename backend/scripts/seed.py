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
from app.services.roadmap import SLUG_TO_PATTERN
from app.seeds.global_arena_explanations import EXPLANATIONS
from app.seeds.global_arena_rules import normalize_problem

try:
    from app.seeds.data_tuf_a2z import TUF_A2Z_SLUGS
except ImportError:  # pragma: no cover - seed file always present in practice
    TUF_A2Z_SLUGS: set[str] = set()


def main() -> None:
    validated = []
    for raw in PROBLEMS:
        try:
            validated.append(ProblemSeed.model_validate(raw))
        except ValidationError as exc:
            print(f"[FAIL] {raw.get('slug', 'unknown')}: {exc}")
            raise SystemExit(1)

    created = updated = 0
    normalized = 0
    global_arena_warnings = []
    with SessionLocal() as db:
        for seed in validated:
            payload: dict = {
                "title": seed.title,
                "difficulty": Difficulty(seed.difficulty),
                "topic": Topic(seed.topic),
            }
            # Description / starter_code / test_cases are only applied when the seed
            # actually provides them. Catalog-only entries omit them so that existing
            # fully-authored problems are never clobbered.
            if seed.description is not None:
                payload["description"] = seed.description
            if seed.starter_code:
                payload["starter_code"] = seed.starter_code
            if seed.test_cases:
                payload["test_cases"] = [tc.model_dump() for tc in seed.test_cases]
            if seed.function_starter:
                payload["function_starter"] = seed.function_starter
            if seed.function_driver:
                payload["function_driver"] = seed.function_driver
            if seed.sources:
                payload["sources"] = list(seed.sources)
            if seed.pattern_key:
                payload["pattern_key"] = seed.pattern_key
            if seed.companies:
                payload["companies"] = list(seed.companies)
            if seed.editorial_url:
                payload["editorial_url"] = seed.editorial_url
            if seed.video_url:
                payload["video_url"] = seed.video_url

            # Global arena rules: exactly three visible test cases and exactly
            # two examples per problem. Applied at seed time so any database
            # reset produces the formatted catalog automatically.
            if (
                seed.slug in EXPLANATIONS
                and seed.description is not None
                and "## Example" in seed.description
                and seed.test_cases
            ):
                new_desc, new_cases, _ = normalize_problem(
                    seed.slug,
                    seed.description,
                    [tc.model_dump() for tc in seed.test_cases],
                    global_arena_warnings,
                )
                payload["description"] = new_desc
                payload["test_cases"] = new_cases
                normalized += 1

            problem = db.query(Problem).filter(Problem.slug == seed.slug).first()
            if problem is None:
                # Placeholder defaults for catalog-only rows that have no authored content.
                payload.setdefault("description", f"Practice: {seed.title}")
                payload.setdefault("starter_code", {})
                payload.setdefault("test_cases", [])
                # New rows publish immediately; admin unpublishes on existing
                # rows are never clobbered by re-seeds.
                payload["is_published"] = True
                problem = Problem(slug=seed.slug, **payload)
                db.add(problem)
                # The session runs with autoflush=False, so flush explicitly:
                # later sources reuse authored slugs (e.g. NeetCode 150 catalog
                # entries) and their existence check must see this row.
                db.flush()
                created += 1
            else:
                for field, value in payload.items():
                    setattr(problem, field, value)
                updated += 1
            # Backfill provenance without clobbering explicit values: every
            # current entry derives from the NeetCode curriculum unless the
            # seed says otherwise (e.g. sources=["tuf"]).
            if not (problem.sources or []):
                problem.sources = (
                    list(seed.sources) if seed.sources else ["neetcode"]
                )
            # Shared curriculum rows carry both sheets (e.g. two-sum lives in
            # NeetCode 150/250 and the A2Z Arrays step).
            if seed.slug in TUF_A2Z_SLUGS and "tuf" not in (problem.sources or []):
                problem.sources = [*(problem.sources or []), "tuf"]
            if not problem.pattern_key:
                problem.pattern_key = (
                    seed.pattern_key or SLUG_TO_PATTERN.get(seed.slug)
                )
        # Source-tag merge for shared rows: catalog entries that overlap with
        # the A2Z sheet are dropped from PROBLEMS by dedupe, so tag them here.
        if TUF_A2Z_SLUGS:
            shared = (
                db.query(Problem)
                .filter(Problem.slug.in_(sorted(TUF_A2Z_SLUGS)))
                .all()
            )
            for problem in shared:
                if "tuf" not in (problem.sources or []):
                    problem.sources = [*(problem.sources or []), "tuf"]
        db.commit()

    with SessionLocal() as db:
        ensure_badge_catalog(db)
        badge_count = db.execute(text("SELECT count(*) FROM badges")).scalar()
    print(f"Badge catalog synced -> {badge_count} badges")
    print(f"Seeded {len(validated)} problems -> created={created} updated={updated}")
    print(f"Global arena rules applied -> {normalized} problems")
    if global_arena_warnings:
        print(f"Global arena warnings ({len(global_arena_warnings)}):")
        for w in global_arena_warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
