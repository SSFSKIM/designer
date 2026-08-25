# C9a — Per-tier fidelity claims

Child of [the vitrea composite spec](./2026-08-24-vitrea-liquid-glass-design.md).
Binding sections: §Calibration harness & methodology, §Purpose positioning,
Decision Log #20 and #26.

**Amended by K5 (2026-08-25).** C9a closed recommending "a CSS-tier tunables seam
plus a Chromium-only dom-tier sweep, before the tier coherence is claimed
anywhere" (§3). K5 executed that: the CSS tier now derives its material from the
same profile the renderer reads, the mapping between them is tuned, all 30
dom-tier cells are measured and committed, and §3 states the result. Sections
touched: §1 (coverage), §3 (rewritten, with C9a's untuned figures kept as the
before-state), §3.1 (new — tier coherence), §5 (dom-tier thresholds, now
proposable), §7 (constants changed). Everything about the texture tier is C9a's
and unchanged — K5 moved no renderer constant, and the re-measured texture cells
reproduce C9a's numbers exactly, which is the evidence for that.

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

**Coverage: 60 of 60 cells measured** — all 30 texture-tier and, since K5, all 30
dom-tier — in one `results/matrix.json` (`schemaVersion 3`), captured in a
reproducible interleaved order (FNV-1a of `profileKey|sceneId`, matching the
native harness's own permutation).

C9a measured 18 dom-tier cells and deliberately did *not* commit them, because
that tier was untuned and committing the numbers would have put a configuration
nobody had decided to ship a copy-paste away from being quoted as a claim. K5
tuned it, so all 30 are now committed with their full cell keys — `renderer: css`,
`samplingBackend: css-backdrop`, `tier: dom` — beside the texture cells they can
now legitimately be compared with.

Reproduce from clean:

```
pnpm --filter @vitrea/calibration run compare -- \
  --profile apple-macos-26.5-1x-light-standard --set calibration,validation,holdout
pnpm --filter @vitrea/calibration run compare -- \
  --profile apple-macos-26.5-1x-dark-standard --set calibration \
  --material-profile profiles/apple-macos-26.5-1x-dark-standard.json
pnpm --filter @vitrea/calibration run compare -- \
  --profile apple-macos-26.5-1x-light-standard --set calibration,validation,holdout \
  --renderer css
pnpm --filter @vitrea/calibration run compare -- \
  --profile apple-macos-26.5-1x-dark-standard --set calibration --renderer css \
  --material-profile profiles/apple-macos-26.5-1x-dark-standard.json
```

The two dom-tier runs take no mapping override: the tuned mapping *is*
`platform-web`'s shipped `CSS_TIER_MAPPING`, and a committed cell has to be a
measurement of what ships. Re-running the four commands reproduces all 60 cells,
and the texture cells come back at C9a's published figures to four decimals —
which is the evidence that K5 moved no renderer constant.

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
> can be.** Chromium is the one engine whose `backdrop-filter` output any capture
> path can see (S1), so this is a one-engine claim and says so.
>
> **On Chromium, in the cell of §1 with `renderer: css` and `samplingBackend:
> css-backdrop`:** vitrea's CSS tier reaches OKLab ΔE 0.0113 mean / 0.0248 worst
> and SSIM 0.9655 mean / 0.9271 worst over the 12 light calibration cells; ΔE
> 0.0123 / 0.0273 and SSIM 0.9697 / 0.9511 over the 6 validation cells; and, on
> the six scenes held out of all tuning, **ΔE 0.0319 mean / 0.0606 worst and SSIM
> 0.9317 mean / 0.9131 worst** — within 0.00004 of the texture tier's own holdout
> ΔE of 0.0320. The six dark calibration cells reach ΔE 0.0162 / 0.0258.
>
> **Its shape axis is not gated against the texture tier's thresholds**, and the
> reason is now attributed rather than described: the tier's own `box-shadow`, not
> its geometry (§3.2).

### What tuning moved

K5 tuned one constant — the mapping's `referenceBackdropLuminance` — and the
CSS tier's alpha stopped being an independent number:

| set | axis | untuned (C9a) | tuned (K5) |
| --- | --- | --- | --- |
| calibration (light, 12) | ΔE mean | 0.0275 | **0.0113** |
| calibration (light, 12) | ΔE worst | 0.0727 | **0.0248** |
| calibration (light, 12) | SSIM mean | 0.9544 | **0.9655** |
| validation (light, 6) | ΔE mean | 0.0352 | **0.0123** |
| validation (light, 6) | SSIM mean | 0.9440 | **0.9697** |
| calibration (dark, 6) | ΔE mean | 0.0505 | **0.0162** |
| calibration (dark, 6) | SSIM mean | 0.9001 | **0.9443** |

The dark row is the largest single improvement and it is not a tuning result at
all: before K5 a CSS-tier root **ignored the material profile entirely**, so the
dark profile's tint never reached it and the dark material was drawn as a white
veil. Deriving the tier from the profile fixed that as a side effect of the seam
existing. Nothing selects a profile from the colour scheme yet either way — that
is still §4.3, unchanged.

Holdout has no before-figure and deliberately so: it was untouched until the
mapping froze, then measured once, which is the only reading a holdout number
supports.

### C9a's untuned reading, kept

> *"On the 18 light calibration and validation cells, the CSS tier reaches SSIM
> 0.9544 mean / 0.9040 worst and OKLab ΔE 0.0275 mean / 0.0727 worst — about 3.2×
> the texture tier's ΔE in the same cells. It is UNTUNED."*

Reproduced exactly from clean before any K5 change, which is what established
that the pipeline and this machine had not drifted between the two children.

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

### 3.1 Tier coherence — the number the claim turns on

C9a's closing recommendation was that coherence not be claimed until it was
measured. It is now measured, by a diff this package did not previously have:
`cli/tier-delta.ts`, web against web, with no fixture in it. Two tiers can each
sit inside their own threshold against Apple and still be visibly different from
each other, and a demotion is exactly where a reader sees them side by side
rather than each beside Apple.

Over the 17 measurable light calibration and validation cells, same scenes both
tiers, Chromium:

| | before (C9a's state) | after (K5) |
| --- | --- | --- |
| interior level, GPU ÷ CSS, mean | **3.19** | **0.99** |
| interior level, GPU ÷ CSS, per-cell range | **1.67 … 9.18** | **0.90 … 1.07** |
| cross-tier SSIM, mean / worst | 0.9459 / 0.8568 | **0.9693 / 0.9496** |
| cross-tier OKLab ΔE, mean / worst | 0.0370 / 0.1086 | **0.0080 / 0.0151** |
| each tier's own ΔE vs Apple, GPU / CSS | 0.0097 / 0.0314 | 0.0097 / **0.0116** |

Read the range row first. Before, the CSS tier was between 1.7× and 9.2× more
transparent than the GPU tier depending on the backdrop — the ">2×" C9a reported
was the checkerboard cells, and over a dark backdrop it reached nine. After, the
worst cell of seventeen differs by 11%, and the direction is no longer consistent,
which is what a converted alpha rather than a copied one looks like.

On the six holdout scenes, measured once at the frozen mapping: cross-tier ΔE
0.0229 mean / 0.0358 worst, interior ratio 0.964 mean. The two worst cells are
the `glass-over-glass` pair, and for a reason §6.4 already names — on the GPU
tier that scene's overlay group is necessarily `dom`, so those cells were always
a mixed-backend comparison, and on the CSS tier both groups are `css`. The tiers
genuinely differ most exactly where the GPU tier is least itself.

**So: coherence can be claimed, in this wording.**

> On Chromium, a group that demotes from the WebGPU texture tier to the CSS tier
> keeps the same material to within 1% of its interior level in the mean and 11%
> on the worst measured cell, at a cross-tier OKLab ΔE of 0.0080 mean / 0.0151
> worst over the fitted sets and 0.0229 / 0.0358 over the held-out ones. It is
> not the same rendering — refraction is absent on the CSS tier by contract
> (`refraction: "none"`), and the shape axis differs by the shadow of §3.2 — but
> the material's opacity, tint and frost no longer change visibly on demotion.

And what it may **not** say: that the two tiers are identical, or that any of this
holds on Gecko or WebKit. It is a Chromium measurement of a material's level, on
one profile, at 1×.

**The floor, stated as arithmetic rather than as a hope.** Exact coherence is
unreachable and no amount of tuning reaches it. For the shipped white tint at the
renderer's α = 0.62, matching the two composites needs a CSS alpha of 0.761 over a
backdrop at linear luminance 0.05 and 0.635 over one at 0.8 — a 1.2× spread with
no single scalar in it, because the renderer applies its transfer function *after*
the blend and the page applies it *before*. One scalar can be exact at one
backdrop level and is necessarily wrong either side. 0.0080 mean ΔE is what
remains after choosing that level well; it is a property of `backdrop-filter`, not
a residual anyone can tune away.

**Why the mapping was fitted for coherence and not for fidelity.** The two
objectives disagree, monotonically and in opposite directions: across
`referenceBackdropLuminance` from 0.005 to 0.30 the cross-tier ΔE rises
0.0078 → 0.0115 while the CSS tier's own ΔE against Apple *falls* 0.0118 → 0.0094.
They can disagree because the GPU tier is not itself exactly on the reference, so
the point that best matches the GPU tier is not the point that best matches Apple.
Coherence was chosen: a CSS tier fitted independently against the fixtures is free
to drift from the GPU tier again the moment either is retuned — which is precisely
how this gap opened, when C9a moved one tier's constant — whereas a *converted*
tier inherits the GPU tier's fidelity by construction. The price is on the record
above: 0.0116 against Apple where an independent fit would have reached 0.0094,
both far inside the 0.07 threshold §5 proposes.

### 3.2 The shape axis belongs to the box-shadow, and that is now measured

C9a reported that the dom tier's shape axis was not comparable to the texture
tier's, and attributed it to the `box-shadow` the CSS tier draws *outside* the
element, which the luminance-delta extractor counts as material. That was right,
and it understated the case. Setting `shadowAlpha` to 0 and changing nothing else:

| axis | with the shadow | without it | texture tier |
| --- | --- | --- | --- |
| silhouette IoU, calibration | 0.6756 | **0.9424** | 0.9542 |
| silhouette IoU, holdout | 0.7626 | **0.9684** | 0.9924 |
| contour p95 mean, calibration | 18.67 px | **2.22 px** | 1.98 px |
| ΔE mean, calibration | 0.0113 | **0.0092** | 0.0086 |
| cross-tier ΔE, mean | 0.0119 | **0.0096** | — |
| CSS-tier ΔE vs Apple, all sets | 0.0169 | **0.0149** | 0.0155 |

The dom tier's *geometry* was never the problem — it lands at IoU 0.94 and 2.2 px
contour, comparable to the texture tier — and the shadow was hiding that. It is
also costing the perceptual axis and the coherence figure, and without it the CSS
tier would be marginally *closer* to Apple than the GPU tier is.

Attributed rather than assumed: the IoU mean sat at 0.6755–0.6756 at **every**
point of every sweep run for this child, moving in the fourth decimal while the
tint alpha moved by a third and the border alpha went to zero. Nothing but the
shadow moves that axis.

**Not removed, and this is the one open decision K5 hands back.** The reference
material has no exterior shadow — C9a measured both sides at ≈0 outside the
contour — so on measurement alone the shadow is a fidelity defect on three axes
at once. Against that: the repo's effects policy says the fallback *is* the
design, and the ambient shadow is what makes an unfiltered surface read as
floating rather than as a flat translucent box, which is S1's undetectable-failure
case. That is a taste judgement with a design owner, and C9b's landed showpiece
inherits whichever way it goes. Measured, priced, and left to the parent.

### 3.3 The foreground rule had to change with the material, and did

Not a fidelity number, but the largest single consequence of tuning this tier, so
it belongs beside the claim rather than in a commit message.

K4 wired X6's hint straight to the foreground token: a group hinting `tone:
"dark"` got the light ink. That was correct while the material was 28% opaque —
the backdrop showed through, and light ink on a dark backdrop is right. At the
material's measured opacity it inverts: what a reader sees behind the glyphs is
`mix(backdrop, tint, α)`, and at α = 0.78 that is the white tint. Measured on the
demo's own controls before this was fixed, **WCAG contrast 1.24 against a 4.5
floor** — near-white ink on a near-white surface.

So the CSS tier now decides its foreground against the level behind the glyphs
rather than against the backdrop alone, using the hint's `luminance` where an app
gives one and the tone's coarse reading otherwise. The mechanism K4 established
is untouched; only the arithmetic changed, and both regimes remain reachable —
the *clear* variant over the same dark hint still resolves to the light token,
because at its alpha the backdrop genuinely does dominate.

Two things this does not do. It is **not** a contrast calculation and does not
promise a ratio: it picks between two ink tokens, and an app needing a guaranteed
ratio still sets its own foreground. And it is **CSS-tier only** — whether the GPU
tier's foreground path needs the same correction is a parent question, because
that path is the renderer's and K5 moved nothing there.

**What else is verified for the dom tier:**

- It resolves and draws on all three engines, asserted through non-pixel suites.
- The two tiers' shared quantities are now shared *by construction* rather than by
  coincidence: `platform-web` mirrors the renderer's per-variant optics and
  `packages/calibration/test/tier-coherence.test.ts` pins the mirror in both
  directions. Before K5 the agreement on σ = 8 was two literals that happened to
  match.

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
- **A dom-tier shape threshold.** The axis measures the tier's `box-shadow`
  rather than its geometry (§3.2), and gating a quantity that is 0.68 with the
  shadow and 0.94 without it would be gating a design decision nobody has taken
  yet. It becomes proposable the moment the shadow question in §3.2 is settled,
  either way.

### Dom tier, `apple-macos-26.5-1x-light-standard`, Chromium, `renderer: css`

Added by K5, on the same rule as the texture tier's — **bounded by the holdout
numbers, not the calibration ones** — and with the shape axis deliberately absent.

| axis | metric | proposed | worst cal+val | worst holdout |
| --- | --- | --- | --- | --- |
| perceptual | SSIM mean | ≥ 0.90 | 0.9271 | 0.9131 |
| perceptual | OKLab ΔE mean | ≤ 0.08 | 0.0273 | 0.0606 |
| coherence | cross-tier OKLab ΔE mean | ≤ 0.05 | 0.0151 | 0.0358 |
| coherence | interior level, GPU ÷ CSS | 0.80 … 1.25 | 0.895 … 1.067 | 0.863 … 1.040 |

Three things about this table are deliberate.

**The coherence rows are a new kind of gate** and they belong here rather than
with the texture tier, because coherence is a property of the pair and the CSS
tier is the one that moves. They are what would catch the next C9a — a renderer
constant retuned without the mapping being re-measured — before a reader sees it
as a material changing on demotion.

**Every bound is looser than the texture tier's counterpart** (ΔE ≤ 0.08 against
≤ 0.07, SSIM ≥ 0.90 against ≥ 0.88 is the exception and is tighter only because
the dom tier happens to score better on SSIM). The dom tier renders through an
engine's blur rather than vitrea's own math, and a gate that assumed otherwise
would be asserting control over Chromium's compositor.

**It is a one-engine gate.** Gecko and WebKit render `backdrop-filter` as a no-op
in every capture path, so there is nothing to threshold there and the manual page
remains their only evidence (C9d's release gate).

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
scenes sit at (≈0.81) is 0.0079 — the signal is seven to twenty-six times below
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
| **K5** — `CSS_TIER_MAPPING.referenceBackdropLuminance` | *(did not exist)* | **0.02** | fitted against the cross-tier delta over 17 light cal+val cells; §3.1 |

The K5 row is a different kind of entry from the two above it, and the difference
matters more than the number. The other constants are *the material*; this one is
**the price of the crossing** — the CSS tier no longer carries a tint alpha at
all. It reads `optics.regular.tintAlpha` off the same profile the renderer does
and converts it, so this row moves when the renderer's row moves, and the tuned
value here is the conversion rather than a second opinion about the material.

What K5 replaced, for the record: `platform-web`'s CSS tier held its own
`tintAlpha: 0.28`, `saturation`, `borderAlpha`, tint colour and shadow as literals
in `optics.ts` and `css-tier.ts`. Those are gone. The tint alpha and border alpha
are derived from the profile, the tint and border *colours* are the profile's own
`tint` and `highlight` sRGB-encoded (which is what let the dark profile finally
reach this tier), and the remaining CSS-only quantities — `saturate()`, the border
width, the shadow triple — live in `CssTierMapping` where they can be swept.

Two mapping constants were swept and **declined**, each recorded in
`packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json`:
`borderAlphaPerRimAlpha` (a 1.01× grid — the fixtures do not identify it, and
zeroing it would delete the tier's contrast floor to win flatness, which is C9a's
own rim reasoning applied one tier along) and the shadow triple (§3.2 — measured,
priced, and a design decision rather than a measurement).

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
