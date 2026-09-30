"""Supabase JWT verification (new sb_* keys are ES256 → JWKS, not HS256).

The sole auth path: valid Supabase tokens resolve to the linked local user
(auto-provisioned on first sight). No local passwords, no backend JWTs.
"""

import logging
from functools import lru_cache

import jwt

from app.core.config import settings

logger = logging.getLogger(__name__)


def _jwks_url() -> str:
    return f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"


@lru_cache(maxsize=1)
def _jwks_client() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(_jwks_url())


def verify_supabase_token(token: str) -> dict | None:
    """Return {'sub': str, 'email': str|None} or None when not a Supabase token."""
    if not settings.supabase_configured:
        return None
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1",
            options={"require": ["sub", "exp"]},
        )
        return {"sub": str(payload["sub"]), "email": payload.get("email")}
    except Exception as exc:
        logger.debug("Supabase token verify failed: %s", exc)
        return None


def clear_cache() -> None:
    _jwks_client.cache_clear()


def get_or_create_supabase_user(db, sub: str, email: str | None):
    """Link by supabase_id, else by email, else create. Never raises for
    missing email — falls back to a stable placeholder username."""
    from app.models.user import User

    user = db.query(User).filter(User.supabase_id == sub).first()
    if user is not None:
        return user
    email_norm = (email or "").lower().strip()
    if email_norm:
        user = db.query(User).filter(User.email == email_norm).first()
        if user is not None:
            user.supabase_id = sub
            db.commit()
            db.refresh(user)
            return user
    base = (email_norm.split("@")[0] if email_norm else f"sb_{sub[:8]}")[:24] or f"sb_{sub[:8]}"
    username = base
    for i in range(1, 100):
        if db.query(User).filter(User.username == username).first() is None:
            break
        username = f"{base[:24 - len(str(i)) - 1]}_{i}"
    user = User(
        username=username,
        email=email_norm or f"{sub}@supabase.local",
        hashed_password=None,
        supabase_id=sub,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
