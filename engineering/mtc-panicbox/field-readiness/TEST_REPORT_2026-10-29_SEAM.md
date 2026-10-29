# VEIL MTC seam screening v0.1 — synthetic test report, 2026-10-29

**Test environment:** isolated Linux, Python 3.x, standard library only. No actual October 27 session audio, logs, Windows PC, Samsung phone, physical microphones, or live network used.

**New module:** `wav_seam_screen.py`; **new tests:** `test_wav_seam_screen.py` (23 tests).

**Test command:** `python -m unittest -q test_wav_seam_screen.py test_session_segment_audit.py test_wav_growth_probe.py test_external_watchdog.py test_status_contract.py`

**Result:** 98/98 PASS (23 new seam + 21 prior segmented audit + 21 WAV growth + 16 watchdog + 17 status contract). Compilation PASS. Missing-session CLI returned `HOLD`, exit 2. All fixtures generated synthetically in temporary folders.

**Coverage:** silence, steady signal, large cross-join sample step, clipping, 8/16/24/32-bit PCM, stereo, 3-segment session, short segments, malformed/truncated files, mismatched rates, missing segment, missing base, SHA changed after structural audit, symlink refusal, bounded memory failure, source bytes/mtime unchanged, no full path/raw samples in report, CLI JSON and failure exit, invalid thresholds/window.

**Interpretation:** Tests show expected software behavior on synthetic fixtures, NOT physical capture continuity or anomalous acoustic evidence. Join screening is a human review aid only. Actual MTC Oct 27 session remains to be inspected with explicit user authorization on a personal home computer; original evidence should be preserved and inspected via copies.
