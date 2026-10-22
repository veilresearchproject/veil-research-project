# SIGNAL Local Core 0.1 — free-first Windows proof of concept

**Status: Nine local mocked-interface tests passing (October 22, 2026). Not yet run on the user's Windows PC or with an actual local model.**

This is SIGNAL's first local language-model conversation engine. It is separate from the scripted public SIGNAL character. It has no laboratory instrument, camera, microphone, or public website connection.

## Free setup

1. Install **Python 3.10+** from https://www.python.org/downloads/windows/ . Enable the Python launcher. No additional Python packages are required.
2. Install **Ollama for Windows** from https://ollama.com/download/windows . Use locally, **not** the Ollama Cloud service. System drivers and storage requirements apply.
3. Open Command Prompt and run `ollama pull llama3.2:3b` (model roughly 2 GB, installation uses additional storage and a once-only internet download). Review Meta Llama model licensing before any commercial redistribution.
4. Start Ollama. Double-click `START_SIGNAL.bat` in the same directory as the Python file, or run `py -3 signal_core.py`.
5. Try `Hello SIGNAL, how should I review an unusual thermal reading?`. Save a memory with `/remember preferred name = Drew`, list with `/memories`, delete with `/forget preferred name`, or clear temporary conversation with `/clear`.

## Privacy and safety

- This Python code sends requests only to `127.0.0.1:11434` (local Ollama API). No remote/cloud fallback, secrets, paid API, or recurring inference charge. **Do not choose cloud models.**
- Normal chat lasts only in RAM for up to eight exchanges. Only explicitly remembered facts persist as an unencrypted JSON file in `%LOCALAPPDATA%\VEIL\SIGNAL`. Do not store secrets there.
- Any local language model can hallucinate. Its prompt is not a security boundary. No camera, live evidence, files, instrument actions, panic-box commands, or safety-critical control exists in this version.
- Nine automated tests use a mocked local HTTP backend; neither a real model nor GPU performance was tested on the user's workstation.
- Local operation still uses disk, memory, power, and hardware. No promise of cost-free physical operations.

## Tests

From this directory: `py -3 -m unittest -v test_signal_core.py`

## Next steps

1. Perform real Windows local-model smoke test, record hardware and latency results.
2. Evaluate properly licensed smaller models on the same question set.
3. Add separately tested offline speech input and optional Windows voice output.
4. Add **read-only** adapters to MTC sample metadata and sensor CSV evidence, with original file integrity, provenance, and human-reviewed interpretations.
5. Connect the animated SIGNAL front end only through a secure, authorized boundary after local validation; never publicly expose the Ollama server.

The public SIGNAL website must continue to label scripted experiences as demonstrations.
