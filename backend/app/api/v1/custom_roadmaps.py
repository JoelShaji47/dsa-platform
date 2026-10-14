import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.custom_roadmap import (
    CustomRoadmap,
    CustomRoadmapGeneration,
    CustomRoadmapMember,
    CustomRoadmapStep,
    CustomRoadmapTick,
)
from app.models.user import User
from app.schemas.custom_roadmap import BuildRoadmapPayload, JoinPayload, RoadmapOut, StepOut
from app.services.custom_roadmaps import (
    WEEKLY_LIMIT,
    build_steps,
    default_title,
    generations_this_week,
    new_share_code,
)

router = APIRouter(prefix="/roadmaps/custom", tags=["custom-roadmaps"])


def _can_see(db: Session, roadmap_id, user_id) -> CustomRoadmap | None:
    rm = db.get(CustomRoadmap, roadmap_id)
    if rm is None:
        return None
    if rm.owner_id == user_id:
        return rm
    member = (
        db.query(CustomRoadmapMember)
        .filter(
            CustomRoadmapMember.roadmap_id == roadmap_id,
            CustomRoadmapMember.user_id == user_id,
        )
        .first()
    )
    return rm if member else None


def _serialize(db: Session, rm: CustomRoadmap, user: User) -> RoadmapOut:
    steps = (
        db.query(CustomRoadmapStep)
        .filter(CustomRoadmapStep.roadmap_id == rm.id)
        .order_by(CustomRoadmapStep.position)
        .all()
    )
    my_ticks = {
        t.step_id
        for t in db.query(CustomRoadmapTick)
        .filter(
            CustomRoadmapTick.user_id == user.id,
            CustomRoadmapTick.step_id.in_([s.id for s in steps] or [uuid.uuid4()]),
        )
        .all()
    }
    # Friend progress: owner sees the other member, joiner sees the owner.
    other_id = None
    if rm.owner_id != user.id:
        other_id = rm.owner_id
    else:
        m = (
            db.query(CustomRoadmapMember)
            .filter(CustomRoadmapMember.roadmap_id == rm.id)
            .first()
        )
        other_id = m.user_id if m else None
    friend_done = None
    if other_id is not None:
        friend_done = (
            db.query(CustomRoadmapTick)
            .filter(
                CustomRoadmapTick.user_id == other_id,
                CustomRoadmapTick.step_id.in_([s.id for s in steps] or [uuid.uuid4()]),
            )
            .count()
        )
    return RoadmapOut(
        id=str(rm.id),
        title=rm.title,
        kind=rm.kind,
        level=rm.level,
        goal=rm.goal,
        company=rm.company,
        mins_per_day=rm.mins_per_day,
        total_days=rm.total_days,
        share_code=rm.share_code,
        owner=rm.owner_id == user.id,
        steps=[
            StepOut(
                id=str(s.id),
                position=s.position,
                problem_slug=s.problem_slug,
                title=s.title,
                kind=s.kind,
                pattern_key=s.pattern_key,
                difficulty=s.difficulty,
                est_mins=s.est_mins,
                day_index=s.day_index,
                done=s.id in my_ticks,
                video_url=(s.meta or {}).get("video_url"),
            )
            for s in steps
        ],
        me_done=len(my_ticks),
        total=len(steps),
        friend_done=friend_done,
    )


@router.get("", response_model=list[RoadmapOut])
def list_mine(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owned = db.query(CustomRoadmap).filter(CustomRoadmap.owner_id == current_user.id).all()
    member_ids = [
        r.roadmap_id
        for r in db.query(CustomRoadmapMember)
        .filter(CustomRoadmapMember.user_id == current_user.id)
        .all()
    ]
    joined = db.query(CustomRoadmap).filter(CustomRoadmap.id.in_(member_ids)).all() if member_ids else []
    seen: dict = {}
    for rm in owned + joined:
        seen[str(rm.id)] = rm
    return [_serialize(db, rm, current_user) for rm in sorted(seen.values(), key=lambda r: r.created_at, reverse=True)]


@router.get("/quota")
def quota(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    used = generations_this_week(db, current_user.id)
    return {"used": used, "limit": WEEKLY_LIMIT, "remaining": max(0, WEEKLY_LIMIT - used)}


@router.post("", response_model=RoadmapOut, status_code=status.HTTP_201_CREATED)
def build(
    payload: BuildRoadmapPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    used = generations_this_week(db, current_user.id)
    if used >= WEEKLY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Only 2 roadmaps per 7 days. Join a friend's instead or wait.",
        )
    kind = payload.kind
    if payload.kind == "learn_anything":
        kind = "dsa_build"  # v1: same catalog engine; dedicated templates land next
    steps = build_steps(
        db,
        level=payload.level,
        goal=payload.goal,
        company=payload.company,
        mins_per_day=payload.mins_per_day,
        total_days=payload.total_days,
        target_count=payload.target_count,
        kind=kind if kind in ("dsa_build", "video") else "dsa_build",
    )
    rm = CustomRoadmap(
        owner_id=current_user.id,
        title=payload.title or default_title(payload.level, payload.goal, payload.total_days, payload.company),
        kind=payload.kind,
        level=payload.level,
        goal=payload.goal,
        company=payload.company,
        mins_per_day=payload.mins_per_day,
        total_days=payload.total_days,
        target_count=payload.target_count,
        share_code=new_share_code(db),
    )
    db.add(rm)
    db.flush()
    for s in steps:
        db.add(CustomRoadmapStep(roadmap_id=rm.id, **s))
    db.add(CustomRoadmapGeneration(user_id=current_user.id))
    db.commit()
    db.refresh(rm)
    return _serialize(db, rm, current_user)


@router.post("/join", response_model=RoadmapOut)
def join(
    payload: JoinPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    code = payload.share_code.strip().upper()
    rm = db.query(CustomRoadmap).filter(CustomRoadmap.share_code == code).first()
    if rm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No roadmap with that code")
    if rm.owner_id != current_user.id:
        db.merge(CustomRoadmapMember(roadmap_id=rm.id, user_id=current_user.id))
        db.commit()
    return _serialize(db, rm, current_user)


@router.get("/{roadmap_id}", response_model=RoadmapOut)
def get_one(
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rm = _can_see(db, roadmap_id, current_user.id)
    if rm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return _serialize(db, rm, current_user)


@router.get("/{roadmap_id}/today", response_model=RoadmapOut)
def get_today(
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """One honest list: steps for the current day slice only."""
    rm = _can_see(db, roadmap_id, current_user.id)
    if rm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    full = _serialize(db, rm, current_user)
    created = rm.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    day = min(rm.total_days, max(1, (datetime.now(timezone.utc) - created).days + 1))
    full.steps = [s for s in full.steps if s.day_index == day]
    return full


@router.post("/{roadmap_id}/ticks/{step_id}")
def tick(
    roadmap_id: uuid.UUID,
    step_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rm = _can_see(db, roadmap_id, current_user.id)
    if rm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    step = db.get(CustomRoadmapStep, step_id)
    if step is None or step.roadmap_id != rm.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Step not found")
    db.merge(CustomRoadmapTick(step_id=step.id, user_id=current_user.id))
    db.commit()
    return {"done": True}


@router.delete("/{roadmap_id}/ticks/{step_id}")
def untick(
    roadmap_id: uuid.UUID,
    step_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rm = _can_see(db, roadmap_id, current_user.id)
    if rm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    db.query(CustomRoadmapTick).filter(
        CustomRoadmapTick.step_id == step_id,
        CustomRoadmapTick.user_id == current_user.id,
    ).delete()
    db.commit()
    return {"done": False}


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rm = db.get(CustomRoadmap, roadmap_id)
    if rm is None or rm.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    db.delete(rm)
    db.commit()
    return None
