# VEIL Virtual Research Center — Acoustic Architecture and Materials v1.6

A proposed **future** center, not a built or engineered facility.

## New 3D detail
- 56 individual triangular acoustic absorption modules with depth and face-specific shading across the MTC rear wall.
- 13 overhead folded multi-face acoustic blades, 6 integrated service rails, and 4 folded hanging ceiling sails. These are **79 new editable world-space mesh groups**, not photos, with 420 added triangles.
- A modest physically-inspired surface finish pass: deterministic software-renderer grain/clipped finish overlays and WebGL shader brushed-metal roughness, roof/acoustic microtexture and reflective highlights. This is **not physically based ray tracing** and should not be called photorealistic.
- Preserves v1.5 roof/section cutaways, 13 visitor stops and standalone offline browser access.

## Important verification boundary
- Browser smoke tests are software-renderer tests on simulated viewport sizes, not actual Samsung hardware.
- WebGL GPU shader evaluation unverified if no WebGL context is available.
- No website/Facebook publication or merge authorized.

## Browser QA and visuals
- All eight inline JS scripts pass Node syntax checks.
- Actual desktop software-renderer screenshot at MTC stop compared at the same camera position with v1.5; 8.85% of pixels changed beyond mean RGB difference 20. This is a measured visual difference **not** a quantified photorealism improvement.
- Tested roof on/off and section cutaway on simulated 412×850 mobile viewport, locations drawer, unchanged 13 guided stop definitions, no JavaScript page errors.
- 79 editable v1.6 GLB groups / 420 triangle faces confirmed on GLB reload.
- Shader source parses as JS string, but GLSL/WebGL could **not** be compiled/tested in headless environment. Actual GPU and physical Galaxy S25 must be tested before publishing.
- Current model remains obviously stylized. The next upgrade should be deliberate asset reconstruction and UV/PBR material system, not an asserted photoreal finish.
## Isolated review
Complete offline HTML, GLB, JSON and real model screenshot comparisons are in the VEIL ChatGPT Library folder. This development preview references `../assets/`. Do not merge to main or change the live site until owner review.
