# SIGNAL — Local Assignment Runner v0.1

**VEIL Research Project | October 22, 2026 | working engineering prototype**

## Purpose

SIGNAL is being developed as a useful local-first assistant that can receive a **specific, authorized assignment**, perform an **allowlisted operation**, produce **traceable findings**, and submit them for **human approval or rejection**. This version is a narrow functioning executor, not a large language model, an autonomous researcher, or a device controller.

The first supported assignment is `audit_csv`, which uses the **same real deterministic** sensor-data audit core as the public SIGNAL v0.8 webpage. It detects per-sensor temperature steps, time-order issues, and sampling gaps; it does not infer paranormal causes.

**Workflow:** ASSIGNED → RUNNING → AWAITING_REVIEW → ACCEPTED / REJECTED. Any failure becomes BLOCKED with a reason. The runner does not mark its own findings accepted.

## Try on Windows (free, optional prerequisites)

1. Download or clone the existing VEIL GitHub repository so the `signal` folder and its `csv-audit-core.js` file are present.
2. Install Node.js from https://nodejs.org/ only if not already installed. Node.js is a separate, free runtime; no API account, purchase or subscription is required. The assistant does not install software for you.
3. In `signal/assistant/`, double-click **START_SIGNAL_DEMO.bat**. This runs a **synthetic** example and generates a report that requires review.
4. For your own data, copy a CSV into the private `signal/assistant/workspace/inbox/` folder created by the demo.
5. Use Command Prompt from `signal/assistant`:

```bat
node runner.js assign room-temperature.csv 60 1.5
node runner.js status
node runner.js run SIG-...THE-ASSIGNMENT-ID...
node runner.js review SIG-...THE-ASSIGNMENT-ID... accept "Researcher Name"
```

The `assign` command prints the actual generated ID. Replace the placeholders above, including the full ID. Use `reject` instead of `accept` for a result needing correction. Review records the *entered* reviewer name; **it does not authenticate identity**.

Run `node runner.js demo` for another self-contained synthetic assignment. No special privileges or external sensors are required.

## Actual implementation / properties

- `assignment-core.js`: finite-state assignment protocol; rejects unapproved task types, unauthorized transitions, premature approvals, missing reviewer names, and unsafe input filenames.
- `runner.js`: offline Node.js CLI with allowlisted CSV execution, local source SHA-256 hash, human review status, error reports, and files stored within `workspace/`.
- `../csv-audit-core.js`: real CSV checks and explicit scientific limitations.
- `START_SIGNAL_DEMO.bat`: no-cost Windows launch helper.
- `workspace/`: ignored by Git, so local inputs and results are not accidentally committed during ordinary Git operations.

The runner makes no web/API requests, runs no shell commands, publishes no posts, and has no MTC/Panic Box hardware access. It does not modify other VEIL site files. It is a **single-operator prototype**; concurrent runs, tamper-proof logs, authenticated identity/permissions, and protection against a malicious local user are **not implemented**. File SHA-256 establishes byte identity, not scientific provenance, chain of custody or authenticity.

Treat `workspace/` as locally private, but do not store secrets or sensitive human-subject data until security controls and retention policy are implemented.

## Validation and acceptance

- Assignment core tested through happy-path and rejected state transitions.
- Runner executed in a simulated filesystem against the actual CSV audit library: creation, deterministic execution, export, human review, and duplicate-run rejection passed.
- Separate CSV engine regression tests: `node signal/tests-csv-audit.js` (14/14 passed in development test environment).
- **Not yet verified on the user's Windows computer**, with installed Node.js, and **not a lab-ready system**. The online webpage's conversation is still authored/scripted.

## Near-term roadmap

1. Validate the launch script and runner on the actual Windows desktop, and check resulting CSV reports against known fixtures.
2. Add a human-approved assignment board, due times and priority without inventing background autonomy.
3. Provide explicit opt-in voice capture, local speech recognition where available, and a genuine local conversational model that can propose (not silently authorize) tasks.
4. Build machine-readable, read-only adapters for MTC/Panic Box logs, evidence chain-of-custody documentation, timestamps and uncertainty.
5. Add authenticated role-based access, review signatures, audit integrity, safe concurrency, tests, recoverability, and data retention before deploying in real investigations.

No additional paid services, subscription AI credits, or equipment purchases are required for this narrow prototype.
