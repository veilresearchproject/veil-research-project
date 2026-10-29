# VEIL Research Center — SIGNAL Command Room v1.7

**Future conceptual facility only. VEIL has no constructed research center.**

## Scope of this version

A substantial ACTUAL 3D interior upgrade of the second-floor SIGNAL Command Center. Previous versions largely showed plain blue situation display panels. The new room has six high-detail situation monitors modeled in geometry, seven embellished workstations, simulated 3D waveform traces, alarm/status bars, acoustic ceiling baffles, overhead cable channels, and indirect ceiling lighting. The last of the 13 existing stops now looks into this command room rather than facing the laboratory windows. The laboratory overlook remains accessible by turning around and by navigating.

IMPORTANT: All graphic telemetry in the display is **simulation/concept art in real 3D geometry**, not sensor readings, recordings or evidence. No SIGNAL backend or live cameras are connected.

## Mesh and source assets

* New editable non-box Command Center GLB: 41 named mesh groups, 7,912 triangles, with source triangle JSON.
* Existing architectural boxes and earlier curved instruments and high-bay meshes are preserved in the source.
* 13 guided stops preserved; roof/section, day/night lighting, mobile and WASD movement retained.
* Standalone single-file HTML has its concept images embedded. `future-research-center/index.html` references adjacent assets folder and is suitable for website review.

## Test evidence

* All eight inline JavaScript blocks parse via Node --check.
* Exported command-center GLB re-imports with 41 named groups and 7,912 triangles and finite vertices.
* Headless Chromium **software renderer** tested all 13 stops and roof-off/on, interior section and day/night toggles, at desktop 1440×850 and phone-sized 412×850. Zero browser JavaScript page errors.
* Actual v1.6 vs v1.7 model screenshots of exactly the same command-room camera show ~17% of pixels changed beyond mean RGB difference 20. That measures an image change, NOT photo realism.
* ZIP archive integrity CRC tested.

## Not validated / remaining release gates

* No GPU/WebGL context could be initialized in this environment. WebGL shader compilation and output therefore remain **unverified**.
* No physical Samsung Galaxy S25 browser touch/performance test was possible; phone-sized tests used desktop browser viewport emulation.
* Whole building is still largely stylized and low-fidelity. Physically based UV textures, materials, more realistic area lighting/GI and higher-resolution architectural surfaces remain outstanding. Not a photorealistic final release.
* This is not an engineered plan and should not be represented as a constructed facility.

## Deployment

**Development/review copy only**. Do not merge the GitHub draft, update the live VEIL website or post to Facebook without separate explicit owner approval.

GitHub review path: `future-research-center/command-v17/`. Images resolve from `../assets/` on deployment. Full offline standalone HTML, editable GLB, triangle JSON and QA screenshots are stored in ChatGPT Library → VEIL Research Project → Virtual Research Center. DO NOT merge or publish without owner approval.
