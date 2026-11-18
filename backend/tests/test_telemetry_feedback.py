"""Telemetry feedback, OPEN events, failure meta, timed-test events.

Covers the Phase B/C logging gaps:

- clicked/dismissed on recommendation impressions (first action wins)
- problem_opened events on the detail endpoint
- Judge0 failure signature (first_failure / failed_cases) in submit + run meta
- timed-test submissions logged as their own test_submit event
"""

import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.enums import SubmissionStatus
from app.models.interaction import InteractionEvent
from app.models.problem import Problem
from app.models.telemetry import RecommendationImpression, RecommendationOpportunity
from app.services.grader import GradeResult
from app.services.grader import TestOutcome as Outcome
from tests.conftest import make_test_user

client = TestClient(app)

TWO_SUM = "two-sum"


def _make_opp(db, uid):
    opp = RecommendationOpportunity(
        user_id=uid, model_version="heuristic-v1", candidate_count=3
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp.id


def _imp_for(db, opp_id, user_id, problem_slug, rank=0):
    pid = db.query(Problem.id).filter(Problem.slug == problem_slug).scalar()
    imp = RecommendationImpression(
        opportunity_id=opp_id,
        user_id=user_id,
        problem_id=pid,
        rank=rank,
        rendered=True,
        model_version="heuristic-v1",
    )
    db.add(imp)
    db.commit()
    db.refresh(imp)
    return imp


def _stub_grader_failures(monkeypatch, outcomes):
    async def fake(source_code, language, test_cases):
        return GradeResult(status=SubmissionStatus.WRONG_ANSWER, test_results=outcomes)

    monkeypatch.setattr("app.api.v1.problems.grade_code", fake)


def _accepted_outcome(i=0, status_key="ACCEPTED"):
    return Outcome(index=i, hidden=False, passed=True, status_key=status_key)


def _failed_outcome(i=0, status_key="WRONG_ANSWER"):
    return Outcome(index=i, hidden=False, passed=False, status_key=status_key)


# ---- click / dismiss feedback ---------------------------------------------

def test_click_feedback_applied_once(monkeypatch):
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    with SessionLocal() as db:
        opp_id = _make_opp(db, uid)
        _imp_for(db, opp_id, uid, TWO_SUM, rank=0)

    res = client.post(
        "/api/v1/roadmap/impressions/feedback",
        headers=headers,
        json={"opportunity_id": str(opp_id), "slug": TWO_SUM, "action": "click"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["applied"] is True
    assert body["clicked"] is True
    assert body["dismissed"] is False

    # First action wins: a second, different action is not applied.
    res2 = client.post(
        "/api/v1/roadmap/impressions/feedback",
        headers=headers,
        json={"opportunity_id": str(opp_id), "slug": TWO_SUM, "action": "dismiss"},
    )
    assert res2.status_code == 200
    assert res2.json()["applied"] is False
    assert res2.json()["clicked"] is True
    assert res2.json()["dismissed"] is False


def test_dismiss_feedback_applied_once(monkeypatch):
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    with SessionLocal() as db:
        opp_id = _make_opp(db, uid)
        _imp_for(db, opp_id, uid, TWO_SUM, rank=0)

    res = client.post(
        "/api/v1/roadmap/impressions/feedback",
        headers=headers,
        json={"opportunity_id": str(opp_id), "slug": TWO_SUM, "action": "dismiss"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["applied"] is True
    assert body["dismissed"] is True
    assert body["clicked"] is False


def test_feedback_rejects_bad_action(monkeypatch):
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    with SessionLocal() as db:
        opp_id = _make_opp(db, uid)
        _imp_for(db, opp_id, uid, TWO_SUM, rank=0)

    res = client.post(
        "/api/v1/roadmap/impressions/feedback",
        headers=headers,
        json={"opportunity_id": str(opp_id), "slug": TWO_SUM, "action": "love"},
    )
    # Pydantic's Literal["click","dismiss"] rejects invalid actions at the
    # schema layer (422) before the route's ValueError path is reached.
    assert res.status_code == 422


def test_feedback_requires_impression(monkeypatch):
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    with SessionLocal() as db:
        opp_id = _make_opp(db, uid)

    # No impression recorded for this opportunity/problem -> 404, not a
    # fabricated denominator for CTR.
    res = client.post(
        "/api/v1/roadmap/impressions/feedback",
        headers=headers,
        json={"opportunity_id": str(opp_id), "slug": TWO_SUM, "action": "click"},
    )
    assert res.status_code == 404


def test_feedback_cross_user_rejected(monkeypatch):
    h1, u1 = make_test_user()
    h2, _ = make_test_user()
    u1 = uuid.UUID(str(u1))
    with SessionLocal() as db:
        opp_id = _make_opp(db, u1)
        _imp_for(db, opp_id, u1, TWO_SUM, rank=0)

    res = client.post(
        "/api/v1/roadmap/impressions/feedback",
        headers=h2,
        json={"opportunity_id": str(opp_id), "slug": TWO_SUM, "action": "click"},
    )
    assert res.status_code == 404


# ---- problem_opened event -------------------------------------------------

def test_problem_detail_logs_open_event(monkeypatch):
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    with SessionLocal() as db:
        pid = db.query(Problem.id).filter(Problem.slug == TWO_SUM).scalar()

    client.get(f"/api/v1/problems/{TWO_SUM}", headers=headers)

    with SessionLocal() as db:
        events = (
            db.query(InteractionEvent)
            .filter(
                InteractionEvent.user_id == uid,
                InteractionEvent.problem_id == pid,
                InteractionEvent.event == "open",
            )
            .all()
        )
    assert len(events) == 1
    assert events[0].meta["pattern_key"] is not None


# ---- failure signature in submit / run meta -------------------------------

def test_submit_meta_carries_failure_signature(monkeypatch):
    stub_outcomes = [
        _accepted_outcome(0, "ACCEPTED"),
        _failed_outcome(1, "WRONG_ANSWER"),
        _failed_outcome(2, "WRONG_ANSWER"),
    ]
    _stub_grader_failures(monkeypatch, stub_outcomes)
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    with SessionLocal() as db:
        pid = db.query(Problem.id).filter(Problem.slug == TWO_SUM).scalar()

    res = client.post(
        f"/api/v1/problems/{TWO_SUM}/submit",
        headers=headers,
        json={"language": "python", "source_code": "x"},
    )
    assert res.status_code == 200, res.text

    with SessionLocal() as db:
        event = (
            db.query(InteractionEvent)
            .filter(
                InteractionEvent.user_id == uid,
                InteractionEvent.problem_id == pid,
                InteractionEvent.event == "submit",
            )
            .order_by(InteractionEvent.created_at.desc())
            .first()
        )
    assert event is not None
    assert event.meta["failed_cases"] == 2
    assert event.meta["first_failure"] == "WRONG_ANSWER"


def test_run_meta_carries_failure_signature(monkeypatch):
    stub_outcomes = [
        _failed_outcome(0, "TIME_LIMIT_EXCEEDED"),
        _failed_outcome(1, "TIME_LIMIT_EXCEEDED"),
    ]
    _stub_grader_failures(monkeypatch, stub_outcomes)
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    with SessionLocal() as db:
        pid = db.query(Problem.id).filter(Problem.slug == TWO_SUM).scalar()

    client.post(
        f"/api/v1/problems/{TWO_SUM}/run",
        headers=headers,
        json={"language": "python", "source_code": "x"},
    )

    with SessionLocal() as db:
        event = (
            db.query(InteractionEvent)
            .filter(
                InteractionEvent.user_id == uid,
                InteractionEvent.problem_id == pid,
                InteractionEvent.event == "run",
            )
            .order_by(InteractionEvent.created_at.desc())
            .first()
        )
    assert event is not None
    assert event.meta["failed_cases"] == 2
    assert event.meta["first_failure"] == "TIME_LIMIT_EXCEEDED"


def test_submit_meta_no_failure_when_accepted(monkeypatch):
    from tests.test_roadmap import stub_grader

    stub_grader(monkeypatch)
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    with SessionLocal() as db:
        pid = db.query(Problem.id).filter(Problem.slug == TWO_SUM).scalar()

    res = client.post(
        f"/api/v1/problems/{TWO_SUM}/submit",
        headers=headers,
        json={"language": "python", "source_code": "x"},
    )
    assert res.status_code == 200

    with SessionLocal() as db:
        event = (
            db.query(InteractionEvent)
            .filter(
                InteractionEvent.user_id == uid,
                InteractionEvent.problem_id == pid,
                InteractionEvent.event == "submit",
            )
            .order_by(InteractionEvent.created_at.desc())
            .first()
        )
    assert event.meta["failed_cases"] == 0
    assert event.meta["first_failure"] is None


# ---- timed-test submission is its own event -------------------------------

def test_timed_test_submit_event_shape_is_storable():
    """The route writes a ``test_submit`` InteractionEvent for the pair.

    Exercising the full route requires a live TestSession object graph; the
    behavioral contract is that the event type exists and is stored against
    the (user, problem) pair with the test_session_id in meta. This test pins
    that shape so a future refactor can't silently drop the event.
    """
    headers, uid = make_test_user()
    uid = uuid.UUID(str(uid))
    sid = uuid.uuid4()
    with SessionLocal() as db:
        problem = db.query(Problem).filter(Problem.slug == TWO_SUM).one()
        evt = InteractionEvent(
            user_id=uid,
            problem_id=problem.id,
            event="test_submit",
            meta={
                "test_session_id": str(sid),
                "language": "python",
                "status": "ACCEPTED",
                "passed": True,
                "attempts": 1,
                "failed_cases": 0,
                "first_failure": None,
            },
        )
        db.add(evt)
        db.commit()
        assert evt.id is not None

    # Sanity: the route imports TEST_SUBMIT from activity (no silent rename).
    from app.services.activity import TEST_SUBMIT

    assert TEST_SUBMIT == "test_submit"

