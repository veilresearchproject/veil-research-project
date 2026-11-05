@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v28 fingerprint prototype (separate from v25, v26 and v27).
echo Open http://127.0.0.1:8768/ in a browser on this computer.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 v28_server.py
) else (
  python v28_server.py
)
echo SIGNAL v28 stopped or unavailable. See README_V28.md.
pause
