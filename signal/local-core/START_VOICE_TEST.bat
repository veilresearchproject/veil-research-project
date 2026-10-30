@echo off
setlocal
cd /d "%~dp0"
py -3 signal_voice_smoke.py
if errorlevel 1 echo Voice test encountered a problem. See VOICE_OUTPUT.md.
pause
