import json

from sqlalchemy.orm import Session

from app.models.enums import SubmissionStatus
from app.models.problem import Problem
from app.models.submission import Submission
from app.services import gemini

HINT_LEVELS = 3

HINT_LEVEL_META = {
    1: ("Nudge", "a gentle intuition push"),
    2: ("Approach", "the algorithmic direction to consider"),
    3: ("Sketch", "a pseudocode-level plan, still short of real code"),
}

STATUS_LABELS = {
    SubmissionStatus.WRONG_ANSWER: "Wrong Answer",
    SubmissionStatus.TLE: "Time Limit Exceeded",
    SubmissionStatus.RUNTIME_ERROR: "Runtime Error",
    SubmissionStatus.COMPILATION_ERROR: "Compilation Error",
}


def hint_prompt(problem: Problem, level: int) -> str:
    _, intent = HINT_LEVEL_META[level]
    return (
        f"Problem: {problem.title}\n"
        f"Difficulty: {problem.difficulty.value}\n"
        f"Topic: {problem.topic.value}\n\n"
        f"{problem.description}\n\n"
        f"Give the student {intent} for this problem. "
        "Keep it under 120 words, use markdown. "
        "Never write out a full working implementation or reveal exact solutions."
    )


def get_or_create_hint(db: Session, problem: Problem, level: int) -> tuple[str, bool]:
    from app.models.hint import ProblemHint

    cached = (
        db.query(ProblemHint)
        .filter(ProblemHint.problem_id == problem.id, ProblemHint.level == level)
        .first()
    )
    if cached is not None:
        return cached.content, False

    content = gemini.generate_sync(hint_prompt(problem, level))
    row = ProblemHint(
        problem_id=problem.id,
        level=level,
        content=content,
        model=gemini.model_name(),
    )
    db.add(row)
    db.commit()
    return content, True


def has_used_hints(db: Session, user_id, problem_id) -> bool:
    from app.models.hint import HintUsage

    return (
        db.query(HintUsage.id)
        .filter(
            HintUsage.user_id == user_id,
            HintUsage.problem_id == problem_id,
        )
        .first()
        is not None
    )


def record_hint_usage(db: Session, user_id, problem_id, level: int) -> None:
    from app.models.hint import HintUsage

    exists = (
        db.query(HintUsage.id)
        .filter(
            HintUsage.user_id == user_id,
            HintUsage.problem_id == problem_id,
            HintUsage.level == level,
        )
        .first()
    )
    if exists is None:
        db.add(HintUsage(user_id=user_id, problem_id=problem_id, level=level))
        db.commit()


def _failing_case_lines(problem: Problem, result: dict) -> str:
    lines = []
    cases = problem.test_cases
    for outcome in result.get("test_results", []):
        if outcome.get("passed", False):
            continue
        index = outcome["index"]
        if index >= len(cases):
            continue
        case = cases[index]
        if case.get("is_hidden", False):
            lines.append(f"- Hidden test #{index + 1} failed (its input is secret).")
            continue
        actual = (outcome.get("actual_output") or "(no output)").strip()
        lines.append(
            f"- Failing visible test #{index + 1}:\n"
            f"  Input:\n```\n{case['input'].strip()}\n```\n"
            f"  Expected:\n```\n{case['expected_output'].strip()}\n```\n"
            f"  Got:\n```\n{actual[:2000]}\n```"
        )
    return "\n".join(lines) or "- No per-test details available."


def review_prompt(submission: Submission, problem: Problem, result: dict) -> str:
    label = STATUS_LABELS.get(submission.status, submission.status.value)
    return (
        f"A student's solution to the problem below was rejected by the judge.\n\n"
        f"Problem: {problem.title} ({problem.difficulty.value}, {problem.topic.value})\n"
        f"Language: {submission.language}\n"
        f"Verdict: {label}\n\n"
        f"{problem.description}\n\n"
        f"Judge details:\n{_failing_case_lines(problem, result)}\n\n"
        f"Their code:\n"
        f"```{'python' if submission.language == 'python' else submission.language}\n"
        f"{submission.code[:8000]}\n"
        f"```\n\n"
        "Respond with ONLY a JSON object using exactly these keys:\n"
        '{"verdict": "<one-sentence diagnosis>", '
        '"bug_type": "<short category like off-by-one, edge-case, wrong-algorithm, '
        'infinite-loop, io-format, complexity>", '
        '"explanation": "<markdown, why it fails, reference the failing evidence>", '
        '"fix_hint": "<markdown, how to fix it without handing over the full solution>"}'
    )


def parse_review_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        cleaned = cleaned[first_newline + 1 :] if first_newline != -1 else cleaned
        end = cleaned.rfind("```")
        if end != -1:
            cleaned = cleaned[:end]
    data = json.loads(cleaned.strip())
    keys = ("verdict", "bug_type", "explanation", "fix_hint")
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"review JSON missing keys: {missing}")
    return {key: str(data[key]) for key in keys}


def build_failure_review(db: Session, submission: Submission, problem: Problem, result: dict) -> dict:
    raw = gemini.generate_sync(review_prompt(submission, problem, result), json_mode=True)
    review = parse_review_json(raw)
    submission.ai_review = review
    db.commit()
    return review
