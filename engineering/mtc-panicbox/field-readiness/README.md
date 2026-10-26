# VEIL MTC / Panic Box — external status watchdog prototype v0.1

**October 26, 2026 | SIMULATED metadata only | NO live recorder integration**

This is an independent, read-only Python 3.10+ process that consumes **the existing v0.2 simulated status contract**. It does not modify the MTC recorder, Panic Box state, WAV files, images, or logs. It makes **no network connection** and sends **no phone alerts**. It is intentionally not installed or tested on any employer-owned machine.

The producer is **not implemented**. A future recorder may atomically replace a JSON snapshot in a local, access-controlled directory. Until a trusted producer exists, all snapshots and results are synthetic and can be forged. The watcher compares two advancing snapshots and rejects missing, malformed, oversize, symlinked, or replayed snapshots. A local monotonic timer marks the source stale after 20 seconds without a changed snapshot. A changed snapshot with unchanged bytes/callback counts triggers the existing v0.2 contract alarms. If the recorder crashes or stops publishing, the independent watcher can report missing updates **while it itself remains running**. It cannot detect its own crash, a dead host, forged snapshots, actual WAV sample integrity, or failed offsite delivery. For these, an independent remote receiver/power path and physical tests are required.

Run offline from this folder (home PC or isolated test environment only):

```sh
python -m unittest -v test_status_contract.py test_external_watchdog.py
python external_watchdog.py path/to/SIMULATED_status.json --poll-seconds 5
python external_watchdog.py path/to/SIMULATED_status.json --once
```

`--once` cannot establish progress; it should report `UNCONFIRMED` or an alert. JSON status prints to stdout; no files are written. The code does not contain ALL CLEAR or any hardware-control capability. A Panic Box FULL snapshot with a lost link remains FULL and produces a warning.

**Known limitations:** snapshots are neither authenticated nor cryptographically bound to actual evidence. Local file writes must be atomic in the future producer to avoid partial reads; partial reads currently fail closed. File size and callback counters can advance while acoustic capture is invalid, so an independent microphone, WAV frame integrity, channel/silence checks and blinded review are still necessary. Windows-specific process/service persistence, OS permission model, power-loss behavior, secure phone telemetry and alert transport are not tested.

**Next physical milestone (PERSONAL HOME WINDOWS ONLY):** connect a read-only snapshot exporter to the existing recorder without changing its audio path, then run a 65-minute or overnight test with deliberate microphone disconnect, simulated disk-full and recorder-process termination. Independently confirm the original WAVs remain recoverable and unmodified, and verify the watcher fails closed on each fault. Do not run this on the AJAX laptop.
