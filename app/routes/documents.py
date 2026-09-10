from flask import Blueprint, Response, redirect, render_template, request

from .. import documents

bp = Blueprint("documents", __name__)


def _friendly_label(doc_key):
    labels = {
        "portfolio:rollout_plan": "AI Rollout Plan",
        "portfolio:story_bank": "Cutover-to-TPM Story Bank",
        "resume:master": "Master Resume",
    }
    if doc_key in labels:
        return labels[doc_key]
    if doc_key.startswith("resume:variant:"):
        return f"Resume — {doc_key.rsplit(':', 1)[-1]} variant"
    return doc_key


@bp.route("/documents/<path:doc_key>/export")
def export(doc_key):
    current = documents.get_current(doc_key)
    content = current["content"] if current else ""
    filename = doc_key.replace(":", "_") + ".md"
    return Response(
        content,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@bp.route("/documents/<path:doc_key>/print")
def print_view(doc_key):
    current = documents.get_current(doc_key)
    return render_template(
        "document_print.html",
        label=_friendly_label(doc_key),
        content=current["content"] if current else "(nothing saved yet)",
        notes=current["notes"] if current else None,
    )


@bp.route("/documents/<path:doc_key>/version/<int:version_id>")
def view_version(doc_key, version_id):
    version = documents.get_version(version_id)
    return render_template(
        "document_version.html",
        doc_key=doc_key,
        label=_friendly_label(doc_key),
        version=version,
    )


@bp.route("/documents/<path:doc_key>/version/<int:version_id>/restore", methods=["POST"])
def restore_version(doc_key, version_id):
    version = documents.get_version(version_id)
    if version:
        documents.save_version(doc_key, version["content"], version["notes"])
    return redirect(request.referrer or "/")
