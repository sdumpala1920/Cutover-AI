# Cutover to AI — 12-Week Career Transition Command Center

A single-user, local web app that runs a 12-week, ~2-hr/day plan for
transitioning from Oracle Cloud / cutover-and-program-management work into
AI Program Management, AI Strategy, Chief of Staff, or AI Governance roles.

Core rule: open the app, see exactly **one** next action. No menus, no
decision fatigue — a fitness-app-style "Today" screen with a single session
card, a timer, and a progress ring. Everything else (dashboard, quiz,
certifications, portfolio, resume, jobs, coach) lives one click away in the
top nav, never competing with Today for attention.

Full requirements live in [`docs/SPEC.md`](docs/SPEC.md).

## Quick start (no terminal needed after the first time)

1. **Mac:** double-click **`start_mac.command`**.
   **Windows:** double-click **`start_windows.bat`**.
2. First run takes a minute (installs dependencies); every run after that
   is instant. Your browser opens to the app automatically.
3. Keep that terminal/console window open while you use the app — closing
   it stops the server. Come back anytime by double-clicking the same file
   again.

(If double-clicking doesn't work — e.g. macOS blocks unsigned scripts by
default the first time — see **Manual setup** below, or right-click →
Open once to approve it.)

### Using it on your phone too

With the app running on your computer:
1. Find your computer's local network IP (Mac: System Settings → Wi-Fi →
   Details; Windows: `ipconfig` → "IPv4 Address"), e.g. `192.168.1.42`.
2. On your phone (same Wi-Fi network), visit `http://192.168.1.42:5000`.
3. In your phone browser's menu, choose **Add to Home Screen** — the app
   has an icon and name set up for this, so you get a home-screen icon
   that opens straight to Today.

This only works while your computer and the app are on and the app is
running — it's not hosted anywhere online.

## Manual setup

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # optional — only needed for the Coach feature, see below
python run.py
```

Then open http://127.0.0.1:5000 — it redirects straight to `/today`.

The database is created automatically on first run at `data/app.db`
(git-ignored). Delete it anytime to reset all progress; content in
`content/` is untouched by that.

## The Conversational Coach — one extra setup step

Every module works out of the box **except** the Coach, which has a chat
conversation with you and needs your own Anthropic API key (billed
pay-as-you-go — a separate account/setup from a claude.ai subscription):

1. Get a key at **console.anthropic.com** (Settings → API Keys).
2. Copy `.env.example` to `.env` in the project folder and paste your key
   in: `ANTHROPIC_API_KEY=sk-ant-...`
3. Restart the app. The Coach page will show a setup message until this is
   done; every other page ignores it entirely.

`.env` is git-ignored — your key is never committed or uploaded anywhere.

## Tech stack

Kept deliberately boring so it never gets in the way:

- **Backend:** Python + Flask. No build step, no frontend framework —
  server-rendered Jinja2 templates with a little vanilla JS (the live
  timer, and the Coach's chat window, which uses `fetch` so sending a
  message doesn't reload the page).
- **Persistence:** SQLite (`data/app.db`, created automatically on first
  run), accessed directly via `sqlite3` — no ORM. This holds all *progress
  state*: timer logs, quiz attempts, certification status, versioned
  portfolio/resume documents, job/application tracking, and coaching
  session transcripts.
- **Content:** plain, hand-editable JSON under `content/` (curriculum,
  quizzes, certifications, priority companies). Kept out of the database
  so it can be rewritten anytime as you research further, without
  touching code or losing logged progress.
- **AI:** the Anthropic API (`anthropic` Python SDK), used only by the
  Coach module, via `claude-opus-5` by default (configurable in `.env`).

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

## The Conversational Coach

A chat-based coach for reflection and skill practice, voiced through an
internal persona ("Elena Marsh" — never named or described to you in the
app itself, only felt through tone and style):

- **Coaching mode** — a reflective, Socratic dialogue about a goal or
  challenge you name (or let the coach ask).
- **Practice mode** — a short role-play (a talk, a pitch, a hard
  conversation): you perform your part in the chat, the coach gives
  in-the-moment feedback.
- Feedback is structured around three pillars: **Anchor** (your one main
  point), **Presence** (delivery — pacing, authenticity), **Story**
  (narrative clarity and specificity).
- Sessions are bite-sized by default (~5-10 min, with a gentle nudge, never
  a hard cutoff) and always end in exactly one concrete next step, which is
  saved and shown on your session history.
- The coach folds in a short recap of your last few sessions and your
  current place in the 12-week program, so it can reference past work
  naturally instead of starting cold every time.

## File structure

```
run.py                     entry point (python run.py)
start_mac.command          double-click launcher (macOS)
start_windows.bat          double-click launcher (Windows)
.env.example                copy to .env for your Anthropic API key (Coach only)
docs/SPEC.md                 full feature spec (living document)
app/
  __init__.py               Flask app factory, nav, date-formatting filter
  config.py                 paths, rest-day config, curriculum sizing, Coach settings
  db.py                     SQLite connection + schema init
  schema.sql                all progress-state tables
  content_loader.py         reads content/*.json (curriculum, quizzes, certs, companies)
  scheduler.py              daily engine: resolve "today", timer, catch-up, projection, streak
  quiz.py                   Sunday Check quiz generation, grading, spaced repetition, weak topics
  certifications.py         merges certifications.json with tracked status
  documents.py              generic versioned-document store (Portfolio + Resume)
  readiness.py              composite readiness score + category breakdown + weekly summary
  coach.py                  Conversational Coach: persona, Claude API calls, session state
  routes/
    today.py, dashboard.py, quiz.py, certifications.py, portfolio.py,
    resume.py, documents.py, jobs.py, interview.py, coach.py
  templates/                one .html per page, extending base.html (has the nav)
  static/
    css/style.css, js/today.js, js/coach.js
    manifest.json, icons/     phone "Add to Home Screen" support
content/
  curriculum/week_01.json .. week_12.json   <-- edit these to refine content
  quizzes/week_01.json .. week_12.json       <-- edit these to add quiz questions
  certifications.json
  priority_companies.json
data/
  app.db                    created at runtime (git-ignored)
```

## Curriculum & quiz content status

- **Week 1 — AI Fundamentals: fully seeded** (`status: "seeded"`), 6 days,
  2 blocks/day (~2 hrs/day): Google AI Essentials (all 4 modules) +
  DeepLearning.AI "AI For Everyone" (Weeks 1-2) + vocabulary log + daily AI
  news habit setup + a first draft seed for Portfolio Project #1. Its
  8-question quiz is seeded too.
- **Weeks 2-12: placeholders** (`status: "placeholder"`) — each has a
  `theme`, `role_focus`, and `notes` describing what it should cover, but
  no `days`/`blocks`/quiz questions yet. The Today view will show "Week N
  is a placeholder" once Week 1 is finished, prompting you to seed the
  next week's `days` array in the same shape as `week_01.json` (and its
  quiz in the same shape as `quizzes/week_01.json`).

To seed a new week: copy the `days` structure from `week_01.json` into the
target week's file and flip `"status"` to `"seeded"` (same pattern for its
quiz file). No code changes needed — `content_loader.py` picks it up
automatically.

## Build phases — all complete

1. ✅ Today view + daily session engine + timer + logging + catch-up logic
2. ✅ Weekly accountability quiz + readiness score dashboard
3. ✅ Certification tracker + Portfolio module
4. ✅ Resume & Positioning module
5. ✅ Job Discovery module — built as the manual-refresh workflow the spec
   suggested (priority-company shortcut links + a manual add/track flow),
   not automated scraping
- ✅ Conversational Coach — chat-based coaching + practice mode, added on
  top of the original 5 phases
