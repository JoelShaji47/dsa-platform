"""Layer 1 student model: per-(user, pattern) ability estimates.

One row per (user, pattern) holding the Elo/IRT ability logit ``theta`` and the
number of graded observations ``n`` behind it. Problem difficulty is global,
so it lives on the problem row (``problems.difficulty_b`` / ``difficulty_n``)
rather than here.

The update rule, the hint partial-credit policy and the confidence formula are
in ``app.services.skill_model`` — this table is only the durable state.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class SkillEstimate(Base):
    __tablename__ = "skill_estimates"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "pattern_key", name="uq_skill_estimates_user_pattern"
        ),
        Index("ix_skill_estimates_user", "user_id"),
        Index("ix_skill_estimates_pattern", "pattern_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    pattern_key: Mapped[str] = mapped_column(String(60), nullable=False)
    # Ability logit: higher = stronger in this pattern.
    theta: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0", nullable=False
    )
    # Graded observations behind theta (drives the K decay and confidence).
    n: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship()
