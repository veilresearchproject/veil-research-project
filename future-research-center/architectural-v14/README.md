# VEIL Research Center — Architectural Shell & Real-Geometry Pass v1.4

The VEIL Research Center is a **proposed future facility**, NOT a constructed/operational research center. All 3D assets are concept models and not engineering drawings.

## Substantial modeled changes
- Corrected an important architectural gap: the front office wing now has a **fully triangulated shallow-pitch standing-seam roof** with raised metal seams and folded eaves (26 removable roof mesh groups).
- Built an actual chamfered, extruded visitor entrance portal with a projecting header and physical light housings.
- Added 13 three-dimensional façade fin and portal groups assigned to the section envelope class.
- Improved the MTC rear laboratory acoustic treatment using 54 physically modeled rib/wedge relief modules, plus three swept cable paths; no flat image impostors.
- The 3D renderer now handles separate **permanent / roof / envelope mesh VBOs** so new architecture respects the actual roof and interior section controls in WebGL as well as the software fallback.
- All earlier 13 guided locations, editor geometry, controls and equipment meshes remain in place.

## Verifiable numbers and checks
- 45 new editable 3D architectural mesh groups; 2,932 new triangles (desktop). Total curved + architectural triangles: 17,360 (desktop) / 12,728 (simulated phone viewport).
- New architecture mesh exported to `VEIL_Architectural_Mesh_v14.glb` and `VEIL_Architectural_Mesh_v14_geometry.json`; round-trip verification confirmed 45 groups, 2,932 faces, all vertices finite.
- All 8 inline JS scripts pass Node syntax checks.
- Headless Chromium browser tests in software-rendering fallback pass desktop 1440×850 and mobile viewport 412×850, with zero JavaScript page errors; controls tested: roof-off/roof-on, interior section reversal, day/night lighting, navigation to MTC and mobile Locations drawer.
- Actual before/after screenshot captured from running 3D code, not conceptual artwork.
- All ZIP entries pass CRC check.

## Outstanding quality and release gates
- **Not photorealistic yet**. Much of the older building remains simplified box geometry; this changes a substantial area of the physical building, but it is not the fully detailed exterior/interior from the concept imagery.
- WebGL/GPU shader output cannot be verified in this headless browser environment; the 3D software renderer was tested. Physical Galaxy S25 and actual GPU frame rate remain untested.
- Geometry lacks construction-grade dimensions, accessibility validation, engineering plans and functional SIGNAL integration.
- No public website or Facebook update was made. Keep development staging isolated; obtain explicit approval before publishing.

## Open locally
1. For the simplest test, download `VEIL_Research_Center_v14_OPEN_IN_BROWSER.html` and open it with desktop Chrome or Edge.
2. Alternatively unzip this complete project, open `future-research-center/index.html`, press Explore.
3. Use Roof and Section toggles to compare architectural shell and cutaway; the MTC audio zone is guided stop 07/13.
## Isolated GitHub review
The HTML source is staged in `future-research-center/architectural-v14/` and uses shared `future-research-center/assets/`. Standalone offline HTML, GLB/JSON exports, screenshot comparisons and ZIP are saved in ChatGPT Library. No public live-site changes or Facebook publications. Keep PR a draft until hardware and visual review.
