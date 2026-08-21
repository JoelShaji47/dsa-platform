from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import Difficulty, SubmissionStatus, Topic
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.schemas.problem import ProblemDetail, ProblemListItem
from app.schemas.submission import (
    RunResultOut,
    SubmissionResultOut,
    SubmitPayload,
    TestResultOut,
    VisibleTestResult,
)
from app.services.gamification import award_new_badges, award_xp, update_streak
from app.services.grader import grade_code
from app.services.judge0 import Judge0Error
from app.services.tutor import has_used_hints

router = APIRouter(prefix="/problems", tags=["problems"])


def _solved_problem_ids(db: Session, user_id) -> set:
    rows = (
        db.query(Submission.problem_id)
        .filter(
            Submission.user_id == user_id,
            Submission.status == SubmissionStatus.ACCEPTED,
        )
        .distinct()
        .all()
    )
    return {row[0] for row in rows}


@router.get("", response_model=list[ProblemListItem])
def list_problems(
    topic: Topic | None = None,
    difficulty: Difficulty | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProblemListItem]:
    query = db.query(Problem)
    if topic is not None:
        query = query.filter(Problem.topic == topic)
    if difficulty is not None:
        query = query.filter(Problem.difficulty == difficulty)
    if search:
        query = query.filter(Problem.title.ilike(f"%{search}%"))

    solved_ids = _solved_problem_ids(db, current_user.id)
    return [
        ProblemListItem(
            id=problem.id,
            title=problem.title,
            slug=problem.slug,
            difficulty=problem.difficulty,
            topic=problem.topic,
            solved=problem.id in solved_ids,
        )
        for problem in query.order_by(Problem.difficulty, Problem.title).all()
    ]


@router.get("/{slug}", response_model=ProblemDetail)
def get_problem(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProblemDetail:
    problem = db.query(Problem).filter(Problem.slug == slug).first()
    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

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
        solved=problem.id in solved_ids,
    )


def _get_problem_or_404(db: Session, slug: str) -> Problem:
    problem = db.query(Problem).filter(Problem.slug == slug).first()
    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    return problem


@router.post("/{slug}/run", response_model=RunResultOut)
async def run_code(
    slug: str,
    payload: SubmitPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunResultOut:
    problem = _get_problem_or_404(db, slug)
    visible_cases = [
        case for case in problem.test_cases if not case.get("is_hidden", False)
    ]

    try:
        result = await grade_code(
            payload.source_code, payload.language.value, visible_cases
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
            VisibleTestResult(
                index=outcome.index,
                passed=outcome.passed,
                input=case["input"],
                expected_output=case["expected_output"],
                actual_output=outcome.actual_output,
                status_key=outcome.status_key,
            )
            for outcome, case in zip(result.test_results, visible_cases)
        ],
    )


@router.post("/{slug}/submit", response_model=SubmissionResultOut)
async def submit_solution(
    slug: str,
    payload: SubmitPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResultOut:
    problem = _get_problem_or_404(db, slug)

    try:
        result = await grade_code(
            payload.source_code, payload.language.value, problem.test_cases
        )
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

    submission = Submission(
        user_id=current_user.id,
        problem_id=problem.id,
        code=payload.source_code,
        language=payload.language.value,
        status=result.status,
        runtime_ms=result.runtime_ms,
        memory_kb=result.memory_kb,
        judge_summary=[
            {"index": outcome.index, "passed": outcome.passed}
            for outcome in result.test_results
        ],
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
        test_results=[
            TestResultOut(index=outcome.index, passed=outcome.passed)
            for outcome in result.test_results
        ],
    )
