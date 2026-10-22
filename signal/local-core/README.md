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

## Experimental read-only synthetic evidence boundary (separate module)

`synthetic_evidence.py` is a deterministic, stdlib-only parser. It accepts **caller-supplied bytes**, not filenames, network addresses, microphones, devices, or instrument commands. It is **not wired into Ollama, the public SIGNAL character, the existing CSV Audit Bench, or the assignment runner**. It deliberately labels every output `SYNTHETIC_ONLY` and `model_inference: false`.

Supported fixed CSV schemas are:

- `thermal`: `timestamp,sensor_id,temperature_c` — per-stream sampling gaps, temperature steps and timestamp-order warnings.
- `mtc_markers`: `timestamp,recorder_id,marker` — counts from a restricted marker vocabulary. This **does not** interpret or capture EVP/audio, and marker ordering/state validity is **not yet checked**.

Limits: UTF-8 only, 128 KB maximum, 1,000 data rows, strict header and identifier checks, explicit ISO 8601 timezones, optional expected SHA-256 verification. Source identity and chain of custody are **not** established by a hash. A caller must independently verify input provenance and consent before any future integration.

### Reproducible verification

From `signal/local-core` with Python 3.10+:

```shell
python -m unittest -v test_signal_core.py test_readonly_intake.py
python benchmark_readonly_intake.py --cases 240 --seed 20261022 --json
```

The first command runs the original nine mocked local-model interface tests plus twelve synthetic evidence intake regression tests. The benchmark generates **240 deterministic synthetic cases across eight categories**, including thermal changes, cadence gaps, timestamp-order problems, MTC metadata, SHA mismatch, unsupported schemas and marker rejection. It exits nonzero if a case fails. The JSON includes a reproducible output digest and machine-dependent Python parser timing and peak traced memory; **neither timing nor accuracy reflects a real Ollama model or a physical instrument**.

Verified in an isolated Python 3.13.5 environment on October 22, 2026: twelve intake tests passed; 240/240 generated synthetic cases passed, output fingerprint `24b8ae8c10ca88cba5c2e50945a4224bf359caa0d5f93b01566df20f5cbf8f8d`. The original nine local-core mock tests were previously reported passing, but this change is not a live Windows/Ollama test. Repeat the full command after checking out this branch.

### Before any actual lab connection

1. Review the code and regression cases in a pull request; do not assume tests establish physical measurement validity.
2. Validate on the user's Windows workstation with the intended Python version, real local Ollama and actual model (separate from synthetic intake).
3. Add an explicit, permissioned **read-only** input adapter with bounded file selection, source identity, immutable raw-byte hashing and documented provenance.
4. Validate MTC marker sequencing, timing synchronization, and sensor calibration independently; never grant this parser instrument-control capability.
