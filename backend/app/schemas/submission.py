import uuid

from typing import Literal

from pydantic import BaseModel, Field

from app.models.enums import Language, SubmissionStatus


class SubmitPayload(BaseModel):
    language: Language
    source_code: str = Field(min_length=1)
    mode: Literal["main", "function"] = "main"


class CustomRunPayload(BaseModel):
    """User-supplied stdin for an exploratory run (never graded or stored)."""

    language: Language
    source_code: str = Field(min_length=1)
    stdin: str = ""


class CustomRunOut(BaseModel):
    status_key: str
    status: SubmissionStatus | None = None
    stdout: str | None = None
    stderr: str | None = None
    compile_output: str | None = None
    runtime_ms: float
    memory_kb: float


class TestResultOut(BaseModel):
    index: int
    passed: bool


class VisibleTestResult(TestResultOut):
    input: str
    expected_output: str
    actual_output: str | None
    stderr: str | None = None
    status_key: str


class RunResultOut(BaseModel):
    status: SubmissionStatus
    runtime_ms: float
    memory_kb: float
    test_results: list[VisibleTestResult]


class SubmitTestResult(BaseModel):
    """Per-test submit feedback.

    Visible cases carry the full diff context (input/expected/actual) so the
    client can show *why* a submission failed. Hidden cases expose only the
    pass flag plus the judge status key (e.g. TIME_LIMIT_EXCEEDED) — their
    inputs and expected outputs never leave the server.
    """

    index: int
    passed: bool
    hidden: bool = False
    status_key: str = ""
    input: str | None = None
    expected_output: str | None = None
    actual_output: str | None = None
    stderr: str | None = None


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
    test_results: list[SubmitTestResult]


class SubmissionHistoryItem(BaseModel):
    submission_id: uuid.UUID
    status: SubmissionStatus
    language: str
    code: str
    runtime_ms: float | None = None
    memory_kb: float | None = None
    judge_summary: list[dict] | None = None
    submitted_at: str
