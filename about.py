"""
Generates the static docs/about.html page - who's behind The Aesthetic
Brief, who it's for, and how stories get selected. Content is fixed
(doesn't depend on scan data), so this isn't wired into scanner.py's
daily run - regenerate manually by running this file directly whenever
the copy changes.

Reuses webpage.py's STYLE/FAVICON_SVG so this page automatically stays
in sync with the main site's colors, fonts, and light/dark theming
rather than maintaining a second copy of the design system.
"""

from pathlib import Path

from webpage import STYLE, FAVICON_SVG

DOCS_DIR = Path(__file__).parent / "docs"

PAGE_STYLE = """<style>
.about-page { max-width: 640px; margin: 0 auto; padding: 4rem 1.5rem 6rem; }
.about-back { font-size: 0.82rem; color: var(--ink-faint); text-decoration: none; display: inline-block; margin-bottom: 2rem; }
.about-back:hover { color: var(--accent-strong); }
.about-eyebrow { font-size: 0.66rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); margin: 0 0 0.9rem; }
.about-title { font-family: var(--font-display); font-style: italic; font-size: clamp(1.9rem, 4vw, 2.4rem); font-weight: 500; line-height: 1.1; margin: 0 0 2.5rem; text-wrap: balance; }
.about-page h2 { font-family: var(--font-display); font-style: italic; font-size: 1.25rem; font-weight: 500; margin: 2.25rem 0 1rem; }
.about-page p { font-size: 0.98rem; line-height: 1.7; color: var(--ink-soft); margin: 0 0 1.1rem; }
.about-page a { color: var(--accent-strong); }
.about-signoff { font-family: var(--font-display); font-style: italic; color: var(--ink); margin-top: 0.5rem; }
</style>
"""

BODY = """
<a class="about-back" href="/">&larr; Back to The Aesthetic Brief</a>
<p class="about-eyebrow">About</p>
<h1 class="about-title">Why this exists</h1>

<p>I'm Manny Shiferaw. I built The Aesthetic Brief because I was tired of manually digging through Google News, regulator bulletins, and trade publications every week just to keep up with what's actually happening in medical aesthetics &mdash; new injectable approvals, regulatory changes, industry M&amp;A, shifting consumer attitudes.</p>

<p>What started as a tool for myself and my own team quickly felt like something worth sharing. If I needed this, I figured other people running clinics probably did too.</p>

<h2>Who this is for</h2>
<p>Aesthetic medicine operators &mdash; clinic owners, medical directors, and the people making day-to-day decisions about what treatments to offer, how to stay compliant, and where the industry is heading. This isn't written for patients or general beauty readers; it's written for the business side of running a clinic.</p>

<h2>How stories get selected</h2>
<p>Every day, an automated system checks a fixed list of sources &mdash; regulators (Health Canada, FDA, EMA), trade publications, and targeted industry news searches &mdash; and scores each story for relevance using rules built around what actually matters to a clinic operator. Anything below a relevance threshold doesn't make the cut. This isn't AI-generated or AI-summarized content; it's rule-based filtering of real reporting from real sources, with my own judgment applied on top for whatever goes into the weekly email.</p>

<h2>Get in touch</h2>
<p>Questions, feedback, or something I should be covering that I'm not? <a href="mailto:hello@theaestheticbrief.ca">hello@theaestheticbrief.ca</a></p>

<p class="about-signoff">&mdash; Manny</p>
"""


def build_about() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>About &mdash; The Aesthetic Brief</title>
<meta name="description" content="Who's behind The Aesthetic Brief, who it's written for, and how stories get selected.">
<link rel="icon" href="data:image/svg+xml;base64,{FAVICON_SVG}">
{STYLE}
{PAGE_STYLE}
</head>
<body>
<div class="about-page">
{BODY}
</div>
</body>
</html>
"""


def write_about() -> Path:
    DOCS_DIR.mkdir(exist_ok=True)
    out_path = DOCS_DIR / "about.html"
    out_path.write_text(build_about(), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    path = write_about()
    print(f"Wrote {path}")
