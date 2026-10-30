# SIGNAL Pocket Review — offline phone prototype v0.1

**VEIL Research Project · October 30, 2026 · isolated development branch, not published.**

## Milestone

An entirely self-contained mobile-friendly `index.html` file that can display **read-only scanner candidate timestamps** without running Ollama, starting a desktop server, uploading a recording, or using a paid API. This is a *review companion*, **not** a live SIGNAL chat, audio player, scientific conclusion, or remotely connected instrument dashboard.

### Use

1. Obtain `index.html` from this branch and save it locally (do not publish it to the VEIL website). Open the file in a modern browser. Some Android browsers/file managers may restrict local HTML opening; Samsung Galaxy S25 behavior **has not been tested**.
2. Select **Try synthetic demo** to see three invented scanner flags grouped into two review windows. The synthetic label is prominent.
3. To review your own session, first generate a `review_summary.json` using the separate MTC local scanner v0.2/v0.3, then **manually** copy only that JSON file to your phone. Tap **Choose scanner report**. The report is parsed locally, without an upload.
4. Select the start time field of any window to copy or transcribe it for later review of the **original audio on the desktop**. Tap **Clear review** to remove displayed data.

### Safety and scientific limits

- **Do not copy sensitive raw audio, private conversations, or unconsented recordings to a phone.** Scanner reports may still contain sensitive session metadata. Keep files private and follow VEIL's recording permissions and retention procedures.
- Structural validation is not independent evidence verification. This mobile viewer does **not** cross-check the MTC event logs, original WAV hashes, or recording authenticity; it prominently marks imported reports **UNVERIFIED**.
- Scanner flags are acoustic outliers, **not identified voices, EVP, or paranormal evidence**. No automated interpretation of causes.
- The page performs no network requests, uses no third-party scripts, does not store imported data in browser storage, and never modifies the selected report. Its Content Security Policy blocks network connections. No microphone, camera, file writes, or hardware controls.
- Unlike the Windows desktop, this prototype does not communicate with local Ollama. Do not expose the existing desktop service to a LAN or internet to make it accessible to the phone; it intentionally binds to `127.0.0.1`.
- Clearing the page removes in-memory data displayed in this tab; it **does not delete the imported file** from the phone or guarantee browser-memory erasure.

### Tests (no dependencies)

Run `node --test test_pocket_review.cjs` from this directory. Tests cover accepted scanner schema, overlapping grouping and original indices, bad values, oversized candidate sets, safe display constraints, and the synthetic/unverified labels. The app is also suitable for a local Chromium smoke test; actual Android and original MTC data validation remain pending.

### Next milestone

On a personal device, verify local HTML opening and file-picker behavior on Samsung S25. If successful, design a *separately approved*, authenticated and read-only local-network pairing path for live status; do not relax the existing desktop loopback-only service without a security review.
