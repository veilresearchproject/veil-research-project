## Update — v0.7 (October 30, 2026)

The existing desktop now supports subtle speaking-activity facial movement and a silent Preview face movement control. Mouth poses are illustrative and not accurate phoneme lip sync. System Reduce Motion accessibility settings are respected. For details, see MOTION_ANIMATION.md.

# SIGNAL — Desktop Face Alpha v0.5

**VEIL Research Project | October 30, 2026 | local Windows engineering prototype**

This adds an **optional graphical character interface** to the same Python SIGNAL local core used in v0.3. It does not replace MTC recording or the existing VEIL website. The six headshot states were cropped from SIGNAL's approved character expression board (the imperfect, bespectacled, messy-haired researcher).

## Start here: no AI model needed

1. Extract the entire ZIP into a folder such as `C:\VEIL\SIGNAL_Desktop_v0_4` (do not run individual scripts from inside the ZIP).
2. Confirm Python 3.10+ is installed (`py -3 --version` in Command Prompt).
3. Double-click **START_SIGNAL_FACE_DEMO.bat**. A browser window should open to an address beginning with `http://127.0.0.1:`.
4. Test the character's expressions and text interface. The top banner says **SCRIPTED VISUAL DEMO**. This is **not a real AI conversation**.
5. Try **Enable voice**. It uses Windows' installed speech voices through the existing `signal_voice.py`. Voice starts OFF and requires an explicit click. Stop speaking cancels the local speech process.

## NEW in v0.5: Optional microphone (offline, one phrase)

Click **Start listening** in the conversation input row, speak a brief phrase, and review the resulting text **before clicking Send**. The microphone is off at startup, and **Stop listening** immediately cancels an active attempt. It never records an audio file or streams audio to the AI. Requires a locally installed Windows speech recognizer and microphone; not all Windows setups have the legacy offline recognizer. If unavailable, the rest of SIGNAL continues to work by typing. [Read microphone privacy and limitations](MICROPHONE_PRIVACY.md).

## Live conversation with local Ollama

1. Install and run Ollama for Windows locally, using your chosen locally downloaded model. The configured default is `llama3.2:3b`; change `MODEL` in `signal_core.py` only if you intentionally use another local model. The model download uses internet once; subsequent text inference runs locally.
2. Double-click **START_SIGNAL_DESKTOP.bat**, which uses the **existing** `signal_core.Assistant` and `LocalModel` classes. This is not the scripted demo.
3. Type a question and press **Send** or Enter. Replies appear next to SIGNAL's face. Enable voice if you want to hear them.
4. To load your overnight MTC log, expand **Load a local MTC evidence log** and paste the full session-folder path, or type `/mtc "C:\path\to\session"` in the chat. SIGNAL checks the three JSON logs read-only, then places a bounded summary in conversational context.
5. Close the black command window (Ctrl+C) to stop the local server. **Do not expose it on a public network.**

## Exactly what is implemented

- Approved SIGNAL portrait with 6 expressive stills (attentive, analytical, amused, curious, focused, reassuring), plus gentle motion and voice-activity animation. **This is not phoneme-synchronized lip movement.**
- Actual conversation calls the previously tested local Ollama connection. **Requires a running local model and enough PC resources.**
- Opt-in Windows speech via existing Windows System.Speech; supported controls: enable/disable, rate, and stop speaking.
- Read-only MTC session log load; original WAV and logs remain untouched. Optional one-shot offline Windows microphone dictation (never auto-submits), but no continuous listener, camera, automatic EVP classification, speaker cloning or safety-critical device control.
- Local-only HTTP service binds `127.0.0.1` to an ephemeral port. No remote fallback. Exact allowlist of browser files; random per-launch request token and origin checks; no third-party CSS, fonts, libraries or scripts. Your typed messages are not persisted automatically; only an explicit operator-selected conversation snapshot is saved locally.
- Browser expression states are selected by simple keyword rules and speech-process activity; they **do not indicate actual emotions, perceptual understanding, or human presence**.

## Known limits

- A microphone can now transcribe one phrase for review. This is NOT continuous hands-free chat, wake-word listening, or robust hands-free operation.
- Local Windows speaker output and live Ollama latency **have not yet been tested on your actual Windows desktop**. Python unit tests and a browser UI simulation do not substitute for the hardware test.
- The visual demo shows scripted sample replies, clearly labeled. Research decisions require independent review. Never use SIGNAL to clear a Panic Box alarm.
- This software is a single-user engineering prototype, not a hardened, multi-user or internet-exposed service. Keep confidential evidence out of it until permissions, storage protection, and retention rules are implemented.

## Verification commands

From the extracted folder in Command Prompt:

```bat
py -3 -m unittest -v test_signal_core test_mtc_evidence test_signal_mtc_integration test_signal_voice test_signal_desktop test_signal_listen
```

**Development verification:** 49 automated tests passed (previous 39 + 8 push-to-talk engine tests + 2 new loopback endpoint tests). Browser UI elements, demo text flow, expression switching and voice-toggle controls passed a simulated browser test with no JavaScript errors. The production local HTTP service was separately exercised by Python HTTP tests. WAV/audio waveform playback and actual Windows audio hardware were not tested as part of this version.

**Recommended next acceptance test on your desktop:** Demo opens → voice plays → stop interrupts speech → live Ollama answers → load MTC session → confirm actual log summary; then evaluate expression timing and accessibility before merging GitHub changes.

## v0.7 facial motion refinement
The artificial dark mouth slit and rapid full-face cycling were removed. Use Motion: subtle / Motion: still under the portrait. Our next real-world step is to launch Ollama and verify voice playback with this visual interface.

## v0.9 — Local setup check and manual MTC review notebook

Run `CHECK_SIGNAL_SETUP.bat` before attempting Ollama. This tests the local model list and Windows speech component availability without activating the microphone. See `V08_DEVELOPMENT_NOTES.md` for detailed validation and limitations. The interface adds a **Local readiness check** and a separate **Investigator observation notebook** for manually classified MTC timestamps. Notes never overwrite raw evidence.

### v0.9 — local audio scanner bridge

After verifying MTC session logs, expand **MTC scanner flags — group and review**. Use **Find latest matching report** to select the latest compatible existing `~/VEIL_Reviews/*/review_summary.json`, or paste the file path. The imported acoustic candidate time windows are grouped when overlapping. You can select a group to prefill the existing notebook, but you still need to listen in the **separate** MTC waveform viewer and identify possible ordinary causes. See `V09_DEVELOPMENT_NOTES.md`.

## Update — v0.10 (October 30, 2026)

**New: one-click local Ollama model check** (under *Local readiness check*). It sends a fixed short evidence-limits question only after you click the button. The test does not start the microphone or speech, change chat history, or access MTC evidence.

**New: export investigator review packet** (under the MTC review controls). With a verified MTC session loaded, click *Save structured JSON* or *Save printable report*. The packet includes the read-only log summary, any matching imported scanner review windows, and **all** human notes for that session. JSON has a packet-content SHA-256, and printable HTML includes the fingerprint and explicit limitations. Source WAVs are not hashed or altered, and neither file represents a forensic authentication or automatic finding.

Read `V10_DEVELOPMENT_NOTES.md` for the Windows acceptance checklist. If Ollama does not start or the new interface misbehaves, revert to the archived v0.9 ZIP. This version has no paid API, subscriptions, or automatic remote connections.

## Update — v0.11: Progressive local replies, explicit stop and research-safe completion

When the configured Ollama model supports local streaming, regular chat messages
arrive incrementally. The interface clearly labels text as **partial and unverified**
until Ollama returns its terminal completion signal. Completed replies are kept
in this session's existing 16-message in-memory history; interrupted replies are
not saved to history and do not trigger speech. Slash commands still use the
original authenticated non-streaming route. Scripted demo mode never claims live
AI streaming.

**Stop reply** sends an authorized cancellation signal outside the long-running
model lock. It also stops receiving new text in the browser. Model-network cleanup
may take until Ollama produces the next token; this is a best-effort stop and
not a remote hardware emergency stop. Cancelling a reply is different from
**Stop speaking**, which interrupts already-running Windows speech output.

The stream is returned as bounded local-only NDJSON. Text is displayed with
`textContent`, not evaluated as HTML. Same per-launch request token and host/origin
checks as other endpoints. There is no cloud fallback or automatic logging of
conversation content. See `V11_DEVELOPMENT_NOTES.md` and run `RUN_SIGNAL_TESTS.bat`.


## Update — v0.12: Optional local conversation continuity

The **Conversation continuity** panel provides three explicit choices:
**Save current conversation**, **Restore saved conversation**, and **Delete saved conversation**.
There is no autosave or auto-restore. SIGNAL saves at most the last eight *completed*
question-and-answer exchanges to a local plaintext JSON file in the current Windows
user profile (typically `%LOCALAPPDATA%\VEIL\SIGNAL\conversation_snapshot.json`).
The file is not encrypted and is **not** an evidence archive: do not save passwords,
private evidence, sensitive personal details, or investigator observations as chat.
Original MTC WAVs, log files, imported scanner flags, manual notes, microphone recordings,
API tokens and optional memory facts are not included. The saved conversation is background
context only and can contain unverified model text; independently reload MTC data when needed.

Restore requires an operator confirmation, replaces the in-memory chat, and explicitly
unloads MTC and scanner context to avoid accidental cross-session claims. Delete removes
only the saved snapshot, not the current chat or separately stored evidence notes.
Invalid/corrupt/oversize snapshots are rejected before existing chat is changed. Atomic
file replacement reduces half-written saves. SHA-256 checks accidental corruption, not
adversarial tampering; the local file is not signed. No cloud synchronization is attempted.

The local desktop HTTP server also gives a short 150ms grace period for back-to-back
requests to avoid spurious 'busy' results after another response has already finished.
The operator's Stop reply remains responsive while generation is active; the system does
not permit saving during an incomplete generation.

**Verification:** 137 tests passed in three consecutive full-suite runs; an isolated
Chromium UI simulation tested save, restore and delete with mocked replies. Windows/Ollama,
Windows speech, and local microphone hardware are still unverified on the user's PC.


## Update — v0.13: Choose an installed local model

Use **Choose an installed local model** to list and select an eligible Ollama model
already on this PC. Selection lasts for this run; it does not download anything.
A confirmed change starts a new chat and unloads research context. Saved files
are unchanged. See `V13_DEVELOPMENT_NOTES.md` for acceptance tests and limits.


## Update — v0.14: Responsive audio controls

Stop speaking, Disable voice and Stop listening no longer wait behind a slow
model reply. Windows speech-process updates are synchronized. A failed microphone
stop/status request leaves a visible uncertain state and a retry control. A new
Test voice button uses the existing opt-in local speech test. Read
`DESKTOP_TEST_STEPS.md` and `V14_DEVELOPMENT_NOTES.md` before real-PC acceptance.


## Update — v0.15: Waiting status and cleanup feedback

Local replies and model tests now show elapsed waiting time. After an interrupted
stream, input remains disabled until the server reports cleanup finished. Timeout
messages distinguish slow responses from an unavailable server. See
`V15_DEVELOPMENT_NOTES.md`; elapsed time is not a completion estimate.


## Update — v0.16: Checked Start Here menu

Extract the full release and double-click `START_HERE.bat`. A checked menu offers
the demo, live assistant, setup check, automated tests and desktop checklist.
Nothing installs, downloads or activates audio automatically. For source builds,
`build_signal_release.py` generates the byte manifest and deterministic Windows
ZIP. Read `V16_DEVELOPMENT_NOTES.md` for validation and hardware limits.


## Update — v0.17: Interrupted-question recovery

Submitting no longer immediately clears the editor. Failure or interruption keeps
a tab-local recovery copy. Restore fills the editor without sending, and successful
manual retry clears the matching copy. Confirmed model/chat resets clear old draft
context. See `V17_DEVELOPMENT_NOTES.md`; no automatic retry or disk storage is added.
