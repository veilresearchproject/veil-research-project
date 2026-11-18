# Research-history capture workflow

1. Verify selected Facebook identity and destination. Capture authorized VEIL activity.
2. Assign stable ID VEIL-RH-YYYY-FNNN for Facebook or VEIL-RH-YYYY-ANNN for editorial history.
3. Record actor, platform, parent post/comment, stable permalink and object ID. Deduplicate by platform/object ID or canonical URL; cross-posts stay separate linked records.
4. Preserve final posted/submitted wording rather than an assistant draft. Label partial capture and reconstructed whitespace. Keep missing values null.
5. Record event time with offset and displayed timestamp/precision separately from capture time. Use America/New_York for displayed dates. Do not turn relative labels into exact dates.
6. Preserve available original exports/media privately with SHA-256 hashes, source filenames, capture method and chain of custody. A screenshot alone does not establish original authorship or an unedited source.
7. Keep observations, interpretations and uncertainty separate. Apply reverse-image/source verification to investigative images and document search limits.
8. Append dated history for each reply, submission, delivery failure, decision, publication and follow-up. Distinguish pitches from manuscripts.
9. Check public suitability before commit. Private correspondence, unpublished/exclusive manuscripts, private-group content, personal information and witness evidence stay restricted.
10. Validate structured data, unique IDs and source references, review changes, commit and reread saved files.

## State and verification

Operational state and source verification are separate. Supported initial verification labels: verified_sent, verified_publication, verified_live_text_date_unknown, verified_feed_text_permalink_unknown. Future records may be unverified, reported_only or partial with explicit limits. A sent message does not prove delivery; a lack of reply does not establish rejection.

## Corrections

Append a dated correction and source; retain previous versions through Git history. Preserve manuscript versions and edited-post history. Mark later deletion/inaccessibility without erasing the prior observation. Git history tracks our revisions, not authenticity of the original platform.

## Routine capture

Retain draft status until posting/submission is verified. Check access on each new run. No daily monitoring or comprehensive automated capture is implied by this workflow.
