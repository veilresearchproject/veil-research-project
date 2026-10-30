# SIGNAL v0.11 — Local streaming conversation, manual cancellation

**Scope:** Continue v0.10 without changing the approved character, image assets,
MTC recorder, scanner, evidence logs, or live VEIL website.

## What changed

- `signal_core.LocalModel.stream_answer` calls `http://127.0.0.1:11434/api/chat`
  with `stream: true`, capped generation, a maximum frame and reply size,
  explicit terminal completion requirement, and no cloud fallback.
- `Assistant.stream_ask` adds to memory **only after** stream completion. An
  interrupted stream yields no saved turn and no text-to-speech activation.
- `signal_desktop.py` adds an authorized streaming response endpoint using
  `application/x-ndjson` and an independent operator stop endpoint.
- The existing desktop chat shows partial replies incrementally and labels
  them unverified; **Stop reply** interrupts an unfinished generation.
- Existing slash commands, optional Windows TTS, microphone consent,
  character face/mouth images and all MTC evidence tools remain unchanged.

## Research integrity

Streaming output is still unverified AI-generated text. The model has not
listened to source WAV recordings or verified an EVP. Lab measurements and human
review notes stay separate. No feature can issue Panic Box ALL CLEAR.

## Limitations

- Real Ollama token-generation latency and Windows browser/audio hardware are
  not verified in this development environment. Unit tests use synthetic model
  responses; actual behavior is subject to the installed Ollama model.
- The operator's stop action takes effect at the next output token; the browser
  aborts immediately. If the local model stalls, its network call can take up
  to the configured timeout to unwind, and a reply that already completed may
  remain in session history. This is not a safety-device control.
- This is a local one-operator alpha, not a remotely networked research center.
- Current mouth motion is illustrative and not phoneme/lip synchronized.

## Acceptance checklist on Windows

1. Keep v0.10 as backup. Unzip this v0.11 into its own folder.
2. Run `RUN_SIGNAL_TESTS.bat`, then `CHECK_SIGNAL_SETUP.bat`.
3. Start Ollama with the configured local model; confirm `Test Ollama conversation`.
4. Ask an ordinary question; observe text appearing in chunks and a completed
   response. Ensure a spoken reply only occurs when voice was enabled.
5. Ask for a longer answer and use **Stop reply** before completion. Ensure no
   spoken partial answer and no completed footnote; the model history should not
   retain a partial assistant reply.
6. Turn voice ON and test a short response, then **Stop speaking**.
7. Confirm MTC log load, scanner selection, human note, and export still work.
8. Report any errors before considering a merge of the stacked development PRs.

No Work credits, API fees or package installs are needed for these development changes.
