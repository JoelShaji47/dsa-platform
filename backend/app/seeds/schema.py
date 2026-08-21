from typing import Literal

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False


class ProblemSeed(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", max_length=220)
    difficulty: Literal["EASY", "MEDIUM", "HARD"]
    topic: Literal[
        "ARRAY",
        "STRING",
        "LINKED_LIST",
        "STACK",
        "QUEUE",
        "TREE",
        "GRAPH",
        "DP",
    ]
    description: str = Field(min_length=50)
    starter_code: dict[Literal["python", "cpp", "java"], str]
    test_cases: list[TestCase] = Field(min_length=4)

    def visible_tests(self) -> list[TestCase]:
        return [t for t in self.test_cases if not t.is_hidden]
