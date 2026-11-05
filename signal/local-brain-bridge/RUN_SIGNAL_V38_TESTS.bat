@echo off
setlocal
cd /d "%~dp0"
echo SIGNAL v38 tests - no cloud, no device actions.
where py >nul 2>&1
if %errorlevel%==0 (
 py -3 -m unittest -v test_memory_v34.py test_lab_http.py test_local_v33.py test_doctor_v33.py
) else (
 python -m unittest -v test_memory_v34.py test_lab_http.py test_local_v33.py test_doctor_v33.py
)
where node >nul 2>&1
if not %errorlevel%==0 (
 echo Node.js not installed: JS tests skipped.
 goto done
)
node test_next_cores.cjs
node test_casebook.cjs
node test_fingerprint.cjs
node test_correlation.cjs
node test_clock.cjs
node test_blind.cjs
node test_v33_ui.cjs
:done
pause
