@echo off
setlocal
cd /d "%~dp0"
if not defined SIGNAL_MODEL set "SIGNAL_MODEL=llama3.2:3b"
echo SIGNAL v33: independent local preview; v25 remains untouched.
echo Open http://127.0.0.1:8772/ in a browser on THIS computer.
echo If Ollama is not running, scripted mode and research notes still work.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 signal_local_v33.py
) else (
  python signal_local_v33.py
)
pause