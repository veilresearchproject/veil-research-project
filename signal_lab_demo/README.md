# SIGNAL laboratory demonstrator v0.2 — six incremental updates

**Synthetic data only.** No physical sensors, voice services or AI model connected. All scripts use the Python standard library with no cloud calls or fees.

From the `signal_lab_demo` folder:

```bash
python run_lab.py --output signal_lab_output
python -m unittest -v test_updates.py
```

Windows may use `py` in place of `python`. Open `signal_lab_output/dashboard.html` in a browser.

## Six updates
1. `profile.py` — validated thresholds and intervals.
2. `ingest.py` — strict, read-only synthetic CSV parsing.
3. `correlate.py` — temporal grouping of flags, without causal interpretation.
4. `provenance.py` — file SHA-256 inventory and verification.
5. `review.py` — explicit human review decisions in append-only-by-convention JSONL.
6. `dashboard.py` — static, offline HTML summary.

`run_lab.py` ties the modules to the original v0.1 simulation. `test_updates.py` checks each capability. The six comparable local tests passed; CI has not independently run these repository files.

**Limitations:** All timestamps and sensor readings are synthetic. Fingerprints reveal file changes but are not an authenticated chain of custody. Human review logs are ordinary local files, not cryptographically immutable. Keep this branch separate from the public website and existing desktop baseline pending review.


## Version 0.3 — milestones 7–16

Run `python -m unittest -v test_updates.py test_advanced.py` and `python advanced_lab.py --approve-simulation --output demo_output`. View `demo_output/dashboard.html`, `briefing.txt`, and `casebook.json`; verify with `python advanced_lab.py --verify-only --output demo_output`.

7. Strict allowlisted text commands (not speech recognition)
8. Validated synthetic experiment protocol
9. Fail-closed preflight
10. Virtual experiment schedule
11. Passive sensor-health summary
12. Source-attributed event casebook
13. Deterministic noncausal research briefing
14. Restricted export artifact filenames
15. Whole-bundle fingerprint verification
16. Integrated operator-approved synthetic workflow

**Important:** No real sensors, AI model, speech recognition, physical actuation, or network requests. The program only generates simulated data; it is not a production laboratory instrument. The v0.3 local package passed 16 unit tests; remote CI validation has not been performed. Keep this draft PR unmerged pending review.
