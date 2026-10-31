@echo off
setlocal
cd /d "%~dp0"
echo SIGNAL pre-desktop automated development checks
echo This runs Python tests only. It will not launch Ollama, a microphone, or speech.
echo.
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -m unittest -v test_four_workstreams test_operator_workbench test_model_readiness test_desktop_acceptance_check
) else (
  python -m unittest -v test_four_workstreams test_operator_workbench test_model_readiness test_desktop_acceptance_check
)
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" (
  echo Focused development tests PASS. This does NOT verify Windows audio or Ollama.
) else (
  echo Some development tests FAILED. Do not install this as the active SIGNAL release.
)
echo.
pause
exit /b %RESULT%
