@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v27 Casebook preview - separate from v25 and v26.
echo Your existing Ollama process must be running for optional local AI.
echo Preview URL: http://127.0.0.1:8767/
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 v27_server.py
) else (
  python v27_server.py
)
echo SIGNAL v27 stopped or could not start. See README_V27.md for requirements.
pause
