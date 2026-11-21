# VEIL Research Center v1.8 — GB-001 Spatial/Thermal Correlation Laboratory

**Concept only. VEIL has not constructed a physical research center.**
**All displays, diagnostic waveforms, indicators and simulated test objects are illustrations—not live SIGNAL data, actual field evidence or paranormal detections.**

## Meaningful 3D work completed

This version substantially reconstructs the previously sparse **Flexible Experiment Room** (stop 09/13) into a physically modeled proposed GB-001 instrumented test environment. The change is to actual navigable world-coordinate geometry in both the WebGL and Canvas software renderers, not a replacement gallery image.

- A clear acrylic GB-001 chamber with independent transparent glass panels, extruded corner frame, gasket/latches, isolation cradle and inert reference target.
- Four separately mounted camera/depth optical heads with annular lenses, gimbal support and modeled cable routing.
- Spatial/thermal correlation frame with two rails, 17 sampled-sensor heads, calibration registration ticks and independent structural supports. A sampled thermal array is **not** a dense thermal camera; no sensing is simulated as real measurement.
- Two modeled review panels with graticules, line plots, indicators and status bars—**all synthetic**.
- Six suspended softbox/diffuser fixtures, rear acoustic diffusers, resilient modular floor platform, instrument console and cable harness.
- Existing room table changed from timber-brown to powder-coat gray; the guided camera pulled back to show the complete assembly.

**Added actual geometry:** 43 named editable mesh groups, **16,264 triangles** at desktop resolution (14,860 on phone-sized viewport due to pre-existing adaptive torus/cylinder tessellation). The existing 13 tour stops, MTC acoustic section, SIGNAL Command Center, roof/section toggles, lighting and navigation are preserved.

## Material/renderer foundation

- Material code 11: separately depth-sorted clear acrylic in the Canvas painter and a dedicated alpha-blended, depth-write-disabled GPU bucket in WebGL. This is approximate transmission/Fresnel, **not raytraced refraction**.
- Added a spatially bounded softbox lighting contribution to the GPU fragment shader for the flexible lab.
- Exported **editable glTF 2.0 GLB with real planar UVs and embedded base-color + metallic/roughness textures**. The GLB has 80 mesh primitives across 43 named source groups, 16,264 triangles, six material categories present in the room and seven deterministic PBR texture pairs. The 80 primitives all round-trip with valid UVs.
- **Important distinction:** The PBR glTF asset is a separate interchange/material study. The HTML tour still uses its existing custom lightweight shader and Canvas renderer; it does **not** yet load those GLB PBR textures. This is not a fully PBR-rendered walkthrough.

## Tested

- Eight inline scripts passed `node --check`.
- Chromium software-rendered all 13 tour stops on 1440×900 desktop and 412×850 mobile-sized viewport; zero page JS errors.
- Roof on/off, section cutaway/restoration, lighting day/night and mobile touch Locations drawer passed; tested manual movement and boundary collision.
- Actual v1.7 vs v1.8 room screenshots were taken from the same camera position/yaw; **38.05%** of whole-image pixels (and **46.70%** of the scene crop) changed by mean RGB difference >20. These are *visual-difference statistics*, not image-quality or photorealism scores.
- GLB imported back successfully: 16,264 triangles, 80 UV-mapped mesh primitives, finite coordinates; source JSON preserved exact per-triangle colors/material codes.
- Complete project ZIP CRC checked.

## Outstanding limitations

- Overall building is **not photorealistic**. Much of the architecture still uses stylized low-detail box primitives, simplistic global lighting, approximate acrylic transmission, and flat/limited materials in the browser tour.
- Actual WebGL shader compilation and GPU output remain **unverified** in this environment (graphics context unavailable). A source-level shader change is included but requires real-device validation.
- Real Samsung Galaxy S25 browser touch/GPU performance **not tested**. Mobile tests used a desktop browser with simulated touch and a 412×850 viewport.
- The room is an architectural/research **visualization**, not a validated engineering drawing or functional apparatus.
- For a convincing photorealistic result, next major work should focus on physically based lighting (including actual area lights/indirect bounce), accurate architecture, PBR texture integration into the interactive renderer, glass depth sorting/refraction and performance profiling on a real phone.

## Deployment status

**Development/review only.** This version does not update the live VEIL website or Facebook and must not be merged/published without separate owner approval. Previous versions remain intact.

### Staging notes
This review branch references `../assets/` for the existing concept gallery. The fully self-contained offline HTML, UV-mapped PBR GLB, source triangle JSON, deterministic texture maps, QA reports, screenshots and complete ZIP are archived in ChatGPT Library → VEIL Research Project → Virtual Research Center. The GLB PBR materials are **not** yet loaded by the HTML viewer. No merge or live deployment is authorized.
