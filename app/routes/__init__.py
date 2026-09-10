from .today import bp as today_bp
from .dashboard import bp as dashboard_bp
from .coach import bp as coach_bp
from .quiz import bp as quiz_bp
from .certifications import bp as certifications_bp
from .portfolio import bp as portfolio_bp
from .resume import bp as resume_bp
from .documents import bp as documents_bp
from .jobs import bp as jobs_bp
from .interview import bp as interview_bp


def register_routes(app):
    app.register_blueprint(today_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(coach_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(certifications_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(interview_bp)
