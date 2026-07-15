"""
Youth Bar Medical Aesthetics - industry news scanner.

Usage:
    python scanner.py run                    Fetch every source, score, save digest
    python scanner.py run --category regulatory   Only run one category (useful for testing)

See README.md for setup and scheduling instructions.
"""

import argparse
from datetime import datetime, timezone

from config import SOURCES, CATEGORIES
import db
import sources as source_fetcher
import scoring
import digest
import webpage
import emaildraft


def run(category: str | None):
    if category and category not in CATEGORIES:
        valid = ", ".join(CATEGORIES)
        raise SystemExit(f"Unknown category '{category}'. Valid options: {valid}")

    active_sources = [s for s in SOURCES if not category or s["category"] == category]
    if not active_sources:
        raise SystemExit(f"No sources configured yet for category '{category}'.")

    conn = db.connect()
    fetched_at = datetime.now(timezone.utc).isoformat()

    new_count = 0
    dup_count = 0

    print(f"Fetching {len(active_sources)} source(s)...")
    for source in active_sources:
        items = source_fetcher.fetch_source(source)
        for item in items:
            item["relevance_score"] = scoring.score_item(item)
            item["geo_scope"] = scoring.geo_scope(item)
            item["fetched_at"] = fetched_at
            is_new = db.insert_item(conn, item)
            if is_new:
                new_count += 1
            else:
                dup_count += 1

    print(f"\n{new_count} new item(s) stored, {dup_count} already seen (skipped).")

    out_path = digest.write_digest(conn, fetched_at, category)
    print(f"Digest written to: {out_path}")

    site_path = webpage.write_site(conn)
    print(f"Website updated: {site_path}")

    draft_path = emaildraft.write_draft(conn)
    print(f"Email draft written to: {draft_path}")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Youth Bar industry news scanner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Fetch sources and build today's digest")
    run_parser.add_argument(
        "--category",
        choices=list(CATEGORIES.keys()),
        default=None,
        help="Only run sources for this category (default: all configured categories)",
    )

    args = parser.parse_args()

    if args.command == "run":
        run(args.category)


if __name__ == "__main__":
    main()
