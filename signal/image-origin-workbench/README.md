# SIGNAL Image-Origin Research Workbench v0.1 (research-only)

Status: **isolated review prototype**. No website deployment, Ollama integration, online reverse-image API access, automatic source crawling, user accounts, cloud storage, payments, equipment control, or publication mechanism.

## Why this exists

A normal text web search is **not** the equivalent of Google Lens. Uploaded images can be cropped, reposted under unrelated captions or stripped of metadata. A user might find a matching *section* when the whole image matches poorly. This tool gives investigators a repeatable, transparent manual-search workflow rather than falsely claiming SIGNAL can operate Google Lens itself.

## Six implemented research updates

1. **Local image registration**: browser SHA-256 of original bytes, dimensions and file size; originals are never included in the exported report or uploaded by the app. Checksum = byte identity, **not** proof of authenticity or chain of custody.
2. **Region search**: browser drag/touch selection; PNG crop downloaded locally; original-pixel coordinates and derived crop SHA-256 logged. Whole image search still required.
3. **Multi-provider human handoff**: clearly labeled links to [Google Lens](https://lens.google.com/), [TinEye](https://tineye.com/), [Bing Visual Search](https://www.bing.com/visualsearch), and encoded Google/Bing keyword queries. Investigators upload images manually to each outside service; **no automatic uploads**.
4. **Traceable source log**: visual match relationship, source URL, category, documented date/date basis, capture time of research record, claimed creator, caption, region and notes. No automatic scraping and no unverified source promotion.
5. **Conservative origin assessment**: earliest *entered adequately dated* matching result, warnings for conflicting captions and incomplete searches. Never equates earliest discovered page with original photographer/date, and never infers a paranormal cause.
6. **Audit and reporting**: export portable JSON log and private Markdown draft; operator-entered reviewer details explicitly unauthenticated; publishing remains disabled.

## Open and test

Run `python -m http.server 8766` from the repository root, then visit `http://127.0.0.1:8766/signal/image-origin-workbench/`. Use a localhost or HTTPS browser context for SubtleCrypto hashing. This is a local static development server, **not** SIGNAL's existing Ollama port 8765. Alternatively, when on a review branch, a local copy may be tested from disk but browsers may block SHA-256 under file:// contexts.

On Windows (with free Python already installed), run `py -3 -m http.server 8766` from the repo directory. Keep the server bound to loopback when handling real evidence: `py -3 -m http.server 8766 --bind 127.0.0.1`. Never bind confidential case data to all network interfaces.

To run verified pure-logic tests: `node --test signal/image-origin-workbench/test-core.js` from repo root. Requires Node 18+ **for tests only**; app itself uses browser built-ins. Core tests include URL policies, date accuracy, crop bounds, chronology, origin uncertainty, source injection resistance, checklist limitations and reviewer safety. Tests do not establish browser device compatibility.

## Operator checklist

- Preserve original media, consent, URL source pages and chain of custody outside this tool.
- Load whole original; record local byte checksum; do Lens whole image; note if Lens selected a smaller section.
- Crop at least one distinctive region; upload it **yourself** and repeat search; record the exact region/variant used.
- Repeat with TinEye/Bing and search distinctive text/captions; compare alternate crops, edited derivatives and changed captions.
- Verify publication dates with primary publisher records and independent archives when possible. An archive capture proves availability by that date, not creation date.
- Record each match, non-match and inaccessible service separately. Save original pages/screenshots only where permitted.
- Identify what was directly observed, what was claimed and what has *not* been established. Do human review before public statements.

## Privacy and scientific limits

This prototype loads image data entirely locally in the browser and never calls fetch or external image-upload APIs. Clicking an external provider opens their website, where privacy terms and uploads are separate user actions. No local storage/cookies/database are used by this workbench, so leaving the page loses unfinished work unless exported. Browser extensions, hosting infrastructure and selected external sites are outside this prototype's privacy guarantees.

A social post's visible date may not be its original posting date. The earliest traceable web appearance is NOT proof of origin. A partial match and an altered crop may involve different source contexts. OCR or visual interpretation must be independently checked. Even a verified identical file SHA-256 is not independent confirmation of cause or authenticity.

The researcher must manually enter valid dates/URLs; validation checks format, not truth. This is not a credentialed reviewer or real digital signature. Do not publish third-party images without permission. Never put sensitive case files or personal information in a public repository.

## Sources for human workflow (checked November 17, 2026)

- Google Search Help: https://support.google.com/websearch/answer/1325808?hl=en
- Chrome Help on Lens/region selection: https://support.google.com/chrome/answer/15086890
- TinEye how-to: https://tineye.com/how
- Bing Visual Search help: https://support.microsoft.com/en-us/bing/using-bing-visual-search

## Integration gate

Only after a human validates this workflow on desktop and Samsung mobile may the team plan an optional link inside SIGNAL's UI. Keep file handling on-device. A future authenticated agent may use permitted search APIs or operator-supervised browser actions, but must never claim it searched Google Lens if it only ran a text or general image search. Any online search requires explicit consent and source/date logs. Keep existing `signal/index.html` unchanged while testing.
