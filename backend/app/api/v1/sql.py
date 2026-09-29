"""Standalone SQL track. Mirrors the DSA problems router but only ever serves
``Topic.SQL`` problems and only accepts ``Language.SQL`` submissions.

Execution reuses the DSA pipeline untouched: the query is wrapped in a
Python+SQLite harness (``app.services.sql_grader``) and graded by Judge0's
Python runtime via ``grade_code``. Submissions, XP, streaks and badges flow
through the same tables, so SQL solves count platform-wide exactly like DSA
solves; the DSA endpoints never see these problems.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import Difficulty, Language, SubmissionStatus, Topic
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.schemas.problem import ProblemDetail, ProblemListItem
from app.schemas.submission import (
    RunResultOut,
    SubmissionResultOut,
    SubmitPayload,
    SubmitTestResult,
    VisibleTestResult,
)
from app.services.activity import RUN, SUBMIT, log_event
from app.services.gamification import award_new_badges, award_xp, update_streak
from app.services.grader import RUN_VISIBLE_CASE_LIMIT
from app.services.judge0 import Judge0Error
from app.services.sql_grader import SQLValidationError, build_sql_source, grade_sql
from app.services.tutor import has_used_hints

router = APIRouter(prefix="/sql", tags=["sql"])


def _sql_problem_or_404(db: Session, slug: str) -> Problem:
    problem = (
        db.query(Problem)
        .filter(Problem.slug == slug, Problem.topic == Topic.SQL)
        .first()
    )
    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SQL problem not found",
        )
    return problem


def _require_sql(payload: SubmitPayload) -> None:
    if payload.language != Language.SQL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SQL problems only accept language 'sql'",
        )


def _visible_cases(problem: Problem) -> list[dict]:
    return [
        case
        for case in problem.test_cases
        if not case.get("is_hidden", False)
    ][:RUN_VISIBLE_CASE_LIMIT]


def _solved_problem_ids(db: Session, user_id) -> set:
    rows = (
        db.query(Submission.problem_id)
        .filter(
            Submission.user_id == user_id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
        )
        .distinct()
        .all()
    )
    return {row[0] for row in rows}


@router.get("", response_model=list[ProblemListItem])
def list_sql_problems(
    difficulty: Difficulty | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProblemListItem]:
    query = db.query(Problem).filter(Problem.topic == Topic.SQL)
    if difficulty is not None:
        query = query.filter(Problem.difficulty == difficulty)
    if search:
        query = query.filter(Problem.title.ilike(f"%{search}%"))

    solved_ids = _solved_problem_ids(db, current_user.id)
    problems = query.order_by(Problem.difficulty, Problem.title).all()
    return [
        ProblemListItem(
            id=p.id,
            title=p.title,
            slug=p.slug,
            difficulty=p.difficulty,
            topic=p.topic,
            solved=p.id in solved_ids,
            solvable=bool(p.starter_code and p.test_cases),
            sources=p.sources or [],
            pattern_key=p.pattern_key,
        )
        for p in problems
    ]


@router.get("/{slug}", response_model=ProblemDetail)
def get_sql_problem(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProblemDetail:
    problem = _sql_problem_or_404(db, slug)
    solved_ids = _solved_problem_ids(db, current_user.id)
    visible_cases = [
        case for case in problem.test_cases if not case.get("is_hidden", False)
    ]
    return ProblemDetail(
        id=problem.id,
        title=problem.title,
        slug=problem.slug,
        description=problem.description,
        difficulty=problem.difficulty,
        topic=problem.topic,
        starter_code=problem.starter_code,
        test_cases=visible_cases,
        solvable=bool(problem.starter_code and problem.test_cases),
        solved=problem.id in solved_ids,
        hidden_test_count=sum(
            1 for case in problem.test_cases if case.get("is_hidden", False)
        ),
        sources=problem.sources or [],
        pattern_key=problem.pattern_key,
        companies=problem.companies or [],
        editorial_url=problem.editorial_url,
        video_url=problem.video_url,
        function_modes=[],
        function_starter={},
    )


@router.post("/{slug}/run", response_model=RunResultOut)
async def run_sql(
    slug: str,
    payload: SubmitPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunResultOut:
    problem = _sql_problem_or_404(db, slug)
    _require_sql(payload)
    try:
        build_sql_source(payload.source_code)
    except SQLValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
    visible_cases = _visible_cases(problem)

    try:
        result = await grade_sql(payload.source_code, visible_cases)
    except Judge0Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )

    log_event(
        db,
        user_id=current_user.id,
        problem_id=problem.id,
        event=RUN,
        meta={"language": "sql", "status": result.status.value},
    )

    return RunResultOut(
        status=result.status,
        runtime_ms=result.runtime_ms,
        memory_kb=result.memory_kb,
        test_results=[
            VisibleTestResult(
                index=outcome.index,
                passed=outcome.passed,
                input=case["input"],
                expected_output=case["expected_output"],
                actual_output=outcome.actual_output,
                stderr=outcome.stderr,
                status_key=outcome.status_key,
            )
            for outcome, case in zip(result.test_results, visible_cases)
        ],
    )


@router.post(
    "/{slug}/submit",
    response_model=SubmissionResultOut,
    response_model_exclude_none=True,
)
async def submit_sql(
    slug: str,
    payload: SubmitPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResultOut:
    problem = _sql_problem_or_404(db, slug)
    _require_sql(payload)
    try:
        build_sql_source(payload.source_code)
    except SQLValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )

    try:
        result = await grade_sql(payload.source_code, problem.test_cases)
    except Judge0Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )

    already_solved = (
        db.query(Submission.id)
        .filter(
            Submission.user_id == current_user.id,
            Submission.problem_id == problem.id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
        )
        .first()
        is not None
    )

    xp_awarded = 0
    xp_forfeited = False
    if result.status == SubmissionStatus.ACCEPTED:
        if not already_solved:
            if has_used_hints(db, current_user.id, problem.id):
                xp_forfeited = True
            else:
                xp_awarded = award_xp(current_user, problem.difficulty)
                current_user.xp += xp_awarded
        update_streak(current_user)

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
        language=Language.SQL.value,
        status=result.status,
        runtime_ms=result.runtime_ms,
        memory_kb=result.memory_kb,
        judge_summary=[r.model_dump() for r in submit_results],
    )
    db.add(submission)
    db.flush()
    new_badges = (
        award_new_badges(db, current_user)
        if result.status == SubmissionStatus.ACCEPTED
        else []
    )
    db.commit()
    db.refresh(submission)

    log_event(
        db,
        user_id=current_user.id,
        problem_id=problem.id,
        event=SUBMIT,
        meta={
            "language": "sql",
            "status": result.status.value,
            "passed": result.status == SubmissionStatus.ACCEPTED,
        },
    )

    return SubmissionResultOut(
        submission_id=submission.id,
        status=submission.status,
        runtime_ms=submission.runtime_ms or 0.0,
        memory_kb=submission.memory_kb or 0.0,
        xp_awarded=xp_awarded,
        xp_forfeited=xp_forfeited,
        user_xp=current_user.xp,
        current_streak=current_user.current_streak,
        new_badges=new_badges,
        test_results=submit_results,
    )
