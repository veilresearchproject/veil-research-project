@echo off
setlocal
cd /d "%~dp0"
echo Running local SIGNAL unit and HTTP tests - no Ollama or microphone needed.
where py >nul 2>nul
if errorlevel 1 (
 echo Python launcher not found. Check your Python installation.
 pause
 exit /b 1
)
py -3 -m unittest discover -p "test_*.py" -q
if errorlevel 1 (
 echo One or more tests failed. Preserve this screen for troubleshooting.
) else (
 echo All available automated tests passed on this computer.
)
pause
