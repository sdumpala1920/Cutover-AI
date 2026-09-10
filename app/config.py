import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite persistence — logged time, timer state, quiz scores, etc.
DATABASE_PATH = os.path.join(BASE_DIR, "data", "app.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "app", "schema.sql")

# Editable content — curriculum, certifications. Kept as plain JSON so it's
# trivial to hand-edit or regenerate via research without touching code.
CONTENT_DIR = os.path.join(BASE_DIR, "content")
CURRICULUM_DIR = os.path.join(CONTENT_DIR, "curriculum")
QUIZZES_DIR = os.path.join(CONTENT_DIR, "quizzes")
CERTIFICATIONS_PATH = os.path.join(CONTENT_DIR, "certifications.json")
PRIORITY_COMPANIES_PATH = os.path.join(CONTENT_DIR, "priority_companies.json")

# Study calendar: which weekday indices (Mon=0 ... Sun=6) are rest days.
# Spec targets 5-6 study days/week; default is Sun-off, Mon-Sat study.
REST_WEEKDAYS = {6}

TOTAL_WEEKS = 12
DAYS_PER_WEEK = 6  # non-rest study days modeled per curriculum week
TOTAL_CURRICULUM_DAYS = TOTAL_WEEKS * DAYS_PER_WEEK
TARGET_HOURS_PER_DAY = 2
TOTAL_TARGET_HOURS = TOTAL_CURRICULUM_DAYS * TARGET_HOURS_PER_DAY  # 144

# Sunday Check quiz: how many prior-week questions to mix in for spaced
# repetition, on top of that week's own questions.
QUIZ_REVIEW_QUESTION_COUNT = 2

# Portfolio Module pieces (doc_key suffixes under "portfolio:").
PORTFOLIO_PIECES = {
    "rollout_plan": "AI Rollout Plan",
    "story_bank": "Cutover-to-TPM Story Bank",
}

# Resume & Positioning Module: one tailored variant per target role
# (doc_key "resume:variant:<RoleType>"), plus a single master resume
# (doc_key "resume:master"). Spec suggests activating this ~week 9+; the
# module itself stays reachable the whole time, just with a soft nudge.
RESUME_ROLE_TYPES = ["Strategy", "PMO", "CoS", "Governance"]
RESUME_ACTIVATION_WEEK = 9

MOCK_INTERVIEW_TARGET_COUNT = 4  # used as the readiness-score denominator

# Readiness Score Dashboard categories -> which curriculum weeks feed each,
# so the dashboard doesn't need its own separate content mapping. See
# app/readiness.py for how these combine with quiz/portfolio/interview
# signals into a 0-100 score per category.
READINESS_CATEGORIES = {
    "AI Fundamentals": {"weeks": [1, 2]},
    "Enterprise AI Strategy": {"weeks": [3, 4]},
    "AI Program Mgmt & Governance": {"weeks": [7, 8]},
    "Communication & Portfolio": {"weeks": [5, 6, 9, 10], "uses_portfolio": True},
    "Interview Readiness": {"weeks": [11, 12], "uses_mock_interviews": True},
}
