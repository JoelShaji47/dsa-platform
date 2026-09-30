from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.supabase_auth import get_or_create_supabase_user, verify_supabase_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_exception
    # Supabase JWT (ES256 via JWKS) — the only accepted credential.
    # First sight auto-provisions the linked local row.
    claims = verify_supabase_token(credentials.credentials)
    if claims is None:
        raise credentials_exception
    try:
        return get_or_create_supabase_user(db, claims["sub"], claims.get("email"))
    except Exception:
        db.rollback()
        raise credentials_exception


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
