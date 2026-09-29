"""Weekly Duolingo-style leagues.

- 7 tiers, seasons run Monday 00:00 UTC → Sunday 23:59 UTC.
- Cohorts of ≤30, grouped by tier then prior-week XP (similar activity races).
- Top 10 promote, bottom 5 relegated; rank 1 earns the Weekly Champion badge.
- Rollover is lazy: the first read in a new week finalizes the previous one,
  so no cron is needed.
"""

import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from sqlalchemy import func

from app.models.league import League, LeagueMember
from app.models.user import User
from app.services.gamification import xp_earned_between

logger = logging.getLogger(__name__)

TIERS = ["Bronze", "Silver", "Gold", "Sapphire", "Ruby", "Emerald", "Diamond"]
MAX_TIER = len(TIERS) - 1
COHORT_SIZE = 30
PROMOTE_COUNT = 10
RELEGATE_COUNT = 5


def tier_name(tier: int) -> str:
    return TIERS[max(0, min(tier, MAX_TIER))]


def week_start(day: date | None = None) -> date:
    day = day or date.today()
    return day - timedelta(days=day.weekday())


def week_bounds(day: date | None = None) -> tuple[datetime, datetime]:
    start = week_start(day)
    start_dt = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
    return start_dt, start_dt + timedelta(days=7)


def _week_xp(db: Session, user_id, start: datetime, end: datetime) -> int:
    return xp_earned_between(db, user_id, start, end)


def _finalize_league(db: Session, league: League, start: datetime, end: datetime) -> None:
    from app.models.badge import Badge, UserBadge

    members = db.query(LeagueMember).filter(LeagueMember.league_id == league.id).all()
    if not members:
        db.delete(league)
        return
    scored = sorted(
        ((m, _week_xp(db, m.user_id, start, end)) for m in members),
        key=lambda t: (-t[1], str(t[0].user_id)),
    )
    n = len(scored)
    for rank, (member, xp) in enumerate(scored, start=1):
        member.final_rank = rank
        member.final_xp = xp
        movement = 0
        user = db.get(User, member.user_id)
        if user is None:
            continue
        if rank <= min(PROMOTE_COUNT, n) and xp > 0:
            movement = 1
            user.league_tier = min((user.league_tier or 0) + 1, MAX_TIER)
        elif rank > max(n - RELEGATE_COUNT, 0):
            movement = -1
            user.league_tier = max((user.league_tier or 0) - 1, 0)
        member.movement = movement
        if rank == 1 and xp > 0:
            badge = db.query(Badge).filter(Badge.criteria == "WEEKLY_CHAMPION").first()
            if badge is not None:
                exists = (
                    db.query(UserBadge.id)
                    .filter(UserBadge.user_id == user.id, UserBadge.badge_id == badge.id)
                    .first()
                )
                if exists is None:
                    db.add(UserBadge(user_id=user.id, badge_id=badge.id))
    db.commit()


def _seed_week(db: Session, monday: date) -> None:
    prev_start = monday - timedelta(days=7)
    users = (
        db.query(User)
        .filter(User.league_opt_out.is_(False))
        .order_by(User.league_tier, User.created_at)
        .all()
    )
    if not users:
        return
    # Order cohorts by tier, then by last week's XP (similar activity together).
    prev_s, prev_e = week_bounds(prev_start)
    ranked = sorted(
        users,
        key=lambda u: ((u.league_tier or 0), -_week_xp(db, u.id, prev_s, prev_e), str(u.id)),
    )
    tier_of_first: dict = {}
    for i in range(0, len(ranked), COHORT_SIZE):
        chunk = ranked[i : i + COHORT_SIZE]
        tier = chunk[0].league_tier or 0
        tier_of_first[i] = tier
        league = League(week_start=monday, tier=tier)
        db.add(league)
        db.flush()
        for u in chunk:
            db.add(LeagueMember(league_id=league.id, user_id=u.id))
    db.commit()


def ensure_current_season(db: Session, today: date | None = None) -> date:
    """Finalize any stale week and seed the current one. Returns Monday."""
    monday = week_start(today)
    latest: date | None = (
        db.query(League.week_start).order_by(League.week_start.desc()).first()
    )
    latest = latest[0] if latest else None
    if latest is None:
        _seed_week(db, monday)
        return monday
    if monday < latest and db.query(League.id).filter(League.week_start == monday).first() is None:
        # Historical week with no cohorts (tests/backfill) — seed directly.
        _seed_week(db, monday)
        return monday
    while latest < monday:
        stale = db.query(League).filter(League.week_start == latest).all()
        s, e = week_bounds(latest)
        for league in stale:
            try:
                _finalize_league(db, league, s, e)
            except Exception:
                logger.exception("league finalize failed for %s", league.id)
                db.rollback()
        latest = latest + timedelta(days=7)
        _seed_week(db, latest)
    return monday


def join_week(db: Session, user: User, monday: date) -> League | None:
    """Place a mid-week joiner into the smallest fitting cohort (same tier
    preferred), creating one if every cohort is full. Opted-out users stay out."""
    if user.league_opt_out:
        return None
    tier = user.league_tier or 0
    counts = (
        db.query(League.id, func.count(LeagueMember.id).label("n"))
        .outerjoin(LeagueMember, LeagueMember.league_id == League.id)
        .filter(League.week_start == monday)
        .group_by(League.id, League.tier)
        .order_by(League.tier != tier, "n")
        .all()
    )
    for league_id, n in counts:
        if (n or 0) < COHORT_SIZE:
            league = db.get(League, league_id)
            db.add(LeagueMember(league_id=league.id, user_id=user.id))
            db.commit()
            return league
    league = League(week_start=monday, tier=tier)
    db.add(league)
    db.flush()
    db.add(LeagueMember(league_id=league.id, user_id=user.id))
    db.commit()
    return league


def leave_week(db: Session, user: User, today: date | None = None) -> None:
    """Opt out: removed from this week's board, skipped by future seedings."""
    user.league_opt_out = True
    monday = week_start(today)
    db.query(LeagueMember).filter(
        LeagueMember.user_id == user.id,
        LeagueMember.league_id.in_(
            db.query(League.id).filter(League.week_start == monday)
        ),
    ).delete(synchronize_session=False)
    db.commit()


def rejoin_week(db: Session, user: User) -> None:
    user.league_opt_out = False
    db.commit()


def my_league(db: Session, user: User, today: date | None = None) -> League | None:
    monday = ensure_current_season(db, today)
    member = (
        db.query(LeagueMember)
        .join(League, League.id == LeagueMember.league_id)
        .filter(League.week_start == monday, LeagueMember.user_id == user.id)
        .first()
    )
    if member is None:
        return join_week(db, user, monday)
    return db.get(League, member.league_id)


def board(db: Session, user: User, today: date | None = None) -> dict:
    monday = ensure_current_season(db, today)
    league = my_league(db, user, today)
    if league is None:
        return {
            "league": None,
            "members": [],
            "opted_out": bool(user.league_opt_out),
            "tier_name": tier_name(user.league_tier or 0),
        }
    start, end = week_bounds(monday)
    members = db.query(LeagueMember).filter(LeagueMember.league_id == league.id).all()
    rows = []
    for m in members:
        u = db.get(User, m.user_id)
        if u is None:
            continue
        rows.append(
            {
                "user_id": str(u.id),
                "username": u.username,
                "xp": _week_xp(db, u.id, start, end),
                "is_me": u.id == user.id,
            }
        )
    rows.sort(key=lambda r: (-r["xp"], r["username"]))
    n = len(rows)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
        r["zone"] = (
            "promote"
            if i <= min(PROMOTE_COUNT, n)
            else ("relegate" if i > max(n - RELEGATE_COUNT, 0) else "hold")
        )
    mine = next((r for r in rows if r["is_me"]), None)
    prev = (
        db.query(LeagueMember)
        .join(League, League.id == LeagueMember.league_id)
        .filter(
            League.week_start == monday - timedelta(days=7),
            LeagueMember.user_id == user.id,
        )
        .first()
    )
    return {
        "league": {
            "id": str(league.id),
            "tier": league.tier,
            "tier_name": tier_name(league.tier),
            "week_start": monday.isoformat(),
            "week_end": (monday + timedelta(days=6)).isoformat(),
            "size": n,
            "my_rank": mine["rank"] if mine else None,
            "my_xp": mine["xp"] if mine else 0,
            "last_week_movement": prev.movement if prev else None,
        },
        "members": rows,
    }


def global_board(db: Session, limit: int = 50) -> list[dict]:
    rows = (
        db.query(User)
        .filter(User.league_opt_out.is_(False))
        .order_by(User.xp.desc(), User.created_at)
        .limit(limit)
        .all()
    )
    return [
        {
            "rank": i,
            "username": u.username,
            "xp": u.xp or 0,
            "streak": u.current_streak or 0,
            "tier_name": tier_name(u.league_tier or 0),
        }
        for i, u in enumerate(rows, start=1)
    ]


def monthly_board(db: Session, today: date | None = None, limit: int = 50) -> list[dict]:
    day = today or date.today()
    start = datetime(day.year, day.month, 1, tzinfo=timezone.utc)
    end = datetime(day.year + (day.month == 12), (day.month % 12) + 1, 1, tzinfo=timezone.utc)
    users = db.query(User).filter(User.league_opt_out.is_(False)).all()
    rows = [
        {"username": u.username, "xp": _week_xp(db, u.id, start, end)}
        for u in users
    ]
    rows = [r for r in rows if r["xp"] > 0]
    rows.sort(key=lambda r: (-r["xp"], r["username"]))
    for i, r in enumerate(rows[:limit], start=1):
        r["rank"] = i
    return rows[:limit]


def pattern_board(db: Session, pattern_key: str, limit: int = 50) -> list[dict]:
    from sqlalchemy import func

    from app.models.enums import SubmissionStatus
    from app.models.problem import Problem
    from app.models.submission import Submission

    rows = (
        db.query(
            User.username,
            func.count(func.distinct(Submission.problem_id)).label("solved"),
        )
        .join(Submission, Submission.user_id == User.id)
        .join(Problem, Problem.id == Submission.problem_id)
        .filter(
            User.league_opt_out.is_(False),
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.test_session_id.is_(None),
            Problem.pattern_key == pattern_key,
        )
        .group_by(User.id, User.username)
        .order_by(func.count(func.distinct(Submission.problem_id)).desc(), User.username)
        .limit(limit)
        .all()
    )
    return [
        {"rank": i, "username": username, "solved": solved}
        for i, (username, solved) in enumerate(rows, start=1)
    ]
