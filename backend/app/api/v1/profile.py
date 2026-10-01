from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import Difficulty, SubmissionStatus, TestStatus
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.test_session import TestProblem, TestSession
from app.models.user import User
from app.schemas.profile import (
    ActivityDay,
    ProfileOut,
    ProfileSubmission,
    ProfileTestSummary,
    ProfileUser,
    SolvedCounts,
)
from app.services.gamification import list_user_badges
from app.services.leagues import tier_name
from app.services.roadmap import get_activity

router = APIRouter(prefix="/profile", tags=["profile"])

SUBMISSION_LIMIT = 25
TEST_LIMIT = 25
ACTIVITY_DAYS = 140


@router.get("", response_model=ProfileOut)
def my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileOut:
    """Everything the profile dashboard needs in one round trip."""
    accepted_problem_ids = (
        db.query(Submission.problem_id)
        .filter(
            Submission.user_id == current_user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
        )
        .distinct()
        .subquery()
    )

    solved_by_difficulty = dict(
        db.query(Problem.difficulty, func.count(Problem.id))
        .select_from(Problem)
        .join(accepted_problem_ids, accepted_problem_ids.c.problem_id == Problem.id)
        .filter(Problem.is_published.is_(True))
        .group_by(Problem.difficulty)
        .all()
    )
    easy = solved_by_difficulty.get(Difficulty.EASY, 0)
    medium = solved_by_difficulty.get(Difficulty.MEDIUM, 0)
    hard = solved_by_difficulty.get(Difficulty.HARD, 0)

    recent = (
        db.query(Submission, Problem.title, Problem.slug, Problem.difficulty)
        .join(Problem, Problem.id == Submission.problem_id)
        .filter(
            Submission.user_id == current_user.id,
            Submission.test_session_id.is_(None),
        )
        .order_by(Submission.submitted_at.desc())
        .limit(SUBMISSION_LIMIT)
        .all()
    )

    sessions = (
        db.query(TestSession)
        .filter(TestSession.user_id == current_user.id)
        .order_by(TestSession.started_at.desc())
        .limit(TEST_LIMIT)
        .all()
    )
    session_ids = [row.id for row in sessions]
    problem_counts = dict(
        db.query(TestProblem.session_id, func.count(TestProblem.id))
        .filter(TestProblem.session_id.in_(session_ids))
        .group_by(TestProblem.session_id)
        .all()
    ) if session_ids else {}

    # Counted separately from `sessions`, which is capped at TEST_LIMIT.
    total_tests = (
        db.query(func.count(TestSession.id))
        .filter(
            TestSession.user_id == current_user.id,
            TestSession.status == TestStatus.SUBMITTED,
        )
        .scalar()
        or 0
    )

    activity = get_activity(db, current_user, days=ACTIVITY_DAYS)["days"]

    return ProfileOut(
        user=ProfileUser(
            username=current_user.username,
            xp=current_user.xp,
            current_streak=current_user.current_streak,
            league_tier=current_user.league_tier,
            league_name=tier_name(current_user.league_tier),
            created_at=current_user.created_at,
        ),
        solved=SolvedCounts(
            easy=easy, medium=medium, hard=hard, total=easy + medium + hard
        ),
        total_tests=total_tests,
        activity=[ActivityDay(**day) for day in activity],
        submissions=[
            ProfileSubmission(
                id=submission.id,
                problem_title=title,
                problem_slug=slug,
                difficulty=difficulty,
                status=submission.status,
                language=submission.language,
                runtime_ms=submission.runtime_ms,
                submitted_at=submission.submitted_at,
            )
            for submission, title, slug, difficulty in recent
        ],
        tests=[
            ProfileTestSummary(
                id=session.id,
                status=session.status,
                score=session.score or 0,
                passed_count=session.passed_count or 0,
                total=problem_counts.get(session.id, 0),
                violations=session.violations or 0,
                assigned_topics=session.assigned_topics or [],
                started_at=session.started_at,
                ended_at=session.ended_at,
                time_taken_seconds=session.time_taken_seconds or 0,
            )
            for session in sessions
        ],
        badges=list_user_badges(db, current_user),
    )
