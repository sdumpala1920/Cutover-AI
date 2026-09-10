// Purely cosmetic: ticks the live elapsed-time display for the block that's
// currently running. All real timing/logging happens server-side off the
// start/stop timestamps, so this never needs to be authoritative.
function pad(n) {
    return String(n).padStart(2, "0");
}

function tick() {
    document.querySelectorAll(".timer-live[data-started-at]").forEach((el) => {
        const startedAt = new Date(el.dataset.startedAt);
        const display = el.querySelector(".timer-display");
        if (!display || isNaN(startedAt.getTime())) return;
        const elapsedSec = Math.max(0, Math.floor((Date.now() - startedAt.getTime()) / 1000));
        const h = Math.floor(elapsedSec / 3600);
        const m = Math.floor((elapsedSec % 3600) / 60);
        const s = elapsedSec % 60;
        display.textContent = `${pad(h)}:${pad(m)}:${pad(s)}`;
    });
}

setInterval(tick, 1000);
tick();

// Reveal the confidence/note capture form when "Stop" is clicked, instead
// of submitting immediately — the spec calls for a quick capture on stop.
document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-toggle-stop]");
    if (!btn) return;
    const key = btn.getAttribute("data-toggle-stop");
    const form = document.getElementById(`stop-form-${key}`);
    if (form) {
        form.hidden = !form.hidden;
        if (!form.hidden) {
            const noteInput = form.querySelector(".note-input");
            if (noteInput) noteInput.focus();
        }
    }
});
