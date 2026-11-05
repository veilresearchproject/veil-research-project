@echo off
setlocal
cd /d "%~dp0"
set "SIGNAL_V43_PORT=8775"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v43.1 integrated briefing preview - independent local folder and port.
echo Nothing here changes v25 or the public VEIL website.
echo Open http://127.0.0.1:8775/ on this computer.
where py >nul 2>&1
if %errorlevel%==0 (
 py -3 signal_local_v43.py
) else (
 python signal_local_v43.py
)
echo SIGNAL preview stopped or could not start. Refer to README_V43_1.md.
pause
