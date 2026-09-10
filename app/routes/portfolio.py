from flask import Blueprint, current_app, redirect, render_template, request, url_for

from .. import documents

bp = Blueprint("portfolio", __name__)


@bp.route("/portfolio")
def index():
    pieces = []
    for key, label in current_app.config["PORTFOLIO_PIECES"].items():
        doc_key = f"portfolio:{key}"
        pieces.append({
            "key": key,
            "doc_key": doc_key,
            "label": label,
            "current": documents.get_current(doc_key),
            "history": documents.get_history(doc_key),
        })
    return render_template("portfolio.html", pieces=pieces)


@bp.route("/portfolio/<piece_key>/save", methods=["POST"])
def save(piece_key):
    if piece_key not in current_app.config["PORTFOLIO_PIECES"]:
        return redirect(url_for("portfolio.index"))
    content = request.form.get("content", "")
    documents.save_version(f"portfolio:{piece_key}", content)
    return redirect(url_for("portfolio.index"))
