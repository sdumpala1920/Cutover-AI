import sqlite3
from datetime import date

from flask import current_app, g


def get_db():
    """Return the request-scoped SQLite connection, opening it if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create tables if missing and seed one-time settings. Safe to call every boot."""
    with app.app_context():
        db = get_db()
        with open(app.config["SCHEMA_PATH"], "r") as f:
            db.executescript(f.read())

        row = db.execute(
            "SELECT value FROM app_settings WHERE key = 'start_date'"
        ).fetchone()
        if row is None:
            db.execute(
                "INSERT INTO app_settings (key, value) VALUES ('start_date', ?)",
                (date.today().isoformat(),),
            )
        db.commit()
        close_db()


def register_teardown(app):
    app.teardown_appcontext(close_db)
