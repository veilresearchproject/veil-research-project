# SIGNAL Local Voice Output v0.3 — offline Windows proof of concept

**VEIL Research Project | October 30, 2026 | engineering prototype**

SIGNAL now has **optional local Windows text-to-speech output**, using the Windows built-in System.Speech synthesizer. No paid API, cloud calls, third-party Python packages, or voice cloning. This extends the existing local-core Python/Ollama program and the read-only MTC log adapter.

## Windows instructions
1. Keep these files together. Python 3.10+, Windows PowerShell and an installed Windows speech voice are required.
2. Double-click **START_VOICE_TEST.bat** to hear a test **without Ollama**.
3. Double-click **START_SIGNAL.bat** to start SIGNAL conversational chat (requires Ollama with a local model).
4. Type `/voice list` for available voices, `/voice on` to speak responses, `/voice stop` to interrupt, `/voice off` to disable, `/voice rate 1` (-5 to 5) to change speed, or `/voice test` for a short test phrase.
5. For opt-in MTC log context, use `/mtc "C:\path\to\your\session"`; `/mtc-clear` and `/clear` clear the loaded log summary.

## Scientific, privacy and safety constraints
- Voice synthesis is **output only**: no microphone, recognition, audio analysis, instrument control or voice cloning.
- The program sends plain speech text through a local subprocess standard-input pipe, not into constructed shell commands.
- Voice starts **off** for each run; it speaks only if explicitly enabled. Long replies are spoken only in a bounded excerpt; the full reply remains on screen.
- The spoken model can be mistaken; source verification and human review remain essential. The MTC adapter reads only JSON logs, not WAV audio.
- Speech quality depends on locally installed Windows voices. Actual Windows voice playback has **not been verified on the user's PC**.
- No cloud fallback or paid API. Local Ollama model setup is separate.
- If anything fails, consult `/voice list` and the test launcher before troubleshooting Ollama.

## Testing
Run from this directory:
`py -3 -m unittest -v test_signal_core test_mtc_evidence test_signal_mtc_integration test_signal_voice`

**30 tests passed in development:** 20 existing SIGNAL/MTC tests and 10 new voice tests using mocked Windows PowerShell processes. The actual Windows sound output still needs a device-level test. Voice cloning, if pursued later, would be a separate, explicitly consented, carefully protected feature.
