"""Interaction telemetry for the recommender.

Thin helper — API routes call log_event() alongside their main write so every
run / submit / hint / review is captured with a timestamp. Telemetry must never
break the request it annotates, so failures are swallowed after a rollback.
"""

from sqlalchemy.orm import Session

from app.models.interaction import InteractionEvent

RUN = "run"
SUBMIT = "submit"
HINT = "hint"
REVIEW = "review"
CHAT = "chat"
OPEN = "open"
# Timed-test submissions are their own signal: they are graded under a clock,
# so they must not be mixed with practice attempts when modelling ability.
TEST_SUBMIT = "test_submit"


def failure_summary(outcomes) -> dict:
    """Compact failure signature for event meta.

    Stores only the Judge0 status keys and a count — never the failing input,
    expected output or submitted source. Returns ``first_failure=None`` for a
    clean run so "passed" and "failed with no status" stay distinguishable.
    """
    failed = [o for o in outcomes if not getattr(o, "passed", True)]
    if not failed:
        return {"failed_cases": 0, "first_failure": None}
    first = next(
        (getattr(o, "status_key", "") for o in failed if getattr(o, "status_key", "")),
        None,
    )
    return {"failed_cases": len(failed), "first_failure": first}


def log_event(
    db: Session,
    *,
    user_id,
    problem_id,
    event: str,
    meta: dict | None = None,
) -> None:
    try:
        db.add(
            InteractionEvent(
                user_id=user_id,
                problem_id=problem_id,
                event=event,
                meta=meta or {},
            )
        )
        db.commit()
    except Exception:
        db.rollback()
