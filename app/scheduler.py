"""The daily session engine: resolves "today", handles the block timer, and
implements the auto-rolling catch-up logic.

Core idea (this is what makes catch-up automatic rather than a special case):
"Today's session" is always defined as *the first curriculum day that isn't
fully completed yet* — never "whatever day matches today's calendar date".
If a day is skipped or left half-done, it simply keeps being "today" until
it's finished; every later day quietly slides later with it. No shifting of
stored dates is ever needed, which is also why the projected completion
date recalculates for free from live progress counts.
"""
from datetime import date, datetime, timedelta

from flask import current_app

from . import content_loader as content
from .db import get_db

STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _ensure_day_row(db, day):
    db.execute(
        "INSERT OR IGNORE INTO day_progress (day_key, week, day, status) "
        "VALUES (?, ?, ?, ?)",
        (day["day_key"], day["week"], day["day"], STATUS_PENDING),
    )
    for b in day["blocks"]:
        db.execute(
            "INSERT OR IGNORE INTO block_progress (block_key, day_key, status) "
            "VALUES (?, ?, ?)",
            (b["block_key"], day["day_key"], STATUS_PENDING),
        )


def _block_rows_for_day(db, day_key):
    return db.execute(
        "SELECT * FROM block_progress WHERE day_key = ?", (day_key,)
    ).fetchall()


def _recompute_day_status(db, day_key):
    blocks = _block_rows_for_day(db, day_key)
    statuses = [b["status"] for b in blocks]
    if statuses and all(s == STATUS_COMPLETED for s in statuses):
        db.execute(
            "UPDATE day_progress SET status = ?, "
            "completed_at = COALESCE(completed_at, ?) WHERE day_key = ?",
            (STATUS_COMPLETED, _now_iso(), day_key),
        )
    elif any(s in (STATUS_IN_PROGRESS, STATUS_COMPLETED) for s in statuses):
        db.execute(
            "UPDATE day_progress SET status = ?, "
            "first_started_at = COALESCE(first_started_at, ?) WHERE day_key = ?",
            (STATUS_IN_PROGRESS, _now_iso(), day_key),
        )
    else:
        db.execute(
            "UPDATE day_progress SET status = ? WHERE day_key = ?",
            (STATUS_PENDING, day_key),
        )


def _merge_progress(day):
    """Attach live progress rows onto a content day dict."""
    db = get_db()
    _ensure_day_row(db, day)
    db.commit()

    day_row = db.execute(
        "SELECT * FROM day_progress WHERE day_key = ?", (day["day_key"],)
    ).fetchone()
    day["status"] = day_row["status"]
    day["completed_at"] = day_row["completed_at"]

    block_rows = {
        r["block_key"]: r for r in _block_rows_for_day(db, day["day_key"])
    }
    for b in day["blocks"]:
        row = block_rows[b["block_key"]]
        b["status"] = row["status"]
        b["accumulated_seconds"] = row["accumulated_seconds"]
        b["timer_started_at"] = row["timer_started_at"]
        b["last_confidence"] = row["last_confidence"]
        b["last_note"] = row["last_note"]
    return day


def resolve_today():
    """Return the current day-to-work-on, fully merged with progress state,
    or a dict describing that seeded content has run out.
    """
    for day in content.iter_days():
        merged = _merge_progress(day)
        if merged["status"] != STATUS_COMPLETED:
            return {"kind": "day", "day": merged}

    upcoming = content.next_unseeded_week()
    return {"kind": "awaiting_content", "week": upcoming}


def start_block(block_key):
    day, block = content.find_block(block_key)
    if not block:
        return False
    db = get_db()
    _ensure_day_row(db, day)
    row = db.execute(
        "SELECT timer_started_at, status FROM block_progress WHERE block_key = ?",
        (block_key,),
    ).fetchone()
    if row and row["timer_started_at"] is None and row["status"] != STATUS_COMPLETED:
        db.execute(
            "UPDATE block_progress SET status = ?, timer_started_at = ? "
            "WHERE block_key = ?",
            (STATUS_IN_PROGRESS, _now_iso(), block_key),
        )
        _recompute_day_status(db, day["day_key"])
        db.commit()
    return True


def stop_block(block_key, confidence, note):
    day, block = content.find_block(block_key)
    if not block:
        return False
    db = get_db()
    _ensure_day_row(db, day)
    row = db.execute(
        "SELECT timer_started_at, accumulated_seconds FROM block_progress "
        "WHERE block_key = ?",
        (block_key,),
    ).fetchone()
    if row is None:
        return False

    started_at = row["timer_started_at"]
    now = datetime.now()
    duration = 0
    if started_at:
        started_dt = datetime.fromisoformat(started_at)
        duration = max(0, int((now - started_dt).total_seconds()))
        db.execute(
            "INSERT INTO block_logs (block_key, started_at, stopped_at, "
            "duration_seconds, confidence, note) VALUES (?, ?, ?, ?, ?, ?)",
            (block_key, started_at, now.isoformat(timespec="seconds"),
             duration, confidence, note),
        )

    db.execute(
        "UPDATE block_progress SET status = ?, timer_started_at = NULL, "
        "accumulated_seconds = accumulated_seconds + ?, last_confidence = ?, "
        "last_note = ?, completed_at = ? WHERE block_key = ?",
        (STATUS_COMPLETED, duration, confidence, note,
         now.isoformat(timespec="seconds"), block_key),
    )
    _recompute_day_status(db, day["day_key"])
    db.commit()
    return True


def get_start_date():
    db = get_db()
    row = db.execute(
        "SELECT value FROM app_settings WHERE key = 'start_date'"
    ).fetchone()
    return date.fromisoformat(row["value"])


def is_rest_day(d):
    return d.weekday() in current_app.config["REST_WEEKDAYS"]


def _project_forward(from_date, remaining_study_slots):
    """Walk forward from from_date (exclusive) consuming one study slot per
    non-rest day, and return the date the last slot lands on."""
    if remaining_study_slots <= 0:
        return from_date
    d = from_date
    slots_left = remaining_study_slots
    while slots_left > 0:
        d = d + timedelta(days=1)
        if not is_rest_day(d):
            slots_left -= 1
    return d


def get_projection():
    """Baseline (on-time) completion date vs. live projected completion
    date, recalculated from however much curriculum is actually done.
    """
    total_slots = current_app.config["TOTAL_CURRICULUM_DAYS"]
    start_date = get_start_date()
    today = date.today()

    db = get_db()
    completed = db.execute(
        "SELECT COUNT(*) AS n FROM day_progress WHERE status = 'completed'"
    ).fetchone()["n"]
    remaining = max(0, total_slots - completed)

    baseline_end = _project_forward(start_date - timedelta(days=1), total_slots)
    projected_end = _project_forward(today, remaining)

    delta_days = (projected_end - baseline_end).days
    return {
        "start_date": start_date,
        "total_slots": total_slots,
        "completed_slots": completed,
        "remaining_slots": remaining,
        "baseline_end": baseline_end,
        "projected_end": projected_end,
        "delta_days": delta_days,  # >0 means behind schedule
    }


def get_week_progress(week_number):
    """Minutes logged vs. target minutes for a given curriculum week, for
    the home screen's progress ring."""
    week = content.get_week(week_number)
    target_minutes = 0
    if week and week.get("status") == "seeded":
        for day in week.get("days", []):
            for b in day.get("blocks", []):
                target_minutes += b.get("target_minutes", 0)
    else:
        # Placeholder weeks have no authored blocks yet; estimate against
        # the spec's ~2 focused hours/day, 6 days/week target.
        target_minutes = current_app.config["DAYS_PER_WEEK"] * 120

    db = get_db()
    day_keys = [content.day_key(week_number, d) for d in range(1, 8)]
    placeholders = ",".join("?" for _ in day_keys)
    row = db.execute(
        f"SELECT COALESCE(SUM(bp.accumulated_seconds), 0) AS secs "
        f"FROM block_progress bp WHERE bp.day_key IN ({placeholders})",
        day_keys,
    ).fetchone()
    logged_minutes = round((row["secs"] or 0) / 60)

    percent = 0
    if target_minutes > 0:
        percent = min(100, round(100 * logged_minutes / target_minutes))

    return {
        "week": week_number,
        "target_minutes": target_minutes,
        "logged_minutes": logged_minutes,
        "percent": percent,
    }


def get_all_weeks_status():
    """Per curriculum week: how many of its days are completed, out of how
    many total, and whether the week is fully done. Days never visited by
    resolve_today() yet simply have no row (treated as not completed) —
    this never needs to lazily create rows for days far in the future."""
    db = get_db()
    weeks = {}
    for day in content.iter_days():
        weeks.setdefault(day["week"], []).append(day["day_key"])

    result = {}
    for week, day_keys in weeks.items():
        placeholders = ",".join("?" for _ in day_keys)
        rows = db.execute(
            f"SELECT status FROM day_progress WHERE day_key IN ({placeholders})",
            day_keys,
        ).fetchall()
        completed = sum(1 for r in rows if r["status"] == STATUS_COMPLETED)
        total = len(day_keys)
        result[week] = {
            "completed_days": completed,
            "total_days": total,
            "is_complete": total > 0 and completed == total,
        }
    return result


def get_streak():
    """Consecutive study days (rest days don't break it) with at least one
    completed block, walking backward from today."""
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT date(stopped_at) AS d FROM block_logs"
    ).fetchall()
    active_dates = {r["d"] for r in rows}

    streak = 0
    d = date.today()
    # Allow today to be "in progress" without breaking a streak built through
    # yesterday: only start counting from today if it already has activity;
    # otherwise start the walk from yesterday.
    if d.isoformat() not in active_dates:
        d = d - timedelta(days=1)

    while True:
        if is_rest_day(d):
            d = d - timedelta(days=1)
            continue
        if d.isoformat() in active_dates:
            streak += 1
            d = d - timedelta(days=1)
        else:
            break
    return streak
