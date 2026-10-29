# VEIL MTC segmented WAV seam screening v0.1 — 2026-10-29

**Status:** Isolated engineering prototype; synthetic-tested only; NOT merged, published, or validated on Windows/Samsung or on the actual October 27 MTC recording. $0 additional. Python 3.10+ standard library, offline and read-only.

## Purpose and interpretation

The October 27 MTC v0.1.4 session reportedly produced `room_mic_continuous.wav` and `room_mic_continuous_part002.wav`. The existing `session_segment_audit.py` (draft PR #13) checks structural validity and SHA-256 hashes, but cannot assess audio near the join. This new **screening** module adds bounded decoded PCM sample analysis at each adjacent segment boundary. It reports the final/initial window RMS in dBFS, clipping fractions, and the one-sample jump across the boundary, with optional review cues for silence, clipping, and a large jump. It re-hashes each complete file and compares SHA-256 with the prior structural audit, detects changed file metadata, refuses symlinks, and writes nothing to the source folder.

**No cue proves missing samples or anomalous phenomena. No absence of cues proves seamless recording.** A natural transient can cause a large sample step, and missing minutes can still leave a small step. Quiet windows may simply reflect a quiet room; a flat silent track can pass structural checks. Human review must examine the original recording and independent event timing, including the question playback, stop status, and join region. Do not use automated sound detection as proof of EVP. Keep blinded/sham review preregistered.

## Personal home Windows use only (after Andrew's review)

1. Preserve original session folder and original hashes, copy it to a separate local analysis folder. Never use an AJAX-owned computer. Do not run during active recording.
2. Put `session_segment_audit.py` and `wav_seam_screen.py` in a **tools** folder, outside the evidence folder. Both must be present; the seam tool depends on the audited strict RIFF/PCM parser.
3. From a personal home Windows PowerShell with local Python installed, run:

   `py wav_seam_screen.py "C:\\VEIL\\analysis-copy\\MTC_20261027_215040_70c105"`

4. The JSON is printed to the terminal, not saved to the evidence folder. If a report is needed, redirect it to a **separate analysis location** and label it derived data. Exit code 0 means screening completed (or no joins), **not recording validated**; exit 2 means hold/error.
5. Compare the join with playback of the actual audio and independently read `events.jsonl`, `session_result.json`, `session_metadata.json`, independent video/audio, and question schedule. Record uncertainty, known dog/door sounds, and unresolved gaps.

## Safety and limitations

- Supported only on finalized strict classic RIFF PCM files supported by draft PR #13 (8/16/24/32-bit, 1–8 channels, 8–192 kHz). No RF64, WAVE64, floating point, compressed, unfinished headers, or active writes.
- Edge windows default to 0.25 s each side, selectable 0.01–1 s, with a maximum of 250,000 decoded samples per edge to limit RAM. For large files, full-file SHA-256 reading twice (structural audit and seam verification) can be slow. Reading may affect filesystem access times; no deliberate evidence writes.
- Heuristic defaults: quiet ≤ -55 dBFS RMS, sample step ≥ 0.5 full-scale, clipped fraction ≥ 1%. These are **review prompts, not calibrated scientific decision thresholds**. No acoustic source identification, sample-continuity certification, automatic EVP classification, or session completion inference.
- Does not parse events, cross-correlate independent microphones, or align wall-clock timestamps. Windows reparse points, physical locking, and real Windows performance untested. Files could be modified after this scan; hash manifests and a documented chain of custody are still required.
- Outputs filenames and edge statistics, not raw audio, transcripts, full private file paths, or memory. No network, cloud, paid API, device control, or public website changes.

## Reproducible synthetic tests

Run from this folder: `python -m unittest -q test_wav_seam_screen.py test_session_segment_audit.py test_wav_growth_probe.py test_external_watchdog.py test_status_contract.py`

October 29 run: **98/98 PASS** (23 new seam tests + 21 segment audit + 21 WAV growth + 16 external watchdog + 17 status contract), isolated Linux/Python environment. `py_compile` PASS. CLI missing-folder negative test exited 2 with `HOLD`. All generated audio synthetic. **Actual October 27 recording NOT available or tested.**

## GitHub isolation

Stacked draft branch based on `feat/mtc-postsession-segment-audit-20261028` (PR #13), itself based on draft PR #9 and #7. No merge, no public release. Preserve main, website, SIGNAL character, assignment runner, and CSV audit. Founder approval before using on physical evidence or merging.
