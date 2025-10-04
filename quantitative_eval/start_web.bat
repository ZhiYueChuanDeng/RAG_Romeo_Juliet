@echo off
REM Change to the directory where this script is located
cd /d "%~dp0"

echo ============================================================
echo Starting Romeo ^& Juliet Web Application
echo ============================================================
echo.

REM Check if Ollama is running
echo [1/3] Checking Ollama status...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo   ^> Ollama is already running
) else (
    echo   ^> Starting Ollama service...
    start "" "ollama" app
    timeout /t 3 /nobreak >NUL
    echo   ^> Ollama started
)
echo.

REM Check if llama3.2 model is available
echo [2/3] Checking llama3.2 model...
ollama list | find "llama3.2" >NUL
if "%ERRORLEVEL%"=="0" (
    echo   ^> Model llama3.2 is ready
) else (
    echo   ^> Model llama3.2 not found. Downloading...
    echo   ^> This may take several minutes on first run...
    ollama pull llama3.2
    echo   ^> Model downloaded successfully
)
echo.

echo [3/3] Starting Flask web application...
echo   ^> Please wait while the system initializes...
echo   ^> This may take 30-60 seconds on first run.
echo.
echo Once you see "Running on http://...", open your browser and visit:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python app.py

pause
