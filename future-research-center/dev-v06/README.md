# VEIL Research Center — A Vision Taking Shape

## Development v0.6.0 • October 29, 2026

**Before it is built, it must first be seen.**

This is an artistic and interactive proposed future research center. VEIL is an independent research initiative developing methods, software and prototype experiments; this research center is a long-term goal and does **not** exist as a built facility.

### Open

1. Extract the ZIP, preserving the `assets` folder alongside `index.html`.
2. Open `future-research-center/index.html` in Chrome or Edge.
3. Choose **Explore in 3D**. Walk with W/A/S/D, drag to look, Shift for speed. On phones use touch and on-screen arrows.
4. Tour guided stops from the left sidebar. The guided tour uses gentle camera panning *within each room*; changing stops still cuts between locations rather than following a physical camera path.
5. Use **Lighting: Day / Lab night** to change atmosphere; the actual scene geometry is shared between both modes.
6. Click **Concept gallery** for separately labeled illustrative art; these images are not model textures or proof of an existing building.

### What's new

- Modeled exposed architectural ceiling rafts, workshop tasks lights, exhibit footings, visitor information pedestal, circulation markers, and facade lights.
- Actual 3D LED dot-matrix letters for VEIL / SIGNAL / MTC / ECHO / WORKSHOP, not photographic overlays.
- Day and lab-night display modes (WebGL shader or fallback software renderer).
- Guided-pan camera movement at tour stops, without claiming a continuous video fly-through.
- Single-origin editable JSON and GLB exports. The offline web file has no third-party runtime dependencies.

### Limits / QA

The GLB has flat-colored box primitives, not finished photoreal PBR meshes. Shadowing and windows are stylized, stairs/collisions illustrative, not building-code compliant. The existing roof cutaway and upper deck are intentional to make interior zones visible. Test on a real GPU device and Android/Samsung before publication; browser-level testing in this work environment used software fallback. No SIGNAL backend or live sensor integration is included. Keep this version in draft review; it should not replace the public VEIL site until you approve it.
### GitHub isolated preview

The review copy lives under `future-research-center/dev-v06/`. Shared illustration assets resolve from the existing `future-research-center/assets/` directory. The public visitor entry and main GitHub Pages experience are not changed by this branch.
