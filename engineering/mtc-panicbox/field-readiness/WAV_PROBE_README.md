# VEIL MTC — Read-only WAV growth observer v0.1 (2026-10-27)

**Isolated prototype; synthetic-tested on Linux/Python 3.13. NOT field validated.**

This independent, standard-library-only observer supplements the synthetic JSON watchdog in draft PR #7. It opens an explicitly selected active WAV file read-only, parses no more than 64 KiB of header, and compares physical file size and estimated complete PCM frames across polls. It never modifies WAVs, microphones, recorder software, Panic Box mode, logs, evidence manifests, or hardware. No network, phone telemetry, paid API, cloud, or service.

Results: UNCONFIRMED means first observation or no proven file growth. GROWTH_OBSERVED_NOT_AUDIO_VERIFIED means the same file gained estimated complete PCM frames. ALERT means missing/locked/malformed/unsupported WAV, no frame progress for >20 seconds, prolonged partial frame, truncated/replaced file, format change, or clock regression. Truncation, replacement, format change and clock regression latch until manual review/restart. File growth NEVER proves a microphone is connected, sound was captured, evidence is genuine, or a recording is healthy.

Only classic RIFF/WAVE integer PCM is supported (8/16/24/32-bit; 1–8 channels; fmt before data). Assumes the data chunk extends to EOF. RF64, WAVE64, compressed, float, trailing-metadata WAVs, and large headers are unsupported or may give misleading estimated frame counts. Live WAV headers may not update until closure; the observer warns of header-size disagreement. Windows file-sharing locks/reparse points require separate tests. The probe cannot detect its own crash, host power loss, audio silence, microphone dropout, buffered writer delays, or changes to a different segmented file. Do not expose results as live phone status.

Run tests offline from this folder (isolated environment or PERSONAL HOME WINDOWS PC ONLY; never AJAX-owned work computer):

    python -m unittest -v test_wav_growth_probe.py test_external_watchdog.py test_status_contract.py

Optional personal-home test on a disposable, non-evidence, uncompressed PCM WAV:

    python wav_growth_probe.py "C:\path\to\active_test.wav" --poll-seconds 5 --stalled-after-seconds 20

A single --once observation cannot establish progress. Console JSON includes counters and alert codes, not WAV content or full paths. Do not run this against irreplaceable original evidence before reviewing the evidence-handling procedure.

Home-only next step: determine whether the existing MTC recorder uses supported PCM WAV and allows concurrent read-only file opens; test on a NEW disposable recording, independently compare the WAV and room audio, inject a stopped writer/recorder and microphone fault, and preserve originals/hashes. For segmented recordings, require explicit human selection of each active segment; do not silently accept replacement. Later run real 65-minute/overnight endurance with independent corroboration and preregistered blinded/sham sound review.

**Test record (2026-10-27):** 54/54 automated tests passed on isolated Linux/Python 3.13: 21 new WAV tests, 16 external watchdog, 17 status contract. The 65-minute timeline was a fast-forwarded synthetic clock with generated PCM bytes, NOT a real 65-minute recording. No Windows, Samsung, real microphone, remote communications, power, or equipment-control tests. No cost or publication.
