@echo off
setlocal
cd /d "%~dp0"
py -3 signal_core.py
if errorlevel 1 echo SIGNAL could not launch. Python 3 and local Ollama may need setup; see VOICE_OUTPUT.md.
pause
