import threading
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import SubmissionStatus
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.schemas.tutor import (
    AssistantRequest,
    AssistantResponse,
    HintLevelInfo,
    HintMetaOut,
    HintRevealOut,
    ReviewOut,
)
from app.services import gemini, tutor
from app.services.activity import CHAT, HINT, REVIEW, log_event
from app.services.llm import LLMError

router = APIRouter(tags=["tutor"])

_ASSIST_LIMIT = 20
_ASSIST_WINDOW = 60.0
_assist_hits: dict = {}
_assist_lock = threading.Lock()


def _check_assist_rate(user_id) -> None:
    now = time.monotonic()
    key = str(user_id)
    with _assist_lock:
        hits = [t for t in _assist_hits.get(key, []) if now - t < _ASSIST_WINDOW]
        if len(hits) >= _ASSIST_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Coach rate limit: 20 messages per minute. Slow down a touch.",
            )
        hits.append(now)
        _assist_hits[key] = hits


def _get_problem_or_404(db: Session, slug: str) -> Problem:
    problem = db.query(Problem).filter(Problem.slug == slug).first()
    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    return problem


def _used_levels(db: Session, user_id, problem_id) -> set[int]:
    from app.models.hint import HintUsage

    rows = (
        db.query(HintUsage.level)
        .filter(
            HintUsage.user_id == user_id,
            HintUsage.problem_id == problem_id,
        )
        .all()
    )
    return {row[0] for row in rows}


@router.get("/problems/{slug}/hints", response_model=HintMetaOut)
def hint_metadata(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HintMetaOut:
    problem = _get_problem_or_404(db, slug)
    solved = (
        db.query(Submission.id)
        .filter(
            Submission.user_id == current_user.id,
            Submission.problem_id == problem.id,
            Submission.status == SubmissionStatus.ACCEPTED,
        )
        .first()
        is not None
    )
    used = _used_levels(db, current_user.id, problem.id)
    return HintMetaOut(
        total_levels=tutor.HINT_LEVELS,
        xp_forfeit_applies=not solved,
        levels=[
            HintLevelInfo(level=level, label=tutor.HINT_LEVEL_META[level][0], revealed=level in used)
            for level in sorted(tutor.HINT_LEVEL_META)
        ],
    )


@router.post("/problems/{slug}/hints/{level}", response_model=HintRevealOut)
def reveal_hint(
    slug: str,
    level: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HintRevealOut:
    if level not in tutor.HINT_LEVEL_META:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hint level must be between 1 and {tutor.HINT_LEVELS}",
        )
    problem = _get_problem_or_404(db, slug)

    try:
        content, _generated = tutor.get_or_create_hint(db, problem, level)
    except gemini.GeminiError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )

    tutor.record_hint_usage(db, current_user.id, problem.id, level)
    log_event(
        db,
        user_id=current_user.id,
        problem_id=problem.id,
        event=HINT,
        meta={"level": level},
    )

    return HintRevealOut(level=level, label=tutor.HINT_LEVEL_META[level][0], content=content)


@router.post("/submissions/{submission_id}/review", response_model=ReviewOut)
def review_submission(
    submission_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewOut:
    submission = (
        db.query(Submission)
        .filter(
            Submission.id == submission_id,
            Submission.user_id == current_user.id,
        )
        .first()
    )
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )
    if submission.status == SubmissionStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only failed submissions can be reviewed",
        )
    log_event(
        db,
        user_id=current_user.id,
        problem_id=submission.problem_id,
        event=REVIEW,
        meta={"submission_id": str(submission.id)},
    )
    if submission.ai_review is not None:
        return ReviewOut(**submission.ai_review)

    problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
    if problem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )

    result = {"test_results": submission.judge_summary or []}
    try:
        review = tutor.build_failure_review(db, submission, problem, result)
    except gemini.GeminiError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )
    return ReviewOut(**review)


@router.post("/problems/{slug}/assistant", response_model=AssistantResponse)
def chat_assistant(
    slug: str,
    payload: AssistantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssistantResponse:
    problem = _get_problem_or_404(db, slug)
    _check_assist_rate(current_user.id)

    code = payload.code if payload.include_code else ""
    # Strip null bytes; ORM-bound downstream so no SQLi surface.
    code = code.replace("\x00", "")
    message = payload.message.replace("\x00", "")
    history = [{"role": h.role, "content": h.content.replace("\x00", "")} for h in payload.history]
    last_result = payload.last_result.model_dump() if payload.last_result else None

    try:
        reply, provider = tutor.chat_with_coach(
            problem,
            language=payload.language,
            code=code,
            last_result=last_result,
            history=history,
            message=message,
        )
    except LLMError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )
    log_event(
        db,
        user_id=current_user.id,
        problem_id=problem.id,
        event=CHAT,
        meta={"language": payload.language},
    )
    return AssistantResponse(reply=reply, provider=provider)
