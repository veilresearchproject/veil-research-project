# SIGNAL — Local Brain Bridge v0.1 (November 2, 2026)

## What works
A polished browser conversation demo with scripted default responses, opt-in local LLM via Ollama, short session-only context, browser speech synthesis, explicit no-model fallback and a Clear control. Source files contain no external CDNs, cookies, analytics, cloud keys, or network URLs except `127.0.0.1`. The Python server uses only standard library and binds `127.0.0.1`, not the public network.

**Desktop milestone (reported November 2):** On the user's Windows computer, Python 3.13.17, Ollama CPU mode and `llama3.2:3b` successfully produced a real local-model response through the bridge. This was a user-run manual verification, not an automated deployment test. Local voice quality, long-running reliability, phone access and sensor integration remain unverified. This is not a field system, sensor controller, paranormal evidence evaluator, or sentient system.

## Immediate scripted demo
Open `index.html` in a browser to try scripted answers. A local HTML file cannot connect to Ollama directly; it intentionally defaults to script-only mode. It does not run a hidden AI or make internet requests.

## Optional real local AI on Windows desktop (only when ready)
1. Confirm Windows and computer specs first (RAM, CPU, disk); a very old desktop may not support the model comfortably.
2. Install Ollama from its official site, **https://ollama.com/**. Review software trust and model licenses before installation.
3. Run `ollama pull llama3.2:1b` once (or use `llama3.2:3b` if already installed). This is approximately a **1.3 GB** model download and requires internet only for installation and download. No subscription or API key is needed. (Ollama model library: https://ollama.com/library/llama3.2.)
4. Start Ollama normally; it should expose the local service on `127.0.0.1:11434`.
5. From this folder, start the bridge: `py -3 server.py` (or `python server.py`). Requires Python 3.9+.
6. Open `http://127.0.0.1:8765/`, click **Check local model**, then **Enable local AI**.
7. To stop, use Ctrl+C in the terminal. To return to scripted mode, click **Disable local AI**.

No changes to your main VEIL website are made; this runs on *your computer only*. It cannot be accessed from your Galaxy S25 without additional LAN network/security work, intentionally left disabled in this version.

## Testing
Run `python -m unittest -v test_bridge.py` for local fake-Ollama backend integration tests, and `node test_frontend.cjs` for browser-script unit checks. The tests make no public network requests and do not require Ollama. Actual LLM quality, loading time, RAM use, phone speech, and real hardware behavior are unverified.

## Privacy/security limits
- The Python server listens only on 127.0.0.1; browser API calls must be same-origin JSON POSTs. No CORS or LAN access.
- SIGNAL does not store transcripts, persist chats to files, or print prompt contents. Ollama is a separate program with its own settings/logging policies; verify those separately before using sensitive data.
- Browser text-to-speech may use network-based voices, independent of the bridge. Do not enter private health, family, or confidential business details in this prototype.
- Local LLM output can hallucinate, and the system prompt is not a guarantee of factuality. Verify original evidence before drawing conclusions.
- The optional model uses memory and processing power. This is a low-cost direction, not an assertion that your current desktop supports it.
## November 3 identity guard (review branch)
The system prompt now explicitly anchors VEIL as Andrew Underwood's independent project for studying reported anomalous environmental events. It instructs SIGNAL not to invent what the letters VEIL stand for or confuse the project with viral epidemiology. Two new deterministic integration tests check that the identity instructions reach the local model. **These are instructions, not a guarantee** that a small language model will never hallucinate. User desktop retest after applying this branch is still required.

For the previously verified CPU-only setup, start Ollama from a separate Command Prompt with `set "CUDA_VISIBLE_DEVICES=-1"`, `set "OLLAMA_VULKAN=0"`, `set "OLLAMA_LLM_LIBRARY=cpu"`, then `ollama serve`. In the SIGNAL folder use `set "SIGNAL_MODEL=llama3.2:3b"` then `py -3 server.py`. Retain both command windows. These Windows commands are specific to the previously observed Quadro P5000 compatibility issue; other systems may not need them.
