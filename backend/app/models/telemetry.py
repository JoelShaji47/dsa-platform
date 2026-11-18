"""Recommendation telemetry: impressions and solve sessions (Phase B).

Privacy-conscious by design: no source code, keystrokes, secrets or personal
information is stored here — only ids, ranks, versions, counters and
timestamps needed to reconstruct recommendation opportunities and outcomes.

- ``RecommendationOpportunity``: one row per recommendation request served
  (the ranking query). Candidates actually rendered are logged by the client
  via ``POST /roadmap/impressions``; server-side generation alone is NOT an
  impression (A3/B1: distinguish generated vs exposed).
- ``RecommendationImpression``: one row per exposed (opportunity, problem)
  with displayed rank, source pool, model + feature-schema versions, plus
  explicit learner feedback (``clicked_at`` / ``dismissed_at``, first action
  wins). Unique (opportunity_id, problem_id) makes client retries idempotent.
- ``SolveSession``: one row per learner work session on a problem, linking
  work to submissions/hints/impressions. Counters reconcile against the
  canonical submission/hint records at finish time. Active seconds use a
  heartbeat model with an idle timeout — wall-clock duration is never
  reported as active time.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Heartbeat model: gaps longer than this count as idle, not solving.
IDLE_TIMEOUT_SECONDS = 120
# Claimed complexity strings are capped to keep the column abuse-proof.
MAX_COMPLEXITY_LEN = 20


class RecommendationOpportunity(Base):
    __tablename__ = "recommendation_opportunities"
    __table_args__ = (
        Index("ix_rec_opps_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    model_version: Mapped[str] = mapped_column(String(60))
    feature_schema_version: Mapped[int] = mapped_column(Integer, default=2)
    candidate_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RecommendationImpression(Base):
    __tablename__ = "recommendation_impressions"
    __table_args__ = (
        UniqueConstraint("opportunity_id", "problem_id", name="uq_impression_opp_problem"),
        Index("ix_impressions_user_created", "user_id", "created_at"),
        Index("ix_impressions_problem", "problem_id"),
        Index("ix_impressions_opportunity", "opportunity_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recommendation_opportunities.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), index=True
    )
    rank: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(30), default="roadmap")
    model_version: Mapped[str] = mapped_column(String(60))
    feature_schema_version: Mapped[int] = mapped_column(Integer, default=2)
    rendered: Mapped[bool] = mapped_column(Boolean, default=True)
    # Explicit learner feedback on the exposure. Both are NULL until the
    # learner acts; the first action wins (see telemetry.record_feedback), so
    # a row is never both clicked and dismissed. Kept off the feature matrix:
    # they happen after the ranking decision and would leak into training.
    clicked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dismissed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SolveSession(Base):
    __tablename__ = "solve_sessions"
    __table_args__ = (
        UniqueConstraint("user_id", "client_session_id", name="uq_session_user_client"),
        Index("ix_sessions_user_problem", "user_id", "problem_id"),
        Index("ix_sessions_created", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    # Client-generated idempotency key (retries re-send it; unique per user).
    client_session_id: Mapped[str] = mapped_column(String(60))
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), index=True
    )
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recommendation_opportunities.id", ondelete="SET NULL"),
        nullable=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    heartbeat_count: Mapped[int] = mapped_column(Integer, default=0)
    active_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    hint_count: Mapped[int] = mapped_column(Integer, default=0)
    run_count: Mapped[int] = mapped_column(Integer, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    editorial_revealed: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    first_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Self-reported complexity (learner's claim) — NEVER treated as verified.
    claimed_time_complexity: Mapped[str | None] = mapped_column(
        String(MAX_COMPLEXITY_LEN), nullable=True
    )
    claimed_space_complexity: Mapped[str | None] = mapped_column(
        String(MAX_COMPLEXITY_LEN), nullable=True
    )
    # Verified complexity stays NULL: this codebase has no reliable automated
    # assessment mechanism, and we do not infer Big-O from submitted code.
    verified_time_complexity: Mapped[str | None] = mapped_column(
        String(MAX_COMPLEXITY_LEN), nullable=True
    )
    verified_space_complexity: Mapped[str | None] = mapped_column(
        String(MAX_COMPLEXITY_LEN), nullable=True
    )
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


def estimate_active_seconds(
    heartbeats: list[datetime], idle_timeout_s: int = IDLE_TIMEOUT_SECONDS
) -> float:
    """Heartbeat active-time estimator (documented method).

    Sums inter-heartbeat gaps capped at ``idle_timeout_s``; gaps beyond the
    timeout (tab closed, network drop, refresh) contribute only the timeout
    value. Empty/single heartbeat -> 0.0. Deterministic and safe on
    duplicates (sorting + zero deltas contribute nothing).
    """
    if len(heartbeats) < 2:
        return 0.0
    ordered = sorted(
        h.replace(tzinfo=timezone.utc) if h.tzinfo is None else h
        for h in heartbeats
    )
    total = 0.0
    for prev, cur in zip(ordered, ordered[1:]):
        gap = (cur - prev).total_seconds()
        if gap < 0:
            continue
        total += min(gap, idle_timeout_s)
    return round(total, 1)
