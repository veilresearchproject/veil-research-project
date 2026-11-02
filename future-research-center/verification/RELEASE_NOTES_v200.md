# VEIL Research Center v2.0.0 — GB-001 architectural enclosure and practical light study

**Status:** Verified development checkpoint, not a photorealistic release. November 2, 2026. The center is a future concept; all telemetry and diagnostic displays are simulated.

## Scope

Built directly from the verified v1.9.9 Library HTML and ZIP, retaining all earlier GLBs and 13 guided stops. The new GB-001 room architecture consists of **five editable triangle-mesh groups totaling 4,628 actual triangles**: rear insulated modular wall with joints and cable raceway, two side wall liners with impact protection, an epoxy floor with expansion joints, and a roof-class ceiling service perimeter. The roof-class group disappears with the established roof-off control. Existing v1.8 43 GB-001 groups are unchanged.

The six previously modeled softbox diffusers now contribute **bounded direction-dependent, distance-attenuated illumination** in the actual WebGL fragment shader. This is an analytic area-light approximation, **not path-traced global illumination**. New wall and floor surfaces use the existing triplanar PBR texture atlas in the live WebGL renderer. An independent UV-mapped PBR glTF 2.0 GLB export is supplied for editing and inspection; the HTML does not import this separate GLB or use its authored UVs.

The new rear wall is represented in the collision model. Existing mobile tap and hold movement code is retained.

## Verification

- Real Chromium WebGL SwiftShader under Xvfb, 1440 × 900: **13/13 stops**, roof/section/night controls, two embedded PBR atlases, zero JavaScript exceptions, zero WebGL errors.
- Chromium mobile emulation at 412 × 850: **13/13 stops**, roof/section/night controls, Locations drawer, forward tap **0.55 model units**, forward hold **2.423 model units**, zero JavaScript exceptions and zero WebGL errors.
- Canvas fallback: smoke-tested three representative stops (exterior, GB-001, second-floor Command Center) and mobile Locations drawer; no JavaScript exceptions. Full 13-stop fallback sweep **not** verified in this run.
- Eight inline JavaScript blocks passed Node syntax checks.
- New mesh export: 4,628 finite nondegenerate triangles, 26 glTF primitives, authored `TEXCOORD_0` UVs, 52 embedded PBR texture images, glTF 2.0 GLB round-trip verified.
- Seven original GLBs copied byte-for-byte from v1.9.9 ZIP. ZIP CRC integrity verified.
- Actual WebGL screenshots from **identical camera position/yaw/pitch and viewport**, before and after. 14.98% of pixels changed by >20 mean RGB; **this is not a photorealism score**.

## Remaining limitations

- The facility is still visibly stylized; it does **not** meet a convincing photorealism standard.
- Lighting is approximate, not physically accurate path-traced illumination. No accurate refractive ray tracing or global illumination.
- Mobile tests are Chromium touch emulation, **not** a physical Samsung Galaxy S25 GPU performance measurement.
- The HTML renderer samples world-space triplanar PBR atlases; the separately exported GLB uses UV-mapped materials and is not loaded by the HTML tour.
- The real research center does not exist. All displays are synthetic illustrations, not SIGNAL or field evidence.

No live website changes, merges, Facebook posts, or spending.