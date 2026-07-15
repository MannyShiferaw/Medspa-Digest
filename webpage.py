"""
Renders a static HTML page (docs/index.html) showing a rolling 7-day
window of relevant items, grouped by category. This is what gets
published to GitHub Pages - unlike digest.py's markdown file (which
only shows *that run's* new items and is often empty), this always
shows a living page of recent coverage.
"""

import base64
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

# Simple monogram favicon (dark ink square, italic brass "A") - kept as an
# inline SVG data URI so there's no separate binary asset file to manage.
_FAVICON_RAW_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="14" fill="#201d17"/>'
    '<text x="32" y="46" font-family="Georgia, serif" font-style="italic" '
    'font-size="38" font-weight="600" fill="#c19a5b" text-anchor="middle">A</text>'
    "</svg>"
)
FAVICON_SVG = base64.b64encode(_FAVICON_RAW_SVG.encode()).decode()

# Beehiiv subscribe form embed (Audience → Grow → Subscribe Forms in the
# Beehiiv dashboard). Its internal look (button color, fonts) is controlled
# there, not by our CSS - browsers don't let us style another origin's
# embedded content.
BEEHIIV_EMBED = (
    '<script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" '
    'data-beehiiv-form="44940058-f306-4ebf-b43c-20ec5c062f93"></script>'
)

# Lets Beehiiv attribute new subscribers to this site (vs. other referral
# sources) rather than just counting raw signups with no source data.
# Site-wide, loaded early in <head> so it captures visit context before
# anyone reaches the signup form.
BEEHIIV_ATTRIBUTION = (
    '<script type="text/javascript" async '
    'src="https://subscribe-forms.beehiiv.com/attribution.js"></script>'
)

# Light mode is the brand's home base (warm off-grey + brass accent).
# Dark mode reuses the same family, shifted onto a warm near-black ground -
# same brass accent, so it reads as one brand rather than an auto-inverted
# afterthought.
#
# Layout: a sticky sidebar (brand + category nav) alongside a focused
# reading column, rather than one long centered page - keeps line length
# readable while giving the wide desktop viewport an actual job, and is
# where a future email-signup box would live.
STYLE = """<style>
:root {
  --bg: #f4f3f0;
  --panel: #ffffff;
  --ink: #201d17;
  --ink-soft: #67624f;
  --ink-faint: #948e79;
  --accent: #9c7233;
  --accent-strong: #7a5623;
  --accent-soft: #efe6d4;
  --line: #e2ddd0;
  --line-strong: #cfc8b6;
  --font-display: "Iowan Old Style", "Palatino Linotype", Georgia, ui-serif, serif;
  --font-body: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, "SF Mono", "Roboto Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #16140f; --panel: #1d1a13; --ink: #f3ede0; --ink-soft: #b7ac95;
    --ink-faint: #7c7361; --accent: #c19a5b; --accent-strong: #e0bc7f;
    --accent-soft: #2c2618; --line: #322c22; --line-strong: #453d2d;
  }
}
:root[data-theme="dark"] {
  --bg: #16140f; --panel: #1d1a13; --ink: #f3ede0; --ink-soft: #b7ac95;
  --ink-faint: #7c7361; --accent: #c19a5b; --accent-strong: #e0bc7f;
  --accent-soft: #2c2618; --line: #322c22; --line-strong: #453d2d;
}
:root[data-theme="light"] {
  --bg: #f4f3f0; --panel: #ffffff; --ink: #201d17; --ink-soft: #67624f;
  --ink-faint: #948e79; --accent: #9c7233; --accent-strong: #7a5623;
  --accent-soft: #efe6d4; --line: #e2ddd0; --line-strong: #cfc8b6;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--font-body); margin: 0; -webkit-font-smoothing: antialiased; }
.tabular { font-variant-numeric: tabular-nums; }

.site-header { text-align: center; padding: 3rem 1.5rem 1.75rem; border-bottom: 1px solid var(--line); }
.site-header .eyebrow { margin: 0 0 0.9rem; }
.site-header .brand-title { font-family: var(--font-display); font-style: italic; font-size: clamp(2rem, 4vw, 2.6rem); font-weight: 500; line-height: 1.08; margin: 0 0 1rem; text-wrap: balance; }
.site-tagline { font-size: 0.98rem; line-height: 1.6; color: var(--ink-soft); max-width: 46ch; margin: 0 auto; text-wrap: balance; }

/* Full-width banner, not the 260px sidebar - the Beehiiv widget renders its
   own title/subheader/button and needs real room, or it wraps into an
   unreadable vertical stack. */
.subscribe-banner { border-bottom: 1px solid var(--line); background: var(--panel); }
.subscribe-banner-inner { max-width: 640px; margin: 0 auto; padding: 0.5rem 1.5rem 0; text-align: center; }
.subscribe-embed { max-width: 100%; }

.page-shell { display: grid; grid-template-columns: 260px 1fr; align-items: start; max-width: 1120px; margin: 0 auto; }

.sidebar { position: sticky; top: 0; height: 100vh; overflow-y: auto; padding: 2.5rem 1.75rem 2rem; border-right: 1px solid var(--line); }
.eyebrow { font-size: 0.66rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); margin: 0 0 0.9rem; }
.sidebar-label { font-size: 0.92rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink-soft); margin: 0 0 0.9rem; }

.side-nav { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1.75rem; }
.side-nav a { font-size: 0.82rem; font-weight: 500; color: var(--ink-soft); text-decoration: none; padding: 0.45rem 0.7rem; border: 1px solid var(--line); border-radius: 8px; display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease; }
.side-nav a:hover { border-color: var(--accent); color: var(--accent-strong); background: var(--panel); }
.side-count { color: var(--ink-faint); font-family: var(--font-mono); font-size: 0.68rem; }

.side-note { font-size: 0.78rem; line-height: 1.6; color: var(--ink-faint); padding-top: 1.5rem; border-top: 1px solid var(--line); }
.side-note code { font-family: var(--font-mono); background: var(--panel); border: 1px solid var(--line); padding: 0.05em 0.35em; border-radius: 4px; }
.side-note a { color: var(--ink-soft); }
.side-note a:hover { color: var(--accent-strong); }

.main { padding: 3rem 2.5rem 5rem; min-width: 0; }
.main-inner { max-width: 620px; }

.category { margin-bottom: 3.25rem; scroll-margin-top: 1.5rem; }
.category:last-child { margin-bottom: 0; }
.category-head { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; border-bottom: 1px solid var(--line-strong); padding-bottom: 0.6rem; margin-bottom: 1.6rem; }
.category-label { font-family: var(--font-display); font-style: italic; font-size: 1.3rem; font-weight: 500; margin: 0; }
.category-count { font-size: 0.78rem; color: var(--ink-faint); font-variant-numeric: tabular-nums; white-space: nowrap; }

.item-list { display: flex; flex-direction: column; }
.item { padding: 1.15rem 0; border-bottom: 1px solid var(--line); }
.item:first-child { padding-top: 0; }
.item:last-child { border-bottom: none; }
.item-title { font-family: var(--font-display); font-size: 1.15rem; font-weight: 500; line-height: 1.35; margin: 0 0 0.55rem; text-wrap: balance; }
.item-title a { color: var(--ink); text-decoration: none; background-image: linear-gradient(var(--ink-faint), var(--ink-faint)); background-position: 0 100%; background-repeat: no-repeat; background-size: 0% 1px; transition: background-size 0.2s ease, color 0.2s ease; }
.item-title a:hover { color: var(--accent-strong); background-size: 100% 1px; }
.item-title a:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }
.item-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; font-family: var(--font-mono); font-size: 0.68rem; color: var(--ink-faint); margin-bottom: 0.45rem; }
.meta-source { text-transform: uppercase; letter-spacing: 0.04em; color: var(--ink-faint); }
.meta-dot { color: var(--line-strong); }
.geo-pill { font-weight: 700; letter-spacing: 0.03em; padding: 0.12rem 0.5rem; border-radius: 4px; background: var(--panel); border: 1px solid var(--line-strong); color: var(--ink-soft); text-transform: uppercase; white-space: nowrap; }
.geo-pill.geo-local { background: var(--accent-soft); border-color: transparent; color: var(--accent-strong); }
.meta-date { color: var(--ink-faint); }
.relevance-score { margin-left: auto; font-weight: 700; color: var(--accent-strong); background: var(--accent-soft); padding: 0.12rem 0.5rem; border-radius: 4px; }
.item-summary { font-family: var(--font-body); font-size: 0.88rem; line-height: 1.55; color: var(--ink-soft); margin: 0; max-width: 62ch; }
.empty-note { font-size: 0.88rem; color: var(--ink-faint); font-style: italic; }

@media (max-width: 780px) {
  .site-header { padding: 2.5rem 1.25rem 1.5rem; }
  .page-shell { display: block; }
  .sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--line); padding: 2rem 1.25rem 1.75rem; }
  .side-nav { flex-direction: row; flex-wrap: wrap; }
  .side-nav a { flex: 0 0 auto; border-radius: 100px; }
  .main { padding: 2rem 1.25rem 4rem; }
  .main-inner { max-width: none; }
}
</style>
"""


def format_date(iso_string: str) -> str:
    """Short 'Jul 14' style date for the item meta line."""
    if not iso_string:
        return ""
    try:
        return datetime.fromisoformat(iso_string).strftime("%b %-d")
    except ValueError:
        return ""


def render_item(row) -> str:
    title = html.escape(row["title"])
    source = html.escape(row["source"])
    link = html.escape(row["link"] or "#")
    geo_key = row["geo_scope"] or "global"
    geo_label = html.escape(GEO_LABELS.get(geo_key, geo_key))
    score = row["relevance_score"] or 0
    summary = row["summary"] or ""
    show_summary = summary and summary.lower()[:40] not in row["title"].lower()
    item_date = format_date(row["published_at"] or row["fetched_at"])

    summary_html = f'<p class="item-summary">{html.escape(summary)}</p>' if show_summary else ""
    date_html = f'<span class="meta-dot">&middot;</span><span class="meta-date">{item_date}</span>' if item_date else ""

    return f"""
    <article class="item">
      <h3 class="item-title"><a href="{link}" target="_blank" rel="noopener">{title}</a></h3>
      <div class="item-meta">
        <span class="meta-source">{source}</span>
        <span class="meta-dot">&middot;</span>
        <span class="geo-pill geo-{geo_key}">{geo_label}</span>
        {date_html}
        <span class="relevance-score" title="Relevance score">{score}/5</span>
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
            f'<a href="#{slug}">{html.escape(label)} '
            f'<span class="side-count">{len(rows)}</span></a>'
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
    nav = f'<nav class="side-nav" aria-label="Jump to category">{"".join(nav_items)}</nav>' if nav_items else ""

    description = (
        "The daily business and industry briefing for medical-aesthetics professionals. "
        "Regulatory updates, treatment trends, market intelligence, and growth strategies, "
        "filtered into what actually matters for your clinic."
    )
    site_url = "https://theaestheticbrief.ca/"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Aesthetic Brief</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{site_url}">
<meta property="og:type" content="website">
<meta property="og:title" content="The Aesthetic Brief">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{site_url}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="The Aesthetic Brief">
<meta name="twitter:description" content="{html.escape(description)}">
<link rel="icon" href="data:image/svg+xml;base64,{FAVICON_SVG}">
{BEEHIIV_ATTRIBUTION}
{STYLE}
</head>
<body>
<header class="site-header">
  <p class="eyebrow">Independent Intelligence for Aesthetic Medicine</p>
  <h1 class="brand-title">The Aesthetic Brief</h1>
  <p class="site-tagline">The daily business and industry briefing for medical-aesthetics professionals.</p>
</header>
<div class="subscribe-banner">
  <div class="subscribe-banner-inner">
    <div class="subscribe-embed">{BEEHIIV_EMBED}</div>
  </div>
</div>
<div class="page-shell">
  <aside class="sidebar">
    <p class="sidebar-label">Sections</p>
    {nav}
    <p class="side-note">Updated {date.today().isoformat()} &middot; <span class="tabular">{total}</span> item(s) from the last {WINDOW_DAYS} days.<br><br>We monitor regulators, trade publications, business news, and clinical sources daily, filtering out low-relevance coverage.<br><br>Compiled daily by The Aesthetic Brief intelligence desk.<br><br><a href="/about.html">About &amp; contact</a> &middot; <a href="/privacy.html">Privacy</a></p>
  </aside>
  <main class="main">
    <div class="main-inner">
      {body}
    </div>
  </main>
</div>
</body>
</html>
"""


def write_sitemap() -> Path:
    """Just the homepage for now - add an entry per page if/when archive pages exist."""
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://theaestheticbrief.ca/</loc>
    <lastmod>{date.today().isoformat()}</lastmod>
    <changefreq>daily</changefreq>
  </url>
</urlset>
"""
    out_path = DOCS_DIR / "sitemap.xml"
    out_path.write_text(sitemap, encoding="utf-8")
    return out_path


def write_site(conn, min_score: int = 3) -> Path:
    DOCS_DIR.mkdir(exist_ok=True)
    out_path = DOCS_DIR / "index.html"
    out_path.write_text(build_site(conn, min_score), encoding="utf-8")
    write_sitemap()
    return out_path
