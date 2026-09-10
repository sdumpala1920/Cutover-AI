# CLAUDE CODE BUILD SPEC: "Cutover to AI" — 12-Week Career Transition Command Center

## WHO THIS IS FOR
- 10 years in Oracle Cloud Consulting (Inventory & Procurement implementations, Senior Consultant)
- Last 3 years in management: ~1.5 yrs leading Supply Chain teams as Team Lead, ~1.5 yrs leading cutovers / test management / program-side work
- Signature strength: running complex multi-team cutovers (ranging from 600 to 2,000+ tasks) by building a plan collaboratively with dependent teams, tracking critical path, and constantly communicating status to stakeholders — NOT deep hands-on technical work
- Wants to move away from hands-on functional consulting into AI, without starting "from zero" — leveraging the program/PMO/communication skillset directly
- Location: Midtown Atlanta (some offices shifting to Alpharetta). Strong preference for remote/WFH; open to Atlanta hybrid or onsite for the right role; open to fully remote roles anywhere in the US
- Compensation goal: high base pay + meaningful equity/stock upside (ideally at a high-growth or pre-IPO AI company)

## TARGET ROLES
All four share a common core: business-level AI fluency + structured program execution + stakeholder communication. They differ mainly in emphasis.

1. Applied AI / Enterprise AI Strategy & Leadership — dream companies: OpenAI, Anthropic
2. AI PMO / AI Program & Transformation Lead (most direct match to cutover experience)
3. Chief of Staff (to a CAIO / Head of AI / AI initiative leader)
4. AI Governance / AI Risk & Compliance Program Lead
5. (Lower priority, more hands-on) AI Customer Engineer / Solutions role

App should surface additional adjacent roles as research uncovers them (e.g. AI Change Management Lead, AI Adoption Lead, AI Transformation Consultant).

## MARKET VALIDATION TO SEED INTO THE APP'S "WHY THIS FITS YOU" CONTENT
- Anthropic has posted a "Technical Program Management, Alignment" role requiring 5+ years in chief-of-staff/program management/operations in a research, technical, or fast-moving environment (incl. consulting/startups), and the ability to take a loosely-scoped problem and break it into concrete steps — a near-exact match to cutover leadership experience.
- Anthropic and OpenAI both state they value independent evidence of thinking/judgment over formal credentials for non-technical/program roles — certifications matter more for traditional enterprise/consulting ATS screens than for AI-native labs.
- Recommended primary certification: **Google Cloud Generative AI Leader** — explicitly designed for non-technical, strategy-first leaders evaluating and overseeing GenAI initiatives (not a coding-focused exam). AWS AI Practitioner is a reasonable secondary/broad-market credential but is more technical/engineering-flavored — deprioritize unless targeting a specific AWS-based employer.

## CORE DESIGN PRINCIPLE: ZERO DECISION FATIGUE
The single most important UX rule: the user should NEVER open the app and wonder "what do I do today?" There is always exactly ONE clear next action surfaced. Think fitness app crossed with a cutover plan — a single ordered checklist with one "current step" highlighted, not a menu of options.

## FEATURE SPEC

### 1. Daily Session Engine (the heart of the app)
- Total plan: 12 weeks, target ~2 focused hours/day, 5–6 days/week (~120-150 hrs total)
- Each day has exactly ONE session pre-built, broken into labeled blocks (e.g. "Block 1 (60 min): Watch [specific course module] + capture 3 notes", "Block 2 (60 min): [specific exercise, e.g. draft section of AI rollout plan]")
- Each block can be started/stopped independently (supports splitting across afternoon/evening) with a simple start/stop timer that logs actual time spent
- On stopping a block: quick capture — confidence rating (1-5), one-line note on what was done/learned
- **Auto-rolling catch-up logic**: if a day is skipped or only partially completed, remaining content automatically shifts forward and the schedule recalculates — the plan bends, never breaks, and always shows an updated projected completion date
- Home screen = "Today" view: today's date, one clear session card, progress ring for the week, nothing else competing for attention

> **Update:** this engine still owns *scheduling* (what day/block is next, timers, catch-up). Reflective and skill-practice blocks are increasingly delivered *through* the Conversational Coach below rather than as static text — see 1a. The two are complementary: the Daily Session Engine says "do this next"; the Coach is one way "doing it" can actually feel like doing it.

### 1a. Conversational & Interactive Coaching (the "Coach")

**Feature description.** Redesigns coaching/training delivery from static content (slides, text blocks, video-only instructions) to a conversational, chat-based interaction, available as its own module ("Coach") and reachable from relevant Daily Session blocks.

- Turn-based dialogue: the coach asks a question or poses a scenario, the user responds, the coach reacts and adapts — never a fixed linear script.
- Branching based on user responses: the model decides in the moment whether to probe deeper, offer a follow-up challenge, or move on, based on what the user actually said.
- **Practice mode**: short role-play scenarios (a talk, a pitch, a difficult conversation) where the user performs their part in the chat and gets in-the-moment feedback tied to the three coaching pillars (below).
- **Coaching mode**: a reflective/strategic Socratic dialogue — not a lecture.
- Lightweight progress tracking across sessions: the coach can reference what's been covered and what needs reinforcement, referencing past sessions naturally rather than starting cold every time.
- Bite-sized by default (~5-10 minutes) with a gentle nudge — never a hard cutoff — to wrap up around that mark; the user can always go deeper if they're engaged.
- Every session ends with **exactly ONE** clear, doable next step — never a list of takeaways.

**User flow.**
1. User opens **Coach** (top nav) or clicks a "talk to your coach about this" link from a Daily Session block.
2. Picks a mode (Coaching session / Practice mode) and, optionally, types a topic ("my pitch for an AI PMO role," "a hard conversation about scope").
3. The coach opens with a short greeting plus its first question or scenario — no menu, no instructions dump.
4. Turn-based chat: user replies, coach reacts/probes/challenges/moves on. Kept short on both sides.
5. Around the 5-10 minute mark, a gentle inline nudge appears; the user can keep going or end.
6. User clicks **End session** (available at any time) → the coach's final message is exactly one concrete next step. Session is marked ended and that next step is saved as its recap.
7. Past sessions (mode, topic, recap) are listed on the Coach landing page; starting a new session folds the last few sessions' recaps into that session's context so the coach can reference them naturally.

**System prompt / persona notes — INTERNAL ONLY, never shown to users.**

The coaching voice is implemented as an internal persona named **Elena Marsh**. Her name, background, and these notes exist purely as system/prompt context that shapes tone and behavior; nothing about her — not her name, not the word "persona" — is ever surfaced in the UI or spoken to the user. If a user asks who or what they're talking to, the coach stays in voice and redirects warmly rather than breaking character or naming the persona.

- **Background:** former community theatre director who moved into coaching nonprofit leaders and first-time public speakers. Believes confidence is built through honest reps, not innate talent. Guiding belief: *"You don't need to be perfect up there. You need to be real."*
- **Tone:** warm mentor — encouraging and patient, but never lets a vague or surface-level answer pass unchallenged. Pushes gently: *"That's a start — now go one layer deeper"* rather than empty praise like *"Great job!"*
- **Feedback style:** always specific and tied to what the user just said/did, never generic. E.g. *"The way you paused before your main point — that's the moment the story landed"* instead of *"Nice pacing!"*
- **Patient with repetition** — comfortable revisiting the same skill across multiple sessions without making the user feel behind.
- **Every session ends with exactly ONE clear, doable next step** — never a list of takeaways.

**Three coaching pillars**, used to structure both prompts and feedback:
1. **ANCHOR** (strategy) — clarify the single main point/goal of the user's communication: *"What's the one thing you want them to walk away with?"*
2. **PRESENCE** (delivery) — breath, pacing, eye contact, stillness, authenticity.
3. **STORY** (content/structure) — clarity, narrative arc, specificity over abstraction.

**Data model / session-state notes.**
- `coaching_sessions`: id, mode (`coaching`|`practice`), topic, status (`active`|`ended`), recap (the one next step, captured at end), started_at, ended_at.
- `coaching_messages`: id, session_id, role (`user`|`coach`), content, created_at — full transcript, replayed as conversation history on every turn since the Messages API is stateless.
- Cross-session memory is intentionally lightweight: rather than a separate summarization/embedding system, the last 2-3 ended sessions' (mode, topic, recap) are folded into a per-request context block alongside the user's current curriculum position, so the coach can reference prior work naturally without heavyweight infrastructure.
- The persona prompt is a frozen text block (prompt-cached) sent on every request; the dynamic per-session context (curriculum position, recent recaps) is a separate, uncached block appended after it.
- Requires the user's own Anthropic API key (billed pay-as-you-go, separate from a claude.ai subscription) — everything else in the app works without it.

### 2. Twelve-Week Curriculum Structure (seed content, refine live via research)
- **Weeks 1-2**: AI Fundamentals — Google AI Essentials, DeepLearning.AI "AI for Everyone", daily AI news habit, core vocabulary building
- **Weeks 3-4**: Enterprise AI & Applied AI Concepts — RAG, AI agents, foundation models, responsible AI basics; culminates in scheduling the Google Cloud Generative AI Leader exam
- **Weeks 5-6**: Portfolio Project #1 — write a full AI transformation/rollout plan for a real business domain (recommend: supply chain/procurement) — use cases, phased rollout, risks, stakeholder plan, success metrics
- **Weeks 7-8**: AI Program Management & Governance — model evaluation checkpoints, responsible AI/risk frameworks, AI change management; sit the Google GenAI Leader exam
- **Weeks 9-10**: Portfolio Project #2 + Story Bank — rewrite real cutover case studies (600 / 1,500 / 2,000-task cutovers) into STAR-format stories in AI/TPM language
- **Weeks 11-12**: Interview Readiness — mock interviews, behavioral practice, AI case-style questions (strategy/PMO-appropriate, not coding), company-specific prep incl. Anthropic & OpenAI interview style and culture research

Each week explicitly tagged to which target role(s) it serves (Strategy/PMO/CoS/Governance).

### 3. Readiness Score & Progress Dashboard
- Composite score out of 100, recalculated weekly, based on: modules completed, hours logged vs. target, weekly quiz performance, portfolio pieces completed, certification status, mock interview scores
- Radar or bar chart across categories: AI Fundamentals, Enterprise AI Strategy, AI Program Management/Governance, Communication/Portfolio, Interview Readiness
- Weekly summary auto-generated: hours logged, streak, quiz average, what's next

### 4. Weekly Accountability Quiz ("Sunday Check")
- Auto-generated 5-10 question quiz each week covering that week's material
- Mixes in 1-2 questions from prior weeks (spaced repetition) so nothing is forgotten
- Score feeds directly into readiness score; flags weak topics for review

### 5. Certification Tracker
- Simple table: certification/course name, provider, status (not started/in progress/done), target week, notes
- Seed with: Google AI Essentials, DeepLearning.AI AI for Everyone, Google Cloud Generative AI Leader (primary cert), optional AWS AI Practitioner as secondary

### 6. Portfolio Module
- Dedicated space to draft, store, and version the two major portfolio pieces (AI rollout plan; cutover-to-TPM story bank)
- Exportable as clean documents for later use in resume/interview prep

### 7. Resume & Positioning Module (activate ~week 9+)
- Store master resume/background
- Generate role-tailored variants for each target role type (Strategy, PMO, CoS, Governance)
- Explicit "translation layer" notes: how to phrase cutover/supply-chain experience in AI/TPM language
- Track which resume version was sent to which application

### 8. Job Discovery Module (build LAST, after confirming feasibility)
- Likely starts as a simple manual-refresh workflow rather than full automated scraping
- Weekly (or daily, if feasible) search for fresh postings matching target titles/keywords
- Filter for location: Remote US, or Atlanta-metro hybrid/onsite
- Priority flag for: OpenAI, Anthropic, major AI consulting practices (Deloitte, Accenture, KPMG, EY), major cloud vendors' enterprise AI/strategy teams (Oracle, Microsoft, Google, AWS), AI-native enterprise software companies
- Application tracker: date applied, role, company, status, resume version used

## TECHNICAL BUILD NOTES
- Single user, no auth needed — simple local web app
- Suggested stack: lightweight Python backend (Flask/FastAPI) or a simple static frontend, with SQLite or local JSON for persistence — propose the simplest option that supports daily timers, logging, and recalculating schedules
- Clean, minimal dashboard UI — prioritize the "Today" single-task view above all else
- Build in phases:
    1. Today view + daily session engine + timer + logging + catch-up logic
    2. Weekly quiz engine + readiness score dashboard
    3. Certification tracker + portfolio module
    4. Resume module
    5. Job discovery module (confirm feasible approach before building)
- Curriculum content, quiz questions, and job search results should be easy to refresh/edit over time (e.g. editable JSON/config files) since they'll be periodically updated via ongoing research
- **Conversational Coach dependency:** the Coach module (1a) is the one part of the app that calls an external service — the Anthropic Claude API — and requires the user's own API key in a git-ignored `.env` file. Every other module works fully offline with no key.

## FIRST STEPS REQUESTED FROM CLAUDE CODE
1. Propose simple tech stack + file structure
2. Scaffold Phase 1 first (Today view, daily engine, timer, catch-up logic)
3. Seed Week 1 content fully (with placeholders for weeks 2-12 to refine together)
4. Confirm before building Phase 5 (job discovery), since it has the most technical complexity

---

## IMPLEMENTATION STATUS (living note — see README.md for details)

- ✅ Phase 1 — Today view, daily session engine, timer, auto-rolling catch-up
- ✅ Phase 2 — Weekly quiz engine, readiness score dashboard
- ✅ Phase 3 — Certification tracker, Portfolio module
- ✅ Phase 4 — Resume & Positioning module
- ✅ Phase 5 — Job Discovery module, built as the manual-refresh workflow the spec suggested (priority-company shortcuts + a manual add/track flow), not automated scraping
- ✅ Conversational Coach (1a) — turn-based chat coaching + practice mode, "Elena Marsh" persona kept server-side only, three-pillar feedback structure, lightweight cross-session recap memory. Requires the user's own Anthropic API key.
- Curriculum content: Week 1 fully seeded; Weeks 2-12 are placeholders (theme + notes only) ready to be filled in the same JSON shape.
