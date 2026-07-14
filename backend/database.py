"""
Zoara persistence layer.
SQLite is used for simplicity and true persistence across restarts -
the Brand Brain lives in zoara.db and survives server restarts, which is
the whole point: Zoara should get smarter about a brand every time it's used.
"""
import sqlite3
import json
import os
import uuid
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "zoara.db")


def now():
    return datetime.now(timezone.utc).isoformat()


def new_id():
    return str(uuid.uuid4())


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS brands (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    strategy_answers TEXT DEFAULT '{}',
    strategy_doc_text TEXT DEFAULT '',
    strategy_doc_filename TEXT DEFAULT '',
    formats TEXT DEFAULT '[]',
    platforms TEXT DEFAULT '[]',
    goals TEXT DEFAULT '{}',
    build_specs TEXT DEFAULT '{}',
    creative_angles TEXT DEFAULT '{}',
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS competitors (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    label TEXT DEFAULT '',
    extracted_summary TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS inspo_links (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    room TEXT NOT NULL,
    url TEXT NOT NULL,
    user_note TEXT DEFAULT '',
    extracted_summary TEXT DEFAULT '',
    extracted_pattern TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS research_jobs (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'running',
    requested_count INTEGER DEFAULT 30,
    error TEXT DEFAULT '',
    created_at TEXT,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS research_ideas (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    job_id TEXT,
    topic TEXT NOT NULL,
    source_pattern TEXT DEFAULT '',
    suggested_angle TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    tweak_comment TEXT DEFAULT '',
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS content_items (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    format TEXT NOT NULL,
    platform TEXT NOT NULL,
    research_idea_id TEXT,
    parent_id TEXT,
    title TEXT DEFAULT '',
    content_json TEXT DEFAULT '{}',
    raw_text TEXT DEFAULT '',
    status TEXT DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS critiques (
    id TEXT PRIMARY KEY,
    content_item_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    strategist_score INTEGER,
    customer_score INTEGER,
    overall_score REAL,
    strategist_feedback TEXT DEFAULT '',
    customer_feedback TEXT DEFAULT '',
    improvement_notes TEXT DEFAULT '',
    passed_cutoff INTEGER DEFAULT 0,
    user_comment TEXT DEFAULT '',
    created_at TEXT
);
"""


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def row_to_dict(row, json_fields=None):
    if row is None:
        return None
    d = dict(row)
    for f in (json_fields or []):
        if f in d and d[f] is not None:
            try:
                d[f] = json.loads(d[f])
            except (json.JSONDecodeError, TypeError):
                d[f] = {} if not d[f].strip().startswith("[") else []
    return d
