"""Loads curriculum content from content/curriculum/*.json.

Content is intentionally plain, hand-editable JSON (per the build spec) so
weeks 2-12 can be refined over time without touching application code.
Nothing here is cached across requests in debug mode, so edits show up on
the next page load.
"""
import json
import os

from flask import current_app


def _load_week_file(path):
    with open(path, "r") as f:
        return json.load(f)


def get_all_weeks():
    """Return every week's raw JSON dict, sorted by week number."""
    curriculum_dir = current_app.config["CURRICULUM_DIR"]
    weeks = []
    for name in sorted(os.listdir(curriculum_dir)):
        if name.endswith(".json"):
            weeks.append(_load_week_file(os.path.join(curriculum_dir, name)))
    weeks.sort(key=lambda w: w["week"])
    return weeks


def get_week(week_number):
    for week in get_all_weeks():
        if week["week"] == week_number:
            return week
    return None


def day_key(week_number, day_number):
    return f"w{week_number:02d}d{day_number:02d}"


def block_key(dkey, block_id):
    return f"{dkey}:{block_id}"


def iter_days():
    """Yield every *seeded* day (week['status'] == 'seeded') in curriculum
    order, each augmented with day_key/block_key identifiers plus a back
    reference to its parent week's theme and role focus.
    """
    for week in get_all_weeks():
        if week.get("status") != "seeded":
            continue
        for day in week.get("days", []):
            dkey = day_key(week["week"], day["day"])
            blocks = []
            for b in day.get("blocks", []):
                blocks.append({**b, "block_key": block_key(dkey, b["id"])})
            yield {
                "day_key": dkey,
                "week": week["week"],
                "day": day["day"],
                "week_theme": week.get("theme"),
                "title": day.get("title"),
                "role_tags": day.get("role_tags", []),
                "blocks": blocks,
            }


def get_day(dkey):
    for day in iter_days():
        if day["day_key"] == dkey:
            return day
    return None


def find_block(bkey):
    dkey = bkey.split(":", 1)[0]
    day = get_day(dkey)
    if not day:
        return None, None
    for b in day["blocks"]:
        if b["block_key"] == bkey:
            return day, b
    return day, None


def next_unseeded_week():
    """First week whose content hasn't been written yet (status != seeded)."""
    for week in get_all_weeks():
        if week.get("status") != "seeded":
            return week
    return None


def get_certifications():
    path = current_app.config["CERTIFICATIONS_PATH"]
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def get_priority_companies():
    path = current_app.config["PRIORITY_COMPANIES_PATH"]
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------
# Weekly Accountability Quiz content — content/quizzes/week_NN.json
# ---------------------------------------------------------------------

def get_all_quiz_weeks():
    """Every quiz file, sorted by week, regardless of seeded/placeholder."""
    quizzes_dir = current_app.config["QUIZZES_DIR"]
    if not os.path.isdir(quizzes_dir):
        return []
    weeks = []
    for name in sorted(os.listdir(quizzes_dir)):
        if name.endswith(".json"):
            with open(os.path.join(quizzes_dir, name), "r") as f:
                weeks.append(json.load(f))
    weeks.sort(key=lambda w: w["week"])
    return weeks


def get_quiz_for_week(week_number):
    for w in get_all_quiz_weeks():
        if w["week"] == week_number:
            return w
    return None


def get_seeded_quiz_weeks_before(week_number):
    """Seeded quiz weeks strictly before week_number, used as the pool for
    spaced-repetition review questions."""
    return [
        w for w in get_all_quiz_weeks()
        if w.get("status") == "seeded" and w["week"] < week_number
    ]
