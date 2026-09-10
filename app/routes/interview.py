from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from ..db import get_db

bp = Blueprint("interview", __name__)


@bp.route("/interview")
def index():
    db = get_db()
    entries = db.execute(
        "SELECT * FROM mock_interviews ORDER BY practiced_on DESC, id DESC"
    ).fetchall()
    return render_template("interview.html", entries=entries)


@bp.route("/interview/add", methods=["POST"])
def add():
    db = get_db()
    score = request.form.get("score", type=int)
    db.execute(
        "INSERT INTO mock_interviews (practiced_on, topic, score, notes, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            request.form.get("practiced_on") or datetime.now().date().isoformat(),
            (request.form.get("topic") or "").strip(),
            score,
            (request.form.get("notes") or "").strip(),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    db.commit()
    return redirect(url_for("interview.index"))
