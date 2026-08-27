# v1 recomposition evidence — 2026-08-26

Child of [the vitrea composite spec](./2026-08-24-vitrea-liquid-glass-design.md).
This document is the evidence record for §Parent-Level Acceptance: the eight
behaviors of §What "done" looks like, verified **end-to-end in the shipped
artifacts** — a cold consumer app built against the registry tarballs, the live
site, and the calibration suite — not the sum of child gates.

## Provenance

- `@vitreajs/vitrea@0.1.0` and `@vitreajs/vitrea-react@0.1.0` published
  2026-08-26 by the user (registry `time.modified` 2026-08-26T14:54:25.932Z).
- Consumer app: Vite 8 + React 19, built OUTSIDE the workspace;
  `package-lock.json` resolves both packages to `registry.npmjs.org` tarballs;
  the built bundles contain **zero** occurrences of any workspace path. Runtime
  export counts 41 (core) / 33 (react). Viewport 1440×900 at deviceScaleFactor 1.
- GPU-tier runs use full Chromium (`channel: "chromium"`) with
  `--enable-unsafe-webgpu --enable-features=Vulkan,WebGPU`. Playwright's default
  headless shell gets a SwiftShader adapter whose device is immediately lost, and
  the runtime honestly resolves `css / no-webgpu` — a harness fact worth knowing,
  not a product defect.
- Live site: https://ssfskim.github.io/designer/ (GitHub Pages, deployed from
  `main` at d55d8e3).

## The eight verdicts

**1. Arbitrary DOM, zero setup — PASS.** Three `[data-vitrea-proxy]` elements
(`dom-region`, `toolbar`, `toolbar-menu`), each with computed
`backdrop-filter: blur(8px) saturate(1.8)` and a members-derived `clip-path`;
the texture group correctly has none. All four groups `webgpu / ok`. Hiding only
the optics canvas changes the plate region by mean 65.78 abs RGB — the GPU optics
are painting. The label is real DOM: `getSelection()` returns exactly `"Share"`,
the button takes focus, IME insertion yields `日本語入力`, and the platform
accessibility tree reads `toolbar "Document actions" → button "Share"` (the
automatable stand-in for VoiceOver). Zero console messages. One surprise
recorded in §Consumer report: `GlassMorph`'s hoisted closed platter holds the
toolbar's first tab stop.

**2. Texture upgrade — PASS, one sub-claim re-expressed.** Registering a real
`HTMLImageElement` upgrades the group to `gpu-texture / refraction: true /
analysis: exact` while the dom group on the same page stays `css-backdrop /
approximate / hint`. Lensing measured as boundary displacement of a hard band
edge 23.5px inside the contour, against a control edge outside all surfaces:
monotone in declared thickness — 0 / 0 / −0.06 / **+4.22** / **+9.15** /
**+18.22** px at thickness 0/5/12/18/30/50, control 0.00 at every step. The
thick plate's edge optics reach 6–8× deeper than the small button's (lens band
15px vs 2px, regular). **The re-expression: the material paints no external
drop shadow at all** (24px outside ring: mean abs diff 0.000 for both surfaces,
both variants) — the acceptance's "deeper shadow" phrase, written 2026-08-24,
predates Decision Log #32(e)/#34(e) where the shadow term was measured as a
fidelity liability and removed; what the phrase was pointing at (a
size/thickness-dependent depth read) is the internal rim deviation and lens-band
depth tabulated above, and it holds.

**3. Interruptible press — PASS.** Off-centre press at (+17, +13): compression
settles at 1.50% (constant `pressCompressionScale = 0.015`, peak 1.56% with
elastic overshoot to 1.0382 on the press channel), glow rises 0 → 0.594 at
exactly the press point (`--vitrea-press-x: 17px`, `-y: 13px`). Released
mid-rise at 0.3956 with velocity +0.1797/frame: the next frame is 0.5029 —
momentum carried through the release, then turnover and settle with a −0.0196
elastic undershoot. The step across the release boundary (+0.1073) is smaller
than the largest in-flight step (0.1797): no snap, no restart. Zero console
messages.

**4. The morph — PASS, thickness channel unobservable from outside.** Across 71
opening and 70 closing frames: exactly one `[data-vitrea-morph]`, constant
total surface count, morph host opacity 1 every frame — not a crossfade. Top
816 → 651 (median step 0.235px) with a 1.84px elastic overshoot; radius
interpolates 16 → 21.8 in 14 monotone steps read from the group proxy's
`clip-path`; the group promotes base → overlay and back, proxy moving with it.
The opened platter occludes the toolbar's DOM text: hit test at the text centre
flips from the region section to `button.menu__item`, mean abs RGB diff 123.79
over the text area. `thickness 8 → openThickness 16` is declared but carried in
no DOM channel, so it is reported as declared, not measured.

**5. Honest degradation — PASS.** Full Chromium with WebGPU feature-disabled AND
`navigator.gpu` deleted, app unchanged, still requesting `renderer="webgpu"`:
all four groups `activeRenderer: css / health: demoted / demotionReason:
no-webgpu`, `configuredSource` preserved (`texture` and `dom`), stable across an
interaction round. Presentable glass via host-level declarations (glass-vs-none
mean 90.1 abs RGB). **Zero console errors**; the single warning is the runtime
naming the demotion and its honest `recovery: "none"`. The inverse holds:
`?renderer=css` by choice reports `health: ok` with no demotion reason —
choosing is not failing. Correction recorded: the CSS tier has **no** proxy
elements — proxies are a GPU-tier construct; the CSS tier writes
`backdrop-filter` on each host. Independently, the recomposition's live-site
capture under the headless shell (genuinely WebGPU-less) exercised the same
path on the shipped site: CSS-tier glass, readout `css / no-webgpu /
configuredSource preserved`, zero console errors.

**6. Accessibility modes — PASS.** Reduced motion (emulated + prop): press
compression 1.47% → 0% while glow still animates; morph endpoints identical,
overshoot gone, monotone approach; prop `reducedMotion={false}` overrides the
media query back. Increased contrast (emulated + prop): border 1px → 2px,
border alpha 0.353 → 0.95, saturate(1.8) → saturate(1), ink to chroma-0 black,
`--vitrea-foreground` → `light-dark(#000, #fff)`; prop override returns every
value. Forced colors: opaque `Canvas` background, 2px `CanvasText` border,
`backdrop-filter: none`, GPU proxies neutralised to blur(0), optics contribution
collapses to 7.72 mean abs RGB; no `forcedColors` override prop, matching the
published `GlassRootProps`. Reduced transparency (prop path; no Playwright
emulation exists): blur 8 → 14px, background alpha 0.78 → 0.882,
`--vitrea-occlusion` 0.781 → 0.884.

**7. Calibrated fidelity — MET.** Thresholds adopted 2026-08-26 as proposed and
enforced by `packages/calibration/test/adopted-thresholds.test.ts`; fresh run at
recomposition: 128/128. Two capture gaps recorded in the composite spec as
accepted limitations (motion metrics; the 2× and accessibility profiles), both
feeding the post-v1 controlled-recapture item.

**8. Shipped — PASS.** Cold `npm install @vitreajs/vitrea @vitreajs/vitrea-react
react react-dom` resolves; both entries import under native ESM in node;
react-dom is a `>=19.0.0` peer in the registry metadata (the #41(b) inlining
defect confirmed absent from the shipped bytes). The shipped README's claim
reads exactly "Reference-calibrated against macOS 26.5 captures," scoped to the
texture tier. Live site at DPR 2: home and playground render clean, GPU tier
healthy (`webgpu / gpu-texture / refraction: true / analysis: exact`,
`health: ok` on every group), native fixtures resolve, zero console errors (one
non-reproducible 404 on first visit was the browser's `favicon.ico` probe — the
site ships no favicon; cosmetic).

## Consumer report — first cold consumption of the published packages

Nine findings, in rough order of cost. These seed the 0.1.1 patch and the
post-v1 docs round.

1. **29 `TS2304` errors under `skipLibCheck: false`**: both published `.d.ts`
   files reference 14 WebGPU global types (`GPUDevice`, `GPUTextureView`, …)
   but neither package declares them nor depends on `@webgpu/types`. Cheap fix:
   ship the dependency or a `declare` block.
2. **`setBackdropTexture` — the API acceptance #2 is about — appears in neither
   README**, and neither does the texture placement contract (`object-fit:
   cover` over the whole viewport, not the group). An app that also paints the
   image must match that mapping; discovered only from the `.d.ts` JSDoc and
   the WGSL.
3. **The GPU tier is silently unreachable under Playwright's default headless
   shell** — everything works, on the wrong tier, and the readout honestly says
   `no-webgpu`, so you believe it. The recipe lives only in an internal
   playwright config; READMEs mention neither the flags nor `channel`.
4. **The library's defaults trip its own 3σ rule under its own
   `reducedTransparency` mode**: blur 14px → floor 42 > default padding 24; one
   prop flip emits 7 warnings including a `proxy-overlap-after-enforcement` at
   the demo's own toolbar gap. GPU tier only.
5. **`[data-vitrea-proxy]` exists only on the GPU tier** — reasonable, but
   undocumented, and it changes what "confirm the dom-backdrop path" means per
   tier.
6. **`GlassMorph`'s closed platter takes the toolbar's first tab stop** (hoisted
   plane mount precedes the `<nav>`; roving tabindex follows document order).
   Correct ARIA, unexpected sequence, undocumented.
7. **`GlassSurface` has no intrinsic size** — the plane host layer's parent is
   shrink-to-fit; the sizing model is undescribed.
8. **README export list omits `APPLE_LIKE_SMOOTHING`**, which `GlassMorph`'s
   corner profile needs.
9. **The published react `package.json` ships its `devDependencies`**, including
   three unpublished `@vitrea/*@0.0.0` workspace names — harmless, but noise
   that advertises versions the registry doesn't have.

Two things that went right and are worth keeping: the `.d.ts` JSDoc is the best
documentation in the package (it is what got the texture path, corner-reference
rule, and plane model across), and X7 held through a plain consumer build with
zero configuration — no runtime deps, and the WebGPU renderer emitted as its own
lazily-loaded chunk (86 kB / 29.9 kB gzip) that a CSS-tier session never
fetches.
