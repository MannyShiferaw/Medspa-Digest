"""
Generates the static docs/privacy.html page. Content is fixed, not tied
to scan data - regenerate manually by running this file directly if the
copy ever changes.

Not legal advice - this is a standard, honest disclosure of what's
actually collected (email via the Beehiiv signup form, plus basic
attribution data) and who it's shared with (Beehiiv, as the email
service provider). Revisit with a real lawyer if the business scales
into anything more involved than that.
"""

from datetime import date
from pathlib import Path

from webpage import STYLE, FAVICON_SVG

DOCS_DIR = Path(__file__).parent / "docs"

PAGE_STYLE = """<style>
.legal-page { max-width: 640px; margin: 0 auto; padding: 4rem 1.5rem 6rem; }
.legal-back { font-size: 0.82rem; color: var(--ink-faint); text-decoration: none; display: inline-block; margin-bottom: 2rem; }
.legal-back:hover { color: var(--accent-strong); }
.legal-eyebrow { font-size: 0.66rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); margin: 0 0 0.9rem; }
.legal-title { font-family: var(--font-display); font-style: italic; font-size: clamp(1.9rem, 4vw, 2.4rem); font-weight: 500; line-height: 1.1; margin: 0 0 0.5rem; text-wrap: balance; }
.legal-updated { font-size: 0.82rem; color: var(--ink-faint); margin: 0 0 2.5rem; }
.legal-page h2 { font-family: var(--font-display); font-style: italic; font-size: 1.15rem; font-weight: 500; margin: 2rem 0 0.85rem; }
.legal-page p, .legal-page li { font-size: 0.94rem; line-height: 1.7; color: var(--ink-soft); margin: 0 0 1rem; }
.legal-page ul { margin: 0 0 1rem; padding-left: 1.25rem; }
.legal-page a { color: var(--accent-strong); }
</style>
"""

BODY = f"""
<a class="legal-back" href="/">&larr; Back to The Aesthetic Brief</a>
<p class="legal-eyebrow">Privacy</p>
<h1 class="legal-title">Privacy Policy</h1>
<p class="legal-updated">Last updated {date.today().isoformat()}</p>

<h2>What we collect</h2>
<p>If you subscribe to the weekly email, we collect your <strong>email address</strong> and basic information about where you signed up (e.g. via theaestheticbrief.ca rather than elsewhere), so we can send you the newsletter and understand roughly what's working. We don't collect names, phone numbers, or anything else unless you send it to us directly. We don't sell, rent, or share your email with advertisers.</p>
<p>Just browsing the site doesn't require an account and doesn't collect anything beyond standard, anonymous server logs.</p>

<h2>Who has access to it</h2>
<p>Subscriber emails are stored and managed by <a href="https://www.beehiiv.com" target="_blank" rel="noopener">Beehiiv</a>, the email service provider that powers the newsletter. They act as our data processor, bound by their own privacy and security practices. We don't otherwise share your email with third parties.</p>

<h2>Your choices</h2>
<p>Every email includes an unsubscribe link &mdash; one click removes you from the list immediately. You can also email <a href="mailto:hello@theaestheticbrief.ca">hello@theaestheticbrief.ca</a> any time to ask what we have on file or to have it deleted. If this policy changes in any meaningful way, we'll update this page and the date above.</p>
"""


def build_privacy() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy Policy &mdash; The Aesthetic Brief</title>
<meta name="description" content="What The Aesthetic Brief collects, why, and how to opt out.">
<link rel="icon" href="data:image/svg+xml;base64,{FAVICON_SVG}">
{STYLE}
{PAGE_STYLE}
</head>
<body>
<div class="legal-page">
{BODY}
</div>
</body>
</html>
"""


def write_privacy() -> Path:
    DOCS_DIR.mkdir(exist_ok=True)
    out_path = DOCS_DIR / "privacy.html"
    out_path.write_text(build_privacy(), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    path = write_privacy()
    print(f"Wrote {path}")
