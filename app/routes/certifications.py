from flask import Blueprint, redirect, render_template, request, url_for

from .. import certifications

bp = Blueprint("certifications", __name__)


@bp.route("/certifications")
def index():
    return render_template("certifications.html", certs=certifications.get_all())


@bp.route("/certifications/<cert_key>/update", methods=["POST"])
def update(cert_key):
    status = request.form.get("status", "not_started")
    notes = (request.form.get("notes") or "").strip()
    certifications.update(cert_key, status, notes)
    return redirect(url_for("certifications.index"))
