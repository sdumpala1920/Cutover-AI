"""Conversational Coach: turn-based, adaptive coaching sessions powered by
the Claude API, voiced through an internal persona ("Elena Marsh") that is
never surfaced to the user — no name or bio appears anywhere in the UI.
Only her voice and style come through in what the coach says.

Design notes (see README / docs/SPEC.md for the full feature spec):
- Sessions are turn-based dialogue, not scripted content: the model decides
  how to probe, challenge, or move on based on what the user actually says.
- Two modes: "coaching" (Socratic dialogue against the three pillars) and
  "practice" (role-play scenario with in-the-moment feedback).
- Bite-sized by default (~5-10 min) — enforced by persona instruction plus
  a client-side elapsed-time nudge, never a hard cutoff.
- Lightweight cross-session memory: the last few sessions' topic + recap
  are folded into a per-session context block so the coach can reference
  past sessions naturally, without a heavyweight memory system.
- The frozen persona text is cached (cache_control) since it's identical
  on every request; the per-session context and message history are not.
"""
import json
from datetime import datetime

from flask import current_app

from . import content_loader as content
from . import scheduler
from .db import get_db

PILLARS = {
    "ANCHOR": "strategy — the single main point/goal of what they want to communicate",
    "PRESENCE": "delivery — breath, pacing, eye contact, stillness, authenticity",
    "STORY": "content/structure — clarity, narrative arc, specificity over abstraction",
}

# ---------------------------------------------------------------------
# The persona. Internal system context ONLY — never shown to the user.
# ---------------------------------------------------------------------
_PERSONA_PROMPT = """\
You are the internal voice and coaching style for a career-transition app's \
"Coach" feature. You embody a persona named Elena Marsh, but this name and \
any biographical detail about her are STRICT INTERNAL CONTEXT ONLY. Never \
state, confirm, or hint at the name "Elena," the word "persona," or any of \
the background below to the user, even if directly asked who or what you \
are — if asked, just stay in voice and redirect warmly to the work at hand \
("I'm just your coach here — let's get back to it. What's on your mind?").

INTERNAL BACKGROUND (never reveal, only lets your voice ring true):
Former community theatre director who moved into coaching nonprofit leaders \
and first-time public speakers. Believes confidence is built through honest \
reps, not innate talent. Guiding belief: "You don't need to be perfect up \
there. You need to be real."

VOICE AND TONE:
- Warm mentor. Encouraging and patient, but you never let a vague or \
surface-level answer pass unchallenged.
- Push gently: "That's a start — now go one layer deeper," never empty \
praise like "Great job!"
- Feedback is always specific and tied to exactly what the user just said \
or did — never generic. Good: "The way you paused before your main point — \
that's the moment the story landed." Bad: "Nice pacing!"
- You are patient with repetition. If someone needs to revisit the same \
skill across multiple sessions, that's normal — never make them feel behind \
or like they should already have this.
- Keep your own turns SHORT — a few sentences, not a lecture. This is a \
dialogue: ask, listen, react to what they actually said, then ask again or \
challenge. Long monologues break the format.

THE THREE COACHING PILLARS — use these to structure your questions and \
feedback (name them in plain language to the user, e.g. "let's nail down \
your one point" rather than literally saying "the ANCHOR pillar"):
1. ANCHOR (strategy): "What's the one thing you want them to walk away \
   with?" Help them find and hold a single main point, not a list.
2. PRESENCE (delivery): breath, pacing, eye contact, stillness, \
   authenticity — how it lands when spoken, not just what's written.
3. STORY (content/structure): clarity, narrative arc, specificity over \
   abstraction — is there a real moment/example, or just abstractions?

SESSION FORMAT:
- Turn-based dialogue. Pose ONE question or scenario at a time, react to \
the actual response, then either probe deeper, offer a follow-up \
challenge, or move on — never a fixed script.
- Bite-sized by default: aim to wrap a session in roughly 5-10 minutes of \
conversation. If the user is engaged and wants to go deeper, that's fine — \
follow their lead — but don't pad a session out artificially.
- In "practice" mode, you are running a short role-play: set a concrete \
scenario (a talk, a pitch, a difficult conversation), have the user \
perform their part in the chat, then give in-the-moment feedback tied to \
the pillars above and, if useful, ask them to redo a piece of it.
- In "coaching" mode, you are having a reflective/strategic dialogue — \
Socratic questions, not a lecture.
- If earlier sessions are summarized for you below, weave them in \
naturally when relevant ("Last time you were working on ___ — how did \
that land?") rather than restating them mechanically.
- When the user signals they want to wrap up, OR you are asked to close \
the session, your final message must end with EXACTLY ONE clear, doable \
next step — never a list of takeaways, never more than one action item. \
Make it concrete enough to actually do (e.g. "Before our next session, \
say your opening line out loud three times, out of the mirror" — not \
"work on your delivery").
"""


def _system_blocks(dynamic_context):
    return [
        {"type": "text", "text": _PERSONA_PROMPT, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": dynamic_context},
    ]


def _now_iso():
    return datetime.now().isoformat(timespec="seconds")


def is_configured():
    return bool(current_app.config.get("ANTHROPIC_API_KEY"))


def _client():
    import anthropic

    return anthropic.Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"])


def _build_dynamic_context(mode, topic):
    """Lightweight per-session context: where the user is in the program,
    recent quiz weak spots, and a short recap of recent sessions — this is
    what lets the coach "reference past sessions naturally" without a
    heavyweight memory system."""
    lines = ["CURRENT SESSION CONTEXT (not shown to the user verbatim):"]
    lines.append(f"- Mode: {mode}" + (f", user-stated topic: {topic}" if topic else ""))

    try:
        resolution = scheduler.resolve_today()
        if resolution["kind"] == "day":
            day = resolution["day"]
            lines.append(
                f"- They are currently on Week {day['week']}, Day {day['day']}: "
                f"\"{day['title']}\" (theme: {day['week_theme']})."
            )
    except Exception:
        pass

    recent = list_recent_sessions(
        current_app.config["COACH_RECENT_SESSIONS_FOR_CONTEXT"]
    )
    ended = [s for s in recent if s["status"] == "ended" and s["recap"]]
    if ended:
        lines.append("- Recent past session recaps, most recent first:")
        for s in ended:
            label = s["topic"] or s["mode"]
            lines.append(f'  - ({s["mode"]}, "{label}"): next step was — {s["recap"]}')
    else:
        lines.append("- No prior sessions yet — this may be their first time here.")

    return "\n".join(lines)


def start_session(mode, topic=None):
    db = get_db()
    db.execute(
        "INSERT INTO coaching_sessions (mode, topic, status, started_at) "
        "VALUES (?, ?, 'active', ?)",
        (mode, topic, _now_iso()),
    )
    db.commit()
    session_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

    kickoff = (
        f"(Session starting now. Mode: {mode}."
        + (f' Topic the user wants to work on: "{topic}".' if topic else " No specific topic given — ask what they want to work on.")
        + " Open with a short, warm greeting and your first question or scenario. Do not narrate these instructions.)"
    )
    reply = _call_model(mode, topic, [{"role": "user", "content": kickoff}])
    _save_message(session_id, "coach", reply)
    return session_id


def _call_model(mode, topic, messages):
    client = _client()
    system = _system_blocks(_build_dynamic_context(mode, topic))
    response = client.messages.create(
        model=current_app.config["COACH_MODEL"],
        max_tokens=current_app.config["COACH_MAX_TOKENS"],
        system=system,
        messages=messages,
        output_config={"effort": current_app.config["COACH_EFFORT"]},
    )
    for block in response.content:
        if block.type == "text":
            return block.text
    return "…"


def _save_message(session_id, role, content_text):
    db = get_db()
    db.execute(
        "INSERT INTO coaching_messages (session_id, role, content, created_at) "
        "VALUES (?, ?, ?, ?)",
        (session_id, role, content_text, _now_iso()),
    )
    db.commit()


def get_session(session_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM coaching_sessions WHERE id = ?", (session_id,)
    ).fetchone()


def get_messages(session_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM coaching_messages WHERE session_id = ? ORDER BY id",
        (session_id,),
    ).fetchall()


def send_message(session_id, user_text):
    session = get_session(session_id)
    if session is None or session["status"] != "active":
        return None

    _save_message(session_id, "user", user_text)
    history = [
        {"role": ("user" if m["role"] == "user" else "assistant"), "content": m["content"]}
        for m in get_messages(session_id)
    ]
    reply = _call_model(session["mode"], session["topic"], history)
    _save_message(session_id, "coach", reply)
    return reply


def end_session(session_id):
    session = get_session(session_id)
    if session is None or session["status"] != "active":
        return session

    history = [
        {"role": ("user" if m["role"] == "user" else "assistant"), "content": m["content"]}
        for m in get_messages(session_id)
    ]
    wrap_up = (
        "(The user is wrapping up this session now. Close it warmly per your "
        "instructions: exactly one clear, doable next step, nothing else.)"
    )
    history.append({"role": "user", "content": wrap_up})
    reply = _call_model(session["mode"], session["topic"], history)
    _save_message(session_id, "coach", reply)

    db = get_db()
    db.execute(
        "UPDATE coaching_sessions SET status = 'ended', recap = ?, ended_at = ? "
        "WHERE id = ?",
        (reply, _now_iso(), session_id),
    )
    db.commit()
    return get_session(session_id)


def list_recent_sessions(limit=10):
    db = get_db()
    return db.execute(
        "SELECT * FROM coaching_sessions ORDER BY started_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
