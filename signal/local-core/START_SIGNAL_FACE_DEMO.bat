@echo off
setlocal
cd /d "%~dp0"
echo Launching SIGNAL character/voice interface demonstration (scripted, not AI)...
py -3 signal_desktop.py --demo
if errorlevel 1 echo Check your Python 3 installation. See SIGNAL_DESKTOP_README.md.
pause
