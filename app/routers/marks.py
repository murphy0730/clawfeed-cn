"""Marks (bookmarks) routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, require_user
from app.models import User
from app import crud
from app.schemas import MarkCreate, MarkLegacyCreate

router = APIRouter(tags=["marks"])


@router.get("/api/marks")
async def list_marks(
    status: str | None = None,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    marks = crud.list_marks(db, user_id=user.id, status=status)
    return [
        {
            "id": m.id,
            "url": m.url,
            "title": m.title,
            "note": m.note,
            "status": m.status,
            "created_at": m.created_at,
        }
        for m in marks
    ]


@router.post("/api/marks")
async def create_mark(
    data: MarkCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    result = crud.create_mark(db, url=data.url, user_id=user.id, title=data.title, note=data.note)
    return {"ok": True, **result}


@router.delete("/api/marks/{mark_id}")
async def delete_mark(
    mark_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    crud.delete_mark(db, mark_id, user.id)
    return {"ok": True}


# ── Backward-compat endpoints ──


@router.post("/mark")
async def legacy_create_mark(
    data: MarkLegacyCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    url = (data.url or "").split("?")[0]
    if not url:
        raise HTTPException(status_code=400, detail="invalid url")
    result = crud.create_mark(db, url=url, user_id=user.id)
    return {
        "ok": True,
        "status": "already_marked" if result["duplicate"] else "marked",
    }


@router.get("/marks")
async def legacy_list_marks(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    marks = crud.list_marks(db, user_id=user.id)
    history = [
        {
            "action": "processed" if m.status == "processed" else "mark",
            "target": m.url,
            "at": m.created_at,
            "title": m.title or "",
        }
        for m in marks
    ]
    return {
        "tweets": [
            {"url": m.url, "markedAt": m.created_at}
            for m in marks
            if m.status == "pending"
        ],
        "history": history,
    }
