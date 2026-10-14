import uuid
from datetime import datetime

from sqlalchemy import (
    CHAR,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CustomRoadmap(Base):
    __tablename__ = "custom_roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200), default="My roadmap")
    kind: Mapped[str] = mapped_column(String(30), default="dsa_build")
    level: Mapped[str] = mapped_column(String(30), default="basics")
    goal: Mapped[str] = mapped_column(String(30), default="fundamentals")
    company: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mins_per_day: Mapped[int] = mapped_column(Integer, default=60)
    total_days: Mapped[int] = mapped_column(Integer, default=21)
    target_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    share_code: Mapped[str] = mapped_column(CHAR(6), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    steps: Mapped[list["CustomRoadmapStep"]] = relationship(
        back_populates="roadmap", cascade="all, delete-orphan",
        order_by="CustomRoadmapStep.position",
    )
    members: Mapped[list["CustomRoadmapMember"]] = relationship(
        back_populates="roadmap", cascade="all, delete-orphan"
    )


class CustomRoadmapStep(Base):
    __tablename__ = "custom_roadmap_steps"
    __table_args__ = (
        UniqueConstraint("roadmap_id", "position", name="uq_custom_step_position"),
        Index("ix_custom_steps_roadmap_day", "roadmap_id", "day_index"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("custom_roadmaps.id", ondelete="CASCADE"),
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer)
    problem_slug: Mapped[str | None] = mapped_column(String(220), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    kind: Mapped[str] = mapped_column(String(20), default="problem")
    pattern_key: Mapped[str | None] = mapped_column(String(60), nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    est_mins: Mapped[int] = mapped_column(Integer, default=45)
    day_index: Mapped[int] = mapped_column(Integer, default=1)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, server_default=text("'{}'::jsonb"))

    roadmap: Mapped["CustomRoadmap"] = relationship(back_populates="steps")


class CustomRoadmapMember(Base):
    __tablename__ = "custom_roadmap_members"

    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("custom_roadmaps.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    roadmap: Mapped["CustomRoadmap"] = relationship(back_populates="members")


class CustomRoadmapTick(Base):
    __tablename__ = "custom_roadmap_ticks"

    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("custom_roadmap_steps.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    done_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CustomRoadmapGeneration(Base):
    """Append-only log for the 2-per-rolling-7-days rate limit."""

    __tablename__ = "custom_roadmap_generations"
    __table_args__ = (
        Index("ix_custom_generations_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
