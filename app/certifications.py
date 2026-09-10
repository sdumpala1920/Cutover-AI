"""Certification Tracker: merges the research-editable seed list in
content/certifications.json with the user's mutable status/notes in the
cert_progress table — same content-vs-progress split used throughout.
"""
import re
from datetime import datetime

from . import content_loader as content
from .db import get_db


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def get_all():
    db = get_db()
    rows = {r["cert_key"]: r for r in db.execute("SELECT * FROM cert_progress").fetchall()}

    result = []
    for cert in content.get_certifications():
        key = slugify(cert["name"])
        progress = rows.get(key)
        result.append({
            **cert,
            "cert_key": key,
            "status": progress["status"] if progress else "not_started",
            "user_notes": progress["notes"] if progress else "",
        })
    return result


def update(cert_key, status, notes):
    db = get_db()
    now = datetime.now().isoformat(timespec="seconds")
    db.execute(
        "INSERT INTO cert_progress (cert_key, status, notes, updated_at) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(cert_key) DO UPDATE SET status = excluded.status, "
        "notes = excluded.notes, updated_at = excluded.updated_at",
        (cert_key, status, notes, now),
    )
    db.commit()
