# vitrea — Liquid Glass Material Runtime for the Web — Design Spec

## Purpose

Replicate Apple's Liquid Glass material and interaction system (WWDC25's `glassEffect`, `GlassEffectContainer`, `interactive()`, `glassEffectID`) on the web, as an open-source TypeScript library named **vitrea**. Apple's material is not a blur preset: it is real-time, size-parameterized lensing; per-element adaptation of tint, shadow, and foreground to the live backdrop; container-scoped sampling; and shape-to-shape morphing — a system no CSS filter chain can express and no existing web library ships as a production-integrable whole.

vitrea serves four goals at once — a standalone OSS product, the material engine the designer skill's archived SVG-filter direction pointed toward, a technical showpiece, and a commercially credible asset. When those goals conflict on a v1 decision, **fidelity wins** (Decision Log #2).

Positioning: not "the first WebGPU glass demo" — verified prior art exists (liquid-glass-studio, liquidGL, glass-effect-webgpu, liquid-glass-js). vitrea is **the production-oriented, reference-calibrated material compositor for semantic web controls**: explicit backdrop contracts, shared sampling groups, coherent cross-element morphing, adaptive accessibility, progressive fidelity tiers, and fidelity claims backed by a versioned native calibration harness. That combination is what each verified competitor lacks.

## Locked design decisions (from the 2026-08-24 grill and review round)

See the Decision Log for rationale and rejected alternatives. In brief: hybrid-first backdrop promise; WebGPU + CSS-only renderer ladder (no WebGL2 in v1); framework-agnostic core + React bindings only; monorepo restructure of this repo (plugin untouched at `skills/`); native SwiftUI calibration harness from the start; v1 = primitives + core controls + one cross-layer morph pair; finish line = public demo site + npm publish of `@vitrea/core` and `@vitrea/react`; the Chromium-only SVG-displacement tier gets a reserved capability seam but no v1 implementation.

## What "done" looks like (acceptance, phrased as behavior)

1. **Arbitrary DOM, zero setup.** A React app wraps its tree in `GlassRoot` and places `GlassButton`s in a `GlassToolbar` over ordinary page content. Glass renders via the dom-backdrop path (CSS backdrop proxy + GPU optics). Label text remains real DOM: selectable, focusable, IME-capable, announced by VoiceOver as a button.
2. **Texture upgrade.** Registering an image or video as a group's backdrop upgrades that group to true refraction: edge lensing visibly bends the backdrop, and a larger surface shows deeper shadow and stronger lensing than a small button over the same backdrop.
3. **Interruptible press.** Pointer-down produces press-point glow and ~1–2% compression on a spring; releasing mid-press redirects the animation from its current position and velocity with no snap or restart.
4. **The morph.** Activating a toolbar button morphs it into a menu platter as one continuous material transition on the overlay plane — geometry, radius, and material thickness interpolate; no crossfade of two separate surfaces. The menu's glass body correctly occludes the toolbar's DOM content beneath it.
5. **Honest degradation.** In a browser without WebGPU (e.g. flagged Firefox on Linux), the same app renders presentable CSS-tier glass with no console errors, and `useGlassCapabilities()` reports `renderer: "css"`. No tier ever silently pretends to a capability it lacks.
6. **Accessibility modes.** `prefers-reduced-motion` removes overshoot and deformation while preserving spatial continuity; `prefers-contrast: more` strengthens borders and forces near-monochrome foregrounds; `forced-colors: active` renders system colors with no glass. Each is overridable via `GlassRoot` props.
7. **Calibrated fidelity.** The calibration suite diffs demo renders against versioned `apple-macos-26.5-*` fixtures across canonical scenes (backgrounds × components × states × sizes) with shape, material, and motion metrics inside declared thresholds — including holdout scenes not used for tuning.
8. **Shipped.** `npm install @vitrea/core @vitrea/react` works; the public demo site shows the showpiece with side-by-side native captures; the README's fidelity claim reads "reference-calibrated against macOS 26.5 captures," nothing broader.

## Architecture

### Repo layout & packages

This repo becomes a dual-artifact monorepo (pnpm workspaces). The existing plugin is untouched: the marketplace installs from `./` and reads `skills/`; the root `package.json` is `private: true`.

```
packages/
  core/            scene model, instance registry, capability/tier resolution,
                   material policy, scheduler interfaces, accessibility policy
  geometry/        ShapeSpec → ContourIR → compiled shapes; continuous corners,
                   concentric offset, parametric morph solver, group union
  motion/          MotionDriver family (springs, attack/decay, low-pass,
                   crossfade, step), interaction state machine, interruption
  platform-web/    DOM host registration, GeometrySync, GlassLayerManager,
                   backdrop proxies, CSS-tier renderer, media-query policy,
                   WebGPU lifecycle (capability probe, device loss, resize)
  renderer-webgpu/ GPU resource graph, backdrop import, blur/analysis pyramids,
                   group field pass, optics pass, highlight pass, texture pool
  react/           thin declarative bindings (GlassRoot, GlassGroup,
                   GlassSurface, controls); asChild composition seam
  calibration/     fixture schema, diff metrics, profile-fitting CLI
apps/
  demo/            Vite + React public showpiece; also the dev playground
  reference-apple/ SwiftUI capture harness (Xcode project) + capture scripts
```

`core`, `geometry`, `motion` never import `window`, `document`, or `HTMLElement` — pure, unit-testable math and state. `platform-web` owns the browser. `react` maps lifecycle and JSX to `platform-web` registration and stays thin enough that Vue/Svelte/WC adapters later duplicate nothing.

**Published packages: `@vitrea/core` and `@vitrea/react` only.** Internal packages are bundled at publish; the WebGPU renderer loads behind a dynamic import so CSS-tier users never download WGSL.

### The rendering contract

One compositor — one `GPUDevice`, scheduler, pipeline cache, texture pool, instance registry — serving **one canvas pair per managed stacking plane**. v1 ships exactly two planes: **base** and **overlay** (menus/popovers). Per plane, paint order is:

```
page content
  ↓
backdrop-proxy layer     (dom-backdrop mode only: pointer-events:none geometry
                          mirrors carrying backdrop-filter, portaled to the
                          plane root so the optics canvas is never re-blurred)
  ↓
optics canvas            (glass bodies: tint, lensing, rim — pointer-events:none)
  ↓
semantic host DOM        (real <button> etc.: text, icons, focus, IME, a11y tree)
  ↓
highlight canvas         (specular sweeps, press glow — pointer-events:none)
```

Arbitrary interleaving with foreign stacking contexts is **documented out of contract** for v1: all glass lives in GlassRoot's managed planes; menus portal internally to the overlay plane. During a cross-plane morph the surface is promoted to the destination plane so the transition renders on one canvas pair, seam-free. No public layer API ships in v1.

### Core model

```
BackdropSource            GlassGroup                GlassNode
├─ kind: texture | dom    ├─ backdropSourceId       ├─ ContourIR / compiled shape
├─ raw texture/source     ├─ morph namespace        ├─ viewport bounds, clip chain
├─ blur pyramid           ├─ material profile       ├─ z-slot (plane + order)
├─ analysis maps          ├─ adaptation policy      ├─ variant: regular | clear
├─ dirty epoch            ├─ mergeDistance          ├─ interaction state
└─ resolution policy      └─ samplingPadding        └─ foreground policy
```

**Invariant:** blur/analysis pyramids belong to `BackdropSource`, rebuilt **at most once per dirty source per frame** — never per group. Static backdrops rebuild nothing. In dom-backdrop mode the browser compositor does the blur; the GPU builds no pyramid at all.

### Backdrop & analysis contracts (the honesty core)

Capability is a tuple of orthogonal axes, resolved per group and reported by `useGlassCapabilities()`:

```
renderer: webgpu | css
backdrop: texture | dom          (per GlassGroup)
analysis: exact | hint | none
```

- `texture` + `exact`: the app registers a GPU-ownable source (image, video, canvas, procedural gradient, app-rendered texture). Full refraction; luminance/variance/edge-density reduction runs on-GPU with temporal hysteresis.
- `dom` + `hint`: CSS backdrop proxy does blur/saturation; GPU renders rim-lensing approximation, tint, glow, morph. Adaptation comes from **one** hint contract: a `backdrop` prop on `GlassGroup` (`{ tone, luminance?, complexity? }`) or an estimator provider. A built-in best-effort DOM estimator (known background colors/images, CORS permitting) may implement the provider — always documented as an estimator, never implied to be pixel analysis.
- `dom` + `none` (default for arbitrary DOM): fixed regular material, geometry-driven rim/specular, foreground from explicit tokens or `color-scheme`.

A capability seam is **reserved** (not implemented) for two future backends: Chromium's `backdrop-filter: url()` displacement tier and HTML-in-Canvas DOM-to-texture (origin trial, Chrome 148–150).

### Foreground adaptation (GPU → DOM data path)

`ForegroundAdaptation = fixed | author-hint | sampled-async { rateHz, hysteresis }`. GPU classification results reach DOM `color` via **low-frequency async readback** (never per-frame) updating a CSS variable, with threshold + hysteresis so scrolling never pumps the foreground. `sampled-async` is available only where `analysis: exact`; dom-backdrop groups use hints or fixed tones; the CSS tier uses explicit light/dark tokens.

### GPU device ownership

Default: **vitrea owns the device** (`createGlassRoot({ powerPreference })`); apps hand external sources (image/video/canvas → `copyExternalImageToTexture` / `importExternalTexture`). Alternative: **app owns the device** — the app passes its `GPUDevice` and provides same-device texture views per frame, or accepts a render-target callback from vitrea. There is no cross-device texture sharing in WebGPU, so the contract also covers: device-loss recovery, source resize, premultiplied alpha, color space tagging, video frame cadence, visibility pause/resume, and fallback demotion.

### Geometry

Source of truth is a **Contour IR** (cubic Bézier/arc segments + corner metadata + winding), compiled per renderer need to: analytic SDF (v1's only compiled form), distance-mask atlas, or mesh (both post-v1). Shape families in v1 — vitrea's supported set, not "Apple's taxonomy":

- **fixed** rounded rectangle with a continuous-curvature corner profile (Figma-squircle-style bezier fit as the seed; exact coefficients are calibration-determined and internal — the public API exposes only `profile: "continuous" | "circular"`),
- **capsule**,
- **concentric** rounded rectangle: radius = parent contour inward-offset by inset, floored at a minimum — concentricity governs radii, not the curve profile (the research refuted that conflation).

Morphs in v1 are **parametric only**: interpolation over `{ center, size, radii, cornerProfile, thickness }` (capsule ↔ rounded rect, button ↔ menu platter, indicator slides). Contour resampling and topology-changing morphs are post-v1. Group rendering goes through a **per-group field pass** (instances → group SDF/coverage field → one optical pass), which makes bounded smooth-min proximity union within a group nearly free; union aesthetics (neck width, max bulge, separation threshold) are capped and calibration-tuned so nothing reads as jelly.

### Motion

Per-channel drivers, not springs-everywhere:

| Channel | Driver |
| --- | --- |
| position, size, radius, press compression | velocity-preserving interruptible spring |
| lens strength | spring or critically damped |
| glow/illumination | fast attack + slow exponential decay |
| backdrop-adaptation values | exponential low-pass + hysteresis |
| foreground light/dark | threshold + hysteresis + crossfade |
| opacity/materialization, disabled | monotonic ease or step — no overshoot |
| quality tier | long hysteresis + cooldown |

Springs integrate closed-form (or capped fixed-step) so 60Hz, 120Hz, and dropped frames produce the same response. Interaction states in v1: idle, hover, pressed, focused, disabled, morphing. The neighbor glow-diffusion field is post-v1.

Reduced Motion removes elastic overshoot, deformation, and shimmer travel; keeps direct-manipulation positional continuity; shortens morphs to non-elastic interpolation; reserves crossfade for large plane shifts.

### Material variants

`variant: "regular" | "clear"` is first-class. Regular is the adaptive default. Clear is persistently more transparent with constrained adaptation and requires a dimming policy; mixing variants inside one `GlassGroup` raises a dev-mode warning, mirroring Apple's guidance.

### Accessibility policy

Lives in `core` as policy, applied by `platform-web` via media queries with `GlassRoot` prop overrides (`reducedTransparency | reducedMotion | increasedContrast: "system" | boolean`). Reduced transparency → more frosted, less refraction, higher occlusion. Increased contrast → stronger borders, near-monochrome foregrounds, reduced ambient tint. `forced-colors` → system colors, borders, no glass. `prefers-reduced-transparency` is not Baseline; the explicit override is therefore load-bearing, not a courtesy.

### Color pipeline

Internal optical math in linear-light textures; compositing premultiplied-alpha; output sRGB. v1 calibration is locked to sRGB; Display-P3 and HDR/extended-range are future profiles. Without this lock, golden images destabilize across GPUs/browsers and blur/highlight energy drifts from reference.

### Performance envelope & quality governor

The GPU budget (~2ms/frame) is a **hypothesis to validate**, pinned to declared benchmark scenes — mobile: 390×844 CSS px @ DPR 3, one video backdrop, 8 surfaces, 3 groups, 1 active morph, 60Hz; plus a desktop 2× scene — measured per pass (backdrop import, blur, analysis, body, highlight, composite) alongside browser end-to-end frame time. Effect-texture resolution is decoupled from DOM DPR. The governor degrades **within** a tier first (refraction resolution, adaptation cadence, edge analysis) and switches tiers only with long hysteresis and cooldown — never mid-interaction.

### Calibration harness & methodology

`apps/reference-apple` renders canonical scenes — backgrounds (light/dark solids, photo, high-contrast text, video) × components × states (rest/hover/press/release/disabled/selected/focused/menu-open) × sizes — captured on this machine into versioned fixture profiles keyed like `apple-macos-26.5-2x-light-standard` (OS, hardware, scale, color scheme, a11y mode, capture method, refresh rate). Native and web renders use **identical pre-rendered raster backgrounds** so font-rasterization differences never pollute the diff. Metrics are separated by axis: shape (contour distance, corner curvature, silhouette IoU), material (blur edge-spread, luminance transfer, tint response, rim intensity, shadow falloff), motion (response latency, peak compression, overshoot, settling, redirect continuity, morph silhouette trajectory), perceptual (edge-weighted diff, SSIM/OKLab ΔE, human A/B). Fixtures split into calibration / validation / **holdout** sets to prevent overfitting to specific scenes. All fidelity claims cite the profile, never "pixel-identical to Apple."

Spring constants, corner coefficients, tint thresholds, hysteresis rates, merge-distance defaults, and clear-variant dimming are **delegated unknowns**: named here, answered by the harness, recorded into calibration profiles.

### Testing

`geometry` and `motion`: vitest unit tests, TDD. WGSL passes: headless golden-image tests (sRGB-locked). Integration: Playwright against the demo app, including the CSS tier and capability resolution. Fidelity: the calibration diff suite (capture is machine-local; fixtures and thresholds are committed and CI-diffable).

## v1 scope

Components: `GlassRoot`, `GlassGroup`, `GlassSurface` (with `asChild`), `GlassButton`, `GlassIconButton`, `GlassToolbar`, `GlassSegmentedControl`, and a menu built by composing `GlassSurface asChild` over an external accessible menu primitive (React Aria / Base UI class; `@vitrea/react` takes no hard dependency — the demo picks one). Transitions: press/release, segmented-indicator slide, button → menu matched morph. Backdrops: image, video, canvas/app texture, procedural gradient, dom-hybrid. Geometry: the three shape families. Planes: base + internal overlay. Profile: macOS 26.5 first.

## Out of scope (v1 cut list)

WebGL2 backend; Vue/Svelte/Web-Components adapters; Sheet, Slider, Toggle, TabBar, Popover, SearchField; neighbor glow diffusion; scroll-edge effects; arbitrary-contour/resampled morphs; public layer API and arbitrary stacking interleave; automatic pixel analysis of arbitrary DOM (never promised); HTML-in-Canvas backend (seam only); Chromium SVG-displacement tier (seam only — Decision Log #11); Display-P3/HDR profiles; iOS/iPadOS calibration profiles.

## Decision Log

1. **Name: vitrea** (`@vitrea/core`, `@vitrea/react`; npm scope verified unclaimed 2026-08-24). Rejected: *lensing*, *meniscus* (weaker as brands), *glasskit* (collision-prone, bland).
2. **Fidelity-first tiebreaker** among the four purposes (OSS product, designer-skill engine, showpiece, commercial). Rejected: adoption-first, skill-integration-first — the defensible ground against verified competitors is being visibly closest to native. Carried by: calibration harness (§Calibration), v1 cut list.
3. **Hybrid-first backdrop promise** — works on arbitrary DOM, fidelity scales when the app registers GPU-ownable backdrops (§Backdrop contracts). Rejected: GPU-scene-first (shrinks the audience), arbitrary-DOM-only (caps the ceiling).
4. **WebGPU + CSS-only ladder; WebGL2 cut from v1.** Research: WebGPU default-on in all three engines (Chromium 113+/Android 121+, Firefox 141+ Windows / 145+ ARM Mac, Safari 26); Firefox-on-Linux still flagged → CSS tier is a hard requirement, not courtesy (§rendering contract axis `renderer: css`). Rejected: WebGL2 backend (roughly doubles renderer surface for a shrinking tail the CSS tier covers), WebGPU-only (breaks the OSS promise).
5. **Monorepo restructure of this repo**; plugin untouched (manifest reads `skills/`, verified). Rejected: subdirectory project, separate repo.
6. **Core + React bindings only in v1**; adapters later. Rejected: +Web Components (surface before the core API settles), React-only (retrofit cost).
7. **v1 = primitives + controls + one morph pair** — the morph pair is what proves the differentiating subsystems. Rejected: primitives-only (validates nothing distinctive), broad set (delays v1).
8. **Calibration harness from the start** — fidelity-first is unfalsifiable without ground truth. Rejected: eyeball-first, no harness.
9. **Finish line: demo site + npm publish.** Rejected: demo-only, in-repo milestone.
10. **Controlled track; design-whole-then-decompose** — the pieces share one design surface, so the interaction surface had to be generated before cutting. Rejected: single execution plan (too big to execute reliably), autonomous execplan (fidelity taste arises mid-flight).
11. **Chromium displacement tier: seam reserved, not implemented** (fork Option 1, user-decided). Verified: `feDisplacementMap` in `backdrop-filter` is Chromium-only (WebKit bug 245510; Firefox unsupported). Rejected: implement in v1 (third optical stack + Chromium-only calibration fork), never (concedes competitors' best demo permanently).
12. **Review adoptions (2026-08-24 independent reviews, both verified where checkable):** BackdropSource/analysis split with explicit `exact | hint | none` (§honesty core) — fixes the hybrid-mode contradiction; `sampled-async` low-rate readback for foreground (§Foreground) — fixes the GPU→DOM contradiction; canvas pair per managed plane (§rendering contract) — fixes the z-order wall liquidGL demonstrates; backdrop-proxy layer (§rendering contract); GPU device ownership contract (§GPU device ownership); `platform-web` package (§packages); Contour IR over canonical-SDF-as-truth (§Geometry); parametric-only v1 morphs; per-channel MotionDrivers (§Motion); Regular/Clear first-class (§Material variants); color pipeline lock (§Color); blur pyramid owned by BackdropSource (§Core model invariant); calibration rigor — profile keys, raster backgrounds, multi-metric, holdout (§Calibration); benchmark-pinned budget + intra-tier degradation (§Performance); publish two packages with bundled internals; menu via external a11y primitive; repositioned competitive claim (§Purpose).
13. **Review declines/modifications:** SegmentedControl **kept** in v1 (bounded; exercises within-group indicator morph — a distinct case from the cross-plane morph); three parallel hint mechanisms **consolidated** to one prop + provider contract; public `GlassLayer` API **deferred** (internal LayerManager only); flat three-tier naming **superseded** by orthogonal capability axes.

## Surprises & Discoveries

- The design-research run **refuted** the caniuse-derived "85.56% global WebGPU support" figure and the blanket "Firefox disabled by default" claim — caniuse's Firefox row is stale. No verified market-share number exists; the spec cites per-engine facts only.
- The research run's competitive and squircle pillars produced **zero surviving claims**; two independent design reviews filled the gap, and their competitive citations were then verified directly (liquid-glass-studio: WebGL2/WebGPU SDF+springs parameter studio over self-owned backgrounds; liquidGL: shared-canvas snapshot rasterizer whose all-targets-one-z-index constraint is field evidence for the plane model).
- Both independent reviews, working separately, found the **same two contract contradictions** (GPU analysis without a texture; GPU verdicts steering DOM color without readback) — a reminder that internally convergent designs still carry externally visible faults.
- Apple's concentric shapes govern **radius derivation only**, not the corner curve profile — an earlier claim conflating the two was refuted; continuous curvature applies throughout.
- Chromium alone renders SVG displacement inside `backdrop-filter`; WebKit refuses it (bug 245510) and Mozilla lists it as unsupported — confirming the fork's premise and the W3C `svgwg#1142` standards gap.

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-08-24: Initial spec from the chartering grill, design-research run (wf_ce8e34b5-10e), two independent design reviews, and the approved revised design pass.
