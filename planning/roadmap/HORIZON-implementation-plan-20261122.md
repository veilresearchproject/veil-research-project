# VEIL HORIZON — Implementation Plan and Requirements
Date: 2026-11-22 | Draft for internal review | Status: planning only

## Goal and non-goals
Global, multilingual, evidence-first discovery and comparison of documented anomalous-experience reports, images, locations, occupant histories and historical accounts. The system generates **research leads**, not paranormal classifications. It must not identify people based on visual resemblance, harvest private communications, or publish unpublished VEIL data.

## System architecture
1. **Approved-source registry:** source owner, country, languages, permitted endpoints, credentials, terms/version, robots rules where relevant, rate caps, license, retention rules, review dates, and kill switch.
2. **Bounded ingest workers:** scheduler -> connectors -> raw response manifest -> integrity/hash check -> extraction queue. Store only licensed/authorized content; otherwise preserve source links and permitted metadata.
3. **Normalized research store:** SQLite for prototype; migrate to PostgreSQL if concurrency and volume require. Core entities: source, item, report, reported event, geographic place (with uncertain coordinates and historical names), document, image derivative, purported phenomenon, date interval, account, witness pseudonym, investigation, occupancy period, claim, citation, comparison, reviewer action, audit trail and access consent.
4. **Search/analysis:** lexical full-text lookup, controlled vocabulary, language detection and original/translated text, duplicate text grouping, exact and perceptual image hashes, cropped/edited similarity triage, temporal/geospatial correlation, alternate-explanation checks, provenance and cross-source dependence graph. Similarity never equals identity or paranormal evidence.
5. **Review and output:** investigator dashboard and SIGNAL read-only query adapter. Findings link back to item-level citations, extraction versions, confidence, counterexamples and human decisions. Redact private witnesses from shared reports.
6. **Ops:** local-first operation, encrypted sensitive store, offline queue, monitored disk usage, backup+restore test, API-key vault, configurable quotas, international privacy/retention handling, deletion workflow and transparent logs.

## Source acquisition matrix (verification as of 2026-11-22)
| Source | Initial role | Access route | Constraint or gate |
|---|---|---|---|
| Library of Congress | Historical US publications/images, metadata | loc.gov JSON/YAML API | Rate limits; incomplete collections; per-item rights |
| Internet Archive | Historic text/media metadata and permitted files | Archive item search/metadata API | Each item's rights and availability; courteous usage |
| Europeana | European cultural history/photographs | Free account and API key; consider project key for sustained use | Quotas; each contributing item's usage rights |
| Common Crawl | Prior web captures and source discovery | URL index and archived WARC | Not full web or guaranteed historic capture; storage/processing cost and attribution/rights |
| Collaborator submissions | Original investigation files/firsthand provenance | Opt-in controlled submission package | Consent, provenance, witness privacy, redistribution rights |
| Google Search Researcher Result API | Additional research discovery, conditional | Eligible accredited academic researcher and application | Not guaranteed; 1,000 queries/day per approved project; no unrestricted corpus or Lens access |
| Brave Search API | Optional discovery only | Paid/contractual API | Standard terms restrict persistent result storage; do not ingest API results to database absent rights |

Authoritative starting points:
- https://www.loc.gov/apis/
- https://www.loc.gov/apis/json-and-yaml/working-within-limits/
- https://archive.org/developers/
- https://api.europeana.eu/en
- https://europeana.atlassian.net/wiki/spaces/EF/pages/2462351393
- https://commoncrawl.org/get-started
- https://commoncrawl.org/faq
- https://support.google.com/websearch/answer/16091809
- https://api-dashboard.search.brave.com/terms-of-service

## Development stages and exit criteria
**Stage 0 — Governance and specification:** source policy, privacy tiers, licensing matrix, standard event/report/image schema, named owners, review process, research hypotheses APH-001/H04, controls, defined false positives. Exit: reviewed schemas and allowed-source roster, no live scraping.

**Stage 1 — Global bounded pilot:** ingest a curated small set of eligible items from at least 3 countries, at least 2 languages and at least 3 independent source families. Include original/derivative reposts, positive/negative controls, reports with no activity, and deliberate look-alike images. Exit: every displayed claim points to a source and audit entry; no private sensitive information leaked.

**Stage 2 — Provenance and visual verification:** original upload/reference, SHA-256 when bytes are authorized, canonical URL, exact/perceptual hashes, crop transformations and manual reverse-image source checks. Exit: predetermined test set with measured duplicate precision and false positives, and documented limitations.

**Stage 3 — APH-001 correlation:** historic-place matching with uncertainty; occupants/families pseudonymous; independent account timelines, legend-exposure flags, negative controls, sampling limitations. Exit: blind reviewer reproduces an example finding and its alternative explanations.

**Stage 4 — SIGNAL integration:** expose read-only queries and evidence bundles; require citations, explicit uncertainty and reviewer signoff. Exit: documented offline integration tests, safe failure on unavailable sources.

**Stage 5 — Scheduled incremental ingestion:** run only on authorized host, quota ceilings, retry/backoff, failure alerts, stop switch, backup-restore test and budget alarms. Exit: stable monitored run with logged permissions and zero unapproved publishing.

## Resources and roles
- Existing computer for first local prototype; continuously running automation later requires an always-on host or explicitly scheduled desktop sessions.
- Python + SQLite + a lightweight local dashboard; OpenCV / imagehash / optional pose/image embedding approaches with tested accuracy; backups on a separate medium.
- Human roles: lead researcher/approver, technical maintainers, source-rights/privacy reviewer, independent evidence reviewers, international collaborators with consent.
- Credentials/access: Europeana API key requested by account owner, optional Google academic partner application, opt-in collaborator agreements, any approved search API credentials.
- Budget: first proof-of-concept software can use no-cost tools and existing hardware; do not promise zero operational cost for storage, translation, large-scale queries or hardware.

## Suggested first two development sprints
Sprint A: source inventory, schemas, prototype data sample, citation ledger, 10–20 sample records with licensing noted, simple keyword/geography query, and tests.
Sprint B: duplicate-image and textual-source-dependence tests, multilingual original/translation preservation, APH-001 comparison demo using controls, secure export, documented failure cases.

## Major risks and mitigations
False correlation -> independent source graphs, negative controls, base-rate estimates, blinded review.
Recycled images -> content hashes, cropped/manual checks, earliest *known* appearance.
Copyright/site terms -> permission registry and metadata-only fallback.
Living-person privacy -> minimum collection, pseudonyms, restricted access, deletion.
API / cost volatility -> modular connectors, quotas, offline storage, avoid single vendor dependency.
AI hallucination -> citations and original documents; no unsupported factual fill-ins.
Data loss -> separate backups, restoration drills, exportable format.
Security -> least privilege, no public submission endpoint until independently reviewed.

## Decisions before production
Approve source list, private-data policy, public-data release rules, device/hosting arrangement, review authority, collaborative contribution agreement and initial operating budget. No purchases, public outreach, public deployment or merge without permission.

## Current status
Plan only. No ingestion pipeline, research database or automated crawling system built or tested by this document. Files saved in isolated GitHub planning branch; not merged or deployed.
