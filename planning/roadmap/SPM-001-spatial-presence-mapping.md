# VEIL SPM-001 — Spatial Presence Mapping

**Roadmap entry:** 2026-11-22
**Status:** Proposed / not implemented / not tested
**Classification:** Internal development planning only. Not evidence of paranormal activity.
**Owner:** VEIL Research Project
**Origin:** Discussion of Paranormal Response Network's SLS Pro phone application and feasibility of actual standalone cameras.

## Objective
Develop an offline-first, auditable, camera-based body/pose-detection subsystem using standard USB/IP cameras and, optionally, purpose-built depth cameras. Make it reusable across VEIL experiments without requiring a mobile phone or commercial SLS application.

## Intended integrations
1. **Six-Plane Light Cage (initial target):** multi-angle calibrated visible/depth cameras, geometric agreement across viewpoints, instrumented test objects and human controls.
2. **Panic Box:** time-synchronized detection events, pre/post-trigger preservation, human-review alerts.
3. **Temperature Curtain:** independent thermal-array correlation, with separate sensor limitations and alignment/calibration recorded.
4. **SIGNAL:** read-only event summaries and traceable analysis; no autonomous claims of ghosts or physical entities.
5. **3D spatial sensing:** optional registered depth stream, only when supported depth hardware is available.

## Engineering phases
- **P0 — design/control protocol:** define clock sync, camera identities, baseline/control runs, false-positive challenge set, privacy and retention, original-file hashing, calibration, and reporting schema.
- **P1 — zero-cost prototype:** use existing USB webcam or prerecorded video; evaluate local pose inference (e.g., MediaPipe/OpenCV), save bounding boxes/keypoints, model version, confidence, raw video timestamps and operator-reviewed labels. No claims of measured depth.
- **P2 — multi-camera:** calibrated simultaneous capture, known 3D geometry, multi-view consistency, synchronization and explicit occlusion handling. Use second camera only when available.
- **P3 — measured depth and corroboration:** add dedicated depth camera if donated/available; align with independent thermal, EMF, audio, lighting and environmental measurements.
- **P4 — controlled device integration:** connect read-only SPM event feed to SIGNAL, Panic Box and other VEIL equipment using documented permissions and reversible adapters.

## Validation requirements
- Characterize false positive and false negative rates against empty-room scenes, furniture, reflections, projected imagery, cloth, people, pets and lighting transitions.
- Record camera placement, lens/FOV, exposure, illumination, firmware, clock offsets, detector version and thresholds before test.
- Use blinded control intervals and preregistered thresholds where practical; never treat a skeletal overlay alone as evidence of an entity.
- Preserve untouched source recordings, metadata, checksums and derived overlays separately with reproducible provenance.
- Distinguish 2D inferred pose, multi-view triangulation and direct hardware depth measurements.
- Any alert remains an **algorithmic anomaly candidate**, subject to human inspection and conventional-explanation checks.

## Access and publication
Roadmap only, on isolated branch; no merge to main, no public site deployment, no hardware purchases or external communications without approval. Do not store identifying investigation footage or private witnesses' information in a public repository.

## Source limitations
This entry records a project decision made in conversation on 2026-11-22. The SLS Pro screenshots were supplied by the user, but a screenshot alone does not validate vendor claims or detector performance. No hardware integration or testing occurred as part of this roadmap entry.
