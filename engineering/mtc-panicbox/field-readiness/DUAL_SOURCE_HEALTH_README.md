# VEIL MTC dual-source recording health cross-check v0.1

**2026-11-02 | Draft engineering prototype | No-cost / offline / read-only**

## Purpose

Compare two distinct observations: (1) the independent status snapshot watchdog and (2) measured PCM WAV frame growth. Recorder-reported `bytes_written` alone is not evidence that audio reached the WAV file. The combined monitor refuses to certify audio or recording success. It **does not modify the recorder or recordings**.

## Prototype limitations

- The existing `veil.field-status.v0.2` contract **requires `simulation_only: true`**. All outputs from this prototype are simulated, even when the WAV probe reads real file metadata. **Never describe this as validated live Windows status or remote phone monitoring.**
- No authentication, network transport, notification delivery, remote phone status, power-loss survival, actual microphone acoustics, recording provenance, or physical hardware test.
- Correlated metadata and WAV growth are still **not proof of microphone sound capture**, sample continuity, audio content, or evidence integrity.
- A WAV path change or session ID change is held for review. Segmented sessions need explicit boundary handling and the existing post-session seam and log audits.
- Alerts latch in the monitor's RAM until the process is restarted. Restarting does **not** constitute a verified operator acknowledgment, and this software does not enforce any hardware safety latch.
- Panic Box FULL mode is not controlled or cleared by this module. The separate Panic Box control design must keep FULL until authenticated offsite human ALL CLEAR.
- The observer can fail or be stopped. An independent monitor of the monitor, secure telemetry, and offline-alert tests are still required.
- For synthetic tests, only. **Do not connect to or install on the AJAX-owned computer.** Future validation must use the user's personal home Windows desktop and phone.

## Test in isolated local Python environment

Requires Python 3.10+ standard library; place this module alongside `external_watchdog.py`, `status_contract.py`, and `wav_growth_probe.py`.

```sh
python -m unittest -v test_dual_source_health.py
python -m unittest discover -v
python -m compileall -q .
```

Example single-snapshot check (will be `UNCONFIRMED`, never healthy):

```sh
python dual_source_health.py path/to/SIMULATED_status.json path/to/SYNTHETIC.wav --once
```

Exit code 0 means an unconfirmed one-shot check completed, not a passing recording. Exit code 2 indicates other result; no equipment action occurs.

## Synthetic fault coverage

First-sample caution, dual-progress observation, WAV stall while status claims progress, status stall while WAV grows, microphone disconnection, writer failure, callback stall, missing/corrupt status, missing WAV, replayed heartbeat, latched faults, segment rollover, session-ID change, completed-session caution, output privacy, and **90-minute accelerated virtual-time growth followed by a simulated writer error**. The accelerated run lasts <1 second of wall-clock time and is not a 90-minute physical test.

## Next personal-home-desktop acceptance step

1. Preserve the October 27 originals; create read-only analysis copies and SHA-256 inventory before tests.
2. Confirm the recorder's active WAV can be read without locking or interfering with the writer.
3. In a **disposable** home session, compare observed file growth to recorder logs and microphone callback counters. Do not change the running recorder to satisfy this prototype.
4. Deliberately stop a disposable recorder run; confirm independent detection of stalled frames and stale status, then inspect the originals separately.
5. Later add authenticated live telemetry, independent power/communications failure testing, and phone-only read-only UI. **Do not treat static JSON or offline HTML as live status.**
