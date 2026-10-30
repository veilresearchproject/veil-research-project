# SIGNAL Desktop v0.10 — Review Packet and Ollama Rehearsal

This is an incremental, offline-first release on top of v0.9. Keep prior zip builds as backups. SIGNAL remains a prototype, **not** a live paranormal-event detector, safety monitor or verified acoustic analyst.

## New controls

1. **Test Ollama conversation:** Expand *Local readiness check* and click the button. This sends a fixed, harmless evidence-limits prompt to the local Ollama model, without any session logs, investigator notebook notes or memories. It does not enable Windows speech, invoke the microphone, retain a conversation, write any file or contact a paid API. The returned text confirms model connectivity only, not factual accuracy. Demo mode refuses this test.
2. **Export an investigator review packet:** Load verified MTC logs, optionally import the matching v0.3 scanner report, and add human observations. Expand *Export an investigator review packet* and choose **Save structured JSON** or **Save printable report**. The browser downloads the generated file explicitly. Export includes *all* notes from the session, even though the screen shows the most recent 100.
3. **Evidence provenance:** The export identifies the log-consistency checks, scanner-report SHA-256, grouped acoustic flags, separately entered human notes, and important limitations. It includes a SHA-256 fingerprint over the exported *summary fields*. That fingerprint is **not** a source WAV hash, signature, or tamper-proof chain of custody.

## Controls and limitations

- Raw WAVs are not opened, rescanned or modified by this update.
- No browser-visible command executes on the filesystem; exports are generated in memory on demand and downloaded to the operator's PC using the browser's download feature.
- Signal never auto-exports a packet and never auto-approves a microphone transcript.
- Report-generated prose and manual notes are treated as data and escaped in printable HTML.
- The optional model test does not claim that an Ollama response is true, grounded, or evidence of an anomaly.
- For safety, no hardware commands, Panic Box ALL CLEAR, continuous microphone listening, automatic research classifications, or remote service endpoints were added.
- The v0.7 subtle mouth frames and all approved facial artwork are unchanged.

## Validation

- 101 Python standard-library automated tests passing, covering prior functionality plus packet content/fingerprints/all-notes, HTML escaping, HTTP authorization, malformed export requests, manual model test isolation, and source-file immutability.
- JavaScript syntax check (`node --check signal_face.js`) passed.
- The test container's Chromium could not navigate to the local test server (`ERR_BLOCKED_BY_ADMINISTRATOR`). Therefore actual browser interaction and Windows/Ollama/mic/speaker hardware remain to be tested on the VEIL PC.

## Safe Windows acceptance plan

1. Extract the ZIP to a **new folder** and run `CHECK_SIGNAL_SETUP.bat`.
2. Start Ollama manually. Confirm `ollama list` includes `llama3.2:3b` (or review the configured model before downloading anything).
3. Run `START_SIGNAL_DESKTOP.bat`. Under *Local readiness check*, click **Check local setup**, then **Test Ollama conversation**.
4. Keep voice and mic **OFF**. Ask SIGNAL a harmless controlled question to confirm the local conversation.
5. Only after typed text works, turn on voice and separately test Windows speech. Review the subtle facial movement and switch **Motion: still** if distracting.
6. Load October 27 MTC logs, import matching scanner `review_summary.json` only if already generated, add/confirm notes, export a JSON packet and a printable HTML packet. Verify the browser downloads and that the audio files are untouched.

If anything fails, use the saved v0.9 ZIP and report the exact error. No Work credits were required for this incremental development milestone.
