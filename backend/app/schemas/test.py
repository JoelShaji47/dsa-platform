import uuid

from pydantic import BaseModel, Field

from app.models.enums import Difficulty, Language, SubmissionStatus, TestStatus, Topic
from app.schemas.submission import RunResultOut, SubmitTestResult

__all__ = [
    "CreateTestPayload",
    "DraftPayload",
    "RunResultOut",
    "TestConfigOut",
    "TestProblemOut",
    "TestResultItem",
    "TestResultsOut",
    "TestSessionOut",
    "TestSubmitOut",
    "TopicAvailability",
]


class TopicAvailability(BaseModel):
    topic: Topic
    easy: int
    medium: int
    hard: int
    total: int


class TestConfigOut(BaseModel):
    topics: list[TopicAvailability]
    default_duration_seconds: int


class CreateTestPayload(BaseModel):
    topics: list[Topic] = Field(min_length=1)
    duration_seconds: int = Field(default=3600, ge=60, le=7200)


class DraftPayload(BaseModel):
    language: Language
    source_code: str = Field(min_length=1)


class TestProblemOut(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    slug: str
    title: str
    description: str
    position: int
    difficulty: Difficulty
    category: Topic
    starter_code: dict
    test_cases: list[dict]
    hidden_test_count: int
    code: str | None = None
    language: Language | None = None
    attempts: int = 0
    status: SubmissionStatus | None = None
    passed: bool | None = None
    runtime_ms: float | None = None
    memory_kb: float | None = None
    submitted_at: str | None = None


class TestSessionOut(BaseModel):
    id: uuid.UUID
    status: TestStatus
    topics: list[Topic]
    assigned_topics: list[Topic]
    duration_seconds: int
    started_at: str
    deadline_at: str
    time_remaining_seconds: int
    violations: int = 0
    problems: list[TestProblemOut]


class TestSubmitOut(BaseModel):
    problem_id: uuid.UUID
    status: SubmissionStatus
    passed: bool
    attempts: int
    runtime_ms: float
    memory_kb: float
    test_results: list[SubmitTestResult]


class TestResultItem(BaseModel):
    position: int
    slug: str
    title: str
    difficulty: Difficulty
    category: Topic
    passed: bool
    status: SubmissionStatus | None = None
    attempts: int = 0
    runtime_ms: float | None = None
    memory_kb: float | None = None


class TestResultsOut(BaseModel):
    id: uuid.UUID
    status: TestStatus
    score: int
    passed_count: int
    total: int
    time_taken_seconds: int
    violations: int = 0
    topics: list[Topic]
    assigned_topics: list[Topic]
    started_at: str
    ended_at: str | None = None
    results: list[TestResultItem]
