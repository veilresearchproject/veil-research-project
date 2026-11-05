@echo off
setlocal
cd /d "%~dp0"
echo SIGNAL v32 offline readiness check. No files will be modified or software installed.
echo v25 remains untouched. The local model will NOT be contacted during this default check.
where py >nul 2>&1
if %errorlevel%==0 (
 py -3 signal_doctor.py --tests
) else (
 python signal_doctor.py --tests
)
echo.
echo For an optional Ollama localhost check: py -3 signal_doctor.py --check-ollama
pause
