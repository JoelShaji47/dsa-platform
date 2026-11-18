from uuid import UUID

from pydantic import BaseModel, Field


class ImpressionItem(BaseModel):
    slug: str
    rank: int = Field(ge=0, le=1000)
    source: str = "roadmap"
    rendered: bool = True


class ImpressionsIn(BaseModel):
    opportunity_id: UUID
    items: list[ImpressionItem] = Field(max_length=50)


class SessionStartIn(BaseModel):
    problem_slug: str
    client_session_id: str = Field(min_length=1, max_length=60)
    opportunity_id: UUID | None = None


class SessionFinishIn(BaseModel):
    claimed_time_complexity: str | None = Field(default=None, max_length=20)
    claimed_space_complexity: str | None = Field(default=None, max_length=20)


def session_out(s) -> dict:
    return {
        "id": str(s.id),
        "problem_id": str(s.problem_id),
        "opportunity_id": str(s.opportunity_id) if s.opportunity_id else None,
        "status": s.status,
        "active_seconds": s.active_seconds,
        "heartbeat_count": s.heartbeat_count,
        "attempt_count": s.attempt_count,
        "hint_count": s.hint_count,
        "run_count": s.run_count,
        "review_count": s.review_count,
        "editorial_revealed": s.editorial_revealed,
        "first_accepted_at": s.first_accepted_at.isoformat() if s.first_accepted_at else None,
        "claimed_time_complexity": s.claimed_time_complexity,
        "claimed_space_complexity": s.claimed_space_complexity,
        "verified_time_complexity": s.verified_time_complexity,
        "verified_space_complexity": s.verified_space_complexity,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
    }
