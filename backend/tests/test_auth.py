"""Supabase-only auth: /me accepts verified tokens, rejects everything else.

There is no register/login endpoint anymore — sign-up and sign-in happen
directly against Supabase. The suite mints local test tokens (see conftest)
instead of going through any password flow.
"""

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_test_user

client = TestClient(app)


def test_me_requires_token():
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_rejects_malformed_authorization():
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Authorization": "Token abc"}
        ).status_code
        == 401
    )


def test_me_rejects_unknown_token():
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer test-token-00000000-0000-0000-0000-000000000000"},
    )
    assert res.status_code == 401


def test_me_returns_profile_with_valid_token():
    headers, user_id = make_test_user()
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == str(user_id)
    assert body["email"].endswith("@test.com")
    assert "hashed_password" not in body


def test_no_password_endpoints_remain():
    assert client.post("/api/v1/auth/register", json={}).status_code == 404
    assert client.post("/api/v1/auth/login", data={}).status_code == 404
