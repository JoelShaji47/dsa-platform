from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import SubmissionStatus
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.schemas.stats import Bucket, RecentSubmissionOut, StatsOut

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/me", response_model=StatsOut)
def my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatsOut:
    accepted_pairs = (
        db.query(Submission.problem_id)
        .filter(
            Submission.user_id == current_user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
        )
        .distinct()
        .subquery()
    )
    solved_ids = {row[0] for row in db.query(accepted_pairs).all()}

    totals_by_difficulty = dict(
        db.query(Problem.difficulty, func.count(Problem.id))
        .group_by(Problem.difficulty)
        .all()
    )
    totals_by_topic = dict(
        db.query(Problem.topic, func.count(Problem.id)).group_by(Problem.topic).all()
    )

    solved_by_difficulty_rows = (
        db.query(Problem.difficulty, func.count(accepted_pairs.c.problem_id))
        .outerjoin(
            accepted_pairs,
            accepted_pairs.c.problem_id == Problem.id,
        )
        .group_by(Problem.difficulty)
        .all()
    )
    solved_by_difficulty_counts = {
        difficulty: count for difficulty, count in solved_by_difficulty_rows if count
    }

    solved_by_topic_rows = (
        db.query(Problem.topic, func.count(accepted_pairs.c.problem_id))
        .outerjoin(
            accepted_pairs,
            accepted_pairs.c.problem_id == Problem.id,
        )
        .group_by(Problem.topic)
        .all()
    )
    solved_by_topic_counts = {
        topic: count for topic, count in solved_by_topic_rows if count
    }

    total_submissions = (
        db.query(func.count(Submission.id))
        .filter(Submission.user_id == current_user.id)
        .scalar()
        or 0
    )
    total_accepted = (
        db.query(func.count(Submission.id))
        .filter(
            Submission.user_id == current_user.id,
            Submission.status == SubmissionStatus.ACCEPTED,
        )
        .scalar()
        or 0
    )

    recent = (
        db.query(Submission, Problem.title, Problem.slug)
        .join(Problem, Problem.id == Submission.problem_id)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(10)
        .all()
    )

    return StatsOut(
        xp=current_user.xp,
        current_streak=current_user.current_streak,
        total_solved=len(solved_ids),
        total_submissions=total_submissions,
        acceptance_rate=round(total_accepted / total_submissions * 100, 1)
        if total_submissions
        else 0.0,
        solved_by_difficulty={
            difficulty: Bucket(
                solved=solved_by_difficulty_counts.get(difficulty, 0),
                total=totals_by_difficulty.get(difficulty, 0),
            )
            for difficulty in sorted(totals_by_difficulty)
        },
        solved_by_topic={
            topic: Bucket(
                solved=solved_by_topic_counts.get(topic, 0),
                total=totals_by_topic.get(topic, 0),
            )
            for topic in sorted(totals_by_topic)
        },
        recent_submissions=[
            RecentSubmissionOut(
                id=submission.id,
                problem_title=title,
                problem_slug=slug,
                status=submission.status,
                language=submission.language,
                runtime_ms=submission.runtime_ms,
                submitted_at=submission.submitted_at,
            )
            for submission, title, slug in recent
        ],
    )
