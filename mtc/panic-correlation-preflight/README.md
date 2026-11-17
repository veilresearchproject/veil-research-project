# MTC ↔ Panic Box event correlation — read-only preflight v0.1

This tiny, separately testable Python 3.10+ standard-library module compares **synthetic or manually entered event metadata** from the MTC and Panic Box without opening any files or contacting any equipment. It does not record, control devices, infer causes, or validate the researcher-provided timestamps and hashes.

A possible temporal overlap is **not** evidence of a common cause or paranormal event. Independent devices can still share a power/noise/clock artifact, and clock corrections cannot be invented. Missing offsets/uncertainty fail closed. Fields preserve device ID, session ID, source-file SHA-256, timezone-corrected timestamp, measured-clock claim, event uncertainty, and flag type.

## Tests

Run `cd mtc/panic-correlation-preflight && python -m unittest -v test_correlation.py`. Expect 24 offline unit tests. Tests cover timezone, offset boundaries, same device/session, missing clock data, invalid hash and events, conservative classification, and report limitations. Real recorder/camera, Samsung, clock-sync and chain-of-custody tests remain outstanding.

## Example (synthetic metadata only)

```python
from correlation import generate_report
sha = 'a'*64
mtc = dict(event_id='MTC01', session_id='SESSION01', source_kind='MTC', device_id='MIC01', source_file_sha256=sha, recorded_at='2026-11-17T21:00:00Z', clock_offset_ms=0, clock_uncertainty_ms=100, event_window_ms=200, flag_type='WAVE_ENERGY')
box = dict(mtc, event_id='BOX01', source_kind='PANIC_BOX', device_id='CAM01', flag_type='MOTION_FLAG')
report = generate_report([mtc, box])
assert report['pairs'][0]['classification'] == 'POSSIBLE_TEMPORAL_OVERLAP_REVIEW_ONLY'
```

Before real integration, validate source hashes against preserved originals, authenticate the researcher, independently calibrate all clocks and document shared electrical or environmental factors. Human review and publication approval are required.
