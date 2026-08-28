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


class TestCaseOut(BaseModel):
    input: str
    expected_output: str


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
