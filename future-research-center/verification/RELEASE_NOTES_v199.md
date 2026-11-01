# VEIL Future Research Center v1.9.9 — color-managed lighting and grounded material response

**Scope:** offline/no-cost experimental checkpoint; generated from v1.9.8, retaining v1.8 GB-001 mesh, v1.7 SIGNAL Command Center, v1.6 MTC acoustics, and all 13 stops. This is a concept for a future center, not a built facility. All diagnostic screens are simulated.

## Substantial changes

1. **Correct WebGL color-space pipeline.** Convert authored sRGB vertex colors and embedded PBR base atlas texels to linear light before illumination, then retain output gamma encoding. Previous renderer lit sRGB values as if linear, producing visibly washed-out surfaces.
2. **More physically motivated highlights.** Replace a hand-tuned Phong-like highlight with a bounded GGX microfacet distribution, Smith visibility, and Schlick Fresnel approximation. This is a real shader change, not a concept-image replacement.
3. **Room-local indirect illumination.** Approximate cool wall bounce and warm floor bounce in the actual GB-001 coordinates; bounded analytical model, **not** raytraced global illumination.
4. **Improved grounding.** Expand actual floor contact-shadow footprint samples from 8 to 12, adding GB-001 chamber and camera/stand locations. Lower broad ambient fill and reduce distant atmospheric fog.

## Verified

- Chromium **WebGL** via Xvfb + SwiftShader: 13 tour stops, roof/section/day-night controls, two embedded PBR atlases, zero WebGL errors and zero page exceptions.
- Chromium **touch emulation** at 412×850: 0.55-unit forward tap, 1.62-unit 650-ms hold, 13 Locations entries, zero WebGL errors. This is **not** a physical Galaxy S25 test.
- Actual 1440×900 WebGL screenshots, identical camera at GB-001: 80.24% pixels changed at mean absolute RGB >20. This measures image change, **not** photorealism.
- All 8 inline JavaScript sections pass Node syntax checks; all seven preserved GLB models pass structural header/JSON/bufferView checks; ZIP CRC checked after packaging.
- Canvas fallback **not reverified** this session: its automated test timed out. No Canvas-renderer code changed in this checkpoint.

## Known limitations

The model remains **stylized, not photorealistic**. The HTML samples real PBR texture atlases with world-space triplanar mapping; it still does **not** load the authored GLB UV maps. The indirect lighting is an analytical approximation, not path tracing. Actual Samsung Galaxy S25 performance and long-duration navigation remain unverified. All telemetry is simulated. No live website change, merge, paid API, or Facebook post.

## Reproduce

Run `python verification/veil_advance_v199.py VEIL_Research_Center_v198_OPEN_IN_BROWSER.html VEIL_Research_Center_v199_OPEN_IN_BROWSER.html` in the package's `future-research-center/` directory. The original v1.9.8 standalone HTML and all GLB models are retained for reproducibility.