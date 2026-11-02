# SIGNAL response quality checks (offline prototype)

This standalone Python standard-library module provides advisory checks for two observed failures: a hallucinated VEIL identity and replies that defer or truncate speech. It does not claim to fix microphone recognition, speech playback, or Ollama configuration.

Run from this folder:

```sh
python -m unittest discover -s tests -v
```

Integration guidance:
1. Supply the VEIL_IDENTITY sentence to the local model as a trusted, persistent project fact. Do not claim VEIL is an acronym with an invented expansion.
2. Before speaking a generated answer, call check_answer(answer) and regenerate or visibly flag known errors.
3. Set speech_complete=True only after confirmed audio playback completion. If supported, compare the actual spoken transcript with the answer; text sent to TTS is not proof of audible delivery.
4. Keep output local and avoid logging sensitive audio or transcripts without consent.

Known limits: This is a narrow regression harness, not a complete hallucination detector. It is not wired into the desktop app until the current audio pipeline is inspected and integration-tested.
