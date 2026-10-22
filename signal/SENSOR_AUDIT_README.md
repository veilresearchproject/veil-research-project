# SIGNAL Sensor Data Audit Bench v0.8 — Engineering Notes
**Date:** October 22, 2026  
**Status:** Public browser-based research-data utility, *not* a validated laboratory instrument or an AI model.  
**Project:** VEIL Research Project / SIGNAL — https://veilresearchproject.github.io/veil-research-project/signal/#signal-csv-lab

## What works now
- A visitor selects a local CSV file or explicitly loads synthetic sample data.
- The browser processes CSV text without an upload or remote model call.
- The program validates a timestamp including a time zone, a numeric temperature in °C, and optional sensor ID.
- Each sensor's data are checked separately in source order for duplicate/out-of-order timestamps, cadence gaps, and temperature step changes.
- Thresholds are user-defined. Defaults: 60-second expected sampling interval; gaps flagged above 1.5× interval; temperature steps flagged at ≥1.5°C.
- A report is assembled for local download with source filename or synthetic label, row counts, sensor summary, flags with CSV row numbers, limitations, and an optional SHA-256 fingerprint of the selected file bytes when the browser supports Web Crypto.

## Required CSV header and example
```csv
timestamp,sensor_id,temperature_c
2026-10-22T08:00:00Z,Room-A,21.0
2026-10-22T08:01:00Z,Room-A,21.1
2026-10-22T08:02:00Z,Room-A,19.2
```
The `sensor_id` column is optional (single series defaults to `sensor-1`). `timestamp` and `temperature_c` are mandatory. Time strings must be explicit ISO 8601 with a `Z` or timezone offset; ambiguous local timestamps are invalid. Each row represents one sensor measurement. CSV files with several sensors can interleave rows, but observations within each sensor should be ordered chronologically to avoid order warnings.

## Test status (automated, simulated environments)
- The 8-row synthetic dataset from two sensors yields **one 1.9°C temperature step** and **one 240-second gap** at the default thresholds.
- The engine was run through **14 regression scenarios**, including out-of-order and duplicate timestamps, invalid calendar dates, malformed quotation marks, missing timezone, CSV encoding markers, oversized input, reporting disclaimers, and a 12,000-row stream.
- UI interaction was tested with browser API mocks for file selection, optional SHA-256 hashing, report download, synthetic sample, and reset.
- Actual browser/device end-to-end testing and GitHub Pages deployment confirmation remain outstanding until verified.

## Privacy, integrity and scientific limits
- Files remain local to the browser. The code does not send CSV data to VEIL or any cloud AI provider.
- The maximum selected file size is **1 MB** and the analyzer limits input to **15,000 data rows** and 24 columns.
- The tool does **not** verify calibration, data provenance, sensor identity, acquisition integrity, environmental causes, or paranormal phenomena.
- SHA-256 is a fingerprint of bytes, not a chain-of-custody proof.
- Invalid rows are counted and skipped; the analysis must be treated as incomplete if any invalid rows are present. The original CSV should be kept unchanged.
- Event listings are capped for performance. The generated report states if additional flags were omitted.
- The synthetic example is not a VEIL field test or evidence.

## Reproduce regression tests
From a working clone of the public repository, with Node.js installed:
```bash
node signal/tests-csv-audit.js
```
No npm dependencies, credentials, hardware, subscriptions, or API key are required for this test command.

## Source files
- `signal/csv-audit-core.js` — pure CSV parser, quality checks, generated report format.
- `signal/csv-audit-ui.js` — private local file handling and on-screen results.
- `signal/index.html` — user interface and SIGNAL visitor page.
- `signal/tests-csv-audit.js` — reproducible regression checks.

## Next engineering work
1. Verify the page in Edge on Windows, Firefox, and a mobile browser, especially file import, keyboard navigation and report download.
2. Add cross-sensor comparison and documented time sync corrections, not interpretations of cause.
3. Develop an independently testable, local-first Windows conversational AI companion. Only then evaluate **read-only** authorized integration with actual MTC and Panic Box streams.
4. Keep visitors informed about the separation between SIGNAL's fictional on-screen personality, deterministic data-audit utilities, and planned model-driven research assistance.
