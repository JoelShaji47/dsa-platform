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
