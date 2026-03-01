"""Reddit fetcher — uses public JSON endpoint (no auth required)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import httpx

from app.services.fetchers.base import BaseFetcher, RawItemData

logger = logging.getLogger(__name__)

_TIMEOUT = 30
_MAX_POSTS = 30


class RedditFetcher(BaseFetcher):
    async def fetch(self, source) -> list[RawItemData]:
        config = json.loads(source.config) if isinstance(source.config, str) else source.config
        subreddit = config.get("subreddit", "technology")
        sort = config.get("sort", "hot")

        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={_MAX_POSTS}"
        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "ClawFeed/1.0 (news aggregator)"},
            )
            resp.raise_for_status()
            data = resp.json()

        items: list[RawItemData] = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            if post.get("stickied"):
                continue

            post_url = post.get("url", "")
            permalink = f"https://www.reddit.com{post.get('permalink', '')}"
            published_at = None
            if post.get("created_utc"):
                published_at = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc)

            items.append(
                RawItemData(
                    title=post.get("title", ""),
                    url=post_url or permalink,
                    author=post.get("author"),
                    content=post.get("selftext", ""),
                    dedup_key=post.get("id", post_url),
                    published_at=published_at,
                    metadata=json.dumps({
                        "score": post.get("score", 0),
                        "comments": post.get("num_comments", 0),
                        "subreddit": subreddit,
                        "permalink": permalink,
                    }),
                )
            )

        logger.info("Reddit source %s (r/%s): fetched %d items", source.id, subreddit, len(items))
        return items
