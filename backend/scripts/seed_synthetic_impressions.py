"""DEV ONLY — synthetic recommendation telemetry for smoke-testing the ranker.

Never run this against production/Supabase. It fabricates
RecommendationOpportunity + RecommendationImpression rows (plus the accepted
Submissions that back "solved" labels) so ``scripts/train_recommender.py`` has
enough leak-free impression data to clear the ``_check_frame`` gate and save a
ranker artifact.

Idempotent: re-running deletes the synthetic users' opportunities, impressions
and submissions before re-inserting.

Usage (from backend/):
    DATABASE_URL="..." .venv/bin/python scripts/seed_synthetic_impressions.py \\
        --users 20 --opps 6 --imps 8 --seed 7
"""

from __future__ import annotations

import argparse
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


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _seed_db(db: Session, n_users: int, rng: random.Random) -> list[User]:
    users: list[User] = []
    for i in range(n_users):
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


def _pick_problems(db: Session, n: int, rng: random.Random) -> list:
    solvable = (
        db.query(Problem)
        .filter(
            Problem.is_published.is_(True),
            Problem.starter_code.is_not(None),
            Problem.test_cases.is_not(None),
        )
        .all()
    )
    rng.shuffle(solvable)
    return solvable[:n]


def _seed(
    db: Session,
    users: list[User],
    *,
    opps_per_user: int,
    imps_per_opp: int,
    accept_rate: float,
    click_rate: float,
    dismiss_rate: float,
    rng: random.Random,
) -> dict[str, int]:
    """Insert synthetic opportunities + impressions; return counters."""
    problems = _pick_problems(db, max(60, imps_per_opp * 3), rng)
    if len(problems) < 8:
        raise RuntimeError("not enough solvable problems in catalog")

    counters = {"opportunities": 0, "impressions": 0, "accepts": 0,
                "clicks": 0, "dismisses": 0, "none": 0}

    for user in users:
        for _ in range(opps_per_user):
            opp = RecommendationOpportunity(
                user_id=user.id,
                model_version="heuristic-v1-synthetic",
                feature_schema_version=2,
                candidate_count=imps_per_opp,
            )
            db.add(opp)
            db.flush()
            counters["opportunities"] += 1

            base = _now() - timedelta(days=rng.uniform(0, 10))
            picked = rng.sample(problems, min(imps_per_opp, len(problems)))
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
                counters["impressions"] += 1

                roll = rng.random()
                if roll < accept_rate:
                    # Clean accept: single submission, no hints -> relevance 2.
                    sub = Submission(
                        user_id=user.id,
                        problem_id=problem.id,
                        code="synthetic:accepted",
                        language="python",
                        status=SubmissionStatus.ACCEPTED,
                        submitted_at=imp_created
                        + timedelta(minutes=rng.uniform(5, 60)),
                        test_session_id=None,
                    )
                    db.add(sub)
                    counters["accepts"] += 1
                elif roll < accept_rate + click_rate:
                    imp.clicked_at = imp_created + timedelta(
                        minutes=rng.uniform(1, 30)
                    )
                    counters["clicks"] += 1
                elif roll < accept_rate + click_rate + dismiss_rate:
                    imp.dismissed_at = imp_created + timedelta(
                        minutes=rng.uniform(1, 30)
                    )
                    counters["dismisses"] += 1
                else:
                    counters["none"] += 1

    db.commit()
    return counters


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--users", type=int, default=5,
                    help="synthetic users to create")
    ap.add_argument("--opps", type=int, default=4,
                    help="opportunities per user")
    ap.add_argument("--imps", type=int, default=6,
                    help="impressions per opportunity")
    ap.add_argument("--accept-rate", type=float, default=0.30)
    ap.add_argument("--click-rate", type=float, default=0.25)
    ap.add_argument("--dismiss-rate", type=float, default=0.20)
    ap.add_argument("--seed", type=int, default=20261118)
    args = ap.parse_args()

    total = args.accept_rate + args.click_rate + args.dismiss_rate
    if total > 1.0:
        ap.error("accept + click + dismiss rates must sum to <= 1.0")

    rng = random.Random(args.seed)
    with SessionLocal() as db:
        users = _seed_db(db, args.users, rng)
        _clear_synthetic(db, users)
        counters = _seed(
            db, users,
            opps_per_user=args.opps,
            imps_per_opp=args.imps,
            accept_rate=args.accept_rate,
            click_rate=args.click_rate,
            dismiss_rate=args.dismiss_rate,
            rng=rng,
        )
    print("seeded:", counters, f"(seed={args.seed})")


if __name__ == "__main__":
    main()
