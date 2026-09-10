from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

from .. import scheduler

bp = Blueprint("today", __name__)


@bp.route("/")
def index():
    return redirect(url_for("today.today_view"))


@bp.route("/today")
def today_view():
    resolution = scheduler.resolve_today()
    projection = scheduler.get_projection()
    streak = scheduler.get_streak()

    week_progress = None
    if resolution["kind"] == "day":
        week_progress = scheduler.get_week_progress(resolution["day"]["week"])

    today = date.today()
    return render_template(
        "today.html",
        resolution=resolution,
        projection=projection,
        streak=streak,
        week_progress=week_progress,
        today_label=today.strftime("%A, %B ") + str(today.day),
    )


@bp.route("/api/blocks/<path:block_key>/start", methods=["POST"])
def start_block(block_key):
    scheduler.start_block(block_key)
    return redirect(url_for("today.today_view"))


@bp.route("/api/blocks/<path:block_key>/stop", methods=["POST"])
def stop_block(block_key):
    confidence = request.form.get("confidence", type=int)
    note = (request.form.get("note") or "").strip()
    scheduler.stop_block(block_key, confidence, note)
    return redirect(url_for("today.today_view"))
