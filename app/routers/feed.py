"""RSS / JSON Feed output routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.config import get_settings
from app.deps import get_db
from app import crud
from app.services.feed_generator import build_json_feed, build_rss_feed

router = APIRouter(tags=["feed"])
settings = get_settings()


@router.get("/feed/{slug}.json")
async def json_feed(
    slug: str,
    type: str = "4h",
    limit: int = Query(default=10, le=50),
    since: str | None = None,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_slug(db, slug)
    if not user:
        return JSONResponse({"error": "user not found"}, status_code=404)
    digests = crud.list_digests_by_user(db, user.id, type=type, limit=limit, since=since)
    feed = build_json_feed(user.name or slug, user.slug or slug, digests, settings.base_url)
    return JSONResponse(feed, media_type="application/feed+json; charset=utf-8")


@router.get("/feed/{slug}.rss")
async def rss_feed(
    slug: str,
    type: str = "4h",
    limit: int = Query(default=10, le=50),
    since: str | None = None,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_slug(db, slug)
    if not user:
        return JSONResponse({"error": "user not found"}, status_code=404)
    digests = crud.list_digests_by_user(db, user.id, type=type, limit=limit, since=since)
    rss = build_rss_feed(user.name or slug, digests, settings.base_url)
    return Response(rss, media_type="application/rss+xml; charset=utf-8")


@router.get("/feed/{slug}")
async def feed_api(
    slug: str,
    type: str = "4h",
    limit: int = Query(default=10, le=50),
    since: str | None = None,
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_slug(db, slug)
    if not user:
        return JSONResponse({"error": "user not found"}, status_code=404)
    digests = crud.list_digests_by_user(db, user.id, type=type, limit=limit, since=since)
    total = crud.count_digests_by_user(db, user.id, type=type)
    return {
        "user": {"name": user.name, "slug": user.slug},
        "digests": [
            {"id": d.id, "type": d.type, "content": d.content, "created_at": d.created_at}
            for d in digests
        ],
        "total": total,
    }
