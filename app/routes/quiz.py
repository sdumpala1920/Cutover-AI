from flask import Blueprint, redirect, render_template, request, url_for

from .. import quiz as quiz_engine

bp = Blueprint("quiz", __name__)


def _sanitized_questions(instance):
    """Strip answer_index out of what gets rendered in the form."""
    import json

    questions = json.loads(instance["questions_json"])
    return [{k: v for k, v in q.items() if k != "answer_index"} for q in questions]


@bp.route("/quiz")
def index():
    next_week = quiz_engine.next_quiz_week()
    instance = quiz_engine.get_or_create_pending(next_week) if next_week else None
    questions = _sanitized_questions(instance) if instance else []

    return render_template(
        "quiz.html",
        next_week=next_week,
        instance=instance,
        questions=questions,
        history=quiz_engine.submitted_history(),
        weak_topics=quiz_engine.weak_topics(),
    )


@bp.route("/quiz/<int:instance_id>/submit", methods=["POST"])
def submit(instance_id):
    instance = quiz_engine.get_instance(instance_id)
    if instance is None:
        return redirect(url_for("quiz.index"))

    import json
    questions = json.loads(instance["questions_json"])
    answers = {}
    for q in questions:
        val = request.form.get(f"q_{q['id']}")
        if val is not None:
            answers[q["id"]] = int(val)

    quiz_engine.submit(instance_id, answers)
    return redirect(url_for("quiz.index"))


@bp.route("/quiz/<int:week>/retake", methods=["POST"])
def retake(week):
    quiz_engine.generate_instance(week)
    return redirect(url_for("quiz.index"))
