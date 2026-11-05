@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>&1
if %errorlevel%==0 (
 node test_workflow_v43.cjs
) else (
 echo Node.js missing - only Python tests will run.
)
where py >nul 2>&1
if %errorlevel%==0 (
 py -3 -m unittest -v test_local_v43.py
) else (
 python -m unittest -v test_local_v43.py
)
pause
