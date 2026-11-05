@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v31 is a LOCAL blinded-source rehearsal, not an authenticated blind study.
echo Keep working v25 unchanged. Open http://127.0.0.1:8771/ on this computer.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 v31_server.py
) else (
  python v31_server.py
)
pause
