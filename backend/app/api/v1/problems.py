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
    CustomRunOut,
    CustomRunPayload,
    RunResultOut,
    SubmissionHistoryItem,
    SubmissionResultOut,
    SubmitPayload,
    SubmitTestResult,
    VisibleTestResult,
)
from app.services.activity import RUN, SUBMIT, log_event
from app.services.gamification import award_new_badges, award_xp, update_streak
from app.services.grader import RUN_VISIBLE_CASE_LIMIT, grade_code, truncate_output
from app.services.judge0 import Judge0Error, submit
from app.services.tutor import has_used_hints

router = APIRouter(prefix="/problems", tags=["problems"])
custom_router = APIRouter(prefix="/custom-run", tags=["custom-run"])


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
def list_problems(
    topic: Topic | None = None,
    difficulty: Difficulty | None = None,
    search: str | None = None,
    source: str | None = None,
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
    if source is not None:
        # JSONB containment: row.sources includes the requested sheet.
        query = query.filter(Problem.sources.contains([source]))

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
    )


@router.get("/{slug}/submissions", response_model=list[SubmissionHistoryItem])
def get_problem_submissions(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SubmissionHistoryItem]:
    problem = db.query(Problem).filter(Problem.slug == slug).first()
    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    rows = (
        db.query(Submission)
        .filter(
            Submission.user_id == current_user.id,
            Submission.problem_id == problem.id,
        )
        .order_by(Submission.submitted_at.desc())
        .limit(20)
        .all()
    )
    return [
        SubmissionHistoryItem(
            submission_id=s.id,
            status=s.status,
            language=s.language,
            code=s.code,
            runtime_ms=s.runtime_ms,
            memory_kb=s.memory_kb,
            judge_summary=s.judge_summary,
            submitted_at=s.submitted_at.isoformat() if s.submitted_at else "",
        )
        for s in rows
    ]


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
        case
        for case in problem.test_cases
        if not case.get("is_hidden", False)
    ][:RUN_VISIBLE_CASE_LIMIT]

    try:
        result = await grade_code(
            payload.source_code, payload.language.value, visible_cases
        )
    except Judge0Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )

    log_event(
        db,
        user_id=current_user.id,
        problem_id=problem.id,
        event=RUN,
        meta={"language": payload.language.value, "status": result.status.value},
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


def _custom_status(status_key: str) -> SubmissionStatus | None:
    if status_key == "ACCEPTED":
        return SubmissionStatus.ACCEPTED
    if status_key == "COMPILATION_ERROR":
        return SubmissionStatus.COMPILATION_ERROR
    if status_key == "TIME_LIMIT_EXCEEDED":
        return SubmissionStatus.TLE
    return SubmissionStatus.RUNTIME_ERROR


@custom_router.post("", response_model=CustomRunOut)
async def custom_run(
    payload: CustomRunPayload,
    current_user: User = Depends(get_current_user),
) -> CustomRunOut:
    """Run the user's code against their own stdin. Exploratory only — not
    graded, stored, or scored."""
    try:
        result = await submit(
            payload.source_code, payload.language.value, payload.stdin
        )
    except Judge0Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )

    status_key = result.get("status_key", "UNKNOWN")
    stderr = result.get("stderr") or result.get("compile_output")
    return CustomRunOut(
        status_key=status_key,
        status=_custom_status(status_key),
        stdout=truncate_output(result.get("stdout")),
        stderr=truncate_output(stderr) if stderr else None,
        compile_output=truncate_output(result.get("compile_output")),
        runtime_ms=float(result.get("time") or 0) * 1000,
        memory_kb=float(result.get("memory") or 0),
    )


@router.post(
    "/{slug}/submit",
    response_model=SubmissionResultOut,
    response_model_exclude_none=True,
)
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

    # Build per-test feedback: visible cases carry the full diff context,
    # hidden cases carry only pass/fail + status key (inputs never leak).
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
            "language": payload.language.value,
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
