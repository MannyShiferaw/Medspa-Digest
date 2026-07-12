"""
SQLite storage. One table, one job: remember which items we've already
seen so re-running the scanner doesn't produce duplicate digest entries.
"""

import sqlite3
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "news.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT,
    summary TEXT,
    category TEXT,
    geo_scope TEXT,
    relevance_score INTEGER,
    published_at TEXT,
    fetched_at TEXT NOT NULL
);
"""


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def make_guid(entry_guid: str | None, link: str | None, title: str, source: str) -> str:
    """Feed entries usually have a stable guid; fall back to a hash if not."""
    if entry_guid:
        return entry_guid
    if link:
        return link
    raw = f"{source}:{title}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def insert_item(conn, item: dict) -> bool:
    """Insert one item. Returns True if it was new, False if it was a duplicate."""
    try:
        conn.execute(
            """INSERT INTO items
               (guid, source, title, link, summary, category, geo_scope,
                relevance_score, published_at, fetched_at)
               VALUES (:guid, :source, :title, :link, :summary, :category,
                       :geo_scope, :relevance_score, :published_at, :fetched_at)""",
            item,
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # guid already in the DB - we've seen this item before
        return False


def fetch_for_digest(conn, category: str | None, min_score: int, fetched_at: str):
    """
    Items for *this run's* digest only - matched on the exact fetched_at
    timestamp passed in from scanner.py. Without this filter, every past
    relevant item (already seen and skipped as a duplicate) would show up
    in every future digest forever, since dedupe only stops re-insertion,
    not re-selection.
    """
    query = "SELECT * FROM items WHERE relevance_score >= ? AND fetched_at = ?"
    params = [min_score, fetched_at]
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY category ASC, relevance_score DESC, published_at DESC"
    conn.row_factory = sqlite3.Row
    return conn.execute(query, params).fetchall()


def fetch_recent(conn, category: str | None, min_score: int, since_iso: str):
    """
    Items found in the last N days (matched on fetched_at, which is always
    populated - unlike published_at, which some feeds omit). Used by the
    website, which shows a rolling window rather than resetting to empty
    on quiet days like the local per-run digest does.
    """
    query = "SELECT * FROM items WHERE relevance_score >= ? AND fetched_at >= ?"
    params = [min_score, since_iso]
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY category ASC, relevance_score DESC, published_at DESC"
    conn.row_factory = sqlite3.Row
    return conn.execute(query, params).fetchall()
