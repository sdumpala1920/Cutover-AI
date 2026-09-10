// Fetch-based chat: sending a message appends both bubbles without a full
// page reload, which is what makes it feel like a real conversation rather
// than a form. Ending a session is a plain form POST (see coach_session.html)
// since it's a rarer, heavier action where a reload to the "ended" state is fine.
(function () {
    const card = document.getElementById("chat-card");
    if (!card) return;

    const sessionId = card.dataset.sessionId;
    const log = document.getElementById("chat-log");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const nudge = document.getElementById("bitesize-nudge");

    function addBubble(role, text) {
        const div = document.createElement("div");
        div.className = "chat-bubble chat-" + role;
        div.textContent = text;
        log.appendChild(div);
        log.scrollTop = log.scrollHeight;
    }

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;

            addBubble("user", text);
            input.value = "";
            input.disabled = true;

            const thinking = document.createElement("div");
            thinking.className = "chat-bubble chat-coach chat-thinking";
            thinking.textContent = "…";
            log.appendChild(thinking);
            log.scrollTop = log.scrollHeight;

            try {
                const res = await fetch(`/api/coach/${sessionId}/message`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: text }),
                });
                const data = await res.json();
                thinking.remove();
                if (data.error) {
                    addBubble("coach", data.error);
                } else {
                    addBubble("coach", data.reply);
                }
            } catch (err) {
                thinking.remove();
                addBubble("coach", "Connection error — please try sending that again.");
            } finally {
                input.disabled = false;
                input.focus();
            }
        });
    }

    // Gentle bite-size nudge, never a hard cutoff.
    if (nudge && card.dataset.active === "true") {
        const startedAt = new Date(card.dataset.startedAt).getTime();
        const limitMs = parseFloat(card.dataset.bitesizeMinutes) * 60 * 1000;
        setInterval(() => {
            if (Date.now() - startedAt > limitMs) {
                nudge.hidden = false;
            }
        }, 15000);
    }

    log.scrollTop = log.scrollHeight;
})();
