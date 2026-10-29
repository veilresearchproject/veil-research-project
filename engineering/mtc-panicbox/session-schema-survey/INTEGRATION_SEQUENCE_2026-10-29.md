# VEIL MTC/SIGNAL draft integration map — 2026-10-29
**Snapshot, not approval to merge or deploy.** Founder: Andrew Underwood, Founder & Lead Researcher.

## Dependency stacks confirmed from GitHub pull request base refs
- **Capture-health / structural WAV audit:** draft [#7](https://github.com/veilresearchproject/veil-research-project/pull/7) (independent JSON status watchdog) → draft [#9](https://github.com/veilresearchproject/veil-research-project/pull/9) (read-only WAV growth monitor) → draft [#13](https://github.com/veilresearchproject/veil-research-project/pull/13) (post-session split-WAV structural/hashing audit).
- **Offline MTC/SIGNAL review:** draft [#10](https://github.com/veilresearchproject/veil-research-project/pull/10) (post-session review/candidate clips) → draft [#12](https://github.com/veilresearchproject/veil-research-project/pull/12) (synthetic benchmark and split-session integration tests).
- **Independent main-based drafts:** [#4](https://github.com/veilresearchproject/veil-research-project/pull/4) SIGNAL synthetic sequence validation; [#6](https://github.com/veilresearchproject/veil-research-project/pull/6) local offline benchmark/preflight; [#8](https://github.com/veilresearchproject/veil-research-project/pull/8) reliability and storage design; [#11](https://github.com/veilresearchproject/veil-research-project/pull/11) transparent enclosure sourcing; [#14](https://github.com/veilresearchproject/veil-research-project/pull/14) physical Oct 27 evidence review gate; [#15](https://github.com/veilresearchproject/veil-research-project/pull/15) schema-only survey.

*Source: GitHub pull-request base/head metadata reviewed October 29, 2026. A GitHub “mergeable” indication is neither an approved release nor proof of operational safety.*

## Decision and validation order (no automatic merge)
1. **Preserve first:** Home Windows PC only. Stop MTC v0.1.4; inventory/retain original Oct 27 session, create complete review copy, compare SHA-256 original/copy, and log what was compared. See draft #14.
2. **Discover event schema:** After reviewing #15, optionally run it on copied JSON files; share only reviewed structural summary, not private source audio/questions. Inspect real field types and event markers. Do not assume simulated markers in #4/#10 match the real recorder.
3. **Verify recorded media:** In the split-WAV audit dependency stack, use reviewed code on a *copy*. Record exact frame durations, format, part numbers, inconsistencies; then compare with physical/audio seam checks and event logs. Structurally valid files never guarantee uninterrupted recording.
4. **Validate actual question playback and normal stop:** Check explicit event/result data and personally listen at known question times and both WAV seam sides; inspect any outside witness capture before calling a technical pass. No paranormal interpretation.
5. **Adapt offline clip screening only after schemas are mapped:** Review #10 then its dependent #12. Measure on known controlled noise, speech, and equipment-fault samples; distinguish benign environmental triggers, software artifacts and unexplained candidates. Maintain blinded controls.
6. **Release gates:** On an isolated/test installation only, run the full relevant test suite on home Windows, manually review file writes, privacy, permissions, physical risks, and rollback. Andrew decides separately whether any PR should be merged. Do not install or alter the live recorder based solely on synthetic Linux passing tests.

## Do-not-collapse categories
- **Synthetic software PASS** ≠ verified physical recording.
- **A parsed log** ≠ reliable session outcome.
- **An intact WAV** ≠ capture continuity, microphone health or audible questions.
- **A flagged sound** ≠ voice or EVP, and does not demonstrate paranormal origin.
- **Draft mergeability** ≠ founder approval.
- **Bench software** ≠ built MTC enclosure, staffed laboratory, multi-site autonomous control or validated system.

## Next blocking input
The real Oct 27 `session_result.json`, `session_metadata.json` and `events.jsonl` should be evaluated **on a copy at the home PC**. Their exact structure and values are unknown here. No source data was uploaded, and no live hardware accessed while writing this map.

**Boundaries:** $0 purchases, no public claims or outgoing outreach authorized by this map; no main-branch change, no merging any draft without founder review.
