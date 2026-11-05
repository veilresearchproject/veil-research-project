@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v43 independent unified research preview
 echo Local interface: http://127.0.0.1:8774/
echo Do not unzip over your working v25 directory.
where py >nul 2>&1
if %errorlevel%==0 (
 py -3 signal_local_v43.py
) else (
 python signal_local_v43.py
)
echo SIGNAL preview stopped. No settings were changed.
pause
