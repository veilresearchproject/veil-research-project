# VEIL MTC session log/WAV reconciliation — synthetic test report

**Date:** 2026-10-30. **Environment:** isolated Linux, Python 3.13.x (standard library). **Branch:** `feat/mtc-session-log-reconcile-20261030` based on unmerged `feat/mtc-wav-seam-screen-20261029`.

## New behavior
- Reads finished-session `events.jsonl`, `session_result.json`, `session_metadata.json` with bounded no-follow file reads and SHA-256; invokes existing segmented WAV structural audit.
- Detects malformed/missing logs, obvious error/result flags, event order and question-marker problems, and log-to-WAV duration mismatch when relative-time fields are recognized.
- Emits summaries without raw question/event payloads; no writes to evidence folder; unknown recorder schemas are not certified.
- **Deliberately never claims recording success**: result schema not yet authenticated; synthetic clean case returns `UNCONFIRMED`/exit 2.

## Verified tests
- 30 new synthetic unit tests: PASS.
- 98 earlier MTC field-readiness regression tests: PASS (23 seam + 21 segmented audit + 21 growth + 16 watchdog + 17 status).
- **Total: 128/128 PASS**.
- `python -m py_compile` for new and dependency modules: PASS.
- CLI nonexistent-folder smoke test: `ALERT`, exit code 2: PASS.
- File-hash nonmutation and no raw event content in output: covered by new unit tests.

## Explicitly unvalidated
- No real MTC v0.1.4 event/result JSON schema supplied or examined.
- No physical Windows, Samsung, microphone, speaker, network, Panic Box, 65/90-minute or overnight test in this run.
- No actual October 27 session data analyzed. No continuity, playback audibility, physical provenance, or paranormal inference.
- Source read may affect access time on some filesystems; Windows reparse-point and file-locking behavior not exercised.

## Next personal home-PC acceptance gate
Preserve original October 27 session files and hashes, inspect an **analysis copy** of its WAVs/logs using the new tool, check which actual event timestamp keys appear, adapt parser on an isolated branch if needed, and independently listen to recording seams/questions. Require human review before any evidence conclusion or merge.
