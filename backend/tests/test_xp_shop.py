"""XP ledger + streak-freeze shop."""

import uuid
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from tests.conftest import make_test_user
from app.models.enums import SubmissionStatus
from app.models.user import User
from app.models.xp_event import XpEvent
from app.services.gamification import FREEZE_COST, MAX_FREEZES, update_streak
from app.services.grader import GradeResult, TestOutcome as Outcome

client = TestClient(app)


def register_and_login():
    suffix = uuid.uuid4().hex[:8]
    return make_test_user(username=f"shop_{suffix}")


def stub_accept(monkeypatch):
    async def fake(source_code, language, test_cases):
        return GradeResult(
            status=SubmissionStatus.ACCEPTED,
            test_results=[
                Outcome(index=i, hidden=False, passed=True, status_key="ACCEPTED")
                for i in range(len(test_cases))
            ],
        )

    monkeypatch.setattr("app.api.v1.problems.grade_code", fake)


def give_xp(user_id, amount=500):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.xp = (user.xp or 0) + amount
        db.commit()


def test_solve_writes_ledger(monkeypatch):
    stub_accept(monkeypatch)
    headers, user_id = register_and_login()
    client.post(
        "/api/v1/problems/two-sum/submit",
        json={"language": "python", "source_code": "sol"},
        headers=headers,
    )
    with SessionLocal() as db:
        events = (
            db.query(XpEvent)
            .filter(XpEvent.user_id == user_id, XpEvent.reason == "solve")
            .all()
        )
        assert len(events) == 1
        assert events[0].amount == 16
        user = db.query(User).filter(User.id == user_id).one()
        assert user.xp == 16


def test_shop_buy_freeze_and_guardrails():
    headers, user_id = register_and_login()

    empty = client.get("/api/v1/shop", headers=headers).json()
    assert empty["xp"] == 0 and empty["freezes"] == 0

    broke = client.post("/api/v1/shop/freeze", headers=headers)
    assert broke.status_code == 402

    give_xp(user_id, FREEZE_COST * MAX_FREEZES + 50)
    for _ in range(MAX_FREEZES):
        r = client.post("/api/v1/shop/freeze", headers=headers)
        assert r.status_code == 200, r.text
    full = client.post("/api/v1/shop/freeze", headers=headers)
    assert full.status_code == 400

    status = client.get("/api/v1/shop", headers=headers).json()
    assert status["freezes"] == MAX_FREEZES
    assert status["xp"] == 50

    with SessionLocal() as db:
        buys = (
            db.query(XpEvent)
            .filter(XpEvent.user_id == user_id, XpEvent.reason == "freeze_buy")
            .all()
        )
        assert len(buys) == MAX_FREEZES
        assert all(b.amount == -FREEZE_COST for b in buys)


def test_freeze_covers_one_missed_day():
    _headers, user_id = register_and_login()
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.current_streak = 5
        user.last_active_date = date.today() - timedelta(days=2)
        user.streak_freezes = 2
        db.commit()
        update_streak(user)
        assert user.current_streak == 5
        assert user.streak_freezes == 1
        assert user.last_active_date == date.today()
        db.commit()


def test_no_freeze_resets_streak():
    _headers, user_id = register_and_login()
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.current_streak = 5
        user.last_active_date = date.today() - timedelta(days=3)
        user.streak_freezes = 0
        db.commit()
        update_streak(user)
        assert user.current_streak == 1
        db.commit()


def test_weekly_xp_sums_from_ledger(monkeypatch):
    from datetime import datetime, timedelta, timezone

    from app.services.gamification import log_xp, xp_earned_between

    _headers, user_id = register_and_login()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        log_xp(db, user, 30, "solve", created_at=now - timedelta(days=2))
        log_xp(db, user, 20, "solve", created_at=now - timedelta(days=10))
        log_xp(db, user, -100, "freeze_buy", created_at=now - timedelta(days=1))
        db.commit()
        week = xp_earned_between(db, user_id, now - timedelta(days=7), now)
        assert week == 30


def test_score_breakdown_rewards_streak_clean_and_weak():
    from datetime import date

    from app.models.problem import Problem
    from app.services.gamification import score_solve

    _headers, user_id = register_and_login()
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        problem = db.query(Problem).filter(Problem.slug == "two-sum").one()
        # fresh user: clean first try in untouched pattern
        total, parts = score_solve(db, user, problem, hints_used=False, prior_attempts=0)
        assert total == 16
        assert parts == {"base": 10, "streak_mult": 1.0, "clean_mult": 1.25, "weak_mult": 1.25, "total": 16}
        # streak scales: 10-day streak, dirty solve in mastered pattern
        user.current_streak = 10
        user.last_active_date = date.today()
        total2, parts2 = score_solve(db, user, problem, hints_used=True, prior_attempts=4)
        assert parts2["streak_mult"] == 1.5
        assert parts2["clean_mult"] == 1.0
        assert total2 == int(round(10 * 1.5 * 1.0 * parts2["weak_mult"]))
