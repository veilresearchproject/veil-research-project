# SIGNAL v29 — Cross-source timestamp correlation preview (November 5, 2026)

**Status:** Isolated development preview, not a live deployment. v29 extends the v28 geometric voice/Casebook/fingerprint prototype on a **separate branch**. The working v25 desktop installation and live VEIL website remain unchanged. No paid service or purchase required.

## New tested capabilities

1. **Candidate cross-source alignment** — Compare manual Casebook observation timestamps against a user-selected window of 0–300 whole seconds (default ±5 s), using normalized timezone-qualified ISO dates.
2. **Distinct-source screening** — Only notes with explicit timestamps and *different non-empty self-reported source labels* are considered. Repeated labels are excluded; different labels do **not** prove independent equipment or observation.
3. **Research gaps and explicit uncertainty** — The deterministic report counts missing timestamps, missing source labels and timestamps not confirmed by the operator. It reports candidate delta times but never declares matching sounds, apparatus synchronization, paranormal activity, or causal connection.
4. **Deterministic export** — The user may deliberately download a plain-text report. If the Casebook changed since the report was generated, export refuses until comparison is rerun.
5. **Self-contained local preview** — Keeps Casebook and SHA-256 fingerprinting tools from v27/v28; starts on its own loopback port 8769 rather than overwriting the earlier working desktop program.

## Setup on the existing Windows bridge checkout

Place `v29.html`, `correlation-core.js`, `fingerprint-core.js`, `casebook-core.js`, `v29_server.py`, and `START_SIGNAL_V29_TIMELINE.bat` alongside the existing `signal/local-brain-bridge/server.py`. Do **not** replace or overwrite v25. The ZIP is an **add-on**, not a self-contained Ollama installation or replacement desktop program.

Double-click `START_SIGNAL_V29_TIMELINE.bat`; open `http://127.0.0.1:8769/` on the computer itself. Scripted mode and Casebook analysis need no Ollama. Optional local AI needs Ollama already running; the launcher defaults to installed `llama3.2:3b` only if SIGNAL_MODEL is not already set. It does not download software. Stop its independent server with Ctrl+C in the launch terminal.

## Testing in development environment

- `node test_casebook.cjs`: **25/25 passed**.
- `node test_fingerprint.cjs`: **15/15 passed** with known SHA-256 vectors under Node WebCrypto.
- `node test_correlation.cjs`: **23/23 passed** (timezone alignment, edge thresholds, duplicate source labels, missing timestamps, human verification flags, stable sorting, no mutation, safety copy).
- `node test_v29.cjs`: **15/15 passed** static and architecture checks.
- `python -m py_compile v29_server.py`: passed.
- `python browser_smoke_v29.py`: Chromium 390×844 UI check passed with real deterministic client-side correlation and mocked local module serving. Tested case notes, time window changes, candidate report, local export, stale-report rejection, and unknown timestamps. Browser sandbox prevents actual localhost navigation; real Windows `server.py`/Ollama/browser microphone/speaker integration is **not tested**.

## Scientific integrity and limitations

- This tool compares **only human-entered text metadata**. It does not read sound or video content, inspect camera frames or sensors, measure timing latency, establish instrument independence, or validate a recording's original timestamp. It does not find paranormal anomalies.
- Device clocks may drift; recording pipelines may buffer/delay signals; two differently named sources might be physically the same sensor. Human investigators must examine originals, independently confirm clock synchronization and equipment placements, and assess ordinary explanations.
- File fingerprinting remains capped at 25 MiB and does not establish authenticity, acquisition date or chain of custody.
- Casebook is session-only unless the operator deliberately exports JSON; correlation reports are likewise generated locally on demand. The prototype has no authenticated researchers, automatic cloud upload, autonomous field control or true offline speech-recognition engine.
- Optional local model can receive *descriptions only* after deliberate model enablement, checkbox consent and "Ask local SIGNAL" action; never send evidence files to the model. The deterministic correlation feature does not send notes or results to the model.
- This is a prototype and needs external engineering review plus actual desktop testing before using real case material or deploying to investigators.