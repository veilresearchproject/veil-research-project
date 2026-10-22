@echo off
setlocal
title SIGNAL Local Assistant - Assignment Demo
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js is required to run this optional local prototype.
  echo Node.js is free. This script never installs software or incurs charges.
  echo Visit https://nodejs.org/ on your own computer if you choose to install it.
  echo.
  pause
  exit /b 1
)
echo SIGNAL ASSIGNMENT RUNNER - LOCAL DEMONSTRATION
echo ------------------------------------------------
echo Runs a SYNTHETIC CSV audit, not a real instrument recording.
echo Creates private practice records in workspace and leaves
echo the assignment WAITING FOR HUMAN REVIEW.
echo.
node "%~dp0runner.js" demo
echo.
echo You can run 'node runner.js status' in this folder to see assignments.
pause
endlocal
