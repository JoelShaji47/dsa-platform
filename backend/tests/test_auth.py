import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make_user():
    suffix = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{suffix}",
        "email": f"{suffix}@test.com",
        "password": "supersecret1",
    }


def test_register_creates_user_with_defaults():
    data = make_user()
    res = client.post("/api/v1/auth/register", json=data)
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == data["username"]
    assert body["email"] == data["email"]
    assert body["xp"] == 0
    assert body["current_streak"] == 0
    assert "hashed_password" not in body


def test_register_duplicate_email_conflicts():
    data = make_user()
    assert client.post("/api/v1/auth/register", json=data).status_code == 201
    clone = {**data, "username": "different_name"}
    res = client.post("/api/v1/auth/register", json=clone)
    assert res.status_code == 409
    assert "email" in res.json()["detail"]


def test_register_duplicate_username_conflicts():
    data = make_user()
    assert client.post("/api/v1/auth/register", json=data).status_code == 201
    clone = {**data, "email": f"{uuid.uuid4().hex[:8]}@test.com"}
    res = client.post("/api/v1/auth/register", json=clone)
    assert res.status_code == 409
    assert "username" in res.json()["detail"]


def test_register_rejects_short_password():
    data = {**make_user(), "password": "short"}
    res = client.post("/api/v1/auth/register", json=data)
    assert res.status_code == 422


def test_login_by_email_and_by_username():
    data = make_user()
    client.post("/api/v1/auth/register", json=data)
    by_email = client.post(
        "/api/v1/auth/login",
        data={"username": data["email"], "password": data["password"]},
    )
    by_username = client.post(
        "/api/v1/auth/login",
        data={"username": data["username"], "password": data["password"]},
    )
    assert by_email.status_code == 200
    assert by_username.status_code == 200
    assert by_email.json()["token_type"] == "bearer"
    assert len(by_email.json()["access_token"]) > 100


def test_login_wrong_password_401():
    data = make_user()
    client.post("/api/v1/auth/register", json=data)
    res = client.post(
        "/api/v1/auth/login", data={"username": data["email"], "password": "wrongpass99"}
    )
    assert res.status_code == 401


def test_me_requires_token():
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_profile_with_valid_token():
    data = make_user()
    client.post("/api/v1/auth/register", json=data)
    login = client.post(
        "/api/v1/auth/login",
        data={"username": data["email"], "password": data["password"]},
    )
    token = login.json()["access_token"]
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["username"] == data["username"]
