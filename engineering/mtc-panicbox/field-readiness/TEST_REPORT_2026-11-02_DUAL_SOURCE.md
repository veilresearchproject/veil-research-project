# 2026-11-02 dual-source health test report

- Source baseline: October 30 VEIL MTC Session Log Reconciliation v0.1 package; GitHub development branch `feat/mtc-session-log-reconcile-20261030`.
- New: `dual_source_health.py`, `test_dual_source_health.py`, this README and report.
- Test environment: isolated Linux container, Python standard library; no physical hardware, microphone, Samsung phone, real WAV evidence, or Windows execution.
- `python -m unittest -v test_dual_source_health.py`: **17/17 passed**.
- `python -m unittest discover -v`: **145/145 passed** (17 new + 128 existing).
- `python -m compileall -q .`: passed.
- Accelerated synthetic 90-minute run: 1,080 5-second virtual clock steps showed correlated simulated metadata/WAV growth; injected writer fault at virtual second 5,405 triggered `ALERT_REVIEW_REQUIRED`. This is NOT a physical 90-minute run.
- Fault categories: stalled WAV with advancing telemetry, stalled telemetry with WAV growth, missing/corrupt snapshot, microphone disconnected, writer failure, callback stall, missing WAV, replayed heartbeat, session ID or WAV path change. All remain operator-review signals, not acoustic or paranormal findings.
- Original source baseline files unchanged. No equipment control, publication, external contact, paid service, merge or cloud upload of evidence.
- Limitation: cross-check requires two consecutive independent observations, but existing status contract is synthetic-only. No live remote or home Windows validation.
