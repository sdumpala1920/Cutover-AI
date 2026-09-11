@echo off
REM Double-click this file to launch Cutover to AI on Windows.
REM First run: sets up a virtual environment and installs dependencies
REM (takes a minute or two). Every run after that starts instantly.
REM
REM This window is designed to NEVER close on its own — if something goes
REM wrong, it prints the error and waits for a key press, so you always
REM have time to read what happened (and copy it to Claude if needed).

cd /d "%~dp0"
echo Working in: %cd%
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python isn't installed, or wasn't added to PATH during install.
    echo Install it from https://www.python.org/downloads
    echo IMPORTANT: check the box "Add Python to PATH" during setup.
    goto :fail
)

if not exist "run.py" (
    echo run.py wasn't found in this folder — this file needs to stay
    echo inside the Cutover-AI project folder, not be moved out on its own.
    goto :fail
)

if not exist ".venv" (
    echo First-time setup — creating a virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create the virtual environment ^(see error above^).
        goto :fail
    )
)

call .venv\Scripts\activate.bat

echo Installing/checking dependencies ^(only takes long the first time^)...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies ^(see error above^) — check your
    echo internet connection and try again.
    goto :fail
)

if not exist ".env" (
    copy .env.example .env >nul
    echo Created .env from .env.example — edit it to add your Anthropic API key
    echo if you want to use the Coach feature ^(everything else works without it^).
)

echo.
echo Starting Cutover to AI...
echo Opening http://127.0.0.1:5000 in your browser — keep this window open
echo while you use the app. Close this window to stop it.
echo.

start "" cmd /c "timeout /t 2 >nul & explorer http://127.0.0.1:5000"
python run.py

echo.
echo Cutover to AI has stopped.
pause
exit /b 0

:fail
echo.
echo ----------------------------------------------------------------
echo Something went wrong ^(see above^). This window will stay open —
echo copy any error text above and share it if you need help.
pause
exit /b 1
