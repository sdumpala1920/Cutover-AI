from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from .. import content_loader as content
from ..db import get_db

bp = Blueprint("jobs", __name__)


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def _is_priority_company(name):
    companies = {c["company"].lower() for c in content.get_priority_companies()}
    return name.strip().lower() in companies


@bp.route("/jobs")
def index():
    db = get_db()
    postings = db.execute(
        "SELECT * FROM job_postings ORDER BY priority DESC, created_at DESC"
    ).fetchall()
    return render_template(
        "jobs.html",
        postings=postings,
        priority_companies=content.get_priority_companies(),
    )


@bp.route("/jobs/add", methods=["POST"])
def add():
    db = get_db()
    company = (request.form.get("company") or "").strip()
    title = (request.form.get("title") or "").strip()
    if company and title:
        db.execute(
            "INSERT INTO job_postings (company, title, location, url, priority, "
            "status, notes, created_at) VALUES (?, ?, ?, ?, ?, 'new', ?, ?)",
            (
                company, title,
                (request.form.get("location") or "").strip(),
                (request.form.get("url") or "").strip(),
                1 if _is_priority_company(company) else 0,
                (request.form.get("notes") or "").strip(),
                _now_iso(),
            ),
        )
        db.commit()
    return redirect(url_for("jobs.index"))


@bp.route("/jobs/<int:posting_id>/status", methods=["POST"])
def update_status(posting_id):
    status = request.form.get("status", "new")
    db = get_db()
    db.execute("UPDATE job_postings SET status = ? WHERE id = ?", (status, posting_id))
    db.commit()
    return redirect(url_for("jobs.index"))


# ------------------------- Application tracker -------------------------

@bp.route("/applications")
def applications():
    db = get_db()
    apps = db.execute(
        "SELECT a.*, d.doc_key AS resume_doc_key, d.created_at AS resume_saved_at "
        "FROM applications a LEFT JOIN doc_versions d ON a.resume_version_id = d.id "
        "ORDER BY a.date_applied DESC"
    ).fetchall()
    resume_versions = db.execute(
        "SELECT id, doc_key, created_at FROM doc_versions "
        "WHERE doc_key LIKE 'resume:variant:%' ORDER BY doc_key, id DESC"
    ).fetchall()
    postings = db.execute("SELECT id, company, title FROM job_postings ORDER BY created_at DESC").fetchall()
    return render_template(
        "applications.html", apps=apps, resume_versions=resume_versions, postings=postings
    )


@bp.route("/applications/add", methods=["POST"])
def add_application():
    db = get_db()
    company = (request.form.get("company") or "").strip()
    role = (request.form.get("role") or "").strip()
    if company and role:
        job_posting_id = request.form.get("job_posting_id") or None
        resume_version_id = request.form.get("resume_version_id") or None
        now = _now_iso()
        db.execute(
            "INSERT INTO applications (job_posting_id, company, role, date_applied, "
            "status, resume_version_id, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 'applied', ?, ?, ?, ?)",
            (
                job_posting_id, company, role,
                request.form.get("date_applied") or now[:10],
                resume_version_id,
                (request.form.get("notes") or "").strip(),
                now, now,
            ),
        )
        db.commit()
    return redirect(url_for("jobs.applications"))


@bp.route("/applications/<int:app_id>/status", methods=["POST"])
def update_application_status(app_id):
    status = request.form.get("status", "applied")
    db = get_db()
    db.execute(
        "UPDATE applications SET status = ?, updated_at = ? WHERE id = ?",
        (status, _now_iso(), app_id),
    )
    db.commit()
    return redirect(url_for("jobs.applications"))
