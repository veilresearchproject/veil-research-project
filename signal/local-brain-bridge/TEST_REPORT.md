# SIGNAL Local Brain Bridge v0.1 — Verification summary
Date: November 2, 2026

- Backend tests: **15/15 passed** with Python 3.13 standard-library unittest and a fake Ollama listener bound to loopback. Covers response routing, status, system instructions, bounded history, origin checks, JSON-only POST, large input rejection, no file exposure, no transcript store, unreachable Ollama fallback.
- Frontend tests: **15/15 passed** with Node v22 VM DOM mocks. Covers scripted mode, VEIL content, privacy, opt-in model activation, model history, failure, reset, TTS, injection as text, no startup requests.
- Chromium smoke: **passed** at 390x844 pixels using `page.set_content`: scripted prompt, typing, check-model unavailable message, reset, zero JS exceptions and zero outgoing requests. Screenshot is in mobile_screenshot.png.
- Limitation: Chromium navigation to http://127.0.0.1:8765 is blocked by this test environment policy (`net::ERR_BLOCKED_BY_ADMINISTRATOR`), so in-browser end-to-end *local model* networking remains unverified. Python HTTP integration tests exercised the actual local bridge with fake Ollama successfully.
- No real Ollama model installed or run; actual Windows desktop hardware compatibility, quality and offline voice support **not yet verified**.
- All generated and tested code is isolated from live VEIL site. No cloud AI calls or subscriptions.