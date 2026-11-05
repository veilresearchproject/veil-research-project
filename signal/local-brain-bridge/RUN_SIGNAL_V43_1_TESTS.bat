@echo off
setlocal
cd /d "%~dp0"
echo Testing SIGNAL v43.1 local prototype. No instruments or external AI needed.
where py >nul 2>&1
if %errorlevel%==0 (
 py -3 -m unittest -q test_local_v431.py test_local_v43.py test_lab_http.py test_memory_v34.py test_local_v33.py test_doctor_v33.py
) else (
 python -m unittest -q test_local_v431.py test_local_v43.py test_lab_http.py test_memory_v34.py test_local_v33.py test_doctor_v33.py
)
if errorlevel 1 goto failed
where node >nul 2>&1
if errorlevel 1 (
 echo Node.js is not installed; JavaScript tests skipped (Python tests passed).
 goto done
)
for %%f in (test_briefing_v431.cjs test_next_cores.cjs test_casebook.cjs test_fingerprint.cjs test_correlation.cjs test_clock.cjs test_blind.cjs test_v33_ui.cjs test_workflow_v43.cjs) do (
 node "%%f"
 if errorlevel 1 goto failed
)
:done
echo All available SIGNAL v43.1 local checks completed.
pause
exit /b 0
:failed
echo A test failed. Do not rely on this preview for evidence.
pause
exit /b 1
