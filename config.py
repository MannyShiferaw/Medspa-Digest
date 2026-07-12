"""
All the knobs for the scanner live here: which sources to pull from,
which keywords bump a story's relevance score, and how the scoring
math works. Edit this file (not scanner.py/scoring.py) to tune things.
"""

# ---------------------------------------------------------------------------
# Google News RSS helper
# ---------------------------------------------------------------------------
# Google News lets you subscribe to a search as an RSS feed. hl/gl/ceid control
# language/country. "GLOBAL" queries use English/US so we catch worldwide
# trade coverage; "CANADA" queries bias results toward Canadian sources.
GOOGLE_NEWS_GLOBAL = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
GOOGLE_NEWS_CANADA = "https://news.google.com/rss/search?q={query}&hl=en-CA&gl=CA&ceid=CA:en"


def google_news_url(query: str, canada: bool = False) -> str:
    from urllib.parse import quote_plus
    template = GOOGLE_NEWS_CANADA if canada else GOOGLE_NEWS_GLOBAL
    return template.format(query=quote_plus(query))


# ---------------------------------------------------------------------------
# Sources, grouped by category.
#
# Each source is a dict:
#   name       - shown in the digest as the source
#   url        - RSS feed URL (built via google_news_url() for Google News ones)
#   category   - one of the CATEGORIES keys below
#   base_score - starting relevance score (1-5) before keyword boosts.
#                Confirmed trade/regulator feeds start higher than generic
#                Google News hits because they're pre-filtered to the industry.
# ---------------------------------------------------------------------------
CATEGORIES = {
    "regulatory": "Regulatory / Legal",
    "clinical": "Clinical / Treatment Trends",
    "financial": "Financial / Industry Trends",
    "marketing": "Marketing / Growth Strategy",
    "consumer": "Consumer Trend Shifts",
    "competitive": "Competitive / Market Landscape",
    "financing": "Business Financing",
}

SOURCES = [
    # --- Regulatory / legal: direct regulator + trade feeds -----------------
    # These feeds cover ALL health products/drugs/devices, not just aesthetics,
    # so - like the Google News queries below - they start at 2 and need a
    # keyword match (see KEYWORD_BOOSTS) to clear the relevance bar.
    {
        "name": "Health Canada - Health Products Alerts & Recalls",
        "url": "https://recalls-rappels.canada.ca/en/feed/health-products-alerts-recalls",
        "category": "regulatory",
        "base_score": 2,
    },
    {
        "name": "Health Canada - Medical Devices Alerts & Recalls",
        "url": "https://recalls-rappels.canada.ca/en/feed/medical-devices-alerts-recalls",
        "category": "regulatory",
        "base_score": 2,
    },
    {
        "name": "Health Canada - Compliance & Enforcement (Drugs & Health Products)",
        "url": "https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/rss/dhp-mps/compli-conform-eng.xml",
        "category": "regulatory",
        "base_score": 2,
    },
    {
        "name": "FDA MedWatch Safety Alerts",
        "url": "http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/MedWatch/rss.xml",
        "category": "regulatory",
        "base_score": 2,
    },
    {
        "name": "EMA News & Press Releases",
        "url": "https://www.ema.europa.eu/en/news.xml",
        "category": "regulatory",
        "base_score": 2,
    },
    # --- Regulatory / legal: Google News queries -----------------------------
    # Queries are kept narrow (aesthetics-specific terms, not generic ones like
    # "injectable" or "medical device") because Google News OR-matching will
    # otherwise flood the digest with unrelated pharma/device approvals.
    {
        "name": "Google News: Health Canada aesthetics/injectables",
        "url": google_news_url('"Health Canada" (Botox OR "dermal filler" OR "aesthetic device" OR "cosmetic device")'),
        "category": "regulatory",
        "base_score": 2,
    },
    {
        "name": "Google News: FDA aesthetic device/injectable approval",
        "url": google_news_url('FDA approval ("dermal filler" OR neurotoxin OR "aesthetic device" OR "cosmetic device" OR "energy-based device")'),
        "category": "regulatory",
        "base_score": 2,
    },
    {
        "name": "Google News: nursing/NP scope of practice aesthetics (Canada)",
        "url": google_news_url('"scope of practice" (nurse OR "nurse practitioner") (aesthetics OR injectables OR "medical spa")', canada=True),
        "category": "regulatory",
        "base_score": 2,
    },
    {
        "name": "Google News: Nova Scotia nursing/med spa regulation",
        "url": google_news_url('"Nova Scotia" (nursing OR "medical aesthetics" OR "medical spa") regulation', canada=True),
        "category": "regulatory",
        "base_score": 2,
    },
    {
        "name": "Google News: advertising/health claims aesthetics regulation",
        "url": google_news_url('advertising OR "health claims" regulation (cosmetic OR aesthetic) clinic'),
        "category": "regulatory",
        "base_score": 2,
    },

    # --- Clinical / treatment trends ------------------------------------
    {
        "name": "Global Cosmetics News",
        "url": "https://globalcosmeticsnews.com/feed/",
        "category": "clinical",
        "base_score": 2,
    },
    {
        "name": "Google News: new injectable/filler treatment launch",
        "url": google_news_url('new ("dermal filler" OR neurotoxin OR injectable) treatment launch'),
        "category": "clinical",
        "base_score": 2,
    },
    {
        "name": "Google News: energy-based aesthetic device launch",
        "url": google_news_url('(laser OR "energy-based device" OR "RF microneedling" OR ultrasound) aesthetic device launch'),
        "category": "clinical",
        "base_score": 2,
    },
    {
        "name": "Google News: regenerative/peptide aesthetic medicine",
        "url": google_news_url('(peptide OR "regenerative medicine" OR exosome OR PRP) (aesthetic OR skincare) treatment'),
        "category": "clinical",
        "base_score": 2,
    },
    {
        "name": "Google News: FDA/EMA/Health Canada aesthetic device approval",
        "url": google_news_url('(FDA OR EMA OR "Health Canada") approval (aesthetic OR cosmetic) (device OR injectable)'),
        "category": "clinical",
        "base_score": 2,
    },

    # --- Financial / industry trends -------------------------------------
    {
        "name": "Google News: med spa private equity/M&A",
        "url": google_news_url('("med spa" OR "medical spa" OR aesthetics) (acquisition OR "private equity" OR "roll-up" OR merger)'),
        "category": "financial",
        "base_score": 2,
    },
    {
        "name": "Google News: aesthetics clinic M&A/funding (Canada)",
        "url": google_news_url('(medspa OR "medical spa" OR "aesthetics clinic") (acquisition OR merger OR funding)', canada=True),
        "category": "financial",
        "base_score": 2,
    },
    {
        "name": "Google News: med spa industry benchmarks",
        "url": google_news_url('("medical spa" OR "med spa") industry (benchmark OR report OR revenue OR statistics)'),
        "category": "financial",
        "base_score": 2,
    },
    {
        "name": "Google News: aesthetics/wellness funding rounds",
        "url": google_news_url('(aesthetics OR wellness OR skincare) startup ("funding round" OR "venture capital" OR "Series A" OR "Series B")'),
        "category": "financial",
        "base_score": 2,
    },

    # --- Marketing / growth strategy ---------------------------------------
    {
        "name": "Google News: med spa marketing strategy",
        "url": google_news_url('("med spa" OR "medical spa") marketing (strategy OR trends)'),
        "category": "marketing",
        "base_score": 2,
    },
    {
        "name": "Google News: membership/subscription model wellness clinics",
        "url": google_news_url('(membership OR subscription) model (medspa OR "med spa" OR "wellness clinic" OR aesthetics)'),
        "category": "marketing",
        "base_score": 2,
    },
    {
        "name": "Google News: aesthetics clinic social/influencer marketing",
        "url": google_news_url('(aesthetics OR medspa OR "med spa") (influencer OR "social media" OR UGC OR TikTok) marketing'),
        "category": "marketing",
        "base_score": 2,
    },

    # --- Consumer trend shifts -----------------------------------------------
    {
        "name": "Google News: Ozempic face / GLP-1 aesthetic trend",
        "url": google_news_url('"Ozempic face" OR (GLP-1 (aesthetic OR skin) trend)'),
        "category": "consumer",
        "base_score": 2,
    },
    {
        "name": "Google News: Gen Z aesthetics/skincare trend",
        "url": google_news_url('"Gen Z" (skincare OR Botox OR aesthetics OR "anti-aging") trend'),
        "category": "consumer",
        "base_score": 2,
    },
    {
        "name": "Google News: social media-driven beauty trends",
        "url": google_news_url('"skin cycling" OR skinimalism OR (TikTok skincare trend)'),
        "category": "consumer",
        "base_score": 2,
    },
    {
        "name": "Google News: shifting attitudes toward cosmetic procedures",
        "url": google_news_url('consumer attitudes (Botox OR filler OR "cosmetic procedures") (shift OR normalization OR stigma)'),
        "category": "consumer",
        "base_score": 2,
    },

    # --- Competitive / market landscape --------------------------------------
    {
        "name": "Google News: Allergan Aesthetics / AbbVie news",
        "url": google_news_url('("Allergan Aesthetics" OR AbbVie) aesthetics news'),
        "category": "competitive",
        "base_score": 2,
    },
    {
        "name": "Google News: Galderma news",
        "url": google_news_url('Galderma (aesthetics OR injectable OR launch OR earnings)'),
        "category": "competitive",
        "base_score": 2,
    },
    {
        "name": "Google News: Merz Aesthetics news",
        "url": google_news_url('"Merz Aesthetics" OR "Merz Pharma" news'),
        "category": "competitive",
        "base_score": 2,
    },
    {
        "name": "Google News: Halifax/Atlantic Canada med spa news",
        "url": google_news_url('(Halifax OR "Nova Scotia" OR "Atlantic Canada") ("med spa" OR "medical spa" OR "medical aesthetics" OR clinic)', canada=True),
        "category": "competitive",
        "base_score": 2,
    },

    # --- Business financing (checked, but not forced weekly) -----------------
    {
        "name": "Google News: small business/medical practice lending (Canada)",
        "url": google_news_url('("small business" OR "medical practice") (lending OR financing) Canada', canada=True),
        "category": "financing",
        "base_score": 2,
    },
    {
        "name": "Google News: BDC/healthcare clinic financing (Canada)",
        "url": google_news_url('(BDC OR "Business Development Bank") financing (clinic OR healthcare OR "medical practice")', canada=True),
        "category": "financing",
        "base_score": 2,
    },
]

# ---------------------------------------------------------------------------
# Keyword boosts applied on top of a source's base_score.
# Matching is case-insensitive against the item's title + summary.
# Score is clamped to 1-5 after boosts.
# ---------------------------------------------------------------------------
KEYWORD_BOOSTS = {
    2: [
        "health canada", "botox", "dysport", "xeomin", "daxxify",
        "juvederm", "restylane", "dermal filler", "allergan", "abbvie",
        "galderma", "merz", "cooltone", "coolsculpting", "morpheus8", "sculptra",
        "kybella", "ultherapy", "hifu", "rf microneedling", "laser resurfacing",
        "nurse practitioner", "scope of practice", "med spa", "medspa",
        "medical aesthetics", "medical spa", "aesthetic clinic", "aesthetic device",
        "cosmetic device", "neurotoxin", "ozempic face", "glp-1",
        "private equity", "roll-up", "rollup",
    ],
    1: [
        "aesthetic", "cosmetic surgery", "skincare", "dermatolog", "wellness clinic",
        "anti-aging", "anti aging", "regenerative medicine", "microneedling",
        "acquisition", "merger", "funding round", "venture capital",
        "gen z", "skin cycling", "skinimalism", "influencer marketing",
        "membership model", "subscription model", "med spa marketing",
        "medical practice",
    ],
}

# ---------------------------------------------------------------------------
# Geographic scope keywords, checked in priority order (first match wins).
# ---------------------------------------------------------------------------
GEO_KEYWORDS = [
    ("local", ["halifax", "nova scotia", "atlantic canada", "dartmouth", "maritimes"]),
    ("canada", ["canada", "canadian", "health canada", "ontario", "british columbia",
                "alberta", "quebec", "manitoba", "saskatchewan"]),
    ("north_america", ["united states", "u.s.", "fda", "usa"]),
]
GEO_DEFAULT = "global"

MIN_RELEVANCE_TO_INCLUDE = 3

# Google News queries can return up to ~100 historical results on a feed's
# first fetch. We only look at the newest N per source per run so the very
# first digest isn't an unreadable dump of years of back-coverage - once
# running daily, most queries will only turn up a handful of genuinely new
# items per day anyway, so this cap rarely matters after day one.
MAX_ITEMS_PER_SOURCE = 25
