"""RSS & JSON Feed generation — port of feed endpoints from server.mjs."""

from __future__ import annotations

from datetime import datetime
from html import escape as html_escape

from app.models import Digest


DIGEST_ICONS = {"4h": "\u2600\ufe0f", "daily": "\U0001f4f0", "weekly": "\U0001f4c5", "monthly": "\U0001f4ca"}
DIGEST_LABELS = {"4h": "AI \u7b80\u62a5", "daily": "AI \u65e5\u62a5", "weekly": "AI \u5468\u62a5", "monthly": "AI \u6708\u62a5"}


def _digest_title(d: Digest, created_at_str: str) -> str:
    """Build a human-readable title like the Node.js _digestTitle()."""
    try:
        if "+" in created_at_str:
            dt = datetime.fromisoformat(created_at_str)
        else:
            dt = datetime.fromisoformat(created_at_str.replace(" ", "T") + "+08:00")
        time_str = dt.strftime("%Y/%m/%d %H:%M")
    except Exception:
        time_str = str(created_at_str)
    icon = DIGEST_ICONS.get(d.type, "\U0001f4dd")
    label = DIGEST_LABELS.get(d.type, "ClawFeed")
    return f"{icon} {label} | {time_str} SGT"


def _to_iso(created_at_str: str) -> str:
    if "+" in created_at_str:
        return created_at_str
    return created_at_str.replace(" ", "T") + "+08:00"


def build_json_feed(
    user_name: str,
    user_slug: str,
    digests: list,
    base_url: str,
) -> dict:
    return {
        "version": "https://jsonfeed.org/version/1.1",
        "title": f"{user_name}'s ClawFeed",
        "home_page_url": base_url,
        "feed_url": f"{base_url}/feed/{user_slug}.json",
        "items": [
            {
                "id": str(d.id),
                "title": _digest_title(d, str(d.created_at)),
                "content_text": d.content,
                "date_published": _to_iso(str(d.created_at)),
                "url": f"{base_url}/#digest-{d.id}",
            }
            for d in digests
        ],
    }


def build_rss_feed(
    user_name: str,
    digests: list,
    base_url: str,
) -> str:
    items = ""
    for d in digests:
        ca = str(d.created_at)
        title = _digest_title(d, ca)
        try:
            dt = datetime.fromisoformat(_to_iso(ca))
            pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        except Exception:
            pub_date = ca
        content_preview = html_escape((d.content or "")[:2000])
        items += (
            f"<item>"
            f"<title>{html_escape(title)}</title>"
            f"<link>{base_url}/#digest-{d.id}</link>"
            f'<guid isPermaLink="false">{d.id}</guid>'
            f"<pubDate>{pub_date}</pubDate>"
            f"<description>{content_preview}</description>"
            f"</item>\n"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        f"<title>{html_escape(user_name)}'s ClawFeed</title>"
        f"<link>{base_url}</link>"
        "<description>ClawFeed Feed</description>\n"
        f"{items}</channel></rss>"
    )
