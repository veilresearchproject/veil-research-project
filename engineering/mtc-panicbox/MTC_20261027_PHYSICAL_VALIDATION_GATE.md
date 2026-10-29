# MTC-001 — October 27 unattended recording: physical validation gate (DRAFT)
**Prepared:** October 29, 2026  
**Decision owner:** Andrew Underwood, Founder & Lead Researcher  
**Status:** checklist/protocol only; **not** a completed review, certified chain of custody, or paranormal finding.

## Why this document exists
The 90-minute home MTC v0.1.4 unattended test reportedly started around 9:50 p.m. on October 27, 2026 and saved a split room-mic WAV plus session logs. Reported file sizes alone cannot establish good audio, uninterrupted capture, played questions, an error-free stop, or an anomalous event. This gate separates **technical readiness** from later **exploratory audio review**.

No one needs the home workstation while this checklist is being drafted. All actual source-file inspection must wait until Andrew is at his **personal home Windows PC**, not an AJAX/work computer. Keep evidence off external/public services unless deliberately approved.

## Known input inventory (reported, NOT verified)
Session folder reported as `MTC_20261027_215040_70c105`:
- `room_mic_continuous.wav` — reported 337,501 KB
- `room_mic_continuous_part002.wav` — reported 168,753 KB
- `events.jsonl`, `session_metadata.json`, `session_result.json`, and a `questions/` folder
- Operator's rough notes: door-closing noise and dog thump; no other notable sounds recalled

A reported ninety-minute session and two appropriately sized files are **promising, not verified duration or continuity**. Exact sizes, dates, actual question timings, and session termination state remain unknown until inspected.

## Gate A — preservation before listening or tools
1. Confirm the app is stopped. Do not re-run it on the source folder.
2. Copy the **complete** session folder to a local review directory on the home PC. Retain the original untouched, including question source files.
3. Capture for each original and copy: relative path, byte count, SHA-256 (Windows PowerShell `Get-FileHash -Algorithm SHA256`), and when recorded. Hash matching confirms that the copy equals the original **at the time hashed**, not independent provenance.
4. Record the machine clock/timezone, MTC version, microphone and speaker devices, session settings, any power/sleep events, and whether an **independent** audio/video witness exists. If unknown, write UNKNOWN.
5. Never publish the original recording/logs or any identifiable background speech without privacy and consent review.

**Gate A PASS:** complete copy exists; recorded inventory and hashes match for original/copy; original preserved. **HOLD:** missing files, mismatched hashes, or uncertain provenance. Do not delete or silently repair any source.

## Gate B — machine-readable session and WAV structure
Use the **copy** of the stopped session only. Candidate development helpers are in draft PRs [#13](https://github.com/veilresearchproject/veil-research-project/pull/13) (post-session split-WAV structural audit) and [#10](https://github.com/veilresearchproject/veil-research-project/pull/10) (candidate-review pack); neither is merged/released for live use. Review their limitations before running. Avoid copying commands blindly until tested on home Windows.

Independently record:
- **WAVs:** actual order, all expected part numbers, RIFF/PCM format compatibility, sample rate, channels, frame count, duration computed from frames, and truncated/corrupt/missing-part warnings. Compare aggregate **frame duration** with intended 90 minutes and with timestamped start/end events; report differences rather than assuming the split is gapless.
- **Session metadata:** v0.1.4, selected input/output devices, run mode, actual settle/baseline/question delays, repetition, auto-stop settings, recording start times and time zone.
- **Result:** explicit normal-stop reason/status, errors/exceptions, actual end time, output paths. Do not infer a successful stop from file creation.
- **Event log:** parse every line; count question-cycle starts, questions issued/playback events (if logged), recording-start/stop/split events, stalls and errors; note invalid lines, missing event types, duplicate timestamps, and any clock resets. Compare logged questions with recorded audible questions later.
- **Capture health:** assess clipping, extended digital zeros/frozen samples, or suspicious level changes on the **copy**. Silence can be genuine room quiet; absence of these warnings does not prove microphone connectivity. A future supervised mute/disconnect control is necessary.

**Gate B PASS:** no unexplained structural failures, outcome status examined and consistent, no unexplained timing/duration discrepancy, event inventory made. **HOLD:** corrupt WAV, missing part, unresolved error, questionable timestamps or stop state. A WAV audit alone cannot certify acoustic continuity.

## Gate C — targeted listening and independent corroboration
Listen with headphones to **copied** audio only. Log actual file/offset, observation, and confidence; do not edit the source:
1. First 20–30 seconds after settling/baseline begins: audible room sound and absence of unintended occupants, if independently knowable.
2. One full question/playback interval: does the room microphone clearly record the question played through the speaker, plus the subsequent response window? Compare actual playback timing with logged question event.
3. **Both sides of the segment seam:** listen 20–30 seconds before the end of part 1 and 20–30 seconds at start of part 2. Listen for dropout, repeat, click, or missing acoustic progression; compare with event time. Seam listening alone cannot prove sample-accurate continuity.
4. Near the end: verify audio exists to the claimed finish, and if available compare with explicit normal stop event.
5. Investigate known house sounds (door close, dog thump) against remembered notes and any independent witness recording. Report uncertainty.

**Gate C PASS:** representative sound is intelligible, question playback audible in room-mic file, no observed seam defect, plausible end, and notes are logged. **HOLD:** question not audible, suspected gap/dropout, incomplete end, or ambiguous source needing review.

## Report outcome (do not confuse these categories)
- **TECHNICALLY VERIFIED (limited):** Gates A–C pass; report what was actually checked and what remains unverified. Does **not** prove a zero-gap recording or paranormal origin.
- **PROVISIONAL / NEEDS REVIEW:** one or more material questions remain open; preserve everything and identify specific next check.
- **TECHNICALLY FAILED:** documented source corruption, missing evidence, unresolved recorder stop or playback failure, or similar core failure. A failed test still provides useful engineering evidence.

Only **after** technical review, consider the separate scientifically blinded MTC pilot in [issue #2](https://github.com/veilresearchproject/veil-research-project/issues/2). Candidate clips are not evidence of a voice or EVP without matched controls, independent blind ratings, exclusion of normal explanations and replication. Keep recordings of prompts and other contamination in the review set; do not silently discard prompt-adjacent events.

## Home-session worksheet — complete later
| Check | Actual evidence / time / file | Status |
|---|---|---|
| Original and copy inventoried/hashed | NOT YET REVIEWED | PENDING |
| Recorder version, device and settings confirmed | NOT YET REVIEWED | PENDING |
| First/second WAV format and exact frame duration | NOT YET REVIEWED | PENDING |
| Split numbers/seam independently listened to | NOT YET REVIEWED | PENDING |
| `session_result.json` normal stop and errors | NOT YET REVIEWED | PENDING |
| `events.jsonl` counts and timestamps | NOT YET REVIEWED | PENDING |
| At least one emitted question audible in mic file | NOT YET REVIEWED | PENDING |
| End-of-recording representative sound checked | NOT YET REVIEWED | PENDING |
| Door/dog known-noise annotation | NOT YET REVIEWED | PENDING |
| Unresolved artifacts and limitations listed | NOT YET REVIEWED | PENDING |

**Next concrete at-home action:** inspect **copies** of `session_result.json`, `session_metadata.json`, and `events.jsonl` to establish the real event schema before adapting automated review. Do not assert a successful 90-minute recording until audio itself is inspected.

**Boundaries:** $0 authorized spend; no changed v0.1.4 recorder or Panic Box controls; no main-branch merge, device commands, external uploads, paid AI service, or public scientific claim. AI-assisted planning disclosed; founder review required.
