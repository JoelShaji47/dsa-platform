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
        "SQL",
    ]
    # Optional roadmap category (NeetCode pattern key/name). Only present in the
    # NeetCode 150 catalog seed; coarse `topic` remains the DB-level classification.
    category: str | None = None
    # Description is required for new fully-authored problems, but catalog-only
    # entries may omit it (seed keeps any existing authored description).
    description: str | None = Field(default=None, min_length=50)
    # Catalog-only problems have no runnable content yet.
    starter_code: dict[Literal["python", "cpp", "java", "sql"], str] = Field(default_factory=dict)
    test_cases: list[TestCase] = Field(default_factory=list)
    # Function mode (LeetCode-style): solve() stub per language + hidden driver
    # {"prefix": ..., "suffix": ...} wrapped around user code at grade time.
    function_starter: dict[Literal["python", "cpp", "java", "sql"], str] = Field(default_factory=dict)
    function_driver: dict = Field(default_factory=dict)
    # Multi-source provenance (e.g. ["neetcode", "tuf"]). Empty means "backfill
    # from the roadmap map / default to neetcode" in scripts/seed.py.
    sources: list[str] = Field(default_factory=list)
    pattern_key: str | None = None
    companies: list[str] = Field(default_factory=list)
    editorial_url: str | None = None
    video_url: str | None = None

    def visible_tests(self) -> list[TestCase]:
        return [t for t in self.test_cases if not t.is_hidden]
