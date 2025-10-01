@echo off
REM Change to the directory where this script is located
cd /d "%~dp0"

echo ============================================================
echo Starting Romeo ^& Juliet Web Application
echo ============================================================
echo.
echo Please wait while the system initializes...
echo This may take 30-60 seconds on first run.
echo.
echo Once you see "Running on http://...", open your browser and visit:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python app.py

pause
