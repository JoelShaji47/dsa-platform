import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InteractionEvent(Base):
    """Behavioral log feeding the recommender (Phase C).

    One row per meaningful learner action: code runs, submits, hint reveals
    and AI reviews. Aggregated by app/ml/features.py into per-(user, problem)
    training rows (attempts, hints, time-to-accept, ...).
    """

    __tablename__ = "interaction_events"
    __table_args__ = (
        Index("ix_events_user_problem", "user_id", "problem_id"),
        Index("ix_events_created", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE")
    )
    event: Mapped[str] = mapped_column(String(30))
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
