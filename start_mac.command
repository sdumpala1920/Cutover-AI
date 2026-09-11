#!/bin/bash
# Double-click this file to launch Cutover to AI on macOS.
# First run: sets up a virtual environment and installs dependencies
# (takes a minute or two). Every run after that starts instantly.
#
# This window is designed to NEVER close on its own — if something goes
# wrong, it prints the error and waits for you to press Enter, so you
# always have time to read what happened (and copy it to Claude if needed).

pause_and_exit() {
    echo ""
    echo "----------------------------------------------------------------"
    if [ "$1" != "0" ]; then
        echo "Something went wrong (see above). This window will stay open —"
        echo "copy any red/error text above and share it if you need help."
    else
        echo "Cutover to AI has stopped."
    fi
    echo "Press Enter to close this window..."
    read -r
    exit "$1"
}
trap 'pause_and_exit $?' EXIT

cd "$(dirname "$0")" || { echo "Could not find the project folder."; pause_and_exit 1; }

echo "Working in: $(pwd)"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 isn't installed (or not on PATH)."
    echo "Install it from https://www.python.org/downloads then try again."
    pause_and_exit 1
fi

if [ ! -f "run.py" ]; then
    echo "run.py wasn't found in this folder — this script needs to be"
    echo "inside the Cutover-AI project folder, not moved out on its own."
    pause_and_exit 1
fi

if [ ! -d ".venv" ]; then
    echo "First-time setup — creating a virtual environment..."
    if ! python3 -m venv .venv; then
        echo "Failed to create the virtual environment (see error above)."
        pause_and_exit 1
    fi
fi

source .venv/bin/activate

echo "Installing/checking dependencies (only takes long the first time)..."
if ! pip install -q -r requirements.txt; then
    echo "Failed to install dependencies (see error above) — check your"
    echo "internet connection and try again."
    pause_and_exit 1
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit it to add your Anthropic API key"
    echo "if you want to use the Coach feature (everything else works without it)."
fi

echo ""
echo "Starting Cutover to AI..."
echo "Opening http://127.0.0.1:5000 in your browser — keep this window open"
echo "while you use the app. Close this window (or press Ctrl+C) to stop it."
echo ""

( sleep 1.5 && open "http://127.0.0.1:5000" ) &
python3 run.py
