# VEIL MTC session schema survey — test report

**Date:** 2026-10-29. **Status:** SYNTHETIC-TESTED ONLY; review required.

## Test environment
- Isolated Python 3 in execution container (Linux), standard-library-only code.
- `python -m unittest -v test_mtc_session_schema_survey.py`: **20 of 20 PASS**.
- `python -m py_compile mtc_session_schema_survey.py test_mtc_session_schema_survey.py`: **PASS**.

## Test coverage
- Valid synthetic result/metadata JSON plus 2-row JSONL, nested object/array field types and boolean vs number differentiation.
- Simulated private strings in field values suppressed from JSON output.
- Missing result file, malformed JSON, invalid JSONL line and payload leakage check.
- Blank lines, no final newline, non-object event rows, invalid UTF-8 and UTF-8 BOM.
- Too-large metadata JSON, too-large event file and too-long event row, symlinked file and symlinked session root.
- Source files byte-for-byte unchanged before/after survey; CLI success/HOLD exit codes.

## Not tested
- Actual October 27, 2026 90-minute physical recording or logs.
- Windows behavior, live recording, speaker playback, mic disconnect, recording seam, USB drive, external cameras, 48-hour battery endurance, false positive rates, or paranormal phenomena.
- A scanned, valid log does **not** demonstrate any event schema semantics or successful recording.

## Review gates
- Confirm synthetic tests on home Windows on a **copy**, after founder approval.
- Share only the schema summary if acceptable; map real event marker keys/semantics before adding a timeline validator.
- Keep draft unmerged; no expenses or external data upload.
