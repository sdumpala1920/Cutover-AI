"""Weekly Accountability Quiz ("Sunday Check") engine.

A quiz becomes available for a week once every seeded day in that week is
completed. Taking it generates a frozen "instance" (that week's questions
plus 1-2 randomly sampled prior-week questions for spaced repetition),
shuffled once and stored — so a page refresh never reshuffles or regrades
against edited content.
"""
import json
import random
from datetime import datetime

from flask import current_app

from . import content_loader as content
from . import scheduler
from .db import get_db


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def available_quiz_weeks():
    """Weeks that are fully completed AND have seeded quiz content."""
    weeks_status = scheduler.get_all_weeks_status()
    quiz_weeks = [
        w["week"] for w in content.get_all_quiz_weeks() if w.get("status") == "seeded"
    ]
    return sorted(w for w in quiz_weeks if weeks_status.get(w, {}).get("is_complete"))


def latest_instance_for_week(week):
    db = get_db()
    return db.execute(
        "SELECT * FROM quiz_instances WHERE week = ? ORDER BY id DESC LIMIT 1",
        (week,),
    ).fetchone()


def get_instance(instance_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM quiz_instances WHERE id = ?", (instance_id,)
    ).fetchone()


def generate_instance(week):
    """Force-generate a fresh quiz instance for a week (new attempt/retake)."""
    quiz_content = content.get_quiz_for_week(week)
    if not quiz_content or quiz_content.get("status") != "seeded":
        return None

    questions = [dict(q) for q in quiz_content.get("questions", [])]
    review_pool = []
    for prior in content.get_seeded_quiz_weeks_before(week):
        review_pool.extend(dict(q) for q in prior.get("questions", []))

    review_count = min(current_app.config["QUIZ_REVIEW_QUESTION_COUNT"], len(review_pool))
    review_questions = random.sample(review_pool, review_count) if review_count else []
    for q in review_questions:
        q["is_review"] = True

    all_questions = questions + review_questions
    random.shuffle(all_questions)

    db = get_db()
    db.execute(
        "INSERT INTO quiz_instances (week, questions_json, status, created_at) "
        "VALUES (?, ?, 'pending', ?)",
        (week, json.dumps(all_questions), _now_iso()),
    )
    db.commit()
    return latest_instance_for_week(week)


def get_or_create_pending(week):
    """Reuse an in-progress instance for this week, else start a new one."""
    row = latest_instance_for_week(week)
    if row and row["status"] == "pending":
        return row
    return generate_instance(week)


def next_quiz_week():
    """Earliest eligible week that has no *submitted* attempt yet."""
    for week in available_quiz_weeks():
        row = latest_instance_for_week(week)
        if row is None or row["status"] != "submitted":
            return week
    return None


def submit(instance_id, answers_by_question_id):
    row = get_instance(instance_id)
    if row is None or row["status"] == "submitted":
        return None

    questions = json.loads(row["questions_json"])
    score = 0
    for q in questions:
        chosen = answers_by_question_id.get(q["id"])
        if chosen is not None and int(chosen) == q["answer_index"]:
            score += 1

    db = get_db()
    db.execute(
        "UPDATE quiz_instances SET status = 'submitted', score = ?, total = ?, "
        "answers_json = ?, submitted_at = ? WHERE id = ?",
        (score, len(questions), json.dumps(answers_by_question_id), _now_iso(), instance_id),
    )
    db.commit()
    return get_instance(instance_id)


def submitted_history(limit=20):
    db = get_db()
    return db.execute(
        "SELECT * FROM quiz_instances WHERE status = 'submitted' "
        "ORDER BY submitted_at DESC LIMIT ?",
        (limit,),
    ).fetchall()


def average_score_percent(weeks=None):
    """Average % across submitted quizzes, optionally restricted to a set
    of weeks. Returns None if nothing submitted yet (vs. 0, which would
    misleadingly look like a failing average)."""
    db = get_db()
    if weeks:
        placeholders = ",".join("?" for _ in weeks)
        rows = db.execute(
            f"SELECT score, total FROM quiz_instances "
            f"WHERE status = 'submitted' AND week IN ({placeholders})",
            list(weeks),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT score, total FROM quiz_instances WHERE status = 'submitted'"
        ).fetchall()
    if not rows:
        return None
    pct_sum = sum((r["score"] / r["total"]) * 100 for r in rows if r["total"])
    return round(pct_sum / len(rows))


def weak_topics(threshold_percent=70, limit=5):
    """Topics with below-threshold accuracy across all submitted quizzes,
    worst first. Used to flag review areas per the spec."""
    db = get_db()
    rows = db.execute(
        "SELECT questions_json, answers_json FROM quiz_instances WHERE status = 'submitted'"
    ).fetchall()

    tally = {}  # topic -> [correct, total]
    for row in rows:
        questions = json.loads(row["questions_json"])
        answers = json.loads(row["answers_json"] or "{}")
        for q in questions:
            topic = q.get("topic") or "General"
            correct, total = tally.get(topic, [0, 0])
            total += 1
            chosen = answers.get(q["id"])
            if chosen is not None and int(chosen) == q["answer_index"]:
                correct += 1
            tally[topic] = [correct, total]

    weak = []
    for topic, (correct, total) in tally.items():
        pct = round(100 * correct / total) if total else 0
        if pct < threshold_percent:
            weak.append({"topic": topic, "percent": pct, "correct": correct, "total": total})
    weak.sort(key=lambda t: t["percent"])
    return weak[:limit]
