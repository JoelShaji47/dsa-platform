"""Custom roadmaps: build, quota, ticks, friend join (shared plan, separate ticks)."""

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_test_user

client = TestClient(app)

PAYLOAD = {
    "level": "basics",
    "goal": "fundamentals",
    "mins_per_day": 60,
    "total_days": 14,
}


def test_build_returns_ordered_steps():
    headers, _ = make_test_user()
    r = client.post("/api/v1/roadmaps/custom", json=PAYLOAD, headers=headers)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["total"] > 0
    assert len(body["share_code"]) == 6
    positions = [s["position"] for s in body["steps"]]
    assert positions == sorted(positions)
    assert all(s["problem_slug"] for s in body["steps"])


def test_weekly_limit_is_two():
    headers, _ = make_test_user()
    assert client.post("/api/v1/roadmaps/custom", json=PAYLOAD, headers=headers).status_code == 201
    assert client.post("/api/v1/roadmaps/custom", json=PAYLOAD, headers=headers).status_code == 201
    third = client.post("/api/v1/roadmaps/custom", json=PAYLOAD, headers=headers)
    assert third.status_code == 429
    quota = client.get("/api/v1/roadmaps/custom/quota", headers=headers).json()
    assert quota == {"used": 2, "limit": 2, "remaining": 0}


def test_ticks_and_today():
    headers, _ = make_test_user()
    rm = client.post("/api/v1/roadmaps/custom", json=PAYLOAD, headers=headers).json()
    step = rm["steps"][0]
    tick = client.post(
        f"/api/v1/roadmaps/custom/{rm['id']}/ticks/{step['id']}", headers=headers
    )
    assert tick.status_code == 200
    full = client.get(f"/api/v1/roadmaps/custom/{rm['id']}", headers=headers).json()
    assert full["me_done"] == 1
    today = client.get(f"/api/v1/roadmaps/custom/{rm['id']}/today", headers=headers).json()
    assert today["total"] == full["total"]
    assert all(s["day_index"] == 1 for s in today["steps"])


def test_friend_join_shares_plan_with_separate_ticks():
    headers_a, _ = make_test_user()
    headers_b, _ = make_test_user()
    rm = client.post("/api/v1/roadmaps/custom", json=PAYLOAD, headers=headers_a).json()

    joined = client.post(
        "/api/v1/roadmaps/custom/join",
        json={"share_code": rm["share_code"]},
        headers=headers_b,
    )
    assert joined.status_code == 200, joined.text
    assert joined.json()["id"] == rm["id"]

    # B ticks step 1; A must still show 0 for self but see friend progress.
    step = rm["steps"][0]
    client.post(
        f"/api/v1/roadmaps/custom/{rm['id']}/ticks/{step['id']}", headers=headers_b
    )
    view_a = client.get(f"/api/v1/roadmaps/custom/{rm['id']}", headers=headers_a).json()
    assert view_a["me_done"] == 0
    assert view_a["friend_done"] == 1

    bad = client.post(
        "/api/v1/roadmaps/custom/join", json={"share_code": "ZZZZZZ"}, headers=headers_b
    )
    assert bad.status_code == 404
