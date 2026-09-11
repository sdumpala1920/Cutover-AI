"""Entry point: python run.py"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # host="0.0.0.0" so it's also reachable from your phone on the same
    # Wi-Fi (see README) — 127.0.0.1 alone would refuse those connections.
    # use_debugger=False because this is now reachable by other devices on
    # your network: Flask's interactive debugger lets whoever hits an error
    # page run arbitrary code, which is fine on localhost-only but not once
    # other devices can reach it. use_reloader stays on for convenience
    # when editing curriculum/quiz JSON — no code-execution risk there.
    app.run(host="0.0.0.0", port=5000, debug=True, use_debugger=False)
