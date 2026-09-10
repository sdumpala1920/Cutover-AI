from .today import bp as today_bp


def register_routes(app):
    app.register_blueprint(today_bp)
