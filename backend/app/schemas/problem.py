import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import Difficulty, Topic


class ProblemListItem(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    difficulty: Difficulty
    topic: Topic
    solved: bool
    solvable: bool = False
    sources: list[str] = []
    pattern_key: str | None = None


class TestCaseOut(BaseModel):
    input: str
    expected_output: str


class ApproachOut(BaseModel):
    """One rung of the solution ladder, cheapest approach first."""

    name: str
    idea: str
    time_complexity: str
    space_complexity: str
    tradeoff: str | None = None
    # Visualizer registry key when this rung has a step-by-step trace.
    trace_key: str | None = None


class ProblemDetail(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str
    difficulty: Difficulty
    topic: Topic
    starter_code: dict[str, Any]
    test_cases: list[TestCaseOut]
    solvable: bool = False
    solved: bool
    # Languages with LeetCode-style function mode (solve() stub + hidden driver).
    function_modes: list[str] = []
    # solve() stubs per language (drivers stay server-side).
    function_starter: dict[str, Any] = {}
    hidden_test_count: int = 0
    sources: list[str] = []
    pattern_key: str | None = None
    companies: list[str] = []
    editorial_url: str | None = None
    video_url: str | None = None
    # Ordered solution ladder (brute force -> optimal). Empty when unauthored.
    approaches: list[ApproachOut] = []
