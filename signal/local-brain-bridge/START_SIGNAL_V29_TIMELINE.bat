@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v29 timeline comparison - separate localhost preview only.
echo Open http://127.0.0.1:8769/ in a browser on this computer.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 v29_server.py
) else (
  python v29_server.py
)
echo SIGNAL v29 stopped or unavailable. Read README_V29.md.
pause
