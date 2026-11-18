"""Replay the submission log to rebuild Layer 1 skill estimates.

Online updates keep ``skill_estimates`` current after every submit, but the
event log is the source of truth: this script recomputes theta and every
problem's difficulty from scratch, in submission order, so the state can never
drift from the events that produced it. Run it nightly, after a catalogue
import, or whenever the update rule changes.

    python scripts/refit_skill_model.py

Idempotent: running it twice produces byte-identical estimates.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.services import skill_model  # noqa: E402


def main() -> int:
    with SessionLocal() as db:
        summary = skill_model.replay(db)
    print(
        "Skill model replayed: "
        f"{summary['graded_submissions']} graded submissions -> "
        f"{summary['skill_estimates']} (user, pattern) estimates, "
        f"{summary['problems_with_difficulty']} problems with learned difficulty"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
