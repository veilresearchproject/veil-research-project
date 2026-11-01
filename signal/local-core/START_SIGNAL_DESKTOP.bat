@echo off
setlocal
cd /d "%~dp0"
echo Starting SIGNAL local desktop with Ollama...
py -3 signal_desktop.py
if errorlevel 1 echo Check Python 3 and your local Ollama setup. See SIGNAL_DESKTOP_README.md.
pause
