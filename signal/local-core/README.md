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

## Reproducible offline mock evaluation (October 22, 2026)

Run from `signal/local-core/` on Python 3.10+:

```cmd
py -3 -m unittest -v test_signal_core.py
py -3 eval_mock.py --iterations 20 --json
```

The benchmark runs **24 fixed synthetic scenarios × 20 repetitions = 480 mock requests**, covering thermal, audio, integrity, controls, permissions and context. It exercises the real Python Assistant → LocalModel HTTP request construction but substitutes an in-process fake response. It checks the fixed loopback endpoint, eight-turn history limit, required system disclosures, explicit memory write/delete, unknown-command rejection and seven injected response failures. Failures produce a nonzero exit code. No Ollama model, real network, GPU, instrument, camera, or microphone is used. **Mock timing is only Python serialization/test overhead, not actual AI inference latency or response quality.** A mocked model cannot establish that a real model will follow safety instructions.

The local response parser now caps HTTP responses at **1 MB** and individual replies at **8,000 characters**, and converts malformed JSON/invalid UTF-8 to a controlled local error. Offline errors still have **no cloud fallback**. Existing HTTP test fakes were updated to accept bounded `read(size)`.

**Remaining tests:** Windows Xeon/Quadro P5000 + real local Ollama model installation, response latency, model reasoning/accuracy, interrupted/slow inference, and future human-reviewed **read-only** instrument integration. SIGNAL has no instrument controls or real sensor connection. This is an engineering test harness, not scientific validation.
