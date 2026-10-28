# VEIL MTC + SIGNAL — Synthetic Evaluation Add-on v0.3 (28 October 2026)

**Development only.** This folder contains the prior offline v0.2 reviewer plus a new repeatable synthetic audio benchmark and split-session integration tests. No change to the operating MTC v0.1.4 recorder, hardware controls, VEIL website, or public SIGNAL character. These tools do not contact a network or run paid AI. Do not execute on the AJAX work computer.

## What changed

- `signal_synthetic_benchmark.py`: produces deterministic, **entirely artificial** 5-second PCM WAV files with quiet/loud hum, short impacts, strong tones, faint tones, gradual ramps, and deliberate simulated microphone dropouts. Measures how often the unchanged SIGNAL amplitude-rise screener flags those events. Reports the unmodified SHA-256 hash for each synthetic input. WAVs are deleted automatically when the benchmark exits. This is a *functional regression and detection-limit probe*, not an EVP or speech evaluation.
- `test_signal_synthetic_benchmark.py`: 11 regression tests for benchmark structure, output, repeatability, silence, positive detection, restrictions and provenance.
- `test_synthetic_split_session.py`: 6 **offline** end-to-end tests creating a 90-SECOND artificial split WAV session (60 seconds + 30 seconds), question marker, JSON logs, hashed originals, candidate CSV, opt-in derived clips and seam checks. Explicitly exercises missing segment detection and the no-gapless-claims restriction. **90 seconds is not 90 minutes.**

## Tested on 28 October 2026

- Existing v0.2 offline review tests: **46/46 passed**.
- New benchmark tests: **11/11 passed**.
- New split-session tests: **6/6 passed**.
- Full local suite: **63/63 passed** in an isolated Python environment; `py_compile` of new files passed. This does not assert GitHub CI or Windows execution.
- Standalone benchmark: **36 synthetic cases**, including 12 deliberately obvious tone/impact cases (12/12 flagged), 12 negative stationary/silent cases (0 flagged), and 12 exploratory cases (4/12 flagged). By profile: faint tones **0/4**, gradual ramps **4/4**, synthetic microphone dropouts **0/4**.

### What this actually means

The detector correctly catches some defined loud synthetic changes. It **misses faint tones**, and an amplitude-**rise** detector should **not** be expected to catch microphone disconnection or loss of signal. Use the independent capture-health watchdog design to detect microphone/writer faults. Do not claim 100% accuracy, sensitivity to whispers, real-world false-positive rate, speech or EVP recognition, physical reliability, continuous capture or paranormal events based on this synthetic dataset. Negative controls are limited to simple generated hum/silence; they do not represent real homes.

## Reproduce the tests

From the folder containing `*.py` using Python 3.11+ standard library:

```console
python -m unittest -v test_offline_review.py test_evidence_review_pack.py test_seam_survey.py test_signal_synthetic_benchmark.py test_synthetic_split_session.py
python signal_synthetic_benchmark.py --seeds 2 --output "PATH_TO_NEW_FILE.json"
```

The `--output` path must not already exist. The default benchmark uses disposable temporary synthesized audio only. It neither opens the real MTC session nor interacts with recording hardware. The benchmark JSON has event case descriptors and hashes but no audio evidence or user information.

## Next blocked/critical step

Review copies of the **actual October 27 session** files: `session_result.json`, `session_metadata.json`, and `events.jsonl`, so we can map the real v0.1.4 schema before using the review tool on completed audio. Only run a real-file dry run on a preserved COPY of the 90-minute WAV session at the personal home PC, not the work laptop. Then measure real acoustic false-positive rates using blinded controlled sound clips, separately measured fan noise, quiet human speech, deliberate muted microphone and recorder failure. This will require independent health telemetry, not just the SIGNAL level screener.

**Do not merge without the founder's review.**
