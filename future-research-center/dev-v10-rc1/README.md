# VEIL Research Center — Visitor Preview v1.0 RC1

**A Vision Taking Shape** — an interactive architectural 3D concept for a future VEIL Research Center. The facility **does not physically exist**. The model is not photorealistic, engineered or operational.

## Opening the project
Unzip; open `future-research-center/index.html` in Chrome or Edge. The included assets are local and the application has no subscriptions or API keys. Alternatively use the separate offline standalone HTML.

## Visitor tools
- Select **Explore the 3D Research Center** to enter the actual 3D geometry.
- Use **W/A/S/D** to walk, drag or swipe to look, use **Locations** for 13 guided locations, use on-screen arrows on mobile.
- **NEW: Section: Interior** or shortcut **C** removes the modeled cladding and glazing *from the rendering only*, while preserving internal architecture and frame. Toggle again to restore it. Section mode also temporarily removes the roof so you can see inside. This is a visual architectural study, not live footage.
- **R** toggles roof presence; **F** toggles unobstructed Focus View; Lighting switches between day and lab-night concept looks.
- Guided tour auto-steps through the 13 locations; stop or walk freely at any time.

## Actual geometry enhancements
Lobby and reception wayfinding, ceiling acoustic clouds, facility task lights, command workstation consoles, MTC testing benches with status indicators, wall service rails, and restrained facade accents are modeled in 3D. All labels and status indicators are *conceptual simulations*, not instrument data.

## Engineering notes
`VEIL_Research_Center_v10_geometry.json` is the editable tagged box-primitive source; static `VEIL_Research_Center_v10.glb` keeps the envelope and roof intact. The 3D viewer groups facade envelope and roof geometry into independently toggled index-buffer spans; the Canvas 2D fallback uses the equivalent category filters.

## Release gates
This is a visitor preview, **not** the final photorealistic tour or a constructed research facility. Hardware WebGL testing and physical Galaxy S25 touch/performance tests remain pending. Do not merge into the live site or publish without project owner release approval.

This review is isolated under dev-v10-rc1 and references shared ../assets/. No live site publication authorized. The complete 16-file ZIP and standalone self-contained HTML are archived in ChatGPT Library.
