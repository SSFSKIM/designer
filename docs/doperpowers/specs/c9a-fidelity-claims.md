# C9a — Per-tier fidelity claims

Child of [the vitrea composite spec](./2026-08-24-vitrea-liquid-glass-design.md).
Binding sections: §Calibration harness & methodology, §Purpose positioning,
Decision Log #20 and #26.

Every claim below is scoped to a **native profile × web cell**, per X9. Nothing
here says "pixel-identical to Apple", and nothing here is a pass verdict — the
thresholds in §5 are *proposals for the human gate*, not self-certification.

---

## 1. What was measured, and on what

**Ground truth.** 30 ScreenCaptureKit captures in
`apps/reference-apple/fixtures/`, every entry `materialRendered: true` and
`deterministic: true`, across two profiles:

| profile | scenes | calibration | validation | holdout |
| --- | --- | --- | --- | --- |
| `apple-macos-26.5-1x-light-standard` | 24 | 12 | 6 | 6 |
| `apple-macos-26.5-1x-dark-standard` | 6 | 6 | 0 | 0 |

**Web cell**, identical for all 30 cells: Chromium 151.0.7922.34, `renderer:
webgpu`, `samplingBackend: gpu-texture`, adapter `apple/metal-3`, colour space
`srgb`, Playwright element screenshot of `#stage` at `deviceScaleFactor 1`.
Every capture was **byte-identical over two independent page loads**.

**Coverage: 30 of 30 texture-tier cells measured**, in one `results/matrix.json`
(`schemaVersion 3`), captured in a reproducible interleaved order (FNV-1a of
`profileKey|sceneId`, matching the native harness's own permutation). A further
**18 dom-tier cells** (the light calibration and validation scenes on the CSS
tier, Chromium only) were measured for §3 and are deliberately *not* committed to
the matrix: that tier is untuned, so the numbers describe a configuration nobody
has yet decided to ship, and committing them would put them a copy-paste away
from being quoted as a claim. §3 states them in full.

Reproduce from clean:

```
pnpm --filter @vitrea/calibration run compare -- \
  --profile apple-macos-26.5-1x-light-standard --set calibration,validation,holdout
pnpm --filter @vitrea/calibration run compare -- \
  --profile apple-macos-26.5-1x-dark-standard --set calibration \
  --material-profile profiles/apple-macos-26.5-1x-dark-standard.json
```

Verified: deleting `web-captures/` and `results/matrix.json` and running exactly
those two commands reproduces **all 30 cells with every measured value identical**
— only the timestamps differ. Each cell's `capturePath` records the tunables it
ran on, by repo-relative path and SHA-256, so a committed result cannot be read
without knowing the configuration that produced it.

The holdout ids appear in no tuning code and in no sweep. `compare` defaults to
`--set calibration,validation`; holdout requires the flag and prints a banner.

---

## 2. The texture-tier claim

> **Reference-calibrated against macOS 26.5 captures.** vitrea's WebGPU texture
> tier — its own shader math over a GPU-owned backdrop — was calibrated against
> 30 ScreenCaptureKit captures of Apple's `glassEffect` material on macOS 26.5,
> in the cell *Chromium 151, `gpu-texture` backend, Apple Metal-3 adapter, sRGB,
> 1× scale*. Across the six scenes held out of tuning, the rendered result
> reaches a silhouette IoU of 0.9924 mean / 0.9612 worst, a contour distance of
> 0.18 px mean / 0.56 px worst-cell-mean, SSIM 0.9475 mean / 0.9007 worst, and
> OKLab ΔE 0.0320 mean / 0.0548 worst. Tuning improved every one of those axes
> over the untuned defaults. It is not pixel-identical to Apple's material and
> two named gaps remain open (§4).

**Per cell**, tuned, all axes as measured:

| set | n | IoU mean/worst | contour p95 mean/worst (px) | SSIM mean/worst | ΔE mean/worst |
| --- | --- | --- | --- | --- | --- |
| calibration (light) | 12 | 0.9542 / 0.8489 | 1.98 / 4.00 | 0.9754 / 0.9113 | 0.0086 / 0.0221 |
| calibration (dark) | 6 | 0.9490 / 0.8434 | 4.96 / 15.00 | 0.9533 / 0.9334 | 0.0128 / 0.0216 |
| validation (light) | 6 | 0.9595 / 0.8796 | 1.71 / 3.16 | 0.9766 / 0.9440 | 0.0109 / 0.0247 |
| **holdout (light)** | 6 | **0.9924 / 0.9612** | **0.64 / 2.83** | **0.9475 / 0.9007** | **0.0320 / 0.0548** |

Before and after, same cells and same estimator:

| set | axis | untuned | tuned |
| --- | --- | --- | --- |
| calibration | SSIM mean | 0.9378 | **0.9680** |
| calibration | ΔE mean | 0.0334 | **0.0100** |
| calibration | contour p95 mean | 5.61 | **2.77** |
| calibration | IoU mean | 0.9563 | 0.9528 *(marginally worse)* |
| validation | SSIM mean | 0.9696 | **0.9766** |
| validation | ΔE mean | 0.0186 | **0.0109** |
| validation | contour p95 mean | 6.43 | **1.71** |
| holdout | SSIM mean | 0.9172 | **0.9475** |
| holdout | ΔE mean | 0.0691 | **0.0320** |
| holdout | contour p95 mean | 18.97 | **0.64** |

The untuned holdout row is a **post-freeze reference measurement**: it was taken
after tuning was frozen, by restoring the previous defaults as a patch, and no
constant moved afterwards. Without it, "holdout ΔE is 0.032" is a number nobody
can judge.

### The honest reading of the holdout numbers

Two things are true at once, and the second is the one a reader should not be
allowed to miss.

**Tuning generalised on every axis.** All eight holdout figures improved. The
shape axis improved *more* on holdout than on the fitted sets — contour p95 fell
from 18.97 px to 0.64 px — and holdout is now the best-scoring set on shape.

**But holdout is relatively worse than it was on the perceptual axis.** Untuned,
holdout ΔE was 2.3× the calibration-plus-validation figure; tuned, it is 3.1×.
Tuning helped the fitted sets more than it helped the held-out ones, which is a
mild overfitting signal and is reported as one.

It has a named mechanism rather than being a mystery. Holdout deliberately took
the far end of the size sweep — both `rrect-lg` cells, the two largest surfaces
in the matrix — and the one unclosed material gap is precisely that Apple's
opacity varies with surface size while vitrea's does not (§4.1). On
`checkerboard__rrect-lg__rest` the reference's interior sits at 0.6384 and
vitrea's at 0.8000: the single fitted `tintAlpha` over-opacifies the largest
surfaces, and holdout is where the largest surfaces are. The overfitting signal
and the open gap are the same fact seen twice.

---

## 3. The dom-tier claim

> **No cross-engine pixel-wise fidelity claim is made for the dom tier, and none
> can be. A Chromium-only measurement now exists and is stated as such: on the 18
> light calibration and validation cells, the CSS tier reaches SSIM 0.9544 mean /
> 0.9040 worst and OKLab ΔE 0.0275 mean / 0.0727 worst — about 3.2× the texture
> tier's ΔE in the same cells. Its shape axis is not comparable to the texture
> tier's (see below), and it is UNTUNED.**

The cross-engine part is a consequence of S1's finding rather than a gap in this
work, recorded so the absence is legible. Gecko and WebKit render
`backdrop-filter` as a complete no-op in every automatable capture path
(Playwright headless and headed, retail `--screenshot`, WebDriver BiDi, WKWebView
`takeSnapshot`) while rendering it correctly live. A screenshot comparison on
those engines measures a blank. Decision Log #18's accepted narrowing —
Chromium-only pixel assertions, all-engine non-pixel suites, the manual page as a
release gate — is what makes the Chromium figure above a legitimate thing to
state, provided it names its one engine, which it does.

**The dom tier had never actually been diffed before this child**, and the reason
was a latent bug rather than a decision: the scene page reported its colour space
as an explanatory sentence, which the diff refused because X9 types a cell's
`colorSpace` as the closed `"srgb"`. Every prior run was GPU-tier, where the
sentence happened to reduce to exactly `"srgb"`, so the dom tier was structurally
unmeasurable and nothing said so. Fixed by separating the value from the route by
which it was learned.

**Its shape axis is not comparable to the texture tier's, and should not be
gated against the same thresholds.** The CSS tier draws its shadow as a
`box-shadow` *outside* the element, where the texture tier's is inside the
contour, and the luminance-delta extractor counts it as material. Measured
silhouette area against the declared component area: 1.04× over dark backdrops,
where a dark shadow is undetectable, rising to 2.36× on `light-solid` and
2.06–2.11× on the checkerboard group and small-rect scenes. That drives the
tier's silhouette IoU to a mean of 0.676 — a measurement of the shadow's extent,
not of the shape. The perceptual axis, taken over the whole canvas, is unaffected
by this and is the axis the claim above uses.

**What else is verified for the dom tier:**

- It resolves and draws on all three engines, asserted through non-pixel suites.
- Where the two tiers share a quantity the numbers were the same by construction
  — `platform-web`'s `MATERIAL_OPTICS.blurRadius` 8 against the renderer's
  `blurSigma` 8.

**And what is now deliberately out of step.** C9a's tuning did not reach the CSS
tier: `tintAlpha` 0.62 was applied to the renderer's profile, and
`platform-web`'s CSS-tier `tintAlpha` is still 0.28. The two tiers therefore
differ in opacity by more than 2×, and a root that demotes from the texture tier
to the CSS tier will visibly change appearance. This is reported rather than
quietly fixed: propagating a number fitted in a linear-light shader into a
different compositing pipeline (`backdrop-filter` plus an sRGB overlay) without
measuring it there would manufacture a claim, and the CSS tier has no override
seam to sweep through.

It is, however, now *measurable* on Chromium — the fix above is what unblocked it
— so a Chromium-scoped dom-tier tune is a concrete follow-up rather than an open
question. **Recommended: a CSS-tier tunables seam plus a Chromium-only dom-tier
sweep, before the tier coherence is claimed anywhere in the demo or the docs.**

The per-engine conformance table is C9d's release gate, not this document's.

---

## 4. Parent-impact: gaps that need renderer changes, with the evidence

Each of these was measured, and each was **not forced**. They need a new
parameter or a new pass, which is beyond a tunable.

### 4.1 The tint has no size term, and the reference's does

Regressing each side's interior level against the backdrop level under the same
mask, across the calibration scenes, recovers the material's un-attenuated
transmission. The reference's varies systematically with the surface's shorter
span; vitrea's cannot vary at all.

| surface | span (px) | reference: passes / adds | implied α |
| --- | --- | --- | --- |
| `rrect-sm` | 32 | 0.118 / 0.751 | 0.88 |
| `capsule-button` | 44 | 0.259 / 0.699 | 0.74 |
| `rrect-md` | 96 | 0.442 / 0.452 | 0.56 |
| vitrea (any span, tuned) | — | ~0.38 / ~0.62 | 0.62 |

A single `tintAlpha` therefore cannot fit the size sweep, and the residual
interior-level error of 0.071 is dominated by this rather than by a better
choice of value. Confirmed on held-out data: the two `rrect-lg` cells (span 160)
are where vitrea's material is furthest off.

**What it needs:** a size term on the tint alpha, mirroring the existing
`lensSpanMin`/`lensSpanMax`/`lensSizeGainMax` smoothstep that already
size-parameterises lens depth. Two new profile numbers and one shader term. Note
the direction is the *inverse* of the lens gain — a larger surface is more
transparent, not less — so it is not the same term reused.

### 4.2 The dark material wants a multiply, not a lerp

The reference's dark material is simultaneously very dark in the mean (interior
0.048–0.060 regardless of a backdrop ranging 0.213 to 0.570) and still passing
7–13% of the backdrop's structure. vitrea's tint is a lerp toward a colour, and a
lerp must trade one against the other: the fitted `tintAlpha` of 0.97 gets the
mean right (error 0.310 → 0.0096) and cannot get the spread right.

A multiply composite gets both. Inferring transmission from the spread ratio and
from the mean independently, a multiply model agrees with itself within a factor
of 1.3, 0.6, 1.2 and 0.5 across the four measurable dark cells; the lerp is off
by three to nine times.

**Evidence strength: weak-to-moderate.** Four cells, factor-two scatter, no dark
holdout. Enough to name a hypothesis and its measurement, not enough to assert a
blend mode. **What it needs:** a per-variant blend mode, which is a renderer
parameter.

### 4.3 Nothing selects a profile from the colour scheme

The single largest fidelity gap found in this child was not a constant being
wrong but a *mechanism* being wrong.

vitrea's adaptive tint interpolated between a white tint over dark backdrops and
a near-black tint over light ones — always contrasting with what is behind it.
The reference does not do that. Its interior rises monotonically with the
backdrop across the whole canonical range (0.680 at a backdrop of 0.003 through
0.932 at 0.891, light scheme), which is a fixed tint at partial transmission.
What it keys on is the **colour scheme**: over the same bright checkerboard it
sits at 0.809 in light and 0.055 in dark.

C9a neutralised the inversion (both crossover ends now equal) and recorded one
tuned profile per scheme. But **the runtime has no colour-scheme input to the
material**, so dark mode is correct only for a host that passes the dark profile
itself.

**What it needs:** platform-web reading `prefers-color-scheme` and applying the
matching shipped profile, plus a decision on whether the two profiles ship inside
`@vitrea/core` or as data. Small, but it is API surface, so it is the parent's.

### 4.4 The corner reference never reaches the renderer

`platform-web`'s bridge forwards a surface's `smoothing` but not its corner
`reference`, so every web surface resolves to `apple-continuous` — under which
`resolveCorner` pins smoothing to the seed and **discards the forwarded number
entirely**. `profile: "circular"` and numeric smoothing profiles do not reach the
GPU tier.

Benign for calibration (the reference draws `.continuous`, which is what we want
to be measured against) and the reason it stayed invisible. Not benign for the
public API, where X8's two-reference model is documented as reachable.

### 4.5 The union aesthetics are unmeasurable by this scene matrix

C7 flowed forward that the bridge never carried `mergeDistance` into
`DEFAULT_GROUP_UNION`, and that the wiring had to precede the tuning. The wiring
landed with K2. The tuning still cannot happen, for a different reason: **the
reference does not union at the one spacing the matrix declares.**

Counting connected components in the extracted silhouettes, the `toolbar-group`
scene yields three separate bodies on *both* sides — 1572/1572/1570 px for the
reference against 1769/1765/1756 px for vitrea, where an unmerged 44 px capsule
is 1520 px. Filling the two 12 px gaps would add 23% to the group's area; the
reference adds 3.3%. Confirmed by sweeping the declared merge distance across 24,
12 and 4: all three give a byte-identical silhouette area, because the union
blend never engages at this separation whatever the threshold is.

C7's assumption that the native container reaches "one merged body" at spacing 12
is refuted. **What it needs:** a canonical scene whose members are close enough
that the reference itself merges them — a `scenes.json` addition, so a scope
decision.

### 4.6 vitrea's material bleeds ~1.4 px past the reference's contour

Found while refuting 4.5. Per capsule, the reference's silhouette sits 0.37 px
outside the declared shape and vitrea's 1.73 px outside, at the 0.02 detection
threshold. It is what holds the group scene's IoU down to 0.884 — the worst
well-conditioned calibration cell — because three small bodies make IoU
unusually sensitive to a uniform dilation. Not tuned: the bleed comes from the
rim and glow passes together and no single profile constant isolates it.

---

## 5. Proposed thresholds — for the human gate

**Per cell, per tier.** Derived from what tuning achieved, with headroom, and
**bounded by the holdout numbers rather than the calibration ones**: a gate that
calibration passes and holdout fails would certify overfitting rather than
prevent it. On the perceptual axis, holdout is the binding case.

### Texture tier, `apple-macos-26.5-1x-light-standard`, cell as §1

| axis | metric | proposed | worst cal+val | worst holdout |
| --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.82 | 0.8489 | 0.9612 |
| shape | contour distance mean | ≤ 2.5 px | 1.9336 | 0.5590 |
| shape | contour distance p95 | ≤ 5.0 px | 4.0000 | 2.8284 |
| perceptual | SSIM mean | ≥ 0.88 | 0.9113 | 0.9007 |
| perceptual | OKLab ΔE mean | ≤ 0.07 | 0.0247 | 0.0548 |
| perceptual | OKLab ΔE p95 | ≤ 0.17 | 0.1409 | 0.1337 |
| perceptual | edge-weighted mean | ≤ 0.11 | 0.0491 | 0.0923 |

**Gate the shape axis only on a well-conditioned cell.** Predicate:
`silhouetteAreaNative ≥ 0.95 × the declared component area`. The luminance-delta
extractor finds the component by differencing against its backdrop, so it loses
any part of the material whose level coincides with the backdrop's — and one
canonical cell is exactly that case. `checkerboard__capsule-button__rest` in the
dark profile returns a native silhouette of 4324 px where the declared capsule is
4865, holes punched through its own interior, while vitrea's returns 5127 by
picking up its halo. That cell's IoU of 0.843 and contour p95 of 15.0 px describe
the extractor, not the geometry, and they are the worst shape figures in the
whole matrix. `silhouetteAreaNative` and `silhouetteAreaWeb` are on the record in
every cell (schema 3) so this predicate is machine-checkable.

### Texture tier, `apple-macos-26.5-1x-dark-standard`

The same thresholds are satisfied by all six dark cells, but the claim is
weaker and should be gated as **provisional**: the dark profile declares no
validation and no holdout scenes, so nothing in it is held out, and two of its
six cells cannot measure the material at all (an empty native silhouette over a
solid backdrop of its own tone — a real property of the material, not a capture
fault). A dark-scheme claim needs its own split before it should be gated at the
same level as light.

### Not proposed

- **Material-axis thresholds.** The sub-metrics that identify the material are
  either not identifiable on this fixture set (blur sigma, §6.1) or below the
  capture's own quantisation (the light-scheme rim, §6.2). A threshold on a
  quantity the fixtures cannot resolve is a number that will be met by accident.
- **Motion thresholds.** No frame sequences were captured, and the still
  `pressed` cells cannot substitute — see §6.3.
- **dom-tier thresholds.** §3.

---

## 6. What could not be measured, and why

### 6.1 Blur sigma is not identifiable from these backgrounds

Swept at 2, 4, 6 and 8; the whole two-dimensional (`tintAlpha` × `blurSigma`)
grid spans 1.08×, and the optimum at 4 beats 8 by 2%. The reason is structural,
not statistical: no canonical background resolves a step edge at this material's
sigma. The checkerboard's 16 px cell bounds any single-edge window to about one
period, and the impulse background is a sparse train rather than a step. Left at
8, which is also what makes core's 24 px `samplingPadding` exactly the 3σ floor
S1 measured, and what keeps the two tiers on one number.

Worth recording that C7's own instrumentation was reporting a confident wrong
answer here: the material axis measured σ 50.6 px at a fit residual of 63× the
step height, because the default measurement region was a strip across the
interior that straddled many checkerboard edges. A single error function fitted
to a multi-edge profile is not ill-conditioned — it answers a different question.
The region is now derived from the backdrop's own step structure, and the
residual is reported per side so an unidentifiable fit reads as one.

**Would need:** a canonical background with one large step edge — a
half-dark/half-light field. A `scenes.json` addition.

### 6.2 The light-scheme rim is below the capture's quantisation

Swept `rimAlpha` × `specularGain`; the grid is flat to 1.01×. The reference's
light-scheme rim peaks measure 0.0003 to 0.0012 of linear luminance on the solid
and checkerboard scenes, while one 8-bit code step at the interior level those
scenes sit at (≈0.81) is 0.0079 — the signal is four to twenty-six times below
the capture's own resolution. Only the photo scenes carry a rim above it.

The dark scheme is different: rim peaks of 0.041 to 0.055 are comfortably
measurable there, and after the tint tune the rim is the dominant dark-scheme
error term (0.084 of a 0.111 objective). **A rim retune was found and declined.**
Dropping `rimAlpha` to 0.02 and `specularGain` to 0.10 halves the dark objective
to 0.0591 and lifts SSIM from 0.953 to 0.966 — but the residual bottoms out at
almost exactly the mean of the reference's own rim peaks, meaning the win comes
from vitrea's rim going to *zero* rather than from it matching. The reference
demonstrably has a rim there. Per-cell the direction is not even consistent: on
three cells vitrea's rim is too bright and on the fourth too dim (0.0099 against
0.0478). Fitting a four-cell mean by deleting the feature it measures is fitting
the estimator, so the gap is reported instead.

**Would need:** the 2× profile, which puts four times the samples under the same
rim band. External gate — a Retina display.

### 6.3 The pressed cells compare two different states

C7 flagged the pressed scenes as "two independently-derived poses". It is
sharper than that: **the native pressed fixtures are byte-identical to their rest
counterparts** — all four, verified by SHA-256. The harness applies
`Glass.interactive(true)`, which opts the material into responding to press
input rather than posing it pressed, and no press input exists in a capture run.
Apple exposes no declarative way to pose it.

So the four pressed cells measure *vitrea's pressed pose against Apple's rest
pose*. **No press-fidelity claim is made.** They were also excluded from the
tuning decision: re-running the `tintAlpha` sweep over only the ten non-pressed
light calibration scenes returns the same optimum of 0.62, so they did not
influence the fitted value.

### 6.4 The glass-over-glass cells are a mixed-backend claim

C7's scoping item, unchanged and restated as the claim it is. Natively the upper
`glassEffect` samples the lower one's rendered output; on the web that
relationship *is* the plane sandwich, so the overlay group must be declared
`dom` — a texture-backed overlay would sample the raw raster and miss the point
of the scene. Those two cells therefore resolve to `gpu-texture + css-backdrop`
with `refraction: "approximate"` even on the GPU tier.

They are counted in the holdout numbers above, and they are **not** a clean
texture-tier claim. Their figures: `checkerboard__glass-over-glass__rest` SSIM
0.901 / ΔE 0.0345, `photo__glass-over-glass__rest` SSIM 0.944 / ΔE 0.0387 — the
two lowest SSIM figures in the holdout set. Anyone quoting the texture-tier
holdout SSIM worst of 0.9007 should know it is one of these.

### 6.5 Material thickness has no shared value

C7's scoping item, and it stands. `scenes.json` declares no thickness channel, so
the web side uses `platform-web`'s 8 px host default and SwiftUI uses whatever
its material does — a quantity Apple does not expose. **The field was not added.**
Adding it would let both sides honour one number, but only the web side can be
set to it, so it would pin vitrea to a value and leave the reference where it
was: worth doing for reproducibility, worthless as a fidelity measurement. A
scope decision, recorded rather than taken.

### 6.6 Profiles that do not exist

Four profile keys are declared in `scenes.json` and two of them have no
captures. **Every claim above is scoped to the two that do.**

- `apple-macos-26.5-1x-light-reduced-transparency` and
  `-increased-contrast`: macOS exposes the accessibility display modes as
  read-only `EnvironmentValues`, so each needs its own capture run with the
  System Settings toggle on. External, user. Note the inversion C7 recorded: the
  web side *can* set these per render, so vitrea is not the constraint here.
- **The `-2x-` profiles are unreachable on this machine.** A Mac14,12 driving a
  1920×1080 panel reports `backingScaleFactor` 1.0. Every claim above is a 1×
  claim, and the rim and corner questions in §6.1–6.2 are exactly the ones a 2×
  run would move.

---

## 7. Constants changed

| constant | before | after | basis |
| --- | --- | --- | --- |
| `optics.regular.tintAlpha` | 0.28 | **0.62** | across-scene transmission regression + declared sweep objective, 11 light calibration cells |
| `adaptiveTintLight` | sRGB [0.09, 0.09, 0.1] | **[1, 1, 1]** (both ends equal) | the reference does not invert its tint against the backdrop; §4.3 |

Everything else is unchanged, each with a recorded reason: `blurSigma` (§6.1),
rim and specular (§6.2), shadow (both sides ≈0 outside the contour — no measured
gap, and these two constants drive an *inner* shadow in this renderer anyway),
the group union caps (§4.5), corner smoothing (below).

Dark-scheme values live in
`packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json` as a patch
(`tint` [0.05,0.05,0.05], `tintAlpha` 0.97), because only one scheme can be the
runtime default.

**The corner-smoothing question S2 left open is answered: the fixtures cannot
decide it.** S2's own residuals are 6.06e-4 per radius for the Apple-direct fit
and 1.96e-3 for the best Figma route; at the largest canonical radius (20 px)
that is 0.012 px against 0.039 px, both two orders of magnitude below one pixel.
The measurement agrees — contour distance on the corner-bearing calibration
scenes runs 0.00 to 0.14 px mean, at or under the rasterisation floor. No 1×
raster can separate them, and §4.4 makes the Figma route unreachable from the web
runtime in any case. The Apple-direct fit stands, on S2's geometric evidence
rather than on anything C9a measured.

### How the seam works

The mission's requirement was that tuned values land in the calibration profile
JSON "consumed by the runtime's tunables". They do, with one deliberate
interpretation: **the runtime does not read JSON at run time.** A published
package loading a calibration file would ship a data dependency for numbers that
never change between releases, against X7's two-packages-with-bundled-internals
rule. Instead:

- The profile JSON is the authority, carrying provenance and what each number
  does *not* close.
- The renderer's `DEFAULT_MATERIAL_PROFILE` mirrors the one profile it targets.
- `packages/calibration/test/tuned-profiles.test.ts` pins the two together in
  both directions, so the record and the code cannot drift silently.
- Any other profile is applied as data at run time:
  `createGlassRoot({ materialProfile })`, forwarded through platform-web to the
  renderer, with the applied file's SHA-256 recorded in every result cell's
  `capturePath`.

### A methodology fix that invalidated the first round of numbers

Recorded because it would have silently poisoned this entire child, and because
the shape of the mistake generalises.

The GPU tier's adaptive tint is driven by an analysis reduction read back off the
device; the bridge fires `collectAdaptation()` once per frame and never blocks on
it, so the observation lands on a later task. The calibration page stepped every
frame in one synchronous loop, so **no readback could resolve before the final
draw** — every capture rendered the un-adapted material, a state no application
ever shows. The frame count made no difference at all, which is why it stayed
invisible: captures at `frames=8` and `frames=240` are byte-identical.

It was found by injecting marker colours (adaptive ends pure red and pure blue,
tint fully applied) and observing a neutral 249,249,249 interior — no adaptive
contribution whatever. Yielding to the macrotask queue between frames is *not*
enough, because the readback needs the GPU to finish. Pacing on
`requestAnimationFrame` gives each frame's readback the wall-clock time a live
loop gives it, and the interior then reads 63,63,249. Frame timestamps stay
simulated, so determinism is preserved, and it was re-verified: every capture in
every run above is byte-identical over two independent page loads.

The generalisable form: **when a harness drives frames by hand, it takes on
responsibility for every asynchronous path the real frame loop would have
serviced** — and a capture that is stable is not thereby correct.
