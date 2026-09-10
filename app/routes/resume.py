from flask import Blueprint, current_app, redirect, render_template, request, url_for

from .. import documents
from .. import scheduler

bp = Blueprint("resume", __name__)


@bp.route("/resume")
def index():
    master_doc_key = "resume:master"
    variants = []
    for role in current_app.config["RESUME_ROLE_TYPES"]:
        doc_key = f"resume:variant:{role}"
        variants.append({
            "role": role,
            "doc_key": doc_key,
            "current": documents.get_current(doc_key),
            "history": documents.get_history(doc_key),
        })

    resolution = scheduler.resolve_today()
    current_week = resolution["day"]["week"] if resolution["kind"] == "day" else None

    return render_template(
        "resume.html",
        master_doc_key=master_doc_key,
        master_current=documents.get_current(master_doc_key),
        master_history=documents.get_history(master_doc_key),
        variants=variants,
        current_week=current_week,
        activation_week=current_app.config["RESUME_ACTIVATION_WEEK"],
    )


@bp.route("/resume/master/save", methods=["POST"])
def save_master():
    content = request.form.get("content", "")
    documents.save_version("resume:master", content)
    return redirect(url_for("resume.index"))


@bp.route("/resume/variant/<role>/save", methods=["POST"])
def save_variant(role):
    if role not in current_app.config["RESUME_ROLE_TYPES"]:
        return redirect(url_for("resume.index"))
    content = request.form.get("content", "")
    notes = request.form.get("translation_notes", "")
    documents.save_version(f"resume:variant:{role}", content, notes)
    return redirect(url_for("resume.index"))
