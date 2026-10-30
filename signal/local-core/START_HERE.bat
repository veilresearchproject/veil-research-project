@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. SIGNAL needs Python 3.10 or newer with its launcher.
  echo Nothing has been installed or downloaded. See README_FIRST.txt.
  pause
  exit /b 1
)
py -3 signal_launcher.py
if errorlevel 1 echo Keep this message for troubleshooting. Existing evidence files were not changed.
pause
