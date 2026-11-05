# SIGNAL v30 — Clock correction and uncertainty review

**Development preview only**. New `clock-core.js` and `v30.html` extend v29 (which extends prior unmerged draft branches). The real Windows v25 desktop installation and public VEIL website have not been modified. No API keys or paid services.

## Why
Two time-stamped observations can appear to align because recording devices have different clock settings. v29 compares reported timestamps directly; v30 adds deliberately entered clock profiles by source, with a **signed offset** and **estimated uncertainty**, before computing a candidate interval.

**Correction**: corrected UTC estimate = parsed source timestamp + `offsetMs`.
**Distance band for two sources**: `[max(0, |corrected A − corrected B| − (uncertainty A + uncertainty B)), |corrected A − corrected B| + (uncertainty A + uncertainty B)]`.
A pair is listed when the lower end overlaps the user-selected proximity window. It is classified as within-estimated-bounds only when the upper end also lies inside it; neither class means an actual event match or verified clock sync.

## Instructions
Place the provided files beside the existing `server.py` bridge, or copy the entire contents of the ZIP into a *new folder alongside* the existing installation. Do not overwrite v25 or another preview. On Windows, double-click `START_SIGNAL_V30_CLOCK_REVIEW.bat`; browse to `http://127.0.0.1:8770/`. Optional Ollama uses installed model `llama3.2:3b` if no `SIGNAL_MODEL` environment variable was set; CPU-only Ollama configuration remains external. The clock review itself works in scripted mode without Ollama.

Start/import a Casebook, enter observations with **explicit timezone timestamps and source labels**, then enter source profiles. A plus correction shifts a device's reported time *later*; an unknown method is excluded. Give an explanation for entered offset/uncertainty values. Select a proximity window, press **Compare with clock estimates**, and optionally download. Changes to the Casebook, profiles, or window invalidate the earlier export; rerun first.

## Safety and scope
- All metadata and clock profile values are **human-entered**, not measured by SIGNAL. The software does not open original evidence, ingest devices, synchronize clocks, or prove an observation is independent.
- No hardware control, background recording, cloud transfer, filesystem scanning or automatic persistence. The user's browser may invoke TTS through its installed voice engine, which is a separate service.
- Fingerprinting remains limited to selected files of at most 25 MiB; fingerprints do not establish authenticity.
- Up to 30 Casebook notes and 30 clock profiles. Missing/unknown clock profiles do not get silently treated as synchronized.
- Tests use synthetic timestamps and browser simulation. Windows/Ollama/voice real-device integration is still pending.

## Checks
Run `node test_clock.cjs` for the new mathematical and safety checks; `node test_v30.cjs` for UI contract checks; `python browser_smoke_v30.py` for Chromium synthetic UI test (requires Playwright and Chromium). Inherited test scripts `test_casebook.cjs`, `test_fingerprint.cjs`, and `test_correlation.cjs` are retained.