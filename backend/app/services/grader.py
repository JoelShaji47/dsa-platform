import asyncio
from dataclasses import dataclass, field

from app.models.enums import SubmissionStatus
from app.services.judge0 import Judge0Error, submit

MAX_OUTPUT_CHARS = 10_000

RUN_VISIBLE_CASE_LIMIT = 3


@dataclass
class TestOutcome:
    index: int
    hidden: bool
    passed: bool = False
    status: SubmissionStatus | None = None
    status_key: str = ""
    runtime_ms: float = 0.0
    memory_kb: float = 0.0
    input: str = ""
    expected_output: str = ""
    actual_output: str | None = None
    stderr: str | None = None


@dataclass
class GradeResult:
    status: SubmissionStatus
    test_results: list[TestOutcome] = field(default_factory=list)

    @property
    def runtime_ms(self) -> float:
        return max((t.runtime_ms for t in self.test_results), default=0.0)

    @property
    def memory_kb(self) -> float:
        return max((t.memory_kb for t in self.test_results), default=0.0)


def normalize_output(text: str | None) -> str:
    if text is None:
        return ""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def truncate_output(text: str | None) -> str | None:
    if text is None or len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + "\n... (output truncated)"


def _execution_status(status_key: str) -> SubmissionStatus | None:
    if status_key == "ACCEPTED":
        return None
    if status_key == "COMPILATION_ERROR":
        return SubmissionStatus.COMPILATION_ERROR
    if status_key == "TIME_LIMIT_EXCEEDED":
        return SubmissionStatus.TLE
    return SubmissionStatus.RUNTIME_ERROR


async def _run_test(source_code: str, language: str, index: int, case: dict) -> TestOutcome:
    outcome = TestOutcome(
        index=index,
        hidden=bool(case.get("is_hidden", False)),
        input=case["input"],
        expected_output=case["expected_output"],
    )
    result = await submit(source_code, language, stdin=case["input"])
    outcome.status_key = result.get("status_key", "UNKNOWN")
    outcome.runtime_ms = float(result.get("time") or 0) * 1000
    outcome.memory_kb = float(result.get("memory") or 0)

    execution_status = _execution_status(outcome.status_key)
    if execution_status is not None:
        outcome.status = execution_status
        if execution_status == SubmissionStatus.COMPILATION_ERROR:
            outcome.stderr = truncate_output(result.get("compile_output"))
        else:
            outcome.stderr = truncate_output(
                result.get("stderr") or result.get("compile_output")
            )
        outcome.actual_output = truncate_output(result.get("stdout"))
        return outcome

    outcome.actual_output = truncate_output(result.get("stdout"))
    outcome.passed = normalize_output(result.get("stdout")) == normalize_output(
        case["expected_output"]
    )
    return outcome


def _aggregate(outcomes: list[TestOutcome]) -> SubmissionStatus:
    statuses = {o.status for o in outcomes}
    if SubmissionStatus.COMPILATION_ERROR in statuses:
        return SubmissionStatus.COMPILATION_ERROR
    if any(o.status_key == "TIME_LIMIT_EXCEEDED" for o in outcomes):
        return SubmissionStatus.TLE
    if SubmissionStatus.RUNTIME_ERROR in statuses:
        return SubmissionStatus.RUNTIME_ERROR
    if all(o.passed for o in outcomes):
        return SubmissionStatus.ACCEPTED
    return SubmissionStatus.WRONG_ANSWER


async def grade_code(
    source_code: str, language: str, test_cases: list[dict]
) -> GradeResult:
    if not test_cases:
        raise Judge0Error("Problem has no test cases")

    outcomes = await asyncio.gather(
        *(_run_test(source_code, language, i, case) for i, case in enumerate(test_cases))
    )
    return GradeResult(status=_aggregate(list(outcomes)), test_results=list(outcomes))
