import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite persistence — logged time, timer state, quiz scores, etc.
DATABASE_PATH = os.path.join(BASE_DIR, "data", "app.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "app", "schema.sql")

# Editable content — curriculum, certifications. Kept as plain JSON so it's
# trivial to hand-edit or regenerate via research without touching code.
CONTENT_DIR = os.path.join(BASE_DIR, "content")
CURRICULUM_DIR = os.path.join(CONTENT_DIR, "curriculum")
CERTIFICATIONS_PATH = os.path.join(CONTENT_DIR, "certifications.json")

# Study calendar: which weekday indices (Mon=0 ... Sun=6) are rest days.
# Spec targets 5-6 study days/week; default is Sun-off, Mon-Sat study.
REST_WEEKDAYS = {6}

TOTAL_WEEKS = 12
DAYS_PER_WEEK = 6  # non-rest study days modeled per curriculum week
TOTAL_CURRICULUM_DAYS = TOTAL_WEEKS * DAYS_PER_WEEK
