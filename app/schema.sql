-- SQLite schema for Cutover to AI.
-- Curriculum *content* lives in content/curriculum/*.json (edit freely).
-- These tables hold only *progress state* keyed off that content's ids.

CREATE TABLE IF NOT EXISTS app_settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- One row per curriculum day (day_key e.g. "w01d03").
CREATE TABLE IF NOT EXISTS day_progress (
    day_key          TEXT PRIMARY KEY,
    week             INTEGER NOT NULL,
    day              INTEGER NOT NULL,
    status           TEXT NOT NULL DEFAULT 'pending', -- pending | in_progress | completed
    first_started_at TEXT,
    completed_at     TEXT
);

-- One row per block within a day (block_key e.g. "w01d03:vocab-log").
CREATE TABLE IF NOT EXISTS block_progress (
    block_key           TEXT PRIMARY KEY,
    day_key             TEXT NOT NULL REFERENCES day_progress(day_key),
    status              TEXT NOT NULL DEFAULT 'pending', -- pending | in_progress | completed
    accumulated_seconds INTEGER NOT NULL DEFAULT 0,
    timer_started_at    TEXT,     -- ISO timestamp while the timer is running, else NULL
    last_confidence     INTEGER,  -- 1-5, captured on stop
    last_note           TEXT,     -- one-line reflection, captured on stop
    completed_at        TEXT
);

-- History of every start/stop segment, so time-per-block and weekly totals
-- are auditable even across multiple start/stop sessions.
CREATE TABLE IF NOT EXISTS block_logs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    block_key        TEXT NOT NULL REFERENCES block_progress(block_key),
    started_at       TEXT NOT NULL,
    stopped_at       TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    confidence       INTEGER,
    note             TEXT
);

CREATE INDEX IF NOT EXISTS idx_block_logs_block_key ON block_logs(block_key);
CREATE INDEX IF NOT EXISTS idx_block_progress_day_key ON block_progress(day_key);

-- ---------------------------------------------------------------------
-- Phase 2: Weekly Accountability Quiz + Readiness Score
-- ---------------------------------------------------------------------

-- A generated quiz for one week, frozen at generation time (so the answer
-- key used to grade it never drifts from what the user was actually shown,
-- even if content/quizzes/*.json is edited later).
CREATE TABLE IF NOT EXISTS quiz_instances (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    week           INTEGER NOT NULL,
    questions_json TEXT NOT NULL, -- [{id, prompt, options, answer_index, topic, source_week}, ...]
    status         TEXT NOT NULL DEFAULT 'pending', -- pending | submitted
    score          INTEGER,
    total          INTEGER,
    answers_json   TEXT,          -- {question_id: chosen_index}
    created_at     TEXT NOT NULL,
    submitted_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_quiz_instances_week ON quiz_instances(week);

-- ---------------------------------------------------------------------
-- Phase 3: Certification Tracker + Portfolio Module
-- ---------------------------------------------------------------------

-- Mutable status/notes for each certification seeded in
-- content/certifications.json (keyed by a slug of its name). The seed file
-- stays research-editable content; this table is just the user's tracked
-- progress against it, same split as curriculum content vs. day_progress.
CREATE TABLE IF NOT EXISTS cert_progress (
    cert_key   TEXT PRIMARY KEY,
    status     TEXT NOT NULL DEFAULT 'not_started', -- not_started | in_progress | done
    notes      TEXT,
    updated_at TEXT NOT NULL
);

-- Generic versioned-document store, reused by the Portfolio module (the
-- rollout plan + story bank) and the Resume module (master resume + one
-- variant per target role). doc_key examples: "portfolio:rollout_plan",
-- "resume:master", "resume:variant:PMO". Every save inserts a new row —
-- the "current" version of a doc_key is simply its highest id.
CREATE TABLE IF NOT EXISTS doc_versions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_key    TEXT NOT NULL,
    content    TEXT NOT NULL,
    notes      TEXT,             -- e.g. translation-layer notes for a resume variant
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_doc_versions_doc_key ON doc_versions(doc_key, id);

-- ---------------------------------------------------------------------
-- Phase 4/5 support: mock interview log (feeds readiness score) and the
-- Job Discovery module (manual-refresh postings + application tracker).
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS mock_interviews (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    practiced_on TEXT NOT NULL, -- date
    topic        TEXT,
    score        INTEGER,       -- 0-100, self-rated
    notes        TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_postings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    company    TEXT NOT NULL,
    title      TEXT NOT NULL,
    location   TEXT,
    url        TEXT,
    priority   INTEGER NOT NULL DEFAULT 0, -- 1 if company matches priority_companies.json
    status     TEXT NOT NULL DEFAULT 'new', -- new | interested | applied | rejected | archived
    notes      TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    job_posting_id    INTEGER REFERENCES job_postings(id),
    company           TEXT NOT NULL,
    role              TEXT NOT NULL,
    date_applied      TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'applied', -- applied|phone_screen|interview|offer|rejected|withdrawn
    resume_version_id INTEGER REFERENCES doc_versions(id),
    notes             TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_job_postings_status ON job_postings(status);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);

-- ---------------------------------------------------------------------
-- Conversational Coach (chat-based, turn-based dialogue with the hidden
-- "Elena Marsh" persona — see app/coach.py). One row per session; the
-- session's `recap` holds the single next step it closed on.
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS coaching_sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    mode       TEXT NOT NULL DEFAULT 'coaching', -- coaching | practice
    topic      TEXT,
    status     TEXT NOT NULL DEFAULT 'active',   -- active | ended
    recap      TEXT,        -- the one next step, captured when the session ends
    started_at TEXT NOT NULL,
    ended_at   TEXT
);

CREATE TABLE IF NOT EXISTS coaching_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES coaching_sessions(id),
    role       TEXT NOT NULL, -- user | coach
    content    TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_coaching_messages_session ON coaching_messages(session_id, id);
