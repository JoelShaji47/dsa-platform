import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class League(Base):
    """One weekly cohort. Cohorts are ≤30 users of the same tier, ordered by
    prior-week XP so similarly active learners race each other."""

    __tablename__ = "leagues"
    __table_args__ = (Index("ix_leagues_week", "week_start"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    week_start: Mapped[date] = mapped_column(Date)
    tier: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class LeagueMember(Base):
    """Season history: final rank/xp/movement (+1 promoted, 0 held, -1 relegated)."""

    __tablename__ = "league_members"
    __table_args__ = (
        Index("ix_league_members_league", "league_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    league_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leagues.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    final_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_xp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    movement: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
