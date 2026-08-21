import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Difficulty, SubmissionStatus, Topic


class Bucket(BaseModel):
    solved: int
    total: int


class RecentSubmissionOut(BaseModel):
    id: uuid.UUID
    problem_title: str
    problem_slug: str
    status: SubmissionStatus
    language: str
    runtime_ms: float | None
    submitted_at: datetime


class StatsOut(BaseModel):
    xp: int
    current_streak: int
    total_solved: int
    total_submissions: int
    acceptance_rate: float
    solved_by_difficulty: dict[Difficulty, Bucket]
    solved_by_topic: dict[Topic, Bucket]
    recent_submissions: list[RecentSubmissionOut]


class BadgeOut(BaseModel):
    criteria: str
    name: str
    description: str
    earned: bool
    earned_at: datetime | None
