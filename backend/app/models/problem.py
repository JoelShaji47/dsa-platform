import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Difficulty, Topic

if TYPE_CHECKING:
    from app.models.submission import Submission


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="difficulty", validate_strings=True)
    )
    topic: Mapped[Topic] = mapped_column(Enum(Topic, name="topic", validate_strings=True))
    starter_code: Mapped[dict] = mapped_column(JSONB)
    test_cases: Mapped[list] = mapped_column(JSONB)
    # Function mode (LeetCode-style): per-language solve() stub shown in the
    # editor plus hidden driver {prefix, suffix} wrapped around user code at
    # grade time. Empty dicts = main-mode only.
    function_starter: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    function_driver: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    # Multi-source catalog provenance: which sheets list this problem
    # (e.g. ["neetcode", "tuf"]), roadmap pattern key, frequent companies,
    # and editorial/video links.
    sources: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    pattern_key: Mapped[str | None] = mapped_column(
        String(60), nullable=True, index=True
    )
    companies: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    editorial_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Ordered solution ladder (cheapest first): idea, complexity, and the
    # visualizer key that animates the step when a trace exists.
    approaches: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    # Published gate: unpublished problems are invisible in library/roadmap/
    # solve (admin preview only). Seeds always write True.
    is_published: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("true")
    )
    # Learned IRT difficulty logit (Layer 1 student model). NULL until the
    # problem has been graded at least once, in which case the difficulty
    # band prior is used instead. ``difficulty_n`` counts observations.
    difficulty_b: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty_n: Mapped[int] = mapped_column(
        Integer, default=0, server_default=text("0"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    submissions: Mapped[list["Submission"]] = relationship(back_populates="problem")
