# VEIL Research Project — SIGNAL v0.5 + Research Library private pilot handoff
**Prepared:** November 17, 2026 · **Status:** Review-only; not deployed, merged, or approved for actual evidence intake

## What is actually ready in software
The independent Windows ZIP supplied to the founder in the November 17 conversation, `VEIL_SIGNAL_Research_Demo_v0.5_Windows_2026-11-17.zip`, packages the existing local SIGNAL Conversation Lab v0.4 plus a **synthetic-only** evidence panel. It adds a source SHA-256 fingerprint, deterministic temperature-step screening, a private printable simulated report, manual generation of a possible model discussion prompt, explicit uncertainty, and research provenance. It preserves browser-confirmed local voice output, manually approved notes, temporary context, and local Ollama conversation. It runs separately from home-desktop SIGNAL v25 and uses loopback 127.0.0.1:8766.

The companion `VEIL_Research_Library_Private_Pilot_Windows_Handoff_2026-11-17.zip` contains a safety-checked local acceptance wrapper and scorecard for this branch's existing `tools/evidence-review/pilot.py` and `rehearse.py`. It does NOT contain or replace PR #118 source. The repository and handoff package must be placed in separate local folders.

## Verification performed November 17
- SIGNAL v0.5: 60 existing conversation tests plus 21 new deterministic audit, checksum and read-only HTTP checks passed (81/81) in Linux development environment. JavaScript syntax and Python compilation passed; a fresh ZIP extraction passed the same suite and package SHA-256 checks.
- Private pilot acceptance wrapper: 8/8 local safety tests passed (repository source layout, safe private-workspace separation, symlink escape rejection).
- The original PR #118 branch's prior history reports an offline synthetic encrypted intake, SIGNAL CSV analysis, reviewed report, encrypted delivery/receipt, and restored backup; those original tests and rehearsal were **not freshly executed as part of this v0.5 package** because its checkout was not locally available for this iteration.
- Chromium browser navigation was blocked with ERR_BLOCKED_BY_ADMINISTRATOR in this development environment. Actual browser click, Edge/Windows batch, installed Ollama, voice, Windows filesystem ACL and hardware tests remain open.

## Two safe paths at the desktop
**SIGNAL demonstration:** Extract the separately supplied v0.5 ZIP into a new folder, never over v25. Run CHECK_SIGNAL_WINDOWS.bat (81 tests), start the independent loopback local chat, inspect synthetic evidence, manually prepare an unverified question, and open the printable simulated report. Do not use actual submitted evidence in this demo.

**Private Library rehearsal:** Download the exact PR #118 feature branch; consult [private-pilot.md](private-pilot.md). On a private Windows PC with Python 3.10+, Node.js and OpenSSL 3, run `py -3 -B tools/evidence-review/rehearse.py --workspace "$env:LOCALAPPDATA\VEIL\Rehearsal" --keep-report`, then `py -3 -B tools/research-library/validate_catalog.py` and the documented read-only catalog preview. The companion handoff includes a wrapper to run existing regression suites plus this full synthetic rehearsal. This run is **not** public submission and makes no payments.

## Guardrails before real case intake
- Verify participant permission, source rights and submitter authority; preserve pristine originals and recorded full SHA-256 digests.
- Restrict local operator file ACL and encrypt the volume, backups and the handoff channel; verify recipients, keys and restore.
- Have a genuinely separate human reviewer inspect the original and all interpretations; never label a simulated persona an independent reviewer.
- Preserve source device, clock uncertainty, acquisition context, AI or deterministic provenance and dissenting reviews. Compare competing ordinary hypotheses and control results.
- Secure independent review of the pilot code and privacy/retention policy before real human-subject materials, website uploads or billing.
- Site publishing, payments, automatic transmissions and lab hardware control remain **OFF**. No merge/deployment without owner approval and real-PC acceptance.

## Completion criteria
The software demonstration is **packaged and offline-tested**, not physical-hardware-validated. The Research Library private pilot is **available as a draft branch with synthetic rehearsal**, not launched as a public service. Full completion requires Windows validation, rights/security review, signed genuine human decisions and explicit owner authorization. 
