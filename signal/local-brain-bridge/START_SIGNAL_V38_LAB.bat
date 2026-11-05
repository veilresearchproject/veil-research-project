@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v38 lab - localhost-only preview on port 8773.
echo Existing SIGNAL v25 remains unchanged. No hardware connections.
echo Launching; visit http://127.0.0.1:8773/
where py >nul 2>&1
if %errorlevel%==0 (
 py -3 signal_local_v38.py
) else (
 python signal_local_v38.py
)
pause
