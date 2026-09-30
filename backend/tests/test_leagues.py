"""Weekly leagues: cohorts, boards, promotion/relegation, champion badge."""

import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from tests.conftest import make_test_user
from app.models.user import User
from app.services import leagues
from app.services.gamification import BADGE_DEFINITIONS, log_xp

client = TestClient(app)


def register(username=None):
    suffix = uuid.uuid4().hex[:8]
    return make_test_user(
        username=username or f"lg_{suffix}", domain="leaguetest.com"
    )


def monday(n_weeks_ago=0):
    today = date.today() - timedelta(weeks=n_weeks_ago)
    return today - timedelta(days=today.weekday())


def test_board_seeds_cohort_and_ranks_by_week_xp():
    h1, u1 = register()
    h2, _ = register()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for u in (u1,):
            user = db.query(User).filter(User.id == u).one()
            log_xp(db, user, 40, "solve", created_at=now - timedelta(days=1))
            db.commit()

    body = client.get("/api/v1/leagues/me", headers=h1).json()
    assert body["league"]["tier_name"] in leagues.TIERS
    assert body["league"]["size"] >= 2
    assert body["league"]["size"] <= leagues.COHORT_SIZE
    mine = next(m for m in body["members"] if m["is_me"])
    assert mine["xp"] == 40
    assert body["members"][0]["xp"] >= body["members"][-1]["xp"]
    assert all("zone" in m for m in body["members"])

    other = client.get("/api/v1/leagues/me", headers=h2).json()
    assert other["league"]["id"] == body["league"]["id"]


def test_rollover_promotes_relegates_and_crowns_champion():
    from app.models.league import League

    users = [register() for _ in range(12)]
    last_monday = monday(1)
    with SessionLocal() as db:
        # Hermetic week: drop this-week-and-newer leagues so seeding starts
        # from our 12 users (stale same-week shells from earlier runs would
        # otherwise swallow the join and shrink the cohort).
        db.query(League).filter(League.week_start >= last_monday).delete()
        db.commit()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for i, (_h, uid) in enumerate(users):
            user = db.query(User).filter(User.id == uid).one()
            # staggered XP across last week: user 0 earns most (uncontested top),
            # last user earns nothing (uncontested bottom).
            amount = 5000 if i == 0 else ((12 - i) * 10 if i < 11 else 0)
            if amount:
                log_xp(db, user, amount, "solve",
                       created_at=datetime.combine(last_monday, datetime.min.time()).replace(tzinfo=timezone.utc) + timedelta(days=1))
        db.commit()
        leagues.ensure_current_season(db, today=last_monday)
        me = db.query(User).filter(User.id == users[0][1]).one()
        board = leagues.board(db, me, today=last_monday)
        assert board["league"]["size"] >= 12
        # roll into this week -> finalize last week
        leagues.ensure_current_season(db, today=last_monday + timedelta(days=8))

    with SessionLocal() as db:
        from app.models.league import League, LeagueMember

        champ = db.query(User).filter(User.id == users[0][1]).one()
        assert champ.league_tier == 1
        last = db.query(User).filter(User.id == users[-1][1]).one()
        assert last.league_tier == 0  # floor: can't go below Bronze
        # Whoever topped our cohort must hold the champion badge.
        mine = (
            db.query(LeagueMember)
            .join(League, League.id == LeagueMember.league_id)
            .filter(
                League.week_start == last_monday,
                LeagueMember.user_id == users[0][1],
            )
            .one()
        )
        top = (
            db.query(LeagueMember)
            .filter(
                LeagueMember.league_id == mine.league_id,
                LeagueMember.final_rank == 1,
            )
            .one()
        )
        assert top.final_xp and top.final_xp > 0
        from app.models.badge import Badge, UserBadge

        champion = db.query(Badge).filter(Badge.criteria == "WEEKLY_CHAMPION").one()
        assert (
            db.query(UserBadge.id)
            .filter(UserBadge.user_id == top.user_id, UserBadge.badge_id == champion.id)
            .first()
            is not None
        )
        badges = client.get("/api/v1/badges/me", headers=users[0][0]).json()
        assert len(badges) == len(BADGE_DEFINITIONS)


def test_global_and_monthly_boards():
    h, u = register()
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == u).one()
        log_xp(db, user, 25, "solve")
        db.commit()
        username = user.username
    glob = client.get("/api/v1/leagues/global", headers=h).json()["board"]
    assert glob[0]["rank"] == 1
    assert all("tier_name" in r for r in glob)
    monthly_ep = client.get("/api/v1/leagues/monthly", headers=h).json()["board"]
    assert monthly_ep and all("rank" in r and "xp" in r for r in monthly_ep)
    with SessionLocal() as db:
        wide = leagues.monthly_board(db, limit=10000)
    assert any(r["username"] == username and r["xp"] >= 25 for r in wide)


def test_leave_rejoin_and_admin_remove():
    headers, user_id = register()
    body = client.get("/api/v1/leagues/me", headers=headers).json()
    assert body["league"] is not None

    left = client.delete("/api/v1/leagues/me", headers=headers).json()
    assert left["opted_out"] is True
    gone = client.get("/api/v1/leagues/me", headers=headers).json()
    assert gone["league"] is None
    assert gone["opted_out"] is True

    back = client.post("/api/v1/leagues/rejoin", headers=headers).json()
    assert back["league"] is not None

    admin_h, admin_id = register()
    with SessionLocal() as db:
        from app.models.user import User as _U

        db.query(_U).filter(_U.id == admin_id).one().is_admin = True
        db.commit()
    removed = client.delete(
        f"/api/v1/admin/league-members/{user_id}", headers=admin_h
    ).json()
    assert removed["opted_out"] is True
    assert client.get("/api/v1/leagues/me", headers=headers).json()["league"] is None

    # non-admin cannot remove
    other_h, _ = register()
    assert (
        client.delete(f"/api/v1/admin/league-members/{user_id}", headers=other_h).status_code
        == 403
    )
