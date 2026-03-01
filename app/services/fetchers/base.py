"""Base fetcher interface and shared data types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawItemData:
    """Unified data shape returned by all fetchers."""

    title: str = ""
    url: str = ""
    author: str | None = None
    content: str = ""
    dedup_key: str = ""
    published_at: datetime | None = None
    metadata: str = "{}"


class BaseFetcher(ABC):
    """Every fetcher must implement ``fetch``."""

    @abstractmethod
    async def fetch(self, source) -> list[RawItemData]:
        """Pull items from the source and return normalised data."""
        ...
