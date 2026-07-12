"""
Rule-based scoring: no AI, no paid API. Every item starts at its source's
base_score (set in config.py), gets bumped for matching business-relevant
keywords, and gets tagged with a rough geographic scope. Fully deterministic
and free to run as often as you like.
"""

from config import KEYWORD_BOOSTS, GEO_KEYWORDS, GEO_DEFAULT


def score_item(item: dict) -> int:
    text = f"{item['title']} {item['summary']}".lower()
    score = item["base_score"]
    for boost, keywords in KEYWORD_BOOSTS.items():
        if any(kw in text for kw in keywords):
            score += boost
    return max(1, min(5, score))


def geo_scope(item: dict) -> str:
    text = f"{item['title']} {item['summary']}".lower()
    for scope, keywords in GEO_KEYWORDS:
        if any(kw in text for kw in keywords):
            return scope
    return GEO_DEFAULT
