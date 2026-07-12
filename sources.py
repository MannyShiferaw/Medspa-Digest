"""
Fetches and parses RSS/Atom feeds. feedparser handles both formats and
most of the quirks (encoding, malformed XML, etc.) for us, so this file
just wraps it and normalizes the fields we care about.
"""

import re
from datetime import datetime, timezone

import feedparser
import requests

from config import MAX_ITEMS_PER_SOURCE
from db import make_guid

# Some feeds reject requests that don't look like they're coming from a
# real browser (blocking generic/bot-labeled User-Agent strings), so we
# send a normal desktop-browser UA rather than identifying ourselves.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 20


MAX_SUMMARY_CHARS = 280


def clean_html(raw: str | None) -> str:
    """Strip HTML and trim to roughly 1-2 sentences so the digest stays skimmable."""
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", "", raw)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= MAX_SUMMARY_CHARS:
        return text

    truncated = text[:MAX_SUMMARY_CHARS]
    last_period = truncated.rfind(". ")
    if last_period > 80:
        return truncated[:last_period + 1]
    last_space = truncated.rfind(" ")
    return truncated[:last_space].rstrip(",;: ") + "…"


def to_iso(entry) -> str:
    """feedparser exposes a parsed time struct when it can figure out the date."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
    return ""


def fetch_source(source: dict) -> list[dict]:
    """
    Fetch one feed and return a list of normalized item dicts.
    Never raises - a broken/unreachable feed just yields an empty list
    (with a note printed to the console) so one bad source doesn't stop the run.
    """
    try:
        response = requests.get(source["url"], headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        parsed = feedparser.parse(response.content)
    except Exception as exc:
        print(f"  [skip] {source['name']}: could not fetch ({exc})")
        return []

    if parsed.bozo and not parsed.entries:
        print(f"  [skip] {source['name']}: feed did not parse ({parsed.bozo_exception})")
        return []

    items = []
    for entry in parsed.entries[:MAX_ITEMS_PER_SOURCE]:
        title = entry.get("title", "").strip()
        if not title:
            continue
        link = entry.get("link", "")
        summary = clean_html(entry.get("summary", "") or entry.get("description", ""))
        guid = make_guid(entry.get("id") or entry.get("guid"), link, title, source["name"])

        items.append({
            "guid": guid,
            "source": source["name"],
            "title": title,
            "link": link,
            "summary": summary,
            "category": source["category"],
            "base_score": source["base_score"],
            "published_at": to_iso(entry),
        })

    print(f"  [ok]   {source['name']}: {len(items)} items")
    return items
