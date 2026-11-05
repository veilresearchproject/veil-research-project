# SIGNAL v33 — Standalone Local Geometric Research Preview

**November 5, 2026 — review-only development.** This package supersedes the v26–v32 *preview ZIPs* for independent testing. It does **not** replace, upgrade or alter the working v25 Windows desktop installation, which must remain untouched.

## What changed
Unlike the earlier v26–v32 prototype ZIPs, v33 includes its **own Python local bridge server** (`signal_local_v33.py`). It no longer requires copying the original `server.py` from another SIGNAL package. The browser page is `v33.html`; it retains the geometric speaking interface, Casebook observation notebook, local SHA-256 file fingerprinting, timestamp candidate review, clock correction/uncertainty, and blinded-source rehearsal. All browser analysis modules remain deterministic/read-only by default.

The server binds to **127.0.0.1:8772**, responds to only explicitly allowlisted local page/module routes and optional `/api/health` and `/api/chat`. Ollama is always addressed on **127.0.0.1:11434** (or a deliberately configured alternative *port* on the same computer); no public listeners, arbitrary URLs, downloads or cloud endpoints. Typed chat is sent only after the operator selects Enable Local AI. The default is scripted and works without Ollama. Device-provided voices may still require internet independently of SIGNAL, depending on Windows configuration.

## Simple Windows trial (later, when convenient)
1. Extract the v33 ZIP into a **new directory**, separate from every existing SIGNAL/v25 folder. Do not merge it over existing files. No need to locate or copy `server.py`.
2. Keep Ollama installed as before. To use Ollama with the earlier Quadro P5000 issue, your established CPU-only Ollama startup configuration remains external; v33 does not modify it. The default model is the installed `llama3.2:3b`, and no model download is automatic.
3. Double-click **`START_SIGNAL_V33_STANDALONE.bat`**. Open `http://127.0.0.1:8772/` in the desktop browser. You may try scripted mode even with Ollama off. Use Check local model / Enable local AI only when ready. Close the terminal with Ctrl+C to stop the preview.
4. Optionally double-click **`RUN_SIGNAL_V33_TESTS.bat`**. It runs the readiness checker and local tests; no hardware actions. Use `py -3 signal_doctor_v33.py --check-ollama --check-port` to opt in to additional loopback-only checks.

## Verification performed in the development environment
- **26/26 actual Python HTTP integration tests** passed with a fake local Ollama server. Includes real local GET/POST requests, browser-script serving, model-ready probe, protective origin and Host handling, unauthorized equipment-command denial, bounded history/body size, static route allowlist, and fallback when the model is absent.
- **16/16 Python readiness-check unit tests** passed against the standalone package checks.
- Existing six Node suites: 25 Casebook + 15 fingerprint + 23 correlation + 27 clock + 23 blind source-review + 14 v33 UI contract = **127/127 checks**.
- The standalone diagnostic produces `launch_ready=true` when all local files are present. It still cannot guarantee real Windows/Ollama speech or hardware compatibility; those are the next on-device gates.

## Safety and limits
No default persistence of chats or Casebook data, no application-side analytics or cloud API, no camera/microphone capture, no automatic computer control, and no real-device instrumentation. The browser's device text-to-speech may be network-backed by Windows. Ollama is independently installed and must be evaluated under its own logging/privacy policies. User-initiated Casebook/export and fingerprinting may read *only the file the operator chooses*. No source content is sent to AI by default; the Casebook's optional critique still requires a separate explicit sharing action. No research conclusion is automatically accepted as paranormal proof. 

**This remains an experimental, unauthenticated single-operator research preview.** Host and origin checks do not make it safe to expose to LAN, untrusted browser extensions or the public internet. No evidence chain-of-custody certificate, device calibration or blind-study guarantee is implied. Do not merge to the live VEIL site or deploy to third parties without security and scientific review.