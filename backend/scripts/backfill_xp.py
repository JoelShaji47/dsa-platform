"""Backfill xp_events from accepted submissions (one event per first-accept).

The users.xp column stays untouched (display source of truth); the ledger gains
history so weekly/monthly league sums work. Historic hint-forfeits can't be
reconstructed, so backfilled weeks may read slightly high — noted, accepted.

Usage: .venv/bin/python scripts/backfill_xp.py
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.enums import SubmissionStatus
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.xp_event import XpEvent
from app.services.gamification import XP_BY_DIFFICULTY


def main() -> int:
    with SessionLocal() as db:
        existing = {
            (r[0], r[1])
            for r in db.query(XpEvent.user_id, XpEvent.problem_id)
            .filter(XpEvent.reason == "solve", XpEvent.problem_id.isnot(None))
            .all()
        }
        rows = (
            db.query(Submission, Problem.difficulty)
            .join(Problem, Problem.id == Submission.problem_id)
            .filter(
                Submission.status == SubmissionStatus.ACCEPTED,
                Submission.test_session_id.is_(None),
            )
            .order_by(Submission.submitted_at)
            .all()
        )
        seen: set = set()
        added = 0
        for sub, difficulty in rows:
            key = (sub.user_id, sub.problem_id)
            if key in seen or key in existing:
                continue
            seen.add(key)
            db.add(
                XpEvent(
                    user_id=sub.user_id,
                    amount=XP_BY_DIFFICULTY.get(difficulty, 10),
                    reason="solve",
                    problem_id=sub.problem_id,
                    created_at=sub.submitted_at,
                )
            )
            added += 1
        db.commit()
        total = db.query(func.count(XpEvent.id)).scalar()
    print(f"backfilled {added} solve events ({total} total xp_events)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
