# VEIL Research Project | MTC transparent-enclosure build gate v0.1
**Date:** 28 October 2026 · **Status:** PRELIMINARY ENGINEERING / SPONSOR BRIEF · **Owner:** Founder and Lead Researcher, Andrew Underwood

## Mission and boundary
Build a portable, inspectable **fully transparent** Mobile Trans-Communication Device (MTC) around the existing Windows MTC recording system. It asks prerecorded questions on an audible speaker while continuously recording the room, preserves raw WAV and session logs, and makes read-only evidence copies available for SIGNAL's post-session candidate-sound review. Reliable negative findings are legitimate outcomes; no paranormal claim is made or assumed.

**LOCKED requirements:** (a) transparent on all practical viewing sides, not merely a clear lid; (b) recorder's working v0.1.4 code unchanged during mechanical prototyping; (c) no exposed AC mains, raw lithium cells, or EM conditioning generator inside the case; (d) external microphone and question speaker; (e) visually inspectable mounts, cables, SSD and status indicators; (f) independent audio/video corroboration is planned and must not depend on the MTC computer; (g) evidence remains locally stored, original files not rewritten by SIGNAL; (h) no purchase commitments until dimensions, thermal, power, and software compatibility are verified.

## Preliminary physical package (NOT a fabrication drawing)
A **400 mm wide × 300 mm deep × 200 mm high** rectangular envelope is an *exploratory planning envelope only*, to be resized after obtaining actual hardware and cable-bend measurements. It is not an approved specification, dimensional tolerance, vendor quote or panel-cut list. Preferred design is a modular removable top/front panel, clear polycarbonate sidewalls, rounded/smoothed edges, guarded cable entries and a removable internally supported mounting tray. Explore **5–6 mm clear polycarbonate** only as a vendor-discussion starting point; fabrication partner selects actual grade and thickness based on safety, deflection, heat, fasteners and portability. Acrylic can be a tabletop mockup material, but its impact/fracture performance makes it a weaker choice for field service.

### First-pass equipment placement
- Low-power Windows mini-PC and 2 TB SSD/internal storage on tray, with visual space around each for cooling and servicing. Selection/size unknown. No assumed need for an external audio interface; HyperX SoloCast is USB.
- Status display/indicators on clear front; labels must not imply verified recording health merely because a light is on.
- USB, speaker, low-voltage power and optional synchronization connectors accessible on the **rear or side** with strain relief. All panel penetrations designed after choosing connector models.
- External HyperX SoloCast or later equivalent on isolated room stand. Question speaker also outside case; measure acoustic playback and mic pickup.
- Cooling if instrument testing requires it: acoustically isolated fans, filtered openings and airflow path; document noise floor with fans off/on. A ventilated custom housing does **not** inherit IP/NEMA protection claims.
- Power stage 1 uses an appropriate manufacturer-approved listed external AC adapter / enclosed low-voltage source. Portable stage 2 separately specifies protected LiFePO4 battery and qualified fused DC distribution with measured loads. No DIY high-current battery wiring in this design brief.
- Any EM conditioning generator is wholly external and powered OFF before the MTC response-window sequence per the established experimental plan; establish controlled/sham trials.

## Components and procurement priority
| Priority | Item | Initial route | Accept only when |
|---|---|---|---|
| 1 | Custom fully clear enclosure + removable service panel | ClickFold in-kind program; Erie Industrial Plastics offcuts/fabrication; Blanchard machined parts | All-view visibility, dimensions verified, safe cable relief, mechanical strength |
| 1 | Windows mini-PC (approx. 16 GB RAM preferred, 2TB SSD target for field unit) | Surplus donation/loan; existing bench desktop remains primary until validated | v0.1.4 runs unattended on actual Windows hardware, USB devices stable |
| 1 | Independent audio recorder and room video | Sponsor loan/donation | Separate power/storage and synchronization, check full session |
| 1 | Existing USB microphone + existing speaker | Reuse HyperX SoloCast and present speakers | Questions are audible in the actual room-mic WAV; noise floor documented |
| 2 | Tray, standoffs, cable glands, feet, guard and label hardware | Remnants/machine shop/maker partnership | No strain at USB ports; safe screw fit; no exposed edges |
| 2 | Display, indicators, quiet fan if needed | Evaluation samples/surplus | Nondeceptive read-only status; controlled self-noise measurement |
| 3 | LiFePO4 field pack and rated DC distribution | Later engineering partnership after load measurement | Verified manufacturer-approved power protection, 48-hour test target |

## Build phases / mandatory hold points
1. **Evidence/software gate:** inspect three original *copied* logs from 2026-10-27 (`session_result.json`, `session_metadata.json`, `events.jsonl`), verify event schema and normal stop, verify WAV segmentation and acoustic question playback against actual audio; keep MTC recorder code unchanged.
2. **Hardware selection gate:** select candidate mini-PC and exact SSD, external audio gear, power connectors; measure envelope dimensions, USB lead clearance, idle/recording peak watts, inrush and heat. Do not order case panels before completion.
3. **Mechanical mockup:** cardboard/template layout, thermal and acoustic spacing, removable service tray, labels, exterior mic/speaker placement, independent camera sightlines, power separation.
4. **Fabrication/supplier review:** request design advice and **one** prototype fully transparent case, donated offcuts or in-kind machining; get supplier-approved mounting, sheet thickness, corner support and cutout notes. This is not authorization to purchase.
5. **Bench integration:** connect mini-PC and original recorder; no software modifications; verify WAV contents, question sound and log state. Run baseline acoustic recordings with case open and closed and fan on/off.
6. **Endurance:** short → 90-minute replication → 8-hour → 24-hour → 48-hour tests *only after power and storage pass*. Record environmental/acoustic controls, file hashes, independent corroboration and failures. 48-hour capability is a goal, not achieved.
7. **Field-readiness review:** human review of safety, evidence provenance, storage backups, and independent video/audio; negative/null results documented.

## Energy planning, illustrative only
For **48 hours**: ideal capacity = measured average watts × 48 h; at a hypothetical 80% usable-system factor, budgeted battery-side watt-hours = watts × 48/0.80. Illustrations, NOT measured: 10 W ⇒ 600 Wh; 20 W ⇒ 1,200 Wh; 35 W ⇒ 2,100 Wh. Include all external devices powered by that battery; verify pack specifications and reserve with a qualified power designer. No custom pack wiring/purchases proposed.

Audio data only, illustrative: mono 48 kHz / 16-bit PCM ⇒ 0.096 MB/s (decimal), ~0.52 GB / 90 min, ~16.6 GB / 48 h; stereo doubles. Actual existing file settings remain to be verified; a 2 TB target supports field redundancy and additional data rather than implying WAV audio alone needs 2 TB.

## Supplier suitability and truthful outreach status
- **ClickFold Plastics:** published innovation/technology in-kind program (custom plastic products). FAQ requests contact at least one month in advance. Previous attempted Gmail send to `info@clickfold.com` failed; **Gmail draft only, not delivered**. Official FAQ renders sponsorship email as protected/obfuscated in accessible web text: verify via vendor site or call before addressing. Source: https://customplasticenclosures.com/faqs/
- **Erie Industrial Plastics:** stocks acrylic/polycarbonate/PETG and custom fabrication; **no donation program confirmed**. Their official contact form and phone 814-838-0660 are available. Source: https://erieindustrialplastics.com/distribution/ and https://erieindustrialplastics.com/contact/
- **Gannon MakerSpace:** engineering/maker capabilities; inquiry **sent** 28 Oct 2026, no commitment. Source: https://makerspace.gannon.engineering/
- **Blanchard Manufacturing:** fabricates acrylic/polycarbonate, inquiry **sent** 28 Oct 2026, no commitment. Source: https://www.blanchardmanufacturing.com/
- **Bud Industries:** real model PTH-22426-C (300×200×180.1 mm external) and PTH-22458-C (560×280×130 mm external) have **clear cover, gray body**, therefore not fully transparent; possible fallback/test enclosure only. Sales inbox `saleseast@budind.com` is published; previous Gmail send attempt was denied and remains a **draft**, no contact confirmed. Sources: https://www.budind.com/contact-us/ and https://www.newark.com/bud-industries/pth-22426-c/plastic-enclosure-hinged-cover/dp/56AC7859 and https://www.newark.com/bud-industries/pth-22458-c/encl-plast-multipurpose-pc-gf/dp/56AC7883
- **Computer donation routes:** Digitunity's network requires eligible nonprofit/school/public agency status and is not an appropriate assumed fit for independent VEIL; avoid implying eligibility. https://digitunity.org/get-involved/receive-equipment/

## Approval / anti-overclaim boundaries
**No parts authorized for purchase. No supplier has pledged donation. No signed partner agreements. No physical VEIL research center exists. No real-sample proof of anomalous communication.** Prior mockups are conceptual artwork; speaker, USB interface, and power module pictured may not be the final parts. Keep every release reviewable and the design controlled by VEIL's founder.