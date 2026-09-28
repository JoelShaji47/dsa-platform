import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
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
from app.models.enums import Difficulty, SubmissionStatus, TestStatus, Topic
from app.models.problem import Problem
from app.models.user import User


class TestSession(Base):
    __tablename__ = "test_sessions"
    __table_args__ = (Index("ix_test_sessions_user_status", "user_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    status: Mapped[TestStatus] = mapped_column(
        Enum(TestStatus, name="test_status", validate_strings=True),
        server_default=TestStatus.IN_PROGRESS.value,
    )
    topics: Mapped[list] = mapped_column(JSONB, default=list, server_default=text("'[]'::jsonb"))
    assigned_topics: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer, server_default=text(str(3600))
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passed_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship()
    problems: Mapped[list["TestProblem"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="TestProblem.position",
    )


class TestProblem(Base):
    __tablename__ = "test_problems"
    __table_args__ = (
        UniqueConstraint("session_id", "position", name="uq_test_problem_position"),
        UniqueConstraint("session_id", "difficulty", name="uq_test_problem_difficulty"),
        UniqueConstraint("session_id", "problem_id", name="uq_test_problem_problem"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("test_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE")
    )
    position: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="difficulty", validate_strings=True)
    )
    category: Mapped[Topic] = mapped_column(
        Enum(Topic, name="topic", validate_strings=True)
    )
    code: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    status: Mapped[SubmissionStatus | None] = mapped_column(
        Enum(SubmissionStatus, name="submission_status", validate_strings=True),
        nullable=True,
    )
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    runtime_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_kb: Mapped[float | None] = mapped_column(Float, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    session: Mapped["TestSession"] = relationship(back_populates="problems")
    problem: Mapped["Problem"] = relationship()
