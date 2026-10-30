# VEIL MTC read-only log/WAV reconciliation v0.1 — 2026-10-30

**Scope:** Completed MTC sessions, **personal home Windows computer only**. Python 3.10+ standard library, offline, no paid API, no hardware control, no changes to the MTC recorder. Adds a *separate* read-only diagnostic; it does not replace the recorder, existing WAV structural audit, or blinded Audio Evidence Review.

## What it checks

`session_log_reconcile.py` calls the existing `session_segment_audit.py` for the finalized `room_mic_continuous.wav` and `room_mic_continuous_partNNN.wav` files. It independently reads `events.jsonl`, `session_result.json`, and `session_metadata.json` with size limits, no-follow protections, file-change checks and SHA-256 fingerprints of **current bytes**. It detects missing/malformed logs, duplicate or out-of-order recording markers, unmatched/overlapping question markers, explicitly reported recording errors, obvious failed result status, and large disagreements between **recognized relative-time markers** and summed WAV duration. It reports only event-type counts and summary timing, **not raw event payloads, question text, or paths**. It writes a JSON report to stdout only.

The event parser currently recognizes the fields `event` or `type` for event names, and numeric relative-time fields `elapsed_seconds`, `t_seconds`, or `time_seconds`. It recognizes `recording_start` / `recording_started`, `recording_stop` / `recording_stopped`, `question_start`, `question_end`, and a small explicit set of error events. **The actual v0.1.4 Windows recorder event/result schema has not been inspected**. If it differs, the tool should report `ALERT` or `UNCONFIRMED` rather than invent a clean recording. Unknown event names are summarized, not automatically treated as paranormal or faulty. An `error` field in a JSON result is a fault indicator only if truthy. These are provisional adapters to verify against *copies* of actual session logs.

The `session_result.json` schema is **not authenticated**: a generic `"result":"ok"` or `"status":"success"` does not establish normal stop. Therefore even a fully clean synthetic case reports `UNCONFIRMED` and exit code **2**. `ALERT` also exits 2; no current result establishes physical success. A report without alerts is not proof of uninterrupted capture. There is deliberately no automatic `PASS` or paranormal conclusion.

## Home-only usage after recording is completely stopped

1. Preserve original WAVs, `events.jsonl`, `session_result.json`, `session_metadata.json`, photos and any prior hashes. Copy the completed session directory to a separate analysis location. **Do not run on the AJAX work computer**.
2. Put `session_log_reconcile.py` and `session_segment_audit.py` together in a separate tools folder, not in the evidence folder.
3. From personal Windows PowerShell or CMD, with your home Python installation:

   `py session_log_reconcile.py "C:\\path\\to\\ANALYSIS_COPY_OF_MTC_20261027_215040_70c105" --expected-minutes 90 --tolerance-seconds 120`

4. Inspect stdout JSON `alerts`, `holds`, `wav.total_audio_seconds`, `wav.segments`, `events`, and `sources`. If saving the report, redirect **outside** the evidence folder, e.g. `> C:\\VEIL_Analysis\\log_reconciliation.json`. The expected 90 minutes is **operator supplied**, not independently measured. Do not interpret exit 2 as a crash: `UNCONFIRMED` intentionally fails closed.
5. Confirm actual schema against logs, independently listen to the audio, check question audibility, review the WAV seams, and compare with independent video/audio if available. The tool cannot validate physical microphone performance, segment continuity, clock synchronization, full unattended duration, or paranormal causation.

**Data-integrity limitations:** Hashes are of bytes at the time of inspection and do **not** establish prior chain of custody. Filesystem access times may change when files are read, depending on the OS/filesystem. On Windows, reparse-point behavior and file locking still require home-machine testing. Do not use on active recording files. Files over 16 MiB per log/JSON, event lines over 64 KiB, and event logs over 100,000 entries fail closed. WAV checks retain the original audit's strict RIFF/PCM-only limitations. Avoid putting private session evidence in a public GitHub issue or PR.

## Tests (synthetic only)

`python -m unittest -q test_session_log_reconcile.py test_wav_seam_screen.py test_session_segment_audit.py test_wav_growth_probe.py test_external_watchdog.py test_status_contract.py`

2026-10-30: **128/128 PASS** on isolated Linux Python (30 new reconciliation + 23 seam + 21 segmented audit + 21 growth + 16 external watchdog + 17 status). `py_compile` PASS. Missing-folder CLI correctly produced `ALERT`/exit 2. Synthetic fixture source hashes unchanged after audit. **No user WAVs, Windows/Samsung devices, live recorder, overnight test, or actual v0.1.4 log schema validated.**

This work is stacked on draft PR #18, which depends on earlier unmerged MTC audit PRs. No merge or public website update.