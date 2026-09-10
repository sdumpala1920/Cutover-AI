#!/bin/bash
# Double-click this file to launch Cutover to AI on macOS.
# First run: sets up a virtual environment and installs dependencies
# (takes a minute or two). Every run after that starts instantly.
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "First-time setup — creating a virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

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
