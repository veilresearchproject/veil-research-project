# VEIL Research Center — v1.9.8 | Rendering-state and mobile navigation correction

## Significant verified advance

**Rendering correctness:** A frame-to-frame WebGL vertex-buffer binding regression was found in the real v1.9.7 source. Indexed building boxes were drawn before rebinding their own vertex buffer after the prior frame's curved/acrylic pass. In actual SwiftShader screenshots this produced a large, misleading opaque panel obscuring the GB-001 chamber. v1.9.8 rebinds the box vertex buffer before every indexed draw. The chamber, inert target, and surrounding instrumentation are now visibly separated. **This is not a new photo or concept-art overlay.**

**Acrylic:** All eight real chamber-panel triangles are now sorted back-to-front relative to the live camera each WebGL frame. The face-on material alpha changes from 0.15 to 0.035, rising toward 0.19 at grazing angles; Canvas fallback uses correspondingly subtle transparency. No refraction or true ray tracing is claimed.

**Navigation:** Direct Chromium collision probes found two previously unusable tour starts: MTC stop 07 was inside a workbench leg's collision radius and Command Center stop 13 intersected a desk. Their starting camera coordinates are moved into unobstructed corridors. Exterior stop 01 now supports movement in its elevated overview bounds. Touch arrows have 50px targets and guaranteed 0.55-model-unit short-tap steps. Long presses receive time-based movement correction; each correction is divided into <=0.2-model-unit collision-aware substeps to avoid jumping through furniture.

## Real tests

- Node syntax checks: all 8 inline JavaScript sections passed.
- Desktop Chromium 1440×900, WebGL SwiftShader: all 13 stops; roof/section/night toggles; both PBR atlases loaded; eight acrylic triangles sorted; `gl.getError()==0`; no page exceptions.
- Mobile Chromium 412×850, WebGL SwiftShader and emulated touch: arrow taps moved 0.55 units from Command Center, MTC, and Exterior. Press-and-hold moved >2.9 units; mobile Locations contains 13 stops; no JS or GL errors.
- Mobile Chromium 412×850, Canvas2D fallback: all 13 stops and 0.55-unit arrow tap passed; no JS errors.
- Actual **same-camera** v1.9.7 versus v1.9.8 WebGL screenshots, 1440×900, stop 09: 22.1% of pixels changed by >20 RGB. This is **not** a photorealism score.
- Original UV-mapped GB-001 glTF GLB preserved byte-for-byte (80 meshes; SHA-256 in QA). ZIP CRC checked after packaging.

## Limits and owner safeguards

SwiftShader is a software GPU, and the mobile tests are browser-emulated, not physical Samsung Galaxy S25 verification. The live custom renderer still samples triplanar texture atlases rather than the separate GLB's authored UV coordinates. Architectural finish, contact shadows, indirect light, and refractive glass remain incomplete. **The center is a future concept, not a built facility. All telemetry is SIMULATED. The model is still stylized, NOT photorealistic.**

This is an isolated development checkpoint. No merge, live-site publication, spending, Facebook posts, or paid APIs.