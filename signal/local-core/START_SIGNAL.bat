@echo off
cd /d "%~dp0"
py -3 signal_core.py
if errorlevel 1 echo Python 3 launcher not found. Read README.md first.
pause
