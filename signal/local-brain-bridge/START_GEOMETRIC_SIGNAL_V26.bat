@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v26 geometric preview - separate from working v25.
echo Only starts localhost:8766. Keep the existing v25 installation unchanged.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 v26_server.py
) else (
  python v26_server.py
)
echo SIGNAL v26 stopped or could not start. Read GEOMETRIC_V26_README.md for setup.
pause
