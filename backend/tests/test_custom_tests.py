"""Custom timed tests: timers + question count + hand-picked slugs (one by one)."""

import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.enums import Topic
from app.models.problem import Problem
from tests.conftest import make_test_user

client = TestClient(app)


def _headers():
    headers, _ = make_test_user()
    return headers


def _create(headers, payload):
    r = client.post("/api/v1/tests", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def _solvable_slugs(limit=4):
    with SessionLocal() as db:
        rows = (
            db.query(Problem)
            .filter(
                Problem.is_published.is_(True),
                Problem.starter_code != {"__none__": True},
            )
            .limit(50)
            .all()
        )
        out = [p.slug for p in rows if p.starter_code and p.test_cases][:limit]
    assert len(out) >= limit, "seed DB must have solvable problems"
    return out


def test_config_exposes_custom_options():
    body = client.get("/api/v1/tests/config", headers=_headers()).json()
    assert body["default_duration_seconds"] == 3600
    assert 900 in body["duration_options_seconds"]
    assert 7200 in body["duration_options_seconds"]
    assert body["max_questions"] == 6


def test_custom_timer_is_respected():
    body = _create(
        _headers(),
        {"topics": [Topic.ARRAY.value], "duration_seconds": 900, "num_questions": 1},
    )
    assert body["duration_seconds"] == 900
    assert len(body["problems"]) == 1


def test_custom_count_five_balanced():
    body = _create(
        _headers(),
        {"topics": [Topic.ARRAY.value, Topic.DP.value], "num_questions": 5},
    )
    assert len(body["problems"]) == 5
    assert [p["position"] for p in body["problems"]] == [1, 2, 3, 4, 5]
    assert len({p["problem_id"] for p in body["problems"]}) == 5


def test_custom_difficulty_mix():
    body = _create(
        _headers(),
        {
            "topics": [Topic.ARRAY.value],
            "num_questions": 2,
            "difficulties": ["EASY", "EASY"],
        },
    )
    assert [p["difficulty"] for p in body["problems"]] == ["EASY", "EASY"]


def test_hand_picked_slugs_keep_order():
    slugs = _solvable_slugs(3)
    body = _create(
        _headers(),
        {"topics": [Topic.ARRAY.value], "problem_slugs": slugs},
    )
    assert [p["slug"] for p in body["problems"]] == slugs


def test_duplicate_slugs_rejected():
    slugs = _solvable_slugs(2)
    r = client.post(
        "/api/v1/tests",
        json={"topics": [Topic.ARRAY.value], "problem_slugs": [slugs[0], slugs[0]]},
        headers=_headers(),
    )
    assert r.status_code == 422


def test_unknown_slug_rejected():
    r = client.post(
        "/api/v1/tests",
        json={"topics": [Topic.ARRAY.value], "problem_slugs": ["no-such-problem-xyz"]},
        headers=_headers(),
    )
    assert r.status_code == 422


def test_difficulty_count_mismatch_rejected():
    r = client.post(
        "/api/v1/tests",
        json={
            "topics": [Topic.ARRAY.value],
            "num_questions": 3,
            "difficulties": ["EASY"],
        },
        headers=_headers(),
    )
    assert r.status_code == 422
