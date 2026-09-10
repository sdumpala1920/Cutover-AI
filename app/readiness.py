"""Readiness Score Dashboard: a composite 0-100 score plus a per-category
breakdown, recalculated live from whatever progress data already exists
(no separate snapshot table needed — every input is already timestamped).
"""
from flask import current_app

from . import certifications
from . import content_loader as content
from . import documents
from . import quiz
from . import scheduler
from .db import get_db


def _hours_logged_percent():
    db = get_db()
    row = db.execute(
        "SELECT COALESCE(SUM(accumulated_seconds), 0) AS secs FROM block_progress"
    ).fetchone()
    hours = (row["secs"] or 0) / 3600
    target = current_app.config["TOTAL_TARGET_HOURS"]
    return min(100, round(100 * hours / target)) if target else 0, round(hours, 1)


def _portfolio_percent():
    pieces = current_app.config["PORTFOLIO_PIECES"]
    if not pieces:
        return 0, 0, 0
    done = sum(1 for key in pieces if documents.count_versions(f"portfolio:{key}") > 0)
    return round(100 * done / len(pieces)), done, len(pieces)


def _certification_percent():
    certs = certifications.get_all()
    if not certs:
        return 0
    done = sum(1 for c in certs if c["status"] == "done")
    return round(100 * done / len(certs))


def _mock_interview_percent():
    db = get_db()
    row = db.execute(
        "SELECT AVG(score) AS avg_score, COUNT(*) AS n FROM mock_interviews"
    ).fetchone()
    if not row["n"]:
        return 0, 0
    return round(row["avg_score"]), row["n"]


def composite_score():
    """Equal-weighted average of the six signals the spec calls out:
    modules completed, hours logged vs. target, quiz performance,
    portfolio pieces completed, certification status, mock interview
    scores. Each is 0 until that activity has actually started."""
    projection = scheduler.get_projection()
    modules_pct = (
        round(100 * projection["completed_slots"] / projection["total_slots"])
        if projection["total_slots"] else 0
    )
    hours_pct, hours_logged = _hours_logged_percent()
    quiz_pct = quiz.average_score_percent() or 0
    portfolio_pct, portfolio_done, portfolio_total = _portfolio_percent()
    cert_pct = _certification_percent()
    interview_pct, interview_count = _mock_interview_percent()

    components = [modules_pct, hours_pct, quiz_pct, portfolio_pct, cert_pct, interview_pct]
    score = round(sum(components) / len(components))

    return {
        "score": score,
        "modules_pct": modules_pct,
        "hours_pct": hours_pct,
        "hours_logged": hours_logged,
        "quiz_pct": quiz_pct,
        "portfolio_pct": portfolio_pct,
        "portfolio_done": portfolio_done,
        "portfolio_total": portfolio_total,
        "cert_pct": cert_pct,
        "interview_pct": interview_pct,
        "interview_count": interview_count,
    }


def category_scores():
    """Per-category breakdown for the dashboard's bar chart. Each category
    is 60% curriculum completion (for its assigned weeks) + 40% split
    across whatever secondary signals apply (quiz average for its weeks,
    portfolio completion, mock-interview coverage) — secondary signals are
    only folded in once the category's weeks have actually started, so an
    untouched future category doesn't get unfairly dragged down."""
    weeks_status = scheduler.get_all_weeks_status()
    categories = current_app.config["READINESS_CATEGORIES"]
    results = []

    for name, cfg in categories.items():
        weeks = cfg["weeks"]
        completed_days = sum(weeks_status.get(w, {}).get("completed_days", 0) for w in weeks)
        total_days = sum(weeks_status.get(w, {}).get("total_days", 0) for w in weeks)
        curriculum_pct = round(100 * completed_days / total_days) if total_days else 0

        if curriculum_pct == 0:
            results.append({"name": name, "percent": 0})
            continue

        secondary = []
        quiz_avg = quiz.average_score_percent(weeks=weeks)
        if quiz_avg is not None:
            secondary.append(quiz_avg)
        if cfg.get("uses_portfolio"):
            pct, _, _ = _portfolio_percent()
            secondary.append(pct)
        if cfg.get("uses_mock_interviews"):
            pct, _ = _mock_interview_percent()
            secondary.append(pct)

        if secondary:
            secondary_avg = sum(secondary) / len(secondary)
            percent = round(0.6 * curriculum_pct + 0.4 * secondary_avg)
        else:
            percent = curriculum_pct

        results.append({"name": name, "percent": percent})

    return results


def weekly_summary():
    resolution = scheduler.resolve_today()
    if resolution["kind"] == "day":
        current_week = resolution["day"]["week"]
        whats_next = resolution["day"]["title"]
    else:
        current_week = None
        whats_next = "Seed the next week's curriculum to keep going."

    week_progress = scheduler.get_week_progress(current_week) if current_week else None
    return {
        "current_week": current_week,
        "hours_logged_this_week": round((week_progress["logged_minutes"] / 60), 1) if week_progress else 0,
        "streak": scheduler.get_streak(),
        "quiz_average": quiz.average_score_percent(),
        "whats_next": whats_next,
    }
