"""Admin control plane: guard, problem CRUD/publish, users."""

import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.problem import Problem
from app.models.user import User
from tests.conftest import make_test_user

client = TestClient(app)


def register_and_login(username=None):
    suffix = uuid.uuid4().hex[:8]
    return make_test_user(
        username=username or f"adm_{suffix}", domain="admintest.com"
    )


def make_admin(user_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).one()
        user.is_admin = True
        db.commit()


def test_non_admin_forbidden():
    headers, _ = register_and_login()
    assert client.get("/api/v1/admin/overview", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/problems", headers=headers).status_code == 403


def test_overview_counts():
    headers, user_id = register_and_login()
    make_admin(user_id)
    body = client.get("/api/v1/admin/overview", headers=headers).json()
    assert body["problems"] >= 587
    assert body["published"] >= 150
    assert body["users"] >= 1


def test_problem_crud_and_publish_flow():
    headers, _ = register_and_login()
    admin_h, admin_id = register_and_login()
    make_admin(admin_id)
    slug = f"admin-probe-{uuid.uuid4().hex[:6]}"

    created = client.post(
        "/api/v1/admin/problems",
        json={
            "title": "Admin Probe",
            "slug": slug,
            "difficulty": "EASY",
            "topic": "ARRAY",
            "is_published": False,
        },
        headers=admin_h,
    )
    assert created.status_code == 201, created.text
    assert created.json()["is_published"] is False

    # public can't see drafts
    assert client.get(f"/api/v1/problems/{slug}", headers=headers).status_code == 404

    # bad starter (no marker) rejected
    bad = client.patch(
        f"/api/v1/admin/problems/{slug}",
        json={"starter_code": {"python": "print(1)"}},
        headers=admin_h,
    )
    assert bad.status_code == 422

    # publish with real content
    good = client.patch(
        f"/api/v1/admin/problems/{slug}",
        json={
            "starter_code": {"python": "x = 1\n# ===== YOUR CODE HERE =====\n"},
            "test_cases": [{"input": "1\n", "expected_output": "1"}],
            "is_published": True,
        },
        headers=admin_h,
    )
    assert good.status_code == 200, good.text
    assert good.json()["solvable"] is True

    assert client.get(f"/api/v1/problems/{slug}", headers=headers).status_code == 200

    # soft-delete hides it again
    assert client.delete(f"/api/v1/admin/problems/{slug}", headers=admin_h).status_code == 200
    assert client.get(f"/api/v1/problems/{slug}", headers=headers).status_code == 404

    # hard-remove the probe so repeated runs don't accumulate drafts
    with SessionLocal() as db:
        db.query(Problem).filter(Problem.slug == slug).delete()
        db.commit()

    # dup slug + bad slug
    dup = client.post(
        "/api/v1/admin/problems",
        json={"title": "x", "slug": "two-sum", "difficulty": "EASY", "topic": "ARRAY"},
        headers=admin_h,
    )
    assert dup.status_code == 409
    bad_slug = client.post(
        "/api/v1/admin/problems",
        json={"title": "x", "slug": "Bad Slug!", "difficulty": "EASY", "topic": "ARRAY"},
        headers=admin_h,
    )
    assert bad_slug.status_code == 422


def test_users_admin_and_grant():
    _h, _uid = register_and_login()
    admin_h, admin_id = register_and_login()
    make_admin(admin_id)

    listing = client.get("/api/v1/admin/users?limit=5", headers=admin_h).json()
    assert listing["total"] >= 2
    target = next(u for u in listing["items"] if u["id"] != str(admin_id))

    promoted = client.patch(
        f"/api/v1/admin/users/{target['id']}", json={"is_admin": True}, headers=admin_h
    ).json()
    assert promoted["is_admin"] is True

    granted = client.patch(
        f"/api/v1/admin/users/{target['id']}", json={"grant_xp": 50}, headers=admin_h
    ).json()
    assert granted["xp"] >= 50

    # cannot demote yourself
    self_dem = client.patch(
        f"/api/v1/admin/users/{admin_id}", json={"is_admin": False}, headers=admin_h
    )
    assert self_dem.status_code == 400
