# SIGNAL integration checkpoint — October 31, 2026

The working desktop already includes:
- Character expression states and illustrative speech sprite animation
- Optional local Windows TTS and microphone controls
- A local MTC review notebook and scanner flag review
- Model status/readiness controls

## New in this isolated branch
`four_workstreams.py` contains evidence-first personality profiles, a deterministic four-state speaking scheduler, a bounded human MTC review queue, and an allowlisted *read-only* future instrument telemetry format.

`operator_workbench.py` connects the four helpers into an opt-in **offline dry-run** workflow. It accepts an explicitly created JSON fixture, does not connect hardware, does not modify the active desktop application, and prints structured output with limits. It is a developer integration checkpoint, not a replacement for the existing browser UI.

Create a fixture named `workbench_fixture.json` manually:

```json
{
  "observations": [{"timestamp_s": 31.25, "description": "Operator noted a click; source unknown"}],
  "telemetry": [{
    "instrument_type": "mtc",
    "device_id": "MTC_1",
    "timestamp_utc": "2026-10-31T15:00:00Z",
    "measurements": {"status": "ready"}
  }]
}
```

From `signal/local-core`:

```bat
py -3 -m unittest -v test_four_workstreams test_operator_workbench
py -3 operator_workbench.py workbench_fixture.json --subject research --speaking-ms 140
```

The JSON is a synthetic example; **do not substitute raw research evidence without an evidence-handling review**.

## Acceptance gates before an integrated desktop release
1. Run full Python regression suite and JS browser simulations.
2. Wire approved persona guidance into the *existing* local model path without removing existing system rules.
3. Map the helper scheduler to existing sprite images and voice status, observing reduced motion. Do not add a second animation loop.
4. Map verified, consent-selected notebook data to the bounded MTC review queue. Do not rewrite original WAV/JSON.
5. Keep instrument input transport disabled until authentication, schema constraints, provenance and event handling are designed and tested.
6. Package a fresh verified Windows ZIP and run real desktop voice, microphone and Ollama acceptance.

No merges to main or changes to the user's current installed build have been made.
