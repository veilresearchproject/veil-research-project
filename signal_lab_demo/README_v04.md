# SIGNAL Synthetic Laboratory Research v0.4 — milestones 17–26

**Developer draft only.** This extends the experimental `signal_lab_demo` on GitHub PR #114. It does **not** replace the user's working Windows SIGNAL v25. No real sensors, speech recognition, AI model, camera, microphone, cloud access, or device controls are involved. Outputs do **not** establish paranormal evidence.

## Ten implemented milestones

17. Require explicit study hypothesis, null hypothesis, control, outcome, blinded review, and consent *plan* (not a registered study).
18. Maintain device-specific identity and clock-offset/uncertainty registry, without claiming real calibration.
19. Normalize UTC timestamps across declared device offsets and uncertainties; reject unknown sources or duplicate events.
20. Flag out-of-range numeric readings using explicit bounds and an `UNKNOWN` cause.
21. Group temporally overlapping uncertainty intervals and count *distinct devices* while refusing causal conclusions.
22. Compare test/control flag rates using stated exposure durations; handle zero controls without invalid ratios.
23. Create condition-masked reviewer items with private, separate synthetic custodian mapping; masking alone does not validate blinding.
24. Record self-reported human classifications with mandatory rationales; prevent silent duplicate replacement.
25. Report agreement or unresolved disagreement across independent reviewers without elevating votes to evidence.
26. Produce a static, escaped, offline readout with input CSV SHA-256 fingerprint and explicit limitations.

## Running the standalone tests (Python stdlib only)

From the `signal_lab_demo` folder:

```cmd
py -3 -m unittest -v test_evidence_v04.py test_run_v04.py
```

The isolated v0.4 unit/integration tests were executed in a Linux sandbox using Python 3.11+ and **passed** before commit. The integration tests mock the prior v0.3 bundle verifier; a full Windows end-to-end run of the actual v0.3-to-v0.4 pipeline is **not yet confirmed**. Re-run on the desktop before any deployment or genuine study.

## Using existing v0.3's synthetic data on Windows

From `signal_lab_demo`, where `advanced_lab.py` already exists, run:

```cmd
py -3 advanced_lab.py --approve-simulation --output synthetic_v03_first_run
py -3 run_v04.py --approve-simulation --input synthetic_v03_first_run --output synthetic_v04_first_run
```

Open `synthetic_v04_first_run\v04_readout.html` in a browser. Choose **fresh folder names** for later attempts; v0.4 refuses to overwrite an occupied destination. The runner first checks that the v0.3 synthetic input passed its existing full-bundle integrity verification. It also checks the source CSV SHA-256 against the original manifest before doing anything with it.

The user-facing report contains summary metadata only. The generated `reviewer_packet_SYNTHETIC.json` deliberately removes event timestamps, source IDs and condition labels; **do not share the whole output folder** with reviewers because the `custodian_key_PRIVATE_SYNTHETIC.json` is stored separately there. For real trials, preregistration, separation-of-duties, instrument calibration, participant privacy, clock validation, and authentic chain of custody require professional design and external review.

## Non-goals / remaining gates

- All inputs must be labeled `SYNTHETIC_SIMULATION`; first-half control assignment is just a demonstrator, **not** randomized or preregistered.
- A single CSV contributes all three simulated channels, so their coincidence **is not independent sensor corroboration**.
- The first-pass packet does not itself include playable media; independent reviewers need separately consented and prepared anonymous clips before any real trial.
- A SHA-256 digest detects changed bytes; it does not authenticate who recorded them or establish forensic custody.
- No automatic merges, installations, public website changes, or alterations to the desktop v25 baseline.