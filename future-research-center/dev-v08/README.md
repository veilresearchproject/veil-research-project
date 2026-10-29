# VEIL Research Center — A Vision Taking Shape

## Development v0.8.0 • October 29, 2026

**Before it is built, it must first be seen.** VEIL's *future* research center is not yet constructed. VEIL currently develops prototypes, software, and evidence-first experimental methods.

### How to explore

1. Extract the ZIP and open `future-research-center/index.html` in Chrome or Edge.
2. Click **Explore the 3D Research Center**, choose from 13 stops, or navigate with W/A/S/D and mouse drag. Use arrow controls on phones.
3. Click **Roof: On** in the top toolbar (or press **R**) to change to **Roof: Cutaway**. This removes the modeled roof skin only, exposing the lab and office spaces from the air while retaining the trusses. Toggle again to restore it. Both software fallback and WebGL geometry use the same visibility state.
4. Use Day / Lab night lighting, clean view, 3D guided route, and visual design references. **Concept art is separate from real modeled screenshots.**
5. For technical review, `VEIL_Research_Center_v08_geometry.json` is editable; `VEIL_Research_Center_v08.glb` is a static combined model export with roof intact. Roof toggling works in the HTML runtime, not yet in third-party GLB viewers.

### v0.8 model changes

- Added real box geometry for dual ceiling-level supply ducts, flanges, slot diffusers, and air distribution, hanging acoustic rafts, overhead cable trays, lobby glazing mullions, command-console details, additional MTC acoustic baffles, workshop cable protectors, and research floor guidance stripes.
- Added a **reversible roof cutaway** using a separate GPU index range and software-renderer equivalent, with keyboard shortcut **R** and accessible pressed state.
- No external libraries, hosted JavaScript, API key, subscription, or paid asset needed to run the standalone walkthrough.

### Release gates and boundaries

This is a stylized architectural block model, *not* a completed photorealistic environment or structural design. Dimensions are illustrative. The procedural shader is not physically based/raytraced. Full desktop GPU/WebGL, Samsung Galaxy S25, performance, accessibility and browser QA are still required before deployment. SIGNAL is a demonstration concept, not a connected live lab assistant. Do not merge draft changes or publish publicly without an explicit release review.
## GitHub isolated staging

This review copy is in `future-research-center/dev-v08/`, with shared concept assets referenced from `future-research-center/assets/`. It is not the public visitor path. Do not merge until approved. The exported editable JSON and GLB are in the full v0.8 ZIP preserved in ChatGPT Library.
