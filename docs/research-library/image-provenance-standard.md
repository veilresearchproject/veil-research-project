# VEIL Research Project — Image-Origin & Reverse-Search Standard

**Version:** 0.1 draft — November 17, 2026  
**Applies to:** submitted, shared, found and investigator-created images before source-history claims are published.  
**Status:** standard proposed for human review; does not authorize posting images or uploading private evidence.

## Required workflow for every image inquiry

1. **Permission and preservation** — obtain appropriate consent/authority; preserve original file, receipt time, source channel, original filename, size and SHA-256; keep a private custody log separate from any public report. Avoid unnecessary uploads of faces, home interiors, minors or confidential evidence.
2. **Separate what is shown from what is claimed** — record exact claim, first link provided by submitter and observable visual facts; never label AI output as a direct observation.
3. **Whole-image reverse search** — operator uploads image to **Google Lens** and records screenshot/query region, search time, matches, error/blocked status. General web/image search alone does **not** fulfill this step.
4. **Partial-image and variant search** — repeat Lens with a deliberately selected distinctive crop (Google may initially choose a different region), plus cropped/rotated/re-captioned variants where useful. Record the crop coordinates and a hash of any saved derived copy. Preserve the uncropped original.
5. **Independent visual engines** — search TinEye and Bing Visual Search where lawful and possible; distinguish genuine visual matches from similar subjects. Record failures rather than silently assuming “no results.”
6. **Caption/history search** — search quoted captions, place names, object descriptions and notable features; seek prior posts, syndication, memes, artwork, stock/photo-library uses, alternate stories and credible original photographers.
7. **Dated source assessment** — verify claimed posting dates against publisher pages and independent archives when available. An archived capture establishes the image existed **by the capture date**, not the date it was photographed. The first *found* repost is never automatically designated the original.
8. **Media integrity/context** — inspect whether the image is edited, AI-generated, composited, miscaptioned, cropped or context-dependent when evidence permits. File metadata is fallible; hash identity is not photographic authenticity. If not measured, state 'not evaluated'.
9. **Competing explanations** — separate visual coincidence, camera artifact, staged scene, mundane sources and unresolved questions. Report contrary matches and negative/blocked searches, not only supporting results.
10. **Human review / publication gate** — independently review significant claims, log sources, timestamps, limits, image rights and corrections. Obtain publication consent; remove private personal data. Output classification can remain **inconclusive** without weakening the report.

## Required reporting fields

`case_id`, original file checksum and preservation record (private), acquisition method and permission, search provider/query/crop/time, source URL, capture/archive/publication date plus date basis, original/repost/altered/context-only match assessment, alternate captions, competing ordinary explanations, image transformations, analysis method, confidence limits, reviewer and corrections, publication authorization.

## SIGNAL automation limits

SIGNAL may calculate local fingerprints, generate crop files, prepare text searches, validate evidence logs and generate draft reports. It must not claim to have conducted Google Lens visual search unless a human actually completed it or an authorized technically verified integration did so. Search engines' UI/API and permissions can change. **Never** upload private evidence automatically or publish claims without human approval. Source discovery is not evidence of paranormal activity.

**Local prototype:** `signal/image-origin-workbench/` (branch review).  
**Background support:** Google Search Help (image upload); Chrome Help (Lens region selection); TinEye/how; Bing Visual Search Support.

## Example report language

> An image with similar/identical visual content was located on [source] by [documented date]. This is the earliest adequately dated appearance identified during the searches recorded here, **not necessarily the first publication or original photograph**. The location, photographer and circumstances of capture remain [known with sources / claimed but unverified / unknown].

## Draft workflow update — case continuity and source independence (November 17, 2026)

- Preserve the JSON export privately. For a resumed case, require the same original image checksum, byte size and decoded dimensions before restoring source notes. This is a local consistency check, **not** proof of authenticity.
- Reset any imported human review and repeat the review after changes. Never import a publication approval from a self-declared field. Crop hashes and coordinates may be retained, but the actual derived crop file must be generated again if not separately preserved.
- Record archive capture date, on-page publication date and independently corroborated date as distinct evidence classes. A site appearing in an archive says nothing conclusive about photograph capture time.
- Flag repeat URLs and common hostnames. Several reposting websites are not independent evidence of the underlying scene, and a creator claim alone does not establish authorship.
- Current prototype tests: 56 offline SIGNAL unit/static checks passed; real desktop and Samsung UI, image search engines and source-page authenticity still need direct verification.
