import uuid

from pydantic import BaseModel, Field

from app.models.enums import Difficulty, Language, SubmissionStatus, TestStatus, Topic
from app.schemas.submission import RunResultOut, SubmitTestResult

__all__ = [
    "CreateTestPayload",
    "CustomCaseIn",
    "CustomCasesPayload",
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


DURATION_OPTIONS_SECONDS: list[int] = [900, 1800, 2700, 3600, 5400, 7200]
MAX_TEST_QUESTIONS: int = 6


class TestConfigOut(BaseModel):
    topics: list[TopicAvailability]
    default_duration_seconds: int
    duration_options_seconds: list[int] = DURATION_OPTIONS_SECONDS
    max_questions: int = MAX_TEST_QUESTIONS


class CreateTestPayload(BaseModel):
    topics: list[Topic] = Field(min_length=1)
    duration_seconds: int = Field(default=3600, ge=60, le=7200)
    # Custom question count (1..MAX). Defaults to the classic 3 (E/M/H).
    num_questions: int = Field(default=3, ge=1, le=MAX_TEST_QUESTIONS)
    # Fully custom question list: exact problem slugs in the requested order.
    # When provided, num_questions is ignored and len(problem_slugs) is used.
    problem_slugs: list[str] | None = Field(default=None, min_length=1, max_length=MAX_TEST_QUESTIONS)
    # Optional per-position difficulty override, e.g. ["EASY","EASY","MEDIUM"].
    # When provided its length must match the final question count.
    difficulties: list[Difficulty] | None = Field(default=None, min_length=1, max_length=MAX_TEST_QUESTIONS)


class DraftPayload(BaseModel):
    language: Language
    source_code: str = Field(min_length=1)


class CustomCaseIn(BaseModel):
    """One user-edited sample case (input stdin + expected stdout)."""

    input: str = ""
    expected_output: str = ""


class CustomCasesPayload(BaseModel):
    """Grade code against the user's own edited cases. Exploratory only —
    never stored, never scored, attempts untouched."""

    language: Language
    source_code: str = Field(min_length=1)
    test_cases: list[CustomCaseIn] = Field(min_length=1, max_length=10)


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
