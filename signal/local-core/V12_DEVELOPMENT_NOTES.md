# SIGNAL v0.12 — operator-controlled local conversation continuity

Date: 2026-10-30. Incremental upgrade on v0.11.

## Changes
- `signal_session.py`: validate and atomically write one explicit completed-chat snapshot;
  SHA-256 detects unintentional corruption, not evidence authentication.
- `/api/session`: authenticated GET for snapshot metadata and POST `save|restore|delete`.
- Restore never automatically reloads MTC logs or scanner flags, and preserves existing
  in-memory history if the snapshot is corrupt.
- `signal_face.html/js`: readable panel with explicit buttons and confirmation before
  restoring or deleting. Restored messages are inserted through `textContent`, not HTML.
- `signal_desktop.py`: 150ms lock grace for sequential rapid UI requests, avoiding
  rare false 409 responses after a completed request.
- `test_signal_session.py`: 15 local tests for validation, persistence, HTTP authorization,
  no autosave, deletion, corruption, and evidence context unloading.

## Privacy and boundaries
- Snapshot stored in default profile directory, plaintext, unencrypted.
- No autosave, automatic cloud upload, WAV access, voice capture or saved microphone audio.
- Only last 16 completed alternating messages (8 exchanges), not partial stream output.
- Does not save AI model, instructions, private evidence, research notes or calibration data.
- Stored unverified model statements remain unverified and cannot replace MTC validation.
- Tested direct HTTP requests and isolated browser simulation; **not yet Windows tested**.

## Verification
- `python -m unittest discover -p 'test_*.py' -q`: 137 tests passing x3.
- `node --check signal_face.js`: passes.
- Chromium frontend simulation: demo chat, click save, restore, delete; no JS exceptions.
- Direct Chromium localhost navigation blocked by execution-environment policy.
- `START_SIGNAL_DESKTOP.bat` real Ollama & speaker, and `START_SIGNAL_FACE_DEMO.bat`
  on the user's Windows desktop must still be tested before production use.

## Human acceptance sequence
1. Extract into a NEW folder; leave v0.11 available.
2. Run `CHECK_SIGNAL_SETUP.bat`, then `START_SIGNAL_FACE_DEMO.bat`.
3. Test Save, close/relaunch, Restore, Delete. Check no automatic restoration occurs.
4. Start Ollama, launch `START_SIGNAL_DESKTOP.bat`, run `Test Ollama conversation`.
5. Type a short research question, observe streaming text. Keep voice OFF at first.
6. Enable speech and evaluate naturalness, speaker output and mouth motion separately.
7. Load the verified October MTC session and scanner JSON only by explicit action.
