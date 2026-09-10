from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for

from .. import coach

bp = Blueprint("coach", __name__)


@bp.route("/coach")
def landing():
    configured = coach.is_configured()
    sessions = coach.list_recent_sessions(15) if configured else []
    return render_template("coach.html", configured=configured, sessions=sessions)


@bp.route("/coach/start", methods=["POST"])
def start():
    if not coach.is_configured():
        return redirect(url_for("coach.landing"))
    mode = request.form.get("mode", "coaching")
    if mode not in ("coaching", "practice"):
        mode = "coaching"
    topic = (request.form.get("topic") or "").strip() or None
    session_id = coach.start_session(mode, topic)
    return redirect(url_for("coach.session_view", session_id=session_id))


@bp.route("/coach/<int:session_id>")
def session_view(session_id):
    session = coach.get_session(session_id)
    if session is None:
        return redirect(url_for("coach.landing"))
    messages = coach.get_messages(session_id)
    return render_template(
        "coach_session.html",
        session=session,
        messages=messages,
        bitesize_minutes=current_app.config["COACH_BITESIZE_MINUTES"],
    )


@bp.route("/api/coach/<int:session_id>/message", methods=["POST"])
def send_message(session_id):
    session = coach.get_session(session_id)
    if session is None or session["status"] != "active":
        return jsonify({"error": "Session not found or already ended."}), 400

    data = request.get_json(silent=True) or {}
    text = (data.get("message") or "").strip()
    if not text:
        return jsonify({"error": "Message can't be empty."}), 400

    try:
        reply = coach.send_message(session_id, text)
    except Exception as e:  # noqa: BLE001 — surface a friendly error to the chat UI
        return jsonify({"error": f"The coach couldn't respond ({e}). Check your Anthropic API key in .env and try again."}), 502

    return jsonify({"reply": reply})


@bp.route("/coach/<int:session_id>/end", methods=["POST"])
def end(session_id):
    coach.end_session(session_id)
    return redirect(url_for("coach.session_view", session_id=session_id))
