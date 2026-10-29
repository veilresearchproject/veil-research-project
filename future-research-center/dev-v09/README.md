# VEIL Research Center — Architectural Model v0.9

**A Vision Taking Shape** — a speculative *future* research center, not an existing built or engineered facility. October 29, 2026.

## Start

Extract the archive and open `future-research-center/index.html` in Chrome or Edge. Press **Explore the 3D Research Center**.

- **NEW: Focus view** in the lower right, or press **F**. Hide floating panels while retaining discreet Previous/Next viewpoint buttons and the future-center concept label. Press again to restore full tour panels. Focus mode is designed for actual model inspection, not concept art.
- **Improved exterior camera** gives more room to see the whole facility and approach.
- **R** toggles the removable roof (browser viewer only). Top toolbar also has **Lighting: Day / Lab night**.
- Navigate with W/A/S/D or on-screen arrow keys; drag mouse/touch to look, move through stairway, switch levels, or choose one of 13 stops.
- Small-screen layout has a Locations drawer; the focus-mode shortcut remains accessible on phone-sized viewports.

## Modeled scene additions

3D detailing around the office glazing, entry portal and approach, diffuse light fittings, low landscape beds, second-floor command-area glass, lab perimeter service raceways, MTC acoustic absorbers, hardware and walkways. All modeled as actual geometry, not pasted pictures. Units, dimensions and engineering clearances remain conceptual.

## Performance change

The Canvas 2D fallback no longer resizes its drawing surface every animation frame. Software rendering uses conservative bounding-sphere view culling to skip offscreen objects before polygon projection, reducing CPU usage when visitors explore interior rooms. WebGL retains the larger scene; detailed physical shaders / GPU-device performance remain unverified.

## Editable files

- `VEIL_Research_Center_v09_geometry.json`: full tagged, editable box-model source.
- `VEIL_Research_Center_v09.glb`: static exported model with roof present.
- `index.html`: complete offline interactive tour. All illustration assets bundled locally. No paid subscriptions, external scripts or API keys.

## Release gates

Desktop WebGL GPU compilation, Samsung Galaxy S25 physical testing, material quality, frame rates and accessibility remain to be verified. This is not photorealistic and there is no physical research center. Do not publish the development version or merge draft PRs without explicit owner review.

## GitHub review only

This source is staged under `future-research-center/dev-v09/`, references shared `../assets/` concept imagery, and is **not published or merged**. Editable geometry JSON, static GLB, and offline project ZIP are preserved in the VEIL Virtual Research Center ChatGPT Library folder. Desktop and simulated phone software renderer tests pass; GPU/mobile hardware remains outstanding.
