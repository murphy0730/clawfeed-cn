"""LLM service — generates digest content via OpenAI-compatible API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from openai import AsyncOpenAI

from app.config import get_settings, ROOT

logger = logging.getLogger(__name__)

_PROMPT_PATH = ROOT / "templates" / "digest-prompt.md"


def _load_system_prompt() -> str:
    if _PROMPT_PATH.exists():
        return _PROMPT_PATH.read_text(encoding="utf-8")
    return "You are an AI news curator. Generate a structured digest from the provided feed content."


def _format_items(items, digest_type: str) -> str:
    """Turn a list of raw items into a text block for the LLM."""
    now = datetime.now(timezone.utc)
    lines = [
        f"Digest type: {digest_type}",
        f"Generated at: {now.isoformat()}",
        f"Total items: {len(items)}",
        "",
        "--- Feed Items ---",
    ]
    for i, item in enumerate(items, 1):
        source_name = item.source.name if hasattr(item, "source") and item.source else "Unknown"
        lines.append(f"\n[{i}] {item.title}")
        if item.url:
            lines.append(f"    URL: {item.url}")
        if item.author:
            lines.append(f"    Author: {item.author}")
        lines.append(f"    Source: {source_name}")
        if item.published_at:
            lines.append(f"    Published: {item.published_at.isoformat()}")
        if item.content:
            # Truncate long content
            content = item.content[:500]
            if len(item.content) > 500:
                content += "..."
            lines.append(f"    Content: {content}")
    return "\n".join(lines)


async def generate_digest(items, digest_type: str) -> str:
    """Send items to LLM and return the generated digest text."""
    settings = get_settings()

    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY not configured")

    client = AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )

    system_prompt = _load_system_prompt()
    user_content = _format_items(items, digest_type)

    logger.info("Calling LLM (%s) with %d items for %s digest", settings.llm_model, len(items), digest_type)

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    content = response.choices[0].message.content or ""
    logger.info("LLM returned %d chars for %s digest", len(content), digest_type)
    return content
