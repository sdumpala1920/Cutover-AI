from flask import Blueprint, render_template

from .. import readiness

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
def index():
    return render_template(
        "dashboard.html",
        composite=readiness.composite_score(),
        categories=readiness.category_scores(),
        summary=readiness.weekly_summary(),
    )
