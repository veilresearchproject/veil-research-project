# VEIL HORIZON — Global Historical Anomaly Research Network

Date: 2026-11-22
Status: Proposed roadmap; not implemented or validated.
Scope decision: Worldwide from inception, not Pennsylvania-only.
Visibility: Planning draft on isolated GitHub branch. No merger or website publication authorized.

## Purpose
Build an offline-first, source-traceable research database and controlled discovery engine for historical and contemporary reports of alleged anomalous phenomena. Cross-compare locations, occupant transitions, families across generations, phenomena types, photographs and other media, while systematically testing normal explanations and transmission of stories.

## Why global from the start
VEIL already communicates with paranormal groups internationally. Restricting records to Pennsylvania would systematically exclude cross-border analogues and collaborator contributions. Design schema, ingestion and search for multilingual, multi-country data at launch; expand ingestion connectors in tested batches rather than claiming unlimited web crawling.

## Proposed record model
- Source: stable URL, archive ID, publisher, capture date, original publication date, author attribution, permissible license/use status, retrieval metadata and checksums where legal.
- Event: reported date/time ranges, independent witnesses (privacy-preserving identifiers), report type, description, source provenance, verification status and uncertainty.
- Place: geographic coordinates with accuracy estimate, historical/current name and borders, jurisdiction, address changes, geology and environmental context as available.
- Timeline: building occupancy and transition periods, records of reports and equally important quiet/non-event periods; avoid publishing living occupants' private addresses.
- Family/people: consent/authority basis, pseudonymous linkage for living persons, archival sources for deceased historic subjects; protect vulnerable subjects.
- Image: original-source reference, derivative/crop relationships, perceptual hashes and similarity metrics; NO automatic personal identity conclusions from face similarity.
- Comparison: hypothesis ID, matching features, independence assessment, alternative explanations, algorithm/model versions, confidence and human reviewer decision.
- Links between locations, accounts and images are *candidate correlations*, never evidence of paranormal causation by themselves.

## Geographic and language design
Support global UTC-normalized timestamp plus original local date/time/timezone; language tags, original-language quotations and source-linked translations; uncertainty in dates, names and geocoding. Treat shifted borders, transliteration and changing place names explicitly. Prefer permissions-based contributions from VEIL's global contacts.

## Initial phased build
1. Source catalog and safe connectors: approved archival APIs, open-access newspapers, historical libraries and opt-in partner submissions, respecting robots, terms, rate limits and copyrights.
2. Database and provenance: structured records, relational relations, full-text search, access controls, encryption for private records, backups and export.
3. Image-history workflow: exact matches and perceptual similarity, edited/cropped detection, manually verified earliest *known* appearance and attribution, false-positive benchmarks.
4. Correlation engine: APH-001 location-versus-family/occupant-transition and intergenerational reports; preregister comparison logic, negative controls, base rates and independence checks.
5. SIGNAL research interface: natural-language questions with source citations, uncertainty and human sign-off; read-only by default.
6. Scheduled monitoring on an authorized always-on host, with review queues, safety limits, observability and budget caps.

## Research integrity and safety
- Store only content authorized for collection, and public links/metadata in place of unauthorized full-media copies.
- Do not defeat access controls or scrape private groups. Handle opt-in submissions, privacy/retention/deletion and international data protection requirements deliberately.
- Do not infer genetic paranormal traits, claim specific identities from repeated apparition images, or equate resemblance with a shared entity.
- Distinguish first-person testimony, newspaper retellings, folklore, fictional sources and derivative reposts.
- Record source dependency to avoid amplifying the same story as multiple independent cases.
- Require human scientific review and a documented conventional-explanation analysis before labeling a report noteworthy.
- Private project research must not be exposed on the public site or public repository without separate authorization. This roadmap contains no confidential investigation data.

## First measurable pilot (global, bounded)
Curate permitted sample records from multiple countries and at least two languages, including known duplicates/retellings, non-events and control cases. Test source tracking, translations, geographic normalization, image reuse detection and cross-border query accuracy. Report false matches and missing data before scaling.

## Current limitation
No crawler, worldwide archive integration, global database or recurring ingestion has been implemented under this entry. Building a system that runs continually requires an authorized host and source-by-source permissions; ChatGPT chat alone is not an unrestricted background internet agent.
