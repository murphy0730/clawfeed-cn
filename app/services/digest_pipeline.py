"""Digest generation pipeline: fetch → dedup → LLM → store."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import SessionLocal
from app.models import RawItem, Source
from app.services.fetchers import SUPPORTED_TYPES, get_fetcher
from app.services.llm import generate_digest

logger = logging.getLogger(__name__)

# Time windows for each digest type (how far back to look for unused items)
TIME_WINDOWS: dict[str, int] = {
    "4h": 6,        # 6 hours
    "daily": 26,    # 26 hours
    "weekly": 170,  # ~7 days
    "monthly": 744, # ~31 days
}


async def run_pipeline(digest_type: str) -> int | None:
    """Execute the full pipeline and return the new Digest ID, or None on failure."""
    db: Session = SessionLocal()
    try:
        return await _run(db, digest_type)
    except Exception:
        logger.exception("Pipeline failed for digest_type=%s", digest_type)
        return None
    finally:
        db.close()


async def _run(db: Session, digest_type: str) -> int | None:
    # 1. Get active sources
    sources = crud.list_active_sources_by_types(db, SUPPORTED_TYPES)
    if not sources:
        logger.warning("No active sources found for types %s", SUPPORTED_TYPES)
        return None

    logger.info("Pipeline [%s]: processing %d sources", digest_type, len(sources))

    # 2. Fetch from each source
    total_new = 0
    for source in sources:
        fetcher = get_fetcher(source.type)
        if not fetcher:
            continue
        try:
            raw_items = await fetcher.fetch(source)
        except Exception:
            logger.exception("Fetch failed for source %s (%s)", source.id, source.name)
            continue

        # 3. Store with dedup (IntegrityError = already exists)
        new_count = 0
        for item_data in raw_items:
            raw = RawItem(
                source_id=source.id,
                title=item_data.title,
                url=item_data.url,
                author=item_data.author,
                content=item_data.content,
                published_at=item_data.published_at,
                dedup_key=item_data.dedup_key,
                metadata_=item_data.metadata,
            )
            try:
                db.add(raw)
                db.flush()
                new_count += 1
            except IntegrityError:
                db.rollback()
        db.commit()
        total_new += new_count

        # 4. Update source fetch stats
        source.last_fetched_at = datetime.now(timezone.utc)
        source.fetch_count = (source.fetch_count or 0) + 1
        db.commit()

        logger.info(
            "Source %s (%s): %d fetched, %d new",
            source.id, source.name, len(raw_items), new_count,
        )

    # 5. Get unused items within time window
    hours = TIME_WINDOWS.get(digest_type, 26)
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    unused_items = crud.get_unused_raw_items(db, since=since)

    if not unused_items:
        logger.info("Pipeline [%s]: no unused items to digest", digest_type)
        return None

    logger.info("Pipeline [%s]: %d unused items for LLM", digest_type, len(unused_items))

    # 6. Generate digest via LLM
    content = await generate_digest(unused_items, digest_type)
    if not content:
        logger.warning("Pipeline [%s]: LLM returned empty content", digest_type)
        return None

    # 7. Store digest (user_id=None → global)
    digest = crud.create_digest(db, type=digest_type, content=content)

    # 8. Mark items as used
    item_ids = [item.id for item in unused_items]
    crud.mark_items_used(db, item_ids)

    logger.info(
        "Pipeline [%s]: created digest #%d (%d items, %d new fetched)",
        digest_type, digest.id, len(unused_items), total_new,
    )
    return digest.id
