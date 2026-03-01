"""Digest CRUD routes."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import get_db, verify_api_key
from app import crud
from app.schemas import DigestCreate

router = APIRouter(prefix="/api", tags=["digests"])


@router.get("/digests")
async def list_digests(
    type: str | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    digests = crud.list_digests(db, type=type, limit=limit, offset=offset)
    return [
        {
            "id": d.id,
            "type": d.type,
            "content": d.content,
            "metadata": d.metadata_,
            "created_at": d.created_at,
        }
        for d in digests
    ]


@router.get("/digests/{digest_id}")
async def get_digest(digest_id: int, db: Session = Depends(get_db)):
    d = crud.get_digest(db, digest_id)
    if not d:
        raise HTTPException(status_code=404, detail="not found")
    return {
        "id": d.id,
        "type": d.type,
        "content": d.content,
        "metadata": d.metadata_,
        "created_at": d.created_at,
    }


@router.post("/digests/generate", status_code=202)
async def trigger_digest_generation(
    background_tasks: BackgroundTasks,
    type: str = Query(default="daily"),
    _api_key: str = Depends(verify_api_key),
):
    if type not in ("4h", "daily", "weekly", "monthly"):
        raise HTTPException(status_code=400, detail="type must be one of: 4h, daily, weekly, monthly")

    from app.services.digest_pipeline import run_pipeline

    background_tasks.add_task(_run_pipeline_sync, type)
    return {"message": f"{type} digest generation started", "status": "accepted"}


async def _run_pipeline_sync(digest_type: str):
    from app.services.digest_pipeline import run_pipeline
    await run_pipeline(digest_type)


@router.post("/digests", status_code=201)
async def create_digest(
    data: DigestCreate,
    _api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    d = crud.create_digest(
        db,
        type=data.type,
        content=data.content,
        metadata=data.metadata,
        created_at=data.created_at,
    )
    return {"id": d.id}
