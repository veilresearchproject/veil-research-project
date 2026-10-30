# SIGNAL Desktop v0.9 — Read-only MTC scanner bridge

VEIL Research Project | October 30, 2026 | Local engineering prototype

## Purpose

Connect SIGNAL's existing v0.8 evidence notebook to the separate VEIL MTC Local Audio Review v0.3 scanner output without transferring or scanning large WAV recordings. This milestone adds read-only interpretation of **machine-selected acoustic candidates**, not EVP, voice or paranormal detection.

## How to use on Windows

1. Extract the entire v0.9 ZIP into its own folder; leave all older versions and original recordings alone.
2. Run `CHECK_SIGNAL_SETUP.bat` to check Ollama, Windows speech and offline recognizer. This does not turn on the microphone, speak, install software, or contact a remote AI.
3. Start Ollama locally and double-click `START_SIGNAL_DESKTOP.bat`. If Ollama is not ready, you can still test the clearly labeled scripted interface using `START_SIGNAL_FACE_DEMO.bat`.
4. Expand **Load a local MTC evidence log** and enter the session folder containing `session_result.json`, `session_metadata.json` and `events.jsonl`. This is a read-only verification step.
5. Run our **existing** VEIL MTC Local Audio Review scanner v0.3 on the same session if you have not already. It generates `review_summary.json` under your Windows home folder's `VEIL_Reviews` directory, along with its separate waveform playback viewer. The WAVs remain on your computer.
6. Expand **MTC scanner flags — group and review** and select **Find latest matching report**. Or paste a path ending in `review_summary.json` and select **Load flags**.
7. Review each candidate in the separate MTC waveform viewer. Click **Note this time** beside an event in SIGNAL to prefill the observation notebook; classify the event and save your note. The notebook is separate from all source research data.
8. Ask SIGNAL a question about the loaded review findings. His local model will receive a compact summary of **timestamps and acoustic flags**, not any raw audio or scanner-provided prose.

## Engineering behavior

- Merges only *overlapping or touching* candidate time ranges, not every close-by noise. Maintains original scanner indices; does not erase or merge any original detector entries on disk.
- Rejects a report from the wrong session, unsupported versions, bad timestamps, inconsistent duration or segment counts, corrupt JSON, symlinks, and oversized reports.
- The latest-report finder is opt-in and searches only immediate child folders of `~/VEIL_Reviews`. It does not scan all drives.
- Stores the imported review only in current program memory, clears it when the MTC session changes, and never modifies WAVs, scanner reports or MTC logs.
- Independent human observations remain separated in the existing JSONL notebook.
- This is **not** proof of audio integrity, a paranormal event or source identification; it does not listen, recognize speech or infer causes.
- When you stop SIGNAL, unsaved imported review context is gone. Written notebook observations remain in `%LOCALAPPDATA%\VEIL\SIGNAL\review_notes`.

## Validation

- 88 Python automated tests pass (existing SIGNAL core and local HTTP checks, plus scanner report validation, duplicate grouping, latest-match search and conversation context tests).
- The existing v0.3 MTC scanner generated a synthetic WAV/audio event report, and the SIGNAL importer successfully read it. This used invented test sound, not the real overnight recording.
- A simulated Chromium UI test passed: 3 scanner flags displayed as 2 grouped review windows, clicking a window populated 31.5 seconds in the notebook, and chat still functioned without JavaScript errors.
- The test browser was unable to navigate directly to localhost (`ERR_BLOCKED_BY_ADMINISTRATOR`), so actual live local-server rendering needs Windows verification.
- No genuine Ollama model, Windows speaker or physical microphone was tested in this release.

## Next Milestone

On the Windows desktop, check real Ollama inference, voice output, and microphone compatibility. If successful, consider a secure, user-approved deep link between SIGNAL's selected timestamp and the existing waveform viewer. Avoid merging audio-source and interpreted notes prematurely.
