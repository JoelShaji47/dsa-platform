import uuid

from pydantic import BaseModel, Field

from app.models.enums import Language, SubmissionStatus


class SubmitPayload(BaseModel):
    language: Language
    source_code: str = Field(min_length=1)


class TestResultOut(BaseModel):
    index: int
    passed: bool


class VisibleTestResult(TestResultOut):
    input: str
    expected_output: str
    actual_output: str | None
    status_key: str


class RunResultOut(BaseModel):
    status: SubmissionStatus
    runtime_ms: float
    memory_kb: float
    test_results: list[VisibleTestResult]


class SubmissionResultOut(BaseModel):
    submission_id: uuid.UUID
    status: SubmissionStatus
    runtime_ms: float
    memory_kb: float
    xp_awarded: int
    xp_forfeited: bool = False
    user_xp: int
    current_streak: int
    new_badges: list[str] = []
    test_results: list[TestResultOut]
