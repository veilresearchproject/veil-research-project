# SIGNAL — MTC read-only session adapter v0.1

**VEIL Research Project · October 30, 2026 · engineering prototype**

SIGNAL can now inspect an unattended MTC session's three small JSON logs, verify the recorded SHA-256 values for the metadata and events file, check declared audio segment frame continuity, count question-playback and response-window events, and summarize the declared session outcome. This runs **locally and offline** with Python's standard library.

This is a read-only evidence-log adapter, **not** an EVP detector or automatic audio listener. It never reads WAV audio, modifies evidence, contacts a model, or controls equipment. Frame offsets in the JSON files are **claims in a log**, not an independent proof that the WAV files are gapless.

## Use on Windows

1. Keep the MTC session folder and its `session_result.json`, `session_metadata.json`, and `events.jsonl` files together. Leave the WAV recordings where they are; the adapter doesn't need to upload or read them.
2. Open a Command Prompt in `signal\local-core`.
3. Run (replace the example with the actual path, keeping quotes):

   ```bat
   py -3 mtc_evidence.py "C:\Users\User\Desktop\MTC_Oct27"
   ```

4. For a structured report, add `--json` after the folder argument. Outputs are displayed only; no original evidence is altered.
5. For automated regression tests, run `py -3 -m unittest -v test_signal_core.py test_mtc_evidence.py test_signal_mtc_integration.py`.

## Test record

- 20 distinct tests pass: 9 existing SIGNAL local-core tests, 8 MTC log-adapter tests, and 3 new conversation-integration tests. All use mocked local-model calls when a model is involved.
- Actual October 27 MTC v0.1.4 JSON logs were reviewed in an isolated test environment: 5400.021 seconds declared, two segments, 121 question starts/completions, 121 completed response windows, 12 cycle starts and 11 completed cycles, reported outcome COMPLETE with zero faults; logged SHA-256 values match. WAV audio was not available for this validation.

## Local conversation integration

The existing `signal_core.py` now supports `/mtc "C:\path\to\session"`, which loads a bounded, verified summary for subsequent questions to the **local Ollama model**. `/mtc-clear` removes it; `/clear` also clears it. No evidence is persisted in SIGNAL memory. The model may still make mistakes, so check its wording against the deterministic report. Do not interpret "no reported faults" as proof of physical recording quality or source authenticity.

**Next:** run the updated SIGNAL Windows launcher against a locally installed Ollama model and inspect the answers; later add an audio-review adapter for user-confirmed time ranges. No paid API or cloud backend is required.
