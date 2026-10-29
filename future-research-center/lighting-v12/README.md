# VEIL Research Center — Architectural lighting preview 1.2

**Open `VEIL_Research_Center_Architectural_v12_SINGLE_FILE.html` in Chrome or Edge.** It contains its illustrative gallery assets inside the file and works offline. Or open `index.html` here with the included `assets/` directory beside it.

Use the 13 guided stops, **F** focus, **R** roof visibility, and **C** interior section cutaway. On a phone, open **Locations** to switch labs. This tour depicts a *future proposal*, not an existing VEIL research facility.

The project is a **stylized 3D architectural experience, not yet photorealistic**. The `VEIL_Research_Center_Visual_v12_geometry.json` contains editable scene data; the existing `VEIL_Research_Center_Visitor_1_0.glb` preserves the unchanged base modeled geometry. Projected sun-shadow polygons are generated at runtime from that geometry rather than baked into the GLB. `VEIL_v12_QA.json` records desktop and simulated phone software-renderer testing. Full GPU shader compilation and physical Galaxy S25 testing remain outstanding.
## Staged GitHub preview

This development copy is isolated at `future-research-center/lighting-v12/`, with illustrations loaded from existing `future-research-center/assets/`. No updates to the public landing page, and no live deployment. This includes real 3D geometry-derived sunlight-shadow surfaces and improved architectural glass. Headless browser software renderer QA passed; full WebGL/GPU and real Samsung tests remain outstanding. **Do not merge before review**.
