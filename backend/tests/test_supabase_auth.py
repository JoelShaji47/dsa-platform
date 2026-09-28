"""Supabase dual-mode auth: valid Supabase JWT auto-provisions, legacy still works."""

import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def register_and_login():
    suffix = uuid.uuid4().hex[:8]
    data = {
        "username": f"sb_{suffix}",
        "email": f"sb_{suffix}@test.com",
        "password": "supersecret1",
    }
    client.post("/api/v1/auth/register", json=data)
    login = client.post(
        "/api/v1/auth/login",
        data={"username": data["email"], "password": data["password"]},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_supabase_token_auto_provisions(monkeypatch):
    from app.api import deps as deps_module

    sub = f"supabase-uid-{uuid.uuid4().hex[:8]}"
    seen = {}

    def fake_verify(token: str):
        seen["token"] = token
        if token == "sb-valid":
            return {"sub": sub, "email": "New_User@Test.com"}
        return None

    monkeypatch.setattr(deps_module, "verify_supabase_token", fake_verify)

    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer sb-valid"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == "new_user@test.com"
    assert seen["token"] == "sb-valid"

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == "new_user@test.com").one()
        assert user.supabase_id == sub
        assert user.hashed_password is None

    # Second call links, doesn't duplicate.
    r2 = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer sb-valid"})
    assert r2.json()["id"] == body["id"]


def test_supabase_token_links_existing_email(monkeypatch):
    from app.api import deps as deps_module

    headers = register_and_login()
    me = client.get("/api/v1/auth/me", headers=headers).json()
    sub = f"supabase-uid-{uuid.uuid4().hex[:8]}"

    def fake_verify(token: str):
        if token == "sb-link":
            return {"sub": sub, "email": me["email"]}
        return None

    monkeypatch.setattr(deps_module, "verify_supabase_token", fake_verify)
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer sb-link"})
    assert r.status_code == 200
    assert r.json()["id"] == me["id"]

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == me["email"]).one()
        assert user.supabase_id == sub


def test_legacy_login_still_works():
    headers = register_and_login()
    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 200


def test_garbage_token_rejected(monkeypatch):
    from app.api import deps as deps_module

    monkeypatch.setattr(deps_module, "verify_supabase_token", lambda token: None)
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401
