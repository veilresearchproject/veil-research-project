# SIGNAL v26 — Geometric Speaking Preview (isolated development)

This is a **new local-only experiment**, not a replacement or an upgrade of the working SIGNAL v25 desktop package. The exact v25 files were not available in the repository; do not overwrite them. The preview builds on the existing `signal/local-brain-bridge` prototype server and is deliberately served at **127.0.0.1:8766** instead of 8765.

## Five development improvements
1. **Geometric form:** faceted cyan/teal core, rotating rings, state transitions, no human face.
2. **Meaningful colors:** blue when entering input, purple when waiting for a model, cyan speaking, magenta humor, amber uncertainty, red errors.
3. **Speech-reactive behavior:** device text-to-speech with preferred English Ryan voice if present, speech-start/stop/boundary animations, caption fallback and race-safe stop. This is event-driven motion, **not** real captured-audio amplitude or perfect lip sync.
4. **Optional local AI:** opt-in same-origin `/api/health` and `/api/chat` via Ollama, bounded session-only history, cancel and clear. Default scripted mode sends no model requests. No instrument controls.
5. **Accessible, tested controls:** caption panel, reduced-motion switch, mobile layout, keyboard focus, no transcript storage, basic reproducible contract/smoke tests.

## Windows desktop preview
Place `v26.html`, `v26_server.py`, and `START_GEOMETRIC_SIGNAL_V26.bat` alongside the existing **`server.py`** in the `signal/local-brain-bridge` development folder; **do not move or replace any v25 files**. Ollama must already be running, with the configured local model installed. You used `llama3.2:3b` in CPU-only mode; preserve your prior Ollama CPU environment if it is still needed.

The `.bat` launcher defaults to `llama3.2:3b`, matching your installed model (unless `SIGNAL_MODEL` is already set). You may instead set `SIGNAL_MODEL=llama3.2:3b` in Command Prompt before running `py -3 v26_server.py` from the folder. Open **http://127.0.0.1:8766/**, choose **Check local model**, then **Enable local AI**. There is no need to stop the existing working port 8765 instance.

Scripted preview also works by opening `v26.html` directly; the local model will deliberately be unavailable in `file://` mode. The v26 preview is **not** tested on your actual Windows desktop yet.

## Verification and limits
`node test_v26.cjs` checks the HTML JavaScript parses, privacy bounds, controls, and core behavior. Browser smoke tests can exercise the scripted mode without any real Ollama model. Full Windows speech voices, real Ollama interaction, accent timing, and device-specific performance require hands-on validation. This prototype has no microphone or speech recognition, no connected sensors, no real evidence interpretation, and no equipment action path. Browser/device voice engines may require internet. Keep original research evidence separate from this test interface.