# SIGNAL v31 — Blinded-source review rehearsal

**Prototype, November 5, 2026.** Builds on the unmerged v30 branch. No merge, no public website deployment, no modification to the working Windows v25 desktop. No API key, paid account, sensor input or cloud service is required for the review logic.

## Research workflow
With a Casebook loaded, press **Start rehearsal and hide source details**. The interface creates a randomly permuted, description-only packet that omits the source type, label, recorded timestamp and case title. The original metadata/answer key stays in volatile browser memory; ordinary panels are temporarily hidden. Download the description-only packet to distribute to a *separate* reviewer who has not seen the original case.

Reviewer selects one of three cautious outcomes for each description and supplies written reasoning. They enter an unattributed name or pseudonym and press **Record review decisions**. The answer key is revealed only when the operator explicitly presses **Reveal source mapping** *after* all review decisions are recorded. A separate reviewer-decision export contains no source mapping. All exports are manual. The original Casebook cannot be edited through the hidden interface until reveal/reset. Any change in Casebook state invalidates the review.

## Scientific limitations
This is a **source-label masking rehearsal**, not an authenticated blind or double-blind investigation. A description may disclose its source or expected outcome; the operator may have already seen the source metadata; the JavaScript variables/answer key are accessible in browser developer tools; reviewer names are not authenticated; and saving JSON to disk is not an integrity-preserving audit trail. For genuine independent review, send the description-only export to a reviewer without access to the originals, register a protocol beforehand, preserve raw evidence, log reviewer independence and prevent changes after locking.

No AI interpretation is used to decide the outcomes; the three cautious categories cannot claim proof of paranormal causes. No raw recordings, images, sensor streams or equipment are inspected by this component.

## Setup and tests
This ZIP is an **add-on** to an existing checkout containing `server.py` from the SIGNAL Local Brain Bridge. Place files beside that bridge without overwriting v25. Double-click `START_SIGNAL_V31_BLIND_REVIEW.bat`, then open `http://127.0.0.1:8771/`. Ollama can remain disabled for the blind review. The local server only binds to loopback; real Windows Ollama and device voice integration require separate user testing.

- `node test_blind.cjs`: 23/23 deterministic blind packet and decision tests passed in development.
- `node test_v31.cjs`: interface/privacy checks.
- `python browser_smoke_v31.py`: Chromium synthetic rehearsal, source hiding, decision locking, reveal, and local export.
- Inherited Casebook, fingerprint, correlation and clock modules remain available for separate review.