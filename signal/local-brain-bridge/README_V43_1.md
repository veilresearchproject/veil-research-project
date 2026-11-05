# VEIL SIGNAL v43.1 — Integrated Geometric Research Assistant

**November 5, 2026 | Isolated, review-only Windows preview**

This is an incremental refinement of SIGNAL v43, not a replacement for the **working v25** desktop installation. It adds the geometric speaking assistant **inside the research workspace**. It retains the v43 deterministic local WAV energy screening, note and assignment workflow, checked JSON import/export, approved memory UI, and **simulated-only** multi-instrument board.

## New capabilities

1. **Read-only case briefing:** Uses locally validated counts, without reading private case titles, descriptions, file names, raw audio, or approved long-term memories aloud. Click *Brief me*; no microphone is used.
2. **Next unreviewed candidate:** Identifies and selects the earliest unreviewed *file-relative* WAV energy marker. Never labels a voice, EVP, or paranormal event.
3. **Research and synthetic-device status:** Gives aggregate status of **manual** assignments and explicitly **simulated** MTC, Panic Box and camera entries. This is not equipment telemetry and supplies no device controls.
4. **Geometric voice interface:** Faceted SIGNAL animates on browser TTS events. Voice requires separate explicit device-voice consent and a click; speech can use vendor networks depending on installed Windows voices. Speech stops when you remove consent, leave the page, stop the voice, or change the case. Text remains visible and reduced-motion is available.
5. **Optional local Ollama chat on the same screen:** Expand the Ollama section, explicitly enable the installed model, and type a question. Only that typed question plus bounded (12 message) chat history goes to the existing loopback `/api/chat`; no case, WAV, assignments, approved memory, or instrument data is appended automatically. Disabling/clearing the model, changing local research records, or leaving the page resets this context. Local LLM claims are not validated evidence.

## Windows desktop trial

1. **Create a fresh folder**. Extract the entire `SIGNAL_v43_1` folder there; do **not** copy it over v25 or another version.
2. Double-click **`START_SIGNAL_V43_1_INTEGRATED.bat`**. Requires installed Python 3.9+; standard Python library only for the server. The preview listens only on **127.0.0.1:8775**. No cloud API keys, purchases, administrator rights, internet downloads, or instrument drivers are needed for deterministic features.
3. On the same computer open **http://127.0.0.1:8775/**. Start with **Brief me**, **Next unreviewed**, and simulated statuses. Case handling and WAV analysis operate locally. The selected file fingerprint step requires a modern secure-context browser (localhost qualifies).
4. To try optional AI, first start your already installed Ollama separately. If your older NVIDIA card still needs the previous workaround, keep its known CPU-only Ollama startup configuration; this package does not change it. The default configured model is **llama3.2:3b**. Expand *Optional local Ollama conversation*, click *Enable local AI*, then type a question yourself.
5. Optional voice is browser-provided and **may not be fully offline**; keep it unchecked for sensitive casework until your voice privacy is independently verified. Windows microphone and live hardware are not connected.
6. Stop the preview with Ctrl+C in its launch terminal. The separate v25 installation remains unchanged.

## Development verification

- `node test_briefing_v431.cjs` — 30/30 deterministic new checks passed (no automatic file reads, safe aggregate-only briefing, control-command refusal, first unreviewed marker).
- `python -m unittest -q test_local_v431.py` — 8/8 local HTTP tests passed, using fake Ollama and tempfile storage.
- `python browser_smoke_v431.py` — headless Chromium desktop (1280x900) and mobile (390x844) passed: synthetic WAV, new read-only UI, case changes invalidating briefing, consented mock speech, stale callback cancellation, reduced motion, read-only denial, fake local AI request and no accidental source-note transmission.
- Inherited v33/v38/v43 checks: **202/202** JavaScript and **82/82** Python passing in the development container.
- Browser tests for file fingerprinting use a **mock digest only inside the about:blank test page** because browser sandbox blocks local secure-origin navigation. Real WebCrypto SHA-256 implementation and known digest vectors are covered by a separate Node test. Real Windows Ollama inference, device TTS, microphone, actual file handling and hardware remain untested.

## Research integrity, safety and privacy

- The briefing **never validates the authenticity** of evidence or the independence of instruments. Raw WAV file content is accessed only after the user deliberately chooses and attaches a file in the local workspace.
- Previously created v43 JSON packets retain their rules; a SHA-256 integrity digest is **not** an authenticity certificate, digital signature or chain of custody. Imported reviewer identities and observations remain self-reported.
- All instrument displays are synthetic, with **no live control, panic reset, ALL CLEAR, cameras or sensor interfaces**.
- The Python server is **single-operator, loopback-only**, not authenticated, and is not a secure public evidence review service. It must not be exposed to other devices, untrusted extensions, public internet or the VEIL website.
- Local approved memory uses an on-disk store only after deliberate confirmation; the new briefing engine neither reads nor transmits that memory. Browser-delivered TTS may use external services; Ollama has separate local software/configuration and logging considerations.

**Review-only GitHub branch. No merge or website deployment without explicit operator approval.**
