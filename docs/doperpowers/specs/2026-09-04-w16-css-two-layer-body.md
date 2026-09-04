# W16 — The two-layer CSS body: the two-component law, the depth ramp, the second scale and the lift on the CSS tier (2026-09-04)

> **Parent:** the post-v1 wave (`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`),
> by way of W11's Deferred entry "Chartered, deferred (Decision Log 5) — the
> two-layer CSS body" (`2026-09-02-w11-remaining-floors.md`; claims §5.42 §5),
> which every body wave since has extended: W13's Deferred (the depth ramp
> through a two-layer body with an inset mask, W13 Decision Log 5 (a)), W14's
> Decision Log 4 (the CSS tier's added-light term deferred to "the layering
> decision the two-layer CSS body work should make once, for both features"),
> and W15's Decision Log 3 (the tier keeps the 1x law at every scale, and
> claims §5.70 §5's four-column table is this charter's opening brief).
> **Ordering (user, 2026-09-04):** "the next opener is the two-layer CSS body
> charter: the CSS tier still draws the 1x law at every scale by your
> decision, and the four-column table from this wave is the brief that charter
> starts from." **Consumes:** claims §5.42 §5 (the tier's mixed σ is the worst
> single form on the probe, RMS 0.049–0.078 against the GPU law's 0.014–0.028;
> Chromium renders the two-component law as two sibling `backdrop-filter`
> layers with the heavy one's `opacity` as the mix weight to RMS 0.0011, and
> not at all as a nested child), §5.38 §2 (the dom rows' deficit after the
> body is the rim band, which no CSS form carries), §5.55 §5 and §5.69 §4 (the
> reference's single-blur ceiling at 2x, 3.0 / 2.5 / 4.0 / 5.0 / 5.0 CSS px,
> predicted by the reference's own mix through its own widths to within 0.8
> CSS px), §5.65 §2 and §5.66 (the lift read through sRGB's decode; the CSS
> tier's derived black alpha `α′ = α − L/B` and the residual it cannot close —
> `photo__rrect-md` 0.1803 against 0.2013), §5.68 §7 (the CSS tier's σ and the
> stacked cells' proxy padding), §5.70 §5 (the table). **Starts from** `main`
> at the W15 bed (`c00f89e`, recomposed `1130104`; 0.5.0 published from
> `26b159f`): the GPU tier's body is the fourth-form ramp over a fully-heavy
> 2x deep value with device-pixel widths at every scale; the CSS tier is one
> in-place `backdrop-filter: blur()` at the 1x law's single-σ projection at
> every scale (`CSS_TIER_RAMP_SCALE = 1`), the black multiply with W14's
> derived alpha and no lift, eight dom-tier `ssimMean` floors held by decision
> since W11c (`UNMET_ROWS` 8, all of them the CSS tier's).

## Purpose

The CSS tier is the tier every engine without WebGPU gets, the tier a failed
probe demotes to, and the tier the demo's reduced paths run on — and its body
has been the wrong shape since the reference's body was measured. The
reference's body is two components: a sharp term at about one device pixel and
a heavy term at eight to ten, mixed by a share that is highest just inside the
contour and fades over a fixed reach to a span-graded deep value (W11c, W13,
W15). The GPU tier carries all of that. The CSS tier carries one `blur()` at
one σ per span — the law's single-σ projection, on the author's host element
itself, the tier creating no element of its own — and a single Gaussian
cannot be both sharp and faint (§5.42 §5): at the tier's transmission a sharp σ draws
the checker too strong and the mixed σ draws it too soft, so the tier's
interior spread reads 0.069 against the reference's 0.113 on `rrect-md` and
0.026 against 0.065 on `rrect-lg`, its checkerboard means fell 0.008–0.012
when W11c moved it to the mixed σ, its `hc-text` rows fell 0.013–0.027, and
eight `ssimMean` rows on the checkerboard cells are held by decision with the
claim narrowed to "the mixed-σ form". Every one of those is a documented gap
to macOS, and every one has the same cause.

Chromium can draw the law. Measured at W11c: two sibling elements over the
same backdrop, the first at `blur(1.25px)` and the second at `blur(9.92px)`
with `opacity: 0.4`, render 0.6·G₁.₂₅ + 0.4·G₁₀ of the backdrop to RMS 0.0011
in encoded luma — the second layer blurs the first's output, so the composed
heavy σ is σ_b·√(1 + (gain² − 1)) = σ_b·gain, and its `opacity` is the heavy
share. The same layer as a **child** of the first is inert. So the form is a
second layer drawn after the sharp one and under the host's content, and it
was deferred at W11c because it changes the tier's in-place doctrine and the
rim's painting order for an expected yield of one floor. Three waves later the
yield is larger and the decision is overdue, because three more things now
wait on the same second element:

1. **The depth ramp.** W13's k(u) — the heavy share rising linearly from
   `1 − s₀(span)` at the contour to `kDeep(span)` at the reach — is a
   spatially varying mix, which one `opacity` cannot carry and a `mask-image`
   on the heavy layer can (W13 Deferred).
2. **The second scale.** At 2x the tier draws the 1x law by decision (W13
   Decision Log 5 (a), W15 Decision Log 3), and the table W15 handed over
   says why no projection of one σ can reach the reference's 2x ceiling: the
   tier's fully-heavy end is 6.0 CSS px where the reference's heavy width at
   2x is 3.0–5.0, and its mix saturates at 0.60–0.91. The reference's own mix
   through its own widths predicts its own ceiling to within 0.8 CSS px on
   every span (§5.69 §4) — so a tier that draws two layers at device-pixel
   widths through the live ratio, with the heavy share as the GPU tier
   computes it, is predicted to land there with no term of its own.
3. **The lift.** W14's outer shadow is a black multiply plus the backdrop's
   own blurred light on one falloff; the CSS tier paints the multiply with a
   derived alpha and cannot paint an addition with one element, and the
   residual is measured (`photo__rrect-md` 0.1803 against 0.2013). W14
   Decision Log 4 put the element decision here.

This wave decides the CSS tier's element model once, for the body, the ramp,
the second scale and the lift, and lands as much of it as Chromium measures
true — with the GPU tier not moving by a byte.

## Parent-Level Acceptance

- **The CSS tier's body is the two-component law, measured, not projected.**
  On W11's probe bed (native 1x, pitches 8 / 16 / 32 / 64, level and
  transmission free per span) the tier's RMS against the reference is within
  1.5× the GPU law's at every span (§5.42 §5's column: 0.0138–0.0281), where
  today's mixed σ reads 0.038–0.078; and W13's depth-window instrument, run on
  the tier's own captures, recovers the renderer's k(u) within ±0.05 in every
  window over 4 ≤ u ≤ span/2 − 4 on `rrect-md` and `rrect-lg` at 1x, with the
  instrument's recovery of a known law beside every reading (X4).
- **The dom checkerboard rows move the way the mechanism says.** The
  interior's spread (`interiorStdDev`) is within 0.01 of native at every 1x
  calibration span and within 0.015 at 2x (the statistic's whole-silhouette
  limit, W15 Surprises); the checkerboard interior means recover the level
  W11c's mixed σ cost them (`rrect-lg` dom 0.6323 → ≥ 0.6440 against the
  reference's 0.7066); the `hc-text` dom rows recover their pre-W11c reading
  (the capsule 0.9739 → ≥ 0.9799, `rrect-md` 0.9072 → ≥ 0.9295 at 1x);
  and each of the eight dom `ssimMean` floors held since W11c comes off by
  fix or is re-held with its mechanism named — and the only mechanism this
  wave may name is the rim band (§5.38 §2), which no CSS form carries.
- **The CSS tier's second scale is the reference's, decided on measurement.**
  The tier's widths are device-pixel quantities through the live ratio and its
  heavy share the GPU tier's own; the tier's single-σ equivalent per span at
  2x lands within 0.8 CSS px of the reference's ceiling (§5.69 §4's fourth
  column: 2.91 / 2.82 / 3.64 / 4.19 / 5.01); the four 2x dom rows rise;
  `CSS_TIER_RAMP_SCALE` is retired or its successor decided by the user with
  the measurement beside it.
- **The lift is painted on the CSS tier or decided against with the number.**
  Painted: `photo__rrect-md`'s dom occlusion residual closes to within 0.005 of
  the reference and the thick solids' bands read within 0.01 of the GPU
  tier's. Decided against: G0's measurement of what Chromium can add, with
  its RMS, in the Decision Log.
- **The GPU tier does not move.** Every GPU-tier capture at every profile and
  scale is byte-identical to the W15 bed, and every GPU row reproduces within
  0.0002; `tier-coherence` pins the two layers' σ and share to the renderer's
  law over dpr {1, 1.5, 2, 3}; the accessibility folds (reduced transparency,
  increased contrast) apply on both tiers to the same composed mix, and their
  dom rows stay within bound, any move named.
- **The cost is measured, budgeted and met.** G0 measures the tier's
  per-surface frame cost at one blur, two blurs, and two blurs with a mask, on
  a synthetic page and on the demo's densest CSS-tier page at 1x and 2x; the
  user sets the budget in the Decision Log before the landing; the landing
  meets it.
- **Chromium is measured; the other engines are decided honestly.** The form
  is captured and refereed on Chromium (the only engine any automatable path
  can measure `backdrop-filter` on); a self-scoring section is added to S1's
  manual page for `opacity` and `mask-image` on a `backdrop-filter` layer, the
  conformance table gains the rows the form depends on and fails closed until
  the user's labeled pass, and what the tier draws on an unverified engine is
  the user's decision (Decision Log 1 q2).
- **By eye:** the X5 sheets — the CSS tier beside the native fixture and
  beside the GPU tier, at 1x and 2x — at the dry run and the landing, sent to
  the user; their reading recorded; the landing is theirs to call.
- **The host stays the author's element.** Its in-flow content paints above
  the material as today; no created layer is focusable, hit-testable or
  announced; the plane sandwich's four-layer array, the hit-test map and the
  one-focusable-per-surface rule are unchanged; the tier still builds no
  proxy, so `probe-failed` still demotes to it.
- All package suites green, lint clean; the platform-web e2e pins that name
  the host's filter (`proxies`, `probe`, `webgpu-tier`, `css-tier-pixels`)
  re-recorded only with the reason; the canonical matrix
  rebuilt once at recomposition; the holdout read once per frozen
  configuration; every gap left in claims, this Deferred list, or the tracker.

## Grounding Baseline (the W15 bed, 2026-09-04, `c00f89e`)

CSS (`dom`) tier, light standard, checkerboard; `ssimMean` against its bound
or floor, the interior's spread (`interiorStdDev`) and level (`interiorMean`)
web against native, the GPU tier's `ssimMean` on the same fixture:

| cell | span | set | dpr | `ssimMean` | bound / floor | std web / native | mean web / native | GPU |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | 32 | calibration | 1 | 0.9855 | ≥ 0.90 | 0.1472 / 0.1549 | 0.6117 / 0.6285 | 0.9990 |
| `capsule-button` | 44 | calibration | 1 | 0.9619 | ≥ 0.90 | 0.1250 / 0.1424 | 0.6075 / 0.6207 | 0.9856 |
| `rrect-md` | 96 | calibration | 1 | 0.8963 | floor 0.8952 | 0.0767 / 0.1131 | 0.6352 / 0.6829 | 0.9862 |
| `rrect-ml` | 128 | calibration | 1 | 0.8515 | floor 0.847 | 0.0591 / 0.0865 | 0.6335 / 0.6936 | 0.9797 |
| `toolbar-group` | 44 × 3 | calibration | 1 | 0.9584 | ≥ 0.90 | 0.1332 / 0.1481 | 0.6029 / 0.6210 | 0.9642 |
| `glass-over-glass` | 130 / 56 | holdout | 1 | 0.8516 | floor 0.8489 | 0.1279 / 0.1321 | 0.6699 / 0.7231 | 0.9823 |
| `rrect-lg` | 160 | holdout | 1 | 0.8448 | floor 0.8361 | 0.0375 / 0.0650 | 0.6323 / 0.7066 | 0.9743 |
| `rrect-sm` | 32 | calibration | 2 | 0.9880 | ≥ 0.92 | 0.1462 / 0.1636 | 0.6116 / 0.6285 | 0.9988 |
| `capsule-button` | 44 | calibration | 2 | 0.9708 | ≥ 0.92 | 0.1291 / 0.1552 | 0.6147 / 0.6226 | 0.9860 |
| `rrect-md` | 96 | calibration | 2 | 0.9174 | floor 0.9159 | 0.0771 / 0.1272 | 0.6420 / 0.6832 | 0.9903 |
| `rrect-ml` | 128 | calibration | 2 | 0.8808 | floor 0.8754 | 0.0593 / 0.1018 | 0.6404 / 0.6929 | 0.9860 |
| `toolbar-group` | 44 × 3 | calibration | 2 | 0.9656 | ≥ 0.92 | 0.1321 / 0.1581 | 0.6099 / 0.6246 | 0.9666 |
| `glass-over-glass` | 130 / 56 | holdout | 2 | 0.8709 | floor 0.8677 | 0.1267 / 0.1401 | 0.6756 / 0.7223 | 0.9843 |
| `rrect-lg` | 160 | holdout | 2 | 0.8760 | floor 0.8686 | 0.0377 / 0.0810 | 0.6393 / 0.7052 | 0.9762 |

The tier's interior spread is 32–54% under the reference on the four large
spans at 1x and 39–63% at 2x — the single blur flattening what the reference
keeps — and 5–12% under on the thin ones. The spread's shortfall is the
whole of the tier's checkerboard deficit after the rim band: the GPU tier,
which carries the two components, reads 0.09–0.13 above it on the same four
cells. The `hc-text` dom rows at 1x: the capsule 0.9739 (0.9799 before W11c
G1), `rrect-md` 0.9072 (0.9295 before), the tinted capsule unchanged; at 2x
`rrect-md` 0.9405 (0.9332 before). The checkerboard interior means fell
0.010–0.012 at W11c G1 on every span (`rrect-lg` 0.6440 → 0.6323 at 1x
against the reference's 0.7066) and have not recovered. The cross-tier ΔE on
the dom checkerboard cells reads 0.023 / 0.037 / 0.043 / 0.035 on
`rrect-md` / `-ml` / `-lg` / `glass-over-glass` at 1x against the coherence
bound of ≤ 0.05. The eight floors are exactly the eight `dom` rows above with
a floor in the fifth column; `UNMET_ROWS` is 8 and every one of them is this
tier's. The dark-standard dom rows (13 per scale) meet their bounds and are
not this wave's subject; they are read at the dry run like every other row.

**What the tier draws today, and with what.** No element is created: every
declaration lands on the author's host (`css-tier.ts`, `cssTierDeclarations`
applied by `root.ts`) — `backdrop-filter: blur(σ) saturate(…)`, the tint as
`background-color`, the press glow as `background-image`, the rim as
`border`, the outer shadow as `box-shadow`, `border-radius` as the only mask,
and the tokens. The σ is `sizeScatterSigmaAt` at the ramp's area mean
(`scatterThickness`) at `CSS_TIER_RAMP_SCALE = 1`; the tier has no
device-scale input. The tier builds no proxy on any path, and `proxies.spec`
pins that as the doctrine's test. The plane sandwich's four-layer array, the
hit-test map's "no `layer:` entries" and one focusable element per surface
are pinned by `registration.spec`, `hit-testing.spec` and `focus.spec`.

## Design (advisory unless marked)

- **[binding] Two tiers, one profile (K5).** Every quantity the CSS tier
  draws — the two σ, the heavy share at the contour and at depth, the reach,
  the lift's amplitude and falloff — derives from the material profile
  through `packages/platform-web/src/optics.ts`, the same document the
  renderer reads, and no constant is fitted for this tier alone. Where the
  tier cannot draw a term exactly (a mask's shape, a lift's blend), the
  conversion is a derivation from the profile's own numbers with its residual
  measured and recorded, as W14's `α′ = α − L/B` was.
- **[binding] The GPU tier does not move.** This wave changes
  `packages/platform-web` (the CSS tier, its optics mirror, its DOM) and the
  calibration harness's CSS-tier rows; the renderer's material, passes and
  goldens are untouched and verified byte-identical at the dry run and the
  landing.
- **[binding] The element model is decided once**, for the body's two layers,
  the ramp's mask, the second scale and the lift together (W14 Decision Log
  4's condition). The host stays the author's element and its content the top
  of the stack; the tier's created layers are its own, carry no semantics
  (`aria-hidden`, `pointer-events: none`), and are torn down with the group.
- **[binding] The reference arbitrates the ends; the form decides the
  means.** No acceptance term names a σ, a share or a mask shape.
- **[binding] Chromium is the measured engine.** Every number in this wave is
  a Chromium capture; the other engines enter through the conformance table
  and the user's labeled pass, never through an assumption.
- **[binding] X8 — the holdout is read once** per frozen configuration, at
  the dry run; the landing reproduces it.
- Advisory — **the element model**: the tier creates elements for the
  first time. The host loses its in-place filter and gains created children
  that paint **above the host's own background and border and below its
  in-flow content** — which, since positioned children otherwise paint above
  in-flow text, means negative `z-index` children under a host that
  establishes a stacking context (`isolation: isolate` is not a backdrop-root
  trigger, S1's own finding), each `position: absolute` over the border box
  with the host's radius, `pointer-events: none`, `aria-hidden`: (1) the
  **sharp layer**, `backdrop-filter: blur(σ_s)`; (2) the **heavy layer**,
  `backdrop-filter: blur(σ_b·√(gain² − 1))` drawn after it so that it blurs
  the sharp layer's output and composes to σ_b·gain, with the heavy share as
  `opacity` where the ramp is flat and as a `mask-image` where it is not.
  The nested-child result of §5.42 §5 is the reason the host itself cannot
  keep the sharp filter: a filtered parent makes a filtered child inert, so
  both layers must be children of a filter-free host. The tint may stay on
  the host beneath the layers, because a blur of a uniform shade over the
  backdrop is the shade over the blurred backdrop (both operations are
  linear in the backdrop) — except within a kernel's width of the contour,
  where the blur samples outside the host and the engine's edge mode decides;
  G0 measures that ring before the tint's place is chosen. The border, the
  press glow, the shadow and the tokens are redistributed by G0's list, one
  line per property, with the rule that no created layer is focusable,
  hit-testable or announced and the tier still builds no proxy. The doctrine
  `css-tier.ts` states narrows from "in place, nothing layered" to "no
  proxy": the filter still reads what is behind the host, which is why
  `probe-failed` may still demote here.
- Advisory — **the mask**: the ramp's k(u) is linear in the depth u from the
  contour to the reach U (device px), from `1 − s₀(span)` to `kDeep(span)`.
  Three candidate carriers, measured by G0 against the shader's k(u): (a) a
  stack of gradients (`linear-gradient` per side, `radial-gradient` per
  corner) composited — approximate at the corners because `mask-composite`
  multiplies alphas where the distance field takes a minimum; (b) an SVG
  mask of the inset rounded rect blurred — an erf profile, exact corners;
  (c) a raster mask the tier draws itself into a small canvas at device
  resolution from the exact k(u) and sets as `mask-image` — exact profile
  and corners, one raster per size change. The first thing G0 measures is
  whether `mask-image` composes with `backdrop-filter` and `opacity` on one
  element in Chromium at all; every carrier depends on it.
- Advisory — **the second scale**: `σ_s = blurSigma / dpr` and the heavy
  width from `scatterDeepThickness(span, profile, dpr)` divided by dpr, the
  share from the renderer's own `kDeep` and ramp at the live ratio — the
  renderer's functions in `material.ts` mirrored in `optics.ts` as the
  `MATERIAL_SOURCE_SIZE` block already is; the ratio observed through the
  `observeDevicePixelRatio` plumbing W13 Decision Log 5 (b) named. Between 1x
  and 2x the terms interpolate as the renderer's do.
- Advisory — **the lift**: a fourth element outside the contour — the host's
  box grown by the shadow's reach, `backdrop-filter: blur(σ_L)`, masked to the
  falloff ring outside the silhouette, composited with `mix-blend-mode:
  plus-lighter` at the profile's amplitude — is the direct reading of "the
  backdrop's own blurred light on one falloff". G0 measures its RMS against
  the GPU tier's lift on `photo__rrect-md` and the thick solids, and its cost;
  if the ring cannot be drawn without re-rooting the backdrop, the tier keeps
  the derived alpha and the residual stays named.
- Advisory — **the accessibility folds** apply once on the composed mix: the
  reduced-transparency occlusion floor lifts the tint's alpha exactly as
  today, and the two blur layers are unchanged by it; increased contrast the
  same. The dom rows in `DOM_TIER_REDUCED_TRANSPARENCY` and
  `DOM_TIER_INCREASED_CONTRAST` are read at the dry run and any move named.
- Advisory — **cost**: a `backdrop-filter` blur is a render-surface readback
  and a two-pass Gaussian per layer; two per surface doubles it, a mask adds a
  surface. `contain: paint` on the host and `will-change` off by default are
  the first things to measure against; a per-group cap (the heavy layer
  collapsed into a single mixed σ above N surfaces) is a fallback the budget
  may ask for, and would be a declared, measured degradation rather than a
  silent one.
- Advisory — **the sheets**: X5's script relabelled for three columns —
  native, CSS tier, GPU tier — so the eye reads the tier against both.

## Children

### G0: Chromium's answers, with their instruments — spike (deliverable: findings)

- **Purpose:** on a probe page under the calibration harness's own Chromium
  (real GPU, `channel: "chromium"`): (a) the two-layer body as negative-`z-index`
  children of a filter-free host with the host's radius on, against W11's
  probe bed (`scenes-w9-probe.json`'s pitches through `probe-score.ts`) —
  the RMS per span beside §5.42 §5's columns — and the contour ring with the
  tint on the host beneath the layers against the tint above them; (b) `mask-image` with
  `backdrop-filter` and `opacity` on one element — does it compose, and if so
  the three mask carriers' k(u) against the shader's, measured by W13's
  depth-window instrument on the probe captures; (c) the second scale
  predicted — the tier's two layers at device-pixel widths through dpr 2, its
  single-σ equivalent per span beside §5.69 §4's four columns; (d) the lift
  as an outer ring with `plus-lighter` — feasible, its RMS against the GPU
  tier's lift on `photo__rrect-md` and the thick solids; (e) the cost — frame
  time per surface at one blur, two, and two with a mask, on a synthetic
  20-surface page and on the demo's densest CSS-tier page, 1x and 2x; (f)
  the redistribution list — what the host carries in place today and where
  each goes; (g) the manual-page section for the other engines, added to
  `spikes/s1-proxy-topology/pages/manual-check.html` as section H
  (self-scoring: sibling `opacity`, `mask-image` on a filtered layer,
  `plus-lighter` on a filtered ring), with the conformance-table fields it
  would move named.
- **Acceptance:** every reading carries the instrument's recovery of a known
  law beside it (X4); the mask question answered yes or no with the capture;
  a cost table the user can set a budget from; findings in
  `packages/calibration/results/2026-09-04-w16-css-two-layer/g0/`; the
  claims section written; the manual-page section landed on its own (it
  moves no material).
- **Edges:** none. **Track:** spike; one worker, findings not the spec.

### G1: The declared form and its dry run — controlled

- **Purpose:** the element model and the mask carrier chosen on G0's
  measurements, implemented on a branch in `packages/platform-web` (the
  tier's DOM, `optics.ts`'s derivations, the dpr plumbing, the folds), the
  calibration harness's CSS-tier capture unchanged in kind; the twelve runs
  to a scratch matrix; the dom rows predicted from the runs; the stops
  refereed; the sheets at 1x and 2x; the holdout read once (X8). No sweep:
  the tier has no free constant, and a row the derivation cannot reach is a
  finding with its mechanism, not a fit.
- **Acceptance:** the declaration in claims — the model, the derivations,
  the stops with numbers, the rows' predictions — before any landing capture;
  the sheets sent; the user's reading recorded; Decision Log 1's questions
  answered on G0's and G1's evidence.
- **Edges:** blocked-by G0. **Track:** controlled.

### G2: The landing and its referee — controlled

- **Purpose:** merge; `tier-coherence` extended to pin the two layers over
  dpr (its area-mean projection sweep retired with its reason, the exact σ
  and frost pins given a per-layer rule, W14's lift-fold pin kept or retired
  as the lift decides); `css-tier.test.ts` re-shaped for a declaration per
  layer; the platform-web e2e pins that read the host's `backdropFilter`
  re-pointed at the sharp layer with the reason; the
  conformance rows added, failing closed; the canonical rebuild once; the
  eight floors off by fix or re-held with the mechanism; the sheets at the
  landing; the user's eye; recomposition.
- **Stops (declared here, refined by G1 with numbers):** (S1) every GPU-tier
  capture at every profile byte-identical to the W15 bed and every GPU row
  within 0.0002; (S2) no dom row below its adopted bound or its floor, and
  none of the eight held checkerboard `ssimMean` rows below the W15
  bed's (`rrect-md` 0.8963 / 0.9174, `-ml` 0.8515 / 0.8808, `glass-over-glass`
  0.8516 / 0.8709, `rrect-lg` 0.8448 / 0.8760 at 1x / 2x);
  (S3) `interiorStdDev` on the dom checkerboard cells within 0.01 of native at
  1x and 0.015 at 2x on the calibration spans; (S4) the dom checkerboard
  interior means at 1x at or above their pre-W11c-G1 level (`rrect-md` 0.6451,
  `-ml` 0.6444, `-lg` 0.6440, `glass-over-glass` 0.6818, the thin spans within
  0.002 of theirs) and the `hc-text` dom rows at or above theirs (the capsule
  0.9799, `rrect-md` 0.9295 at 1x); (S5) the solids, `photo` and the tinted dom cells
  within 0.002 in every adopted metric except where G1 predicted the move
  (the lift's cells); (S6) `tier-coherence` does not loosen and the cross-tier
  ΔE on the fitted sets does not rise; (S7) the cost within the budget the
  user set; (S8) a hard stop is a landing the user's eye rejects.
- **Edges:** blocked-by G1. **Track:** controlled; the landing is the user's
  call (Decision Log).

## Cross-Child Contracts

- **X1 — the canonical rebuild.** As W15 X1: `rm results/matrix.json`, the
  twelve runs, the demo fixture re-copied. Owner: parent.
- **X2 — floor bookkeeping.** The eight dom `ssimMean` floors come off by fix
  or stay with the mechanism named; `UNMET_ROWS` follows. Owner: parent.
- **X3 — the untouched tier.** The whole-bed scan against the W15 bed; on the
  GPU tier byte identity, not a tolerance. Owner: parent.
- **X4 — the instrument's validation travels with every reading.** W13's
  depth-window instrument recovers a known two-layer law from a Chromium
  capture before it reads the tier. Owner: G0; G1 binds.
- **X5 — the by-eye sheets.** W15's script with a third column, at 1x and 2x,
  at the dry run and the landing, under
  `results/2026-09-04-w16-css-two-layer/sheets/`. Owner: parent.
- **X6 — the band-windowed rows** (`ssimBand`, `ssimInterior`,
  `ssimOutside`) read on the dom cells beside `ssimMean`. Owner: parent.
- **X7 — the coherence pin.** `tier-coherence.test.ts` asserts the tier's two
  σ and its share per span against the renderer's functions over dpr
  {1, 1.5, 2, 3}, and the folds on both tiers. Owner: G2.
- **X8 — the holdout, read once** per frozen configuration. Owner: G1; parent
  verifies.
- **X9 — the engines.** Section H on the manual page and the conformance
  rows it moves; fail closed until the user's labeled pass. Owner: G0 writes,
  G2 wires.

## Ordering & Dependency Map

G0 → G1 → G2 → recomposition. Nothing lands before G2's referee; the manual
page's section H (X9) lands from G0 on its own, since it moves no material.

## Risks & Mitigations

- **`mask-image` does not compose with `backdrop-filter` in Chromium** (or
  composes only with `opacity` absent). Mitigation: it is G0's first
  measurement; without it the ramp is carried as one `opacity` at the
  projection of k(u) onto the surface — the body's two components without
  the band — and the band stays the tier's named gap.
- **Two blurs per surface cost more than the tier may spend.** Mitigation:
  G0 measures before anything is built; the budget is the user's; a declared
  per-group collapse is the fallback, never a silent one.
- **The host's in-place doctrine carried invariants** (the probe-demotion
  path, hit-testing, the semantic host's own styles, `overflow` and radius on
  the created layers). Mitigation: G0's redistribution list, one line per
  property; the platform-web e2e pins name each DOM change.
- **The other engines.** Sibling `opacity` on `backdrop-filter` is ordinary
  CSS; `mask-image` and `plus-lighter` on a filtered layer are not verified
  anywhere but Chromium, and no automatable path can measure them.
  Mitigation: X9, fail closed; Decision Log 1 q2.
- **The `hc-text` and reduced-transparency rows move the wrong way** (the
  sharp layer restores the checker's contrast on text too). Mitigation: S4
  and the folds' rows read at the dry run; the reference's own numbers are
  the arbiter.
- **The created layers' filters die under the host's rounded clip.**
  Chromium ≥ 152 drops `backdrop-filter` under `clip-path: path()` beneath a
  rounded clipping ancestor (`engine-defects.ts`); `mask-image` and
  `border-radius` were not in that matrix. Mitigation: G0 (a) is captured
  under the harness's real Chromium with the host's radius on, and the
  probe's first cell is the plainest one.
- **Two filtered elements each under the software-raster area limit cost
  something jointly** (headless Chromium drops the filter between 1.75 and
  3.0 Mpx; two elements is unrecorded). Mitigation: G0 (e) measures at the
  demo's largest surface at 2x as well as at count.
- **The lift re-roots the backdrop** (`mix-blend-mode` is a backdrop-root
  trigger). Mitigation: G0 measures the ring on the probe with a sampling
  group beneath it; if it re-roots, the lift stays deferred with the number.

## Deferred / Out of Scope

- **The rim band on the CSS tier** — the lens, the two-light rim, the corner
  lobes: no CSS form carries a displacement field, and the dom rows' deficit
  after the body is exactly this (§5.38 §2). Stays the tier's own documented
  gap; any floor this wave re-holds names it.
- The thin material's scale-dependent level (§5.55 §3), the dark-ground
  transmission (the dot), the 2x gain's top above span 160, the thin spans'
  2x spread, the whole-silhouette interior statistic — W15's Deferred,
  unchanged.
- The CSS tier's frame timing on one solid cell (W15 Deferred) — read again
  at the rebuild; if it recurs, the harness's, not the tier's.
- **The CSS tier's lift (from W14 Decision Log 4; decided against here, Decision Log 2
  (d)).** No CSS construction adds a filtered backdrop's light to a ring and keeps the
  backdrop (§5.71 §6). The tier's ring error on a structured backdrop is the derived alpha's
  over-correction — `photo__rrect-md` 0.0112 lighter than native where the GPU tier is 0.0059
  darker — and is W14's conversion's own item, not a missing addition.
- The software rasteriser's joint area limit for two filtered elements (headless Chromium
  drops one filter between 1.75 and 3.0 Mpx; two elements unmeasured, and this wave's
  captures are forbidden the software path) — a probe on the fallback adapter, its own item.
- The reference filter's cost, the accessibility folds on the two layers, and the
  `interiorStdDev` statistic at 2x — G0's addendum and G1's dry run, respectively.

## Tracking Map

| child | where | status |
| --- | --- | --- |
| G0 | `packages/calibration/results/2026-09-04-w16-css-two-layer/g0/g0-two-layer.md`, claims §5.71; section H on `spikes/s1-proxy-topology/pages/manual-check.html` (X9) | CLOSED 2026-09-04 — `mask-image` composes; the two `blur()` layers halve the residual and are floored by the encoded space; a linear-light reference filter meets the acceptance and is Chromium-only; the lift's advisory form does not exist; the cost budget measured, and re-measured for the linear-light form in the findings' §5.1 and claims §5.71 §7.1 — the knee does not move |
| G1 | branch `w16-g1-two-layer`, one worker (Decision Log 2 (a)–(d); the forks of q0–q2 behind conformance rows and one constant) | OPENED 2026-09-04 |
| G2 | — | blocked-by G1 |

## Decision Log

### Decision Log 1 — the cut, the binding rules, and what the user decides (2026-09-04)

**The cut.** Three gates, as W13–W15 ran: a spike that measures what Chromium
can draw before anything is built, a declared form with a dry run, a landing
with its referee. One difference from the body waves: the tier has no free
constant (K5), so G1 has no sweep — its declaration is a set of derivations
from the profile, and a row the derivation cannot reach is a mechanism to
name, not a number to fit.

**The binding rules** are the Design's: one profile, the GPU tier untouched,
the element model decided once, the reference arbitrating the ends, Chromium
the measured engine, the holdout once.

**What the user decides, on the evidence the gates produce:**

1. *The cost budget* (G0 (e)) — what a CSS-tier surface may cost at two blurs
   and a mask, and whether a per-group collapse is wanted as a fallback.
   The parent's recommendation waits for the numbers.
2. *The unverified-engine policy* (X9) — on an engine whose conformance rows
   for `mask-image` on a filtered layer are `"unverified"`, does the tier
   draw the two-layer body with the ramp collapsed to one `opacity` (the
   body's two components, no band), or the single-blur form it draws today?
   **Recommended: the two layers with one `opacity`** — sibling `opacity` on
   `backdrop-filter` is ordinary CSS on every engine, the failure mode is a
   flat mix rather than a broken surface, and the band is the only thing the
   pass unlocks.
3. *The lift* (G0 (d)) — in this wave as G1's fourth element if G0 measures
   it feasible and cheap, or its own follow-up. **Recommended: in this wave
   if feasible** — W14 Decision Log 4 asked for the layering decision to be
   made once, and the element model is being decided here.
4. *The landing* — the user's eye, as every wave.

### Decision Log 2 — G0 read: the element model bound, the raster mask, the second scale as a derivation, the lift decided against, and the linear-light form put to the user (2026-09-04)

**Evidence** (claims §5.71; `results/2026-09-04-w16-css-two-layer/g0/g0-two-layer.md`).
`mask-image` composes with `backdrop-filter` and `opacity` on one element in Chromium (a
uniform mask is bit-identical to the same `opacity`; a mask on a wrapper makes the child's
filter inert). Two `blur()` layers reproduce the law they are given to RMS 0.0024–0.0049
against their own forward model and still read 2.4–2.8× the GPU law's residual on the thick
spans, because `blur()` operates on the page's encoded values and the same law blurred in
the encoded space reads exactly that; the acceptance's 1.5× is unreachable with `blur()` at
any σ, share or mask. `backdrop-filter: url(#f)` with an SVG `feGaussianBlur` at
`color-interpolation-filters="linearRGB"` blurs in linear light and reads 1.17 / 1.10 / 1.50 /
1.41 / 1.20× of the GPU law at 1x and 0.97–1.03× at 2x; its sRGB sibling is bit-for-bit the
`blur()` form, which is the control; only Chromium renders a reference filter inside
`backdrop-filter` (`referenceFilterInBackdrop`, true on the Chromium rows alone). The tint
beneath the layers is blurred by them and darkens a 4 CSS px ring by 0.010–0.015; above them
it is exact. Of the three mask carriers only the raster is inside ±0.05 of the shader's k(u)
through W13's instrument (mean 0.0010, max 0.0020 against the mask channel's own 8 bits);
the gradient stack's corners read 0.06–0.19 and the blurred SVG inset up to 0.12. Two
layers at device-pixel widths land 0.38–1.07 CSS px *narrow* of §5.69 §4's fourth column,
and the capture agrees with the arithmetic to 0.3 px — a true Gaussian at the renderer's
nominal 2x heavy width (3.0–4.1 CSS px) is narrower than the reference's (3.75–5.5). A blend
mode does not reach a `backdrop-filter`'s output (`plus-lighter`, `screen` and `normal` on
a filtered ring render identically) and a blending ancestor is a backdrop root, so the
advisory lift form does not exist; and on `photo__rrect-md` the CSS tier is already 0.0112
lighter than the native over the shadow ring where the GPU tier is 0.0059 darker. One
`backdrop-filter` per surface never leaves the display cadence; two leave it from 32
surfaces of 160 × 96 (0.49–0.61 M filtered device px per frame at 1x) and saturate near
27 ms from 80; the mask is free; the demo's densest CSS-tier page (`/playground/`, eight
elements, 0.16 M device px at 2x) is at the cadence in every form. Contract X4 held
throughout: the scoring reproduced §5.42 §5's five published numbers to four decimals before
any new reading, and W13's instrument recovered a known ramp and a known flat share from
Chromium pages at 0.008–0.020.

**Decided (the parent), binding for G1:**

- **(a) The element model is G0's §6 list.** The host keeps `position: relative`,
  `isolation: isolate`, `border-radius`, its `border-width` for layout with the colour made
  transparent, the outer `box-shadow` and the five tokens. Three created children, each
  `position: absolute` at `inset: calc(-1 * border-width)` so its border box is the host's,
  `border-radius: inherit`, `pointer-events: none`, `aria-hidden`, painting above the host's
  background and below its in-flow content: **L1** the sharp filter; **L2** the heavy filter
  with the ramp as a raster `mask-image` drawn from the exact k(u) at device resolution;
  **L3** the tint, the press glow and the rim as an inset `box-shadow`. The tint sits above
  both filters (§5.71 §3). The joint-view reason: the paint order, the mask's placement and
  the tint's ring were each measured, and the charter binds the model to be decided once.
- **(b) The ramp's carrier is the raster mask.** The gradient stack and the blurred SVG
  inset are retired with their numbers (§5.71 §4).
- **(c) The second scale is a derivation, not the nominal.** The tier draws the renderer's
  kernel's *effective* Gaussian width — the moment-matched σ of what the mip chain draws at
  the profile's nominal, measured on the renderer's own captures at both scales — through the
  same functions the renderer uses for everything else. §5.69 §3 already read the renderer's
  nominal 6 device px as 8–11 to a Gaussian estimator, and §5.71 §5 shows a true Gaussian at
  the nominal landing narrow on every span by the size of that difference. G1 measures the
  conversion, records its residual and carries no fitted constant (K5); a span the derivation
  cannot bring within the acceptance's 0.8 CSS px is re-held with the mechanism named — the
  GPU law's own 2x distance from the reference, which W15's Deferred owns.
- **(d) The lift is decided against for this wave, on measurement.** CSS has no construction
  that adds a filtered backdrop's light to a ring and keeps the backdrop (§5.71 §6), and the
  number it would buy is smaller and of the wrong sign on the one bed cell that has a lift.
  The residual is re-attributed: the CSS tier's ring error on a structured backdrop is the
  derived alpha's over-correction, W14's own, and goes to Deferred with the number and to
  W14's Revision Notes as a correction beside its claim. Decision Log 1 q3 is answered by
  the measurement rather than by a preference; the user may overrule it.
- **(e) The charter's first Risk is closed** (`mask-image` composes; the raster mask is free
  and exact), and its Purpose item 2 and its advisory lift form are corrected by (c) and (d).

**Put to the user, with the parent's recommendation** (the answers set defaults; G1 builds
every fork behind a conformance row or one constant so that no answer reopens the build):

0. *The linear-light body* (new). On an engine whose conformance row says it renders a
   reference filter inside `backdrop-filter` — Chromium today — the two layers blur through
   an SVG `feGaussianBlur` at `linearRGB` (one `<svg>` of definitions per root, one
   `<filter>` per distinct σ, created by the tier); elsewhere `blur()`. It is the only
   measured form that meets the body's acceptance; it turns `referenceFilterInBackdrop` from
   a reserved seam into a fidelity dependency; its cost is a G0 addendum in progress.
   **Recommended: yes.**
1. *The cost budget* (Decision Log 1 q1). An area rule rather than a count: the two-layer
   form while a root's total filtered surface area is under **0.4 M device px per frame**,
   the heavy layer collapsing into today's single mixed σ above it — declared, measured and
   named in the resolved state, never silent. Two blurs leave the cadence from 0.49 M on
   this machine; every page the demo ships clears 0.4 M by 2.5×. **Recommended: adopt**, the
   threshold re-read once the reference filter's cost is in.
2. *Unverified engines* (q2). Two layers with the heavy share as one `opacity`; the raster
   mask and the reference filter each gated on their own conformance row, fail closed.
   **Recommended: unchanged.**
3. *The lift* (q3): (d) above.
4. *The landing* (q4): the user's eye at the dry run and the landing.

**G1 opens** on (a)–(d), on a branch, with 0–2 built as switchable defaults.

## Surprises & Discoveries

- **2026-09-04 (G0) — the tier's body is floored by the colour space, not by its form.**
  `backdrop-filter: blur()` is an operator on the page's ENCODED values and the reference's body is
  linear in luminance. The two-layer form reproduces the law it is given to RMS 0.0024–0.0049
  against its own forward model, and still reads 2.4–2.8× the GPU law's residual on the thick spans,
  because the same law blurred in the encoded space reads exactly that (claims §5.71 §2). No σ,
  share or mask can move it. This was not in the charter's Consumes, its Design or its Risks: every
  one of them treats `blur()` and the law as interchangeable, and §5.42 §5's "RMS 0.0011" was a
  measurement of the MIX, in encoded luma, not of the composed body against the reference.
- **2026-09-04 (G0) — there is a linear-light form, and it is Chromium-only.**
  `backdrop-filter: url(#f)` with `color-interpolation-filters="linearRGB"` blurs in linear light and
  is the only measured form that meets the parent-level acceptance (1.10–1.50× of the GPU law at 1x,
  0.97–1.03× at 2x). Its `sRGB` sibling is bit-for-bit the `blur()` form, which is the control. The
  conformance table's existing `referenceFilterInBackdrop` field — until now the "reserved
  displacement seam" of Decision Log #11 — becomes a **fidelity dependency** if G1 takes it.
- **2026-09-04 (G0) — a blend mode does not reach a `backdrop-filter`'s output.**
  `plus-lighter`, `screen` and `normal` on a filtered ring render identically, to 0.4/255: the blend
  blends the element's own content, which an empty ring has none of. Putting the blend on a parent
  makes the child's filter inert, because a `mix-blend-mode` ancestor is a backdrop root. The
  charter's advisory lift form is therefore not buildable at all, which is one step earlier than the
  Risk it anticipated ("the lift re-roots the backdrop") — that Risk does not fire for a sibling
  (byte-identical body beneath) and fires absolutely for an ancestor.
- **2026-09-04 (G0) — a masked ANCESTOR kills a descendant's `backdrop-filter`, while a mask on the
  filtered element itself composes exactly.** Ten carrier spellings on the element compose, one on a
  wrapper does not. `engine-defects.ts` records Chromium ≥ 152 dropping `backdrop-filter` under
  `clip-path: path()` beneath a rounded clipping ancestor; this is the neighbouring fact, it is
  normative rather than a defect, and it constrains the element model (the mask cannot be hoisted).
- **2026-09-04 (G0) — the lift is not the CSS tier's largest ring error on the bed as it stands.**
  On `photo__rrect-md__rest` the CSS tier is 0.0112 encoded LIGHTER than the native over the shadow
  ring while the GPU tier is 0.0059 DARKER, so W14's derived alpha over-corrects on that cell and
  added light would move it the wrong way (claims §5.71 §6).
- **2026-09-04 (G0) — an uncapped `requestAnimationFrame` interval measures nothing about a
  `backdrop-filter`.** Every configuration from no filter to two filters and a mask, 0–320 surfaces,
  read 0.1–0.3 ms with `--disable-gpu-vsync --disable-frame-rate-limit`: the rasterisation is the
  compositor's and the main thread is idle. The cost table is a vsync-on saturation sweep instead.

## Outcomes & Retrospective

(open)

## Revision Notes

- 2026-09-04: chartered from W11's Deferred entry, W13's and W14's deferrals and W15's
  Decision Log 3, on the user's pick; G0 opened.
- 2026-09-04: G0 closed. Findings in
  `packages/calibration/results/2026-09-04-w16-css-two-layer/g0/g0-two-layer.md`, claims §5.71,
  section H landed on S1's manual page (X9's first half). Three of the charter's advisory or
  predictive statements are contradicted by measurement and are written up in the findings' §8 and
  claims §5.71 §8 for the parent rather than edited into the binding content here: the body's
  acceptance is unreachable with `blur()`, the second scale lands narrow rather than on, and the
  lift's advisory form does not exist. Decision Log 1's three open questions each have a
  measurement and a recommendation in the findings; none is answered here.
- 2026-09-04: G0 addendum, on the parent's request, because the budget has to be set on the cost of
  the form that actually reaches the reference. The vsync-on saturation sweep re-run with both
  layers as `url(#f)` / `linearRGB` reference filters, with and without the raster mask, at both
  scales and over the three demo pages: **the knee does not move** — one reference filter is as free
  as one `blur()` at every count measured, two leave the cadence between 32 and 36 surfaces exactly
  as two `blur()` layers do, and the two forms separate only past the knee at dpr 2. The area rule
  the findings recommend for Decision Log 1 q1 stands unchanged, and is restated on filtered area
  per layer rather than on a surface count or a form. Numbers appended beside §7's, nothing
  rewritten (findings §5.1, claims §5.71 §7.1).
- 2026-09-04: G0 CLOSED (claims §5.71) — `mask-image` composes; two `blur()` layers are floored by
  the encoded space; the linear-light reference filter meets the acceptance on Chromium; the raster
  mask is exact and free; the second scale lands narrow at the nominal widths; the lift's form does
  not exist. Decision Log 2: the element model bound, the raster carrier, the second scale as a
  derivation of the renderer's effective width, the lift decided against on measurement; the
  linear-light form, the area budget and the engine policy put to the user with recommendations.
  G1 opened on a branch with the forks behind conformance rows.
