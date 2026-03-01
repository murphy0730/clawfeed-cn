"""Subscription management routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, require_user
from app.models import User
from app import crud
from app.schemas import SubscribeRequest, BulkSubscribeRequest

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


@router.get("")
async def list_subscriptions(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    subs = crud.list_subscriptions(db, user.id)
    return [{**s, "sourceDeleted": bool(s.get("is_deleted"))} for s in subs]


@router.post("")
async def subscribe(
    data: SubscribeRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    source = crud.get_source(db, data.sourceId)
    if not source:
        raise HTTPException(status_code=404, detail="source not found")
    crud.subscribe(db, user.id, data.sourceId)
    return {"ok": True}


@router.post("/bulk")
async def bulk_subscribe(
    data: BulkSubscribeRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    added = crud.bulk_subscribe(db, user.id, data.sourceIds)
    return {"ok": True, "added": added}


@router.delete("/{source_id}")
async def unsubscribe(
    source_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    crud.unsubscribe(db, user.id, source_id)
    return {"ok": True}
