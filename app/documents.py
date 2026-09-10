"""Generic versioned-document store, shared by the Portfolio module (rollout
plan, story bank) and the Resume module (master resume, per-role variants).

Every save inserts a new row keyed by doc_key; the "current" version is
just the highest id for that key. Nothing is ever overwritten in place, so
history and "restore an old version" both fall out for free.
"""
from datetime import datetime

from .db import get_db


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def save_version(doc_key, content, notes=None):
    db = get_db()
    db.execute(
        "INSERT INTO doc_versions (doc_key, content, notes, created_at) "
        "VALUES (?, ?, ?, ?)",
        (doc_key, content, notes, _now_iso()),
    )
    db.commit()


def get_current(doc_key):
    db = get_db()
    return db.execute(
        "SELECT * FROM doc_versions WHERE doc_key = ? ORDER BY id DESC LIMIT 1",
        (doc_key,),
    ).fetchone()


def get_history(doc_key, limit=25):
    db = get_db()
    return db.execute(
        "SELECT * FROM doc_versions WHERE doc_key = ? ORDER BY id DESC LIMIT ?",
        (doc_key, limit),
    ).fetchall()


def get_version(version_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM doc_versions WHERE id = ?", (version_id,)
    ).fetchone()


def count_versions(doc_key):
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) AS n FROM doc_versions WHERE doc_key = ?", (doc_key,)
    ).fetchone()
    return row["n"]
