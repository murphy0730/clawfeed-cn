"""Sources CRUD + URL resolver routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user, require_user
from app.models import User
from app import crud
from app.schemas import SourceCreate, SourceUpdate, SourceResolveRequest
from app.services.source_resolver import resolve_source_url

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.post("/resolve")
async def resolve_url(
    data: SourceResolveRequest,
    _user: User = Depends(require_user),
):
    url = data.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    try:
        result = await resolve_source_url(url)
        return result
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e) or "cannot resolve")


@router.get("")
async def list_sources(
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user:
        sources = crud.list_sources(db, user_id=user.id, include_public=True)
        sub_ids = {
            s["id"]
            for s in crud.list_subscriptions(db, user.id)
        }
        return [{**s, "subscribed": s["id"] in sub_ids} for s in sources]
    return crud.list_sources(db, include_public=True)


@router.get("/{source_id}")
async def get_source(
    source_id: int,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = crud.get_source(db, source_id)
    if not s:
        raise HTTPException(status_code=404, detail="not found")
    if not s.is_public and (not user or s.created_by != user.id):
        raise HTTPException(status_code=404, detail="not found")
    return {c.name: getattr(s, c.name) for c in s.__table__.columns}


@router.post("", status_code=201)
async def create_source(
    data: SourceCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    s = crud.create_source(
        db,
        name=data.name,
        type=data.type,
        config=data.config,
        is_public=data.isPublic,
        created_by=user.id,
    )
    return {"id": s.id}


@router.put("/{source_id}")
async def update_source(
    source_id: int,
    data: SourceUpdate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    s = crud.get_source(db, source_id)
    if not s:
        raise HTTPException(status_code=404, detail="not found")
    if s.created_by != user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    crud.update_source(db, source_id, data.model_dump(exclude_none=True))
    return {"ok": True}


@router.delete("/{source_id}")
async def delete_source(
    source_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    s = crud.get_source(db, source_id)
    if not s:
        raise HTTPException(status_code=404, detail="not found")
    if s.created_by != user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    crud.delete_source(db, source_id, user.id)
    return {"ok": True}
