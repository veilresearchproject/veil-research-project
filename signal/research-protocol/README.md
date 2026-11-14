# SIGNAL: research-protocol preflight (draft)

Standalone, offline-first preregistration checklist for VEIL experimental design. This is intentionally **not wired** to the local Ollama assistant, public site, any recording system, or lab instrument. It reads a *caller-supplied in-memory object* and returns deterministic missing-field issues. A passing checklist is **not** research approval, ethics review, evidence authenticity, calibration, or proof of paranormal activity.

This prototype aims to help VEIL explain future MTC or Panic Box studies to academic methodologists. The synthetic MTC example uses invented devices and sessions; no home address or third-party recordings are included. Avoid using actual people or locations without consent.

Required: neutral test and null hypotheses, primary outcome, matched control, predeclared analysis, blinding, participant privacy/consent, uncertainty, human review, independent device IDs, clock references, and UTC preregistration earlier than planned session start. It does not create an immutable registration or enforce that the researcher really locked the plan; that needs independent timestamping and review.

Run the offline Node built-in tests: `node --test signal/research-protocol/protocol-preflight.test.mjs`.

Further work: peer review of schema and controls; explicit randomization assignments, immutable plan versioning, unaltered evidence manifests, checksums and signed approvals. Do not merge or deploy until reviewed. Working desktop v25 remains untouched.
