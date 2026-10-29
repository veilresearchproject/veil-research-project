# SIGNAL local evidence ledger — phone-side proof of concept (2026-10-29)

Status: design/prototype plan, **not** hardware-validated. No Solos hardware purchased or connected.

## Objective
Build an offline-first Android companion that accepts camera/audio artifacts from smart glasses or the phone, documents capture provenance, and correlates evidence with independent VEIL instrumentation.

## Engineering facts supplied by Solos SDK lead (2026-10-28)
- Android and iOS SDK documentation v5.9.2 provided by Russell Gapasin.
- Photo capture, video recording and Wi-Fi video transfer are exposed; microphone and speaker use BLE.
- JPEG output is not raw and does not embed a trustworthy acquisition timestamp.
- BLE photo transfer offline is limited to 1.2MP; 16MP transfer uses Wi-Fi.
- Video segment cap: 20 minutes, with storage-capacity limitations.
- Media transfer to the companion app has no mandatory Solos cloud data path.
- Simultaneous microphone/video operation, capture timestamps, interruption signals, and research-publication terms are awaiting clarification.

## V0 acceptance criteria
1. Each imported item gets a unique event ID, device ID, recording-session ID, source, host UTC wall-clock acquisition/receipt time (explicitly labeled), monotonic timestamp for local ordering, media size and SHA-256 hash.
2. Preserve original bytes untouched in a read-only logical evidence location; write metadata separately as append-only JSONL.
3. Label *host receipt time*, *device capture time*, and *estimated event time* distinctly. Never invent device timestamps.
4. A session state machine logs START, STOP, DISCONNECT, RECONNECT, capture errors, clock correction and missing-segment intervals. Do not silently bridge data gaps.
5. Phone microphone / camera simulator permits development without Solos hardware; switch to glasses adapter only after SDK review and authorized evaluation.
6. Allow export of the entire session, checksums and schema version; no cloud APIs required.
7. Audio, environmental sensors, Temperature Curtain, light cage and MTC all use the same session ID and synchronization test event; correlate with documented clock uncertainty.

## Immediate implementation sequence
- Implement a local JSONL ledger and file-hash manifest with unit tests.
- Prepare Android bridge contract: `captureArtifact(bytes, deviceId, sessionId, source, receiptTimeUtc, monotonicNs)`.
- Build simulated BLE disconnects, missing video segment, 20-minute rollover and timestamp drift tests.
- Review SDK documentation and permissions; avoid copying proprietary SDK materials to a public repository.
- Only then seek donated/loaned equipment and conduct a documented pilot.

## Evidence integrity warnings
A SHA-256 checksum detects later byte changes, but cannot prove a claimed paranormal origin, prevent fabrication before ingest, or establish absolute capture time. Independent continuous reference video/audio and calibrated sensor clocks remain necessary.
