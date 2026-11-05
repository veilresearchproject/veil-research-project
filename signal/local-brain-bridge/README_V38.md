# SIGNAL v34–v38 — Research Extensions Lab (November 5, 2026)

**Status: standalone, review-only development prototype. No v25 installation, public website, or existing GitHub main branch changed. Do not deploy in investigations without an engineering/security review.**

This package extends the v33 local geometric research preview with five modular developments. The animated geometric v33 interface is available through the **Open v33 geometric companion** link in the new v38 dashboard; the new features have their own separate page.

## Five milestones

1. **v34 — Human-approved local memory.** `memory_v34.py` writes approved project facts to `~/.veil_signal_lab/approved_memory_v34.json` in a local JSON file (up to 50 notes, each 500 characters). Each note requires explicit approval, a named operator and a source reference. Notes can be individually deleted after confirmation. No automatic conversation capture, silent AI injection, Internet storage or original-evidence ingestion. This is **not** an encrypted/authenticated multi-user vault; don't enter passwords, health, family or confidential records. The machine operator retains responsibility for filesystem privacy and backups.
2. **v35 — Voice lifecycle.** `voice-core.js` implements explicit speaking/listening/processing/idle and barge-in states with race-sensitive cancellation in the UI. A simulated push-to-talk and typed transcript demonstrate handoff timing. The browser can request device text-to-speech; **there is no microphone recording, recognition, or verified offline voice engine yet.**
3. **v36 — Assignment workflow.** `assignments-core.js` implements manually created, started, submitted and named-human-reviewed assignments. Nothing is executed by the module. The board lives in session memory and its status is not evidence of work being performed.
4. **v37 — Actual local WAV sample screening.** `audio-core.js` parses user-selected RIFF WAVE PCM16 mono/stereo files (8–192 kHz, max 25 MiB/10 minutes), computes RMS energy over 100 ms windows and flags relative energy-change intervals for human audition. Never transcribes, labels EVP, verifies paranormal claims, edits originals or contacts cloud services. Test synthetic impulses only before field validation. Quiet/background noise, compression, playback leakage, AGC and clipping can all create misleading peaks.
5. **v38 — Simulated multi-instrument dashboard.** `dashboard-core.js` displays synthetic MTC, Panic Box and camera statuses, with test-only status changes and explicit simulated exports. There are **no real telemetry adapters, physical alerts, sensor data feeds, or ALL CLEAR controls.**

## Windows trial

1. Unzip into a **new folder**, not into your working v25, v33, or any public website directory.
2. Double-click `START_SIGNAL_V38_LAB.bat`. Requires installed Python 3.9+. No extra Python packages are needed for the app.
3. Open **http://127.0.0.1:8773/** in the same Windows computer. The new Lab Extensions are ready without Ollama.
4. Follow the link **Open v33 geometric companion** to open the animated geometric AI interface served on port 8773. If you later enable local AI, use your already installed `llama3.2:3b` through Ollama; the new app does not install/download models or configure your Quadro GPU.
5. Close with Ctrl+C in the Windows terminal. The original v25 remains untouched. The approved-memory JSON file, if you explicitly save notes, will remain in your home directory until deleted.

## Tests run in development

- New deterministic Node suite: `node test_next_cores.cjs` — **43/43 passed**.
- New approved memory + local HTTP suites: `python -m unittest -q test_memory_v34.py test_lab_http.py` — **28/28 passed**.
- Inherited Python v33 tests (real local HTTP fake-Ollama + readiness): **42/42 passed**.
- Inherited Casebook, fingerprint, correlation, clock, blind-review and v33 UI suites: **127/127 passed**.
- Headless Chromium 390×844 smoke: **passed** for mobile layout, simulated statuses, assignment lifecycle, voice state transitions, explicit memory approval/XSS-safe text rendering, and an actual 16-bit PCM synthetic audio file screened in-browser.
- Inherited v33 Chromium UI smoke: **passed**. `python -m py_compile` on new server and memory module: **passed**.

Tests do **not** establish compatibility with your Windows installation, microphone, speakers, network policy, native voices, real Ollama, real instrument timestamps or evidence retention rules.

## Security/research boundaries

- The server binds to `127.0.0.1:8773` only, with host checks, same-origin checks on memory POST, fixed allowlisted endpoints and 4096-byte memory request limit. Like v33, this remains a single-user prototype, **not safe for LAN exposure or untrusted browser extensions**.
- The approved memory service stores only operator-supplied notes and never supplies them to a model automatically. Human review is self-reported and not cryptographically authenticated. Atomic writes reduce partial-file risk but do not make it a forensic evidence ledger.
- The new v37 analysis happens in the browser, reads user-selected bytes only, and has **no evidence-quality or authenticity certification**. Its timestamps are relative to sample index, not synchronized to other cameras/recorders without separate validated metadata.
- Independent reviewers must see original recordings and acquisition logs, verify clock corrections, retain provenance, and consider mundane explanations. SIGNAL must not claim paranormal proof.

## Future work / on-device gates

- Test voice playback and barge-in with installed Windows voices; choose a real offline English speech recognizer only after measuring CPU/RAM and explicit microphone permission.
- Check local memory write permissions, backups and restore on your Windows profile. Make any proposed AI memory retrieval separately opt-in with clear previews and prompt-injection precautions.
- Test several *synthetic/authorized* WAV clips with differing sample rates, clipping/noise and question playback before reviewing real experimental recordings.
- Provide authenticated reviewer separation and evidence audit trails before real third-party reviews.
- Instrument adapter design only in read-only simulation. Never connect a real Panic Box ALL CLEAR or instrument-control endpoint to an LLM without an independent authorized human safety system.
