# VEIL MTC + SIGNAL — Offline Completed-Session Review (prototype v0.1)

**Date:** October 28, 2026. **Development only.** Synthetic-tested; NOT yet tested on Andrew's home Windows PC, real Oct 27 MTC v0.1.4 logs, actual 90-minute audio, or external recording devices. It does NOT modify the working MTC v0.1.4 recorder. No automatic changes, network calls, cloud AI, subscription or paid APIs. Standard-library Python 3.11+ only. No executables to install.

## Purpose

* `session_validator.py`: read-only inspection of files named `room_mic_continuous.wav`, `room_mic_continuous_part002.wav`, etc. Checks segment ordering, WAV headers and formats, declared audio durations, existence/parseability of `session_result.json` and `session_metadata.json`, and **only explicitly recognized** timestamped markers from `events.jsonl`.
* `signal_audio_screener.py`: streams 16-bit PCM mono/stereo WAVs and looks for sound-level excursions above a rolling baseline. Reports candidate **timestamps**, not inferred speech or EVP; nothing is cut out, denoised, modified, or classified as paranormal.
* `run_review.py`: combines both checks into a readable JSON report, writing nothing unless `--output` is supplied. When writing, it refuses a destination inside the session folder or an existing report filename.
* `test_offline_review.py`: synthetic fixtures and failure-path regression tests, using only Python's standard library. These tests are NOT physical validation.

## Prerequisites and careful first run — PERSONAL HOME PC ONLY

1. Finish the recording normally. Keep the ORIGINAL session folder untouched. Ideally make a **separate working copy of the completed session** before testing. Do not use AJAX work hardware.
2. With Python 3.11+ on the personal computer, open a Command Prompt in this tool directory, then run:

   ```bat
   python -m unittest -v test_offline_review.py
   python run_review.py "C:\path\to\COPY_OF_MTC_20261027_215040_70c105" --skip-audio
   ```

3. After we inspect the actual v0.1.4 JSON event schema and verify the supported WAV format, optional sound-level scan:

   ```bat
   python run_review.py "C:\path\to\COPY_OF_MTC_20261027_215040_70c105" --output "C:\VEIL_Review_Reports\mtc_review_20261027.json"
   ```

   The directory for the output report must already exist. The tool refuses to overwrite a report. Source WAV and JSON files are only read.

4. For adapting to real v0.1.4 logs, share **only** the three small text files (`events.jsonl`, `session_result.json`, `session_metadata.json`) with ChatGPT, if comfortable. Do not upload the large original WAV files just to inspect the log schema. First verify the event-type and timestamp keys and true session-result status fields; only then interpret question cycles and normal stop state.

## Explicit limits / fail-closed behavior

* Real Oct 27 metadata schemas have **not been examined**. The prototype reads `session_result.json` / `session_metadata.json` but currently checks only JSON-object structure and key names. **Stop success, app errors, question-cycle counts, configuration correctness, and normal termination are NOT yet parsed or verified.**
* The `events.jsonl` prototype expects `type`, `event_type`, `event`, or `name` with values such as `recording_start`, `recording_stop`, `question_start`, `question_end`; it accepts UTC-offset ISO timestamps in `timestamp_utc`, `timestamp`, `ts`, or `time`. This is a **synthetic test contract, not an assertion** that the actual v0.1.4 logger uses those keys. Unrecognized markers are not silently interpreted; unknown schemas remain `UNVERIFIED`.
* A WAV duration is calculated from its declared header/sample frames and **does not demonstrate gap-free audio**. A second part filename is not proof of an uninterrupted transition; compare independent timestamps and listen around the boundary.
* Question playback markers are **not independent acoustic evidence** that a speaker played the question or the microphone recorded it. For masking probable questions in candidate search, marker timing is only used when recognized, internally ordered and roughly consistent with WAV duration. You must still listen to actual audio. The mask includes a two-second buffer on either side; it can hide coincident sounds.
* Sound-level changes can be footsteps, HVAC, clicks, room noise, microphone handling, playback, or anything else. They are **candidates for human review only**. This version cannot recognize whispered speech, voice phonemes, word content, spirit voices, or distinguish known from unknown sources. Quiet activity can be missed and ordinary sounds falsely flagged. The absence of candidates does not mean no anomalies.
* Supported scan format: standard, uncompressed **16-bit PCM** mono or stereo RIFF WAV. Unsupported formats are reported; no automatic conversion or original-file alteration.
* The scanner streams the WAV, but full-length 90-minute testing, Windows WAV-sharing behavior, and source-header/actual-frame consistency require independent validation. Do not run against a live active recording.
* For privacy this tool makes **no network requests**, and the report includes filenames, key names, derived timing and levels but not full original audio content. Avoid sharing full metadata if it contains private or sensitive fields without reviewing it first.
* No evidence provenance verification: no cross-device timestamps, full original SHA-256 manifest, chained storage audit, synchronized video, or scientific causality claim.

## Automated test record

On Oct 28, 2026, 22/22 synthetic unit tests passed under isolated Python (not Windows). Test coverage includes split-number detection, invalid/missing JSON, unknown event markers, ordering, question pairing, PCM sound change detection, prompt masking, stereo, silence, untouched source bytes, and refusal to write within original evidence or overwrite a report. **This does not imply the real 90-minute run passed.**

## Engineering boundary and next stage

Staged on a separate review branch / DRAFT PR. No changes to `main`, working MTC recorder, public website, SIGNAL character, external watchdogs, Panic Box controls, scheduler or user home/work computers. Do not merge or deploy without human review. Next: map Oct 27 real metadata, add stop/errors/cycles validation, and test on a *copy* of a completed home session. For scientific audio analysis, compare independent room mics/cameras, preregister threshold settings, document known sound sources, and retain negative results.
