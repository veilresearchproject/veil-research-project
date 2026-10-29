# VEIL Research Center — A Vision Taking Shape

## Real-time architectural 3D prototype v0.4.0 (development build)

**Before it is built, it must first be seen.**

This build is an evolving, three-dimensional *concept* of a proposed VEIL Research Center, not an existing facility, not a professional building model, and not a guarantee that the final physical center will follow this layout. VEIL currently develops experimental methods, prototypes and software; the proposed staffed research center is a long-term goal.

## Open it (no installation, paid service or API keys)

1. Extract the entire ZIP to a normal folder; **do not open the HTML while it is still inside the ZIP**.
2. Open `future-research-center/dev-v04/index.html` in Chrome or Microsoft Edge.
3. Choose **Walk the upgraded 3D center**. On desktop use **W/A/S/D** (Shift to move faster), drag the mouse to look, and click the numbered location cards. **E** jumps upstairs to the SIGNAL Command Center; **Q** returns to the main hall. Phone users can turn with touch and use the on-screen arrows.
4. The visual design references gallery uses artistic images. They are **not** textures derived from the interactive model, and don't represent images captured from an actual constructed research facility.

## What was actually implemented in v0.4.0

- Added native 3D geometry to the existing site architecture. More than 900 explicit world-space objects across 135 named categories, exported to editable `VEIL_Research_Center_v04_geometry.json` and 3D exchange format `VEIL_Research_Center_v04.glb`.
- Actual added modeled reception counter, inset front floor, reception computers, laboratory instrument benches/monitors, material detail, roof and structural seamwork, light-cage sensors, MTC microphone/recording hardware, ECHO environmental instrumentation, temperature curtain detail, cabinets/drawers and loading-bay cases/markers.
- New WebGL shader system with material-specific **procedural** concrete grain, ribbed steel, woodgrain, LED emission, monitor visualization, and downlight variation. These are experimental representations, not physically accurate PBR or photogrammetry.
- Retained 11 guided stops, 2nd-floor SIGNAL Command Center over the same 3D hall, floor-plan controls, keyboard/touch walk movement, and cinematic artwork gallery.
- All local assets remain bundled, with no external runtime dependencies.
- Included authored `BUILD_NOTES.md` and geometry for future Blender/three.js/Unreal asset pipelines.

## Honest limitations

- This is a **real interactive 3D** low/mid-poly development build, **not yet a photorealistic fully modeled facility** matching the generated concept pictures. Image creation alone does not yield 3D surfaces or geometry.
- Windows 3D view may use WebGL GPU mode for improved material shading; when WebGL is blocked, the existing simpler canvas/software renderer is used, so it will look visibly more blocky.
- Browser-based 3D collision detection, stairs/elevator physical navigation, accurate glass refraction, raytraced reflections, decals, physically based lighting, advanced occlusion, precomputed lightmaps and architectural compliance are **not** implemented.
- Layout and equipment dimensions are illustrative; the software is not a construction/design engineering package.
- No live research instrumentation or actual autonomous SIGNAL system is connected.

## Verification during this build

1. JavaScript syntax checked (`node --check`) for both inlined scripts — passed.
2. Real geometry extraction and a non-zero extent check for **921 model objects** — passed.
3. Exported GLB was re-imported using `trimesh` (135 geometry components and expected dimensions) — passed.
4. Navigation, site initialization and a sample hall view checked in an automated Chromium software-rendered browser — passed (no JavaScript page errors).
5. GPU WebGL shader visual confirmation and a live Windows/Android browser test — **not tested** in this headless environment (GPU WebGL unavailable).

## Project provenance and release process

This v0.4 branch should remain a **draft development branch** separate from the public VEIL GitHub Pages tour until manually inspected and approved. The public 0.3 tour stays unchanged. Do not claim that the reference artwork is captured from this 3D scene. Use this as a working development milestone rather than a final visitor release.