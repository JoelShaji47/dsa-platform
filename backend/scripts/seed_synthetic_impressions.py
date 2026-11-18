"""DEV ONLY — synthetic recommendation telemetry for smoke-testing the ranker.

Never run this against production/Supabase. It fabricates
RecommendationOpportunity + RecommendationImpression rows (plus the accepted
Submissions that back "solved" labels) so ``scripts/train_recommender.py`` has
enough leak-free impression data to clear the ``_check_frame`` gate and save a
ranker artifact.

Idempotent: re-running deletes the synthetic users' opportunities, impressions
and submissions before re-inserting.
"""

from __future__ import annotations

import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.enums import SubmissionStatus
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.telemetry import RecommendationImpression, RecommendationOpportunity
from app.models.user import User

USERS = 5
OPPORTUNITIES_PER_USER = 4
IMPRESSIONS_PER_OPPORTUNITY = 6
ACCEPT_RATE = 0.30      # share of impressions backed by an accepted submission
CLICK_RATE = 0.25       # share clicked (no accept)
DISMISS_RATE = 0.20     # share dismissed (no accept, no click)

RNG = random.Random(20261118)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _seed_db(db: Session) -> list[User]:
    """Create (or refresh) the synthetic users and return them."""
    users: list[User] = []
    for i in range(USERS):
        uid = uuid.uuid4()
        user = User(
            id=uid,
            username=f"synthetic_user_{i}",
            email=f"synthetic_user_{i}@example.invalid",
            hashed_password=None,
            supabase_id=f"synthetic-supabase-{uid}",
        )
        db.add(user)
        users.append(user)
    db.commit()
    for u in users:
        db.refresh(u)
    return users


def _clear_synthetic(db: Session, users: list[User]) -> None:
    """Remove synthetic opportunities/impressions/submissions (idempotent re-run)."""
    ids = [u.id for u in users]
    db.query(RecommendationImpression).filter(
        RecommendationImpression.user_id.in_(ids)
    ).delete(synchronize_session=False)
    db.query(RecommendationOpportunity).filter(
        RecommendationOpportunity.user_id.in_(ids)
    ).delete(synchronize_session=False)
    db.query(Submission).filter(
        Submission.user_id.in_(ids),
        Submission.code.like("synthetic:%"),
    ).delete(synchronize_session=False)
    db.commit()


def _pick_problems(db: Session, n: int) -> list:
    solvable = (
        db.query(Problem)
        .filter(
            Problem.is_published.is_(True),
            Problem.starter_code.is_not(None),
            Problem.test_cases.is_not(None),
        )
        .all()
    )
    RNG.shuffle(solvable)
    return solvable[:n]


def _seed(db: Session, users: list[User]) -> int:
    """Insert synthetic opportunities + impressions; return impression count."""
    problems = _pick_problems(db, 60)
    if len(problems) < 8:
        raise RuntimeError("not enough solvable problems in catalog")

    total_impressions = 0
    for user in users:
        for _ in range(OPPORTUNITIES_PER_USER):
            opp = RecommendationOpportunity(
                user_id=user.id,
                model_version="heuristic-v1-synthetic",
                feature_schema_version=2,
                candidate_count=IMPRESSIONS_PER_OPPORTUNITY,
            )
            db.add(opp)
            db.flush()

            base = _now() - timedelta(days=RNG.uniform(0, 10))
            picked = RNG.sample(problems, IMPRESSIONS_PER_OPPORTUNITY)
            for rank, problem in enumerate(picked):
                imp_created = base + timedelta(minutes=rank * 5)
                imp = RecommendationImpression(
                    opportunity_id=opp.id,
                    user_id=user.id,
                    problem_id=problem.id,
                    rank=rank,
                    rendered=True,
                    model_version=opp.model_version,
                )
                db.add(imp)
                db.flush()
                total_impressions += 1

                roll = RNG.random()
                if roll < ACCEPT_RATE:
                    sub = Submission(
                        user_id=user.id,
                        problem_id=problem.id,
                        code="synthetic:accepted",
                        language="python",
                        status=SubmissionStatus.ACCEPTED,
                        submitted_at=imp_created + timedelta(minutes=RNG.uniform(5, 60)),
                        test_session_id=None,
                    )
                    db.add(sub)
                elif roll < ACCEPT_RATE + CLICK_RATE:
                    imp.clicked_at = imp_created + timedelta(minutes=RNG.uniform(1, 30))
                elif roll < ACCEPT_RATE + CLICK_RATE + DISMISS_RATE:
                    imp.dismissed_at = imp_created + timedelta(minutes=RNG.uniform(1, 30))

    db.commit()
    return total_impressions


def main() -> None:
    with SessionLocal() as db:
        users = _seed_db(db)
        _clear_synthetic(db, users)
        n = _seed(db, users)
    print(f"seeded {n} synthetic impressions across {USERS} users")


if __name__ == "__main__":
    main()
