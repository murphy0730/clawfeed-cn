"""Source Pack routes."""

from __future__ import annotations

import json
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user, require_user
from app.models import User
from app import crud
from app.schemas import PackCreate

router = APIRouter(prefix="/api/packs", tags=["packs"])


@router.get("")
async def list_packs(
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    packs = crud.list_packs(db, public_only=True, user_id=user.id if user else None)
    result = []
    for p in packs:
        sources_json = p.pop("sources_json", "[]")
        p["sources"] = json.loads(sources_json)
        result.append(p)
    return result


@router.post("/{slug}/install")
async def install_pack(
    slug: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    pack = crud.get_pack_by_slug(db, slug)
    if not pack:
        raise HTTPException(status_code=404, detail="not found")
    sources = json.loads(pack.get("sources_json") or "[]")
    added = 0
    for s in sources:
        config_str = (
            s["config"] if isinstance(s["config"], str) else json.dumps(s["config"])
        )
        existing = crud.get_source_by_type_config(db, s["type"], config_str)
        if existing:
            if existing.is_deleted:
                continue
            if not crud.is_subscribed(db, user.id, existing.id):
                crud.subscribe(db, user.id, existing.id)
                added += 1
        else:
            crud.create_source(
                db,
                name=s["name"],
                type=s["type"],
                config=config_str,
                is_public=False,
                created_by=user.id,
            )
            added += 1
    crud.increment_pack_install(db, pack["id"])
    return {"ok": True, "added": added, "skipped": len(sources) - added}


@router.get("/{slug}")
async def get_pack(
    slug: str,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pack = crud.get_pack_by_slug(db, slug)
    if not pack:
        raise HTTPException(status_code=404, detail="not found")
    if not pack.get("is_public") and (
        not user or pack.get("created_by") != user.id
    ):
        raise HTTPException(status_code=404, detail="not found")
    sources_json = pack.pop("sources_json", "[]")
    pack["sources"] = json.loads(sources_json)
    return pack


@router.post("", status_code=201)
async def create_pack(
    data: PackCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    name = (data.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    slug = data.slug or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:50]
    # Ensure unique slug
    candidate = slug
    i = 1
    while crud.get_pack_by_slug(db, candidate):
        candidate = f"{slug}-{i}"
        i += 1
    sources_json = data.sourcesJson or data.sources_json or "[]"
    p = crud.create_pack(
        db,
        name=name,
        description=data.description,
        slug=candidate,
        sources_json=sources_json,
        created_by=user.id,
    )
    return {"id": p.id, "slug": candidate}


@router.delete("/{pack_id}")
async def delete_pack(
    pack_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    pack = crud.get_pack(db, pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail="not found")
    if pack.created_by != user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    crud.delete_pack(db, pack.id)
    return {"ok": True}
