# VEIL MTC completed-session segmented WAV audit v0.1 — 2026-10-28

**Scope:** Read-only, offline, Python 3.10+ standard library. Designed for the completed 90-minute MTC test reported October 27 (session folder `MTC_20261027_215040_70c105`), **but that actual recording was not available to this engineering run**. All automated tests used generated synthetic PCM WAV files in temporary directories. Do not use on the AJAX work computer; personal home Windows desktop only.

## What it actually checks

`session_segment_audit.py` discovers `room_mic_continuous.wav` and numbered `room_mic_continuous_part002.wav`, `part003.wav`, etc. It checks for a missing base, numbering gaps, inconsistent sample formats, finalized RIFF/PCM headers, exact chunk/file lengths, complete PCM frames, and optional operator-supplied total duration tolerance. It streams SHA-256 hashes of the original files using read-only file descriptors and refuses symbolic links and files changing during inspection. It emits a JSON report to stdout without saving it to the evidence directory, and never reads/changes `events.jsonl`, `session_result.json`, or `session_metadata.json`.

A result of `STRUCTURE_CONSISTENT_NOT_CONTINUITY_VERIFIED` means only that **the individual completed PCM WAV files passed these structural checks**. It is NOT a confirmation of no missing audio at the segment boundaries, microphone validity, question playback, a normal stop, absence of errors, accurate wall-clock timing, paranormal activity, or an uninterrupted 90-minute session. Hashes describe bytes at inspection time; without a prior trusted manifest they do NOT establish historical provenance. Reading may update filesystem access times depending on OS/mount settings; code does not intentionally write evidence.

Unsupported/fail-closed: RF64/WAVE64, float/compressed WAV, WAV with trailing chunks, non-finalized headers, or other nonclassic RIFF/PCM layouts. Files in a currently active recording are not supported. Windows reparse-point/locking behavior and physical hardware remain untested.

## Personal home PC steps (do not use work PC)

1. **Wait until the MTC session is fully stopped**. Preserve the entire original session folder; do not rename or edit original WAVs, logs, or images. Ideally copy the session to a separate analysis folder and inspect the copy, retaining originals untouched.
2. Put `session_segment_audit.py` in a separate tools folder, not inside the evidence folder. From PowerShell or CMD using a personal home Python installation:

   `py session_segment_audit.py "C:\\path\\to\\MTC_20261027_215040_70c105" --expected-minutes 90 --tolerance-seconds 120`

3. Read the stdout JSON: `status`, `alerts`, `segments` with SHA-256, duration, frames and format, and `total_audio_seconds`. Exit code 0 means structural checks passed; exit code 2 means an alert or unconfirmed result. This does not create a report file automatically. If you save a report manually, keep it outside the original evidence folder and label it **derived analysis**.
4. Independently inspect `session_result.json`, `events.jsonl`, and `session_metadata.json` to check normal stop, questions played, errors and time markers. Listen to both original WAVs in a read-only workflow and inspect the join with an independent recorder. Preregister any EVP review and use blinded/sham controls. Do not claim continuity or a successful unattended 90-minute run from file sizes alone.

## Tests

`python -m unittest -q test_session_segment_audit.py test_wav_growth_probe.py test_external_watchdog.py test_status_contract.py`

**2026-10-28 result:** 75/75 passed in isolated Linux/Python 3.13: 21 new completed-session audit tests, plus 21 WAV-growth probe, 16 independent watchdog, and 17 status-contract regression tests. `py_compile` passed. Missing-folder CLI returned an `ALERT` with exit code 2. No real Windows/Samsung, microphone, audio evidence, actual 90-minute files, network, Panic Box hardware, or power-failure tests occurred. No cloud, APIs, paid services, equipment control, or publication.

**GitHub:** New draft PR stacked on draft PR #9, which is stacked on draft PR #7; nothing merged into `main` without review.
