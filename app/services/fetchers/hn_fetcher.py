"""HackerNews fetcher using the Firebase API."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import httpx

from app.services.fetchers.base import BaseFetcher, RawItemData

logger = logging.getLogger(__name__)

_HN_BASE = "https://hacker-news.firebaseio.com/v0"
_TIMEOUT = 30
_MAX_STORIES = 30


class HNFetcher(BaseFetcher):
    async def fetch(self, source) -> list[RawItemData]:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{_HN_BASE}/topstories.json")
            resp.raise_for_status()
            story_ids: list[int] = resp.json()[:_MAX_STORIES]

            items: list[RawItemData] = []
            tasks = [self._fetch_item(client, sid) for sid in story_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, RawItemData):
                    items.append(r)
                elif isinstance(r, Exception):
                    logger.debug("HN item fetch error: %s", r)

        logger.info("HN source %s: fetched %d items", source.id, len(items))
        return items

    @staticmethod
    async def _fetch_item(client: httpx.AsyncClient, item_id: int) -> RawItemData:
        resp = await client.get(f"{_HN_BASE}/item/{item_id}.json")
        resp.raise_for_status()
        data = resp.json()
        if not data:
            raise ValueError(f"Empty HN item {item_id}")

        url = data.get("url", f"https://news.ycombinator.com/item?id={item_id}")
        published_at = None
        if data.get("time"):
            published_at = datetime.fromtimestamp(data["time"], tz=timezone.utc)

        return RawItemData(
            title=data.get("title", ""),
            url=url,
            author=data.get("by"),
            content=data.get("text", ""),
            dedup_key=str(item_id),
            published_at=published_at,
            metadata=f'{{"score": {data.get("score", 0)}, "comments": {data.get("descendants", 0)}}}',
        )
