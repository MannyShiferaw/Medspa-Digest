"""
Generates output/email-draft-<date>.html - a short, top-2-per-category
version of the digest meant to be opened in a browser, selected, and
pasted directly into Beehiiv's post editor for a manual send. Beehiiv
doesn't offer automated sending on the free plan, so this exists to make
that manual step fast instead of requiring Manny to dig through the full
site or markdown file each time.

Kept as plain, semantic HTML (headings, bold, links) rather than the
site's full styling - the goal is clean copy/paste fidelity into a rich
text editor, not a page anyone browses directly.
"""

import html
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from config import CATEGORIES
from db import fetch_recent

DOCS_DIR = Path(__file__).parent / "docs"
WINDOW_DAYS = 7
PER_CATEGORY_CAP = 2


def render_item(row) -> str:
    title = html.escape(row["title"])
    link = html.escape(row["link"] or "#")
    summary = row["summary"] or ""
    show_summary = summary and summary.lower()[:40] not in row["title"].lower()
    summary_html = f"<p>{html.escape(summary)}</p>" if show_summary else ""
    return f'<p><strong><a href="{link}">{title}</a></strong></p>{summary_html}'


def build_draft(conn, min_score: int) -> str:
    since_iso = (datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).isoformat()

    sections = []
    for slug, label in CATEGORIES.items():
        rows = fetch_recent(conn, slug, min_score, since_iso)[:PER_CATEGORY_CAP]
        if not rows:
            continue
        items_html = "".join(render_item(row) for row in rows)
        sections.append(f"<h2>{html.escape(label)}</h2>{items_html}")

    body = "".join(sections) if sections else "<p>Nothing in the last 7 days met the relevance bar.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<title>Email draft - {date.today().isoformat()}</title>
</head>
<body style="font-family: -apple-system, sans-serif; max-width: 640px; margin: 2rem auto;">
<p><em>Top {PER_CATEGORY_CAP} per category, last {WINDOW_DAYS} days. Select all below this line and paste into Beehiiv - add your own take on anything worth flagging before sending.</em></p>
<hr>
<h1>The Aesthetic Brief &mdash; {date.today().isoformat()}</h1>
{body}
</body>
</html>
"""


def write_draft(conn, min_score: int = 3) -> Path:
    # Stable filename (no date) so the URL is a bookmark-once-and-reuse
    # link - https://theaestheticbrief.ca/email-draft.html - rather than
    # something you'd have to look up fresh each day. Published to docs/
    # since that's the folder GitHub Pages actually serves.
    DOCS_DIR.mkdir(exist_ok=True)
    out_path = DOCS_DIR / "email-draft.html"
    out_path.write_text(build_draft(conn, min_score), encoding="utf-8")
    return out_path
