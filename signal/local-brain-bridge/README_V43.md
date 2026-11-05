# SIGNAL v39–v43 — Unified case workflow (November 5, 2026)

**Status:** isolated review-only software development prototype. Builds on the v34–v38 laboratory preview and v33 faceted geometric companion; does **not** install over the working SIGNAL v25, change the VEIL website, send data to a cloud model, or communicate with any research instrument. This is not an authenticated forensic case-management system.

## The five new tested development milestones

1. **v39 — Unified local case workspace.** Start one active case in the new v43 page. Keep candidate markers, human notes and assignments together. If a case already has a WAV, attaching a different file is refused until a new case is intentionally started. Existing v34 memory, v35 voice demonstration and v38 simulated station dashboard remain accessible in the same page.
2. **v40 — WAV provenance metadata.** Operator selects a supported WAV (16-bit PCM mono/stereo, 8–192 kHz, <=25 MiB, <=10 minutes). A real local in-browser SHA-256 digest is calculated with the browser's WebCrypto; selected sample bytes undergo existing deterministic RMS energy screening. Only metadata, fingerprint and up to 80 candidate markers are retained in the session. Original WAV bytes are never included in exported packets or sent to Ollama; the number of omitted markers is reported. File metadata/fingerprint cannot establish original provenance or authenticity.
3. **v41 — Human-reviewed amplitude-marker queue.** Select a candidate interval and enter a named reviewer and rationale. Choose **needs listening**, **ordinary explanation possible**, or **inconclusive**; there is no “paranormal verified” status. Reviews cannot be silently overwritten, and a status change is not proof that someone actually listened to the original. Reviewer identity is self-reported and unauthenticated.
4. **v42 — Manual research handoff.** From a reviewed marker, deliberately create a **manual assignment** in the existing v36 assignment board. Task descriptions refer to file-relative times, abbreviated SHA-256 fingerprint and independent checks. The app performs no autonomous analysis from assignment creation, does not send instrument commands, and cannot accept a task without the existing human review workflow. A separate optional button fills—not automatically speaks—the existing v35 voice-demo text with a cautious case summary.
5. **v43 — Reproducible session packet and independent preview.** Deliberate JSON export/import of the case, manual assignments and explicitly *simulated* station state; payload includes a SHA-256 integrity digest for detecting changes. A modified payload is rejected before import. **This digest is not a digital signature, identity verification, forensic evidence certificate, or chain of custody.** A separate text report provides methods, marker times and uncertainties. Approved long-term memories, chat, raw WAV files and original sensor records are explicitly excluded. Import requires user confirmation, and will replace only the current ephemeral case/tasks/simulated stations.

## Windows instructions (when convenient)

1. Extract the zip into a **new directory**, never into v25 or another SIGNAL installation.
2. Double-click `START_SIGNAL_V43_UNIFIED.bat` (requires Python 3.9+). This binds to **127.0.0.1:8774** and does not change Windows settings or install anything.
3. Open **http://127.0.0.1:8774/** in the same PC's browser. Use **Start new case**, select WAV under the v37 panel, then **Attach & fingerprint selected WAV** in the new workspace. The SHA-256 tool requires a secure browser context (localhost qualifies in modern browsers).
4. Review any amplitude markers with a human explanation. A separate button creates a manual assignment. A different button can prepare text for the voice demo. JSON export/import is deliberately manual.
5. The link **Open v33 geometric companion** provides the faceted speaking personality and optional local Ollama on this same loopback server. It remains a separate page; the v43 workspace does **not** automatically send case data into the AI or its conversation history.
6. To stop, press Ctrl+C in the console. The v25 local baseline should remain untouched throughout.

The default model setting remains the user's existing installed `llama3.2:3b`, with Ollama running separately (CPU-only workaround remains external). Scripted and deterministic research features work even if Ollama is unavailable. Browser/device-provided TTS might not be offline, so verify voice privacy before sensitive work.

## Tests performed in the development environment

- New workflow/packet core: `node test_workflow_v43.cjs` — **32/32 passed**, including SHA-256 known vector, malformed input, unauthorized transitions, tampered handoffs and source isolation.
- Local HTTP: `python -m unittest -q test_local_v43.py` — **12/12 passed** using an isolated 127.0.0.1 server, no real Ollama. Fixed static routes, original memory safeguards, Host and Origin denial, no instrument endpoint.
- Chromium browser smoke: `python browser_smoke_v43.py` — **passed** with synthetic PCM WAV, actual deterministic local energy screening, manual marker review, assignment, export/import, tamper rejection, and 390 px responsive layout. Browser test sandbox blocks loopback/HTTPS navigation, so its WebCrypto digest was *mocked for browser UI flow*. **Actual SHA-256 correctness was tested separately with Node WebCrypto and the published `abc` vector.** Screenshots show the simulated test UI, not a true Windows deployment.
- Re-run inherited v33/v38 Python and Node suites separately; they do not validate actual Windows microphone/TTS, Ollama, sound playback, instrument calibration, authentication or field casework.

## Research and security limits

- Session data is not automatically saved. User-approved memory remains in the existing v34 local service and is not included in session exports. If the operator explicitly exports JSON, it becomes an unencrypted local file; treat it accordingly.
- Filename metadata is operator-selected and has no acquisition chain of custody. SHA-256 only verifies bytes at the time they were hashed. The operator must retain source files separately and use their own evidence policies.
- Energy peaks reflect RMS amplitude, not transcribed words, claimed EVPs, paranormal activity, or event causation. Time offsets are relative to the WAV and must never be assumed synchronized to any independent clock.
- Simulated Panic Box/MTC/Camera statuses are marked synthetic, have no live hardware connection, and include **no ALL CLEAR** or dangerous control endpoint.
- Human reviews and assignment approvals are self-reported, not authenticated. Do not use for sensitive investigations or public third-party evidence service until security, retention, consent, independent review and forensic provenance controls are built and audited.
- The Windows launch/real Ollama/browser hardware roundtrip still requires a separate on-device acceptance test. **Do not merge or publish without explicit approval.**
