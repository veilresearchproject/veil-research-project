# VEIL Research Center — A Vision Taking Shape (draft v0.3)

**Before it is built, it must first be seen.**

This folder is a proposed future-facility vision for the independent VEIL Research Project. It is **not** an existing, built, financed, staffed, licensed, or professionally engineered research center. The virtual 3D model is conceptual and separate from its five cinematic concept images.

## Preview and publish

Open `index.html` directly in a desktop browser or copy this directory to a local static HTTP server. When this branch is eventually reviewed and merged into `main`, GitHub Pages can serve the tour at `/veil-research-project/future-research-center/`. **No publication should occur before Andrew's approval.**

Features: custom WebGL concept model and software fallback; guided tour through exterior, reception, research spaces and the **upstairs** SIGNAL Command Center; concept gallery; mobile touch movement, mouse/keyboard navigation; separate covered loading annex for four vans; SIGNAL future-system preview (no active feeds).

Dependencies: none; artwork is hosted locally in `assets/`. All controls are illustrative and no real devices, facility cameras, or data systems are connected.

## QA status

- Verified: JavaScript syntax (`node --check`), HTML references and WebP asset decoding, 11 guided stops, 3D primitive layout, branch assets.
- Not yet verified: interactive rendering in an ordinary desktop GPU browser, Galaxy S25 mobile browser, different device accessibility settings. Headless Chromium in the automated test container did not initialize an EGL graphics display, which limits visual QA.
- Needs professional review before any physical construction proposal: structural, ADA, life safety, HVAC, cabling, acoustic treatment, power, budgets and dimensions.

Website copy and Facebook artwork should explicitly retain the concept-only status.
