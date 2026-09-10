from flask import Flask

from . import config as config_module
from .db import init_db, register_teardown
from .routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(config_module)

    register_teardown(app)
    init_db(app)
    register_routes(app)

    @app.template_filter("fmt_date")
    def fmt_date(d):
        """Format a date without relying on platform-specific strftime flags."""
        return f"{d.strftime('%b')} {d.day}, {d.year}"

    return app
