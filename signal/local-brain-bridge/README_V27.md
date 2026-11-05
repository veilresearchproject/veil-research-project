# SIGNAL v27 — Geometric Casebook prototype (November 5, 2026)

**Status:** Isolated review prototype. This does **not** install, merge, deploy, overwrite, or modify the user's working v25 Windows desktop version. SIGNAL v26 also remains unchanged. No purchases or cloud subscriptions.

## Development milestones delivered

1. **Case intake** — Create a session-only case; add up to 30 source-description observations (audio, video, image, sensor, witness, other), optional source label and optional explicitly timezone-qualified observation time. This is human-entered metadata, **not analysis of original evidence**.
2. **Controls and gaps** — Four explicitly self-reported checklist fields per observation: original preserved, timestamp verified, alternatives considered, independent corroboration checked. The deterministic summary labels gaps as "not confirmed" instead of claiming false or abnormal evidence.
3. **Human-review gate** — A researcher may mark a case "needs more information" or "reviewed without conclusion" using a *self-reported* reviewer name. There is no "verified paranormal" outcome. Adding another observation resets review to unreviewed. No reviewer authentication is claimed.
4. **Local import/export** — Browser user-initiated JSON download/import, strict schema validation, size limits, text rendered safely (never HTML); no automatic persistence or cloud upload. Export is a case description, **not chain of custody or tamper-evident authentication**.
5. **Optional AI critique** — When the user explicitly enables local Ollama **and** checks case-sharing consent **and** presses "Ask local SIGNAL", the prototype passes a bounded <=800-character description prompt to the existing localhost-only bridge. It does not send files, sensor streams or evidence samples. The model can suggest ordinary explanations and additional checks; it cannot authenticate or decide a result.

## Windows setup for an existing SIGNAL bridge checkout

The v27 files should be placed beside the existing `server.py` in the project's `signal/local-brain-bridge/` directory. **Do not copy them over v25**. The preview uses new filenames and a new port:

- `v27.html`, `casebook-core.js`, `v27_server.py`, `START_SIGNAL_V27_CASEBOOK.bat`.
- Ollama is optional. If using the local model, keep the currently working **CPU-safe Ollama process** running on `127.0.0.1:11434`, with model `llama3.2:3b` already installed. The Windows launcher sets `SIGNAL_MODEL=llama3.2:3b` only if no override is set; it does not download the model.
- Double-click `START_SIGNAL_V27_CASEBOOK.bat`. Open `http://127.0.0.1:8767/` **on that computer**. Use scripted mode before enabling the model.
- Do not rely on older v25 commands or override the old 8765 port. Stop v27 with Ctrl+C in its separate terminal.
- This standalone download ZIP **does not include** the existing `server.py`, the Ollama model, or v25. It is an add-on, not a self-contained replacement.

## Testing (development environment)

- `node test_casebook.cjs` — **25/25 passed**, deterministic metadata schema / controls / import/export / review / LLM input tests.
- `node test_v27.cjs` — **15/15 passed**, UI contract / no-network architecture / CSP / XSS / local server integration checks.
- `python -m py_compile v27_server.py` — succeeded.
- `python browser_smoke_v27.py` — Chromium 390×844 UI test **passed**: scripted chat, case entry, safe text rendering, missing controls, human review, export and import, explicit local AI mode + case consent, and mocked AI response. Browser runtime here blocks localhost HTTP navigation, so the test inlines the *same Casebook core* and stubs local APIs. **Real browser-to-server, Ollama responses, Windows voice behavior, and physical hardware are not verified.**

## Guardrails and limitations

- No internet, browser cookies, analytics, automatic logging, or automatic note storage. Export is explicit and produces a JSON file on the operator's device; the operator controls retention.
- Voice uses the user's device speech-synthesis service, which may or may not be offline. No voice recognition, microphone recording, camera input, actual anomaly classification or instrument command is implemented.
- No evidence-file ingestion, file hashing, access controls, tamper-evident chain of custody, or authenticated investigator approval. The text-only system cannot establish evidence authenticity or paranormal cause.
- If model mode is enabled, notes are shared **only on the separate action** using the same-origin loopback API. A locally installed model may still make factual errors, or be vulnerable to prompt injection inside the descriptions. Never put sensitive subject data in a prototype.
- The input prompt is capped at 800 characters by the local bridge. Later entries may be omitted, and the prompt clearly indicates this. Do not use an AI reply as a research finding.
- Windows desktop test and a real security review are required before introducing real experimental data or field deployment.