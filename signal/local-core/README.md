# SIGNAL Local Core v0.3 — VEIL Windows prototype

**Status:** Thirty automated tests passed in a non-Windows development environment on October 30, 2026. Windows speaker playback, actual Ollama-model performance, and hardware integration are **not** yet validated.

SIGNAL is evolving as a privacy-conscious, local-first lab assistant. The current program supports local text conversation via the Ollama API (127.0.0.1 only), explicitly saved local memories, **read-only MTC session log review**, and **opt-in Windows text-to-speech output**. It does not listen to a microphone, directly examine the WAV audio, control lab devices, or send data to a cloud inference API.

## Getting started

1. Install Python 3.10+ for Windows (with the Python launcher) if necessary.
2. First double-click **START_VOICE_TEST.bat** to check the built-in Windows voice *without needing Ollama*.
3. For AI conversations, install and run local Ollama (see https://ollama.com/download/windows) and download the local model: `ollama pull llama3.2:3b`. The download needs internet access once and disk space; check model licensing.
4. Double-click **START_SIGNAL.bat**. Use `/help` for commands.
5. Type `/voice on` for speech output, `/voice stop` or `/voice off` to interrupt or disable it. The voice is off at startup.
6. To inspect a completed MTC session's logs, use `/mtc "C:\path\to\session"`. This reads only `session_result.json`, `session_metadata.json` and `events.jsonl`; no WAV upload is needed.

Details: [Windows voice](VOICE_OUTPUT.md) · [MTC log review](MTC_READONLY_ADAPTER.md).

## Integrity, permissions, and limitations

- Python standard library; no paid API or third-party speech package. Speech is synthesized by Windows System.Speech.
- Speech synthesis is **output only**, not voice input, identity verification or voice cloning.
- The program has no camera, instrument, remote control, alarm acknowledgement or Panic Box ALL CLEAR permissions.
- Memory facts are stored unencrypted on the user's computer and should not hold secrets or sensitive investigation data.
- MTC session records provide **software logs**, not acoustic proof or a scientific interpretation.
- Never present the public scripted SIGNAL character as a fully autonomous working assistant.

## Test suite

```bat
py -3 -m unittest -v test_signal_core test_mtc_evidence test_signal_mtc_integration test_signal_voice
```

This is an engineering prototype. Keep production research recordings untouched while validating the adapter and voice behavior on a Windows PC.
