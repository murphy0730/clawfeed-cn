"""URL auto-detection for source types — port of resolveSourceUrl() from server.mjs."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx


def _extract_rss_preview(xml: str) -> list[dict]:
    items: list[dict] = []
    pattern = re.compile(
        r"<item[^>]*>([\s\S]*?)</item>|<entry[^>]*>([\s\S]*?)</entry>", re.IGNORECASE
    )
    for m in pattern.finditer(xml):
        if len(items) >= 5:
            break
        block = m.group(1) or m.group(2) or ""
        t = re.search(
            r"<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block, re.IGNORECASE
        )
        l = re.search(
            r'<link[^>]*href=["\']([^"\']+)["\']', block, re.IGNORECASE
        ) or re.search(r"<link[^>]*>(.*?)</link>", block, re.IGNORECASE)
        items.append(
            {
                "title": t.group(1).strip() if t else "(untitled)",
                "url": l.group(1).strip() if l else "",
            }
        )
    return items


async def resolve_source_url(url: str) -> dict:
    u = url.lower()

    # Twitter / X
    if "x.com" in u or "twitter.com" in u:
        list_match = re.search(r"/i/lists/(\d+)", url)
        if list_match:
            return {
                "name": f"X List {list_match.group(1)}",
                "type": "twitter_list",
                "config": {"list_url": url},
                "icon": "\U0001f426",
            }
        handle_match = re.search(
            r"(?:x\.com|twitter\.com)/(@?[A-Za-z0-9_]+)", url
        )
        reserved = {
            "i", "search", "explore", "home", "notifications", "messages", "settings"
        }
        if handle_match and handle_match.group(1).lower() not in reserved:
            handle = handle_match.group(1).lstrip("@")
            return {
                "name": f"@{handle}",
                "type": "twitter_feed",
                "config": {"handle": f"@{handle}"},
                "icon": "\U0001f426",
            }
        return {
            "name": "X Feed",
            "type": "twitter_feed",
            "config": {"handle": url},
            "icon": "\U0001f426",
        }

    # Reddit
    reddit_match = re.search(r"reddit\.com/r/([A-Za-z0-9_]+)", url)
    if reddit_match:
        sub = reddit_match.group(1)
        return {
            "name": f"r/{sub}",
            "type": "reddit",
            "config": {"subreddit": sub, "sort": "hot", "limit": 20},
            "icon": "\U0001f47d",
        }

    # GitHub Trending
    if "github.com/trending" in u:
        lang_match = re.search(r"/trending/([a-z0-9+#.-]+)", url, re.IGNORECASE)
        lang = lang_match.group(1) if lang_match else ""
        return {
            "name": f"GitHub Trending{' - ' + lang if lang else ''}",
            "type": "github_trending",
            "config": {"language": lang or "all", "since": "daily"},
            "icon": "\u2b50",
        }

    # Hacker News
    if "news.ycombinator.com" in u:
        return {
            "name": "Hacker News",
            "type": "hackernews",
            "config": {"filter": "top", "min_score": 100},
            "icon": "\U0001f536",
        }

    # Fetch URL to detect content type
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=5.0, max_redirects=3
    ) as client:
        resp = await client.get(
            url,
            headers={
                "User-Agent": "AI-Digest/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml,application/json,*/*",
            },
        )
        ct = (resp.headers.get("content-type") or "").lower()
        body = resp.text[:200000]

    # RSS / Atom
    if any(
        x in ct for x in ("xml", "rss", "atom")
    ) or body.lstrip().startswith("<?xml") or "<rss" in body or "<feed" in body:
        if "<rss" in body or "<feed" in body or "<channel" in body:
            title_match = re.search(
                r"<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>",
                body,
                re.IGNORECASE,
            )
            name = (
                title_match.group(1).strip()
                if title_match
                else urlparse(url).hostname or url
            )
            preview = _extract_rss_preview(body)
            return {
                "name": name,
                "type": "rss",
                "config": {"url": url},
                "icon": "\U0001f4e1",
                "preview": preview,
            }

    # JSON Feed
    if "json" in ct or body.lstrip().startswith("{"):
        try:
            import json

            j = json.loads(body)
            if j.get("version", "").find("jsonfeed") >= 0:
                preview = [
                    {"title": i.get("title", "(untitled)"), "url": i.get("url", "")}
                    for i in (j.get("items") or [])[:5]
                ]
                return {
                    "name": j.get("title") or urlparse(url).hostname or url,
                    "type": "digest_feed",
                    "config": {"url": url},
                    "icon": "\U0001f4f0",
                    "preview": preview,
                }
        except Exception:
            pass

    # HTML — treat as website
    if "html" in ct or "<html" in body or "<!DOCTYPE" in body:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
        name = (
            " ".join(title_match.group(1).strip().split())[:100]
            if title_match
            else urlparse(url).hostname or url
        )
        return {
            "name": name,
            "type": "website",
            "config": {"url": url},
            "icon": "\U0001f310",
        }

    raise ValueError("Cannot detect source type")
