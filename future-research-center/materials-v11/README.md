# VEIL Research Center — Visual Materials Pass 1.1

**This is a research-facility concept, not an existing building.**

Continuing the 1.0 Visitor Edition without changing the established modeled building, geometry data, 13 stops, user navigation, reversible roof/section views, or day/lab-night controls.

## Actual model improvements

- WebGL model renderer now separates transparent glass from opaque masonry, metal, roof and equipment drawing. Glass uses 36% alpha with view-dependent sky tint and reflective highlights, drawn in a blend pass with depth writing disabled.
- The offline Canvas software renderer uses depth-sorted transparent window surfaces, restrained glass reflections, subtle metal highlights, rebalanced practical LED colors, and a new daylight sky/horizon treatment.
- Surface shading changes operate on real editable 3D geometry rather than pasted photographic panoramas or gallery concept images.
- GLB/JSON source retains 2,606 modeled object primitives, 13 stops and prior geometry for continuity. Images in the gallery remain separately labeled conceptual illustrations.

## Verification

Eight JavaScript blocks pass Node syntax checks. Headless Chromium software renderer passes desktop 1440×850 and simulated 412×850 mobile layouts with zero page errors; 13 guided-stop navigation, help/info, roof/section, lighting, and mobile Locations drawer have been exercised. Actual screenshots were compared against Visitor Edition 1.0; material changes are visually different. Project ZIP CRC passed (28 files).

## Remaining release blockers

Not photorealistic: the architecture is still primarily stylized box geometry and lacks high-resolution physically based UV materials, accurate area lighting/shadows and quality modeled props. **WebGL shader visual output is untested** because a graphics-capable WebGL context could not be initialized in this sandbox (static JS syntax is not a GLSL shader compile test). User's physical Samsung Galaxy S25 is also untested.

The complete standalone offline HTML, full ZIP, QA, before-after actual model screenshots, and editable export are archived in ChatGPT Library → VEIL Research Project → Virtual Research Center.

**Review only. Do not merge to main, change the live site, advertise a public preview, or post to Facebook without Andrew's approval.**