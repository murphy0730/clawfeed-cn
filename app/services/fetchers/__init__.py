"""Fetcher registry — maps source type to fetcher class."""

from __future__ import annotations

from app.services.fetchers.base import BaseFetcher, RawItemData
from app.services.fetchers.rss_fetcher import RSSFetcher
from app.services.fetchers.hn_fetcher import HNFetcher
from app.services.fetchers.reddit_fetcher import RedditFetcher

FETCHER_REGISTRY: dict[str, type[BaseFetcher]] = {
    "rss": RSSFetcher,
    "hackernews": HNFetcher,
    "reddit": RedditFetcher,
}

SUPPORTED_TYPES = list(FETCHER_REGISTRY.keys())


def get_fetcher(source_type: str) -> BaseFetcher | None:
    cls = FETCHER_REGISTRY.get(source_type)
    return cls() if cls else None
