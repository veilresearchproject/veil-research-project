@echo off
setlocal
cd /d "%~dp0"
echo.
echo SIGNAL - Local readiness check (no microphone activation)
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Install Python 3.10 or newer and enable its launcher.
  echo See SIGNAL_DESKTOP_README.md
  pause
  exit /b 1
)
py -3 signal_check_setup.py
if errorlevel 1 echo The setup check encountered a problem. See the onscreen information.
echo.
pause
