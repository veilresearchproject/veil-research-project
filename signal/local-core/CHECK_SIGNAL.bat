@echo off
setlocal
cd /d "%~dp0"
echo Checking SIGNAL local Python and Ollama readiness. No models will be downloaded.
py -3 preflight.py --model llama3.2:3b
set "result=%errorlevel%"
echo.
if "%result%"=="0" (
  echo Local readiness passed. Review the on-screen benchmark command above.
) else (
  echo Not ready for the live benchmark. Read README.md and the messages above.
)
pause
exit /b %result%
