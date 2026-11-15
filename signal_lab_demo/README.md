# SIGNAL laboratory demonstrator v0.1

Synthetic-data-only, no-cost Python standard-library proof of concept. Does not connect to physical equipment or an AI model. **Never interpret threshold flags as paranormal findings.**

From this folder:

```bash
python signal_lab_demo.py --output output
python signal_lab_demo.py --output output --verify
python -m unittest -v
```

Outputs: timestamped **synthetic** readings CSV, SHA-256 provenance manifest and human-review report. Times are fixed sample timeline timestamps, not real capture times. To run on Windows, use `py` if `python` is unavailable.

Next step: separate read-only sensor adapters, safe operator-approved scheduling, and provenance-preserving integration with SIGNAL. Main branch and current desktop installation are untouched.
