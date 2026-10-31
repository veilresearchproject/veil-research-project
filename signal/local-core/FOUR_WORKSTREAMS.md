# SIGNAL four-workstream prototype — integration boundary

This is a code-complete **helper layer**, NOT a fully integrated desktop release.
All helpers are pure and opt-in; they do not run automatically.

1. **Personality:** call `persona_prompt('casual'|'research'|'safety')` when composing an explicitly categorized request. This does not override existing system protections and does not guarantee any model's response.
2. **Animation:** `speaking_pose(elapsed_ms, speaking, reduced_motion)` gives four deterministic face-state names. The desktop renderer must map these to approved local portrait frames, and a trusted Windows TTS speaking-state signal must start/stop the timer. This is not phoneme-accurate lip sync.
3. **MTC:** `review_mtc_observations([...])` produces a bounded human review queue from operator notes only. It never reads WAV files or claims a cause. The operator must verify synchronized evidence separately.
4. **Instruments:** `parse_instrument_event(json)` checks a small allowlisted future telemetry schema. `instrument_summary(event)` explicitly marks it unauthenticated. There is no network listener, pairing, alerting, device control, or ALL CLEAR method.

From `signal/local-core`, test with:

```
python -m unittest -v test_four_workstreams
```

No paid packages or APIs. No public website changes, evidence modifications or microphone permissions. These functions need desktop UI/TTS integration, instrument protocol authentication, and physical Windows acceptance before they can be regarded as deployed features. Preserve the existing working SIGNAL desktop version until those tests pass.
