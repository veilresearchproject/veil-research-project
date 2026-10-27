# VEIL Research Project
## MTC / Panic Box - Storage & Unattended Reliability Design Decision (DDR-001)

**Status:** LOCKED BASELINE DESIGN REQUIREMENTS (not a final parts list)  
**Approved direction:** October 27, 2026  
**Scope:** Portable Mobile Trans-Communication (MTC), Panic Box, and any future combined field deployment.  
**Owner:** Andrew Underwood, Founder & Lead Researcher  
**Revision:** 1.0

### 1. Design intent
Build a portable, self-contained and offline-first research recorder able to run unattended at a location without relying on the researcher's desktop/laptop being present. The unit still needs an onboard computer/controller and power; storage capacity alone cannot prevent a computer crash. Recording, session controls, timestamps, evidence handling and health checks must work without an internet connection. Future authenticated remote phone monitoring is supplemental, not required for local recording.

### 2. Approved baseline storage architecture
| Element | Baseline requirement | Why |
|---|---|---|
| **Primary capture storage** | **Minimum 2 TB internal SSD per independent field recorder** (MTC or Panic Box). Avoid removable USB drives as the sole original recording destination. | Robust, low-vibration local capture. |
| **Separate evidence backup** | **4 TB portable SSD** as the baseline removable verified-copy/transport device; do not treat a backup as the only original. | Separate copy of unmodified original WAV/video, session data, hashes, and logs. |
| **Capacity headroom** | Plan with at least 20% of primary drive free, and validate expected recording output at real measured bitrates; select larger primary capacity as needed. | Sustained recording without filling the drive. |
| **Camera-intensive growth path** | Provision space and controller interfaces for 4-8 TB internal primary storage or an appropriately rated separate video recorder/NVR if measured camera load or session duration requires it. | Scaling future Panic Box multi-camera or high-bitrate recording. |
| **Optional stationary archive** | A larger surveillance-grade drive/NAS is an off-unit archive choice, not the portable field unit's baseline or an original-only store. | Lower-cost long-term storage if required. |

**Not required:** A 256 TB SSD. That figure was an illustrative example, not a purchase specification. Specific manufacturers/models, connectors, controller form factor, storage endurance rating and prices remain **to be selected after benchmarking**. Prefer power-loss-protected SSDs if electrically and economically feasible.

### 3. What the complete field unit must do
1. **Record independently:** Local compute/controller, audio/video interfaces, real-time clock, persistent configuration, internal SSD, protected DC power. No external desktop needed during deployment.
2. **Scheduled experiments:** Support immediate timed sessions, question cycles/repetition, and later configurable starts (e.g. midnight, 3 AM, 6 AM), duration, baseline intervals, location ID and no-overlap rules. Log whether starts were late/missed due to clock/power failure.
3. **Loss-aware capture:** Prefer manageable sequential segments rather than one massive WAV. Keep original acoustic room-mic capture of played questions. Monitor actual sample/frame progression, files/segment rotations, microphone connectivity, dropped callbacks, write failures, remaining space, camera faults, battery state and heartbeat staleness. A growing WAV is not sufficient proof of good audio.
4. **Independent watchdog:** A separately powered/system-independent monitor should signal power/controller/recorder failure; an on-machine process alone cannot detect all machine crashes. When connectivity is lost, phone status must show **unknown/stale**, not healthy.
5. **Evidence integrity:** Preserve unmodified original WAV, video and environmental logs. Use session IDs, before-start room/equipment photos, accurate timestamp/clock-offset records, SHA-256 digests on finalized files, copy verification and manifest of originals, backups and device configurations. Review/anomaly clips are derivatives, never replacements.
6. **Power resiliency:** LiFePO4 or equivalent protected field power with suitable battery-management system, fusing, low-voltage cutoff, independent power monitoring and enough runtime measured under full configured load. Safe shutdown or recoverable segment finalization on critical battery/power faults. Do not promise 48-hour runtime until physically measured.
7. **Safety and consent:** The Panic Box remains in FULL mode after panic/anomaly events until **authenticated offsite human ALL CLEAR**, with identity/time/audit record. A reboot, watchdog reset or lost link must never automatically clear FULL. Recordings comply with location permission and applicable consent rules.
8. **Remote read-only phone monitoring (later):** Secure, authenticated status/alerts; local recording must continue when internet, Wi-Fi, cellular or phone access fails. Do not confuse current offline HTML demos with live connectivity.

### 4. Example storage planning (estimates, not hardware measurements)
- MTC 24-bit / 48 kHz **mono** uncompressed audio: **~12.4 GB / 24 hours**, **~24.9 GB / 48 hours** (decimal GB).
- Two 1080p cameras at **3 Mb/s each**, plus mono MTC audio: **~77 GB / 24 hours**.
- Four 4K cameras at **8 Mb/s each**, plus mono MTC audio: **~358 GB / 24 hours**, **~716 GB / 48 hours**.
- Real capacity requires headroom for actual camera bitrates, metadata, redundancy, filesystems, temperature and SSD endurance. For a multi-camera system, **bench-test actual throughput** and choose larger SSDs if necessary; the 2 TB baseline is not a guarantee for arbitrary configurations or runs.

### 5. Acceptance gates before field use
- **Software tests:** Unit/regression/fault tests for recording progress, segment rotation, missing/truncated files, low disk, simulated power fail, heartbeat loss and scheduled starts.
- **Personal desktop test:** 90-minute unattended run with repeated prerecorded questions crossing a WAV segment boundary, then integrity/subjective review of actual room microphone WAV and logs.
- **Integrated portable prototype:** 24-hour then 48-hour bench endurance with actual sensors/cameras, measured power draw, storage use, reboot/low-power recovery, independent recorder comparison and watchdog fault injection. No unattended physical stress tests without adequate electrical/fire safety.
- **Panic Box gate:** Demonstrate that FULL persists through link loss/reboot and clears only via authenticated human offsite ALL CLEAR; preserve the entire event evidence window.
- **Deployment signoff:** Confirm all necessary hardware specs and safety requirements with physical measurements before purchasing/scaling. Never describe simulated results as field validation.

### 6. Change control
This baseline is the default for future MTC and Panic Box design, procurement discussions, funding lists and prototype revisions. A future change in drive capacity, topology, power or evidence policy requires an explicit, dated design revision stating the reason and test evidence. **No drive purchase or particular brand is authorized by this document.** Current home-bench MTC software continues unchanged unless a separate validated update is intentionally adopted. Do not install VEIL software on AJAX-owned equipment.