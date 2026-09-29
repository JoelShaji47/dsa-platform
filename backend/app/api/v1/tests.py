import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import Difficulty, Language, SubmissionStatus, TestStatus, Topic
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.test_session import TestProblem, TestSession
from app.models.user import User
from app.schemas.submission import RunResultOut, SubmitTestResult
from app.schemas.test import (
    CreateTestPayload,
    DraftPayload,
    TestConfigOut,
    TestProblemOut,
    TestResultsOut,
    TestResultItem,
    TestSessionOut,
    TestSubmitOut,
    TopicAvailability,
)
from app.services.grader import RUN_VISIBLE_CASE_LIMIT, grade_code
from app.services.judge0 import Judge0Error
from app.services.sql_grader import SQLValidationError, grade_sql
from app.services.test_generator import (
    SLOTS,
    TopicPoolEmptyError,
    pick_test_problems,
    solvable_pool,
)

router = APIRouter(prefix="/tests", tags=["tests"])

DEFAULT_DURATION_SECONDS = 3600


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _grade_for_problem(
    problem: Problem, source_code: str, language: str, cases: list[dict]
):
    """Grade a timed-test attempt. SQL problems run through the SQLite
    harness; every other topic uses the Judge0 path unchanged."""
    if problem.topic == Topic.SQL and language == Language.SQL.value:
        try:
            return await grade_sql(source_code, cases)
        except SQLValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            )
    return await grade_code(source_code, language, cases)


def _remaining(session: TestSession) -> int:
    delta = (session.deadline_at - _now()).total_seconds()
    return int(max(0, min(delta, session.duration_seconds)))


def _get_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> TestSession:
    session = (
        db.query(TestSession)
        .filter(TestSession.id == session_id, TestSession.user_id == user_id)
        .first()
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test session not found"
        )
    return session


def _load_problems(db: Session, session_id: uuid.UUID) -> list[TestProblem]:
    return (
        db.query(TestProblem)
        .filter(TestProblem.session_id == session_id)
        .order_by(TestProblem.position)
        .all()
    )


def _get_question(db: Session, session_id: uuid.UUID, question_id: uuid.UUID) -> TestProblem:
    question = (
        db.query(TestProblem)
        .filter(
            TestProblem.id == question_id,
            TestProblem.session_id == session_id,
        )
        .first()
    )
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not in this test"
        )
    return question


def _finalize(db: Session, session: TestSession, final_status: TestStatus) -> TestSession:
    """Administrative cutoff. Reads recorded results only, never grades."""
    if session.status != TestStatus.IN_PROGRESS:
        return session
    session.status = final_status
    session.ended_at = _now()
    rows = _load_problems(db, session.id)
    passed = sum(1 for row in rows if row.passed is True)
    session.passed_count = passed
    session.score = passed
    start = session.started_at or session.created_at
    elapsed = int((session.ended_at - start).total_seconds())
    session.time_taken_seconds = max(0, min(elapsed, session.duration_seconds))
    db.flush()
    return session


def _require_active(db: Session, session: TestSession) -> TestSession:
    if session.status == TestStatus.IN_PROGRESS and _remaining(session) == 0:
        _finalize(db, session, TestStatus.EXPIRED)
        db.commit()
    if session.status != TestStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Test is no longer in progress"
        )
    return session


def _problem_out(question: TestProblem, problem: Problem) -> TestProblemOut:
    visible = [case for case in problem.test_cases if not case.get("is_hidden", False)]
    return TestProblemOut(
        id=question.id,
        problem_id=problem.id,
        slug=problem.slug,
        title=problem.title,
        description=problem.description or "",
        position=question.position,
        difficulty=question.difficulty,
        category=question.category,
        starter_code=problem.starter_code or {},
        test_cases=visible,
        hidden_test_count=len(problem.test_cases) - len(visible),
        code=question.code,
        language=question.language,
        attempts=question.attempts,
        status=question.status,
        passed=question.passed,
        runtime_ms=question.runtime_ms,
        memory_kb=question.memory_kb,
        submitted_at=(
            question.submitted_at.isoformat() if question.submitted_at else None
        ),
    )


def _session_out(db: Session, session: TestSession) -> TestSessionOut:
    rows = _load_problems(db, session.id)
    return TestSessionOut(
        id=session.id,
        status=session.status,
        topics=session.topics or [],
        assigned_topics=session.assigned_topics or [],
        duration_seconds=session.duration_seconds,
        started_at=session.started_at.isoformat(),
        deadline_at=session.deadline_at.isoformat(),
        time_remaining_seconds=_remaining(session),
        violations=session.violations,
        problems=[_problem_out(row, row.problem) for row in rows],
    )


@router.get("/config", response_model=TestConfigOut)
def get_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestConfigOut:
    """Topics are scanned from the database so a taxonomy change is additive."""
    counts: dict[tuple[Topic, Difficulty], int] = {
        (topic, difficulty): 0 for topic in Topic for difficulty in SLOTS
    }
    for problem in solvable_pool(db, list(Topic)):
        key = (problem.topic, problem.difficulty)
        if key in counts:
            counts[key] += 1

    return TestConfigOut(
        topics=[
            TopicAvailability(
                topic=topic,
                easy=counts[(topic, Difficulty.EASY)],
                medium=counts[(topic, Difficulty.MEDIUM)],
                hard=counts[(topic, Difficulty.HARD)],
                total=sum(counts[(topic, difficulty)] for difficulty in SLOTS),
            )
            for topic in Topic
        ],
        default_duration_seconds=DEFAULT_DURATION_SECONDS,
    )


@router.post("", response_model=TestSessionOut, status_code=status.HTTP_201_CREATED)
def create_test(
    payload: CreateTestPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestSessionOut:
    topics = list(dict.fromkeys(payload.topics))
    if not topics:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Select at least one category",
        )

    live = (
        db.query(TestSession)
        .filter(
            TestSession.user_id == current_user.id,
            TestSession.status == TestStatus.IN_PROGRESS,
        )
        .all()
    )
    for stale in live:
        still_running = _remaining(stale) > 0
        _finalize(
            db,
            stale,
            TestStatus.ABANDONED if still_running else TestStatus.EXPIRED,
        )

    try:
        picks = pick_test_problems(db, topics)
    except TopicPoolEmptyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    now = _now()
    session = TestSession(
        user_id=current_user.id,
        topics=[topic.value for topic in topics],
        assigned_topics=[category.value for _, category, _ in picks],
        duration_seconds=payload.duration_seconds,
        started_at=now,
        deadline_at=now + timedelta(seconds=payload.duration_seconds),
    )
    db.add(session)
    db.flush()
    for position, (difficulty, category, problem) in enumerate(picks, start=1):
        db.add(
            TestProblem(
                session_id=session.id,
                problem_id=problem.id,
                position=position,
                difficulty=difficulty,
                category=category,
            )
        )
    db.commit()
    db.refresh(session)
    return _session_out(db, session)


@router.get("/{session_id}", response_model=TestSessionOut)
def get_test_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestSessionOut:
    session = _get_session(db, session_id, current_user.id)
    if session.status == TestStatus.IN_PROGRESS and _remaining(session) == 0:
        _finalize(db, session, TestStatus.EXPIRED)
        db.commit()
    return _session_out(db, session)


@router.put("/{session_id}/questions/{question_id}/draft", response_model=TestSessionOut)
def save_draft(
    session_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: DraftPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestSessionOut:
    session = _require_active(db, _get_session(db, session_id, current_user.id))
    question = _get_question(db, session.id, question_id)
    question.code = payload.source_code
    question.language = payload.language.value
    db.commit()
    return _session_out(db, session)


@router.post(
    "/{session_id}/questions/{question_id}/run", response_model=RunResultOut
)
async def run_question(
    session_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: DraftPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunResultOut:
    session = _require_active(db, _get_session(db, session_id, current_user.id))
    question = _get_question(db, session.id, question_id)
    problem = question.problem

    question.code = payload.source_code
    question.language = payload.language.value
    db.commit()

    visible = [
        case
        for case in problem.test_cases
        if not case.get("is_hidden", False)
    ][:RUN_VISIBLE_CASE_LIMIT]
    try:
        result = await _grade_for_problem(
            problem, payload.source_code, payload.language.value, visible
        )
    except Judge0Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )

    return RunResultOut(
        status=result.status,
        runtime_ms=result.runtime_ms,
        memory_kb=result.memory_kb,
        test_results=[
            {
                "index": outcome.index,
                "passed": outcome.passed,
                "input": case.get("input", ""),
                "expected_output": case.get("expected_output", ""),
                "actual_output": outcome.actual_output,
                "stderr": outcome.stderr,
                "status_key": outcome.status_key,
            }
            for outcome, case in zip(result.test_results, visible)
        ],
    )


@router.post(
    "/{session_id}/questions/{question_id}/submit", response_model=TestSubmitOut
)
async def submit_question(
    session_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: DraftPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestSubmitOut:
    session = _require_active(db, _get_session(db, session_id, current_user.id))
    question = _get_question(db, session.id, question_id)
    problem = question.problem

    try:
        result = await _grade_for_problem(
            problem, payload.source_code, payload.language.value, problem.test_cases
        )
    except Judge0Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )

    cases = problem.test_cases or []
    submit_results: list[SubmitTestResult] = []
    for outcome in result.test_results:
        case = cases[outcome.index] if 0 <= outcome.index < len(cases) else {}
        hidden = bool(outcome.hidden or case.get("is_hidden", False))
        if hidden:
            submit_results.append(
                SubmitTestResult(
                    index=outcome.index,
                    passed=outcome.passed,
                    hidden=True,
                    status_key=outcome.status_key,
                )
            )
        else:
            submit_results.append(
                SubmitTestResult(
                    index=outcome.index,
                    passed=outcome.passed,
                    hidden=False,
                    status_key=outcome.status_key,
                    input=case.get("input"),
                    expected_output=case.get("expected_output"),
                    actual_output=outcome.actual_output,
                    stderr=outcome.stderr,
                )
            )

    submission = Submission(
        user_id=current_user.id,
        problem_id=problem.id,
        code=payload.source_code,
        language=payload.language.value,
        status=result.status,
        runtime_ms=result.runtime_ms,
        memory_kb=result.memory_kb,
        judge_summary=[row.model_dump() for row in submit_results],
        test_session_id=session.id,
        test_problem_id=question.id,
    )
    question.code = payload.source_code
    question.language = payload.language.value
    question.attempts += 1
    question.status = result.status
    question.passed = result.status == SubmissionStatus.ACCEPTED
    question.runtime_ms = result.runtime_ms
    question.memory_kb = result.memory_kb
    question.submitted_at = _now()
    db.add(submission)
    db.commit()

    return TestSubmitOut(
        problem_id=question.problem_id,
        status=question.status,
        passed=question.passed,
        attempts=question.attempts,
        runtime_ms=result.runtime_ms,
        memory_kb=result.memory_kb,
        test_results=submit_results,
    )


@router.post("/{session_id}/violations", response_model=TestSessionOut)
def report_violation(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestSessionOut:
    """Record a proctoring violation. The third one finalizes the test."""
    session = _require_active(db, _get_session(db, session_id, current_user.id))
    session.violations += 1
    if session.violations >= 3:
        _finalize(db, session, TestStatus.SUBMITTED)
    db.commit()
    return _session_out(db, session)


@router.post("/{session_id}/end", response_model=TestSessionOut)
def end_test(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestSessionOut:
    session = _get_session(db, session_id, current_user.id)
    if session.status == TestStatus.IN_PROGRESS:
        _finalize(db, session, TestStatus.SUBMITTED)
        db.commit()
    return _session_out(db, session)


@router.post("/{session_id}/abandon", status_code=status.HTTP_204_NO_CONTENT)
def abandon_test(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    session = _get_session(db, session_id, current_user.id)
    if session.status == TestStatus.IN_PROGRESS:
        session.status = TestStatus.ABANDONED
        session.ended_at = _now()
        db.commit()


@router.get("/{session_id}/results", response_model=TestResultsOut)
def get_results(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestResultsOut:
    session = _get_session(db, session_id, current_user.id)
    if session.status == TestStatus.IN_PROGRESS and _remaining(session) == 0:
        _finalize(db, session, TestStatus.EXPIRED)
        db.commit()
    if session.status not in (TestStatus.SUBMITTED, TestStatus.EXPIRED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Test has no results yet"
        )

    rows = _load_problems(db, session.id)
    return TestResultsOut(
        id=session.id,
        status=session.status,
        score=session.score or 0,
        passed_count=session.passed_count or 0,
        total=len(rows),
        time_taken_seconds=session.time_taken_seconds or 0,
        topics=session.topics or [],
        assigned_topics=session.assigned_topics or [],
        started_at=session.started_at.isoformat(),
        ended_at=session.ended_at.isoformat() if session.ended_at else None,
        results=[
            TestResultItem(
                position=row.position,
                slug=row.problem.slug,
                title=row.problem.title,
                difficulty=row.difficulty,
                category=row.category,
                passed=row.passed is True,
                status=row.status,
                attempts=row.attempts,
                runtime_ms=row.runtime_ms,
                memory_kb=row.memory_kb,
            )
            for row in rows
        ],
    )
