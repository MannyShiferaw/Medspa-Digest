"""
Renders the SQLite rows for today's run into a single markdown file,
grouped by category (in the order defined in config.py) and sorted
most-relevant-first within each category.
"""

from datetime import date
from pathlib import Path

from config import CATEGORIES, MIN_RELEVANCE_TO_INCLUDE
from db import fetch_for_digest

OUTPUT_DIR = Path(__file__).parent / "output"

GEO_LABELS = {
    "local": "Halifax / Atlantic Canada",
    "canada": "Canada",
    "north_america": "North America",
    "global": "Global",
}


def build_digest(conn, fetched_at: str, category: str | None = None) -> str:
    rows = fetch_for_digest(conn, category, MIN_RELEVANCE_TO_INCLUDE, fetched_at)

    by_category: dict[str, list] = {}
    for row in rows:
        by_category.setdefault(row["category"], []).append(row)

    lines = [f"# Youth Bar Industry Digest — {date.today().isoformat()}", ""]

    if not rows:
        lines.append("No new relevant items found in this run.")
        return "\n".join(lines)

    lines.append(f"{len(rows)} new item(s) worth your 5 minutes, grouped by category, most relevant first.")
    lines.append("")

    for cat_key, cat_label in CATEGORIES.items():
        cat_rows = by_category.get(cat_key)
        if not cat_rows:
            continue
        lines.append(f"## {cat_label}")
        lines.append("")
        for row in cat_rows:
            geo = GEO_LABELS.get(row["geo_scope"], row["geo_scope"])
            stars = "★" * row["relevance_score"] + "☆" * (5 - row["relevance_score"])
            lines.append(f"### {row['title']}")
            lines.append(f"*{row['source']} · {geo} · {stars}*")
            lines.append("")
            # Google News' RSS "summary" is often just the title repeated -
            # skip it rather than waste space restating the headline.
            summary = row["summary"] or ""
            if summary and summary.lower()[:40] not in row["title"].lower():
                lines.append(summary)
                lines.append("")
            if row["link"]:
                lines.append(f"[Read more]({row['link']})")
            lines.append("")
        lines.append("")

    return "\n".join(lines)


def write_digest(conn, fetched_at: str, category: str | None = None) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    content = build_digest(conn, fetched_at, category)
    out_path = OUTPUT_DIR / f"digest-{date.today().isoformat()}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
