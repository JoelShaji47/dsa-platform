"""Admin control plane: content publishing, problem authoring, user oversight."""

import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.enums import Difficulty, Topic
from app.models.problem import Problem
from app.models.user import User
from app.services.gamification import log_xp

router = APIRouter(prefix="/admin", tags=["admin"])

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LANGS = ("python", "cpp", "java")


class TestCaseIn(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False


class ProblemPatch(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    difficulty: Difficulty | None = None
    topic: Topic | None = None
    starter_code: dict[str, str] | None = None
    test_cases: list[TestCaseIn] | None = None
    function_starter: dict[str, str] | None = None
    function_driver: dict[str, dict[str, str]] | None = None
    pattern_key: str | None = Field(default=None, max_length=60)
    companies: list[str] | None = None
    editorial_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
    is_published: bool | None = None


class ProblemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=220)
    difficulty: Difficulty
    topic: Topic
    description: str = "Practice: pending authoring"
    starter_code: dict[str, str] = {}
    test_cases: list[TestCaseIn] = []
    pattern_key: str | None = Field(default=None, max_length=60)
    is_published: bool = False


def _serialize(p: Problem) -> dict:
    return {
        "id": str(p.id),
        "title": p.title,
        "slug": p.slug,
        "description": p.description,
        "difficulty": p.difficulty.value,
        "topic": p.topic.value,
        "starter_code": p.starter_code or {},
        "test_cases": p.test_cases or [],
        "function_starter": p.function_starter or {},
        "function_modes": [
            lang
            for lang, stub in (p.function_starter or {}).items()
            if stub and isinstance((p.function_driver or {}).get(lang), dict)
        ],
        "sources": p.sources or [],
        "pattern_key": p.pattern_key,
        "companies": p.companies or [],
        "editorial_url": p.editorial_url,
        "video_url": p.video_url,
        "is_published": p.is_published,
        "solvable": bool(p.starter_code and p.test_cases),
    }


def _validate_payload(starter: dict | None, cases: list | None) -> None:
    if starter is not None:
        unknown = set(starter) - set(LANGS)
        if unknown:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown starter languages: {sorted(unknown)}",
            )
        for lang, code in starter.items():
            if "YOUR CODE HERE" not in (code or ""):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Starter '{lang}' must contain the YOUR CODE HERE marker",
                )
    if cases is not None:
        if not cases:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Test cases must not be empty when provided",
            )
        for tc in cases:
            tc_dict = tc.model_dump() if isinstance(tc, TestCaseIn) else tc
            if not str(tc_dict.get("input", "")).strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Every test case needs a non-empty input",
                )


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    return {
        "users": db.query(func.count(User.id)).scalar(),
        "admins": db.query(func.count(User.id)).filter(User.is_admin.is_(True)).scalar(),
        "problems": db.query(func.count(Problem.id)).scalar(),
        "published": db.query(func.count(Problem.id))
        .filter(Problem.is_published.is_(True))
        .scalar(),
        "solvable": db.query(func.count(Problem.id))
        .filter(Problem.starter_code != {})
        .scalar(),
        "submissions_7d": db.execute(
            text("SELECT count(*) FROM submissions WHERE submitted_at >= now() - interval '7 days'")
        ).scalar(),
    }


@router.get("/problems")
def list_problems_admin(
    search: str | None = None,
    published: bool | None = None,
    solvable: bool | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    query = db.query(Problem)
    if search:
        query = query.filter(
            or_(Problem.title.ilike(f"%{search}%"), Problem.slug.ilike(f"%{search}%"))
        )
    if published is not None:
        query = query.filter(Problem.is_published.is_(published))
    rows = query.order_by(Problem.title).offset(offset).limit(limit).all()
    items = []
    for p in rows:
        is_solvable = bool(p.starter_code and p.test_cases)
        if solvable is not None and is_solvable != solvable:
            continue
        items.append(
            {
                "slug": p.slug,
                "title": p.title,
                "difficulty": p.difficulty.value,
                "topic": p.topic.value,
                "pattern_key": p.pattern_key,
                "is_published": p.is_published,
                "solvable": is_solvable,
            }
        )
    return {"total": query.count(), "items": items}


@router.get("/problems/{slug}")
def get_problem_admin(
    slug: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    problem = db.query(Problem).filter(Problem.slug == slug).first()
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return _serialize(problem)


@router.patch("/problems/{slug}")
def patch_problem(
    slug: str,
    payload: ProblemPatch,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    problem = db.query(Problem).filter(Problem.slug == slug).first()
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    data = payload.model_dump(exclude_unset=True)
    _validate_payload(data.get("starter_code"), data.get("test_cases"))
    for field, value in data.items():
        if field == "test_cases":
            value = [t.model_dump() if isinstance(t, TestCaseIn) else t for t in value]
        setattr(problem, field, value)
    db.commit()
    db.refresh(problem)
    return _serialize(problem)


@router.post("/problems", status_code=status.HTTP_201_CREATED)
def create_problem(
    payload: ProblemCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    if not SLUG_RE.match(payload.slug):
        raise HTTPException(status_code=422, detail="Invalid slug format")
    if db.query(Problem).filter(Problem.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    _validate_payload(payload.starter_code or None, payload.test_cases or None)
    problem = Problem(
        title=payload.title,
        slug=payload.slug,
        difficulty=payload.difficulty,
        topic=payload.topic,
        description=payload.description,
        starter_code=payload.starter_code,
        test_cases=[t.model_dump() for t in payload.test_cases],
        pattern_key=payload.pattern_key,
        is_published=payload.is_published,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return _serialize(problem)


@router.delete("/problems/{slug}")
def unpublish_problem(
    slug: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    """Soft-delete: unpublishes (history-preserving; use PATCH to re-publish)."""
    problem = db.query(Problem).filter(Problem.slug == slug).first()
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    problem.is_published = False
    db.commit()
    return {"slug": slug, "is_published": False}


class UserPatch(BaseModel):
    is_admin: bool | None = None
    grant_xp: int | None = Field(default=None, ge=1, le=10000)


@router.get("/users")
def list_users_admin(
    search: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    query = db.query(User)
    if search:
        query = query.filter(
            or_(User.username.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"))
        )
    rows = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": query.count(),
        "items": [
            {
                "id": str(u.id),
                "username": u.username,
                "email": u.email,
                "xp": u.xp or 0,
                "current_streak": u.current_streak or 0,
                "streak_freezes": u.streak_freezes or 0,
                "league_tier": u.league_tier or 0,
                "is_admin": bool(u.is_admin),
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in rows
        ],
    }


@router.patch("/users/{user_id}")
def patch_user(
    user_id: uuid.UUID,
    payload: UserPatch,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.is_admin is not None:
        if user.id == admin.id and payload.is_admin is False:
            raise HTTPException(status_code=400, detail="You cannot demote yourself")
        user.is_admin = payload.is_admin
    if payload.grant_xp:
        log_xp(db, user, payload.grant_xp, "grant")
    db.commit()
    db.refresh(user)
    return {"id": str(user.id), "is_admin": bool(user.is_admin), "xp": user.xp}


@router.delete("/league-members/{user_id}")
def remove_league_member(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> dict:
    """Remove a player from ranked play entirely (opts them out)."""
    from app.services import leagues as league_svc

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    league_svc.leave_week(db, user)
    return {"user_id": str(user.id), "opted_out": True}
