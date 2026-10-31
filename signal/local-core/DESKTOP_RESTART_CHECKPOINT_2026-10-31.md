# SIGNAL Desktop Restart Checkpoint — 2026-10-31

## Resume target
Repository: `veilresearchproject/veil-research-project`
Latest isolated development branch: `feature/signal-telemetry-validation-20261031`
Latest draft review: https://github.com/veilresearchproject/veil-research-project/pull/61

**This is a development checkpoint, NOT a finished Windows release.** Keep the previously working SIGNAL desktop folder/ZIP untouched. No draft branch has been promoted to a verified desktop package by this checkpoint.

## What existed before today's additions
- Local Ollama conversational prototype successfully ran on the user's Windows PC after local CPU-mode workaround; current Windows behavior must be rechecked.
- Existing SIGNAL desktop face, illustrative speaking sprites, opt-in Windows speech/microphone, MTC notebook, read-only log/scanner review and local setup diagnostics.
- v0.20 persona/version improvements in a draft development branch.

## October 31 draft sequence
- #56: offline operator PASS/FAIL/SKIP acceptance checklist
- #57: loopback Ollama exact-model readiness check without inference
- #58: personality contexts; deterministic illustrative face states; MTC operator-note review queue; read-only synthetic instrument telemetry schema
- #59: opt-in offline workbench exercising all four helper areas with synthetic input
- #60: input validation improvements, Windows focused-test batch runner and desktop handoff
- #61: invalid timestamp/instrument/face timing hardening and regression cases

The PRs are stacked draft branches; newest branch contains prior draft milestones, but still needs regression validation and integration review.

## Files for desktop work
Inside `signal/local-core/`:
- `four_workstreams.py`, `test_four_workstreams.py`
- `operator_workbench.py`, `test_operator_workbench.py`
- `model_readiness.py`, `test_model_readiness.py`
- `desktop_acceptance_check.py`, `test_desktop_acceptance_check.py`
- `RUN_PRE_DESKTOP_TESTS.bat`
- `FOUR_WORKSTREAMS.md`, `INTEGRATION_CHECKPOINT.md`, `PRE_DESKTOP_HANDOFF.md`

## Desktop procedure (in this order)
1. Back up the proven working SIGNAL directory and any research files; never overwrite it.
2. Obtain a **complete checkout or ZIP of this development branch** into a new folder; do not copy a few new modules over an older release. Existing launcher version/manifest still target the prior release.
3. Run `RUN_PRE_DESKTOP_TESTS.bat` and collect complete output. **New regression tests were written but not executed in the prior GitHub-only development sessions.**
4. Run the project's complete Python regression tests, JavaScript syntax and browser checks; investigate all failures.
5. Integrate helpers into the existing desktop UI rather than duplicating face animation, notebook or voice controls. Keep microphone and speech OFF by default.
6. Rebuild a fresh checked Windows package and test its manifest in a newly extracted folder; then use START_HERE.bat and explicitly start Ollama.
7. Confirm real local AI, chosen model, natural persona, speaking face, speech Stop/Disable, microphone consent, and MTC note review with copies/logs; never rewrite source evidence.
8. Do not enable hardware transport, alerts or automatic Panic Box ALL CLEAR. Telemetry helpers are unauthenticated, read-only prototypes.

## Status limits
GitHub commits and draft PRs exist. This checkpoint does not assert current tests passed, real Windows voice/microphone acceptance, hardware authentication, live browser wiring of the four new helpers, or a completed downloadable release.

## Suggested continuation request
“Resume SIGNAL from the October 31 Desktop Restart Checkpoint on branch feature/signal-telemetry-validation-20261031. Preserve the working desktop installation; run and fix tests first, then integrate and package a separate Windows build.”
