# SIGNAL v32 — Local Readiness & Test Gate (November 5, 2026)

**Review-only milestone built on SIGNAL v31, v30, v29 and prior draft changes.** This is a self-contained *diagnostic script* (not a self-contained local AI application or an installable replacement of the existing v25 desktop build).

## What is new
- Read-only diagnostic confirms presence of v31 front-end, backend, and browser modules, syntax-checks the Python preview server without running it, checks Python 3.9+ and whether Node.js is installed.
- Explicitly flags missing `server.py` from the original Local Brain Bridge; preview launch is *not ready* without it. Files are not copied or silently repaired.
- `--tests` runs only a hard-coded allowlist of six local Node test scripts and reports results. It does not execute arbitrary commands provided in user data and does not open browser windows.
- Optional `--check-ollama` fetches installed model names **only on 127.0.0.1:11434** with a two-second timeout; never downloads a model, sends chat content or starts Ollama. Optional `--check-port` tests whether preview port 8771 is already occupied.
- Human-readable console results and `--json` machine-readable output. No persistent logs, telemetry, cloud calls, permanent settings changes, sensor control, file inspection outside this package, or purchases.

## How to use later on your Windows PC
Put these files **in a separate copy of the SIGNAL Local Brain Bridge folder**, with its original `server.py` included. Do not overwrite your working v25. Run `RUN_SIGNAL_V32_READINESS.bat`. For extra local checks, Command Prompt in the folder:

    py -3 signal_doctor.py --tests --check-ollama --check-port
    py -3 signal_doctor.py --json

The checker defaults to fully offline and does not contact Ollama unless you explicitly request it. Its `launch_ready` flag is false if the original bridge server file is missing or any required checks fail. It does *not* certify authentic evidence or working Windows microphones, TTS, models, GPU drivers or instruments. Those tests still need to occur on the physical computer.

## Test results from development environment
- Local Python unit checks: 16/16 passed, including no-network default, missing/extra files, symlinks, malformed model name, simulated local Ollama response, failed Node tests and JSON output.
- Six inherited Node suites executed with `--tests`: Casebook 25/25, fingerprint 15/15, correlation 23/23, clock 27/27, blinded review 23/23, and v31 UI 14/14 (127 test assertions in total across those suites).
- Diagnostic output in development reported the deliberately **missing original server.py as a warning**, with `launch_ready=false`. This is correct for the isolated ZIP; once the existing original bridge is present, it can be rechecked.
- No actual Windows, Ollama, microphone/speakers, MTC, Panic Box or field equipment test has been completed for v32.

## Source and review policy
GitHub draft only, no merge to main or live website. v25 stays untouched. Check results describe software readiness and are not a security certification, installation guarantee or evidence of scientific findings. No cost to produce or run the software other than hardware/electricity already in use.