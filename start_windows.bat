@echo off
REM Double-click this file to launch Cutover to AI on Windows.
REM First run: sets up a virtual environment and installs dependencies
REM (takes a minute or two). Every run after that starts instantly.
cd /d "%~dp0"

if not exist ".venv" (
    echo First-time setup — creating a virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

if not exist ".env" (
    copy .env.example .env >nul
    echo Created .env from .env.example — edit it to add your Anthropic API key
    echo if you want to use the Coach feature (everything else works without it).
)

echo.
echo Starting Cutover to AI...
echo Opening http://127.0.0.1:5000 in your browser — keep this window open
echo while you use the app. Close this window to stop it.
echo.

start "" cmd /c "timeout /t 2 >nul && start "" http://127.0.0.1:5000"
python run.py
