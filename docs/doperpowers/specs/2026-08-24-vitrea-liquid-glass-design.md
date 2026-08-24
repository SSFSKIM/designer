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
5. **Honest degradation.** In a browser without WebGPU (e.g. flagged Firefox on Linux), the same app renders presentable CSS-tier glass with no console errors, and `useGlassCapabilities()` reports the resolved state — `activeRenderer: "css"`, `demotionReason: "no-webgpu"` — while preserving `configuredSource`. No state ever silently pretends to a capability it lacks.
6. **Accessibility modes.** `prefers-reduced-motion` removes overshoot and deformation while preserving spatial continuity; `prefers-contrast: more` strengthens borders and forces near-monochrome foregrounds; `forced-colors: active` renders system colors with no glass. Each is overridable via `GlassRoot` props.
7. **Calibrated fidelity.** The calibration suite diffs demo renders against versioned `apple-macos-26.5-*` fixtures across canonical scenes (backgrounds × components × states × sizes) with shape, material, and motion metrics inside declared thresholds — per supported engine/backend cell, with texture-tier and dom-tier claims stated separately, including holdout scenes not used for tuning.
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
backdrop-proxy layer     (dom-backdrop mode only: ONE pointer-events:none
                          proxy per sampling group, masked to the union of
                          member shapes + samplingPadding, carrying
                          backdrop-filter, portaled to the plane root so the
                          optics canvas is never re-blurred and proxies never
                          double-filter each other)
  ↓
optics canvas            (glass bodies: tint, lensing, rim — pointer-events:none)
  ↓
semantic host DOM        (real <button> etc.: text, icons, focus, IME, a11y tree)
  ↓
highlight canvas         (specular sweeps, press glow — pointer-events:none)
```

Arbitrary interleaving with foreign stacking contexts is **documented out of contract** for v1: all glass lives in GlassRoot's managed planes; menus portal internally to the overlay plane. Two further constraints are **checked, not assumed**: (a) glass surfaces within one plane must not overlap — a dev-mode error, because the sandwich cannot place one surface's body above another surface's DOM label (v1's components never overlap in-plane; the overlapping case *is* the cross-plane case); (b) v1 supports exactly one overlay plane — multiple simultaneous overlays are out of scope. During a cross-plane morph the surface is promoted **as a unit** — body, semantic host, and highlight together — to the destination plane so the transition renders on one canvas pair, seam-free; promotion under scroll and focus is a required integration-test scenario. Backdrop sampling context is a documented constraint: glass hosts must not sit beneath ancestors whose filter, opacity, mask, or clip changes the backdrop root — [Filter Effects 2's Backdrop Root definition explicitly lacks WG consensus](https://drafts.csswg.org/filter-effects-2/), so engines may legitimately differ — and a runtime conformance probe validates the proxy topology at startup, demoting a group to the CSS tier when sampling proves non-equivalent. The full proxy topology across Safari/Chrome/Firefox is **gating spike S1** (§Gating spikes). No public layer API ships in v1.

### Core model

```
BackdropSource            GlassGroup                GlassNode
├─ kind: texture | dom    ├─ backdropSourceId       ├─ shape family params (IR-authored)
├─ raw texture/source     ├─ morph namespace        ├─ viewport bounds, clip chain
├─ blur pyramid           ├─ material profile       ├─ z-slot (plane + order)
├─ analysis maps          ├─ adaptation policy      ├─ variant: regular | clear
├─ dirty epoch            ├─ mergeDistance          ├─ interaction state
└─ resolution policy      └─ samplingPadding        └─ foreground policy
```

**Invariant:** blur/analysis pyramids belong to `BackdropSource`, rebuilt **at most once per dirty source per frame** — never per group. Static backdrops rebuild nothing. In dom-backdrop mode the browser compositor does the blur; the GPU builds no pyramid at all.

### Backdrop & analysis contracts (the honesty core)

Capability is **not a free tuple** — a free product of axes admits undefined and misleading states (a registered texture with no WebGPU; a dom group in an engine whose `backdrop-filter` probe fails; a CORS-tainted video). Configuration and resolution are separate: the app *configures* a source; the runtime *resolves* one of an enumerated set of states per group, reported by `useGlassCapabilities()`:

```ts
interface GlassGroupState {
  configuredSource: "texture" | "dom";     // what the app declared — never mutated
  activeRenderer:  "webgpu" | "css";       // what is actually drawing
  samplingBackend: "gpu-texture" | "css-backdrop" | "none";
  refraction:      "true" | "approximate" | "none";
  analysis:        "exact" | "hint" | "none";
  health:          "ok" | "demoted";
  demotionReason?: "no-webgpu" | "no-backdrop-filter" | "tainted-source"
                 | "incompatible-texture" | "device-lost" | "probe-failed"
                 | "governor";
}
```

Only enumerated states are legal. Every demotion names its reason and its recovery transition (device restored, source replaced, probe re-passed); `configuredSource` survives demotion so an app can always see what it asked for versus what it got. The three healthy primary states:

- `texture` + `exact`: the app registers a GPU-ownable source (image, video, canvas, procedural gradient, app-rendered texture). Full refraction; luminance/variance/edge-density reduction runs on-GPU with temporal hysteresis.
- `dom` + `hint`: CSS backdrop proxy does blur/saturation; GPU renders rim-lensing approximation, tint, glow, morph. Adaptation comes from **one** hint contract: a `backdrop` prop on `GlassGroup` (`{ tone, luminance?, complexity? }`) or an estimator provider. A built-in best-effort DOM estimator (known background colors/images, CORS permitting) may implement the provider — always documented as an estimator, never implied to be pixel analysis.
- `dom` + `none` (default for arbitrary DOM): fixed regular material, geometry-driven rim/specular, foreground from explicit tokens or `color-scheme`.

A capability seam is **reserved** (not implemented) for two future backends: Chromium's `backdrop-filter: url()` displacement tier and HTML-in-Canvas DOM-to-texture (origin trial, Chrome 148–150).

### Foreground adaptation (GPU → DOM data path)

`ForegroundAdaptation = fixed | author-hint | sampled-async { rateHz, hysteresis }`. GPU classification results reach DOM `color` via **low-frequency async readback** (never per-frame) updating a CSS variable, with threshold + hysteresis so scrolling never pumps the foreground. `sampled-async` is available only where `analysis: exact`; dom-backdrop groups use hints or fixed tones; the CSS tier uses explicit light/dark tokens.

### GPU device ownership

Default: **vitrea owns the device** (`createGlassRoot({ powerPreference })`); apps hand external sources (image/video/canvas → `copyExternalImageToTexture` / `importExternalTexture`). Alternative: **app owns the device** — the app passes its `GPUDevice` and provides same-device texture views per frame, or accepts a render-target callback from vitrea. There is no cross-device texture sharing in WebGPU, so the frame contract is operational, not aspirational: every texture source is normalized through one **BackdropFrame acquisition protocol** — `acquire(frameInfo)` at frame start, `release()` after submit, the frame carrying view, size epoch, color space, and alpha mode. `importExternalTexture` handles expire at task end, so video is re-acquired on every frame that samples it, with `VideoFrame` close ownership held by the provider; imported video arrives unpremultiplied while copied images arrive premultiplied, and the compositor normalizes at import. App-supplied views must satisfy declared usage/format/dimension requirements — validated at registration with a typed error, never discovered at draw time. Resizes bump a size epoch that invalidates dependent pyramid allocations. Device loss demotes affected groups (`demotionReason: "device-lost"`) while recovery runs: vitrea-owned devices re-request and re-register automatically; app-owned devices require a replacement-device callback plus a resource re-registration handshake, and groups stay demoted until it completes.

### Geometry

Shapes are authored as a **Contour IR** (cubic Bézier/arc segments + corner metadata + winding) — the interchange representation for export, tessellation, and future arbitrary shapes. The IR is **not** the per-pixel render form: exact distance to a cubic Bézier requires quintic root-finding, so no practical closed-form SDF of the raw contour exists. v1 renders a small set of **parametric pseudo-SDF families** evaluated in-shader with a declared, measured error bound against the true contour (**gating spike S2** validates the bound and the shader cost before the geometry API freezes). Shape families in v1 — vitrea's supported set, not "Apple's taxonomy":

- **fixed** rounded rectangle with a **continuous numeric corner profile** (`smoothing ∈ [0,1]`, 0 = circular arc; the value matching Apple's continuous curvature is calibration-determined and internal, seeded from Figma-squircle fitting — the public API exposes `profile: "continuous" | "circular"` sugar over the number),
- **capsule**,
- **concentric** rounded rectangle: radius derived from the parent's field as a **level-set offset** (inset, floored at a minimum radius) — exact inward offsets of continuous-corner cubics leave the cubic family, so the level-set approximation under the same error budget is the honest contract; concentricity still governs radii, not the curve profile (the research refuted that conflation).

Morphs in v1 are **parametric only**: interpolation over `{ center, size, radii, smoothing, thickness }` — every channel numeric, so every channel interpolates (capsule ↔ rounded rect, button ↔ menu platter, indicator slides). Contour resampling and topology-changing morphs are post-v1. If S2 shows the error budget unachievable, the fallback is promoting distance-mask atlases into v1 — a renderer change behind the same IR, not an API change. Group rendering goes through a **per-group field pass** (instances → group SDF/coverage field → one optical pass), which makes bounded smooth-min proximity union within a group nearly free; union aesthetics (neck width, max bulge, separation threshold) are capped and calibration-tuned so nothing reads as jelly.

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

`apps/reference-apple` renders canonical scenes — backgrounds (light/dark solids, photo, high-contrast text, video) × components × states (rest/hover/press/release/disabled/selected/focused/menu-open) × sizes — captured on this machine into versioned fixture profiles keyed like `apple-macos-26.5-2x-light-standard` (OS, hardware, scale, color scheme, a11y mode, capture method, refresh rate). Native and web renders use **identical pre-rendered raster backgrounds** so font-rasterization differences never pollute the diff. Metrics are separated by axis: shape (contour distance, corner curvature, silhouette IoU), material (blur edge-spread, luminance transfer, tint response, rim intensity, shadow falloff), motion (response latency, peak compression, overshoot, settling, redirect continuity, morph silhouette trajectory), perceptual (edge-weighted diff, SSIM/OKLab ΔE, human A/B). Fixtures split into calibration / validation / **holdout** sets to prevent overfitting to specific scenes. Fixtures record the native side; **results** are versioned by the full render cell: native profile × web cell (browser engine + version, backend tuple, GPU adapter class, canvas color configuration, capture path). Claims and thresholds are **per tier** — the texture tier (vitrea's own shader math) and the dom tier (each engine's own backdrop-filter blur) are calibrated and stated separately, and holdout passes are required per supported engine/backend cell, not once. Canonical scenes include impulse and checkerboard backgrounds, which expose blur kernels and displacement fields directly for system identification. All fidelity claims cite the profile and cell, never "pixel-identical to Apple."

Spring constants, corner smoothing values, tint thresholds, hysteresis rates, merge-distance defaults, and clear-variant dimming are **delegated unknowns**: named here, answered by the harness, recorded into calibration profiles. Two further unknowns gate architecture itself — see §Gating spikes.

### Testing

`geometry` and `motion`: vitest unit tests, TDD. WGSL passes: headless golden-image tests (sRGB-locked). Integration: Playwright against the demo app, including the CSS tier and capability resolution. Fidelity: the calibration diff suite (capture is machine-local; fixtures and thresholds are committed and CI-diffable).

## Gating spikes

Two prototypes run **before their contracts are built upon**; their outcomes land in the Decision Log. They are the first children of the decomposition, not afterthoughts:

- **S1 — backdrop proxy topology.** Prototype the per-plane sandwich with one masked proxy per sampling group over arbitrary DOM in Safari, Chrome, and Firefox: sampling equivalence versus in-place backdrop-filter, overlap and paint-order behavior, scroll/fixed/zoom behavior, and whether the conformance probe can actually detect failure at runtime. A failing engine narrows the promise (its dom groups demote to the CSS tier) — it does not change the API.
- **S2 — geometry field error and cost.** Measure the parametric pseudo-SDF families' field error against ground-truth contour distance across the smoothing range and a size sweep, and their shader cost on the benchmark scenes. Failure promotes distance-mask atlases into v1 behind the same Contour IR.

## v1 scope

Components: `GlassRoot`, `GlassGroup`, `GlassSurface` (with `asChild`), `GlassButton`, `GlassIconButton`, `GlassToolbar`, `GlassSegmentedControl`, and a menu built by composing `GlassSurface asChild` over an external accessible menu primitive (React Aria / Base UI class; `@vitrea/react` takes no hard dependency — the demo picks one). Transitions: press/release, segmented-indicator slide, button → menu matched morph. Backdrops: image, video, canvas/app texture, procedural gradient, dom-hybrid. Geometry: the three shape families. Planes: base + internal overlay. Profile: macOS 26.5 first.

## Out of scope (v1 cut list)

WebGL2 backend; Vue/Svelte/Web-Components adapters; Sheet, Slider, Toggle, TabBar, Popover, SearchField; neighbor glow diffusion; scroll-edge effects; arbitrary-contour/resampled morphs; public layer API and arbitrary stacking interleave; same-plane overlapping glass surfaces (checked dev-mode error) and more than one simultaneous overlay plane; automatic pixel analysis of arbitrary DOM (never promised); HTML-in-Canvas backend (seam only); Chromium SVG-displacement tier (seam only — Decision Log #11); Display-P3/HDR profiles; iOS/iPadOS calibration profiles.

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
13. **Review declines/modifications (2026-08-24 design reviews):** SegmentedControl **kept** in v1 (bounded; exercises within-group indicator morph — a distinct case from the cross-plane morph); three parallel hint mechanisms **consolidated** to one prop + provider contract; public `GlassLayer` API **deferred** (internal LayerManager only); flat three-tier naming **superseded** by orthogonal capability axes (themselves superseded by the resolved-state model in #14).
14. **Adversarial spec review adoptions (codex `gpt-5.6-sol`, 2026-08-24) — all six findings survived verification against the cited specs; none rejected:** same-plane overlap becomes a checked constraint and cross-plane promotion is specified as unit promotion (§rendering contract); backdrop proxies become one masked proxy per sampling group with a startup conformance probe and demotion path, gated by spike S1 (§rendering contract, §Gating spikes); the free capability tuple is replaced by an enumerated resolved-state model with named demotion reasons (§honesty core); the device contract becomes the operational BackdropFrame acquisition protocol (§GPU device ownership); "analytic SDF of the contour" — mathematically vacuous for cubics — is reformulated as parametric pseudo-SDF families with a measured error bound, continuous corner smoothing, and level-set concentric offsets, gated by spike S2 (§Geometry); calibration results gain the web-side cell axis with per-tier claims and per-cell holdouts (§Calibration).

## Surprises & Discoveries

- The design-research run **refuted** the caniuse-derived "85.56% global WebGPU support" figure and the blanket "Firefox disabled by default" claim — caniuse's Firefox row is stale. No verified market-share number exists; the spec cites per-engine facts only.
- The research run's competitive and squircle pillars produced **zero surviving claims**; two independent design reviews filled the gap, and their competitive citations were then verified directly (liquid-glass-studio: WebGL2/WebGPU SDF+springs parameter studio over self-owned backgrounds; liquidGL: shared-canvas snapshot rasterizer whose all-targets-one-z-index constraint is field evidence for the plane model).
- Both independent reviews, working separately, found the **same two contract contradictions** (GPU analysis without a texture; GPU verdicts steering DOM color without readback) — a reminder that internally convergent designs still carry externally visible faults.
- Apple's concentric shapes govern **radius derivation only**, not the corner curve profile — an earlier claim conflating the two was refuted; continuous curvature applies throughout.
- Chromium alone renders SVG displacement inside `backdrop-filter`; WebKit refuses it (bug 245510) and Mozilla lists it as unsupported — confirming the fork's premise and the W3C `svgwg#1142` standards gap.
- The adversarial review caught that "analytic SDF of the contour" was mathematically vacuous — exact cubic-Bézier distance requires quintic root-finding — and that exact inward offsets of continuous-corner cubics leave the cubic family; both forced the pseudo-SDF / level-set reformulation.
- `importExternalTexture` handles expire at task end and imported video arrives unpremultiplied — per-frame reacquisition is a WebGPU semantic, not an optimization choice.
- Filter Effects 2's Backdrop Root definition explicitly lacks working-group consensus, so cross-engine backdrop sampling equivalence cannot be assumed — only probed (hence spike S1).

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-08-24: Initial spec from the chartering grill, design-research run (wf_ce8e34b5-10e), two independent design reviews, and the approved revised design pass.
- 2026-08-24 (same day, second revision): adversarial spec review round — six findings, all adopted (Decision Log #14): checked overlap constraint and unit promotion, per-group masked proxies with conformance probe, resolved-state capability model, BackdropFrame protocol, pseudo-SDF geometry reformulation, per-cell calibration matrix, gating spikes S1/S2.
