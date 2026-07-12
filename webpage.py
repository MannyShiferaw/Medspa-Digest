"""
Renders a static HTML page (docs/index.html) showing a rolling 7-day
window of relevant items, grouped by category. This is what gets
published to GitHub Pages - unlike digest.py's markdown file (which
only shows *that run's* new items and is often empty), this always
shows a living page of recent coverage.
"""

import html
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from config import CATEGORIES
from db import fetch_recent

DOCS_DIR = Path(__file__).parent / "docs"
WINDOW_DAYS = 7

GEO_LABELS = {
    "local": "Halifax / Atlantic Canada",
    "canada": "Canada",
    "north_america": "North America",
    "global": "Global",
}

STYLE = """<style>
:root {
  --bg: #efeee7;
  --surface: #fbfaf6;
  --ink: #21231f;
  --ink-soft: #5b5f55;
  --ink-faint: #8b9086;
  --accent: #3e6357;
  --accent-strong: #2c483f;
  --accent-soft: #e1e8e1;
  --accent-soft-ink: #2c483f;
  --line: #dbdacf;
  --line-strong: #c7c6b9;
  --tick-empty: #d6d5c8;
  --font-display: ui-serif, "New York", "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  --font-body: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #141714; --surface: #1b1f1b; --ink: #ece9e2; --ink-soft: #a9ac9f;
    --ink-faint: #767a6e; --accent: #7fac99; --accent-strong: #a3c9b8;
    --accent-soft: #23322c; --accent-soft-ink: #a3c9b8; --line: #2c2f29;
    --line-strong: #3a3d35; --tick-empty: #33352e;
  }
}
:root[data-theme="dark"] {
  --bg: #141714; --surface: #1b1f1b; --ink: #ece9e2; --ink-soft: #a9ac9f;
  --ink-faint: #767a6e; --accent: #7fac99; --accent-strong: #a3c9b8;
  --accent-soft: #23322c; --accent-soft-ink: #a3c9b8; --line: #2c2f29;
  --line-strong: #3a3d35; --tick-empty: #33352e;
}
:root[data-theme="light"] {
  --bg: #efeee7; --surface: #fbfaf6; --ink: #21231f; --ink-soft: #5b5f55;
  --ink-faint: #8b9086; --accent: #3e6357; --accent-strong: #2c483f;
  --accent-soft: #e1e8e1; --accent-soft-ink: #2c483f; --line: #dbdacf;
  --line-strong: #c7c6b9; --tick-empty: #d6d5c8;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--font-body); margin: 0; -webkit-font-smoothing: antialiased; }
.tabular { font-variant-numeric: tabular-nums; }
.digest { max-width: 700px; margin: 0 auto; padding: 4rem 1.5rem 6rem; }
.masthead { margin-bottom: 2.5rem; }
.eyebrow { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; color: var(--accent); margin: 0 0 0.9rem; }
.masthead-title { font-family: var(--font-display); font-size: clamp(2.1rem, 5vw, 2.75rem); font-weight: 600; line-height: 1.05; letter-spacing: -0.01em; margin: 0 0 0.6rem; text-wrap: balance; }
.masthead-meta { font-size: 0.95rem; color: var(--ink-soft); margin: 0 0 1.1rem; }
.masthead-note { font-size: 0.85rem; line-height: 1.55; color: var(--ink-faint); margin: 0; padding-top: 1.1rem; border-top: 1px solid var(--line); max-width: 56ch; }
.category-nav { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 3.25rem; }
.nav-chip { font-size: 0.78rem; font-weight: 500; color: var(--ink-soft); text-decoration: none; background: var(--surface); border: 1px solid var(--line); border-radius: 100px; padding: 0.4rem 0.85rem; transition: border-color 0.15s ease, color 0.15s ease; }
.nav-chip:hover { border-color: var(--accent); color: var(--accent-strong); }
.nav-count { color: var(--ink-faint); font-variant-numeric: tabular-nums; }
.category { margin-bottom: 3.25rem; scroll-margin-top: 1.5rem; }
.category-head { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; border-bottom: 1px solid var(--line-strong); padding-bottom: 0.6rem; margin-bottom: 1.6rem; }
.category-label { font-family: var(--font-display); font-size: 1.3rem; font-weight: 600; margin: 0; }
.category-count { font-size: 0.78rem; color: var(--ink-faint); font-variant-numeric: tabular-nums; white-space: nowrap; }
.item-list { display: flex; flex-direction: column; }
.item { padding: 1.15rem 0; border-bottom: 1px solid var(--line); }
.item:first-child { padding-top: 0; }
.item:last-child { border-bottom: none; }
.item-title { font-family: var(--font-display); font-size: 1.08rem; font-weight: 500; line-height: 1.35; margin: 0 0 0.5rem; text-wrap: balance; }
.item-title a { color: var(--ink); text-decoration: none; background-image: linear-gradient(var(--ink-faint), var(--ink-faint)); background-position: 0 100%; background-repeat: no-repeat; background-size: 0% 1px; transition: background-size 0.2s ease, color 0.2s ease; }
.item-title a:hover { color: var(--accent-strong); background-size: 100% 1px; }
.item-title a:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }
.item-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; font-size: 0.76rem; color: var(--ink-faint); margin-bottom: 0.45rem; }
.meta-source { text-transform: uppercase; letter-spacing: 0.03em; font-weight: 600; color: var(--ink-soft); }
.meta-dot { color: var(--line-strong); }
.geo-pill { font-size: 0.7rem; font-weight: 600; padding: 0.1rem 0.55rem; border-radius: 100px; border: 1px solid var(--line-strong); color: var(--ink-soft); white-space: nowrap; }
.geo-pill.geo-local { background: var(--accent-soft); border-color: transparent; color: var(--accent-soft-ink); }
.star-meter { display: inline-flex; gap: 0.2rem; margin-left: auto; }
.tick { width: 7px; height: 7px; border-radius: 1.5px; background: var(--tick-empty); }
.tick.is-filled { background: var(--accent); }
.item-summary { font-size: 0.88rem; line-height: 1.55; color: var(--ink-soft); margin: 0; max-width: 62ch; }
.empty-note { font-size: 0.88rem; color: var(--ink-faint); font-style: italic; }
.colophon { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--line); font-size: 0.75rem; color: var(--ink-faint); }
.colophon code { font-family: ui-monospace, "SF Mono", Menlo, monospace; background: var(--surface); border: 1px solid var(--line); padding: 0.05em 0.4em; border-radius: 4px; }
@media (max-width: 480px) { .digest { padding: 2.75rem 1.1rem 4rem; } .item-meta { row-gap: 0.4rem; } .star-meter { margin-left: 0; } }
</style>
"""


def render_item(row) -> str:
    title = html.escape(row["title"])
    source = html.escape(row["source"])
    link = html.escape(row["link"] or "#")
    geo_key = row["geo_scope"] or "global"
    geo_label = html.escape(GEO_LABELS.get(geo_key, geo_key))
    score = row["relevance_score"] or 0
    summary = row["summary"] or ""
    show_summary = summary and summary.lower()[:40] not in row["title"].lower()

    stars = "".join(f'<span class="tick {"is-filled" if i < score else ""}"></span>' for i in range(5))
    summary_html = f'<p class="item-summary">{html.escape(summary)}</p>' if show_summary else ""

    return f"""
    <article class="item">
      <h3 class="item-title"><a href="{link}" target="_blank" rel="noopener">{title}</a></h3>
      <div class="item-meta">
        <span class="meta-source">{source}</span>
        <span class="meta-dot">&middot;</span>
        <span class="geo-pill geo-{geo_key}">{geo_label}</span>
        <span class="star-meter" title="Relevance {score}/5">{stars}</span>
      </div>
      {summary_html}
    </article>
    """


def build_site(conn, min_score: int) -> str:
    since_iso = (datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).isoformat()

    nav_items = []
    sections = []
    total = 0

    for slug, label in CATEGORIES.items():
        rows = fetch_recent(conn, slug, min_score, since_iso)
        if not rows:
            continue
        total += len(rows)
        nav_items.append(
            f'<a class="nav-chip" href="#{slug}">{html.escape(label)} '
            f'<span class="nav-count">{len(rows)}</span></a>'
        )
        items_html = "".join(render_item(row) for row in rows)
        sections.append(f"""
        <section class="category" id="{slug}">
          <div class="category-head">
            <h2 class="category-label">{html.escape(label)}</h2>
            <span class="category-count">{len(rows)} item{"s" if len(rows) != 1 else ""}</span>
          </div>
          <div class="item-list">{items_html}</div>
        </section>
        """)

    body = "".join(sections) if sections else '<p class="empty-note">No relevant items found in the last 7 days.</p>'
    nav = f'<nav class="category-nav" aria-label="Jump to category">{"".join(nav_items)}</nav>' if nav_items else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Aesthetic Brief</title>
{STYLE}
</head>
<body>
<div class="digest">
  <header class="masthead">
    <p class="eyebrow">Independent Intelligence for Aesthetic Medicine</p>
    <h1 class="masthead-title">The Aesthetic Brief</h1>
    <p class="masthead-meta">Updated {date.today().isoformat()} &middot; <span class="tabular">{total}</span> item(s) from the last {WINDOW_DAYS} days</p>
    <p class="masthead-note">Automatically compiled daily from regulator feeds, trade publications, and targeted news searches. Relevance is scored 1&ndash;5 by keyword rules (not AI); anything scoring below 3 is discarded.</p>
  </header>
  {nav}
  {body}
  <footer class="colophon">
    <p>Generated by <code>scanner.py</code> &middot; rolling {WINDOW_DAYS}-day window &middot; refreshes daily</p>
  </footer>
</div>
</body>
</html>
"""


def write_site(conn, min_score: int = 3) -> Path:
    DOCS_DIR.mkdir(exist_ok=True)
    out_path = DOCS_DIR / "index.html"
    out_path.write_text(build_site(conn, min_score), encoding="utf-8")
    return out_path
