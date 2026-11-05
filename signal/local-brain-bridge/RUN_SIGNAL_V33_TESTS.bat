@echo off
setlocal
cd /d "%~dp0"
echo SIGNAL v33 optional local software tests. No models downloaded, no cloud or device control.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 signal_doctor_v33.py --tests
) else (
  python signal_doctor_v33.py --tests
)
pause
