# MTC synthetic marker sequence review — development branch

**Scope:** Read-only, deterministic checks on caller-supplied SYNTHETIC CSV metadata. No instrument connection, audio analysis, camera, Panic Box controls, Ollama inference, or physical evidence interpretation.

## Implementation (October 25, 2026)

- `mtc_sequence_review.py` checks recording/question marker sequences **independently per recorder** after the strict existing `synthetic_evidence.inspect_synthetic` CSV and SHA-256 validation.
- Reports missing starts/ends, repeated starts, questions outside a recording, a recording ended with an open question, non-increasing per-recorder timestamps and unclosed sessions at end of data.
- Returns structured row-numbered findings, source hash and explicit `SYNTHETIC_ONLY` and no-live-access labels.
- `test_mtc_sequence_review.py` contains **16 local synthetic-data regression tests** that passed in isolated Python 3.13.5 on October 25, 2026. This is not an independent GitHub Actions CI result and does not validate actual field hardware.

Run from `signal/local-core`:

```shell
python -m unittest -v test_mtc_sequence_review.py
python -m unittest -v test_signal_core.py test_readonly_intake.py test_mtc_sequence_review.py
```

## Review/merge safety

Draft pull request #4 remains **DO NOT MERGE** pending independent rerun of the tests against the actual final branch, branch-diff review and confirmation that no unrelated website/public character files were modified. Any repository merge requires deliberate review.

**Not verified:** real recorder/room microphone operation, actual speaker questions acoustically captured, timestamps synced against independent cameras/audio recorders, Windows workstation and live Ollama compatibility, real instrument chain of custody, or any paranormal cause. Marker sequence correctness alone is not evidence that an audio file actually contains the played question.
