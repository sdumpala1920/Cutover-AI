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
