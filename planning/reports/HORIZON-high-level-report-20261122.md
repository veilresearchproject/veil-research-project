# VEIL HORIZON
## High-Level Project Report — Global Historical Anomaly Research Network
**Prepared:** 22 November 2026
**Prepared for:** VEIL Research Project and potential academic/research collaborators
**Status:** Concept and implementation roadmap; not an operating platform

### Executive overview
VEIL HORIZON is a proposed international research infrastructure for discovering, organizing and comparing historical and contemporary accounts of unusual experiences. Rather than accepting or rejecting extraordinary claims on appearance alone, it would build source-traceable records of what was reported, when, where, by whom (subject to privacy protections), and how the information traveled between publications and generations.

### Why we are doing this
VEIL investigates whether recurring reports reflect place-associated patterns, family- or occupant-associated experiences, environmental conditions, ordinary perceptual effects, or the propagation of stories, images and expectations. Existing evidence is scattered among old newspapers, cultural archives, investigator collections and social-media reposts. Without a shared evidence model, independent accounts can easily be confused with copies of one original story. HORIZON aims to make these comparisons more systematic, reproducible and testable.

### How it will work
1. **Discover:** approved search and archive connections locate candidate records worldwide. Participating research groups may voluntarily submit documented originals.
2. **Preserve the trail:** each item receives a source reference, original date and retrieval date, language, usage rights, authenticity caveats and (where allowed) integrity hashes.
3. **Organize:** normalize geographic locations, changing place names, uncertain dates, event categories, occupant transitions, image variants and citations in a private research database.
4. **Compare:** algorithms flag potentially related descriptions, recurring visual motifs, reused images, time patterns and place/family associations. Controls and dependence checks help identify coincidences or copied legends.
5. **Review:** SIGNAL presents candidate links with original sources, competing ordinary explanations and confidence limits; human researchers decide what merits further study.
6. **Correlate with field work:** with appropriate consent, VEIL field instrument readings may later be linked to corresponding location reports using preserved timestamps and calibrated sensor records.

### Research questions
- Do supposedly independent accounts share specific details before publicity or prior contact?
- Are reports more consistently associated with a property or with people who move between properties?
- How often are photographs recycled with new narratives?
- Are apparent cross-cultural similarities better explained by shared motifs, image reuse, changing terminology or environmental effects?
- Do controlled measurements offer useful corroboration of any present-day observations?

### Global by design
The database will support multiple countries, original languages and translations from the outset because VEIL already engages with international research groups. Initial testing will use a small, geographically diverse sample; worldwide coverage is an architecture goal, not a claim that every archive will be accessible.

### Partners and data sources
Initial integration targets: Library of Congress, Internet Archive, Europeana, Common Crawl, and voluntary partner submissions. Google research access may be pursued with an eligible academic collaborator, subject to approval and terms. The project will not assume unrestricted access to Google Search, Lens or copyrighted material.

### Integrity, privacy and safeguards
HORIZON will separate testimony, historical documentation and machine-generated interpretations; preserve source lineage; score confidence conservatively; and use negative controls. The database is private during development. Living witnesses are protected by consent requirements, minimal collection, pseudonymization and access controls. Similar faces or figures will never be automatically declared the same individual or supernatural entity. No illegal scraping or bypassing access controls.

### Practical implementation
A staged prototype can use Python, SQLite, free archive APIs and existing computing hardware. First develop the source catalog, data schema and a small multinational sample. Then test image-duplication detection and generational/location comparisons before integrating read-only results into SIGNAL. Production-scale automated searches require approved credentials, a running workstation or server, storage, backups, monitoring and ongoing maintenance.

### What success looks like
A researcher can ask: 'Show earlier independently sourced reports of a child-shaped apparition near this historic property, identify recycled photographs, and list alternative explanations.' The system returns cited records, relationship timelines, uncertainties and a reproducible review package—not an assertion that a ghost exists.

### Strategic value
HORIZON could connect VEIL's field experiments with a global historical evidence record, support academic collaboration and help independent groups avoid misattribution. Its worth will be measured by provenance quality, reproducible comparisons and the useful correction of false assumptions, not by the number of unexplained cases it declares.

### Near-term deliverables
- Approved source/access inventory and international record schema
- Controlled test collection from at least three countries and two languages
- Citation and provenance ledger with image-duplicate tests
- APH-001 location-versus-family comparison demonstration
- Private SIGNAL-facing evidence query prototype
- Documented privacy, licensing, backup and review procedures

**Present position:** HORIZON is approved as a planning direction, not yet constructed. The first engineering work can begin on an isolated development branch following normal VEIL testing and approval boundaries.
