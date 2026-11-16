# VEIL Public Research Library & Evidence Review Program
**Draft program standard | 2026-11-16 | No paid services launched**

## Purpose
Build a free public research archive and a future paid, human-reviewed evidence analysis service that supports the VEIL Research Project without compromising findings.

## Program streams
**Public:** Open access to approved case reports, educational material, methods, experimental results and legally shareable historical references. Facebook is a discovery and community channel; a Facebook account/follow should not be a requirement for access.

**Future paid:** Voluntary single-case, defined-scope technical reviews of photographic, acoustic, video and instrument evidence. Pay-per-case rather than subscription at pilot launch. Do not accept payment until a secure workflow and terms are in place.

## Exploratory prices (not offers)
- Preliminary still-photo review: $10–15
- Detailed photo/audio technical assessment: $25–40
- Video review plus written report: $50–75
- Complex multi-file case: scope and quote first

Actual prices require time-and-cost measurement, declared limits and refund/cancellation terms. Never charge in exchange for a paranormal finding.

## Intake and case controls
1. Consent-based submission with submitter contact, authority to share the files, content warning, file provenance and stated review question.
2. Private secure upload, malware/file-type limits, and separate storage (not public GitHub).
3. Assign case ID `VEIL-IR-YYYY-NNN`, evidence IDs `<case-id>-EV-NNN`, capture-time metadata and SHA-256 hashes.
4. Document chain of custody and scope; prevent sharing private witness data, location details or minors' data without appropriate permissions.
5. Technical verification and alternative-hypothesis testing; document SIGNAL model/tool versions and trace each claim to evidence.
6. Human reviewer verifies every substantive conclusion and signs off; separate research result from paid deliverable.
7. Deliver a dated versioned PDF privately; allow corrections and disputes; publish only with independent explicit permission.
8. Apply a declared retention/deletion schedule; do not use client evidence to train AI or populate a public archive without separate informed authorization.

## Outcome categories
Explained; Probable explanation; Inconclusive; Unexplained after investigation. None of these implies the supernatural.

## Readiness gates
- [ ] Clear legal entity, consumer terms, privacy policy, consent and cancellation/refund policy reviewed for applicable requirements
- [ ] Secure authentication/upload, access limits, backups, malware checks, encryption and incident-response plan tested
- [ ] Documented evidence intake and custody log tested end to end
- [ ] SIGNAL analysis validated against controlled datasets and human review
- [ ] Scope, turnaround, pricing and case-volume capacity measured
- [ ] Payment processor connected to suitable secure backend, never embedded secrets in GitHub Pages
- [ ] One or more representative pilot reports completed and quality-checked
- [ ] Publication permission workflow and permanent correction policy implemented
- [ ] Human approval for public launch

## Pilot success criterion
Run a consented non-paid case from intake to private report, verify originals and hashes, retain an audit trail and document reviewer corrections. Do not claim operational readiness solely from posting this plan.

## Operator pilot

The [private pilot runbook](private-pilot.md) covers encrypted handoff, local intake, SIGNAL CSV audit, human review, private report delivery, and retention. The software supports no-fee cases only. The public catalog accepts manually edited entries for approved VEIL reports. A private report has no publication or catalog-export command.

Use the pilot to record active minutes for intake, technical examination, independent review, corrections and delivery. Track file count and size, media type, turnaround, follow-up burden, storage needs and failed or withdrawn cases. Before proposing fixed scopes or prices, compare total effort across representative photo, audio, video and instrument-data cases. Define deliverables, supported file sizes, turnaround, revision limits and cancellation terms. An eventual order state must remain independent of the evidence finding and publication permission.

A controlled synthetic CSV exercise can verify the mechanics but cannot validate physical sensors, reviewer independence, customer readiness or legal terms. The no-fee consented field pilot remains the next operational gate.


## Pilot effort and catalog checks

Record active work separately from turnaround. Use one stable entry reference per block of work so a retry does not count the same minutes twice.

```text
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor operator record-effort CASE_ID --entry shift-1-intake --stage intake --minutes 15
python tools/evidence-review/pilot.py --store PRIVATE_PATH --actor operator effort-summary CASE_ID
```

The private summary reports active minutes by stage, file counts and bytes, and elapsed minutes from opening the case to the first logged delivery. It contains no evidence contents. Retain and remove these measurements with the case. Compare consented pilot runs before proposing pricing or staffing levels.

Before proposing a catalog release, manually verify publication permission, redactions, the intended revision, and the readable PDF. Run `python tools/research-library/validate_catalog.py` from the repository root to check the public metadata and PDF paths. The validator checks the file header and catalog consistency. Publication approval and report QA remain human decisions.
