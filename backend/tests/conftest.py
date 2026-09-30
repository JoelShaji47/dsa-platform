import uuid

import pytest
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import SessionLocal, get_db
from app.main import app
from app.models.user import User

_bearer = HTTPBearer(auto_error=False)

# Maps throwaway test tokens ("test-token-<uuid>") to user ids. Lets the
# suite authenticate without any password flow — Supabase is the only
# real auth path, and it can't run offline.
_test_tokens: dict[str, uuid.UUID] = {}


def _fake_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    from fastapi import HTTPException, status

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user_id = _test_tokens.get(credentials.credentials)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return user


app.dependency_overrides[get_current_user] = _fake_current_user


def make_test_user(username=None, email=None, domain="test.com"):
    """Insert a user row directly and return (headers, user_id).

    Replaces the old register+login HTTP flow everywhere — auth is
    Supabase-only now, so tests mint a local token instead.
    """
    suffix = uuid.uuid4().hex[:8]
    with SessionLocal() as db:
        user = User(
            username=username or f"user_{suffix}",
            email=email or f"{suffix}@{domain}",
            hashed_password=None,
            supabase_id=f"test-sub-{suffix}",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
    token = f"test-token-{user_id}"
    _test_tokens[token] = user_id
    return {"Authorization": f"Bearer {token}"}, user_id


@pytest.fixture(autouse=True)
def purge_test_users():
    """Drop accounts created by the suite so runs do not accumulate in the
    real database. Related rows (submissions, test sessions, badges, events)
    go with them via ON DELETE CASCADE."""
    yield
    _test_tokens.clear()
    with SessionLocal() as db:
        for domain in ("%@test.com", "%@leaguetest.com", "%@admintest.com"):
            db.query(User).filter(User.email.like(domain)).delete(
                synchronize_session=False
            )
        db.commit()
