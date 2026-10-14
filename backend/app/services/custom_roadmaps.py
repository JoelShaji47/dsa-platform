"""Deterministic custom-roadmap builder (template + per-person sizing).

DSA steps come from the real catalog in pattern-prerequisite order, sized by
the user's duration + daily minutes + level/goal mix. No LLM, so every step
links to a real solvable problem.
"""

import math
import secrets

from sqlalchemy.orm import Session

from app.models.custom_roadmap import CustomRoadmapGeneration
from app.models.problem import Problem
from app.services.roadmap import PATTERNS

EST_MINS = {"EASY": 30, "MEDIUM": 60, "HARD": 90}

SHARE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

LEVEL_MIX = {
    "never_started": ("EASY", "EASY", "EASY", "MEDIUM", "EASY", "MEDIUM", "EASY", "MEDIUM", "HARD", "MEDIUM"),
    "basics": ("EASY", "MEDIUM", "EASY", "MEDIUM", "EASY", "HARD", "MEDIUM", "EASY", "MEDIUM", "HARD"),
    "50_plus": ("EASY", "MEDIUM", "MEDIUM", "HARD", "MEDIUM", "EASY", "MEDIUM", "HARD", "MEDIUM", "HARD"),
    "interview_ready": ("EASY", "MEDIUM", "HARD", "MEDIUM", "HARD", "MEDIUM", "HARD", "MEDIUM", "EASY", "HARD"),
}

GOAL_TITLES = {
    "interview_soon": "Interview sprint",
    "fundamentals": "Strong fundamentals",
    "company": "Company target",
    "curious": "Curious explorer",
}

WEEKLY_LIMIT = 2


def generations_this_week(db: Session, user_id) -> int:
    from datetime import datetime, timedelta, timezone

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    return (
        db.query(CustomRoadmapGeneration)
        .filter(
            CustomRoadmapGeneration.user_id == user_id,
            CustomRoadmapGeneration.created_at >= cutoff,
        )
        .count()
    )


def new_share_code(db: Session) -> str:
    from app.models.custom_roadmap import CustomRoadmap

    for _ in range(20):
        code = "".join(secrets.choice(SHARE_ALPHABET) for _ in range(6))
        exists = (
            db.query(CustomRoadmap.id).filter(CustomRoadmap.share_code == code).first()
        )
        if not exists:
            return code
    raise RuntimeError("Could not mint a share code")


def _load_solvable(db: Session) -> dict[str, Problem]:
    rows = db.query(Problem).filter(Problem.is_published.is_(True)).all()
    return {p.slug: p for p in rows if p.starter_code and p.test_cases}


def build_steps(
    db: Session,
    *,
    level: str,
    goal: str,
    company: str | None,
    mins_per_day: int,
    total_days: int,
    target_count: int | None,
    kind: str = "dsa_build",
) -> list[dict]:
    """Return ordered step dicts (no DB writes)."""
    solvable = _load_solvable(db)
    mix = LEVEL_MIX.get(level, LEVEL_MIX["basics"])

    # Pattern-prerequisite order: PATTERNS is already topologically ordered.
    ordered_slugs: list[str] = []
    for pattern in sorted(PATTERNS, key=lambda p: (p["order"], p["name"])):
        for slug in pattern["problems"]:
            if slug in solvable and slug not in ordered_slugs:
                ordered_slugs.append(slug)

    if kind == "video":
        ordered_slugs = [s for s in ordered_slugs if solvable[s].video_url]

    # Company boost: tagged problems first within their difficulty.
    if goal == "company" and company:
        needle = company.strip().lower()
        ordered_slugs.sort(
            key=lambda s: (
                0 if any(needle in (c or "").lower() for c in (solvable[s].companies or [])) else 1
            )
        )

    total_mins = max(1, total_days) * mins_per_day
    # Walk the mix cycle, picking the next matching-difficulty problem.
    picked: list[Problem] = []
    used: set[str] = set()
    spent = 0
    i = 0
    # Upper bound: don't loop forever on thin pools.
    while len(ordered_slugs) > len(used) and i < 2000:
        want = mix[i % len(mix)]
        nxt = next(
            (s for s in ordered_slugs if s not in used and solvable[s].difficulty.value == want),
            None,
        )
        if nxt is None:  # difficulty exhausted — take whatever remains
            nxt = next((s for s in ordered_slugs if s not in used), None)
        if nxt is None:
            break
        cost = EST_MINS[solvable[nxt].difficulty.value]
        if spent + cost > total_mins and picked:
            break
        picked.append(solvable[nxt])
        used.add(nxt)
        spent += cost
        i += 1
        if target_count and len(picked) >= target_count:
            break

    if not picked:  # tiny DB fallback: first solvable problems fit the budget
        for s in ordered_slugs:
            cost = EST_MINS[solvable[s].difficulty.value]
            if spent + cost > total_mins and picked:
                break
            picked.append(solvable[s])
            spent += cost
            if target_count and len(picked) >= target_count:
                break

    total = len(picked) or 1
    per_day = max(1, math.ceil(len(picked) / max(1, total_days)))
    steps = []
    for pos, p in enumerate(picked, start=1):
        steps.append(
            {
                "position": pos,
                "problem_slug": p.slug,
                "title": p.title,
                "kind": "video" if kind == "video" else "problem",
                "pattern_key": p.pattern_key,
                "difficulty": p.difficulty.value,
                "est_mins": EST_MINS[p.difficulty.value],
                "day_index": min(total_days, (pos - 1) // per_day + 1),
                "meta": {
                    "video_url": p.video_url,
                    "editorial_url": p.editorial_url,
                },
            }
        )
    return steps


def default_title(level: str, goal: str, total_days: int, company: str | None) -> str:
    base = GOAL_TITLES.get(goal, "Custom roadmap")
    if goal == "company" and company:
        base = f"{company.strip()} target"
    return f"{base} · {total_days}d · {level.replace('_', ' ')}"
