# VEIL v1.9.7 — Real PBR material textures in the interactive renderer

- Inspected the actual v1.8 Library baseline, full ZIP, and draft GitHub PR #45 (still open/draft/unmerged), plus v1.9.6 checkpoint.
- Fixed the v1.9.x standalone HTML regression: six concept art assets are again embedded as data URLs, with nine references. No external image paths required.
- Integrated all **seven** deterministic v1.8 base-color and metallic/roughness texture pairs into two packed atlases. The interactive WebGL renderer now **samples the real texture data** for GB-001 curved geometry, using triplanar world coordinates. The separate UV-mapped GLB is preserved but still not loaded by the browser; its authored UVs are NOT yet used in the live renderer.
- Added targeted low-opacity command-room observation glazing material (material 12). This corrects the previous six-faced opaque-window effect without globally changing the building facade.
- Preserved all 13 stops, older scene assets, controls, simulated data warnings and roof/section options.
- This is a **concept** future center, not a physical facility. All readings are **SIMULATED**. Neither the existing scene nor this material upgrade is photorealistic.

## Tests and limits
Node syntax (8 scripts), GLB structural verification, ZIP CRC, and actual WebGL browser QA must be documented in QA_v197.json. WebGL testing under virtual X display + SwiftShader is software GPU emulation, NOT physical Samsung Galaxy S25 performance.

## Verified browser results (October 30, 2026)

- **Actual WebGL shader compile, link and draw succeeded** under Chromium + Xvfb + SwiftShader (software GPU). Both embedded PBR atlases decoded and uploaded (2/2). All 13 stops, day/night, roof and section toggles tested, zero page errors.
- 412×850 Canvas software fallback: all 13 stops, toggles and mobile Locations drawer tested, zero page errors. Gallery image decoded from the standalone HTML.
- Actual same-camera screenshots from v1.9.6 and v1.9.7 were captured. GB-001 scene changed **3.85%** of pixels and Command Room **19.37%** (>20 RGB max-channel difference). These numbers measure changed pixels, **not** realism.
- Structural glTF checks: 80 UV-mapped mesh primitives, 22 materials, 44 textures. ZIP CRC passed.
- **Known visual defect:** GB-001 clear acrylic still looks too opaque in actual GPU rendering. Do not claim this is corrected; address in a subsequent rendering pass.
- Actual physical GPU and Galaxy S25 device remain untested.