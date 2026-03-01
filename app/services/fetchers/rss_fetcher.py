"""RSS / Atom feed fetcher using feedparser."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.services.fetchers.base import BaseFetcher, RawItemData

logger = logging.getLogger(__name__)

_TIMEOUT = 30


class RSSFetcher(BaseFetcher):
    async def fetch(self, source) -> list[RawItemData]:
        config = json.loads(source.config) if isinstance(source.config, str) else source.config
        feed_url = config.get("url", "")
        if not feed_url:
            logger.warning("RSS source %s has no url in config", source.id)
            return []

        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(feed_url, headers={"User-Agent": "ClawFeed/1.0"})
            resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        items: list[RawItemData] = []
        for entry in feed.entries[:50]:
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    pass

            link = entry.get("link", "")
            items.append(
                RawItemData(
                    title=entry.get("title", ""),
                    url=link,
                    author=entry.get("author"),
                    content=entry.get("summary", entry.get("description", "")),
                    dedup_key=link or entry.get("id", entry.get("title", "")),
                    published_at=published_at,
                )
            )
        logger.info("RSS source %s (%s): fetched %d items", source.id, source.name, len(items))
        return items
