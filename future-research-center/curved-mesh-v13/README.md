# VEIL Research Center — High-fidelity curved geometry study 1.3

## What changed

This is the first major **non-box triangulated geometry subsystem** in the existing real-time 3D walkthrough. It is part of the actual world-space scene and renders using the same camera and material lighting as the original architecture, in both WebGL and Canvas software fallback. It does **not** project 2D concept images onto the scene.

- **30 curved mesh groups, 14,428 triangles in the full desktop export**, alongside the existing 2,606 box-based architectural components.
- ECHO copper annular test fixture and stainless mandrel; visible visitor-side multi-winding ring assembly.
- MTC recorder concept model with cylindrical body, concentric collars, and a detailed directional microphone on a stand; additional capsules and tactile interface controls.
- Twelve Six-Plane Light Cage circular optical housings and five Temperature Curtain cylindrical sensor housings.
- Two reception ceramic circular planters.
- New *dedicated drawArrays GPU VBO* for curved meshes, avoiding overflow of the base model's Uint16 drawElements index limit.
- Responsive curved mesh level-of-detail (fewer segments on narrow screens) and group-distance culling for Canvas fallback.
- Separate **VEIL_Curved_Instruments_v13.glb** and **VEIL_Curved_Instruments_v13_geometry.json** source for future editing/import into professional modeling software.

## Tests

Desktop (1440×850) and simulated mobile (412×850) Chromium Canvas fallback tests pass with 13 stops, roof, cutaway, day/night and navigation. The MTC before-and-after actual-model screenshot has a measurable visual difference. Eight inline JavaScript sections parse with Node. GLB reload verifies **30 mesh groups and 14,428 triangles**.

## Honest limitations

This is **not photorealism yet**; the existing building is predominantly box primitives, and shading is approximated. WebGL GPU context remained unavailable in headless Chromium, so the newly added GPU drawArrays code needs validation on real graphics hardware. Real Samsung phone performance still needs a device check. The architectural center is a future vision, not a constructed/operational facility. These designs are illustrative, not tested engineering specs.

## Release rule

No modifications to the live VEIL site or Facebook publication. This is a local review package, not a finished production replacement. Preserve full editable geometry and all earlier versions.
## GitHub review path

This folder is isolated at `future-research-center/curved-mesh-v13/` and consumes images from the existing `future-research-center/assets/` directory. The 30-group exported editable mesh GLB, per-triangle JSON, and complete self-contained HTML are retained in ChatGPT Library. **Draft only; do not merge or change the live website without owner approval.**
