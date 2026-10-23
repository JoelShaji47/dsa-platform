import asyncio
from dataclasses import dataclass, field

from app.models.enums import SubmissionStatus
from app.services.judge0 import Judge0Error, submit

MAX_OUTPUT_CHARS = 10_000

RUN_VISIBLE_CASE_LIMIT = 3

# Wall-clock ceiling for a single test case. Judge0 runs with wait=true and a
# 5s CPU limit, so anything past this is stalled (or genuinely far too slow);
# that one case is recorded as a TLE instead of failing the whole submission.
DEFAULT_CASE_TIMEOUT_SECONDS = 25.0

# Cap in-flight Judge0 calls. A problem can carry dozens of cases, and firing
# them all at once can swamp a single self-hosted container (one Java box can
# reserve ~4 GB).
MAX_CONCURRENT_CASES = 8


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


class ModeError(Exception):
    pass


def function_modes_for(problem) -> list[str]:
    """Languages with a complete function-mode setup (stub + driver)."""
    starters = getattr(problem, "function_starter", None) or {}
    drivers = getattr(problem, "function_driver", None) or {}
    modes = []
    for lang, stub in starters.items():
        driver = drivers.get(lang) if isinstance(drivers, dict) else None
        if stub and isinstance(driver, dict) and driver.get("prefix") is not None and driver.get("suffix") is not None:
            modes.append(lang)
    return modes


def build_source(problem, language: str, code: str, mode: str) -> str:
    """Assemble the Judge0 source. Function mode wraps user code in the
    hidden driver; main mode passes code through unchanged."""
    if mode != "function":
        return code
    if language not in function_modes_for(problem):
        raise ModeError(f"Function mode is not available for {language} on this problem")
    driver = (problem.function_driver or {})[language]
    return f"{driver['prefix']}{code}\n{driver['suffix']}"


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
        input=case.get("input", ""),
        expected_output=case.get("expected_output", ""),
    )
    result = await submit(source_code, language, stdin=case.get("input", ""))
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
        case.get("expected_output", "")
    )
    return outcome


def _timeout_outcome(index: int, case: dict, timeout: float) -> TestOutcome:
    """Synthetic result for a case that outlived the client-side deadline.

    We never learned its real verdict, so it is reported as a TLE with an
    explanatory stderr — the honest reading for a case that ran past 25s under
    a 5s CPU limit. Crucially it keeps the *other* cases' results.
    """
    return TestOutcome(
        index=index,
        hidden=bool(case.get("is_hidden", False)),
        input=case.get("input", ""),
        expected_output=case.get("expected_output", ""),
        passed=False,
        status=SubmissionStatus.TLE,
        status_key="TIME_LIMIT_EXCEEDED",
        stderr=f"Test case did not finish within {timeout:.0f}s (client timeout).",
    )


async def _run_case(
    source_code: str,
    language: str,
    index: int,
    case: dict,
    timeout: float,
    semaphore: asyncio.Semaphore,
) -> TestOutcome:
    """Run one case under a concurrency cap and a wall-clock deadline.

    Only a *timeout* is absorbed here; real infrastructure problems (Judge0
    unreachable, 5xx) still raise Judge0Error so the route can answer 503.
    """
    async with semaphore:
        try:
            return await asyncio.wait_for(
                _run_test(source_code, language, index, case), timeout=timeout
            )
        except asyncio.TimeoutError:
            return _timeout_outcome(index, case, timeout)


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
    source_code: str,
    language: str,
    test_cases: list[dict],
    *,
    case_timeout: float | None = None,
) -> GradeResult:
    if not test_cases:
        raise Judge0Error("Problem has no test cases")

    timeout = DEFAULT_CASE_TIMEOUT_SECONDS if case_timeout is None else case_timeout
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CASES)
    outcomes = await asyncio.gather(
        *(
            _run_case(source_code, language, i, case, timeout, semaphore)
            for i, case in enumerate(test_cases)
        )
    )
    return GradeResult(status=_aggregate(list(outcomes)), test_results=list(outcomes))
