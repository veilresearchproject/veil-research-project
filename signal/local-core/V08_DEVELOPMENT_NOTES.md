# SIGNAL Desktop v0.8 — Next steps toward a dependable local research assistant

**VEIL Research Project · October 30, 2026 · prototype, not production software**

This release extends v0.7 without replacing the approved imperfect character face, MTC recorder, or earlier versions.

## Completed in this milestone

- **Operator-initiated setup diagnostics:** checks the *literal* localhost Ollama `/api/tags` endpoint and looks for the configured model name. On Windows, lists installed speech voices and checks whether an offline legacy recognizer can be instantiated. **No model download, speech recording, speech synthesis, internet fallback, or background Ollama polling occurs during diagnostics.** A 'ready' tag is not a real inference test.
- **Operator evidence notebook:** only after an MTC session's JSON logs are loaded, add an observation at an offset in seconds with one of four human labels: known source, needs review, cause not identified, or instrument issue. Each note includes a UTC write timestamp, and is appended to a dedicated JSONL file in `%LOCALAPPDATA%\VEIL\SIGNAL\review_notes`. No recordings or original evidence logs are edited; no AI classification is assumed. Local records are **unencrypted, unauthenticated, and not tamper-proof**. Back them up securely as needed.
- **In-interface readiness panel** and **review notebook** added to SIGNAL's existing local desktop interface, with the same session token and loopback-only API protections as v0.7.
- **Safer error handling and tests:** malformed times, arbitrary labels, unsafe filenames and symlinked notebook files fail closed. Distinguish system-reported outcomes from actual acoustic analysis.

## Validation

- **72 Python tests passed** using temporary files and mocked external capabilities, including the previous 55 tests, 7 new diagnostics tests, 7 notebook tests, and 3 HTTP endpoint tests.
- JavaScript syntax checked with `node --check` (Node used only for development verification, not required to run SIGNAL).
- Actual user WAV recordings are **not** bundled, opened or modified. Previous session JSON logs alone cannot prove that a voice was audible or that no anomalies occurred.
- Browser rendering was not validated in this environment due to browser security restrictions on local pages; an on-device Windows browser walkthrough remains required.

## Safety and reality check

- The face is still still-image expressions with illustrative mouth motion, not accurate phoneme synchronization.
- Speech recognition is one-shot and explicitly opt-in; no wake-word or passive listening. Recognized text must be reviewed before sending.
- Local Ollama may hallucinate or misunderstand records. The program cannot independently listen to audio or determine a paranormal source.
- No remote control, research-center hardware privileges, Panic Box reset, or unattended autonomous authority.
- The live model, speaker sound, and microphone recognition remain unverified on the user's Windows desktop.

## Hands-on acceptance checklist

1. Run `CHECK_SIGNAL_SETUP.bat`. Confirm Python, local Ollama and local voice capabilities.
2. Open scripted visual demo and check face expressions/motion still switch.
3. Start actual Ollama with a locally installed model. In live interface, run one harmless short question and confirm coherent reply.
4. Enable Windows voice, test one short spoken reply, verify Stop interrupts it. If the voice sounds unnatural, turn movement off and review separately.
5. Load the MTC Oct 27 session folder, confirm 90-minute summary, then save a manually verified door-closing note at the correct offset.
6. Confirm notes are saved separately and original MTC folder byte-for-byte unchanged.
7. Keep this version separate from v0.7 until all hands-on checks pass.
