# SIGNAL — pre-desktop handoff (October 31, 2026)

**Keep your currently working SIGNAL folder as-is.** This development branch is stacked on drafts #55–#59 and is **not** a validated release ZIP. Do not copy individual files over an existing installed package: the checked launcher uses a manifest and version checks.

## Changes ready for development review
- Existing desktop app already has opt-in Windows TTS, illustrative speaking-face sprites, explicit MTC note entry, scanner flags and local model diagnostics.
- Additional pure helper layer: personality policies, four-state pose scheduler, MTC operator-note review queue, and strictly read-only future instrument telemetry schema.
- Opt-in offline operator workbench to exercise the helpers together using synthetic fixture input, NOT original research logs.
- Read-only loopback Ollama model-tag availability diagnostic.
- Human-reported offline acceptance checklist.
- New one-command focused test launcher `RUN_PRE_DESKTOP_TESTS.bat`.
- Hardened workbench duration validation and bounded fixture file reading.

## On desktop, before changing the working installation
1. Preserve the earlier working SIGNAL ZIP and folder.
2. In a **separate complete checkout** of the development branch, run `RUN_PRE_DESKTOP_TESTS.bat`. Record the full console output. Do not mix this with an old release ZIP.
3. Run the project's *existing full regression suite* (not only the focused tests). If anything fails, do not promote the build.
4. Package a fresh release using the existing project packaging workflow and validate its manifest from a new extraction folder.
5. Start the packaged app via START_HERE.bat, select the local model, and check a real Ollama reply. Voice and microphone remain off until separately opted into.
6. Check both casual and safety-critical prompts; confirm no fictional access to evidence or automatic ALL CLEAR.
7. Enable voice only by choice, observe the already existing speech sprites, and verify that Stop speaking/Disable voice are responsive. Explicitly test the reduced-motion setting.
8. Load a *copy or structured log* of a real MTC session into the existing read-only review interface. Do not modify original WAVs or source event JSON. Check annotations and clear context.
9. Keep the future instrument transport disabled. The prototype schema neither authenticates devices nor controls them.

## Release blockers
- New helpers are not yet wired into the browser's live conversation, MTC notebook or face animation; the operator workbench is a developer dry-run.
- New Python regression files have been committed, but have **not been executed by the GitHub connector**. No claim of passing tests or functional Windows compatibility is made.
- Actual Windows microphone, speaker, Ollama performance and future instruments require local acceptance.

## Local dry-run example
Create `example.json` containing:
```json
{"observations":[{"timestamp_s":31.25,"description":"One click noticed by operator; cause unknown"}],"telemetry":[{"instrument_type":"mtc","device_id":"MTC_1","timestamp_utc":"2026-10-31T15:00:00Z","measurements":{"status":"ready"}}]}
```
Then run from `signal/local-core`:
```bat
py -3 operator_workbench.py example.json --subject research --speaking-ms 140
```
Outputs a read-only JSON review scaffold. **It is not live SIGNAL behavior or a hardware test.**
