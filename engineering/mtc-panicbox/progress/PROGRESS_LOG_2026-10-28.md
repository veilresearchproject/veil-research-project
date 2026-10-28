# VEIL Research Project — Engineering and Outreach Progress
**Date:** Wednesday, October 28, 2026  
**Status:** Standalone development and synthetic tests; no physical hardware tests, purchases or new MTC software deployment.

## Completed today

1. Preserved the requirement that MTC be assembled in a **fully transparent, expandable case** with clear service access and visible internal equipment. Earlier 16-inch prototype dimensions are not the final maximum; allow future sensors/storage/interfaces. The first electrical design keeps powered mains and the LiFePO4 battery module external to the clear electronics housing and the microphone/speaker externally located to reduce fan contamination.
2. Transparent enclosure supplier outreach earlier Oct 28: confirmed **SENT** to Gannon MakerSpace, Blanchard Manufacturing, Tarantula Cribs and Pleximart. ClickFold, Bud Industries and HerpCult are drafts after send errors, not delivered. Erie Industrial Plastics requires phone or contact form. No donation confirmed.
3. Existing MTC/SIGNAL offline v0.2 review suite: **46/46 pass** on an isolated Python environment (Oct 28 replay).
4. New deterministic SIGNAL benchmark harness: 11 tests added and passing. **36 synthetic cases:** 12/12 deliberately obvious audio changes flagged; 0/12 silent/steady controls flagged; only 4/12 exploratory cases flagged. Quiet tones 0/4, microphone loss 0/4. This exposes an important false-negative risk: no amplitude-rise detector can substitute for a microphone health watchdog.
5. Added six 90-second **synthetic** split-session end-to-end tests, all passing: 60-second first file, 30-second second file, fake question marker, normal-looking synthetic end marker, candidate CSV, optional clips outside evidence source, SHA-256 original-file preservation, and missing-segment failure. These are not the actual October 27 90-minute session.
6. **63/63 total test cases pass** (`python -m unittest`), and new files compile. No active recorder, public website, user’s work laptop, live SIGNAL persona, or Panic Box firmware changed.
7. Progress workbook saved as `VEIL_Engineering_Progress_2026-10-28.xlsx`, including a measured synthetic test matrix, next engineering gates and supplier inquiry statuses.

## Decision gates (in order)

- [ ] **Actual MTC evidence review:** Obtain copies of `session_result.json`, `session_metadata.json`, `events.jsonl` from Oct 27. Validate actual stop status, question timing, error counts, and correct event vocabulary. **Still blocked; no files received in this task.**
- [ ] **Audio validation:** At personal home PC, use a copy of both completed WAVs and manually listen to segment boundaries, then correlate independent video/audio and logs. Never claim proven gaplessness based on file sizes or apparently smooth sound levels.
- [ ] **SIGNAL acoustic calibration:** Record *known* quiet voice, HVAC, cabinet knocks, intermittent network/power noise, fan noise, and silence. Include a blinded reviewer and log false positives/misses, not paranormal claims.
- [ ] **Independent health alarms:** Use separate status evidence/watchdog to catch silent mic disconnection, stalled WAV writer, power failure, or audio dropout. Existing draft read-only watchdogs are synthetic tested, not field deployed.
- [ ] **Clear enclosure engineering:** Select actual Windows mini-PC and peripherals, measure interior clearances, power draw, ventilation and acoustic effects; reserve future service/expansion volume before any donated case is accepted or purchased.
- [ ] **Outreach:** Check email replies and rejected messages (including Spam) through VEIL's existing outreach-watch workflow; do not resend or represent unsent Gmail drafts as sent.

## Verification boundaries

All benchmark numbers reflect generated test tones and pulses, **not field evidence**. No real hardware or long endurance run occurred today in this environment. Commercial product listings and supplier engagement are unconfirmed until the actual supplier accepts. VEIL remains an independent research initiative developing prototypes, not an operating staffed physical research center.
