"""Supabase-only auth: verified tokens auto-provision/link, rest rejected."""

import uuid

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from tests.conftest import make_test_user

client = TestClient(app)


def use_real_auth(monkeypatch):
    """Drop the suite's test-token override so the real Supabase path runs."""
    from app.api import deps as deps_module

    monkeypatch.delitem(app.dependency_overrides, get_current_user)
    return deps_module


def test_supabase_token_auto_provisions(monkeypatch):
    deps_module = use_real_auth(monkeypatch)

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
    headers, _ = make_test_user()
    me = client.get("/api/v1/auth/me", headers=headers).json()

    deps_module = use_real_auth(monkeypatch)
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


def test_garbage_token_rejected(monkeypatch):
    deps_module = use_real_auth(monkeypatch)

    monkeypatch.setattr(deps_module, "verify_supabase_token", lambda token: None)
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401
