@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v30 clock review is a separate local preview. Do not replace your working v25.
echo Open http://127.0.0.1:8770/ on this Windows computer.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 v30_server.py
) else (
  python v30_server.py
)
pause
