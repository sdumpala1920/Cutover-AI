# Cutover to AI — 12-Week Career Transition Command Center

A single-user, local web app that runs a 12-week, ~2-hr/day plan for
transitioning from Oracle Cloud / cutover-and-program-management work into
AI Program Management, AI Strategy, Chief of Staff, or AI Governance roles.

Core rule: open the app, see exactly **one** next action. No menus, no
decision fatigue — a fitness-app-style "Today" screen with a single session
card, a timer, and a progress ring.

## Tech stack (Phase 1)

Kept deliberately boring so it never gets in the way:

- **Backend:** Python + Flask. No build step, no frontend framework —
  server-rendered Jinja2 templates with a little vanilla JS for the live
  timer display.
- **Persistence:** SQLite (`data/app.db`, created automatically on first
  run), accessed directly via `sqlite3` — no ORM. This is *progress state
  only* (timer logs, block/day status, confidence ratings, notes).
- **Content:** plain, hand-editable JSON under `content/curriculum/` (one
  file per week) and `content/certifications.json`. This is deliberately
  kept out of the database so weeks 2-12 can be rewritten anytime as you
  research further, without touching code or losing logged progress.

This is the simplest option that supports daily timers, per-block logging,
and schedule recalculation — a flat-JSON-only backend would work too, but
SQLite makes "sum minutes logged this week" and "recompute streak" trivial
and safe against partial writes.

## Running it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Then open http://127.0.0.1:5000 — it redirects straight to `/today`.

The database is created automatically on first run at `data/app.db`
(git-ignored). Delete it anytime to reset all progress; content in
`content/` is untouched by that.

## How the daily engine works

- **"Today" is not a calendar lookup.** It's defined as *the first
  curriculum day that isn't fully completed yet*. This is what makes the
  catch-up logic automatic rather than a special case: if you skip a day
  or only finish one of its two blocks, that same day keeps being "today"
  until it's done — nothing to reschedule by hand, and every later day
  quietly slides forward with it.
- **Projected completion date** is recalculated on every page load from
  live progress: `remaining curriculum days` projected forward from
  *today's* calendar date, skipping rest days (Sunday, by default). It's
  shown next to the original on-track finish date so you can see drift.
- **Timer:** Start a block → timestamp saved server-side. Stop a block →
  elapsed time is logged, and you capture a 1-5 confidence rating plus a
  one-line note. Each start/stop segment is recorded in `block_logs`, so a
  block's total logged time is always the sum of its segments even if you
  split it across a session.
- **Streak** counts consecutive study days (rest days don't break it) with
  at least one completed block.

## File structure

```
run.py                     entry point (python run.py)
app/
  __init__.py               Flask app factory
  config.py                 paths, rest-day config, curriculum sizing
  db.py                     SQLite connection + schema init
  schema.sql                progress-state tables (day/block progress, logs)
  content_loader.py         reads content/curriculum/*.json
  scheduler.py              the daily engine: resolve "today", timer, catch-up,
                             projection, streak, weekly progress
  routes/
    today.py                GET /today, POST start/stop block
  templates/
    base.html, today.html
  static/
    css/style.css, js/today.js   (live timer tick, stop-form reveal)
content/
  curriculum/week_01.json .. week_12.json   <-- edit these to refine content
  certifications.json                        <-- seeded for Phase 3, not yet wired into UI
data/
  app.db                    created at runtime (git-ignored)
```

## Curriculum content status

- **Week 1 — AI Fundamentals: fully seeded** (`status: "seeded"`), 6 days,
  2 blocks/day (~2 hrs/day): Google AI Essentials (all 4 modules) +
  DeepLearning.AI "AI For Everyone" (Weeks 1-2) + vocabulary log + daily AI
  news habit setup + a first draft seed for Portfolio Project #1.
- **Weeks 2-12: placeholders** (`status: "placeholder"`) — each has a
  `theme`, `role_focus`, and `notes` describing what it should cover, but
  no `days`/`blocks` yet. The Today view will show "Week N is a
  placeholder" once Week 1 is finished, prompting you to seed the next
  week's `days` array in the same shape as `week_01.json`.

To seed a new week: copy the `days` structure from `week_01.json` into the
target week's file and flip `"status"` to `"seeded"`. No code changes
needed — `content_loader.py` picks it up automatically.

## Build phases

1. ✅ **Today view + daily session engine + timer + logging + catch-up
   logic** — this repo, right now.
2. Weekly accountability quiz + readiness score dashboard
3. Certification tracker UI + Portfolio module (content for both is
   already seeded/scaffolded — certifications.json exists, just not wired
   into a route/template yet)
4. Resume & Positioning module
5. Job discovery module — **build last; confirm feasible approach (manual
   refresh vs. scraping vs. an API-backed search) before starting**, per
   the build spec, since it carries the most technical complexity and the
   most external dependency risk.
