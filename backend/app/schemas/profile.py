import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Difficulty, SubmissionStatus, TestStatus, Topic
from app.schemas.stats import BadgeOut


class ProfileUser(BaseModel):
    username: str
    xp: int
    current_streak: int
    league_tier: int
    league_name: str
    created_at: datetime


class SolvedCounts(BaseModel):
    easy: int
    medium: int
    hard: int
    total: int


class ActivityDay(BaseModel):
    date: str
    count: int


class ProfileSubmission(BaseModel):
    id: uuid.UUID
    problem_title: str
    problem_slug: str
    difficulty: Difficulty
    status: SubmissionStatus
    language: str
    runtime_ms: float | None
    submitted_at: datetime


class ProfileTestSummary(BaseModel):
    id: uuid.UUID
    status: TestStatus
    score: int
    passed_count: int
    total: int
    violations: int
    assigned_topics: list[Topic]
    started_at: datetime
    ended_at: datetime | None
    time_taken_seconds: int


class ProfileOut(BaseModel):
    user: ProfileUser
    solved: SolvedCounts
    total_tests: int
    activity: list[ActivityDay]
    submissions: list[ProfileSubmission]
    tests: list[ProfileTestSummary]
    badges: list[BadgeOut]
