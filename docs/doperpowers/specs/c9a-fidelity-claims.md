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

**Amended by C9d (2026-08-25).** K5 handed three items back to the parent and the
parent ruled on all three (Decision Log #32(b)–(d)); C9d executed them, which moved
the dom tier's numbers. Sections touched: §3 (every dom-tier figure re-measured
over all 30 cells with the `box-shadow` removed, K5's figures kept in §3.2 as the
before-state), §3.1 (a third column, and the coherence-versus-fidelity price
restated now that it is 0.0005 rather than 0.0022), §3.2 (the shadow question is
decided and executed), §3.3 (the GPU tier's foreground was audited, the defect
reproduced at WCAG 1.57, and the rule is now shared across both tiers), §5 (a
dom-tier shape threshold, which the shadow's removal made meaningful). **The
texture tier is untouched here as well: the 30 texture cells in
`packages/calibration/results/matrix.json` are byte-identical across this child.**

**Amended by W7 (2026-08-30).** Backdrop tone adaptation landed, and it is so far
the only amendment that *removes* a limitation rather than adding a claim.
Sections touched: §5.4 (**rewritten** — the seven excluded rows re-entered the
adopted gate and pass at unchanged bounds, and the exclusion was deleted; the
before-state is kept inside it), §5.8 (new — the measurement, the law, the fit,
and the full re-verification), §5.7 (annotated: the size-derived facet it left
open is closed, and the band 32…96 is now pinned by a second independent
measurement), §4.3 (annotated — its *evidence* is superseded by the settled bed;
its parent-impact item still stands). Every adopted threshold in §5 is untouched
in both directions, and `results/matrix.json` is regenerated over all six profiles
and both tiers from fresh captures.

**Amended by the recalibration cascade (2026-08-31) — and the amendment is a
scope warning, not a result.** Every figure and every fitted constant in this
document predates the discovery that the whole capture bed recorded Liquid
Glass's **inactive** appearance (wave Decision Log 14). Measured against the
active bed, the material carries an outer shadow vitrea does not draw at all,
which breaks the silhouette extractor the shape *and* material axes are built on
— so the cascade produced a damage report and stopped rather than fitting against
a corrupted objective. Sections touched: **§5.11 (new)** — the active-bed damage
report, the shadow's measurement, what each stage's refit would have been, and
the three rulings the gate now owes. Nothing else in this document was edited:
no bound moved, no constant moved, `results/matrix.json` is untouched, and every
section above §5.11 must now be read as a description of the inactive pose.

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
dom-tier — captured in a reproducible interleaved order (FNV-1a of
`profileKey|sceneId`, matching the native harness's own permutation).

*Superseded as an artifact, not as a claim.* `results/matrix.json` now holds W1's
**settled six-profile bed**: 176 cells, `schemaVersion 4`, two backing scales ×
light/dark × two accessibility profiles, each dom cell carrying the coherence
axis (§5.2). This section describes the v1 measurement those claims were first
made on; §5's tables were re-verified against the settled bed and their bounds
did not move. The 60-cell v1 matrix is in git history.

The count reached 176 from W7's 168 by W7's own holdout scene arriving in the
four standard profiles (§5.9). It did **not** reach 192: `scenes.json` declares
12 tinted scenes and the harness captured them, but that capture carried no tint
colour, so the tint axis is absent from the matrix by derivation (§5.10).

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
> css-backdrop`:** vitrea's CSS tier reaches OKLab ΔE 0.0091 mean / 0.0240 worst
> and SSIM 0.9700 mean / 0.9304 worst over the 12 light calibration cells; ΔE
> 0.0108 / 0.0273 and SSIM 0.9715 / 0.9511 over the 6 validation cells; and, on
> the six scenes held out of all tuning, **ΔE 0.0291 mean / 0.0560 worst and SSIM
> 0.9373 mean / 0.9205 worst** — against the texture tier's own holdout ΔE of
> 0.0320, so the two tiers' held-out perceptual figures now sit within 0.003 of
> each other with the dom tier marginally ahead. The six dark calibration cells
> reach ΔE 0.0144 / 0.0241.
>
> **Its shape axis is now claimable too**, at silhouette IoU 0.9424 mean / 0.8969
> worst over the light calibration cells and 0.9684 / 0.9357 on holdout, with
> contour distance 1.06 px mean and 2.83 px p95. That axis used to belong to the
> tier's own `box-shadow` rather than to its geometry; C9d removed the shadow on
> the parent's ruling and the geometry underneath was always comparable to the
> texture tier's (§3.2).

> **Amended by C9d (Decision Log #32(c)).** Every dom-tier figure above is
> re-measured over all 30 cells with the `box-shadow` removed. The numbers K5
> reported for the same sets are kept in §3.2's table so the shadow's price stays
> on the record rather than being quietly replaced.

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

| | before (C9a's state) | after (K5) | after (C9d, no shadow) |
| --- | --- | --- | --- |
| interior level, GPU ÷ CSS, mean | **3.19** | **0.99** | 0.987 |
| interior level, GPU ÷ CSS, per-cell range | **1.67 … 9.18** | **0.90 … 1.07** | 0.895 … 1.067 |
| cross-tier SSIM, mean / worst | 0.9459 / 0.8568 | **0.9693 / 0.9496** | **0.9710 / 0.9498** |
| cross-tier OKLab ΔE, mean / worst | 0.0370 / 0.1086 | **0.0080 / 0.0151** | **0.0063 / 0.0124** |
| each tier's own ΔE vs Apple, GPU / CSS | 0.0097 / 0.0314 | 0.0097 / **0.0116** | 0.0097 / **0.0099** |

The last column is C9d's, and the last row of it is the interesting one: with the
shadow gone the CSS tier sits at 0.0099 against Apple where an independent fit
would have reached 0.0094, so the price K5 paid for coherence over independent
fidelity — 0.0116 against 0.0094 — is now 0.0005 rather than 0.0022. The trade
was real when it was made and is very nearly free now. That is not a vindication
of the choice: it is the shadow having been the larger term all along, in a
quantity nobody had separated it out of.

Read the range row first. Before, the CSS tier was between 1.7× and 9.2× more
transparent than the GPU tier depending on the backdrop — the ">2×" C9a reported
was the checkerboard cells, and over a dark backdrop it reached nine. After, the
worst cell of seventeen differs by 11%, and the direction is no longer consistent,
which is what a converted alpha rather than a copied one looks like.

On the six holdout scenes, measured once at the frozen mapping: cross-tier ΔE
0.0229 mean / 0.0358 worst, interior ratio 0.964 mean — re-measured by C9d without
the shadow at ΔE 0.0188 / 0.0313 and interior ratio 0.957. The two worst cells are
the `glass-over-glass` pair, and for a reason §6.4 already names — on the GPU
tier that scene's overlay group is necessarily `dom`, so those cells were always
a mixed-backend comparison, and on the CSS tier both groups are `css`. The tiers
genuinely differ most exactly where the GPU tier is least itself.

**So: coherence can be claimed, in this wording.**

> On Chromium, a group that demotes from the WebGPU texture tier to the CSS tier
> keeps the same material to within 1.3% of its interior level in the mean and 11%
> on the worst measured cell, at a cross-tier OKLab ΔE of 0.0063 mean / 0.0124
> worst over the fitted sets and 0.0188 / 0.0313 over the held-out ones. It is
> not the same rendering — refraction is absent on the CSS tier by contract
> (`refraction: "none"`) — but the material's opacity, tint and frost no longer
> change visibly on demotion, and since C9d removed the dom tier's shadow the
> silhouettes no longer differ by a feature either.

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

### 3.2 The shape axis belonged to the box-shadow, which is now gone

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

**Removed by C9d, on the parent's ruling (Decision Log #32(c)).** The case against
it was the reference: Apple's material has no exterior shadow — C9a measured both
sides at ≈0 outside the contour — so on measurement alone the shadow was a fidelity
defect on three axes at once. The case for it was the repo's effects policy, which
says the fallback *is* the design, and an ambient shadow is what makes an
unfiltered surface read as floating rather than as a flat translucent box, which is
S1's undetectable-failure case. The parent ruled fidelity-first the tiebreaker:
"reads as Apple" outranks "reads as floating", and the tier does not depend on the
shadow for legibility anyway — what carries an unfiltered surface is the tint and
the border, which `e2e/pixel/css-tier-pixels.spec.ts` asserts on unchanged
assertions and still passes.

Re-measured over all 30 cells rather than the sweep's subset, the shipped figures
are the second column above: silhouette IoU 0.9424 / 0.9684 (calibration /
holdout) against 0.6756 / 0.7626 with it, contour p95 2.22 px against 18.67, and
ΔE and cross-tier coherence both better. The seam survives the removal — the
mapping keeps its `shadowOffset`/`shadowBlur`/`shadowAlpha` fields at zero, so a
profile can restore a shadow and the declaration is still derived rather than
special-cased.

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
ratio still sets its own foreground.

**And it is no longer CSS-tier only.** K5 left the GPU tier's half as a parent
question, and Decision Log #32(b) answered it in the order that matters: measure
first, fix only if the defect reproduces. It reproduced, in a shape K5 had not
predicted — the GPU tier published *no* foreground at all, so an app following the
documented `var(--vitrea-foreground, …)` pattern fell back to its own ink. On a
dark-hinted surface over dark page content that measured **WCAG 1.57 against the
4.5 floor**, arrived at from the opposite direction to K5's 1.24 and just as
unreadable. The audit is
`packages/platform-web/e2e/gpu/foreground-audit.spec.ts`; it now measures 10.81.

The fix is one rule with two composite spaces rather than two rules.
`foregroundLevel(material, backdrop, space)` is the shared derivation — the CSS
tier reads it in encoded sRGB, the renderer's material in linear light, and that
difference is the only real one between them (the same difference `cssTintAlpha`
exists for). The crossover, the two ink tokens and accessibility policy's
precedence over the hint all live in one function that either tier calls. Only the
foreground pair is written on the GPU tier; tint, blur and border belong to
whichever tier paints the body, and there that is the canvas.

One thing found while doing it, worth more than the fix: `platform-web` writes the
host's `color` as an inline style, so an app rule on a glass host loses to it
silently. `--vitrea-foreground` is the seam an app is meant to build on, and
building on it means styling something the runtime does not own — a child element.
The demo's disabled control label had to move for exactly that reason, and both
ends now say so.

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

> **Superseded in its direction, its numbers and its recommendation by §5.7
> (W2, 2026-08-30); kept here as the before-state.** The table below was measured
> on the v1 mixed bed, and the settled bed reverses it — the reference's
> transmission *falls* with span (0.210 at 32 px to 0.045 at 96 px) rather than
> rising. Neither reading is a clean measurement of size in any case: the
> estimator runs *across* backdrops, which is exactly where §5.4's tone
> adaptation lives, and an adapting level is indistinguishable from a small
> transmission in it. §5.7 measures the size law *within* a fixed backdrop, where
> it is unambiguous, and lands on a different facet. The parent-impact item this
> section raised is closed there — including the "inverse of the lens gain"
> recommendation below, which is wrong in the direction it names.

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

> **Half superseded by §5.8 (W7, 2026-08-30); the parent-impact item itself still
> stands.** The heading's claim is unchanged — nothing in the runtime reads
> `prefers-color-scheme`, and a host still hands the dark profile in by name. What
> is superseded is the *evidence* this section gives for its middle paragraph. The
> sentence below reporting that the reference's interior "rises monotonically with
> the backdrop across the whole canonical range (0.680 at a backdrop of 0.003…)"
> was measured on the v1 mixed bed, and the settled bed reverses it at the dark
> end: over a backdrop of 0.0117 the light-scheme 44 px capsule reads **0.0117**,
> byte-identical to its own background, not 0.68. So the reference *does* respond
> to the backdrop, continuously and size-gated, and C9a's inversion was wrong in
> its direction rather than in its existence. The mechanism is measured and built
> in §5.8. Kept here as the before-state, as §4.1 is.
>
> The two findings are compatible and the distinction is the useful part: the
> **colour scheme** sets the material's neutral (0.809 against 0.055 over the same
> bright checkerboard, which this section measured correctly), and **backdrop
> adaptation** moves the material away from that neutral toward what is behind it.
> C9a saw the first and could not see the second, because the bed it had was
> caught mid-adaptation on exactly the cells where the second one lives.

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
| shape | silhouette IoU | ≥ 0.82 | 0.9700 | 0.9787 |
| shape | contour distance mean | ≤ 2.50 px | 0.3348 | 0.3337 |
| shape | contour distance p95 | ≤ 5.00 px | 1.0000 | 1.4142 |
| perceptual | SSIM mean | ≥ 0.88 · **UNMET ×3 (§5.27)** | 0.8647 | 0.8305 |
| perceptual | OKLab ΔE mean | ≤ 0.07 · **UNMET ×1 (§5.27)** | 0.0329 | 0.0760 |
| perceptual | OKLab ΔE p95 | ≤ 0.17 · **UNMET ×4 (§5.27)** | 0.1726 | 0.1909 |
| perceptual | edge-weighted mean | ≤ 0.11 | 0.0337 | 0.0682 |

> **Re-measured on the FROZEN ACTIVE bed (2026-09-01).** The enforced suite gates
> **six profiles**: the two light-standard tables in this section and §5.1, the two
> accessibility tables in §5.6, and the dark pair adopted in §5.28. Every bound and
> every observation column in this section and in §5.1 is now what
> `packages/calibration/test/adopted-thresholds.test.ts` enforces against
> `results/matrix.json`, so the file's own doctrine holds again: a reviewer can
> hold that file beside this table and diff the two by eye. Amended rows cite the
> section that adopted them; rows the frozen bed cannot meet are marked UNMET
> with their per-cell floors in §5.27. The figures below are the frozen bed's,
> not the retired inactive bed's, and they moved substantially — the retired
> bed's numbers are preserved in `results/2026-08-30-inactive-bed-matrix.json`.

*The observation columns above were re-measured on the **settled** reference bed
(2026-08-30). The v1 bed's stability check spanned milliseconds while Apple's
material adapts its tone over seconds, so it recorded a mixture of settled and
mid-adaptation states; the harness now dwells and converges, and every cell is
attested by paired independent runs. The adopted **bounds** did not move — not
one digit — but the worst cal+val figures they were compared against did, most
visibly SSIM (0.9113 → 0.9046 at 1×) and ΔE mean (0.0247 → 0.0533), because the
settled reference is darker on every adapting component. Two scenes moved far
enough to fail, and they are §5.4.*

*Correction: the ΔE p95 cal+val cell originally read 0.1409, which is the dark
profile's figure; this table is the light profile, whose matrix value is 0.1070.
The gate was derived with headroom over both, so the threshold is unaffected.*

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
- ~~**A dom-tier shape threshold.**~~ **Proposed by C9d.** K5 declined it because
  the axis measured the tier's `box-shadow` rather than its geometry, and gating a
  quantity that read 0.68 with the shadow and 0.94 without it would have been
  gating a design decision nobody had taken. The parent took it (Decision Log
  #32(c)), the shadow is gone, and the axis now measures geometry — so it is in the
  dom-tier table below.

### Dom tier, `apple-macos-26.5-1x-light-standard`, Chromium, `renderer: css`

Added by K5, on the same rule as the texture tier's — **bounded by the holdout
numbers, not the calibration ones** — and extended by C9d with the shape axis the
shadow's removal made meaningful.

| axis | metric | proposed | worst cal+val | worst holdout |
| --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.85 | 0.9622 | 0.9653 |
| shape | contour distance mean | ≤ 2.00 px | 0.5807 | 0.6668 |
| shape | contour distance p95 | ≤ 7.00 px · **amended §5.15** | 5.0000 | 5.0000 |
| perceptual | SSIM mean | ≥ 0.90 · **UNMET ×4 (§5.27)** | 0.7950 | 0.6883 |
| perceptual | OKLab ΔE mean | ≤ 0.08 | 0.0422 | 0.0719 |
| coherence | cross-tier OKLab ΔE mean | ≤ 0.05 | 0.0258 | 0.0403 |
| coherence | interior level, GPU ÷ CSS | 0.80 … 1.25 · **UNMET ×4 (§5.27)** | 0.890 … 1.635 | 0.796 … 1.265 |

The shape rows carry the texture tier's own well-conditioned-cell predicate
unchanged (`silhouetteAreaNative ≥ 0.95 ×` the declared component area), for the
same reason: the extractor, not the geometry, is what the excluded cell measures.
The bounds are looser than the texture tier's despite the dom tier scoring *better*
on holdout IoU — a converted material through an engine's own blur is not a
quantity to hold to vitrea's shader math, and the holdout figure is six scenes.

Four things about this table are deliberate.

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
remains their only evidence — still open, and now carried as an unchecked item in
`docs/doperpowers/specs/c9d-release-checklist.md`.

**Both holdout observation columns post-date the freeze the perceptual rows were
set against.** The shape rows are C9d's, on an axis the `box-shadow` removal made
meaningful; the perceptual *observations* moved across that same removal in the
Decision Log #32(c) re-measure — worst holdout SSIM 0.9131 → 0.9205, worst
holdout ΔE mean 0.0606 → 0.0560. The proposed bounds predate it unchanged (SSIM
≥ 0.90 and ΔE ≤ 0.08 both before and after), so no constant moved to produce
these rows and no gate was loosened to accommodate them.

### 5.1 The 2× tables, adopted 2026-08-29

W1 of the post-v1 wave widened the bed to six native profiles and re-measured
every one of them (`2026-08-29-w1-g3-measurement.md`). The user adopted its
`apple-macos-26.5-2x-light-standard` proposals as written, on the same doctrine
as the 1× tables above: per cell, per tier, **bounded by the holdout column**.
Both are enforced in `packages/calibration/test/adopted-thresholds.test.ts`
beside the 1× tables, which are unchanged in every digit.

#### Texture tier, `apple-macos-26.5-2x-light-standard`

| axis | metric | adopted | worst cal+val | worst holdout |
| --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.85 | 0.9519 | 0.9784 |
| shape | contour distance mean | ≤ 5.00 device px | 0.4677 | 0.6411 |
| shape | contour distance p95 | ≤ 10.0 device px | 3.0000 | 3.0325 |
| perceptual | SSIM mean | ≥ 0.93 · **UNMET ×4 (§5.27)** | 0.8897 | 0.8762 |
| perceptual | OKLab ΔE mean | ≤ 0.07 · **UNMET ×1 (§5.27)** | 0.0331 | 0.0760 |
| perceptual | OKLab ΔE p95 | ≤ 0.17 · **UNMET ×4 (§5.27)** | 0.1726 | 0.1909 |
| perceptual | edge-weighted mean | ≤ 0.12 | 0.0340 | 0.0682 |

#### Dom tier, `apple-macos-26.5-2x-light-standard`, Chromium, `renderer: css`

| axis | metric | adopted | worst cal+val | worst holdout |
| --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.85 | 0.9643 | 0.9674 |
| shape | contour distance mean | ≤ 4.00 device px | 1.134 | 1.2546 |
| shape | contour distance p95 | ≤ 10.0 device px · **amended §5.26** | 9.4083 | 10.0000 |
| perceptual | SSIM mean | ≥ 0.92 · **UNMET ×4 (§5.27)** | 0.8480 | 0.7990 |
| perceptual | OKLab ΔE mean | ≤ 0.08 | 0.0412 | 0.0719 |
| coherence | cross-tier OKLab ΔE mean | ≤ 0.05 | 0.0259 | 0.0411 |
| coherence | interior level, GPU ÷ CSS | 0.80 … 1.25 · **UNMET ×4 (§5.27)** | 0.891 … 1.638 | 0.797 … 1.266 |

The shape rows carry the same well-conditioned-cell predicate, with the declared
area scaled by the square of the backing scale — `scenes.json` declares
components in points and a 2× silhouette is measured in device pixels, so an
unscaled comparison would clear the predicate four times over and stop biting at
exactly the scale where the extractor is most likely to be doing something
interesting. Neither 2× light table excludes a single cell under it.

**Three movements, each measured rather than inherited.** This is the whole
reason the 2× tables are not a copy of the 1× ones with a scale note attached:

- **The colour bounds are the 1× bounds unchanged, because the measurements
  are.** Worst holdout ΔE mean is 0.0546 at 2× against 0.0548 at 1×; ΔE p95
  0.1333 against 0.1337; across the 24 light cells of each scale the ΔE mean
  agrees to within 0.0011. These are scale-free quantities and they behaved like
  it, so importing the bound is the honest move and re-deriving it would have
  been arithmetic dressed up as evidence.
- **The contour bounds are the 1× bounds doubled, because contour distance is a
  device-pixel quantity.** The same geometric error is twice as many pixels at
  twice the sampling density, and the measurements scale with the device pixel
  ratio almost exactly (texture p95 worst 4.0000 → 8.0000 on cal+val, 2.8284 →
  5.6569 on holdout). Doubling the bound holds the *geometry* tolerance
  constant; keeping the 1× number would have silently tightened it by 2×.
- **The SSIM bounds are tighter than 1×'s, deliberately.** SSIM reads
  systematically higher at 2× — +0.014 in the mean, because a fixed pixel window
  covers finer sampling — so the 1× number would have been slack here. The
  bounds are set from the 2× numbers with §5's own ~2–3% margin over the measured
  worst (texture ≥ 0.93 against a worst of 0.9582; dom ≥ 0.92 against 0.9509),
  which is a genuinely stronger gate than 1×'s, not a rounder one.

### 5.2 Coherence is enforced from the matrix, not from prose

The coherence rows were, until W1, the one part of these tables that no test
could hold. They are a **web-against-web** measurement — the two tiers' own
captures, with no fixture in the comparison — and `web-captures/` is not
committed, so nothing in the repository carried the quantity. The adopted-gate
test recorded the bound in a comment and asserted that no cell had a coherence
axis, as a tripwire for the day one did.

Cell schema **4** is that day (wave Decision Log 9). A dom-tier cell now carries
a `coherence` axis measured against its texture twin — the same profile key and
scene rendered through vitrea's shader math instead of the engine's blur —
holding the two quantities the rows need: whole-canvas cross-tier OKLab ΔE mean,
and the interior-level ratio GPU ÷ CSS under the native silhouette. Both bounds
are now enforced per cell, over **both** light-standard profiles, from
`results/matrix.json`.

> **Extended 2026-09-01: the conditioning predicate now carries these rows.** The
> shape rows had always skipped a cell whose silhouette the extractor could not
> resolve; these rows did not, and the inconsistency had a cost. The interior
> ratio samples each tier's level **under the native silhouette**, so a cell whose
> native mask is 2% of its declared region yields a ratio of two degenerate
> samples — which is exactly what `dark-solid__rrect-md__rest` was doing at 1.589
> and 1.855. It was already excluded from the shape rows by the same measurement.
> One rule on both axes; see §5.28. The exclusion is by measurement and never by
> name, and a pin asserts both halves of that.

Four properties of that axis are worth stating, because each is a decision:

- **It belongs to the dom-tier cell.** The pair has one number; storing it on
  both halves would create two records of one quantity that can disagree, and
  would make the direction of the ratio ambiguous. The CSS tier is also the one
  that moves — C9a's >2× `tintAlpha` gap was a renderer constant retuned without
  the CSS mapping following it.
- **It is written by `cli/compare.ts`, the one sanctioned matrix writer.** The
  two tiers are two `compare` invocations into one matrix, so the dom run simply
  reads the texture capture the earlier run left in the same scene directory. No
  second CLI enriches the matrix after the fact, which keeps "what wrote this
  file" a one-word answer.
- **Absent, never zeroed, in both of the ways it can be.** The whole axis is
  absent when the twin capture is not on disk; the ratio alone is absent where
  the native silhouette is empty and there is no shared interior to sample —
  which is the same single scene (`light-solid__rrect-md__rest`) the shape axis
  is absent on, at both scales.
- **The recorded ratio is cross-checked against an independent derivation.**
  Each tier's `material.interiorMeanWeb` is that tier's interior level under the
  same native silhouette, so the ratio is re-derivable from the matrix by
  division; the test requires the two to agree. An axis the gate trusts because
  the gate has no other source for it is not evidence.

### 5.3 What is still not gated, and the one exclusion that moved

> **CORRECTED 2026-09-01.** The paragraph below was true when written and is not
> true now. **Every one of the six profiles carries validation and holdout scenes
> on the frozen bed**, per tier: `1x-dark-standard` and `2x-dark-standard` at
> 18 calibration / 2 validation / 6 holdout, reduced transparency at 10 / 2 / 4,
> increased contrast at 12 / 2 / 4, and the two light-standard profiles at
> 40 / 12 / 20. W1's split extension is what changed it, and it is exactly the
> "approved close" the original paragraph named — the split was given rather than
> the doctrine relaxed.
>
> The consequence followed for all four, in two steps: **both accessibility
> profiles** were gated 2026-08-30 (§5.6), and **the dark pair** was gated
> 2026-09-01 (§5.28), all 28 of its fidelity rows passing on both columns. There
> are now **no ungated profiles**. This section's title — "what is still not
> gated" — survives only for the axes below it, not for any profile.
>
> The original reasoning is kept intact below, because a bound's history is part
> of the claim.

**Four profiles are measured and not gated.** `1x-dark-standard`,
`2x-dark-standard`, `1x-light-reduced-transparency` and
`1x-light-increased-contrast` each declare **calibration scenes only** — no
validation, no holdout. The column every bound in this document is bounded by
does not exist for them, and setting one from a calibration-only measurement
would certify overfitting in the doctrine's own words. This is v1's
dark-provisional reasoning (§5, "Texture tier, dark") transferred unchanged, and
it is the user's decision of 2026-08-29 (wave Decision Log 9) rather than an
omission.

They are not unmeasured, and the distinction matters: their figures are
tabulated in W1's G3 report, and their coherence axis is asserted **present** in
the adopted-gate test — measured, not gated. The approved close is to give them
a split rather than to relax the doctrine: the split is declared per scene, so
extending their native scene sets to include a validation and a holdout scene
earns them one, and gating follows from that.

**The 1× dark checkerboard-capsule exclusion is instrument-scoped, and 2× proves
it.** §5's well-conditioned predicate excludes
`checkerboard__capsule-button__rest` in the dark profile because the extractor
recovers only 88.9% of the declared capsule there — a dark material over black
squares is genuinely indistinguishable from them at 1× sampling. The same scene,
same material, same backdrop **passes the predicate at 2×**: recovery 100.2%,
IoU 0.9538 against 0.8434, contour p95 5.81 device px against 15.0. The v1
figures described the instrument at 1×, not the material, which is exactly what
the predicate was adopted to keep out of the gate — and the 2× cell is the
independent confirmation that the exclusion was scoped correctly. The exclusion
stands at 1×; it does not generalise to the material.

The increased-contrast profile's two checkerboard scenes fail the same predicate
the other way round, recovering 53–57%: there the extractor loses the
*brightened* material over the checkerboard's white squares. Those four cells
(two scenes × two tiers) are named in the test alongside the two dark ones, and
all six are in ungated profiles — **neither light-standard table excludes
anything, at either scale**.

### 5.4 The limitation the adopted gate did not cover — closed by W7

> **REWRITTEN 2026-08-30 by W7.** This section recorded the project's largest
> measured fidelity gap and the seven rows it cost, held out of the gate as a
> labelled known renderer gap. The gap is closed: the axis is built, the rows
> re-entered the gate at their unchanged bounds, and the exclusion was deleted.
> The before-state is kept below in full, because a claim that a gap closed is
> only worth reading beside the gap.

**vitrea now follows Apple's backdrop tone adaptation.** The measurement, the
law and its constants are §5.8; this section records the seven rows and what they
read now.

| profile | tier | scene | row | before | after | adopted bound |
| --- | --- | --- | --- | --- | --- | --- |
| 1x-light | texture | dark-solid__capsule-button__rest | ΔE p95 | 0.6244 | **0.0000** | ≤ 0.17 |
| 1x-light | texture | impulse__capsule-button__rest | ΔE p95 | 0.6633 | **0.0324** | ≤ 0.17 |
| 2x-light | texture | dark-solid__capsule-button__rest | ΔE p95 | 0.6242 | **0.0000** | ≤ 0.17 |
| 2x-light | texture | dark-solid__capsule-button__rest | SSIM | 0.9259 | **1.0000** | ≥ 0.93 |
| 2x-light | texture | impulse__capsule-button__rest | ΔE p95 | 0.6633 | **0.0372** | ≤ 0.17 |
| 2x-light | texture | impulse__capsule-button__rest | SSIM | 0.9200 | **0.9832** | ≥ 0.93 |
| 2x-light | dom | impulse__capsule-button__rest | SSIM | 0.9191 | **0.9812** | ≥ 0.92 |

**Not one bound moved.** The rows were skipped, never loosened, and they now pass
the same numbers they failed. `KNOWN_RENDERER_GAP_EXCLUSIONS` is gone from
`adopted-thresholds.test.ts`, with a dated note where it stood; the perceptual
rows of both light-standard tables now cover every cell of their profile, which
is asserted by count rather than assumed.

The mechanism that produced that cleanup is worth keeping in mind for the next
gap. The exclusion was **data with four properties enforced around it**: every
entry must *still fail* its bound, its quoted figure must match the committed
matrix, it must carry a reason and a tracking pointer, and the class could not
grow beyond the scenes the ruling named. The first of those is what made the
close self-executing — when the axis landed, the rows passed, the test failed and
named the entries, and the fix was to delete them.

<details>
<summary>The before-state, as this section read from 2026-08-30 until W7</summary>

**vitrea does not follow Apple's backdrop tone adaptation.** Apple's material
adapts its appearance continuously to the luminance behind it: a light-scheme
capsule over a black backdrop settles to near-black. vitrea has no such axis —
its material profiles are discrete per colour scheme — so over an extreme
backdrop the reference all but disappears while vitrea keeps drawing a light
capsule. Measured on the settled bed, over `impulse` (black) the reference's
interior level is 0.013 in linear light where vitrea's is 0.631; over
`dark-solid` the reference falls within the extractor's own 0.02 threshold of
its background, so it has no separable silhouette at all.

This is the largest measured fidelity gap in the project and the only thing that
fails an adopted bound. The seven rows were excluded from the gate as a labelled
known renderer gap (user ruling, 2026-08-30, wave Decision Log 11), and the
exclusion was a *distinct class* from §5's conditioning predicate: the predicate
drops rows whose extractor could not find the component, where the number
describes the instrument. These rows were measured perfectly well; what they
recorded was a defect vitrea was known to have. Conflating the two would let a
real gap hide inside a measurement caveat.

</details>

### 5.5 What the settled bed changed about §5's own exclusions

**v1's canonical ill-conditioned cell repaired itself.** §5 argued for the
well-conditioned predicate on `checkerboard__capsule-button__rest` in the dark
profile, where the extractor recovered 88.9% of the declared capsule and produced
the worst shape figures in the whole v1 matrix. On the settled bed that cell
recovers **100.8%** at 1× (IoU 0.9561) and 100.3% at 2× (IoU 0.9543), and it is
gated like any other cell. The v1 exclusion was **instrument-caused** — an
unsettled capture, not a property of dark glass over a checkerboard. The
predicate itself is unchanged and still earns its place; only this example is
retired.

**A new conditioning failure replaced it, in all four standard profiles.**
`impulse__capsule-button__rest` now recovers **0.3%** of its declared capsule on
every standard profile at both scales. That is the same tone adaptation §5.4
describes, seen through the extractor instead of through ΔE: the settled
reference over a black backdrop is nearly invisible, so there is almost no
silhouette to find. Its shape rows are excluded by the predicate — correctly,
since they would measure the extractor — while its perceptual rows are the ones
§5.4 excludes as the renderer gap. Two different exclusion classes on one cell,
for two different reasons, is exactly why they are kept apart.

**`dark-solid__capsule-button__rest` lost its shape axis in the light profiles.**
Same mechanism, one step further: the reference is now within 0.02 of its own
backdrop, so `cli/measure.ts` records the cell with its perceptual axis alone
rather than inventing a shape.

**The 2× `rrect-md` quantization dither.** The settled bed's paired-run
attestation reports this cell reproducing to a maximum of 1/255 on fewer than
0.5% of its pixels rather than byte-identically — a quantization dither in the
capture path, not a settledness failure. It is well inside every bound the cell
is gated on and is recorded here so a future reader does not mistake the one
non-byte-identical attestation for an unsettled capture.

### 5.6 The accessibility tables, adopted 2026-08-30

W1's split extension gave every provisional profile two validation and two
holdout scenes, which is what these tables were waiting for: a bound needs a
binding column, and calibration-only profiles had none. Both are adopted as
proposed and enforced beside the light-standard tables.

#### `apple-macos-26.5-1x-light-reduced-transparency`

| axis | metric | texture | dom |
| --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.87 | ≥ 0.89 |
| shape | contour distance mean | ≤ 1.50 px | ≤ 1.50 px |
| shape | contour distance p95 | ≤ 3.50 px | ≤ 5.00 px · **amended §5.26** |
| perceptual | SSIM mean | ≥ 0.95 · **amended §5.26** | ≥ 0.91 |
| perceptual | OKLab ΔE mean | ≤ 0.04 | ≤ 0.04 |
| perceptual | OKLab ΔE p95 | ≤ 0.08 | ≤ 0.07 |
| perceptual | edge-weighted mean | ≤ 0.10 | ≤ 0.11 |

The tightest table in this document, and that is the measurement rather than
ambition: the reduce-transparency material is nearly opaque on both sides, so
there is very little backdrop left for the two to disagree about — worst holdout
ΔE mean 0.0300 against light-standard's 0.0548.

Two of its rows were **amended post-read** against the frozen active bed, under
Decision Log 18 ruling 2 and recorded in §5.26: texture SSIM 0.96 → 0.95, driven
by a validation cell reading 0.95948, and dom contour p95 3.5 → 5.0, driven by a
HOLDOUT cell reading exactly 5.0. Neither is a pre-registered bound and neither
was fitted to — both were read once off a bed frozen before they were measured,
and the bound then moved to the reading. Every other row here is unchanged, and
this profile carries **no** floored rows: it meets everything it now claims.

#### `apple-macos-26.5-1x-light-increased-contrast`

| axis | metric | texture | dom |
| --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.85 | ≥ 0.80 |
| shape | contour distance mean | ≤ 1.80 px | ≤ 2.60 px |
| shape | contour distance p95 | ≤ 11.50 px · **amended §5.15** | ≤ 5.50 px |
| perceptual | SSIM mean | ≥ 0.86 | ≥ 0.83 |
| perceptual | OKLab ΔE mean | ≤ 0.06 | ≤ 0.07 |
| perceptual | OKLab ΔE p95 | ≤ 0.10 | ≤ 0.09 |
| perceptual | edge-weighted mean | ≤ 0.17 | ≤ 0.18 |

Its texture contour p95 was **amended 3.2 → 11.5** by §5.15's declared round-two
fit, driven by `photo__capsule-button__rest-tint-orange` at 8.20 with a mean of
1.159 and an IoU of 0.9768. §5.15 flagged that row as the weakest in this document
and it stays flagged: a gate that would rather drop the row than widen it
nearly four-fold has a good argument. It survives because the driving cell is
single-bodied and clears the area floor — an outline difference, not a displaced
surface — and because this profile, like reduced transparency, carries **no**
floored rows.

The loosest, for two measured reasons. Its reference is the **coupled** state —
macOS force-enables reduce transparency with increase contrast, so no
single-flag reference exists to capture (Decision Log 8) — and vitrea's
accessibility material under-occludes against it. That gap is on the material
axis, which is not gated; what reaches this table is its perceptual shadow. Its
shape rows also gate the fewest cells of any adopted table: three of its eight
scenes per tier fail the conditioning predicate, because the brightened material
is lost over the checkerboard's white squares.

**The dark pair stays ungated.** `1x-dark-standard` and `2x-dark-standard` have
a split now too, but their cross-tier figures were re-measured across the
press-glow fix and their tables would be adopted from numbers that had just
moved. Their proposed tables are in W1's G3 measurement report, ready to adopt
once that settles. They remain fully measured — both tiers, coherence axis
present — and named here rather than omitted.

### 5.7 The size law, measured (W2, 2026-08-30)

**Added by W2** of the post-v1 wave
(`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`), whose purpose was §4.1's
parent-impact item and the coverage matrix's §3.2: Apple derives five facets from
a surface's size and vitrea implemented one. Every figure below is measured
against the **settled** six-profile bed, and every constant is fitted against
calibration cells only, with the holdout column read once after the configuration
was frozen.

**No adopted bound was edited, added or removed by this section.**

#### What the reference actually does with size

Two things have to be held apart, and §4.1 did not hold them apart because the
mixed v1 bed could not.

**Across backdrops**, the reference's interior level barely follows the backdrop
at all, and follows it less as the surface grows: solving the level jointly over
the checkerboard (backdrop 0.50) and photo (0.21) cells of one component gives a
transmission of 0.210 at a 32 px span, 0.070 at 44 px and 0.045 at 96 px, toward
a common level near 0.62–0.65. That reads like "a larger size is more opaque" —
and it is **not safe to fit against**, because the same two cells are where
backdrop tone adaptation lives (§5.4), and tone adaptation moves the level toward
a target regardless of the backdrop, which is indistinguishable from a small
transmission. §4.1 reported the *opposite* direction (0.88 at 32 px falling to
0.56 at 96 px) from the unsettled bed; neither number is a clean measurement of
size, and the corrected direction agrees with Apple's prose rather than
contradicting it.

**Within one fixed backdrop**, where tone adaptation is a constant, the size
dependence is unambiguous. Over the checkerboard the fraction of the backdrop's
own contrast that survives the material — `interiorStdDevNative` ÷
`interiorStdDevBackdrop`, the quantity `interiorLevel`'s own note calls the
material's frosting strength — falls monotonically with the span, in every
profile that can measure it:

| profile | 32 px | 44 px | 44 px (group) | 96 px |
| --- | --- | --- | --- | --- |
| `1x-light-standard` | 0.244 | 0.230 | 0.270 | 0.144 |
| `2x-light-standard` | 0.261 | 0.247 | 0.266 | 0.081 |
| `1x-dark-standard` | — | 0.132 | — | 0.068 |
| `2x-dark-standard` | — | 0.119 | — | 0.046 |
| `1x-light-reduced-transparency` | — | 0.160 | — | 0.095 |

and the backdrop **correlation** falls with it (1× light: 0.634 → 0.606 → 0.475;
2× light: 0.599 → 0.572 → 0.365; 1× dark: 0.434 → 0.253). Correlation is the
useful second observable because, under an affine model, it depends on the
material's kernel alone and not at all on its alpha — so a fall in both says the
material is not merely passing less, it is passing it more diffusely.

Six independent profile × span comparisons, one direction. `1x-light-increased-
contrast`'s checkerboard cells are excluded: they fail §5's conditioning
predicate (53–57% recovery), so their statistics describe the extractor.

#### Which facet, and the one discriminator the bed offers

The checkerboard and the photo disagree in a way that tells them apart. The
checkerboard's structure sits at one 16 px period and its surroundings have the
same mean as its interior; the photo is broadband and its surroundings do not.

- Over the checkerboard the retained contrast falls 41% from 32 px to 96 px while
  the interior **level** stays put (0.607 → 0.605 → 0.641).
- Over the photo the retained contrast barely moves between 44 and 96 px (0.546 →
  0.544) while the level converges toward the neighbourhood (0.585 → 0.628).

A larger alpha would have moved both backdrops' contrast together and pulled both
levels toward the tint. A wider kernel moves exactly what moved: it kills the
checkerboard's one period without touching its mean, and it pulls the photo's
interior toward backdrop the mask does not cover. The evidence favours
**scattering** over opacity — which is Apple's own third consequence, "a softer
scattering of light".

#### The coupling

One mechanism, so one curve. `sizeThickness(span)` is a smoothstep from
`sizeSpanMin` to `sizeSpanMax` in the material profile, and every
thickness-derived facet is a gain on it and on nothing else: the lens
(`lensSizeGainMax`), the scattering (`sizeScatterGainMax`), the occlusion
(`sizeOcclusionGain`) and the inner shadow (`sizeShadowGainMax`). Below
`sizeSpanMin` the whole law is exactly inert, which is what makes it additive
rather than a global retune.

It reaches the GPU tier **per pixel**: the factor is resolved per surface on the
CPU and rides the field pass's `aux` channel through the group's union, so a
44 px button and a 280 px platter in one `GlassEffectContainer` read as different
thicknesses from one field pass. It reaches the CSS tier per surface, through the
same two functions, from the host's own measured border box. The constants live
in `@vitrea/renderer-webgpu`'s `DEFAULT_MATERIAL_PROFILE`, are patchable like
every other optic, and are mirrored in `@vitreajs/vitrea-web`'s
`MATERIAL_SOURCE_SIZE` with `packages/calibration/test/tier-coherence.test.ts`
pinning the two in both directions.

**The law folds under the accessibility policy**, through the profile's own
refraction ladder read at the accessibility cap (1 / 0.45 / 0). This was measured
rather than designed in: landed unfolded, the law improved every light-standard
cell and pushed both accessibility profiles' large-span cells past their adopted
ΔE bounds. The reference says why — under reduce-transparency its material is
nearly opaque and its interior level is *flat* in span (0.947 at 44 px, 0.953 at
96) — and vitrea's accessibility fold already under-occludes against it (W1's
Surprise), so extra simulated depth compounds an error rather than closing one.
Deliberately the accessibility cap and not the *resolved* one: a group demoted to
a CSS proxy is drawing the same material, and being demoted is not a statement
about how thick it is.

#### The fit

Fitted on the light-standard calibration cells, against this package's declared
objective (mean of |Δ interior mean| + |Δ interior stdDev| + |Δ rim peak|, linear
light), with SSIM and ΔE read as checks.

**The band, 32…96 px.** Set from the reference's own movement above, not from the
objective. It was 28…420 while it served the lens alone and nothing had measured
it, which put the entire canonical range inside the first 17% of the curve. Over
`sizeSpanMax` ∈ {420, 160, 128, 96, 64} the objective reads 0.1762 / 0.1718 /
0.1700 / 0.1670 / 0.1633 — monotone, and it would rather have 64. **Declined,
with the reason recorded:** that gain comes entirely from the interior-level
term, whose residual is the tone-adaptation gap W7 is chartered to close, so a
band fitted to 64 would be using the size law as a proxy for a mechanism vitrea
does not have — against the reference's own measurement of where its
size-dependence lives — and W7 would have to unpick it.

**The inner shadow, 1.4.** Fitted on the calibration **rest** cells, where the
grid 1.0 / 1.2 / 1.4 / 1.6 / 1.8 / 2.2 reads 0.1577 / 0.1551 / 0.1533 / 0.1530 /
0.1529 / 0.1531. 1.4 through 2.2 is one flat region 0.25% wide; 1.4 is the point
inside it that costs the checks least (ΔE 0.01282 against a baseline 0.01290;
SSIM 0.9671 against 0.9689) and it is the per-cell minimum on both
well-conditioned span-96 rest cells. The pressed cells prefer 2.4 monotonically
and are excluded from the fit on §6.3's grounds: their native side carries no
press pose, so they compare two different states and cannot arbitrate a material
constant.

**The scattering, 1 — implemented and not identifiable.** The objective is flat
to 1.00× over gains 1…6 and best at 1. That is not the backdrop chain's depth
talking, which was the obvious suspicion: on the 320×200 canonical canvas the
chain stops at a 20×12 level, capping the reachable σ at 1.2× the body's, so the
sweep was re-run with `MIN_LEVEL_EXTENT` temporarily lowered from 8 to 4 (raising
the cap to 2.4×) and the grid stayed flat to 1.00× and stayed best at 1. The
architectural constant was restored. This is §6.1's situation on a second axis:
the canonical fixtures cannot resolve the quantity, so it ships at the identity
with the mechanism in place. **What it would need:** a canonical canvas large
enough for a deeper chain, which is a `scenes.json` change and therefore a scope
question rather than a re-run.

**The occlusion, 0 — implemented and fitted to a boundary.** Unlike the
scattering this one has real leverage against it: over 0 / 0.15 / 0.30 / 0.50 the
objective rises monotonically 0.1680 → 0.1849 → 0.2018 → 0.2240, a 1.33× spread,
with the mean term, ΔE and SSIM all worsening together. The diagnosis is not a
tuning failure. vitrea's interior sits 0.16–0.19 above the reference's at *every*
span, because the reference's level is set by backdrop tone adaptation toward
roughly 0.63 while vitrea lerps toward a white tint — so making a large surface
more opaque can only take it further away. The facet is Apple's, stated three
times over (§3.2); the axis that would let it fit is W7's, and the seam is built
so W7 can fit it without building anything.

#### Fit, validation and holdout

Measured once, on the frozen configuration, over the full regenerated bed — all
six profiles, both tiers, fresh captures, 168 cells. Worst cell per set, with the
pre-W2 figure first. The two defect-excluded scenes' perceptual rows (§5.4) are
left out of these worsts, as the gate leaves them out.

| profile | tier | set | ΔE mean | SSIM | edge-weighted |
| --- | --- | --- | --- | --- | --- |
| `1x-light-standard` | texture | calibration | 0.0496 → **0.0495** | 0.9088 → **0.9088** | 0.0573 → **0.0571** |
| | | validation | 0.0533 → **0.0532** | 0.9046 → **0.9046** | 0.0537 → **0.0535** |
| | | holdout | 0.0548 → **0.0547** | 0.9026 → **0.8934** | 0.0923 → **0.0845** |
| `2x-light-standard` | texture | calibration | 0.0496 → **0.0495** | 0.9592 → **0.9565** | 0.0537 → **0.0534** |
| | | validation | 0.0533 → **0.0532** | 0.9582 → **0.9578** | 0.0525 → **0.0523** |
| | | holdout | 0.0546 → **0.0545** | 0.9593 → **0.9566** | 0.1002 → **0.0941** |
| `1x-light-reduced-transparency` | texture | calibration | 0.0105 → **0.0115** | 0.9851 → **0.9849** | 0.0298 → **0.0332** |
| | | validation | 0.0067 → **0.0068** | 0.9611 → **0.9609** | 0.0257 → **0.0258** |
| | | holdout | 0.0300 → **0.0312** | 0.9883 → **0.9843** | 0.0807 → **0.0847** |
| `1x-light-increased-contrast` | texture | calibration | 0.0177 → **0.0186** | 0.9359 → **0.9314** | 0.0646 → **0.0677** |
| | | validation | 0.0115 → **0.0115** | 0.9253 → **0.9252** | 0.0451 → **0.0451** |
| | | holdout | 0.0463 → **0.0474** | 0.8864 → **0.8812** | 0.1445 → **0.1479** |

The dom tier is **unchanged in every digit**, on every profile and every set, and
that is a result rather than an omission: the two facets the CSS tier carries fit
to the identity, and the two that moved are GPU-tier features the CSS tier has no
counterpart for. Both dark profiles' texture figures move only in the fourth
decimal and improve slightly (worst calibration ΔE mean 0.0216 → 0.0206 at 1×).

Read the light-standard rows as the claim: **every ΔE and every edge-weighted
figure improves or holds, and SSIM pays for it.** The improvement concentrates
exactly where the law acts — on the 1× texture tier, ΔE mean falls 0.0466 →
0.0435 on `checkerboard__rrect-lg__rest` (holdout, span 160), 0.0159 → 0.0142 on
`checkerboard__rrect-md__rest`, 0.0247 → 0.0222 on `impulse__rrect-md__rest`, and
edge-weighted falls on every span-96-and-above cell — while every span-32 cell is
byte-unchanged, which is the inertness property observed rather than asserted.
The accessibility profiles pay a little and stay inside their bounds, which is
the fold working: a weakened law, not an absent one.

#### These figures survive the author tint landing beside them

W3's tint (Decision Log 12) landed in the same cut and touches the same seams —
the material profile's constants, the optics pass, and the CSS tier's mirror — so
the bed above was re-verified rather than assumed after the two were composed.
Four scenes spanning the law's whole band (`checkerboard__rrect-sm__rest` at the
floor, `photo__capsule-button__rest` mid-curve, `checkerboard__rrect-md__rest` at
the ceiling, and `photo__toolbar-group__rest` for the group case) were re-measured
on both tiers against the committed matrix: **72 measured values, every one
bit-identical.** The tint's zero-strength identity is real, so no cell in the
matrix describes a configuration that no longer exists, and the holdout column
above was not re-spent.

The composition contract holds in both directions, and the two features meet in
three places. In the **optics pass** the tint decides what colour the tint layer
is made of and the size law decides that layer's *alpha* and the blur beneath it,
so `mix(backdrop, tintColour, tintAlpha)` takes one operand from each and neither
can move the other's. In the **field pass** they take one per-pixel channel each
(`aux.z` the thickness factor, `aux.w` the tint strength) out of an instance
struct widened from 16 floats to 18 for the purpose. On the **CSS tier** the
tint is folded into `optics.tint` before `cssTierDeclarations` runs and the size
law then moves `blurRadius` and `tintAlpha` on top of it — the same order the
shader takes. The one place the two genuinely interact is the right way round:
the tone map reads `backdrop` *after* the scattering has been applied to it, so a
large surface's tint maps against the diffused light a reader actually sees
through it rather than the sharp light nobody does.

#### Three margins to watch

Nothing fails, and two of these are narrower than they were.

- **Cross-tier interior ratio, light profiles: 0.844 → 0.818 against a gated
  floor of 0.80.** On `photo__glass-over-glass__rest` (holdout). This is the
  size law's coherence cost, and its mechanism is plain: the GPU tier's two
  active facets deepen a large surface and the CSS tier has no counterpart for
  either, so the pair diverges precisely on the surfaces the law acts on.
  Closing it means giving the CSS tier an inner shadow, which is a new tier
  feature with its own calibration question, not a constant.
- **Texture-tier SSIM, `1x-light-standard` holdout: 0.9026 → 0.8934 against
  ≥ 0.88.** On `checkerboard__glass-over-glass__rest`. SSIM falls monotonically
  with the shadow gain across the whole sweep; 1.4 is the low end of the flat
  region partly for this reason.
- **The dark profiles' cross-tier interior ratio improved**, which is worth
  saying because it was W1's standing watch item: 1.2412 → 1.1998 at 1× and
  1.2377 → 1.1956 at 2×, against a ceiling of 1.25. The retune moved the dark
  cells *away* from the ceiling rather than through it.

#### What this does not close

Two of Apple's five size-derived facets remain absent rather than inert.
**Size-gated light/dark adaptation** (§3.2, row 3) is measurable on this bed and
striking — over the `dark-solid` backdrop the 44 px capsule adapts until it has
no separable silhouette at all, while the 96 px rrect sits at 0.454 and does not
adapt; over `impulse` the same pair reads 0.013 against 0.412 — but it is a gate
on an adaptation vitrea does not perform, so it belongs to W7 with the axis it
gates, and W7 can key it off `sizeThickness` when it lands. **Ambient colour
spill on large surfaces** (row 4) needs sampling beside a surface rather than
behind it, and is untouched.

> **CLOSED, the first of them, by W7 (2026-08-30) — see §5.8.** The size-gated
> adaptation is now implemented on both tiers and it does key off `sizeThickness`,
> exactly as this paragraph anticipated: the thickness enters the adaptation
> curve's *argument*, so a thicker surface reads its backdrop as brighter and
> holds its own appearance longer. Measured on the same two cells this paragraph
> quotes, vitrea's 96 px surface over `dark-solid` now reads 0.4545 against the
> reference's 0.4542 and its 44 px capsule is within a code step of the backdrop.
> **Ambient colour spill remains untouched.**
>
> W7 also settled one of this section's own numbers from the other direction. The
> band 32…96 is now pinned twice over: W2 set it from the reference's
> transmission, and the tone axis independently requires it — a band ending at 64
> lifts the 44 px capsule out of full adaptation (ΔE p95 0.0000 → 0.1560) and one
> ending at 128 over-adapts the 96 px surface (0.0199 → 0.1139). The objective's
> 3% preference for 64 survives W7 and is declined again, now for a second reason
> as well as the first.

### 5.8 Backdrop tone adaptation, measured (W7, 2026-08-30)

**Added by W7** of the post-v1 wave
(`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`), whose purpose was §5.4's
gap: Apple's material takes on the tone of a dark enough backdrop instead of
sitting in front of it, and vitrea had no such axis at all. Every figure below is
measured against the **settled** six-profile bed, every constant is fitted
against calibration cells only, and the holdout column was read once after the
configuration was frozen.

**No adopted bound was edited, added or removed by this section.** Seven rows
that had been held out of the gate re-entered it and pass (§5.4).

#### The observable that isolates the adaptation from everything else

The obvious measurement is the wrong one. A material's interior level over a
backdrop is transmission and tint and adaptation together, and this bed's
backdrops differ in structure as well as in level, so reading adaptation off the
level directly is the same confusion §4.1 fell into from the other side.

There is one quantity in this bed that cancels all of it: the **separation
between the light and the dark reference over the same backdrop, on the same
component**. Under an adaptation that moves the material's tint toward its
backdrop, that separation is `(1 − α)(1 − a)(tint_light − tint_dark)` — so the
transmission `α`, the backdrop's own structure, and each scheme's tint all cancel,
and what survives is `a`. Normalised at the checkerboard, where nothing adapts:

| backdrop (linear) | span 44 px | span 96 px |
| --- | --- | --- |
| 0.5000 (`checkerboard`) | 0.000 | 0.000 |
| 0.205 / 0.216 (`photo`) | 0.030 | 0.028 |
| 0.0117 (`dark-solid`) | **1.000** | **0.256** |
| 0.0049 (`impulse`) | **1.000** | — |

The 2× bed reproduces every one of those to three decimals — 0.2553 against
0.2556 on the one figure that is not a boundary — which is a reproducibility
check the axis gets for free from the widened bed.

Two facts follow, and the whole design is downstream of them. The adaptation is
**off across the entire ordinary range** and turns on only below roughly a fifth
of the backdrop scale, so it cannot disturb a cell that already passes. And it is
**size-gated hard**: the same backdrop, the same material, 1.000 against 0.256.

#### The law

One curve, four constants, in the material profile beside the size law's:

```
x = backdropLuminance + backdropToneSizeBias · sizeThickness(span)
a = backdropToneMax · (1 − smoothstep(backdropToneLow, backdropToneHigh, x))
```

`backdropToneMax` 1, `backdropToneLow` 0.02, `backdropToneHigh` 0.14,
`backdropToneSizeBias` 0.09.

The size term enters the curve's **argument** rather than its amplitude: a
thicker surface reads its backdrop as brighter than it is, which is what more
material between the viewer and the backdrop means. That is not a stylistic
choice between two equivalent forms. An amplitude gate (`a = A(span) · f(bd)`)
fits the two calibration points by construction and then predicts 0.256 for the
96 px surface over `impulse`, where the argument form predicts 0.34; the
validation cell reads 0.356.

`a` then moves the material by converging its **interior** on the backdrop's own
tone — `mix(interior, tone, a)` — which the renderer expresses as a (colour,
alpha) pair so that one composite does it:

```
tint'  = (tint · (1 − a) · α + tone · a) / α'        α' = α + a(1 − α)
```

At `a = 1` the tint is the tone and the alpha is 1, so the surface *is* its
backdrop's tone and keeps only its rim, its inner shadow and its lensing. That is
what the reference does: `dark-solid__capsule-button__rest` is byte-identical to
its own background in every standard profile, at both scales, in **both colour
schemes**.

Solving the pair rather than lerping the colour and the alpha separately is
load-bearing and was measured, not reasoned: lerped independently, a partially
adapted surface gets *lighter* than the one it started from — more opaque toward a
tint that is still mostly neutral — and the 96 px cells caught it at once
(interior 0.4545 → 0.5179 against a reference of 0.4542).

**Everything that says "a surface is here" fades on the same factor** — the rim,
the specular, the inner shadow and the highlight pass's sweep, all by `1 − a`. That
is not symmetry for its own sake; it is a calibration cell rather than an
inference, because `dark-solid__capsule-button__rest` is byte-identical to its own
background *rim included*, and a material that has taken its backdrop's tone has
no lit edge to show because there is no light in front of it to show one with.

It was also invisible until this axis existed, which is the more useful half of
the finding. A rim of up to 130/255 had been sitting unnoticed inside a bright
capsule body; with the body gone it was a white outline around a surface meant not
to be there — 60 to 595 pixels past 2/255 depending on the pass, against a cell
whose ΔE p95 already read 0.0000. W3 recorded the same class from the other
direction (a bypass that happens to match its expected output is one feature away
from being visible); this is the version where the term is real and merely hidden.
Folding all four took `dark-solid__capsule-button__rest` on the texture tier to
**OKLab ΔE max 0.0000 and SSIM 1.0000** — vitrea's light-scheme capsule over that
backdrop is now byte-identical to the reference capture, which is the only cell in
this document that has ever read that way. On the dom tier the same cell's ΔE max
went 0.6764 → 0.0051, within 2/255 at every pixel.

**The scheme semantics.** The axis is *within* a colour scheme: the profile sets
the neutral and this moves away from it, toward whatever is actually behind the
surface. So the dark profile runs the same law with the same constants and does
not double-adapt — and the bed confirms it, because over `dark-solid` and
`impulse` the light and dark references are the **same pixels**. A crossover
between two scheme tints would have been the other design, and it would have had
nothing left to say about a dark material over a darker backdrop.

**Where the backdrop is sampled, and why it is one number per group.** The tone a
group adapts onto is resolved once, by the host, and handed to both tiers: X6's
declared hint where the app gave one (its luminance, or the coarse reading of a
`dark`/`light` tone), otherwise the linear-light average of the backdrop texture
the app supplied, and otherwise nothing — with nothing meaning *no adaptation* on
either tier rather than a guessed level.

Per group rather than per pixel is the referee's ruling, not a convenience. The
first build read the backdrop per pixel on the GPU tier and one average on the
CSS tier, which is the natural capability of each; over the `impulse` backdrop
that put the two tiers at a cross-tier interior level ratio of **79** against a
gated band of 0.80…1.25. The two tiers blur their backdrops in *different spaces*
— this renderer in linear light, `backdrop-filter` in the encoded one — so a fully
adapted material that still transmits shows different pixels on the two tiers by
construction. A material that shows a colour is tier-independent. Resolved once
per group, the same cell reads a ratio of **1.000**.

What that costs is stated rather than hidden: a surface over a locally dark corner
of a brightly-averaged backdrop source does not adapt to the corner. The bed
cannot see the difference (its only spatially varying backdrops sit far above the
curve's high edge, where the adaptation is zero either way), so nothing here is
fitted to it — it is a capability limit with a capture that would test it: a scene
whose backdrop is dark under the component and bright elsewhere.

#### The fit

Fitted on the light-standard calibration cells, against this package's declared
objective (mean of |Δ interior mean| + |Δ interior stdDev| + |Δ rim peak|, linear
light), with SSIM and ΔE read as checks. Every constant was set from the
reference-side measurement above **first** and then confirmed against the
objective, and the objective agrees with all four:

| axis | grid | best | spread |
| --- | --- | --- | --- |
| `backdropToneHigh` | 0.08 / 0.11 / 0.14 / 0.17 / 0.20 | **0.14** | 1.16× |
| `backdropToneSizeBias` | 0.05 / 0.07 / 0.09 / 0.11 / 0.13 | **0.09** | 1.24× |
| `backdropToneLow` | 0 / 0.01 / 0.02 / 0.03 / 0.04 | **0.02** | 1.04× |
| `backdropToneMax` | 0 / 0.5 / 0.8 / 1 | **1** | 1.10× |

The axis switched off (`backdropToneMax` 0) is the pre-W7 configuration exactly,
and it reads the objective 0.16372 — W2's own closing figure, reproduced. On:
**0.14887**, a 9.1% improvement, with both checks moving the same way (ΔE 0.01299
→ 0.00796, SSIM 0.9620 → 0.9667). It is monotone in the strength, which is the
shape a real mechanism has and a fitted artefact usually does not.

**The dark end of the band is not identifiable from this bed, and the fit says
so.** The reference's backdrops jump from 0.0117 to 0.205 with nothing in between,
so `backdropToneLow` is bounded only by "at or below the darkest calibration
backdrop" — its grid is flat to 1.04×. What the two dark backdrops *do* pin is the
curve's slope near zero, because the 96 px surface reads 0.256 at 0.0117 and 0.356
at 0.0039: a measured intermediate rather than a step. Closing the rest of it
needs native captures at intermediate backdrop levels — three or four solid
backgrounds between linear 0.01 and 0.20 — which is a `scenes.json` addition and
therefore a scope question rather than a re-run.

One coincidence worth naming rather than leaving for a reader to find: the 44 px
capsule's effective backdrop over `dark-solid` is 0.0117 + 0.09 × 0.0923 =
**0.0200**, and `backdropToneLow` is 0.02. Its full adaptation is therefore exact
but not margined. That is the law working rather than a fit to an edge — a 48 px
capsule would adapt slightly less, which is what a continuous size gate means —
and the objective picks 0.02 independently of it. But a future retune that moves
`sizeSpanMin`/`Max` moves this too, which is the coupling §5.7's band note now
records from the other side.

#### Continuity

The acceptance asks for a continuous adaptation with intermediate backdrops
measured rather than only the extremes, and this bed can only half answer it. What
is measured on the reference is three distinct levels across the transition —
0.0039, 0.0117 and 0.205 — with the response strictly between at the middle one.
That establishes a transition rather than a step, and it fixes the slope near
zero; it does not establish the shape of the knee, which is the paragraph above.

What *is* measured across the whole range is vitrea's own response, in three
places, because a discontinuity in the thing we built is the failure this axis is
most exposed to. The curve is sampled at 2000 points per span in the renderer's
unit suite, with a bounded step between neighbours and a flat derivative at both
edges. Sixteen flat backdrops from black to mid-grey are rendered in a browser and
read back off the surface's own pixels, asserting monotone movement and no jump
larger than a third of the whole excursion
(`packages/platform-web/e2e/pixel/backdrop-tone-pixels.spec.ts`). And the demo
carries a control that walks a real surface through the transition, which is the
version a reader can see.

#### Accessibility

The adaptation folds under a preference, through two existing constants and no new
one. `ambientTint` — the axis the wave's composition contract names for how far
the material may move its colour — carries increased contrast (× 0.35) and forced
colours (× 0, and the optics pass stands down before it reaches here). The
refraction ladder read at the **accessibility cap** carries reduced transparency
(× 0.45), which touches no tint axis at all and would otherwise get the adaptation
at full strength — and full strength dissolves a surface into its backdrop, which
is precisely the occlusion that preference asked to be *raised*.

**Measured, not assumed, and the measurement is that nothing moves**: both
accessibility profiles' cells are bit-identical across this change, on both tiers,
every metric. That is not the fold working — it is that neither profile's scene
set contains a backdrop dark enough for this axis to act on at all. So the fold is
a statement about which way to be wrong, and it is unmeasured. Closing it needs a
`dark-solid` or `impulse` scene in the accessibility profiles' scene lists, which
is a capture session rather than a threshold.

The reference does say something adjacent, and it points the same way: under
reduce-transparency its material is nearly opaque and *flat* in the backdrop
across the whole range the bed covers (interior 0.9558 / 0.9557 / 0.9556 at
backdrops 0.529 / 0.500 / 0.205), where the standard material is already moving.

#### Two defects the bed could not see, and the demo could

Neither showed up in 168 cells, because the calibration scenes carry no text and
their backdrops do not move. Both are recorded because the class matters more than
the two instances: **this axis moves the material a long way, so every decision
that was taken against the material has to be re-checked, and every input it reads
has to be re-read.**

**The ink was decided against a backdrop the runtime had measured and then
ignored.** `hintedBackdropLuminance` answers for an *author* hint and nothing else,
so a group whose tone vitrea had measured — and whose material had just adapted
onto it — fell through to the `light-dark()` default. Measured on the demo: a plate
at `rgba(231, 231, 232, 0.811)` carrying the light ink. The adaptation can take a
surface from near-white to near-black while the ink stays where the colour scheme
put it, which is K4 / Decision Log #32(b)'s failure arriving through a third door.
Both tiers now decide the ink against the backdrop they actually resolved —
declared or measured — and against the *adapted* material.

**A live backdrop's measured tone was read once and frozen.** The cache re-read on
the scene's dirty epoch, which is a complete account of an `image` source and none
at all of a `canvas` or `video` one: on a CSS-tier root nothing marks their epoch,
because there is no pyramid to rebuild. Surfaces adapted onto whatever had been on
screen at first paint and stayed there. A live source is now re-read on the cadence
regardless of its epoch, and the cadence is what keeps that affordable.

Neither fix changed a pixel in the bed. The full 168 cells were regenerated after
them and reproduce the pre-fix run identically, reading for reading — which is also
the strongest web-side reproducibility attestation this bed has been given.

#### What this did not close

**The occlusion gain is still zero, and W2's diagnosis of why was wrong.** W2
fitted `sizeOcclusionGain` to a boundary optimum and recorded the reason as the
missing tone axis — "the axis that would let it fit is W7's". The axis now exists
and the sweep is unchanged in shape: 0 / 0.1 / 0.2 / 0.35 / 0.5 reads 0.1489 →
0.2000, monotone, a 1.34× spread. The seam stays wired and inert.

The real residual is visible in the same numbers and is neither size nor tone:
vitrea's interior sits ~0.18 above the reference's in the **middle** of the
backdrop range (0.7911 against 0.6053 over the checkerboard, 44 px), where this
axis is inert by construction and the size law has nothing to say. That is the
material's own transmission — a `tintAlpha` of 0.62 toward a white tint gives 0.79
over a 0.5 backdrop where the reference gives 0.61 — and moving it is a retune of
C9a's fitted constant, which would move every cell in the matrix and every adopted
bound with it. Named here as the next parent-impact item on this axis; not touched.

#### Fit, validation and holdout

Measured once, on the frozen configuration, over the full regenerated bed — all
six profiles, both tiers, fresh captures, 168 cells. Worst cell per set, with the
pre-W7 figure first. The two formerly-excluded scenes are **included** in these
worsts on both sides, unlike §5.7's table, because they are gated cells again.

| profile | tier | set | ΔE mean | SSIM | edge-weighted | ΔE p95 |
| --- | --- | --- | --- | --- | --- | --- |
| `1x-light-standard` | texture | calibration | 0.0495 → **0.0196** | 0.9088 → **0.9107** | 0.0571 → **0.0341** | 0.6244 → **0.0983** |
|  |  | validation | 0.0532 → **0.0189** | 0.9046 → **0.9413** | 0.0535 → **0.0324** | 0.6633 → **0.0918** |
|  |  | holdout | **0.0547** (unmoved) | **0.8934** (unmoved) | **0.0845** (unmoved) | **0.1339** (unmoved) |
|  | dom | calibration | 0.0508 → **0.0181** | 0.9080 → **0.9304** | 0.0587 → **0.0422** | 0.6213 → **0.0862** |
|  |  | validation | 0.0535 → **0.0182** | 0.9036 → **0.9551** | 0.0524 → **0.0403** | 0.6429 → **0.0818** |
|  |  | holdout | **0.0560** (unmoved) | **0.9205** (unmoved) | **0.1070** (unmoved) | **0.1090** (unmoved) |
| `2x-light-standard` | texture | calibration | 0.0495 → **0.0201** | 0.9259 → **0.9565** | 0.0534 → **0.0376** | 0.6242 → **0.0827** |
|  |  | validation | 0.0532 → **0.0192** | 0.9200 → **0.9578** | 0.0523 → **0.0293** | 0.6633 → **0.0911** |
|  |  | holdout | **0.0545** (unmoved) | **0.9566** (unmoved) | **0.0941** (unmoved) | **0.1335** (unmoved) |
|  | dom | calibration | 0.0507 → **0.0181** | 0.9251 → **0.9679** | 0.0557 → **0.0400** | 0.6213 → **0.0790** |
|  |  | validation | 0.0534 → **0.0184** | 0.9191 → **0.9707** | 0.0506 → **0.0416** | 0.6429 → **0.0832** |
|  |  | holdout | **0.0559** (unmoved) | **0.9509** (unmoved) | **0.1040** (unmoved) | **0.1084** (unmoved) |
| `1x-dark-standard` | texture | calibration | 0.0206 → **0.0205** | 0.9335 → **0.9456** | 0.0075 → **0.0067** | 0.1366 → **0.1200** |
|  |  | validation | 0.0155 → **0.0087** | 0.9348 → **0.9627** | **0.0065** (unmoved) | 0.1764 → **0.0924** |
|  |  | holdout | **0.0674** (unmoved) | **0.9196** (unmoved) | **0.0118** (unmoved) | **0.1597** (unmoved) |
|  | dom | calibration | 0.0241 → **0.0227** | 0.9186 → **0.9271** | **0.0132** (unmoved) | 0.1405 → **0.1281** |
|  |  | validation | 0.0164 → **0.0090** | 0.9320 → **0.9679** | **0.0064** (unmoved) | 0.1771 → **0.0938** |
|  |  | holdout | **0.0732** (unmoved) | **0.8961** (unmoved) | **0.0203** (unmoved) | **0.1713** (unmoved) |
| `2x-dark-standard` | texture | calibration | 0.0207 → **0.0203** | 0.9537 → **0.9631** | 0.0088 → **0.0072** | 0.1366 → **0.1177** |
|  |  | validation | 0.0155 → **0.0090** | 0.9483 → **0.9763** | **0.0069** (unmoved) | 0.1771 → **0.0949** |
|  |  | holdout | **0.0671** (unmoved) | **0.9510** (unmoved) | **0.0127** (unmoved) | **0.1594** (unmoved) |
|  | dom | calibration | 0.0241 → **0.0226** | 0.9446 → **0.9552** | 0.0128 → **0.0112** | 0.1405 → **0.1260** |
|  |  | validation | 0.0164 → **0.0094** | 0.9469 → **0.9785** | **0.0066** (unmoved) | 0.1771 → **0.0998** |
|  |  | holdout | **0.0729** (unmoved) | **0.9423** (unmoved) | **0.0179** (unmoved) | **0.1700** (unmoved) |
| `1x-light-reduced-transparency` | texture | calibration | **0.0115** (unmoved) | **0.9849** (unmoved) | **0.0332** (unmoved) | **0.0552** (unmoved) |
|  |  | validation | **0.0068** (unmoved) | **0.9609** (unmoved) | **0.0258** (unmoved) | **0.0431** (unmoved) |
|  |  | holdout | **0.0312** (unmoved) | **0.9843** (unmoved) | **0.0847** (unmoved) | **0.0741** (unmoved) |
|  | dom | calibration | **0.0119** (unmoved) | **0.9643** (unmoved) | **0.0383** (unmoved) | **0.0427** (unmoved) |
|  |  | validation | **0.0054** (unmoved) | **0.9674** (unmoved) | **0.0223** (unmoved) | **0.0331** (unmoved) |
|  |  | holdout | **0.0336** (unmoved) | **0.9345** (unmoved) | **0.0913** (unmoved) | **0.0586** (unmoved) |
| `1x-light-increased-contrast` | texture | calibration | **0.0186** (unmoved) | **0.9314** (unmoved) | **0.0677** (unmoved) | **0.0735** (unmoved) |
|  |  | validation | **0.0115** (unmoved) | **0.9252** (unmoved) | **0.0451** (unmoved) | **0.0559** (unmoved) |
|  |  | holdout | **0.0474** (unmoved) | **0.8812** (unmoved) | **0.1479** (unmoved) | **0.0901** (unmoved) |
|  | dom | calibration | **0.0220** (unmoved) | **0.9204** (unmoved) | **0.0735** (unmoved) | **0.0559** (unmoved) |
|  |  | validation | **0.0131** (unmoved) | **0.9240** (unmoved) | **0.0494** (unmoved) | **0.0483** (unmoved) |
|  |  | holdout | **0.0539** (unmoved) | **0.8581** (unmoved) | **0.1566** (unmoved) | **0.0727** (unmoved) |

Read the light-standard rows as the claim: **every calibration and validation
figure improves, on every metric and both tiers, and not one of the 168 cells
moves the wrong way on any metric.** 140 cells are bit-identical to the pre-W7
bed — the axis is exactly inert above its knee, observed rather than asserted —
and the 28 that move are the four dark-backdrop scenes across the four standard
profiles and both tiers. The two accessibility profiles are bit-identical
throughout, for the reason §Accessibility above gives: neither has a backdrop
this axis can act on.

**The holdout is unmoved, in every digit, on every profile and both tiers — and
that is a weaker result than it looks.** It discharges the half it can: the
configuration was frozen before this column was read, and nothing the fit could
not see regressed. It cannot discharge the other half, because the holdout scenes
are `hc-text`, `rrect-lg` and `glass-over-glass`, whose backdrops all sit far
above the curve's high edge. **This axis has no holdout scene.** What validated it
is the validation set — `impulse__capsule-button__rest` and
`impulse__rrect-md__rest`, neither fitted to, both moving the whole way (ΔE p95
0.6633 → 0.0324 and 0.1101 → 0.0257 on the 1× texture tier) — plus the
independent agreement of the 2× bed, and the size gate's argument form predicting
0.34 at the validation cell against a measured 0.356. A dark-backdrop holdout
scene is what would close it properly, and it is the same `scenes.json` addition
the band's dark end needs.

#### Three margins, after

- **Cross-tier interior ratio, light profiles: 0.8182, unchanged to the digit.**
  On `photo__glass-over-glass__rest` (holdout), against a gated floor of 0.80 —
  the project's tightest margin, W2's, and W7 did not touch it. That is the
  inertness property showing up where it matters most: that cell's backdrop is
  0.219, an order of magnitude above the curve's high edge. The *ceiling* on the
  same profiles improved, 1.0799 → 1.0284, because the cell that used to hold it
  now reads exactly 1.000.
- **Cross-tier ΔE mean: 0.0349, unchanged**, on `photo__rrect-lg__rest` against a
  bound of 0.05. Every cell whose coherence figure moved, moved down.
- **The dark profiles' interior-ratio ceiling: 1.1998 at 1× and 1.1956 at 2×,
  unchanged**, against 1.25. W2's watch item stays where W2 left it.

### 5.9 The adaptation axis finally has a holdout — and the curve fails it

§5.8 closed with "**this axis has no holdout scene**", and named the fix: a
backdrop inside the curve's transition band. `mid-dark-solid` (a neutral 69/255
grey, linear 0.0595) is that scene, captured 2026-08-30 and declared holdout in
`scenes.json`. It was measured **once**, against the configuration §5.8 froze,
with nothing tuned before or after. Two answers came back and they disagree.

**On the adopted gate it passes everything, at both scales and on both tiers.**

| profile | tier | IoU | contour mean / p95 | SSIM | ΔE mean / p95 | edge-weighted |
| --- | --- | --- | --- | --- | --- | --- |
| `1x-light-standard` | texture | 0.9579 | 0.61 / 2.83 | 0.9817 | 0.01036 / 0.1267 | 0.0181 |
|  | dom | 0.9363 | 1.10 / 2.24 | 0.9751 | 0.00941 / 0.1068 | 0.0180 |
| `2x-light-standard` | texture | 0.9558 | 1.32 / 5.66 | 0.9863 | 0.01049 / 0.1267 | 0.0170 |
|  | dom | 0.9355 | 2.23 / 5.00 | 0.9825 | 0.00950 / 0.1068 | 0.0166 |
| `1x-dark-standard` | texture | — | — | 0.9791 | 0.00324 / 0.0383 | 0.0016 |
| `2x-dark-standard` | texture | — | — | 0.9859 | 0.00328 / 0.0383 | 0.0018 |

Every light-standard row clears its adopted bound with room (the tightest is ΔE
p95 at 0.1267 against ≤ 0.17). Cross-tier coherence on the cell is 0.0031 against
≤ 0.05, and the interior ratio 0.9095 against 0.80…1.25. The dark rows carry no
shape or material axis: under the dark scheme the reference over this backdrop is
inside the extractor's 0.02 threshold of it, which is itself the finding that the
dark scheme adapts here and the light one does not.

**On the mechanism it fails, by a factor of five.** The estimator is §5.8's own —
the light-versus-dark separation over one backdrop, in which transmission,
backdrop structure and both scheme neutrals cancel — with the unadapted
separation taken from the two off-curve backdrops of the same component:

| cell | curve argument *x* | adaptation, measured | the curve's prediction |
| --- | --- | --- | --- |
| capsule over `dark-solid` | 0.0200 | **1.000** | 1.000 |
| capsule over `mid-dark-solid` | 0.0678 | **0.127** (0.13…0.17 over baseline choices) | **0.650** |
| `rrect-md` over `dark-solid` | 0.1017 | **0.218** | 0.241 |

The two rows the law was fitted on come back right. The row it had never seen
comes back at a fifth of prediction, and the miss is **not a scaling error that a
retune absorbs**: adaptation rises from 0.127 to 0.218 as *x* rises from 0.0678
to 0.1017, and any curve of the form `1 − smoothstep(low, high, x)` is monotone
decreasing in *x*. Backdrop luminance plus a size term *inside the argument*
cannot produce these three numbers at once. The size dependence is a separate
axis, not a shift along the same one — which is exactly the shape question a
holdout exists to ask, and it could not be asked until a scene varied backdrop
and size independently inside the band.

Read on the same estimator, vitrea executes the constants faithfully: 0.6497
measured against the curve's 0.6502. The implementation is not the defect. The
consequence is on the interior level, where the reference sits at 0.4442 (linear)
and vitrea at 0.2623 over a 0.0595 backdrop — vitrea over-adapts by 0.18, which
the perceptual rows survive only because a capsule's interior is a small part of
the canvas.

**Nothing was tuned in response, and this column is now spent.** A curve of a
different *shape* is a design change, not a retune, and it goes back through the
wave spec. The scene stays holdout for whatever replaces the law.

### 5.10 The author tint is still unmeasured — and now the reason is named

W3 phase 1 landed the tint API, both tiers and the tone curve's four constants at
**provisional** values, and stated that nothing rested on them. That is still
true, and the capture session meant to close it did not.

**The tinted fixtures carry no colour.** The bed committed on 2026-08-30 has 18
tinted native cells, and in each one the material is neutral glass:

- `photo__capsule-button__rest-tint-blue` is **byte-identical** to
  `photo__capsule-button__rest-tint-orange`, at both scales. So are the
  `checkerboard` and `dark-solid` capsule pairs. `systemOrange` and `systemBlue`
  cannot render to the same bytes, so the seed did not reach the material.
- Every tinted cell's native `tintChromaDelta` — the chroma the material adds
  over its own backdrop — lies in −0.0215…+0.0014, which is the same band the
  **untinted** cells occupy (−0.0151…+0.0000). vitrea's own tinted render reads
  +0.030…+0.134 on the same cells, which is what an author tint looks like.
- The tinted interiors are their untinted twins scaled by a channel-uniform
  factor (over `photo`, R/G/B ratios 0.724 / 0.741 / 0.728 — an orange tint would
  spread those by several times).

The tint's **alpha** did arrive: `…-tint-orange-half` differs from
`…-tint-orange`. So the registry was read and the strength was honoured; only the
colour was lost.

**Where it is lost, measured 2026-08-30 on the rebuild.** The question this
section left open — "the seed never reached `Glass`" versus "`Glass.tint(_:)`
ignored it on this OS build" — is answered, and the answer needed no capture. The
harness's new `./capture.sh tint-doctor` reports, on macOS 26.5.2 / Xcode 26.6 /
SDK `MacOSX26.5.sdk`, for all three registry tints:

- `Color.resolve(in:)` returns **exactly** the declared sRGB triple and alpha, in
  both colour schemes — `orange` resolves `sRGB(255.0, 149.0, 0.0) a=1.0000`,
  `blue` resolves `sRGB(10.0, 132.0, 255.0) a=1.0000`, `orange-half` resolves the
  orange triple at `a=0.5000`. `NSColor(_:).usingColorSpace(.sRGB)` agrees, in
  `sRGB IEC61966-2.1`.
- the **`Glass` value carries the hue**. `Glass` is `Equatable`, so this is
  decidable offline: `Glass.regular.tint(orange) != Glass.regular.tint(blue)`, and
  each registry tint is distinguishable from a reference hue at the same alpha.
  Two controls make that meaningful rather than vacuous — the same colour built
  twice compares **equal** (so equality is colour-sensitive), and one hue at two
  alphas compares **distinct** (so alpha is carried too).

So the seed reaches the material value intact, and is discarded between there and
the window server's composite. Fitting the committed bed's tinted cells against
their untinted twins recovers what does survive: a channel-uniform pull toward a
neutral grey near **140/255 at an effective alpha near 0.23**, halving to ~0.117
when the declared alpha is 0.5. That rules out a merely desaturated tint —
`systemOrange` and `systemBlue` differ in luminance (161 vs 115 by Rec.709), so
even a greyscale conversion of the correct tint would have produced two different
files. The hue is not compressed; it is absent.

**The call itself is Apple's documented one.** `Glass.tint(_ color: Color?)` is
the SDK's own declaration, applied to the `Glass` value beside `interactive()`,
which is the shape both Apple's SwiftUI documentation and WWDC25 session 323 use.
So the loss is not in the spelling — it is in the conditions the material was
rendered under, and there the harness was at fault.

**The capture window could never become key.** Apple documents
`NSWindow.canBecomeKey` as "`true` if the window has a title bar or a resize bar,
`false` otherwise" — and this harness captures through a **borderless** window, by
design, so that a window capture needs no cropping. Measured on the rebuild, the
capture window reported `canBecomeKey: false, isKeyWindow: false, isMainWindow:
false, NSApp.isActive: false`, and it did so through every capture of every
committed fixture. The app also took `.accessory` activation policy, which keeps
it from becoming active at all.

That matters because Liquid Glass has an active and an inactive appearance, and
the window server chooses between them from exactly this state. Multiple
independent developer reports describe the inactive one as flat and neutral, with
the tint dropped — a Ghostty maintainer ("when they lose focus, the glass style
changes too… window background color is also ignored"), a second Ghostty thread
("the system makes it flat and gray"), and, on this harness's exact stack of an
`NSHostingView` inside a floating borderless panel, a Hacking with Swift forum
report that "the glass effect turns into a simple blur when the app is not
focused". Apple's own framing of the tint makes the mechanism plain: from "Meet
Liquid Glass", "selecting a color generates a range of tones that are **mapped to
content brightness underneath** the tinted element". A tint is a hue mapped onto a
sampled backdrop; render the inactive material and there is no mapping left, and
the only parameter still carrying meaning is the tint's alpha — which is precisely
what the bed measured.

This is a hypothesis with a verified precondition, not a proven cause. What is
measured: the window was never key, and `canBecomeKey` is now `true` because
`Capture.CaptureWindow` overrides it. What is **not** yet measured: whether the
window actually becomes key in a real session, and whether the hue then lands.
Neither could be checked here — this machine's session refuses to activate the
app at all (`NSApp.isActive` stays false even when launched through
LaunchServices, and AppleScript automation of System Events times out), which is
an environment limitation rather than a code result. **Closing this needs one
granted capture in an interactive login session**, which the scheduled re-capture
already requires.

Two guards now stand behind it. Every fixture records `presentedActive` — was the
window key, in an active app, at the moment it was taken — and a run that
captures any fixture inactive says so in the manifest's caveats. And a bed whose
tints did not reach the material **refuses to publish** rather than filing itself
(§ the tint attestation in `apps/reference-apple/README.md`). Neither of the two
findings this section records can now recur silently.

**What follows from it, operationally.** No tone-curve constant is fitted, no
tint threshold is proposed, and the four constants stay provisional. The tinted
cells are **absent from `results/matrix.json`** rather than present with numbers
that would measure the untinted material under a tinted scene id — and that
absence is derived, not remembered: `cli/compare.ts`'s `colourlessTintEvidence`
finds the byte-identical pair and skips the tint axis on every profile, because
one binary in one session cannot have dropped the seed for those two scenes
alone. `--allow-colourless-tints` measures them anyway and says why. A
re-captured bed admits them automatically, and the fit the W3 plan designed can
then run unchanged.

The hue-independence and size-independence checks, and the dark-scheme and
accessibility assumption checks, are all unanswered for the same reason: with no
hue in the bed, the second-hue validation cell and the second-hue holdout cell
are byte-identical to their orange twins and would have "passed" trivially.

### 5.11 The active-pose bed: the damage report, and why the cascade stopped (2026-08-31)

> **Read this before any figure above it.** Every number in §1 through §5.10, and
> every constant those sections fitted, was measured against Liquid Glass's
> **inactive** appearance. The capture window was borderless and never overrode
> `canBecomeKey`, so it was never key, the app was never active, and the window
> server drew the inactive material through every capture the project has ever
> taken (wave Decision Log 14). Those are correct measurements of the wrong state.
> The inactive bed is kept in git history deliberately — it is the ready-made
> reference for a future window-focus-aware material — but it is no longer the
> reference this document claims against.

The active bed is `973fd7e`: **121 native fixtures**, six profiles, each cell the
byte state at least two of three independent runs share exactly (the active
material is byte-reproducible per *cell*, not per *run*). The recalibration
cascade began by regenerating the whole web side against it with **every constant
unchanged**, so that what the pose costs could be read before anything moved.
That regeneration is `results/2026-08-31-active-bed-stage0.json` — 182 cells,
six profiles × both tiers, calibration and validation only. **The holdout column
was not opened.** No constant was fitted, and none of §5's bounds is re-adopted,
re-proposed or amended by this section; the cascade stopped before it could
honestly do either, and the rest of this section is why.

#### The finding: the active material casts an outer shadow, and the inactive one casts none

This is not a constant that drifted. It is a facet of Apple's material that no
capture in this project had ever seen, and it invalidates the instrument.

On `checkerboard__capsule-button__rest` in `1x-light-standard`, measured outside
the declared component's own rectangle:

| bed | max abs. luminance difference from the backdrop, outside the component | pixels past the 0.02 extraction threshold |
| --- | --- | --- |
| inactive (`973fd7e~1`) | **0.0003** | **0** |
| active (`973fd7e`) | **0.2546** | **4740** |

The shadow is present in every profile, at both scales, in both colour schemes.
It is a downward-offset, multiplicative occlusion — it darkens the backdrop in
proportion to the backdrop's own light, so it is strongest under a bright
backdrop and analytically invisible over a dark one. Peak darkening and reach
from the component's edge at 1×, `1x-light-standard`:

| scene | above | below | beside |
| --- | --- | --- | --- |
| `light-solid__capsule-button__rest` (44 px) | −0.034 / 22 px | −0.082 / 39 px | −0.057 / 30 px |
| `light-solid__rrect-md__rest` (96 px) | −0.057 / 24 px | −0.135 / 41 px | −0.097 / 33 px |
| `checkerboard__capsule-button__rest` | −0.078 / 21 px | −0.255 / 45 px | −0.177 / 36 px |
| `dark-solid__capsule-button__rest` | 0.000 / 0 px | −0.001 / 0 px | 0.000 / 0 px |

It grows with the surface's span, and the reach roughly doubles in device pixels
at 2×, which is what a shadow specified in points does.

**vitrea draws nothing there at all.** Across every calibration and validation
scene of `1x-light-standard`, the mean absolute departure from the backdrop
outside the component is **0.0000 on vitrea's side** and 0.0022…0.0153 on the
reference's, over a shadow footprint covering **8.5% to 29.6% of the canvas**.

The bitter part of that is on the record already, in this repository, with the
right number attached to the wrong conclusion. C9a's light-standard profile
records `cssTierMapping.shadow` as *"the one thing [the CSS tier] draws that the
reference material does not: C9a measured both sides at approximately zero
outside the contour"*, and notes that the tier's `box-shadow` drove its silhouette
area to 2.36× the declared component area and its IoU to a mean of 0.676. C9d
then removed it (Decision Log #32(c)) — `shadowOffset`, `shadowBlur` and
`shadowAlpha` all ship at 0. The active reference casts a shadow of very nearly
that description, and the deleted triple (offset 6, blur 24, alpha 0.18) was
closer to the truth than what ships. The measurement was right; the reference was
the inactive one.

#### Why this stops the cascade rather than merely costing it rows

The shape axis extracts a silhouette by differencing the capture against the
background raster it was composited over — *"anything that differs from the known
background by more than a threshold is inside"*. That premise is exactly what the
active material falsifies: the reference's own shadow differs from the
background, so the extractor returns the component **and its shadow** as one body.
Native silhouette areas run about twice the declared component area (the
checkerboard capsule: 9836 px against a declared 4865), and §5's well-conditioned
predicate cannot catch it, because that predicate guards against *under*-recovery
and has no ceiling.

The damage is not confined to the shape rows, and this is the part that decides
the question. `material.interiorMean*` and `interiorStdDev*` are sampled **under
the native silhouette**, on both sides — so the interior statistics are now
averaged over a region that is roughly half shadowed backdrop. On the flat
`light-solid` capsule the reference's interior standard deviation reads 0.0623
where the true interior is uniform to the digit. Those three quantities are the
whole of this package's declared tuning objective
(`|Δ interior mean| + |Δ interior stdDev| + |Δ rim peak|`, `scripts/sweep.ts`),
so **every fit in the cascade would have been run against a corrupted objective.**

And the perceptual rows, which are whole-canvas and therefore sound as
measurements, now carry a constant penalty from a facet vitrea does not
implement. Fitting the material to absorb it would be the error W2 declined a
band optimum to avoid and W7 named again: using one mechanism as a proxy for a
missing one. Re-adopting a bound over it would certify the gap as acceptable
fidelity, which is what Decision Log 11 refused for a smaller gap.

#### The damage report, per profile × tier

Calibration + validation, active bed, constants unchanged. Worst reading against
each adopted bound, with the number of cells failing it.

| profile | tier | shape rows | SSIM | ΔE mean | ΔE p95 | edge-weighted |
| --- | --- | --- | --- | --- | --- | --- |
| `1x-light-standard` | texture | **FAIL** IoU 0.092 (21/26), cMean 28.5 (22/26), cP95 63.0 (23/26) | FAIL 0.8646 (1/27) | PASS 0.0381 | FAIL 0.2510 (5/27) | PASS 0.0448 |
| | dom | **FAIL** IoU 0.092 (20/26), cMean 28.5 (23/26), cP95 63.0 (23/26) | FAIL 0.8842 (2/27) | PASS 0.0417 | — | — |
| `2x-light-standard` | texture | **FAIL** IoU 0.098 (21/26), cMean 69.9 (22/26), cP95 124.0 (23/26) | FAIL 0.8937 (2/27) | PASS 0.0380 | FAIL 0.2503 (5/27) | PASS 0.0488 |
| | dom | **FAIL** IoU 0.098 (20/26), cMean 69.9 (23/26), cP95 124.0 (23/26) | FAIL 0.9041 (2/27) | PASS 0.0417 | — | — |
| `1x-light-reduced-transparency` | texture | **FAIL** IoU 0.564 (7/7), cMean 10.5 (7/7), cP95 27.0 (7/7) | PASS 0.9614 | PASS 0.0132 | FAIL 0.1406 (1/7) | PASS 0.0242 |
| | dom | **FAIL** IoU 0.529 (7/7), cMean 9.6 (7/7), cP95 25.1 (7/7) | PASS 0.9642 | PASS 0.0159 | FAIL 0.1725 (1/7) | PASS 0.0304 |
| `1x-light-increased-contrast` | texture | **FAIL** IoU 0.356 (7/8), cMean 13.4 (8/8), cP95 35.0 (8/8) | PASS 0.9106 | PASS 0.0236 | PASS 0.0837 | PASS 0.0733 |
| | dom | **FAIL** IoU 0.368 (7/8), cMean 12.5 (8/8), cP95 35.0 (8/8) | PASS 0.9072 | PASS 0.0266 | PASS 0.0732 | PASS 0.0794 |

Read it as three separate results.

**The shape axis is gone, on every gated profile and both tiers**, and it is the
instrument rather than the geometry that failed. It cannot be re-proposed at any
number: a bound loose enough to admit an IoU of 0.09 would not be a shape claim.

**The perceptual axis mostly holds, and on ΔE it holds comfortably** — the
worst ΔE mean anywhere is 0.0417 against bounds of 0.07 and 0.08, and every
edge-weighted row passes with two to four times the margin. SSIM misses on one or
two cells per light-standard profile, all of them `checkerboard__rrect-md__*`, by
0.002…0.016.

**Every ΔE p95 failure is a tinted cell.** Five in each light-standard profile
and one under reduced transparency, worst 0.2510 on
`checkerboard__capsule-button__rest-tint-blue`, against provisional tone-curve
constants that have now been fitted to nothing on either bed. Untinted, the ΔE
p95 row passes everywhere.

#### What the refits would have been — measured, not fitted

None of the following moved a constant. They are stated so the gate can price the
cascade, and each is measured on a **clean analytic mask**: the declared
component geometry, centred as `scenes.json` places it, eroded by 4 pt so no edge
pixel enters — which is a diagnostic, not a proposal for the instrument.

**Stage 1, the base material.** W7 named the mid-range transmission residual as
the next cut's item, on the inactive bed: vitrea 0.79 over a 0.5 backdrop where
the reference read 0.61. The brief for this cascade asked whether the active pose
moves it. **It does not.** Over the checkerboard at a 44 px span the reference
reads 0.6129 and vitrea 0.8043 — a residual of **+0.191** against the inactive
bed's +0.186. What is new is that it is plainly *size-dependent*: at 96 px the
same pair reads 0.6792 against 0.7841, a residual of +0.105.

Two things follow that the inactive bed could not say. The retune is **large and
in the direction C9a moved away from**: matching an interior of 0.613 over a 0.5
backdrop with a white tint needs an effective alpha near 0.23, where the shipped
`tintAlpha` is 0.62 — C9a raised it from an advisory 0.28, and the advisory was
closer to the active material than the fitted value is. And `blurSigma` may
finally be identifiable (§6.1): the active reference retains far more of the
backdrop's structure than vitrea does — interior standard deviation 0.1358
against 0.0176 on the checkerboard capsule, a factor of eight — which is a signal
well clear of the quantisation that made §6.1's sweep flat.

**Stage 2, the size law.** The residual above is size-dependent, but not in the
direction `sizeOcclusionGain` could absorb: vitrea is too *bright*, and occlusion
toward a white tint makes a large surface brighter still. The gain's boundary
optimum at 0 survives the pose change, for the third time and now for a reason
that is neither W2's nor W7's — it will only become fittable after the tint the
size law is a gain on has been re-fitted.

**Stage 3, backdrop adaptation.** Unmeasured here, deliberately: its observable
is the light-versus-dark separation over one backdrop, its only transition-band
scene is `mid-dark-solid__capsule-button__rest`, and that scene is **holdout**.
Reading it now would spend the column §5.9 already spent once.

**The accessibility folds are worse than W1 measured, not better.** Under
increased contrast the reference's interior now sits at 0.982…0.992 where vitrea
reaches 0.831…0.893 — the material has all but stopped transmitting, and
`increasedOcclusionLift` is under-set by roughly 0.09…0.16 of interior level.
Under reduced transparency the two agree within 0.06.

**Stage 4, the tint — the bed is finally good, and the news is a simplification.**
The hue is unambiguously present. On three of the five calibration backdrops the
reference's tinted interior is the declared seed **exactly**, in linear light,
with a per-channel standard deviation of **0.000**: `systemOrange` renders
(1.0000, 0.2961, 0.0000), which is sRGB (255, 149, 0) and nothing else. Over the
two structured backdrops it is the same seed scaled by 0.81…0.83 with a small
spread. So Apple's tinted material is a nearly opaque surface at the author's
colour, modulated only slightly by what is behind it — not the ±45% excursion
phase 1 assumed.

That is a **fit the existing four constants can express**, which is the good news:
`tintToneFloor` → 1 and `tintToneCeilMix` → 0 degenerate the curve to the seed
itself, leaving `tintToneLow`/`High` unidentifiable, in the same way
`adaptiveTint` fitted to an inert crossover in §7. No shape change is implied.
What is *not* in that curve is the size of the error: vitrea renders the tint at
roughly 45% of the seed over `dark-solid` (0.4508, 0.1356, 0.0000 against the
reference's 1.0000, 0.2961, 0.0000) and desaturates it over `photo`. That is the
tinted material's opacity, which rides `tintAlpha` — so Stage 4 cannot be fitted
before Stage 1, and Stage 1 cannot be fitted before the instrument is decided.

#### What the human gate has to decide

Three things, in this order, none of which is a constant.

1. **The outer shadow is a renderer feature vitrea does not have, on either
   tier.** It is measured, its mechanism is named, and it is the largest
   unmodelled facet in the project — larger in canvas footprint than the tone
   adaptation W7 was chartered for. Building it is a wave-sized item on both
   tiers (the CSS tier's is a `box-shadow` it used to draw; the GPU tier has only
   an *inner* shadow today).
2. **The instrument's extraction rule needs a ruling before any shape claim can
   exist again.** "Everything that differs from the background is the surface" is
   false for the active material. Every alternative is a design decision with a
   cost — bounding the search to the declared geometry makes IoU partly
   tautological; discriminating the shadow by its gradient is fragile; excluding
   the shape axis outright retires a claim v1 shipped. This is not a call a
   calibration run should take by itself.
3. **Whether any bound may be re-adopted before (1).** The recommendation here is
   no. The perceptual rows would pass, and they would pass over a reference facet
   vitrea renders as zero across a fifth of the canvas; adopting them would be
   the certify-the-defect move Decision Log 11 rejected when the gap was smaller.

Until those are answered, §5's tables stand as adopted **against the inactive
bed**, `results/matrix.json` is unchanged, and
`KNOWN_RENDERER_GAP_EXCLUSIONS` stays empty — the outer-shadow gap is measured
and mechanism-named, which is the bar for an entry, but it fails the class's own
"cannot grow" property by a wide margin: it would have to swallow every shape row
in the document.

---

### 5.12 The two-axis instrument: a bounded shape axis and a measured shadow axis (2026-08-31)

§5.11 ended with three questions for the human gate. All three were answered on
2026-08-31 (wave Decision Log 15): W8 is chartered to build the shadow on both
tiers, no bound may be re-adopted before it, and **the instrument becomes two
honest axes** — shape extraction bounded to the declared component region, and
the outer shadow measured as an axis of its own. This section is what the second
ruling means operationally: the rule each axis now follows, what each claims,
what each no longer claims, and the reference's numbers for W8 and the cascade to
consume.

Nothing here proposes, adopts or amends a threshold. The shadow axis has no bound
at all and must not acquire one until W8 renders a shadow to bound — a bound over
a facet vitrea draws as zero is the certify-the-defect move Decision Log 11
refused.

#### The bounding rule, and why its margin is zero

The search region is the component's own declaration in `scenes.json` —
`placeComponent` centres it exactly as `ZStack` and the DOM do, the union of its
rounded rects is rasterised by pixel-centre containment at the profile's backing
scale, and extraction returns nothing outside it. The region is derived from the
*declaration*, never from the image: an image-derived bound would be the same
circularity in a longer form, because the shadow that broke the old rule is in
the very pixels the bound would be fitted to.

The design called for "a small margin for real edge softness". **Measured, there
is none to allow**, and the margin ships at zero as a result. A margin exists to
admit the antialiased boundary band; on this bed the reference's occlusion field
begins at the contour with no gap, so the first pixel ring outside the declared
contour is already fully-developed shadow — mean occlusion 0.05…0.19 of the
backdrop's own level, over `1x-light-standard`. Every outward pixel of margin
therefore admits shadow-darkened backdrop into the reference's silhouette and
almost none into a renderer that draws no shadow. The cost is direct and
monotone from the first fraction of a pixel:

| margin, device px | `photo__capsule-button__rest` IoU | `light-solid__capsule-button__rest` IoU |
| --- | --- | --- |
| 0 | 1.000 | 0.888 |
| 0.5 | 0.978 | 0.856 |
| 1 | 0.970 | 0.850 |
| 2 | 0.942 | 0.817 |
| 3 | 0.912 | 0.779 |

Every point of that decline is the shadow re-entering the axis the bound exists
to keep it out of. So the bound is the declaration itself, and the shape axis's
noise floor stays what it always was: the raster grid, ±0.5 px. The margin
remains a parameter (`--region-margin`, `componentRegionMargin` in every cell)
because it is a judgement about a bed rather than a law — a reference that casts
no shadow could afford one — and the value it was measured at is on the record
per cell.

#### What the shape axis claims now, and what it no longer claims

**Claims.** Each side fills, and stays inside, the geometry the scene declares:
coverage of the declared region, contour position within it, and corner profile.
That is the corner-and-edge fidelity the axis exists for, and it is intact — a
surface whose corners are too tight, whose body is misplaced, or which fails to
reach its declared contour reads exactly as it did before.

**No longer claims: area recovery.** Both silhouettes are bounded above by
`componentRegionArea` by construction, so a surface drawn *larger* than its
declaration is clipped to the declaration and reads as a match. Over-fill is not
measurable against a shadow-casting reference by luminance differencing at all,
at any margin — the two are the same pixels — and the honest form of that is to
bound both sides identically and say so rather than to report a number that
mixes them. `silhouetteAreaNative`, `silhouetteAreaWeb` and
`componentRegionArea` are all in the cell so a reader can see which of them
saturated.

**The conditioning predicate changes shape.** §5's well-conditioned rule is a
floor — `silhouetteAreaNative ≥ 0.95 × declared` — with no ceiling, which is
exactly why it could not catch the confound §5.11 found: a silhouette at twice
the declared area passes a floor. Under the bound the ceiling is imposed rather
than measured, so the predicate's honest statement becomes *floor measured,
ceiling assumed*, and any future gate should read `silhouetteArea*` against
`componentRegionArea` rather than against the declared area alone.

**And it needs a web-side arm.** With the bound in place the reference fills the
region on essentially every cell whose backdrop supports the measurement —
`silhouetteAreaNative / componentRegionArea` has a median of 1.000 over those 142
cells, and the only readings under 0.95 are increased contrast over the
checkerboard (0.62, 0.65: the near-opaque material matches the light squares it
covers) and `photo__capsule-button__rest-tint-blue` (0.71). So the cell that is
now badly conditioned is typically a *web-side* one:
over `light-solid`, vitrea's specular rim crosses the backdrop's own level, its
extracted silhouette comes back at 4328 px of a 4872 px region with a ring of
holes at its edge, and the contour traced round that reads a corner curvature of
8.65 1/px against the reference's 0.056. That figure describes the extractor, not
vitrea's corners. The predicate the post-W8 gate adopts should condition on both
sides' areas; this document records the reason rather than proposing the number.

#### The shadow axis, defined

Measured **outside** the declared region, on both sides, by one estimator, in
linear light. The quantity is *occlusion* — `(backdrop − rendered) / backdrop` —
not absolute darkening, because the reference's shadow removes a fraction of the
light behind it and the same shadow is therefore a large drop over a bright
backdrop and an invisible one over a dark one. Normalising is what makes a
shadow's description comparable across the five backdrops the bed puts one
surface over.

Distances are exact distances to the *declared* contour, not to an extracted one,
so the axis is not hostage to what the extractor recovered — it reports on cells
whose shape axis is absent entirely.

| figure | definition |
| --- | --- |
| `meanDeparture{Native,Web}` | mean `backdrop − rendered` over the whole exterior, linear light, signed. Absolute, so it is defined on every scene; negative means that side brightens its surround on balance. |
| `backdropSupport` | fraction of the exterior whose backdrop clears 0.05 linear luminance — the level below which a ratio is arithmetic on no information. |
| `strengthPeak{Native,Web}` | deepest one-pixel-ring mean occlusion, pooled over all four directions, with `strengthPeakDistance` saying where it sits. |
| `extent{Above,Below,Left,Right}{Native,Web}` | how far the occlusion reaches in that direction, in pixels from the declared contour: the outermost ring of a qualifying consecutive pair, where qualifying is a ring mean ≥ 0.01 occlusion. Directions are sectors split on the component's own bounding-box diagonals, so "beside" a capsule is the region past its caps. |
| `offset{X,Y}{Native,Web}` | the displacement the reach implies: half the difference of opposing extents. This is the offset a renderer is fitted to. |
| `centroidOffset{X,Y}{Native,Web}` | the occlusion-mass centroid minus the component's centre. A different question from the offset — where the darkening actually sits on the canvas — and inflated relative to it, because only the visible half of the field is in the integral. |
| `falloffSigma{Native,Web}` | the blur radius of the **blurred-edge** model `amplitude × (1 − Φ(d/σ))`, with `falloffSigmaResidual` as a fraction of the peak. This is the parameter a renderer's shadow takes. |
| `falloffAmplitude{Native,Web}` | the same fit's occlusion at the contour — the strength figure, separated from σ and estimated clear of the body's own edge ring. |
| `falloffLength{Native,Web}` | the **exponential** alternative's decay length, fitted over the same points with the same objective and the same free-parameter count, with `falloffResidual` beside it. |

**The falloff is fitted in two families on purpose.** A shadow is a filled shape
convolved with a blur kernel, so the profile outside it should be a blurred
*edge*; the obvious alternative is an ambient-occlusion-shaped exponential. Both
are fitted over the same rings with the same objective and two free parameters
each — the amplitude solves in closed form for any trial scale — so the pair of
residuals is a comparison rather than two unrelated numbers, and neither family
can win on flexibility. Reporting the winner alone would turn a finding into an
assumption; reporting both keeps the question answerable from the record. The
blurred edge's σ is measured with the shadow's own edge pinned to the declared
contour, which is what keeps the model identified — only the tail beyond the
component is visible, and with a free edge position amplitude, offset and σ trade
against one another along a valley — at the price that σ absorbs the shadow's
spread and the spread of its directional offset, and so reads somewhat above the
blur radius a renderer would be given.

**Absent, never zeroed**, in four distinguishable ways: the whole normalised
block is absent where the backdrop cannot support a ratio; `offset*` is absent
where no direction reached the threshold, which is what a renderer drawing no
shadow produces — an undefined displacement recorded as undefined rather than as
(0, 0); `centroidOffset*` is absent where too little of the exterior is occluded
for a centroid to describe the shadow rather than the backdrop's own support
pattern; each falloff family is absent independently where its own fit lands on
an impossible amplitude or a sub-pixel scale.

**Where the body's own edge is kept out, and where it is left in.** Ring 0 — the
first pixel outside the declared contour — belongs to each side's own edge as
much as to the shadow. Over `photo` the reference's rim spills into it and reads
−0.276 occlusion; under increased contrast the reference draws a hard border
stroke there, 0.560 against a shadow of 0.096 one pixel further out. Two rules
follow, and between them they are why the accessibility profiles now read like
every other profile:

- **the extents require a qualifying adjacent *pair***, so a lone ring 0 is not
  reach. The pair is strict in both directions — the walk starts unqualified
  rather than crediting ring 0 with a phantom predecessor, and an unmeasurable
  ring breaks adjacency rather than being stepped over;
- **the falloff is fitted from ring 1 outward.** Anchoring it on ring 0 fits the
  border instead of the shadow: with ring 0 in, the two accessibility profiles
  return a blur scale under a pixel and a residual forty times the rest of the
  bed's, and with it out they return σ = 17.6…18.0, the same as everywhere else.

`strengthPeak` still reports the raw maximum over *every* ring with its distance,
so the spike itself stays visible and is not quietly smoothed away: on
`photo__capsule-button__rest` under increased contrast it reads 0.560 at ring 0
where `falloffAmplitude` reads 0.203, and that gap is the border.

#### The reference's shadow, measured

Staged matrix `results/2026-08-31-active-bed-bounded-instrument.json` — schema 5,
182 cells, six profiles × both tiers, calibration and validation, over the active
bed with **every constant unchanged**. The holdout column was not opened.
Untinted rest scenes, texture tier; extents in device pixels from the declared
contour.

| profile | scene | span | support | amplitude | above/below/left/right | offset y | σ | σ residual | vs. exponential |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1x-light-standard` | `light-solid__capsule-button` | 44 | 1.00 | 0.137 | 15 / 29 / 25 / 25 | 7.0 | 17.9 | 0.0108 | 2.7× |
| | `checkerboard__capsule-button` | 44 | 0.50 | 0.370 | 24 / 39 / 32 / 34 | 7.5 | 18.0 | 0.0046 | 6.9× |
| | `photo__capsule-button` | 44 | 1.00 | 0.361 | 24 / 39 / 32 / 34 | 7.5 | 18.0 | 0.0060 | 6.0× |
| | `checkerboard__rrect-sm` | 32 | 0.50 | 0.366 | 24 / 39 / 31 / 33 | 7.5 | 17.9 | 0.0050 | 6.5× |
| | `light-solid__rrect-md` | 96 | 1.00 | 0.223 | 19 / 34 / 28 / 28 | 7.5 | 17.6 | 0.0082 | 3.8× |
| | `photo__rrect-md` | 96 | 1.00 | 0.212 | 20 / 36 / 28 / 30 | 8.0 | 17.3 | 0.0046 | 6.2× |
| | `photo__toolbar-group` | 44 | 1.00 | 0.358 | 25 / 40 / 32 / 32 | 7.5 | 18.2 | 0.0068 | 5.4× |
| `2x-light-standard` | `light-solid__capsule-button` | 44 | 1.00 | 0.139 | 30 / 59 / 50 / 50 | 14.5 | 35.8 | 0.0104 | 2.5× |
| | `checkerboard__capsule-button` | 44 | 0.50 | 0.373 | 48 / 77 / 65 / 67 | 14.5 | 36.2 | 0.0053 | 6.4× |
| | `photo__capsule-button` | 44 | 1.00 | 0.365 | 48 / 79 / 64 / 67 | 15.5 | 36.3 | 0.0061 | 5.9× |
| | `light-solid__rrect-md` | 96 | 1.00 | 0.226 | 38 / 68 / 56 / 56 | 15.0 | 35.5 | 0.0086 | 3.8× |
| | `photo__rrect-md` | 96 | 1.00 | 0.215 | 38 / 72 / 57 / 59 | 17.0 | 34.8 | 0.0045 | 6.1× |
| `1x-dark-standard` | `checkerboard__capsule-button` | 44 | 0.50 | 0.067 | 7 / 23 / 19 / 18 | 8.0 | 18.4 | 0.0103 | 1.1× |
| | `photo__capsule-button` | 44 | 1.00 | 0.069 | 8 / 26 / 16 / 20 | 9.0 | 16.2 | 0.0157 | 1.7× |
| | `checkerboard__rrect-md` | 96 | 0.50 | 0.257 | 20 / 36 / 31 / 29 | 8.0 | 17.7 | 0.0065 | 4.3× |
| | `photo__rrect-md` | 96 | 1.00 | 0.195 | 19 / 36 / 28 / 29 | 8.5 | 17.4 | 0.0045 | 6.1× |
| `2x-dark-standard` | `photo__capsule-button` | 44 | 1.00 | 0.069 | 17 / 52 / 33 / 39 | 17.5 | 32.9 | 0.0104 | 1.8× |
| | `photo__rrect-md` | 96 | 1.00 | 0.198 | 37 / 73 / 56 / 58 | 18.0 | 35.0 | 0.0051 | 5.7× |
| `1x-light-reduced-transparency` | `photo__capsule-button` | 44 | 1.00 | 0.203 | 20 / 35 / 28 / 29 | 7.5 | 17.8 | 0.0092 | 3.8× |
| | `photo__rrect-md` | 96 | 1.00 | 0.215 | 20 / 37 / 29 / 29 | 8.5 | 17.7 | 0.0054 | 6.0× |
| `1x-light-increased-contrast` | `photo__capsule-button` | 44 | 1.00 | 0.203 | 20 / 35 / 28 / 29 | 7.5 | 17.8 | 0.0016 | 3.8× |
| | `photo__rrect-md` | 96 | 1.00 | 0.215 | 20 / 37 / 29 / 29 | 8.5 | 17.7 | 0.0011 | 6.0× |

The last column is the exponential's residual divided by the blurred edge's, on
the same points.

Four things follow, and they are descriptions rather than proposals.

**The shadow is a Gaussian blur, and the instrument now says so from the data.**
The blurred edge fits better than the exponential on **all 142 normalised cells**
— residual 0.001…0.019 against 0.005…0.037 — at equal parameter count, so this is
the family the profiles are in and not an artefact of a more flexible model. It
is also the family a renderer implements: `box-shadow` and a GPU shadow pass both
take a blur radius, so the instrument and the mechanism now speak the same
language and the cascade can fit one against the other directly.

**One geometry, specified in points, across the whole bed.** σ is 16.2…18.4
device px on every 1× profile and 32.9…37.2 on every 2× one — it doubles with the
backing scale and moves by under 15% across backdrop, span, colour scheme and
accessibility state. The reach-implied offset behaves the same way: 7.0…9.0 px at
1×, 14.0…18.0 at 2×. So the reference's shadow is, to the precision this bed
supports, **a single point-specified shadow: about a 7.5 pt downward offset with
a σ ≈ 17.8 pt blur**, reaching roughly 20 pt above, 37 pt below and 30 pt beside
a light-standard surface at the 1% iso-occlusion level. (σ is measured with the
shadow's edge pinned to the declared contour, so it absorbs the spread and the
directional offset and reads above the blur radius a renderer would be given —
W8's independent mechanism fit puts that at 15.55 CSS px with a +3.10 spread,
which is the same shadow described in the parameterisation a renderer takes.)

**What varies is the amplitude, not the geometry.** Between a 32 pt and a 96 pt
component at 1× light-standard, σ moves from 17.9 to 17.6 while the amplitude
moves from 0.366 to 0.212; between `light-solid` and `photo` under the same 44 pt
capsule, σ moves from 17.9 to 18.0 while the amplitude moves from 0.137 to 0.361.
A purely multiplicative occlusion would give one amplitude per surface whatever
the backdrop, and these do not. **The multiplicative model describes the shadow's
geometry very well and its amplitude only approximately**, which is what W8's
`span-coupling` and `backdrop-multiplicativity` parameters have to resolve. This
refines §5.11's "it grows with the surface's span": what changes with span and
backdrop is the darkening, not the reach.

**Reduced transparency and increased contrast share one shadow, and the border is
separate.** Both accessibility profiles return the same amplitude and the same σ
to three digits (0.203 / 17.8 on `photo__capsule-button`), and outside the first
ring their `photo` fixtures are pixel-identical — the increased-contrast
difference is the border stroke and the interior, not the shadow. So the shadow
is one facet across all four gated profiles, and the border is a second one that
W8 should build separately.

#### Correction (2026-08-30): the dark scheme is the same shadow, dimmer

The paragraph this replaces read "the dark scheme casts a weaker,
differently-shaped shadow", on the evidence that the reach above the component
falls from 24 px to 8 px between light and dark while the reach below barely
moves. **The measurements stand; the interpretation was wrong, and it is
withdrawn.**

The extents are an *iso-occlusion* contour: they mark where the ring mean crosses
0.01, so a shadow of identical geometry at a lower amplitude crosses that level
sooner, and it crosses it soonest where the shadow is thinnest — which is above
the component, on the far side of a downward offset. The apparent collapse of the
upward reach is therefore the threshold moving, not the shadow.

Two independent lines of evidence say so. W8 refitted the dark cells with the
*light* geometry and only the amplitude free: it costs 3–7% of an already small
residual, and one geometry with one amplitude per profile predicts the
per-direction extents in this table from a single calibration point (light
24/40/32 against the measured 24/39/32–34; dark 10/26/18 against 8/26/16–20;
reduced transparency 20/36/28 against 20/35/28–29). And this axis, refitted in
the family the profiles are actually in, now says the same thing on its own:
**dark σ is 16.2…18.4 against light's 17.3…18.2 — the same number — while the
amplitude falls from 0.361 to 0.069 on the same `photo__capsule-button` cell.**
Same geometry, one fifth the strength.

What W8 needs is therefore an amplitude per colour scheme, not a shadow per
colour scheme. Separating `falloffAmplitude` from `falloffSigma` is the change
that makes that readable off a cell rather than inferred from a threshold
crossing, and it is why the amplitude is now on the record beside the extents.

#### vitrea's baseline: zero, honestly recorded

Across the same 182 cells, vitrea's side of the shadow axis reads:

| figure | vitrea, texture tier | vitrea, dom tier |
| --- | --- | --- |
| `meanDepartureWeb` | −0.0079…+0.0014 luminance | −0.0140…+0.0041 luminance |
| `extent*Web` | **0 in all four directions on 43 of the 71** cells that carry a normalised block | 0 in all four on 29 of 71 |
| `offsetYWeb` | **absent** on exactly those cells — an undefined displacement recorded as undefined, not as (0, 0); present on 28 of 71 | present on 42 of 71 |
| `falloffSigmaWeb` | absent on 62 of 71; 1.96…4.77 px on the nine cells with a near-contour halo | absent on 64 of 71; 1.47…3.45 px on seven |

On every 1×-light-standard untinted rest scene over `photo`, both tiers read
**0 / 0 / 0 / 0** with `strengthPeakWeb` of 0.0000 and no offset at all; over
`light-solid` the same holds except for 2…3 px on the capsule's two sides on the
texture tier. The overall sign is the more telling number: vitrea's mean
departure is *negative* on most cells — where the reference darkens its surround,
vitrea very slightly brightens it.

Where vitrea does read a non-zero extent it is at most 3 px at 1× and 7 px at 2×,
on the checkerboard, dark-scheme and tinted scenes, and it is its **own
material's edge** rather than a shadow. Two things separate the two beyond doubt:
its peak sits at ring 0, and where a blur radius can be fitted at all it is
1.5…4.8 px against the reference's 16.2…37.2 — an order of magnitude, in the one
parameter that describes a shadow's geometry. That is the honest reading and not
an error: the axis is measuring something real that is nowhere near the facet it
would have to reproduce, and has no displacement at all.

#### Schema and gate state

`RESULT_MATRIX_SCHEMA_VERSION` is **5**. The bump is not a field list: every
schema-4 `shape` and `material` figure was measured under a whole-canvas
silhouette that, on the active bed, contained the reference's shadow as well as
its component, so reading a version-4 figure beside a version-5 one as the same
quantity is the specific misreading the version exists to prevent.

`results/matrix.json` stays at schema 4 and is not regenerated, per Decision Log
15 ruling 3: the inactive-bed gate stays enforced as the historically labelled
suite until the one honest post-W8 pass. `test/adopted-thresholds.test.ts` now
pins **both** numbers — the committed matrix at 4 and the build at 5 — so the
divergence is a decision on the record rather than drift, and its
well-conditioned predicate carries the floor-with-no-ceiling limitation in
writing. `KNOWN_RENDERER_GAP_EXCLUSIONS` stays empty. No threshold is proposed,
adopted or amended by this section, on either axis.

The frozen matrix is also the *default* target of `compare` and of `diff
--matrix`, which during the interregnum is a path that cannot succeed. Both CLIs
now check the target's schema **before** doing any work — before the browser
capture, in `compare`'s case — and refuse it by name, citing the ruling and
naming `--out-matrix` as the way past. A run that was never going to be writable
should cost a message, not an hour.

#### What this section corrects, and when

Two figures and one reading in the first version of this section (2026-08-31)
were wrong, and the staged matrix was regenerated on the same tree to replace
them. Recorded rather than silently overwritten, because a claims document that
edits its own numbers without saying so is not evidence.

- **The falloff family.** The axis originally fitted only an exponential decay,
  and reported λ ≈ 12 pt. A shadow is a blurred edge, not an exponential; refitted
  in both families at equal parameter count the blurred edge wins on all 142
  normalised cells, and σ ≈ 17.8 pt replaces λ ≈ 12 pt as the geometric figure.
  W8's independent mechanism fit had reached the same conclusion from the other
  direction (Gaussian RMS 0.00233 against the exponential's 0.00527 over 585
  points), which is what prompted the recheck.
- **The dark-scheme reading**, withdrawn above.
- **Vitrea's small reads.** The extent rule credited ring 0 with a qualifying
  predecessor, so a lone edge-halo ring reported a one-pixel reach in every
  direction and — worse — a *defined* offset of (0, 0), on a side whose offset
  the doctrine says must be absent. Seven cells carried that; the counts in
  vitrea's table above are the corrected ones.
- **A count that was not a count.** The run's caveat block reported cells absent
  from an axis by counting distinct *scene* names, so each tier's 20 unnormalised
  cells — 40 across the staged matrix — were announced as six. Absences are now
  tallied per cell and named per scene, which are different numbers and are
  printed as both.

#### Correction (2026-08-31): the extents were not guarded against the frame

The axis walked rings outward until the departure stopped qualifying, and never
asked whether the walk had run out of *canvas* rather than out of shadow. Where a
component leaves less margin than the reference's shadow needs, that walk reports
the size of the window under the shadow's name — and the σ fitted over the same
profile comes back biased with it, because the rings past the frame are averaged
over an annulus the frame has eaten.

Measured on the active bed at 1× light-standard, texture tier:

| backdrop | span | margin | σ | extent below |
| --- | --- | --- | --- | --- |
| `photo` | 96 | 52 px | 17.31 | 36 |
| `photo` | 130 | 35 px | 17.52 | 35 |
| `photo` | **160** | **20 px** | **15.86** | **33** |
| `checkerboard` | 96 | 52 px | 17.75 | 37 |
| `checkerboard` | 130 | 35 px | 17.69 | 38 |
| `checkerboard` | **160** | **20 px** | **17.55** | **35** |

**σ falls about 8% on `photo` at the clipped span, where the two roomier spans
agree within 1%**, and the same cell reads 31.93 at 2× against 34.8…35.8
everywhere else. The cause is geometric and has nothing to do with the material:
`rrect-lg` is a 160 pt span on a 200 pt canvas, so 20 pt of margin has to hold a
shadow that reaches 33…37 pt below.

**The guard.** Every side now reports `clearance*` — the distance from the
declared contour to the canvas edge on that side, a property of the scene and so
reported once — and withdraws that side's extent when the walk did not finish
inside it. The test is on the ring that *ends* the walk rather than the last one
that qualified: an extent of `e` is a statement that ring `e` failed to qualify,
rings are unit-wide and span `[e, e + 1)`, so the reading rests on a whole ring
only while `e + 1 ≤ clearance`. The one ring of guard band is the ring's own
width, not a chosen tolerance. `offset*` goes with the pair it belongs to, since
half a difference is not a displacement when one of its two terms is the frame.
This is the axis's existing "absent, never zeroed" discipline applied to a second
way of not knowing, and it needs no new constant.

**What it changes in this section: nothing, and that is checkable.** Every
calibration and validation cell on this bed clears the frame by at least **51.5
device px**, and the closest any measured reach comes to the frame is **14.5 px**
— `photo__rrect-md__rest` under increased contrast. The table above, the
`16.2…18.4` and `32.9…37.2` σ ranges, the 142-cell family comparison and vitrea's
baseline counts are all over the 182 calibration-and-validation cells of
`results/2026-08-31-active-bed-bounded-instrument.json`, whose holdout column was
never opened. No figure in §5.12 moves.

One reading in it is now scoped, though. "σ … moves by under 15% across backdrop,
span, colour scheme and accessibility state" is a claim over the spans this bed
measures cleanly — 32 to 96 pt. It is **not** contradicted by the 15.86 at span
160: that reading was the window, and it is withdrawn rather than admitted as an
exception. What the bed can honestly say about span above 96 pt is nothing, which
is the same gap §5.16 found from the other direction.

**What it changes elsewhere.** Re-measuring `results/2026-08-31-round-two.json`
through the corrected instrument — same captures, same constants, `--skip-capture`
so nothing was re-rendered — moves **32 cells, every one of them holdout**:
`photo__rrect-lg__rest` and `checkerboard__rrect-lg__rest` on all four sides
(clearance 19.5 px at 1×, 39.5 at 2×), `photo__rrect-lg__rest-tint-orange` the
same, and both `glass-over-glass` cells below only (clearance 34.5 px at 1×; still
truncated at 2×, where the reach doubles in device px and 69.5 px is no longer
enough). Nothing outside the shadow axis changed on any cell, and inside it
nothing but the extents, the offsets and the new clearances. No bound reads an
extent, so no gate outcome moves.

The staged matrices dated before this one — `active-bed-stage0`, `active-bed-refit`,
`active-bed-adoption-candidate`, `active-bed-bounded-instrument` and
`outer-contour-calval` — keep the pre-guard reading and are **not** regenerated.
They were written under superseded constants, so re-running them on today's tree
would restate history rather than correct it. Where they carry a `rrect-lg` or
`glass-over-glass` extent, it is the window's number.

**And a mis-attribution of my own, withdrawn.** §5.17 first reported this finding
with the sentence *"§5.12's shadow table quotes those figures as measurements of
the reference."* It does not: that table is calibration and validation only, and
neither scene appears in it. The biased figures were quoted in §5.17 itself, as
the finding, which is the only place they ever appeared. The finding was right and
the pointer was wrong.

### 5.13 The active-bed refit, and the holdout that falsified part of it (2026-08-31)

The recalibration cascade, resumed after W8 built the outer shadow and the
instrument became two axes (§5.12). Every constant in the material was refitted
against the **active-pose** bed on **calibration cells only**; validation was read
as a self-check; and the holdout column was opened **once**, at the end, against a
frozen configuration. Staged matrix: `results/2026-08-31-active-bed-refit.json`,
schema 5, 242 cells, six profiles × both tiers, all three sets.

**Nothing in this section is adopted.** `results/matrix.json` is untouched, the
enforced suite still runs the inactive-bed gate as the historically-labelled
suite (Decision Log 15 ruling 3), and the tables below are proposals. Three
findings go to the human gate rather than into a threshold, and they are named at
the end.

#### What moved, and what the fit said

| constant | before | after | the fit |
| --- | --- | --- | --- |
| `optics.regular.tintAlpha` | 0.62 | **0.46** | interior optimum on the 8 tone-inert untinted rest cells (0.38 → 0.16945, 0.46 → 0.15704, 0.54 → 0.17248); ΔE and SSIM agree |
| `optics.regular.blurSigma` | 8 | **3** | identifiable for the first time — the spread term triples from σ 3 to σ 6 |
| `optics.regular.shadowAlpha` | 0.55 | **0.05** | objective 0.14615 → 0.09333, both checks improving; the largest single gain in the cascade |
| `sizeShadowGainMax` | 1.4 | **1** | its facet is now inert, so the grid is flat to 0.2% — the identity rather than a stale fitted number |
| `backdropToneSizeBias` | 0.09 | **0.13** | the validation cell decided it (below) |
| `backdropToneLow` | 0.02 | **0.03** | repairs §5.8's own flagged "exact but not margined" edge at no cost to the objective |
| `tintToneFloor` | 0.45 | **1** | monotone, 2.09× spread — the curve fits to the identity |
| `tintToneCeilMix` | 0.45 | **0** | as above |
| `outerShadow.occlusion` | 0.33 | **0.285** | interior optimum, 2.23× spread, flat to 1% across 0.255…0.315 |
| `outerShadow.reducedTransparencyOcclusion` | 0.566 | **0.70** | sharp, 3.83× spread; 0.285 × 0.70 = 0.1995 against the reference's measured 0.203 |
| dark profile `outerShadow.occlusion` | *(inherited)* | **0.09** | interior optimum on the dark calibration cells, 2.06× spread |

Unchanged with reasons: `rimAlpha` and `rimWidth` (the rim was never mis-set —
see below), `sizeOcclusionGain` and `sizeScatterGainMax` and the band 32…96,
`lensSizeGainMax` 2.6, the dark profile's `tintAlpha` 0.97 and tint level 0.05,
`backdropToneMax`/`High`, W8's shadow geometry, and
`cssTierMapping.referenceBackdropLuminance` 0.02 (its grid spans 1.11× and the
checks disagree with the objective, so the constant stays where K5's cross-tier
derivation put it).

Three results are worth more than the table.

**The inner shadow was suppressing a rim that was there all along.** The active
reference's contour is *brighter* than its own body — a rim peak of 0.025…0.129
above baseline, always at one pixel deep — while vitrea read 0.0000 with its peak
8 to 12 px in, meaning it had no edge feature at all. The rim constants were
never the problem; `shadowAlpha` at 0.55 was darkening the contour faster than
the rim lit it. On the inactive bed the reference's own rim read 0.0000…0.0041,
which is what §6.2 recorded as "below the capture's quantisation" — **that
finding described the inactive pose and is withdrawn.**

**Apple's author tint is the seed, not a range of tones.** On three of the five
calibration backdrops the reference's tinted interior is the declared colour
exactly, in linear light, at a per-channel standard deviation of **0.000**:
`systemOrange` renders (1.0000, 0.2961, 0.0000). The tone curve therefore fits to
the identity, and `tintToneLow`/`High` now describe nothing. What makes the tint
work anyway is the composition order Decision Log 12 fixed: over a dark backdrop
the *adaptation* supplies the opacity and the tint supplies the colour, so
`dark-solid__capsule-button__rest-tint-orange` lands at 0.4275 against a
reference of 0.4257 without the tint touching the alpha at all.

**The size bias was decided by a validation cell, against the estimator §5.8 was
fitted on.** The light-versus-dark separation estimator says a 96 pt surface over
the darkest backdrop adapts by 0.30; the reference's own interior level says it
does not (0.4844, against 0.466 unadapted at the refitted alpha and 0.3566
adapted). `impulse__rrect-md__rest` — validation, fitted to by neither — renders
0.2858 against a reference of 0.4358 at the old bias (ΔE 0.02344) and 0.4594 at
the new one (ΔE 0.00378). The estimator's algebra cancels transmission only if
both schemes share one tint alpha, and the refitted profiles are at 0.46 and
0.97, so it is no longer the primary evidence for this constant.

#### The one holdout pass

Read once, on the frozen configuration, over all six profiles and both tiers.
**Every ΔE mean row holds, on every gated profile and both tiers**, with the
worst untinted holdout figure 0.0587 against bounds of 0.07 and 0.08. So does
every silhouette IoU row, every edge-weighted row on the light-standard profiles,
and every row of both reduced-transparency shape tables.

What fails divides cleanly into two mechanisms and one marginal miss, and none of
the three is a number a threshold should absorb.

**(1) The contour rows fail on an instrument artefact, measured.** The CSS tier's
extracted silhouette over a checkerboard carries interior holes, and the contour
metric walks every hole boundary. Counted directly on the captures:

| cell | tier | interior holes, reference | interior holes, vitrea | area recovered | IoU | contour mean / p95 |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__rrect-lg__rest` (holdout) | dom | 0 | **72** | 96.5% | 0.9653 | 15.34 / 65.0 |
| `checkerboard__rrect-md__rest` | dom | 0 | 22 | 96.2% | 0.9617 | 6.59 / 36.0 |
| `checkerboard__capsule-button__rest` | dom | 0 | 6 | 96.2% | 0.9622 | 2.17 / 15.3 |
| the same three | texture | 0 | **0** | 98.9…99.5% | 0.969…0.989 | ≤ 0.91 / ≤ 2.59 |

IoU stays at 0.96 while the contour explodes, which is the signature. The
mechanism is the one §5.8 already named for the tone axis: **the two tiers blur
in different colour spaces** — this renderer in linear light, `backdrop-filter`
in the encoded one. At σ = 8 the checkerboard's 16 px period was washed out; at
the refitted σ = 3 the CSS tier transmits enough of it that interior pixels
coincide with the backdrop's own level and the extractor punches holes.

> **CORRECTED 2026-08-31 — read §5.14 before this finding.** The paragraph after
> the table attributes the deficit to `sizeOcclusionGain` and says vitrea "is not
> too transparent at 32, 44 or 96". Both halves are wrong, and what found it is
> arithmetic on the shipped constants rather than a new measurement.
> `sizeThickness` is `smoothstep(32, 96, span)`, which is exactly 1 for **every**
> span at or above 96 — so a gain on it takes the same value on `rrect-md`
> (span 96), `glass-over-glass` (130) and `rrect-lg` (160) and provably cannot
> separate them. And the deficit is already present at span 96 in *calibration*:
> over `photo` the residual is −0.086 at 96 against −0.102 at 160. The real
> attribution is two other things — the size band's top and the accessibility
> occlusion constants — and it is §5.14. **The measurements below stand; the
> diagnosis does not.** One naming error with them: `rrect-lg` is 280×160 and the
> size law reads `min(width, height)`, so its span is **160**, not 280.

**(2) The largest surfaces fail perceptually, and the reason is a facet the
calibration set could not identify.** Every remaining failure is on a span-160
`rrect-lg` or the `glass-over-glass` stack, and all of them say the same thing:

| profile | tier | cell | reference interior | vitrea | residual |
| --- | --- | --- | --- | --- | --- |
| `1x-light-standard` | texture | `photo__rrect-lg__rest` | 0.6855 | 0.5835 | **−0.102** |
| `1x-light-standard` | texture | `photo__glass-over-glass__rest` | 0.7064 | 0.5381 | **−0.168** |
| `1x-light-reduced-transparency` | texture | `photo__rrect-lg__rest` | 0.8920 | 0.7794 | **−0.113** |
| `1x-light-increased-contrast` | texture | `photo__rrect-lg__rest` | 0.9691 | 0.7833 | **−0.186** |

vitrea is systematically **too transparent at a 160 pt span** (`rrect-lg`, whose
280 is its *width*), and it is not too transparent at 32, 44 or 96. That is exactly `sizeOcclusionGain`, which ships at
0 — and the reason it ships at 0 is that the calibration set cannot identify it:
the size band saturates at 96 and every fit cell sits at or below the band's top,
so the gain has no leverage anywhere in the fit. The per-cell calibration
residuals already pointed the right way (web − reference falls with span in every
backdrop) but the grid was flat to 1.04×.

**This is a holdout falsification of a fitted constant**, and the discipline's
answer is that it cannot be repaired here: the column is spent, and refitting the
gain against the cells that exposed it is the definition of what the holdout
exists to prevent. It needs calibration cells above the band — one or two spans
between 128 and 280 — which is a `scenes.json` addition and a capture session.

**(3) W7's mid-dark holdout misses one bound by 4%.** On
`mid-dark-solid__capsule-button__rest` the texture tier reads OKLab ΔE p95
**0.1775** against the adopted ≤ 0.17, at both scales. Everything else on that
cell is comfortable — SSIM 0.9761, ΔE mean 0.0147, IoU 1.0000, contour 0.000,
cross-tier coherence inside its band — and the dom tier passes. It is the only
adopted bound that the tone axis itself fails, it is 4.4% over, and it is on the
one scene the wave chartered specifically to bind that axis, so it is reported
rather than absorbed.

#### The threshold proposals

**Held wherever they re-verify.** Every ΔE mean row, every IoU row, both
reduced-transparency shape tables, both increased-contrast shape tables and the
cross-tier ΔE coherence row (worst 0.0360 against ≤ 0.05) re-verify against the
active bed at their adopted numbers and are proposed **unchanged**.

**Not proposed as amended — referred instead.** The contour rows and the
large-surface perceptual rows are not re-proposed at looser numbers, because in
both cases the honest fix is a change to something other than the bound: a
topology arm on the conditioning predicate for the first, and a capture session
for the second. Loosening a contour bound to 65 px would be certifying an
extractor artefact as geometry, and loosening SSIM to admit a −0.186 interior
error would be the certify-the-defect move Decision Log 11 refused.

**The conditioning predicate's web-side arm — the ruling §5.12 asked for.**
§5.12 flagged one degenerate web-side cell (`light-solid`, where vitrea's specular
rim crossed the backdrop's level, recovering 4328 px of a 4872 px region with a
ring of holes and a corner curvature of 8.65 1/px) and left the choice between an
exclusion and a predicate to this pass. **The answer is neither, and then a third
thing.**

- The motivating cell is **repaired** by the refit: area recovery 0.888 → 1.000,
  IoU 0.9990, corner curvature 0.0558 against the reference's 0.0558. The inner
  shadow was what pushed vitrea's rim across the backdrop, and it is now 0.05.
- An **area arm would not work**. The cells that now mis-measure recover
  94.8…96.2% of their region — above any floor worth setting — while the eleven
  cells a 0.95 arm would exclude read IoU 0.94…0.98 and measure geometry fine.
- What breaks the metric is **topology, not area**: 72 holes at 96.5% recovery.
  So the proposed arm is a **simply-connected test on both sides' extracted
  silhouettes**, excluding the shape rows where either side's mask has interior
  holes. It is proposed, not built — a new instrument rule belongs to the gate
  that adopts it.

**Corner curvature must not be gated.** No adopted table includes it, and this
pass is the evidence for keeping it that way: on cells whose IoU is 0.96 and
whose area recovery is 0.96…0.99, `cornerCurvatureWeb / cornerCurvatureNative`
reaches 496×, 800× and 8125×. The estimator is unstable in a way that has nothing
to do with area recovery, which is the same conclusion §6.2's rim candidate
reached from the other direction.

**PROPOSED — the tinted cells, holdout-bounded.** The tint has its own axis and
no adopted bound, so these are new tables rather than an extension of the
untinted ones. Bounded by the holdout column, with §5's own margin.

> **SUPERSEDED 2026-09-01 — by a stricter outcome, not by a looser one
> (Decision Log 22, parent ruling at recomposition).** These tables were never
> adopted and will not be. The tinted cells landed in the enforced suite gated by
> the **general light-standard tables**, which are tighter than every row proposed
> below — texture SSIM ≥ 0.88 against the ≥ 0.93 here is the only row where the
> proposal was stricter, and the tinted cells clear the general bound at 0.8647
> only by being floored, not by a separate table. Ten tinted rows are floored as
> UNMET in §5.27.
>
> The wave therefore ships **no tint-specific gate**. That is deliberate: a
> separate table for tinted cells would have set a second, looser standard for the
> feature this wave added, which is the shape of certification Decision Log 11 and
> Decision Log 16 both refused. Holding tinted cells to the untinted bounds and
> recording where they miss is the stricter reading, and it is what shipped.
>
> **One mechanism below is now half of a larger one, and is worth carrying
> forward.** The paragraph on the tinted coherence ceiling attributes the 1.6493
> interior ratio to sRGB gamut clipping in `cssTintColor`, with isolation evidence
> that it is saturation and not opacity. §5.26 later measured the same rows and
> attributed them to backdrop tone sampled without regard to surface size. Neither
> reading is wrong and **W9 should treat them as one problem**: the tone map
> chooses the tint colour, and how saturated that choice is decides how hard the
> CSS tier clips it. That predicts exactly the ranking §5.26 measured — checkerboard
> 1.635, `hc-text` 1.265, `light-solid` 1.243, photo 1.056, untinted solid 1.001 —
> because a bimodal backdrop drives the tone map to the most saturated choice.
> §5.26's charter says the mechanism is in how the backdrop is sampled; this
> section says the damage is done at the gamut boundary. Both are load-bearing.

| axis | metric | texture, proposed | dom, proposed | worst cal+val | worst holdout |
| --- | --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.88 | ≥ 0.92 | 0.9165 / 0.9677 | 0.9358 / 0.9659 |
| shape | contour distance mean | ≤ 1.50 px | ≤ 1.2 px | 0.5577 / 0.4207 | 0.8255 / 0.5715 |
| shape | contour distance p95 | ≤ 4.00 px | ≤ 3.5 px | 2.8284 / 2.8284 | 3.0000 / 2.0000 |
| perceptual | SSIM mean | ≥ 0.93 | ≥ 0.89 | 0.9499 / 0.9503 | 0.9732 / 0.9150 |
| perceptual | OKLab ΔE mean | ≤ 0.10 | ≤ 0.10 | 0.0274 / 0.0241 | 0.0811 / 0.0766 |
| perceptual | OKLab ΔE p95 | ≤ 0.20 | ≤ 0.18 | 0.1736 / 0.1264 | 0.1771 / 0.1567 |
| perceptual | edge-weighted mean | ≤ 0.07 | ≤ 0.07 | 0.0317 / 0.0195 | 0.0449 / 0.0440 |

The ΔE bounds are looser than the untinted tables' and the reason is not the
tint: the worst tinted holdout figure is `photo__rrect-lg__rest-tint-orange`,
which is the span-160 residual of finding (2) wearing a tint. At a 44 px span the
tinted cells read ΔE mean 0.0056…0.0274.

**The tinted coherence ceiling breaks, with a named mechanism.** Cross-tier ΔE is
comfortable on every tinted cell (worst 0.0360 against ≤ 0.05), but the interior
ratio reaches **1.6493** on `checkerboard__capsule-button__rest-tint-blue`
against a band of 0.80…1.25, with 1.3705 and 1.2655 behind it. The cause is
measured and is not the material: a fully saturated tint needs the CSS tier to
declare an `rgba()` colour brighter than sRGB can express, so `cssTintColor`
clips at 255 and the CSS tier renders a weaker tint than the GPU tier. Isolated —
at the same alpha a *shaded* tone lands within 0.07 of one 8-bit code and the
bare seed misses by 5.59, and at C9a's old alpha of 0.62 the bare seed still
missed by 3.82, so it is the saturation and not the opacity. Fixing it means
solving the CSS alpha and colour **jointly** under the gamut constraint instead
of solving the alpha on luminance and deriving the colour. **Named as the next
parent-impact item on this axis; no coherence bound is proposed for tinted cells
until it lands.**

#### What the gate owes a decision on

1. **`sizeOcclusionGain` is falsified at 0 and cannot be refitted here.** The bed
   needs calibration spans above 96; until it has them, vitrea is measurably too
   transparent on large surfaces and three profiles' large-surface rows cannot
   pass.
2. **The contour rows need the topology arm before they can be gated at all**, on
   either tier, at the refitted blur.
3. **W7's mid-dark holdout misses ΔE p95 by 4.4%** (0.1775 against ≤ 0.17) with
   every other row on that cell comfortable. Decision Log 13 kept the curve's
   shape for this wave; this is the first bound it has ever failed, and the
   two-axis rework it was deferred to is the natural home for it.

### 5.14 The adoption round: the span coda is void, and the gate cannot flip yet (2026-08-31)

Decision Log 16 adopted §5.13 in full, chartered a span coda to close the one
falsified constant, and granted W7's mid-dark miss a documented exceedance —
*which was superseded before it was ever exercised: the cell ships **floored**
rather than excused, enforced at 0.1785 against an unmoved ≤ 0.17 claim listed
UNMET in §5.27, because Decision Log 22's floors replaced the exceedance
mechanism wholesale.* This
section is what executing that found. **The instrument work landed; the suite
flip did not**, and the reason is a correction to §5.13's own diagnosis rather
than anything the coda measured — the coda could not run as designed.

#### The coda is void, and it is arithmetic rather than a measurement

The charter was one capture session adding about two calibration spans in the
128–192 band plus a fresh large holdout cell, then a single-constant fit of
`sizeOcclusionGain` with everything else frozen. Both halves fail before a
camera is involved.

**A gain on a saturated curve cannot separate saturated cells.** The size law's
one input is `sizeThickness(span) = smoothstep(sizeSpanMin, sizeSpanMax, span)`
with the band at 32…96, so it is exactly 1 at every span at or above 96:

| span | 32 | 44 | 96 | 128 | 130 | 160 | 192 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| thickness | 0.000 | 0.092 | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** |

`sizeOcclusionGain` enters as `α' = α + g · thickness · (1 − α)`. At thickness 1
that is one number, identical for `rrect-md` (span 96), `glass-over-glass` (130)
and `rrect-lg` (160) — so no value of the gain can move them apart, and new
calibration cells at 128 or 192 land on the same point of the curve the span-96
cells already occupy. They would add cells and no information.

**And the canonical canvas cannot host the band anyway.** Components are centred
on 320×200, so a span of *S* leaves (200 − S)/2 above and below, against a
reference shadow reaching 39–41 px below a light-standard surface (§5.12):

| span | 96 | 128 | 144 | 160 | 176 | 192 |
| --- | --- | --- | --- | --- | --- | --- |
| vertical margin | 52 px | 36 px | 28 px | 20 px | 12 px | 4 px |
| width at `rrect-lg`'s aspect | 168 | 224 | 252 | 280 | 308 | **336 — off-canvas** |

Every span from 128 up clips the reference's own shadow, and 192 does not fit at
all. Nothing "larger than `rrect-lg`" exists to capture as a fresh holdout:
`rrect-lg` is already the largest surface the canvas holds, and its shadow is
already clipped. **No capture session was run.** Spending an activation window
on a fit that arithmetic says is unidentifiable would have been worse than
saying so.

#### What the deficit actually is — two mechanisms, neither of them the gain

**The band's top, not a gain on it.** Past span 96 the reference keeps changing
and vitrea cannot: over `photo` the reference reads 0.6649 at span 96 and 0.6855
at 160, while vitrea reads 0.5787 and 0.5835 — flat, because every facet of the
size law is saturated there. That is `sizeSpanMax` set too low, and it is the one
constant that *would* separate those cells. It also needs no new captures at all:
at a band top of 160 the bed's existing spans spread across the curve rather than
collapsing onto it —

| `sizeSpanMax` | thickness at 44 / 96 / 130 / 160 |
| --- | --- |
| 96 (shipped) | 0.092 / **1.000 / 1.000 / 1.000** |
| 160 | 0.025 / 0.500 / 0.861 / 1.000 |

— though the top would then be set largely by cells at 96 and below, since
`rrect-lg` and `glass-over-glass` are holdout and must stay unfitted.

**The accessibility occlusion constants were never refitted, and that is this
cascade's own gap.** Stage 0 measured the fold under-occluding and §5.11 recorded
it ("the accessibility folds are worse than W1 measured"); no stage then fitted
`increasedOcclusionLift` or `reducedTransparencyFrost`. The consequence is on the
record as a *calibration* residual, not a large-surface one:

| profile | cell | span | set | reference | vitrea | residual |
| --- | --- | --- | --- | --- | --- | --- |
| increased contrast | `photo__rrect-md__rest` | 96 | **calibration** | 0.9566 | 0.7834 | −0.173 |
| increased contrast | `photo__rrect-lg__rest` | 160 | holdout | 0.9691 | 0.7833 | −0.186 |
| reduced transparency | `photo__rrect-md__rest` | 96 | **calibration** | 0.8930 | 0.7768 | −0.116 |
| reduced transparency | `photo__rrect-lg__rest` | 160 | holdout | 0.8920 | 0.7794 | −0.113 |

The two spans miss by the same amount, which is the whole point: this is not a
size effect and the holdout cells are not where it lives. Six of the failing rows
in §5.13's holdout table are this, and it is fittable on calibration cells that
already exist.

#### Why the gate cannot flip

Decision Log 16 adopts "the refit's passing tables". After the topology predicate
below, the rows that still fail are these, and none of them is an instrument
artefact:

| profile | tier | row | worst | bound | mechanism |
| --- | --- | --- | --- | --- | --- |
| `1x-light-standard` | texture | SSIM | 0.8189 | ≥ 0.88 | band top |
| | | ΔE p95 | 0.1944 | ≤ 0.17 | band top |
| | dom | SSIM | 0.6744 | ≥ 0.90 | band top |
| `2x-light-standard` | texture | SSIM | 0.8750 | ≥ 0.93 | band top |
| | | ΔE p95 | 0.1942 | ≤ 0.17 | band top |
| | dom | SSIM | 0.7904 | ≥ 0.92 | band top |
| `1x-light-reduced-transparency` | texture | SSIM | 0.9593 | ≥ 0.96 | accessibility fold |
| | dom | ΔE mean / p95 | 0.0427 / 0.0816 | ≤ 0.04 / 0.07 | accessibility fold |
| `1x-light-increased-contrast` | texture | SSIM / ΔE mean / edge | 0.8509 / 0.0659 / 0.1827 | ≥ 0.86 / ≤ 0.06 / ≤ 0.17 | accessibility fold |
| | dom | ΔE mean / p95 / edge | 0.0758 / 0.1150 / 0.1988 | ≤ 0.07 / 0.09 / 0.18 | accessibility fold |

Enforcing a suite that omits its SSIM and ΔE p95 rows on the flagship profile
would be a weaker gate than the one it replaces, and excluding these cells as
documented exceedances would certify a measured 0.17-of-interior transparency
error as acceptable fidelity — the move Decision Log 11 refused and Decision Log
16 refused again for the tint. So `results/matrix.json` stays where it is, on the
inactive-bed schema-4 gate, for one more round. That is not a good state: the
enforced suite currently gates the shipped material against a *retired*
reference. It is the lesser of the two, and it should not survive another cut.

**One visible consequence.** `apps/demo`'s `site.spec.ts` case "every scene's
figures come from the primary cell" fails on
`dark-solid__capsule-button__rest-tint-orange`, and it is a direct dependent of
this: the demo reads `results/matrix.json`, the tinted scenes are declared in the
scene set, and the inactive-bed matrix has no tinted cells because that bed's
tints carried no colour (§5.10). The adopted constants do not repair it and were
never going to — **the matrix flip is what repairs it**, and the active-bed
matrix carries all twelve tinted cells per light profile. It is red for a
correct reason and goes green with the adoption.

#### The topology predicate, built and measured

§5.13 proposed a simply-connected arm; Decision Log 16 chartered it. It is built:
`silhouetteHoleCount` counts 4-connected runs of region pixels the mask excludes
that never reach the region border, and every cell now records
`silhouetteHolesNative` and `silhouetteHolesWeb` beside its areas. The whole
matrix was regenerated to add them and **20,293 measured values are identical to
the pre-addition run, with zero differing** — so the instrument change is
provably inert, and §5.13's holdout figures are the same measurement rather than
a second spend.

The predicate that follows has three arms — native area ≥ 0.95 of the region, web
area on the same floor, and simple connectivity on the contour rows only (IoU is
a set overlap and a hole is a genuine set difference; the contour trace is the
metric that walks phantom boundaries). Measured, it costs a great deal:

- **101 of 234** shape-bearing cells carry at least one interior hole.
- The contour rows lose **50** cells to the topology arm and **27** to the two
  area arms.
- On `1x-light-increased-contrast` the contour rows end up gating **zero** cells,
  on both tiers. A row that gates nothing is not a gate, so those two rows should
  be dropped from that table rather than kept vacuous.

It does fix what it was built for — with it, the light-standard contour rows go
from failing at 15.34 mean / 65.0 p95 to passing at 0.50 / 4.29 — and the cell it
cannot reach is `hc-text__rrect-md__rest`, which has **no holes at all** and
loses 4–7% of its region to a ragged boundary over high-frequency text, reading a
contour p95 of 24 px at 1× and 34–49 px at 2×.

**A better fix exists and is recommended instead.** The contour metric compares
all traced boundaries; what it means to compare is each mask's *outer* outline. A
contour distance measured between outer contours would be immune to holes by
construction, would need no predicate arm, and would not cost 50 cells. That is a
metric change rather than a gate change — it moves every contour figure in the
matrix and would need its own regeneration and a fresh read — so it is proposed
here rather than taken.

**Corner curvature is never gated, and now for a recorded reason.** No adopted
table has ever included it, and this pass is the evidence for keeping it that
way: on cells whose IoU is 0.96 and whose area recovery is 0.96…0.99, the ratio
`cornerCurvatureWeb / cornerCurvatureNative` reaches 496×, 800× and 8125×. The
estimator's instability has nothing to do with area recovery, so no conditioning
predicate would rescue it.

#### The tint's gamut clip, recorded as a limitation

Decision Log 16 chartered this to the backlog rather than to a fix, and it
belongs beside the tinted tables. A fully saturated author tint drives the
cross-tier interior ratio to **1.6493** against a band of 0.80…1.25, and the
cause is not the material: to reproduce the GPU tier's composite the CSS tier
would have to declare an `rgba()` colour brighter than sRGB can express, so
`cssTintColor` clips at 255 and renders a weaker tint. Isolated to the
saturation rather than the opacity — at the same alpha a shaded tone lands within
0.07 of one 8-bit code while the bare seed misses by 5.59, and at C9a's old alpha
of 0.62 the bare seed still missed by 3.82. The fix is to solve the CSS alpha and
colour jointly under the gamut constraint instead of solving the alpha on
luminance and deriving the colour. **No tinted coherence bound is proposed until
it lands**, and `packages/platform-web/test/tint.test.ts` pins the shortfall so
it cannot drift unnoticed.

#### What one more round needs

Three fits, all on calibration cells that already exist, then **one** fresh
holdout read of the whole configuration:

1. `increasedOcclusionLift` and `reducedTransparencyFrost` — the gap this cascade
   left, worth six of the ten failing rows.
2. `sizeSpanMax` — the band's top, which is what the falsification actually
   names, with `sizeOcclusionGain` refitted after it since the gain only becomes
   identifiable once the curve stops saturating inside the bed.
3. A disclosure that must ride with them: §5.13's holdout column has been read,
   so whoever fits these has seen which holdout cells fail. The fit must be
   declared and gridded before it runs, on calibration cells only, and the
   contamination stated in the record.

### 5.15 Round two, declared before it runs (2026-08-31)

Wave Decision Log 17 upheld both of §5.14's refusals and chartered two things:
the outer-contour instrument, and a round-two fit whose grid and objective are
**written down before the fit executes**. This section is that declaration. It
was committed before any constant moved and before the round-two holdout was
read, so a reader can check what was promised against what was reported.

#### The instrument, landed first

`contourDistance` now measures between each mask's **outer** contour: both
silhouettes are hole-filled before their boundaries are taken. A hole is not part
of an outline, and letting hole walls in made the metric report the extractor
rather than the geometry — `checkerboard__rrect-lg__rest` read a contour mean of
15.34 px beside an IoU of 0.9653.

Regenerated over calibration and validation, **71 contour cells moved and 103 did
not, and not one non-contour value changed** — the change is scoped exactly to
what it should touch. The worst readings collapse: 15.34 mean / 65.0 p95 → 0.605
/ 5.00; 12.99 / 74.0 → 0.762 / 4.00; 12.13 / 40.95 → 1.23 / 2.00.

The topology *arm* §5.14 built is withdrawn from the gate and kept in the record
as the measurement that motivated this. `silhouetteHoles{Native,Web}` stay on
every cell, because filling a hole for the contour's sake must not make the hole
invisible — and IoU still sees it, since a hole is a genuine set difference even
when it is not an outline difference.

#### The conditioning predicate, in final form

Two arms, and **neither introduces a chosen number**:

1. **Area, both sides**: `silhouetteArea{Native,Web} ≥ 0.95 × componentRegionArea`.
   The existing floor, now asked of both sides rather than of the native one alone.
2. **Bodies, both sides**: `silhouetteBodies{Native,Web} ≤ componentRegionBodies`.
   The contour metric compares outlines; a mask the extractor has broken into
   pieces has more outlines than the surface does. The count to beat is the
   *declared region's own*, so a genuinely multi-body component is not penalised —
   `toolbar-group` declares three capsules and its region has three bodies.

The second arm exists because hole-filling does not merge fragments: on
`photo__rrect-md__rest-tint-orange` at 2× the reference is one body and the CSS
tier is four, with the largest fragment sitting inside a ring punched through the
surface's lower-right quadrant. Both counts are recorded per cell, so the
predicate is machine-checkable.

#### The contour bounds, declared

Measured over calibration and validation only, under the predicate above. The
rule: **hold every adopted bound the measurements clear, and amend only where
they cannot** — the G3 amendment doctrine, with an amended value set at the
smallest half-pixel step reaching 1.4× the worst measurement.

| profile | tier | n | IoU worst | mean worst | p95 worst | IoU | mean | p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1x-light-standard` | texture | 22 | 0.9690 | 0.759 | 2.24 | ≥ 0.82 | ≤ 2.5 | ≤ 5.0 |
| | dom | 18 | 0.9565 | 0.604 | 5.00 | ≥ 0.85 | ≤ 2.0 | **≤ 7.0 (amended)** |
| `2x-light-standard` | texture | 21 | 0.9525 | 1.829 | 5.00 | ≥ 0.85 | ≤ 5.0 | ≤ 10.0 |
| | dom | 18 | 0.9584 | 0.762 | 5.00 | ≥ 0.85 | ≤ 4.0 | ≤ 8.0 |
| `1x-light-reduced-transparency` | texture | 6 | 0.9881 | 0.366 | 1.00 | ≥ 0.87 | ≤ 1.5 | ≤ 3.5 |
| | dom | 6 | 1.0000 | 0.000 | 0.00 | ≥ 0.89 | ≤ 1.5 | ≤ 3.5 |
| `1x-light-increased-contrast` | texture | 6 | 0.9768 | 1.159 | 8.20 | ≥ 0.85 | ≤ 1.8 | **≤ 11.5 (amended)** |
| | dom | 5 | 0.9963 | 0.062 | 1.00 | ≥ 0.80 | ≤ 2.6 | ≤ 5.5 |

**Two amendments, each with its measured driver, and neither is an instrument
artefact** — both driving cells are single-bodied and clear the area floor.

- `1x-light-standard` dom p95, 4.0 → 7.0, driven by
  `checkerboard__rrect-md__pressed` at 5.00 with a mean of 0.604 and an IoU of
  0.9565: a localised outline difference over about 5% of the boundary, not a
  displacement of the surface.
- `1x-light-increased-contrast` texture p95, 3.2 → 11.5, driven by
  `photo__capsule-button__rest-tint-orange` at 8.20 with a mean of 1.159 and an
  IoU of 0.9768. **This is the weakest row in the document and is flagged as
  such.** The mechanism is that profile's own border: the increased-contrast
  reference draws a hard border stroke (§5.12 measured its ring-0 occlusion at
  0.560 against a shadow of 0.096), and the extractor localises that stroke
  differently on a tinted capsule than it does vitrea's rim. A gate that would
  rather drop this row than widen it nearly four-fold has a good argument, and
  this section does not pretend otherwise.

#### The round-two fits, declared

**Objective.** `scripts/sweep.ts`'s default interior objective, unchanged: the
mean over calibration cells of `|Δ interior mean| + |Δ interior stdDev| +
|Δ rim peak|` in linear light, with ΔE and SSIM read as checks. Everything not
named below is frozen at §5.13's refit.

**Fit A — the accessibility fold**, the gap this cascade left. One structural
fact shapes it: `increasedOcclusionLift` is the single lift the
`occlusion: "increased"` policy applies, and **both** accessibility profiles
resolve to that policy, because macOS couples the toggles. So one constant serves
two references that want different things — implied alphas of 0.864 under reduced
transparency and 0.945 under increased contrast, needing lifts of 0.748 and 0.898
at the refitted nominal of 0.46. A compromise is the expected outcome here, not a
failure of the fit.

- `increasedOcclusionLift`: 0.4722 (current), 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95
- `reducedTransparencyFrost`: 1.0, 1.75 (current), 2.5, 3.5
- Cells: each accessibility profile's own untinted calibration cells.

**Fit B — the size band**, in this order because the gain is unidentifiable until
the curve stops saturating inside the bed (§5.14's argument):

- `sizeSpanMax`: 96 (current), 128, 160, 192, 224
- then `sizeOcclusionGain`: 0 (current), 0.05, 0.10, 0.20, 0.35
- Cells: the eight tone-inert untinted rest calibration cells of
  `1x-light-standard` — the same set §5.13's base material was fitted on.

**A coupling stated in advance.** Widening the band lowers `sizeThickness` at
span 96, which lowers the tone curve's argument `x = backdrop + bias · thickness`
and therefore *increases* adaptation on the span-96 dark-backdrop cells. The tone
constants stay frozen; that movement is a measured consequence of the band, and
the objective will see it, because `dark-solid__rrect-md__rest` is in the fit set.
If the band's optimum only looks good by breaking the tone axis, the objective
says so rather than hiding it.

**Then one fresh holdout read** of the frozen result, reported against the bounds
declared above.

#### The contamination, stated plainly

§5.13's holdout column **has already been read**, so whoever runs these fits — me
— knows which holdout cells fail and by how much. That cannot be undone. The
declared protocol is the mitigation and not a cure: the grids, the objective, the
cell sets and the bounds above were written and committed before any constant
moved, so a fit steered toward the holdout would show up as a departure from this
section. Anyone auditing it should diff what §5.16 reports against what this
section promised.

### 5.16 Round two, reported against the declaration (2026-08-31)

What §5.15 promised, executed. Staged matrix
`results/2026-08-31-round-two.json` — schema 5, 242 cells, six profiles × both
tiers, all three sets, on the outer-contour instrument. One constant moved. The
holdout was read once. **Nine rows still fail, so this routes to the human gate
rather than to a third round.**

#### What the fits found

**Fit A succeeded, and it was the larger of the two gaps.**
`increasedOcclusionLift` moves **0.4722 → 0.75**. The old value was never a
measurement: it was the pre-C9a absolute floor re-expressed as a fraction so the
new form would reproduce the old behaviour at the old nominal. Against the active
bed it under-occluded badly on both accessibility profiles.

The two profiles disagree about the right lift, exactly as §5.15 predicted they
would, because macOS couples the toggles and one constant serves both:

| lift | increased contrast | reduced transparency | sum |
| --- | --- | --- | --- |
| 0.4722 (shipped) | 0.36045 | 0.10940 | 0.46985 |
| 0.70 | 0.26147 | **0.04875** | 0.31022 |
| **0.75 (chosen)** | 0.24739 | 0.05003 | **0.29742** |
| 0.80 | **0.23366** | 0.06981 | 0.30347 |
| 0.90 | 0.24056 | 0.11082 | 0.35138 |

0.75 is the minimiser of the equal-weight sum, which is the honest tie-break when
one constant serves two equally-gated profiles. `reducedTransparencyFrost` was
swept as declared and is **flat to 1.03× over 1.0…3.5** — unidentifiable, so it
stays at 1.75.

The effect on the interior level is not subtle:

| profile | cell | reference | round one | round two |
| --- | --- | --- | --- | --- |
| reduced transparency | `photo__rrect-md__rest` | 0.8930 | 0.7768 | **0.8930** |
| reduced transparency | `photo__capsule-button__rest` | 0.8927 | 0.7793 | **0.8952** |
| increased contrast | `photo__rrect-md__rest` | 0.9566 | 0.7834 | **0.8970** |
| increased contrast | `photo__capsule-button__rest` | 0.9188 | 0.7860 | **0.8992** |

**Eight failing rows became passing rows**, and every perceptual row on both
accessibility profiles now passes: increased-contrast texture SSIM 0.8509 →
0.8639, ΔE mean 0.0659 → 0.0357, edge-weighted 0.1827 → 0.1133; the dom tier's
ΔE mean 0.0758 → 0.0479, p95 0.1150 → 0.0531, edge 0.1988 → 0.1402; reduced
transparency's dom ΔE mean 0.0427 → 0.0175 and p95 0.0816 → 0.0277.

**Fit B found nothing, and the reason is the same bind one level up.**
`sizeSpanMax` was swept over 96 / 128 / 160 / 192 / 224 and the objective is
**monotone against widening** — 0.09346 at 96 rising to 0.09861 at 224, a 1.06×
spread. `sizeOcclusionGain` then reads 0.09346 at 0 against 0.09341 at 0.05: a
0.05% difference, its fifth boundary result. Both stay where they are.

The cause is structural and worth stating precisely, because it is not "the fit
failed": **the calibration set's largest span *is* the band's current top.** The
eight fit cells sit at spans 32, 44 and 96, so widening the band can only lower
`sizeThickness` at 96 and weaken a size law the objective already likes. The
spans that would separate a band ending at 96 from one ending at 160 — 130 and
160 — exist in this bed **only in the holdout**. §5.14 corrected the deficit's
attribution from the gain to the band; round two shows the band is no more
identifiable from calibration cells than the gain was.

**The flagship profile is bit-identical across round two**, on every perceptual
row of both light-standard profiles at both tiers. `increasedOcclusionLift` is
reached only by an accessibility policy, and that inertness is observed rather
than asserted.

#### The nine failing rows, by mechanism

| # | profile | tier | row | worst | bound | class |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `1x-light-standard` | texture | SSIM | 0.8189 | ≥ 0.88 | band |
| 2 | | texture | ΔE p95 | 0.1944 | ≤ 0.17 | band |
| 3 | | dom | SSIM | 0.6744 | ≥ 0.90 | band |
| 4 | `2x-light-standard` | texture | SSIM | 0.8750 | ≥ 0.93 | band |
| 5 | | texture | ΔE p95 | 0.1942 | ≤ 0.17 | band |
| 6 | | dom | SSIM | 0.7904 | ≥ 0.92 | band |
| 7 | | dom | contour p95 | 10.00 | ≤ 8.0 | declared bound refuted |
| 8 | `1x-light-reduced-transparency` | dom | contour p95 | 5.00 | ≤ 3.5 | declared bound refuted |
| 9 | | texture | SSIM | 0.9595 | ≥ 0.96 | marginal |

**Rows 1–6 are the band, unchanged and unmovable here.** Every one is on
`checkerboard__rrect-lg__rest` (span 160) or a `glass-over-glass` cell (span
130) — the two holdout scenes whose spans lie above the band's top, which is
precisely why they are the cells that expose the deficit and precisely why they
cannot be fitted to.

**Rows 7 and 8 are the pre-registered bounds doing their job.** §5.15 declared
the contour bounds from calibration and validation alone, because DL17 required
the declaration to precede the holdout read. The holdout refuted two of them, on
their first-ever read under the outer-contour metric: `2x-light-standard` dom p95
reads 10.00 device px on `checkerboard__glass-over-glass__rest` against a
declared 8.0 (cal+val was 5.00), and `1x-light-reduced-transparency` dom p95
reads 5.00 on `hc-text__capsule-button__rest` against a declared 3.5 (cal+val was
0.00). Both are single raster steps at their scale.

**These two are deliberately not amended here.** Widening a bound after seeing
the holdout figure that broke it is exactly the contamination §5.15's protocol
exists to prevent, and doing it silently would make the pre-registration
worthless. They are reported as refuted and routed to the gate.

**Row 9 misses by 0.0005**, on `photo__toolbar-group__rest`, a validation cell,
against a bound adopted on the inactive bed. Round one read 0.9593 and round two
0.9595. It is a calibration-side figure, so proposing an amendment does not
consume anything: **≥ 0.95 is the honest active-bed value**, on the same G3
doctrine as §5.15's two amendments, and the gate can take it or leave the row
failing.

#### What this round did and did not change about the adoption

The accessibility half of §5.14's blocker is **closed**. The band half is not,
and it now has a sharper name: not a missing gain, and not a bound that needs
widening, but a bed whose calibration cells cannot see the span range where the
deficit lives. Closing it needs one of three things, and all three are the gate's
to choose:

1. **Give the band calibration cells between 96 and 160.** The canvas can host a
   span of 128 (36 px of vertical margin), at the cost of clipping the
   reference's own shadow below it — so the cell would carry a material axis and
   no usable shadow axis. That is a real trade rather than a free win.
2. **Enlarge the canonical canvas**, which §5.7 already named as the thing the
   scatter gain would need too, and which re-beds every fixture.
3. **Accept the band at 96 and record the large-surface deficit as a measured
   limitation**, gating the flagship profile's SSIM and ΔE p95 rows on the cells
   that are not above the band. That is the only one of the three that needs no
   captures, and it is also the one that narrows what the claim covers.

`results/matrix.json` is unchanged, the gate has not flipped, and the demo's
`site.spec.ts` tinted-cell assertion stays red for the reason §5.14 gives.

---

### 5.17 The span-128 round: blocked at the capture, with two findings that did not need one (2026-08-31)

Wave Decision Log 18 chartered a span-128 calibration cell, adopted three bounds
at their measured values, and cleared the flip to execute on a clean report. **The
capture cannot run: the machine's login session is locked.** Two of DL18's own
instructions produced results anyway, and one of them is a defect in the
committed record.

#### The blocker, measured rather than inferred

Probed through the existing build, before any rebuild — deliberately, because a
rebuild invalidates the TCC grant and there would have been no way back:

```
window canBecomeKey: true, isKeyWindow: false, isMainWindow: false, NSApp.isActive: false
ScreenCaptureKit: BLOCKED
```

And the session state that explains both, read three times over eighteen seconds
and stable every time:

```
CGSSessionScreenIsLocked -> true      kCGSSessionOnConsoleKey -> true
pmset assertions: UserIsActive 0
```

The harness is not at fault, and its Decision Log 14 fixes are all present: the
window subclass returns `canBecomeKey: true`, the activation policy is
`.regular`, and `Capture.present` calls `NSApp.activate(ignoringOtherApps:)`
before `makeKeyAndOrderFront`. A locked session refuses the activation and blocks
ScreenCaptureKit. A capture taken in this state would record the **inactive**
material — the exact defect Decision Log 14 exists to prevent — so it was not
attempted. Per DL18's own instruction this is reported rather than retried, and
nothing was rebuilt, so the TCC grant is intact for whenever the session unlocks.

#### The finding DL18's verification instruction caught

DL18 said of the span-128 cells: *"these cells carry a material axis and NO shadow
axis (the instrument records it absent — verify it does, don't assume)."*
Verified, on cells already in the bed, and **it does not.**

`photo__rrect-lg__rest` has a span of 160 on a 200 px canvas, so 20 px of margin
against a reference shadow reaching 33–37 px below. The instrument reports that
cell's shadow as a measurement — extent below 33 px, sigma 15.86, amplitude 0.17 —
with no absence and no caveat. The truncation biases it visibly:

| backdrop | span | margin | sigma | extent below |
| --- | --- | --- | --- | --- |
| `photo` | 96 | 52 px | 17.31 | 36 |
| `photo` | 130 | 35 px | 17.52 | 35 |
| `photo` | **160** | **20 px** | **15.86** | **33** |
| `checkerboard` | 96 | 52 px | 17.75 | 37 |
| `checkerboard` | 130 | 35 px | 17.69 | 38 |
| `checkerboard` | **160** | **20 px** | **17.55** | **35** |

Sigma falls 8% on `photo` at the clipped span while the two unclipped spans agree
within 1%, and the same cell reads 31.93 at 2x against 34.8–35.8 elsewhere. **This
is in the committed record now**, for `rrect-lg` and less severely for
`glass-over-glass`.

> **Correction (2026-08-31).** The sentence that stood here added "— §5.12's
> shadow table quotes those figures as measurements of the reference." It does
> not. §5.12's shadow table is calibration and validation only, its holdout
> column was never opened, and neither scene appears in it; the figures above are
> read from the holdout-bearing staged matrices and this section is the only
> place they were ever quoted. The finding is unaffected — the biased readings
> were in the committed matrices — but the pointer was wrong.

The guard needs no new constant: an extent walk that reaches the canvas edge has
been truncated, and a truncated field must record the shadow axis **absent**, on
the same "absent, never zeroed" discipline the axis already applies where the
backdrop cannot support a ratio.

> **Landed (2026-08-31), after the session lock stopped the capture.** The guard
> is in `metrics/shadow.ts`, pinned by two synthetic reads of one shadow in two
> windows, and `results/2026-08-31-round-two.json` is re-measured through it from
> the same captures with no constant touched. It withdraws 32 cells' worth of
> extents, **every one of them holdout**, and moves nothing on any calibration or
> validation cell — those clear the frame by at least 51.5 device px. The full
> account, the new `clearance*` figures and the derivation of the one-ring guard
> band are in §5.12's dated correction.

**It also refines DL18's premise, and the guard then refines the refinement.** A
span-128 component leaves 36 px of margin, which is *more* than the 35 px of the
`glass-over-glass` cells whose fitted sigma is within 1% of unclipped — so the
cell was expected to carry a **usable-but-marginal** shadow axis rather than none.
Half of that survives the guard and half does not, and the split is worth stating
before the capture rather than discovering it after:

- **σ and the amplitude survive**, and that part of the refinement stands. It is
  a measurement: at margin 35 the fitted σ is within 1% of the roomy cells, and
  36 px is more margin than that.
- **The extent below will be withdrawn.** The guard truncates a side when the
  ring that ended the walk is not wholly inside the clearance, the reference
  reaches 33…37 px down, and a span-128 component's clearance is 35.5 px. So the
  instrument will very likely record the downward extent absent on exactly these
  cells — which is what DL18 predicted, arrived at by a different route, and the
  reason its instruction was to verify rather than assume. The guard has already
  done this to the margin-35 `glass-over-glass` cells: their σ is untouched and
  their extent below is gone.

**The bar stands either way.** These cells are barred from every shadow-constant
fit — not because the axis is unmeasurable on them, but because a band cell whose
margin sits at the edge of where the bias sets in is the last place a shadow
constant should be estimated from. Recorded here as part of the declaration, so
the bar is a commitment made before the numbers exist rather than a choice made
after seeing them.

#### The span-128 cells, declared before capture

Per DL18 ruling 1, declared here so the session is a paste rather than a design.
**A plan, not a change** — `scenes.json` is untouched, because a declared scene
with no fixture puts the tree's declared bed and its captured bed out of
agreement.

One new component, sitting between `rrect-md` (span 96) and `rrect-lg` (160):

```jsonc
"rrect-ml": {
  "kind": "rrect", "size": [224, 128], "radius": 27,
  "$comment": "The band's calibration point. sizeThickness saturates at sizeSpanMax = 96, so every existing calibration cell sits at or below the band's top and the band cannot be identified from them (claims 5.16). Span 128 is the largest this 320x200 canvas carries with the reference's own shadow substantially intact: 36 px of vertical margin against a downward reach of 33-37 px, comparable to the margin-35 glass-over-glass cells whose fitted sigma is within 1% of the unclipped value. Expect the truncation guard to withdraw the downward extent here (clearance 35.5 px against that reach) while sigma and amplitude survive; that is the instrument working, not a defect in the cell. r/min = 0.211 matches rrect-md's 0.208 and rrect-lg's 0.2125 and stays well under Apple's 0.327 saturation point, so corners remain comparable across the sweep (S2). The shadow axis on this cell is marginal by construction and must not be used to fit a shadow constant."
}
```

Six native cells, three backdrops by two profiles, chosen so the 96 to 128
comparison is like-for-like against the three `rrect-md` cells already in the
tone-inert calibration set:

| profile | scenes | split |
| --- | --- | --- |
| `apple-macos-26.5-1x-light-standard` | `checkerboard__rrect-ml__rest`, `photo__rrect-ml__rest`, `light-solid__rrect-ml__rest` | calibration |
| `apple-macos-26.5-2x-light-standard` | the same three | calibration |

2x is included because three of the six failing flagship rows live there. No
holdout cell is added: the holdout already carries the spans the band needs to be
tested at (130 and 160), and adding one would spend a fourth read on a column
this cascade has already read three times.

#### The band fit, declared before it runs

Same protocol as §5.15 and the same objective — `scripts/sweep.ts`'s default
interior objective, with everything not named below frozen at the round-two state,
`increasedOcclusionLift` 0.75 included.

- `sizeSpanMax`: 96 (current), 112, 128, 144, 160, 192
- then `sizeOcclusionGain`: 0 (current), 0.05, 0.10, 0.20, 0.35
- Cells: the eight tone-inert untinted rest calibration cells of
  `1x-light-standard` **plus the three new span-128 cells**, and the 2x set for
  the 2x profile's own fit.

**The contamination lineage, stated plainly.** §5.13 read the holdout column once
and §5.16 read it a second time; the span-128 round would be the **third read**.
Every read has been of a frozen configuration and no holdout cell has ever been
fitted to, but the fitter has now seen that column three times and knows exactly
which cells fail and by how much. The declaration is the only mitigation there is,
and it is weaker on a third read than it was on a first.

**The outcome is also bounded in advance.** Even a perfectly fitted band cannot
reach `rrect-lg`: span 160 sits above any band top this canvas can calibrate, so a
residual there is expected and ships as a measured limitation on the flagship
claim, scoped to the rows and spans it actually covers.

#### The three bounds, gate-adopted post-read

Decision Log 18 ruling 2, recorded here and carried into the tables when the suite
flips. **These were never pre-registered**: §5.15 declared bounds from calibration
and validation, the holdout refuted two of them, and the gate adopted all three
afterwards with its reasons on the record. Marking them any other way would
misrepresent the protocol.

| profile | tier | row | was | now | the gate's recorded reason |
| --- | --- | --- | --- | --- | --- |
| `2x-light-standard` | dom | contour p95 | 8.0 | **10.0** | raster-step quantisation of a p95 |
| `1x-light-reduced-transparency` | dom | contour p95 | 3.5 | **5.0** | raster-step quantisation of a p95 |
| `1x-light-reduced-transparency` | texture | SSIM | 0.96 | **0.95** | inactive-bed provenance; 0.9595 measured |

With these adopted, **three of round two's nine failing rows close**. The
remaining six are the band, on `checkerboard__rrect-lg__rest` and the
`glass-over-glass` cells — which is what the blocked capture was for.

#### Where this leaves the adoption

DL18 cleared the flip to execute "after the span-128 round reads". It has not
read, so the flip's precondition is unmet and `results/matrix.json` is unchanged.
Shipping the six band rows as a measured limitation *without* attempting the
chartered fit would be presuming that fit's outcome, which is the one thing it
exists to avoid.

What the session needs, in one line: **unlock the machine and leave it unlocked.**
Then the chain runs autonomously — rebuild, TCC re-grant, three runs per profile
with 2-of-3 plurality and `presentedActive` attested per cell, web captures, the
declared band fit, one holdout read, and the flip.

### 5.18 The capture ran, and it found the reference bed is bistable (2026-08-31)

The session unlocked at 04:41 and the chain was armed. It got two steps in and
stopped on a stop condition, and what stopped it is not about span 128 at all: on
the evidence below, **`__pressed` has almost never been captured on this bed, and
two cells of one profile changed appearance between runs of a single session.**
Nothing was fitted, nothing was flipped, and the committed bed is restored
byte-exactly. The section is the finding.

#### What ran, and what it cost

The gate was probed through the **existing** build before anything was touched,
because a rebuild invalidates the TCC grant and there is no way back from that
without a human at the machine:

```
window canBecomeKey: true, isKeyWindow: true, isMainWindow: true, NSApp.isActive: true
ScreenCaptureKit: OK 320x200 — the material path is available
```

**And the rebuild turned out to be unnecessary.** `loadSpec()` reads
`$ROOT/scenes.json` at run time (`Sources/main.swift:44`), and `ROOT` is derived
from `#filePath` against a source tree that has not moved, so extending the scene
matrix is pure data: the binary that already holds the grant reads the new scenes
on its next launch. Every plan since Decision Log 16 has budgeted a rebuild and a
TCC re-grant for a scene addition, and neither is needed. That is worth knowing
before the next session is designed around a risk it does not have.

`scenes.json` was extended exactly as §5.17 declared it, and phase 1 ran: three
capture runs over `1x-light-standard` and `1x-dark-standard` (54 cells each) with
20 s between them, then the 2-of-3 plurality. It came out clean on its own terms
— **51 cells kept from run G, 3 restored on an E = F plurality, 0 unresolved,
`presentedActive` true on every fixture of every profile** — and the three
`rrect-ml` fixtures captured without complaint.

#### The bed moved, and only on three cells

Against the committed bed, the fresh capture differs on exactly three PNGs, all
in `1x-light-standard`:

| cell | max delta | what moved |
| --- | --- | --- |
| `dark-solid__capsule-button__rest` | 1 code on 2 px | noise, on the cell that is pixel-identical to its background anyway |
| `checkerboard__toolbar-group__rest` | **48** | all three capsule interiors +32 codes (204.9 / 204.0 / 203.2 → 236.6 / 236.3 / 235.9); the surround's darkening against its own background weakens from −0.99 to −0.33 |
| `photo__capsule-button__pressed` | **48** | interior 201.44 → 234.49; surround darkening −0.85 → −0.29 |

The same **+32…33 code brightening of the glass body with a weaker outer shadow**,
on two different backdrops. It is not the inactive pose: the retired inactive
bed's own `photo__capsule-button__pressed` reads 203.69 interior — within 2 codes
of the *active* rest cell — and the new capture differs from it by 57.

**The second one flipped mid-session.** Per-run digests on
`photo__capsule-button__pressed`:

| run | digest | reads as |
| --- | --- | --- |
| E | `6a125e3fc28b` | **identical to the committed bytes, and to `photo__capsule-button__rest`** |
| F | `20e88e3fe31c` | the brightened appearance |
| G | `20e88e3fe31c` | the same |

Same binary, same settings, same window, twenty seconds apart. The plurality
doctrine then did what it is built to do and took F = G as the cell's state — but
this was not noise being averaged out, it was a **bistable state being settled by
majority vote**. `checkerboard__toolbar-group__rest` agreed across all three runs
of this session and disagrees with the previous one, which is the same phenomenon
observed one session out.

#### The structural half: `__pressed` is a duplicate of `__rest`

Checking the whole committed bed rather than the two cells that moved:

**Eleven of the twelve `__pressed` fixtures are byte-identical to their `__rest`
twin.** Not close — the same SHA-256. It holds at `HEAD`, at `973fd7e` where the
active bed landed, and in the retired **inactive** bed before it. The single
exception, in every one of those three states, is
`2x-dark-standard / photo__capsule-button__pressed`.

So the pressed pose has essentially never been in this bed, and the one cell that
does carry it is the one the coherence axis's dark-and-pressed tier split was
found on. What the fitted sets actually contain:

| cell | set | byte-identical to | that cell's set |
| --- | --- | --- | --- |
| `checkerboard__capsule-button__pressed` | calibration | `checkerboard__capsule-button__rest` | calibration |
| `checkerboard__rrect-md__pressed` | calibration | `checkerboard__rrect-md__rest` | calibration |
| `photo__capsule-button__pressed` | **validation** | `photo__capsule-button__rest` | **calibration** |
| `photo__rrect-md__pressed` | **validation** | `photo__rrect-md__rest` | **calibration** |

Two consequences, and the second is the serious one. Any objective or table that
averages over the calibration set has been counting two of its scenes twice. And
**two of the validation set's cells are byte-copies of calibration cells**, so on
those two the self-check has been reading the fit's own training data and could
not have failed. That is a defect in the anti-overfitting split itself, not in
any constant fitted under it.

#### Why this stopped the chain rather than being noted in passing

Three reasons, and each on its own is a stop condition this cascade was given:

- **A calibration cell moved by 48 codes.** `checkerboard__toolbar-group__rest` is
  in the calibration set, so every constant round one and round two fitted was
  fitted against bytes that the machine no longer reproduces. Running the band fit
  on the new bed would be fitting one increment on top of a bed that shifted
  underneath the rest of the stack.
- **The bed is bistable and the doctrine cannot see it.** Plurality resolves three
  runs by majority, which is right for noise and wrong for a state flip. A bed
  frozen by majority vote on a bistable cell is not the reproducible reference the
  flip is supposed to enforce against.
- **The split defect is the gate's to rule on.** Whether the validation set's two
  duplicate cells are repaired, replaced or recorded as a limitation changes what
  every "confirmed on held-out data" sentence in this document means.

#### What was done with it

The committed bed is **restored byte-exactly** (`git checkout -- apps/reference-apple`),
`scenes.json` is back to its declared-but-unextended state so the declared and
captured beds stay in agreement, and `results/matrix.json` is untouched as it has
been throughout. The captured run is preserved outside the repository at
`/Users/new/.claude/jobs/5c70e47f/tmp/dl18-evidence/` — run E's and run G's
`photo__capsule-button__pressed`, run G's `checkerboard__toolbar-group__rest`, the
three `rrect-ml` fixtures and run G's manifest — and the whole phase is
reproducible in about eleven minutes on an unlocked session, now that the rebuild
is known to be unnecessary.

The span-128 round is therefore still unrun, and it is no longer the first thing
in the queue.

### 5.19 Decision Log 19, built and declared before the bed is materialised (2026-08-31)

§5.18's two findings were adjudicated the same day. Ruling 1 retires the pressed
cells from every fitted and checked role; ruling 2 gives the materialisation step
a way to tell a noisy cell from a two-state one. **Both are written here before
the runs they will be applied to have been looked at**, on the protocol §5.15
established: the rule is committed, then the data decides, rather than the other
way round.

#### Ruling 2, the bimodality arm

The doctrine it amends took three runs of a cell and published whichever bytes at
least two of them shared. That is right for noise — a wrong answer scattered
around a right one, where a majority finds the right one — and wrong for a state.
On `photo__capsule-button__rest`'s pressed twin the runs split one against two
between two *settled* appearances 32 codes apart, and the majority rule named a
winner and recorded nothing.

The evidence the old rule never used is already in the manifest: **the harness
captures every cell twice and attests it `deterministic` when the two agree.** A
variant that is settled inside its own run is a value the machine returns on
purpose. So the arm asks two questions before it counts anything.

1. **Is each variant settled?** Every run that produced it must have attested the
   cell byte-stable. Absent attestation counts as unsettled: this wants a positive
   claim, not silence read as one.
2. **Do they differ structurally?** Two summaries decide it, both over the whole
   raster, against the leading variant:
   - `maxDelta ≤ 1` — **incidental.** One 8-bit code is the raster's own
     quantisation step. This is a floor, not a tolerance: there is no appearance
     that lives half a code away from another one.
   - otherwise `coherence ≥ 0.5` — **structured**, where coherence is the fraction
     of changed pixels having a 4-neighbour that also changed. Isolated speckle
     scores 0 by construction; any contiguous region past about 4×4 px scores
     above 0.8, because a region's interior grows as its area and its boundary as
     its perimeter. The cut is the midpoint of a separation, not a level anything
     sits near, and every classification prints its measured coherence so the
     separation stays checkable.

A cell whose settled variants differ structurally is **STATE-AMBIGUOUS**: nothing
is published for it and the run stops. Structure is tested *before* the count, so
a 2–1 split cannot publish whichever state happened to win two runs. A cell whose
variants differ only incidentally resolves by majority exactly as before, and a
cell with no plurality at all is refused as it was.

Two things fall out that are worth naming. The arm never publishes bytes from one
run under **another run's manifest entry** — the old script restored a PNG from
run E and left run G's checksum and attestations describing it, which no reader
could have caught. And a role is re-derived from the scene matrix at
materialisation, with every change printed, because a role is a property of the
declaration and cannot change a pixel.

Pinned by nine cases in `test/plurality.test.ts`, including the two the ruling
names: a cell where the odd run out differs by 6 codes on four isolated pixels
still resolves by majority, and a cell where it differs by 32 codes over a
contiguous block refuses and names both variants. Two more guard the edges — a
whole region off by a single code stays incidental, and a variant its own run
never settled is not evidence of a second state.

**What it will do to the new runs is not known as this is written.** If any
`rrect-ml` cell comes back state-ambiguous, that is a finding about the band's
own cells and it routes to the gate rather than being resolved here.

#### Ruling 1, the recorded role

Four scenes — `checkerboard__capsule-button__pressed`,
`checkerboard__rrect-md__pressed`, `photo__capsule-button__pressed` and
`photo__rrect-md__pressed` — leave `calibration` and `validation`. They are not
deleted: they stay declared, captured and committed, because they are the only
cells that could ever answer the pressed question and §5.18's evidence is what
the next wave's charter will be built on.

They need a role that says "in the bed, in no set", and that was previously
unsayable — which is exactly how they came to hold a fitted one. So the split
gains a fourth role, **`recorded`**: captured, committed, measurable, and read by
no fit, no self-check, no bound and no claim. It is opt-in twice over — not in
`compare`'s default sets, and not in the sweep's calibration filter.

The Swift spec loader gains it too, checks it *first* in the role lookup so a
scene retired from tuning cannot keep an old membership by being named twice, and
now **fails the load when a scene appears in two lists at all** — a role decided
by the order of an if-chain is the same class of defect as an unassigned scene,
and it only became reachable once there was a fourth role to move a scene into.

Three tests pin the ruling: every pressed scene holds `recorded`, none holds a
fitted or checked role, and each of their rest twins is still in a set and
unmoved. The dedupe removes the duplicate, not the measurement.

**Every held-out claim in this document is re-scoped to rest cells by this
ruling**, and §5.20 states what that costs: the two validation cells that were
byte-copies of calibration cells were never evidence, so removing them does not
weaken the self-check — it stops it overstating.

### 5.20 The arm's first reading: five calibration cells are bistable (2026-08-31)

§5.19's rule, applied to the runs it was written before. The capture chain ran
and did not finish, and what stopped it is the same phenomenon §5.18 found, an
order of magnitude larger than it looked.

#### What ran

The session was unlocked and the gate probed open **through the existing build**,
before anything was touched: `isKeyWindow: true`, `NSApp.isActive: true`,
`ScreenCaptureKit: OK`. The scene matrix was extended with the three `rrect-ml`
cells exactly as §5.17 declared them, and phase 1 began — three runs over
`1x-light-standard` and `1x-dark-standard`, 54 cells each, twenty seconds apart.

**Run G never published.** The harness refused it, on its own guard:

> The author tint did not reach the material in this run. Byte-identical captures
> declaring different seeds: `checkerboard__capsule-button__rest-tint-orange` and
> `…-tint-blue` are byte-identical (same scene, tints 'orange' vs 'blue').

That is the defect of §5.10 — the one Decision Log 14's active-pose re-baseline
was believed to have closed. Runs E and F, minutes earlier on the same binary,
carried their tints and published. **So the tint reaching the material is not
fixed and not broken; it is intermittent**, and the committed bed's tinted cells
are a draw from that process that happened to come up carrying colour.

Nothing was retried. Re-running until the tint guard passes would select the
state the guard exists to detect, which is the contamination §5.19's arm was
built to stop, not a way around it.

#### What the arm said about the two runs that did publish

Both runs attest **every one of their 54 cells `presentedActive: true` and
`deterministic: true`** — the app was active, the window was key, and each cell
was captured twice and agreed with itself. There is no unsettled reading here to
blame.

They disagree on nine cells. Run through `cli/materialize.ts`:

```
54 cell(s) over 2 profile(s) from 2 run(s): 45 unanimous, 0 voted, 9 refused (8 state-ambiguous)
```

| cell | role | maxDelta | px changed | coherence |
| --- | --- | --- | --- | --- |
| `1x-light` `photo__toolbar-group__rest` | validation | 48 | 23000 | 1.000 |
| `1x-light` `photo__capsule-button__rest-tint-orange` | calibration | 20 | 19271 | 1.000 |
| `1x-light` `hc-text__capsule-button__rest` | **holdout** | 47 | 14527 | 1.000 |
| `1x-light` `checkerboard__toolbar-group__rest` | calibration | 48 | 14326 | 1.000 |
| `1x-light` `photo__rrect-md__rest` | calibration | 6 | 12571 | 0.977 |
| `1x-light` `checkerboard__capsule-button__pressed` | recorded | 48 | 12424 | 1.000 |
| `1x-dark` `checkerboard__capsule-button__rest` | calibration | 50 | 4940 | 1.000 |
| `1x-dark` `checkerboard__capsule-button__rest-tint-orange` | calibration | 18 | 4940 | 1.000 |
| `1x-light` `dark-solid__capsule-button__rest` | calibration | ≤ 1 | — | *incidental* |

**The declared thresholds separated the two populations without being tuned to
them.** Every structured cell came back at coherence 0.977 to 1.000; the single
disagreement the arm called incidental is the cell that is pixel-identical to its
own background, differing by one 8-bit code. Nothing landed anywhere near the 0.5
cut, which is what §5.19 predicted and the reason the number does not carry
weight.

**Five of the eight are calibration cells**, one is validation, and one is
**holdout** — `hc-text__capsule-button__rest`, a cell the doctrine says may be
read exactly once. One of the five, `photo__rrect-md__rest`, is among the eight
tone-inert untinted rest cells the base material was fitted on in §5.13. **The
bed the whole cascade fitted against is bistable in the cells it fitted on.**

**And neither run is the good one.** Of the differing cells, `checkerboard__`
`toolbar-group__rest`, `photo__rrect-md__rest`, `checkerboard__capsule-button__rest`
and three others match the committed bed on run E, while `photo__toolbar-group__rest`
and `hc-text__capsule-button__rest` match it on run F. The state is drawn per
cell, per run — not a pose the whole capture falls into and not a run that went
wrong.

#### The one clean result

The three span-128 cells — `light-solid__`, `checkerboard__` and
`photo__rrect-ml__rest` — came back **byte-identical across both runs**. The
band's own new cells are stable. They are not published, because a bed cannot be
half-materialised around eight cells that cannot be resolved, but the capture
that was blocked in §5.17 and again in §5.18 is not what failed here.

#### A confound this data cannot separate

A `UserIsActive` power assertion naming the internal keyboard and trackpad began
at **06:08:49 — during run G** — and was still held when the chain was inspected
at 06:11:39. Somebody was at the machine while the chain ran. That cannot be
separated from the material's own behaviour with these runs, and it does not
explain the nine-cell split between runs E and F, which finished at 06:02:57 and
06:06:36 respectively, before the assertion began. It is recorded because it is
true, because "the session is unlocked" and "the session is undisturbed" are
different claims, and because an autonomous capture chain needs the second one.

#### What this stops, and what landed anyway

Decision Log 19's steps 3 to 6 — dedupe, refit-compare, the band fit, the flip —
all need a bed. There is no reproducible bed to fit on, so none of them ran, and
**`results/matrix.json` is untouched** as it has been throughout this cascade.
The committed bed is restored byte-exactly and the `rrect-ml` scenes are withdrawn
from the declaration, because a declared scene with no published fixture puts the
declared and captured beds out of agreement — the same reason §5.17 kept them a
plan.

What did land is everything that does not need a bed: §5.19's bimodality arm and
its nine pins, the `recorded` role, and ruling 1's re-declared partition — 17
calibration, 6 validation, 10 holdout, 4 recorded, no scene unassigned and none
named twice. The arm's first act was to refuse to publish, which is the outcome
it exists to make possible.

One cost to name plainly: the spec loader had to learn the fourth role, so the
harness was rebuilt, and **the rebuild invalidated the Screen Recording grant**
(`ScreenCaptureKit: BLOCKED` on the post-build probe, with the window still key
and the app still active). The next capture session needs Screen Recording
removed and re-added for `VitreaReference` before it can start. The evidence for
this section — both runs whole, run G's refusal and its log — is preserved at
`/Users/new/.claude/jobs/5c70e47f/tmp/dl19-evidence/`.

### 5.21 The stability study, declared before it runs (2026-08-31)

Decision Log 20 puts the study before everything else and makes its product a
capture-protocol doctrine. This section is the declaration: hypotheses,
predictions, and what would refute each, written before a single study run
exists. One of the predictions needed no new evidence and is **tested here, in
the same breath it is declared** — the result is below, including the part that
does not go the way DL20's working hypothesis expects.

#### What the existing data already says

Three facts, all read off the two runs of §5.20 and the harness source.

**The capture order was identical in all three runs.** `interleaved()` sorts by a
written-out FNV-1a hash of the cell key, deliberately, because "Swift's string
hashing is seeded per process … a capture order that changes between runs is not
comparable between runs". So the path through the matrix was *the same path*
every time. **A hysteresis driven purely by scene order therefore cannot explain
run-to-run disagreement**, because the order did not vary. Whatever varies is
either the state the run begins in, or something that is not the path.

**The disagreeing cells are scattered, not contiguous.** Positions 0, 2, 4, 21,
32, 34, 49, 50 in a 54-cell order. A single uncontrolled initial state carried
forward by hysteresis would produce a *prefix* of affected cells, and this is not
one — but three of the eight sit in the first five captured, against five in the
remaining forty-nine. Under a uniform null that is **P(≥3 in the first 5) =
0.019**, and it widens to 0.086 by the first eight, so it is a start-of-run
effect rather than a general position effect.

**The harness already knew.** The settle loop carries this comment, dated
2026-08-29: *"the material's tone adaptation is an animation over seconds … under
concurrent system load, individual cells flipped between an adapted and a
mid-adaptation byte state across runs (max deltas 31–36/255), while every run's
paired captures agreed."* That is §5.20's finding, found two days earlier, with
the same magnitudes. The fix then was to dwell 1.75 s and require two captures a
second apart to agree. **It is not sufficient, and the reason is visible in its
own shape: it tests whether the image stopped moving, not whether it converged to
the same place.** Two captures a second apart agree in either attractor.

#### H2, tested now: not supported as stated

DL20 predicts the bistable cells cluster on mid-luminance backdrops. Against the
eight state-ambiguous cells:

| backdrop | ambiguous / total | character |
| --- | --- | --- |
| `checkerboard` | 4 / 15 | structured, mean ≈ 0.5 |
| `photo` | 3 / 19 | structured, mean 0.214 |
| `hc-text` | 1 / 3 | structured, high local contrast |
| `impulse` | 0 / 4 | structured, overwhelmingly dark |
| `light-solid` | 0 / 4 | uniform 0.891 |
| `dark-solid` | 0 / 7 | uniform 0.0117 |
| `mid-dark-solid` | 0 / 2 | uniform 0.0595 |

**Mean luminance does not order this.** `photo` at 0.214 and `checkerboard` at 0.5
both flip; `mid-dark-solid` at 0.0595 sits between `dark-solid` and `photo` and
does not. What the eight do share is that **every one of them sits on a spatially
non-uniform backdrop, and none on a uniform one** — 0 of 13 uniform-backdrop
cells against 8 of 41 structured ones. Under a uniform null that is P = 0.092:
suggestive, not significant, on n = 13. `impulse` is the case that keeps it
honest, being structured and stable, though its structure is sparse and dark.

So H2 is replaced rather than confirmed, and the replacement is a prediction the
study can settle.

#### The hypotheses, and what refutes each

- **H1 — a neutral reset before each cell collapses the bistability.** Prediction:
  across eight interstitial-protocol runs, cells classified bistable fall to zero
  or near it, while the same cells are bistable across eight baseline runs.
  *Refuted if* bistability survives the interstitial at a similar rate — which
  would mean the state is not inherited from the previous cell at all.
- **H1b — order permutation moves the set.** Prediction: under permuted baseline
  orders, *which* cells are bistable changes. **This one is already in tension
  with the record**: the order never varied and the set still varied, so if
  permutation moves the set it is via position-in-run, not via which scene came
  before. *Refuted if* the bistable set is stable across seeds.
- **H2′ — the discriminator is backdrop *structure*, not mean level.** A spatially
  varying backdrop gives the adaptation a distribution rather than a level, and a
  distribution can straddle a decision boundary a single level cannot. Prediction:
  bistability rate on `checkerboard`/`photo`/`hc-text` materially exceeds the rate
  on `light-solid`/`dark-solid`/`mid-dark-solid` across sixteen runs. *Refuted if*
  a uniform-backdrop cell is bistable, or if the rates converge.
- **H3 — tint engagement rides the same state machine.** The refused run lost its
  tints across *both profiles at once*, not cell by cell, and two of the eight
  ambiguous cells are tinted. Prediction: tint dropout is a **run-level** event
  correlated with run conditions, not a per-cell draw; and within a run, a tinted
  cell's state agrees with its untinted twin's. *Refuted if* dropout appears on
  some tinted cells and not others within one run.
- **H4 — the settledness test cannot see this.** Prediction: the newly recorded
  settle-iteration counts show bistable cells settling no more slowly than stable
  ones, so `deterministic: true` carries no information about which attractor was
  reached. *Refuted if* bistable cells take systematically more iterations — which
  would make the existing attestation a usable detector after all, and would be
  the cheapest possible fix.
- **H5 — start-of-run warm-up.** There is no dwell before the first cell; the
  window is presented and cell 0 is captured 0.25 s later. Prediction: the
  first-captured cells stay over-represented among the bistable across eight
  baseline runs, and a warm-up removes it. *Refuted if* the enrichment disappears
  across more runs, making the P = 0.019 a small-sample artefact.

#### The harness the study runs on

Built in one pass, since the rebuild was already spent, and defaulting in every
case to the capture every committed bed was taken under — a run naming no study
flag is the run it always was.

- **`--reset-interstitial <s>`**: a uniform mid-grey field presented before each
  cell and held for `s` seconds. Mid-grey because a reset should start from a
  level that is not itself one of the states under suspicion. It is a protocol
  step and never a fixture: nothing is captured or recorded during it, and the
  manifest names the dwell instead.
- **`--min-idle-seconds <s>`**: the run refuses to start unless `IOHIDSystem`'s
  own idle counter clears the bar, and refuses outright if the counter cannot be
  read — a run must not claim an idle machine on a reading it does not have.
  Idle is also sampled **per cell**, so a run disturbed halfway through says which
  half, and the power manager's `UserIsActive` assertion is recorded beside it as
  an independent witness.
- **`--order-seed <n>`**: reseeds the FNV-1a basis, permuting the order. Absent
  keeps the one stable order, because that is what makes two ordinary runs
  comparable.
- **`--run-label <s>`**, so a study's arms are separable by name.
- Every fixture now records **`orderIndex`**, **`hidIdleSeconds`**,
  **`settleIterations`** and **`settleSeconds`**; every run records the protocol
  block above. Manifest schema **3**: the bump marks the first manifests that can
  be asked *how* a bed was produced, which no earlier bed can answer.

#### The study, and what it may not do

Roughly eight runs of the baseline protocol and eight with the interstitial, over
`1x-light-standard` and `1x-dark-standard` including the tint scenes (H3 needs
them) and the three `rrect-ml` span-128 scenes, order permuted across runs within
each arm, every run idle-guarded. Each run is snapshotted whole before anything
is decided, and **no bed is published, no constant is fitted and no holdout is
read** — the study measures the instrument, not the material.

Every cell is then classified per arm as deterministic, bistable (naming its
states), or refused, and the product is a doctrine proposal: the run count, the
idle bar, the per-cell agreement bar, and the state-control mechanism if H1 holds.
That proposal comes back to the gate, as every doctrine has.

One consequence of declaring the span-128 scenes now: until the study yields a
publishable bed, the declaration names three scenes with no committed fixture.
`compare` refuses a planned cell with no capture rather than inventing one, so
this fails loudly and safely — the condition §5.17 avoided, taken deliberately
here because producing that bed is what the study is for.

#### Addendum (2026-08-31): the study did not start, and the reason is a precondition nobody had written down

The Screen Recording grant was re-added by hand and the go-ahead given. The study
did not run, and what stopped it is worth the doctrine's first entry.

**Timeline.** At 06:47 the post-rebuild probe read `isKeyWindow: true`,
`NSApp.isActive: true`, and `ScreenCaptureKit: BLOCKED` with the explicit
TCC-denied message — the expected state after a rebuild. The grant was then done
by hand. At 06:53 the next probe read **`isKeyWindow: false`,
`NSApp.isActive: false`** and a ScreenCaptureKit *stream* failure rather than a
denial. A second probe at 06:56, taken after waiting for the machine to be
properly idle, read exactly the same. `NSWorkspace.frontmostApplication` was
**`loginwindow`**, and `CGSSessionScreenIsLocked` was **true**.

The machine was locked, deliberately, in the minute after the grant was granted.

**Why that is not a small thing.** A locked session refuses activation and blocks
ScreenCaptureKit *whatever the grant says*, so the grant itself could not be
verified — the probe cannot tell "not granted" from "granted, but locked". And a
capture taken in that state would record the material's inactive pose, which is
the defect Decision Log 14 exists to prevent.

**The precondition, stated properly.** Everything written so far asked for an
*undisturbed* machine, and the harness's idle guard enforces exactly that. But
undisturbed and unlocked are different claims, and on this machine they pull
against each other: the study needs about seventy minutes during which nobody
touches the machine *and* the screen does not lock. Leaving the machine alone is
the natural way to satisfy the first and it defeats the second. This is the third
time a locked session has stopped this wave (§5.17, §5.18, here), and it has been
read as bad luck twice.

So the doctrine gains a precondition before it has any measurements in it: **a
freezable bed requires a session that is unlocked for the whole run, idle for the
whole run, and attested as both in the manifest.** A `caffeinate -d` assertion is
now held for four hours, which stops a *timeout* lock; it cannot stop a
deliberate one, and this one was deliberate.

**What is staged.** The study chain is written and syntax-checked, and it opens
with a pre-flight probe that refuses to spend an hour of runs unless the window
becomes key *and* ScreenCaptureKit answers — the permission wall is reported, not
retried, per DL20. Its sixteen runs are **interleaved rather than blocked**
(`a1 b1 a2 b2 c1 a3 b3 …`), which is a correction to the declaration: running six
baseline runs and then six interstitial runs would confound the protocol arm with
anything that drifts across seventy minutes, and the whole question is whether the
protocol or the clock explains a difference. A lock check guards every run, in the
chain rather than in Swift, so it costs no rebuild and no further re-grant — it
belongs in the harness the next time a rebuild is warranted for another reason.

`--allow-colourless-tints` is set for every study run, deliberately: a tint-dropout
run is the evidence H3 needs, and refusing to publish it would destroy the only
pixels that could answer the question. No bed is materialised either way.

The reading instrument is built and committed too — `cli/stability.ts` classifies
every cell across an arm's runs as deterministic, noisy, bistable or multi-state,
using the same rule `materialize` publishes by, and it reproduces §5.20's reading
exactly when pointed at those two runs (45 deterministic, 1 noisy, 8 bistable).

### 5.22 The stability study: what four runs settled, and what the auto-lock stopped (2026-08-31)

The study ran. It got four runs in before the machine locked itself, and the four
were enough to settle three of the six hypotheses, to measure a hard constraint
nobody knew was there, and to establish the single most important fact about this
bed. It was **not** enough to answer the question the study was chartered for, and
that is stated plainly at the end.

#### The bed is a two-state system with byte-reproducible attractors

The headline, and it is not a hedge. Six cells, five attested runs, **two capture
sessions hours apart**:

| cell | 5.20 run E | 5.20 run F | a1 | b1 | a2 | distinct states |
| --- | --- | --- | --- | --- | --- | --- |
| `photo__rrect-md__rest` | A | B | B | A | A | **2** |
| `hc-text__capsule-button__rest` | A | B | B | B | A | **2** |
| `photo__capsule-button__pressed` | A | A | B | B | A | **2** |
| `checkerboard__toolbar-group__rest` | A | B | A | A | A | **2** |
| `photo__toolbar-group__rest` | A | B | A | B | A | **2** |
| `checkerboard__capsule-button__rest` (dark) | A | B | A | A | A | **2** |

Thirty observations. Every one lands on one of **exactly two SHA-256 values per
cell, and never a third** — and the same two values recur across sessions
separated by hours, a rebuild, and a re-grant. This is not noise, not drift, not
warm-up, and not a gradient across the run. **It is a bistable system with two
stable, byte-reproducible attractors**, and it is the reason a majority vote over
three runs was never going to work: there is nothing to average toward.

It also settles what the two states are *not*. Every observation above is
attested `presentedActive: true` on both sides, so the two attractors are not the
active and inactive poses of Decision Log 14. That axis is real, separate, and
measured below.

#### The auto-lock, measured to the second

The machine locks its own screen after a fixed idle interval, and `caffeinate -d`
does not prevent it. The per-cell idle recording added for this study measures
exactly where it happened:

| run | protocol | cells | idle range | attested active |
| --- | --- | --- | --- | --- |
| `a1` | baseline | 54 | 79…273 s | **54 / 54** |
| `b1` | interstitial 1.5 s | 54 | 296…563 s | **54 / 54** |
| `a2` | baseline | 54 | 584…773 s | **46 / 54** |
| `b2` | interstitial 1.5 s | 54 | 796…1054 s | **0 / 54** |

In `a2` the last attested cell is order 45 at **idle 745.9 s** and the first
unattested is order 46 at **idle 750.3 s**; the failures are a contiguous suffix,
orders 46 through 53. `b2` is unattested from its first cell.

**So the usable unattended capture window on this machine is 746 seconds — twelve
minutes and twenty-six seconds** — and the transition is sharp rather than gradual.
Past it every capture records the material's inactive pose, which is precisely the
defect DL14 exists to prevent.

Two things worked exactly as they were built to. **`presentedActive` caught every
affected cell** — 8 of 54 and 54 of 54, mechanically, with no judgement involved —
and the classifier now refuses to give an unattested cell a verdict at all rather
than reading a lone surviving observation as stability. And **the pre-flight probe
paid for itself**: the earlier watcher run aborted before spending an hour, on a
window that would not become key.

#### The classification, on what survived

Arm A, runs `a1` and `a2`, over the 46 cells both runs attested:

```
deterministic 42 · noisy 1 · bistable 3 · multi-state 0 · unattested 8
```

| cell | order | maxDelta | px changed | coherence |
| --- | --- | --- | --- | --- |
| `photo__rrect-md__rest` | 0 | 6 | 12571 | 0.977 |
| `hc-text__capsule-button__rest` | 2 | 47 | 14527 | 1.000 |
| `photo__capsule-button__pressed` | 24 | 48 | 19271 | 1.000 |

Arm B has one attested run and Arm C none, so **neither can be classified**.

#### The hypotheses

- **H1 — a neutral reset collapses the bistability. UNEVALUATED.** One
  interstitial run survived; an arm cannot be classified from one run. The single
  weak observation is that `b1` disagreed with `a1` on two of the six known
  bistable cells, so the interstitial does not force a canonical state on first
  contact — but one run is not evidence and this is not reported as any.
- **H1b — order permutation moves the bistable set. UNEVALUATED.** No permuted
  run survived.
- **H2′ — the discriminator is backdrop structure, not level. SUPPORTED, still
  short of significant.** All three bistable cells here sit on structured
  backdrops (`photo`, `hc-text`), none on a uniform one, consistent with §5.21's
  0-of-13. No uniform-backdrop cell has yet been bistable in any session.
- **H3 — tint engagement rides the same state machine. ANSWERED, AND NO.** The
  tint-dropout caveat fired on exactly the two runs that lost attestation (`a2`,
  `b2`) and on neither clean run, and `a2`'s unattested cells include its tinted
  ones. **Tint dropout is a symptom of the inactive pose, not a second state
  machine** — which also retires the open question from §5.10, where colour loss
  was attributed to something "inside the material". It was lost focus.
- **H4 — the settledness test cannot distinguish the attractors. CONFIRMED.**
  Bistable cells settle in **1.385** comparisons on average against **1.278** for
  every other cell, with the same shape (most agree on the first comparison, a
  few take two or three). The test measures whether the picture stopped moving,
  and both attractors are equally stopped. The cheapest possible fix is therefore
  ruled out.
- **H5 — start-of-run enrichment. STILL SUPPORTED.** The three bistable cells sit
  at orders 0, 2 and 24; two of three in the first three captured, matching
  §5.21's three-of-first-five.

#### The doctrine proposal

Five parts. The first is measured, the second is counterintuitive, the third is
arithmetic, the fourth is the existing rule made binding, and the fifth is honest
about what is not yet known.

**1. Unlocked throughout, attested per cell.** A run is only evidence if its
session was unlocked for the whole of it. The mechanical test already exists and
already works: **every cell must carry `presentedActive: true`, and a run with any
unattested cell is void rather than partial.** The lock check belongs in the
harness beside the idle guard — it lives in the study chain today only because
putting it in Swift costs a rebuild and a permission re-grant.

**2. The idle bar needs a ceiling as well as a floor.** This is the part nobody
would guess. Too *little* idle means a human is present and perturbing the
capture; too *much* means the machine has locked itself and every subsequent cell
is the wrong material. The bar is therefore an interval: **idle ≥ 60 s at the
start, and the run must be projected to finish before the machine's own lock
threshold** — 746 s here, and a per-machine measurement rather than a constant,
because it is a user setting.

**3. Run count: fourteen, not three, and not eight.** The observed minority state
holds between **20% and 40%** of the draws. To see a state at 20% frequency at
least once:

| true frequency | runs for 90% | for 95% | for 99% |
| --- | --- | --- | --- |
| 0.50 | 4 | 5 | 7 |
| 0.40 | 5 | 6 | 10 |
| 0.30 | 7 | 9 | 13 |
| 0.20 | **11** | **14** | 21 |
| 0.10 | 22 | 29 | 44 |

**A cell is only "deterministic" to the confidence its run count buys.** Three
runs — the doctrine this cascade has used throughout — gives a 51% chance of
missing a 20%-frequency second state, which is how a bed with at least eight
bistable cells was frozen and fitted against. The proposal is **14 runs per
protocol**, and a bed frozen on fewer must say in the record what confidence it
bought.

**4. Per-cell agreement: unanimity, under the structured/incidental rule.** Any
structured disagreement between attested runs bars the cell from a freezable bed;
differences at or below one 8-bit code, or scattered rather than regional, resolve
by majority as before. This is §5.19's arm, promoted from a materialisation check
to a freezing precondition.

**5. State control: unknown, and the study must be re-run to know it.** H1 is the
question the whole study exists to answer and it has no answer yet.

#### What stopped it, and what it needs

The study needs roughly seventy minutes and the machine gives twelve and a half.
That is the whole of it. Two ways past, and the choice is the gate's because the
second changes what an attestation means:

- **Disable the lock timeout for the study window** (System Settings → Lock
  Screen). Nothing in the instrument changes and every attestation keeps its
  current meaning. Costs one manual setting change and its restoration.
- **Inject a synthetic no-op input event between runs** to hold the lock timer
  off. This works unattended and forever, but `hidIdleSeconds` would stop meaning
  "no human is present", so the idle guard would have to be re-founded on
  something else. `presentedActive` would carry the whole burden.

The first is recommended: it is reversible, it changes no measurement, and the
attestation that caught this failure keeps working. `caffeinate -u` was measured
during the study and does **not** reset `HIDIdleTime` (895 → 915 s while held), so
it can hold a display awake without blinding the idle guard — but it did not
prevent this lock, and is not a substitute for the setting.

Four runs are preserved whole at
`/Users/new/.claude/jobs/5c70e47f/tmp/dl20snap-{a1,b1,a2,b2}`. No bed was
materialised, no constant was fitted, no holdout was read, and the committed bed
was restored on the study's own exit path.

### 5.23 The stability study, completed: the reset works, and three hypotheses dissolved (2026-08-31)

The lock was disabled, the sixteen runs ran, and **every one of them came back
54 of 54 attested** — app active, window key, each cell settled against itself —
across idle times from 69 to 3038 seconds. The 746-second wall of §5.22 is gone
and the study is the first complete one this wave has had.

Three arms, interleaved rather than blocked so the protocol cannot be confounded
with anything that drifts across an hour:

| arm | protocol | runs | deterministic | noisy | **unstable** |
| --- | --- | --- | --- | --- | --- |
| A | baseline, fixed order | 6 | 23 | 2 | **29 / 54** |
| B | reset interstitial 1.5 s, fixed order | 6 | 38 | 3 | **13 / 54** |
| C | baseline, permuted order | 4 | 26 | 1 | **27 / 54** |

#### The finding that reframes everything before it

Instability is not a property of a few odd cells. **Over half the bed is
bistable**, and the only reason it looked like eight cells in §5.20 and three in
§5.22 is that those readings had two runs to see it with.

| runs | arm A unstable | arm B unstable |
| --- | --- | --- |
| 2 | 5 | 8 |
| 3 | 10 | 10 |
| 4 | 19 | 10 |
| 5 | 24 | 12 |
| 6 | **29** | **13** |

Baseline discovery climbs by about six cells per run and **has not saturated at
six**. Eleven of arm A's twenty-nine revealed their second state exactly once in
six runs — at five runs they would have read as deterministic. Twenty-eight of
the twenty-nine hold exactly two states; one holds three.

**Every bed this cascade has fitted against was accepted on three runs**, which
against the observed minority frequencies is a coin-flip's chance of seeing the
second state at all. That is not a defect in any particular fit. It is the reason
the fits kept disagreeing with each other.

#### H1 and H1b: the reset works, and the path is causal

**H1 — SUPPORTED, and the mechanism is confirmed.** A 1.5 s neutral field before
each cell cuts instability from **29 to 13**. The stronger evidence is the shape
rather than the level: baseline discovery grows without saturating, while the
interstitial arm plateaus after run three (10, 10, 12, 13). The reset removes the
dominant mechanism outright rather than merely damping it. Its residual is a
different, smaller population — eleven of B's thirteen are also in A's
twenty-nine, and the two that are not are `photo__rrect-md__rest` and
`photo__rrect-ml__rest`.

**H1b — SUPPORTED.** At the same four runs, permuting the order gives **27**
unstable against the fixed order's **19**, and the two sets overlap by only 0.59
(Jaccard): ten cells are unstable only under permutation, two only under the fixed
order. Varying the path both increases instability and moves it.

Together these vindicate Decision Log 20's working hypothesis in refined form:
**the previous cell's settled state carries into the next one, a neutral reset
largely removes that carry-over, and varying the path exposes more of it.** The
naive version was wrong only in its prediction that a fixed order would make runs
reproducible — §5.21 showed it does not, because the carry-over has a stochastic
component as well as a path-dependent one. Both parts are now measured.

#### H2, H2′ and H5: all three dissolve

**H2 (mid-luminance) and H2′ (backdrop structure) are both REFUTED.**

| backdrop | unstable / total | kind |
| --- | --- | --- |
| `mid-dark-solid` | 2 / 2 | uniform |
| `hc-text` | 2 / 3 | structured |
| `checkerboard` | 9 / 15 | structured |
| `dark-solid` | 4 / 7 | uniform |
| `photo` | 10 / 19 | structured |
| `impulse` | 2 / 4 | structured |
| `light-solid` | 0 / 4 | uniform |

Uniform backdrops run **6/13 = 46%** against structured backdrops' **23/41 =
56%** — no meaningful separation, and `mid-dark-solid` is fully bistable at 2 of
2. §5.21's striking 0-of-13 on uniform backdrops was an artefact of having two
runs.

**H5 (start-of-run enrichment) is REFUTED** on the same grounds: the first ten
cells captured run 6/10 unstable against 23/44 for the rest, which is nothing.
§5.21's P = 0.019 was the same artefact.

**The meta-finding is worth more than any of the three.** At two runs the
instrument sees five of twenty-nine unstable cells, and *which* five is
arbitrary — so any pattern found among them is a pattern in the sampling, not in
the material. Three hypotheses were built on such patterns and all three died the
moment the sample was adequate. This is the argument for the run count below, made
by the study on itself.

#### H3 and H4: settled

**H3 — ANSWERED, AND NO.** Across all sixteen fully attested runs, **not one
tint dropout occurred**. §5.22 found dropout on exactly the two runs that lost
attestation and on neither clean one. Tint engagement does not ride the
bistability's state machine; **tint dropout is a symptom of the unfocused pose**,
which retires §5.10's attribution of colour loss to something "inside the
material". Tinted cells are affected by the bistability like everything else
(11 of 15 unstable in arm A) — they are not special.

**H4 — CONFIRMED.** Unstable cells settle in **1.207** comparisons on average
against **1.060** for stable ones (3.20 s against 3.04 s). The gap is a seventh of
one comparison and cannot classify anything. The existing settledness attestation
measures whether the picture stopped moving, and both attractors are equally
stopped.

#### The completed doctrine proposal

**1. Unlocked throughout, attested per cell.** Measured both ways: with the lock
on, everything past 746 s of idle is the unfocused pose (§5.22); with it off, all
sixteen runs held attestation to 3038 s. A run with any unattested cell is void
rather than partial. The lock check belongs in the harness beside the idle guard;
it lives in the study chain today only to avoid spending a rebuild and a
permission re-grant.

**2. The idle bar is an interval, not a floor.** Too little idle means a human is
perturbing the capture — the guard held run `b2` back for 76 s on exactly this
during the study, after the idle counter reset mid-run. Too much means the machine
has locked itself. Floor 60 s; ceiling the machine's own lock threshold unless the
lock is disabled for the session. Per-cell idle stays recorded either way.

**3. Run count: seventeen for 95% confidence, and six is not enough.** The
observed minority share runs from **0.167 to 0.50**, median 0.33.

| minority frequency | runs for 90% | for 95% | for 99% |
| --- | --- | --- | --- |
| 0.50 | 4 | 5 | 7 |
| 0.33 | 6 | 8 | 12 |
| 0.25 | 9 | 11 | 17 |
| **0.167** | 13 | **17** | 26 |
| 0.10 | 22 | 29 | 44 |

Eleven of twenty-nine cells showed their second state exactly once in six runs, so
six runs is itself an undercount and the true minimum frequency may be lower than
0.167. **A bed frozen on fewer runs must record the confidence it bought.** Three
— this cascade's standing doctrine — buys about half.

**4. Per-cell agreement: unanimity, under the structured/incidental rule.** Any
structured disagreement between attested runs bars the cell; differences at or
below one 8-bit code, or scattered rather than regional, still resolve by
majority. §5.19's arm, promoted from a materialisation check to a freezing
precondition.

**5. State control: adopt the reset interstitial — and it is not sufficient.**
1.5 s of neutral field before each cell is necessary and cheap and it more than
halves the problem. It does not solve it. **Thirteen cells remain bistable under
the best protocol tested, eight of them calibration cells and three holdout**, and
twelve of the thirteen showed their second state exactly once in six runs, so that
thirteen is very likely an undercount too.

#### What this means for the flip

Plainly: **the bed cannot be frozen as it stands.** The best protocol this study
found still leaves at least thirteen cells taking two byte-exact states, and eight
of those are cells the constants are fitted on. Freezing that bed into an enforced
suite would enforce one arbitrary draw. Three ways forward, and the choice is the
gate's:

- **Find a stronger reset.** The dwell was 1.5 s and untested at any other value;
  the obvious next experiment is a sweep of it, and of an interstitial that carries
  a glass surface rather than a bare field.
- **Exclude the residual cells** from the frozen bed and record them as a measured
  limitation, which costs eight calibration cells and three holdout cells.
- **Freeze a per-cell state** by adopting the majority state under a 17-run
  protocol and recording that a bistable cell was resolved by frequency rather
  than by agreement — the honest version of what the old doctrine did silently.

All sixteen runs are preserved at
`/Users/new/.claude/jobs/5c70e47f/tmp/dl20snap-{a1…a6,b1…b6,c1…c4}`, and the four
partial runs from the locked attempt at `dl20-partial-locked/`. No bed was
materialised, no constant fitted, no holdout read; the committed bed was restored
on the study's own exit path.

### 5.24 The reset sweep, declared before it runs (2026-08-31)

Decision Log 21 adopted all five doctrine items and chartered a sweep of the
reset's strength before the final bed is captured. §5.23 tested exactly one reset
— a 1.5 s neutral field — so the question of whether the residual thirteen cells
are a floor or an artefact of an under-powered reset is open. This is the
declaration; nothing below has been run.

#### The ranking statistic, and what it can resolve

The comparison is `U(n)` — unstable cells (bistable + multi-state) over `n` runs
of one protocol — and it is only comparable at equal `n`, because §5.23 measured
it climbing with every run.

`U(4)` is the working statistic, and its noise is measured rather than assumed.
Taking all fifteen four-run subsets of §5.23's six-run arms:

| protocol | U(4) min | median | max | sd |
| --- | --- | --- | --- | --- |
| baseline | 17 | 24.0 | 29 | 3.43 |
| reset 1.5 s | 6 | 9.0 | 12 | 1.69 |

The two do not overlap — baseline's *worst* subset beats the reset's *best* — so
`U(4)` separates protocols that differ as much as these do. **Declared
discrimination threshold: a difference of 5 or more in `U(4)` is a ranking; less
than that is declared indistinguishable**, and among indistinguishable protocols
the *shorter* dwell wins, because dwell is paid 54 times per run and again on
every one of the final bed's seventeen.

#### The grid

**Four runs per point, fixed order, idle-guarded, lock-checked, focus-attested,
bed restored on every exit.** Two points are already measured on the same machine,
the same day, under the same conditions, and are reused rather than re-run:

| point | dwell | reset carries | runs | status |
| --- | --- | --- | --- | --- |
| D0 | none | — | 4 (of §5.23's arm A) | measured, U(4) median 24 |
| D0.5 | 0.5 s | bare neutral field | 4 | **to run** |
| D1.5 | 1.5 s | bare neutral field | 4 (of §5.23's arm B) | measured, U(4) median 9 |
| D3 | 3 s | bare neutral field | 4 | **to run** |
| D6 | 6 s | bare neutral field | 4 | **to run** |
| G | winning dwell | **a glass surface** | 4 | **to run, after a rebuild** |

Ten seconds is deliberately left out of the first pass. A run costs
`200 + 54 × dwell` seconds, so D6 is already 35 minutes for four runs and D10
would be 49; if the curve is still falling at 6 s the point gets added, and if it
has flattened it would only buy cost.

#### The glass-bearing reset, specified

The bare field resets the *backdrop* the material adapts to, but it removes the
material entirely, so each cell's surface is created afresh against a neutral
field. **G resets to a canonical glass state instead**: the neutral field with one
fixed surface on it — an untinted `capsule-button` at rest, the same one before
every cell whatever that cell contains — so the state machine starts from one
known glass configuration rather than from no glass at all.

Fixed rather than matched to the upcoming cell, deliberately. A reset that varied
with what came next would be fifty-four different reset states, which is the
condition being removed rather than a cure for it.

It needs a harness change and therefore a rebuild, and a rebuild costs the Screen
Recording grant. So the dwell points run first on the committed binary, the glass
point runs after one rebuild, and that rebuild is deliberately batched with the
accessibility-toggle coordination the final bed needs anyway — one interruption
for the human, not two.

#### What would stop this

If no two adjacent dwell points differ by 5 or more in `U(4)`, and the whole
sweep sits inside the threshold, then the sweep cannot rank and that routes to the
gate rather than being resolved by picking a favourite. If the curve is flat from
0.5 s onward, the finding is that dwell is not the axis and the reset's benefit is
categorical — present or absent — which is itself an answer and changes what the
glass point is testing.

#### Addendum (2026-08-31): the sweep's first attempt, and a correction to doctrine item 1

The dwell sweep started and lost its later runs, and the cause is worth the
doctrine entry it produces.

Runs `d05-1` and `d3-1` came back 54/54 attested. `d6-1` came back **40/54**, and
`d05-2`, `d3-2` and `d6-2` came back **0/54** — the session had dropped to
`loginwindow` partway through the third run, at around 1000 seconds of idle. The
attestation caught all of it, and the tint-dropout caveat fired on exactly the
same runs, which is §5.23's H3 result reproducing itself unprompted.

**The cause was mine.** At the close of the previous round I released the
`caffeinate` wake assertions as a courtesy, having read them as a temporary
workaround for the lock. They were not a workaround; they were load-bearing.

**And that corrects doctrine item 1.** The proposal said "unlocked throughout",
and the user duly disabled the password lock — `sysadminctl` reports
`screenLock is off` and `pmset` reports `displaysleep 0`. **That is not
sufficient.** With no assertion held, the session still descends to `loginwindow`
on its own, and once there neither `caffeinate -u` nor dismissing the screen saver
brings it back: the state is only recoverable by a human. §5.23's sixteen clean
runs to 3038 seconds of idle were clean *because* a wake assertion was held for
their whole duration, which at the time read as incidental.

So item 1 becomes: **a capture campaign requires the password lock disabled AND a
display-wake assertion held for the whole of it.** Either alone is not enough, the
failure is silent from the operator's side, and the only mechanical detector is
the per-cell focus attestation — which is exactly why item 1 makes a run with any
unattested cell void rather than partial.

The sweep is re-armed from a clean start with the assertion held for eight hours,
and it now waits on **both** preconditions — an unlocked session and a Screen
Recording grant that actually answers — before spending a run. The rebuild for the
glass reset has been taken in the same window, so one human visit clears both.

### 5.25 The reset sweep, reported: six seconds, and the glass makes no difference (2026-08-31)

Sixteen new runs against §5.24's declaration, plus eight reused from §5.23 on the
same machine under the same conditions. **Every run came back 54 of 54 attested**,
out to 7784 seconds of idle — the wake assertion held throughout, which is the
corrected doctrine item 1 working.

#### The dwell curve

`U(4)` is the declared statistic — unstable cells over four runs — and its
declared discrimination threshold is 5.

| point | dwell | U(4) | deterministic | run cost |
| --- | --- | --- | --- | --- |
| D0 | none | 19 | 33 | ~200 s |
| D0.5 | 0.5 s | 14 | 37 | ~227 s |
| D1.5 | 1.5 s | 10 | 41 | ~281 s |
| **D3** | 3 s | **21** | 31 | ~362 s |
| D6 | 6 s | **6** | 47 | ~524 s |

**D3 is worse than no reset at all, and it is not one unlucky run.** All four of
its three-run subsets score 12, 16, 18 and 19 — a distribution sitting on top of
D0's own 10, 17, 17, 18. Every other point's subsets are cleanly below. So the
curve is **non-monotone and reproducibly so**: better at 0.5 s, better again at
1.5 s, back to baseline at 3 s, best by far at 6 s.

The honest reading is that this is not a smooth "more dwell is more reset". A
mechanism that would produce it: the reset itself drives an adaptation animation,
and handing the real scene over while that animation is mid-flight is worse than
never starting it — 3 s would then be near the worst phase to interrupt at. That
is a hypothesis the sweep suggests and does not test, and it is recorded as one.

#### Resolving D6 against D1.5

At four runs D6 (6) and D1.5 (10) differ by 4, one short of the declared
threshold, and the declared tie-break prefers the shorter dwell on cost. Rather
than settle the wave's most consequential protocol choice on a one-unit margin,
two more D6 runs were taken so the pair could be compared at the run count that
actually matters:

| protocol | U(6) | U(5) over all six subsets |
| --- | --- | --- |
| D1.5 | 13 | 9, 10, 11, 11, 12, 13 |
| **D6** | **6** | 3, 4, 5, 6, 6, 6 |

A gap of 7 at n=6, above the threshold, with **no overlap at all** between the
two subset distributions. This is not a change to the ranking rule — the rule is
applied unchanged — it is the acquisition of enough data to apply it where it
bites.

**D6 has also stopped discovering.** Its count is 6 at four runs, 6 at five and 6
at six, where the baseline climbed about six cells per run and never flattened.
A protocol whose instability estimate has converged is a different kind of object
from one whose estimate is still a lower bound.

#### The glass point: no effect, and that is the informative result

Four runs at 6 s with the reset carrying a canonical untinted capsule instead of
a bare field:

| reset at 6 s | U(4) |
| --- | --- |
| bare neutral field | 6 |
| **carrying a glass surface** | **6** |

Identical, a difference of zero against a threshold of five. **Whether a surface
is present during the reset makes no difference whatever**, which says the
carry-over being cleared lives in the *backdrop adaptation* rather than in any
per-surface state: resetting what the material looks at is the whole of the
effect, and what it looks at it *with* is irrelevant. That is worth more than a
win would have been, because it names where the state lives.

One nuance the counts hide: the two six-cell sets share only two members. The
residual is therefore **not a stubborn subset of hard cells** but a low-rate draw
that can land on any cell — while remaining, at six seconds, a draw of about six.

#### The winning protocol

**A six-second bare neutral field before every cell.** It ties the glass variant
on the statistic and wins on simplicity, and it beats every shorter dwell
decisively. It costs 524 seconds per 54-cell run against the baseline's 200, and
that is the price of the bed being worth freezing.

The final bed is captured under it: seventeen runs per phase, per adopted doctrine
item 3, buying 95.6% confidence against a one-in-six minority state.

---

### 5.26 The flip, attempted: the instrument is fixed, and the residual is one mechanism (2026-09-01)

The close ran to its last step and stopped there. Everything the flip was asked
to carry is built, verified and pushed on `flip/frozen-active-bed`; `main` keeps
a green suite because the flip does not land green, and what keeps it red is a
finding rather than a bookkeeping gap.

#### What the flip carries, and what verifies it

`results/matrix.json` becomes the frozen active bed — schema 5, 230 cells — and
the retired inactive bed is preserved as
`results/2026-08-30-inactive-bed-matrix.json`. `sizeOcclusionGain` lands at 0.05
in both the WebGPU material and its CSS mirror.

The enforced suite adopts **§5.15's conditioning predicate in its final form**,
which it had never implemented: two arms, both sides, compared against the
cell's own `componentRegionArea` and `componentRegionBodies`. What it replaces
asked only the NATIVE side, against a points area from `scenes.json` multiplied
by the square of the backing scale.

That gap was load-bearing, not cosmetic. Two cells it had been gating:

- `photo__rrect-lg__rest-tint-orange` (holdout) reads **one native body against
  seven web bodies**, 11 holes, an IoU still of 0.968, and a contour p95 of
  **67 px** against a bound of 4. The p95 was measuring the distance between
  fragments of a broken mask. The old predicate saw a native area of 0.958 and
  passed it.
- `hc-text__rrect-md__rest` (holdout) recovers 1.000 of its region natively and
  **0.934 on the web side**. Gated at a contour p95 of 24 px against a bound
  of 4, for the same reason: nobody was asking the web side.

The implementation is checked against §5.15's own published table rather than
against itself. Evaluated over `results/2026-08-31-round-two.json` — the bed
that table was measured on — it reproduces **all eight declared cell counts
exactly**: 22/18, 21/18, 6/6, 6/5.

Adopted with it: §5.15's two declared contour amendments (`1x-light-standard`
dom p95 4.0 → 7.0; `increased-contrast` texture p95 3.2 → 11.5), and Decision
Log 18 ruling 2's three bounds at their measured values, each marked
**gate-adopted post-read** and never pre-registered (`2x` dom p95 8.0 → 10.0;
reduced-transparency dom p95 3.5 → 5.0; reduced-transparency texture SSIM
0.96 → 0.95).

Together these remove **all eighteen contour failures**. The exclusion list is
re-derived from the frozen bed at 60 cells, each named and classified by the arm
that fires. One cell *leaves* it: `hc-text__capsule-button__rest` in increased
contrast recovered 0.519 on the retired bed and recovers **0.982** on the frozen
one, so that profile now gates strictly more of itself than it used to. **Both
accessibility profiles come back completely clean.**

#### The residual: twenty-five fidelity rows and eight coherence rows, one cause

They fall on the two light-standard profiles only, and they are not scattered.
SSIM against the reference degrades **monotonically with surface area — but only
over a high-spatial-frequency backdrop**. `1x-light-standard`, by component, in
increasing declared area:

| tier | backdrop | `rrect-sm` | `capsule` | `rrect-md` | `rrect-ml` | `rrect-lg` |
| --- | --- | --- | --- | --- | --- | --- |
| `dom` | `checkerboard` | 0.986 | 0.964 | 0.883 | 0.795 | **0.688** |
| `dom` | `photo` | 0.986 | 0.977 | 0.962 | 0.944 | 0.926 |
| `dom` | `light-solid` | 0.987 | 0.978 | 0.970 | — | — |
| `texture` | `checkerboard` | 0.993 | 0.964 | 0.913 | 0.865 | **0.831** |
| `texture` | `photo` | 0.999 | 0.986 | 0.996 | 0.994 | 0.991 |
| `texture` | `light-solid` | 0.990 | 0.997 | 0.996 | — | — |

Over a photo the texture tier is flat at 0.99 across a twenty-two-fold range of
area. Over the checkerboard it falls away. The backdrop that breaks it is not
the one with the most colour variety; it is the one with the highest **spatial
frequency**. Size and spatial frequency interact, and neither alone predicts the
miss.

The cross-tier axis reads the same mechanism from the other side. A tinted
capsule over the checkerboard has the two renderers disagreeing about interior
level by 64% — **1.635**, against a 0.8…1.25 bound — while the same tint over a
photo agrees to 5% (1.056) and over a solid to 0.1% (1.001). Ranked, the
divergence follows backdrop structure exactly: checkerboard 1.635 and 1.370,
`hc-text` 1.265, `light-solid` 1.243, photo 1.056 and 0.962.

`platform-web/src/backdrop-tone.ts` states the cause on the CSS side in its own
header, as an acknowledged limit of that tier: **one backdrop mean per source,
not per surface**, fed to a non-linear tone map. Averaging before a non-linear
map is not the same as mapping before the average, and the gap between them is
widest exactly where the backdrop is bimodal. That file also nominates its
referee — "the cross-tier bound is the referee, and it is enforced from the
matrix on every gated cell." The tint scenes have now put such cells in the
matrix for the first time, and the referee has ruled against the approximation.

#### Why this stops the close rather than widening a bound

`sizeOcclusionGain` is a **size** term, and it was fitted in this very round. The
residual is still size-monotonic after adopting it, and it is size-monotonic **on
holdout** — `checkerboard__rrect-lg__rest` at 0.688 and
`checkerboard__glass-over-glass__rest` at 0.808 are both holdout cells. A single
linear size term does not express this, which is Decision Log 21's declared stop
condition reached exactly as written: a holdout surprise that falsifies a fitted
form.

The two moves that would make the suite green are both closed:

- **Widening the bounds** would mean carrying a 0.688 SSIM under a 0.90 bound and
  a 1.64 ratio under a 1.25 one. That is not the G3 amendment doctrine, which
  amends where a measurement cannot be met and holds everywhere else; it is
  abandoning the rows on the cells that most need them.
- **A documented exceedance** is the move Decision Log 11 refused once and
  Decision Log 16 refused again for the tint. Nothing measured here argues for
  reopening it — if anything the size law makes the case stronger, because the
  exceedance would be granted precisely to the largest surfaces.

So the flip waits, and what it waits on is a modelling question rather than a
gate question: **how backdrop tone is sampled as a function of surface size over
structured content**, on both tiers. The GPU tier reads a neighbourhood and the
CSS tier reads one number per source, which is why the CSS tier is worse at every
size — but the GPU tier fails too (0.831 at `rrect-lg`), so this is not only the
CSS tier's known coarseness. That is the next wave's first question, and it is a
better-posed one than the cascade started with.

> **Superseded in its conclusion, not in its measurement (Decision Log 22).**
> The gate did not accept "the flip waits". It ruled that the flip lands, with
> every one of these rows converted to a regression floor and its claim narrowed
> in writing, and it chartered the question above as **W9**. §5.27 is that
> landing. Everything measured in this section stands exactly as recorded — what
> changed is what was done about it.

### 5.27 The landing: thirty-three claims narrowed, and what CI now enforces (2026-09-01)

Decision Log 22 lands the flip. The thirty-three rows §5.26 measured do not
disappear and are not excused: **each keeps its adopted bound as a claim, marked
UNMET, and CI enforces a regression floor pinned at what the bed measures.**
Nothing here is widened and nothing is excepted. The claim narrows, in writing,
which is the founding rule this document was started under.

The distinction that makes this legitimate rather than cosmetic: a bound says
*vitrea is this good*; a floor says *vitrea is no worse than this*. The first is
a claim and can be false. The second is a ratchet and cannot be met by moving it.
Every row below states both, so no reader can mistake one for the other.

**Mechanism** for all thirty-three: §5.26 — backdrop tone sampled without regard
to surface size over high-spatial-frequency content, on both tiers. **Owner**:
W9. **Epsilon**: a floor sits 0.001 below its measurement (0.005 for the
coherence ratio), rounded away from it at four decimals, so re-measurement cannot
fail CI on an unchanged renderer. The captures are deterministic, so that
headroom is against constants moving in their last digit and nothing else.

> **Amended by W9 (2026-09-02, §5.35).** Six rows below are struck: their
> adopted bounds are MET on the re-measured bed and the claims are restored
> (`photo__rrect-lg` tinted ΔE-mean 0.0628, `light-solid` tinted capsule
> ΔE-p95 0.1032, `mid-dark-solid` capsule ΔE-p95 0.0095 — each at both
> scales). Seven `ssimMean` rows carry a second measurement and a re-pinned
> floor, by decision: the response law lands the interior mean and pays
> 0.0002–0.0072 of SSIM for it. The count is 27.
>
> **Amended by W10 (2026-09-02, §5.37).** The six `interiorLevelRatioGpuOverCss`
> rows on tinted capsules are struck: MET on the re-measured bed at 0.94–1.01
> against 0.80…1.25, the claims restored. Two contour rows are ADDED on
> `photo__rrect-md__rest-tint-orange` (1x texture, validation) — a cell the
> conditioning predicate newly admits, whose miss is one interior hole the
> luminance-delta extractor cuts where an opaque orange sits over the photo's
> own orange; an instrument floor with the extractor as its owner. The count
> is 23.
>
> **Amended by W11a (2026-09-02, §5.39).** Six rows on the two nested-glass
> cells are struck: the four `oklabDeltaEP95` rows (0.19 → 0.07–0.12 against
> ≤ 0.17) and the two `interiorLevelRatioGpuOverCss` rows (0.796 → 0.918
> against ≥ 0.8), MET once the GPU tier's upper pane composites over the
> glass beneath it instead of over black. The two texture-tier `ssimMean`
> rows on `checkerboard__glass-over-glass__rest` improve and stay unmet
> (0.8409 → 0.8796 against 0.88; 0.8762 → 0.8948 against 0.93); their floors
> ratchet UP to the new measurement. The two dom-tier rows on the same cell
> are untouched (the CSS tier was never the defect). The count is 17.
>
> **Amended by W11b (2026-09-02, §5.40).** The two W10 instrument rows are
> struck: under the extractor's chroma arm the cell reads IoU 1.000 and
> contour 0 / 0 px, the claims restored. No row is added — twenty-three
> cells the predicate had excluded now gate, and every one of them meets
> every adopted shape bound. The count is 15.
>
> **Amended by W11c G1 (2026-09-03, §5.42).** The three 1x texture-tier
> `ssimMean` rows on `checkerboard__rrect-ml`, `__glass-over-glass` and
> `__rrect-lg` are struck: MET on the re-captured bed (0.8963 / 0.8987 /
> 0.8934 against ≥ 0.88) under the two-component body law, the claims
> restored. The eight dom-tier `ssimMean` rows carry a further measurement
> and a floor ratcheted UP (by 0.011–0.152; the CSS tier's single blur is
> the law's mixed-σ form, its claim narrowed in §5.42 §5). The four 2x
> texture-tier `ssimMean` rows carry a further measurement and a floor
> re-pinned DOWN by decision (0.0015–0.0083; the law is fitted at 1x, the
> 2x reference is a different object, W11 Decision Log 5). The count is 12.

**`1x-light-standard` · texture tier**

| scene | set | metric | claimed | measured | enforced floor |
| --- | --- | --- | --- | --- | --- |
| ~~`photo__rrect-lg__rest-tint-orange`~~ | holdout | `oklabDeltaEMean` | ≤ 0.07 **MET (W9)** | 0.0760 → 0.0628 | — |
| ~~`checkerboard__glass-over-glass__rest`~~ | holdout | `oklabDeltaEP95` | ≤ 0.17 **MET (W11a)** | 0.1909 → 0.1221 | — |
| ~~`light-solid__capsule-button__rest-tint-orange`~~ | calibration | `oklabDeltaEP95` | ≤ 0.17 **MET (W9)** | 0.1726 → 0.1032 | — |
| ~~`mid-dark-solid__capsule-button__rest`~~ | holdout | `oklabDeltaEP95` | ≤ 0.17 **MET (W9)** | 0.1775 → 0.0095 | — |
| ~~`photo__glass-over-glass__rest`~~ | holdout | `oklabDeltaEP95` | ≤ 0.17 **MET (W11a)** | 0.1906 → 0.0744 | — |
| ~~`checkerboard__glass-over-glass__rest`~~ | holdout | `ssimMean` | ≥ 0.88 **MET (W11c G1)** | 0.8409 → 0.8796 (W11a) → 0.8987 | — |
| ~~`checkerboard__rrect-lg__rest`~~ | holdout | `ssimMean` | ≥ 0.88 **MET (W11c G1)** | 0.8305 → 0.8233 (W9 trade) → 0.8934 | — |
| ~~`checkerboard__rrect-ml__rest`~~ | calibration | `ssimMean` | ≥ 0.88 **MET (W11c G1)** | 0.8647 → 0.8620 (W9 trade) → 0.8963 | — |
| ~~`photo__rrect-md__rest-tint-orange`~~ | validation | `contourDistanceMean` | ≤ 2.5 px **MET (W11b)** | 5.8893 → 0.0000 | — |
| ~~`photo__rrect-md__rest-tint-orange`~~ | validation | `contourDistanceP95` | ≤ 5.0 px **MET (W11b)** | 33 → 0 | — |

**`1x-light-standard` · dom tier**

| scene | set | metric | claimed | measured | enforced floor |
| --- | --- | --- | --- | --- | --- |
| ~~`checkerboard__capsule-button__rest-tint-blue`~~ | validation | `interiorLevelRatioGpuOverCss` | ≤ 1.25 **MET (W10)** | 1.6353 → 1.0049 | — |
| ~~`checkerboard__capsule-button__rest-tint-orange`~~ | calibration | `interiorLevelRatioGpuOverCss` | ≤ 1.25 **MET (W10)** | 1.3695 → 0.9996 | — |
| ~~`hc-text__capsule-button__rest-tint-orange`~~ | holdout | `interiorLevelRatioGpuOverCss` | ≤ 1.25 **MET (W10)** | 1.2651 → 0.9383 | — |
| ~~`photo__glass-over-glass__rest`~~ | holdout | `interiorLevelRatioGpuOverCss` | ≥ 0.8 **MET (W11a)** | 0.7958 → 0.9180 | — |
| `checkerboard__glass-over-glass__rest` | holdout | `ssimMean` | ≥ 0.9 **UNMET** | 0.8078 → 0.8499 (W11c G1 ratchet) | ≥ 0.8489 |
| `checkerboard__rrect-lg__rest` | holdout | `ssimMean` | ≥ 0.9 **UNMET** | 0.6883 → 0.6850 (W9 trade) → 0.8372 (W11c G1 ratchet) | ≥ 0.8361 |
| `checkerboard__rrect-md__rest` | calibration | `ssimMean` | ≥ 0.9 **UNMET** | 0.8826 → 0.8963 (W11c G1 ratchet) | ≥ 0.8952 |
| `checkerboard__rrect-ml__rest` | calibration | `ssimMean` | ≥ 0.9 **UNMET** | 0.7950 → 0.7929 (W9 trade) → 0.8481 (W11c G1 ratchet) | ≥ 0.8470 |

**`2x-light-standard` · texture tier**

| scene | set | metric | claimed | measured | enforced floor |
| --- | --- | --- | --- | --- | --- |
| ~~`photo__rrect-lg__rest-tint-orange`~~ | holdout | `oklabDeltaEMean` | ≤ 0.07 **MET (W9)** | 0.0760 → 0.0628 | — |
| ~~`checkerboard__glass-over-glass__rest`~~ | holdout | `oklabDeltaEP95` | ≤ 0.17 **MET (W11a)** | 0.1909 → 0.1221 | — |
| ~~`light-solid__capsule-button__rest-tint-orange`~~ | calibration | `oklabDeltaEP95` | ≤ 0.17 **MET (W9)** | 0.1726 → 0.1032 | — |
| ~~`mid-dark-solid__capsule-button__rest`~~ | holdout | `oklabDeltaEP95` | ≤ 0.17 **MET (W9)** | 0.1775 → 0.0095 | — |
| ~~`photo__glass-over-glass__rest`~~ | holdout | `oklabDeltaEP95` | ≤ 0.17 **MET (W11a)** | 0.1901 → 0.0759 | — |
| `checkerboard__glass-over-glass__rest` | holdout | `ssimMean` | ≥ 0.93 **UNMET** | 0.8762 → 0.8948 (W11a ratchet) → 0.8896 (W11c G1, re-pinned by decision) | ≥ 0.8885 |
| `checkerboard__rrect-lg__rest` | holdout | `ssimMean` | ≥ 0.93 **UNMET** | 0.8823 → 0.8800 (W9 trade) → 0.8785 (W11c G1, re-pinned by decision) | ≥ 0.8775 |
| `checkerboard__rrect-md__rest` | calibration | `ssimMean` | ≥ 0.93 **UNMET** | 0.9266 → 0.9234 (W11c G1, re-pinned by decision) | ≥ 0.9224 |
| `checkerboard__rrect-ml__rest` | calibration | `ssimMean` | ≥ 0.93 **UNMET** | 0.8897 → 0.8810 (W11c G1, re-pinned by decision) | ≥ 0.8800 |

**`2x-light-standard` · dom tier**

| scene | set | metric | claimed | measured | enforced floor |
| --- | --- | --- | --- | --- | --- |
| ~~`checkerboard__capsule-button__rest-tint-blue`~~ | validation | `interiorLevelRatioGpuOverCss` | ≤ 1.25 **MET (W10)** | 1.6377 → 1.0092 | — |
| ~~`checkerboard__capsule-button__rest-tint-orange`~~ | calibration | `interiorLevelRatioGpuOverCss` | ≤ 1.25 **MET (W10)** | 1.3698 → 1.0037 | — |
| ~~`hc-text__capsule-button__rest-tint-orange`~~ | holdout | `interiorLevelRatioGpuOverCss` | ≤ 1.25 **MET (W10)** | 1.2657 → 0.9410 | — |
| ~~`photo__glass-over-glass__rest`~~ | holdout | `interiorLevelRatioGpuOverCss` | ≥ 0.8 **MET (W11a)** | 0.7967 → 0.9184 | — |
| `checkerboard__glass-over-glass__rest` | holdout | `ssimMean` | ≥ 0.92 **UNMET** | 0.8460 → 0.8687 (W11c G1 ratchet) | ≥ 0.8677 |
| `checkerboard__rrect-lg__rest` | holdout | `ssimMean` | ≥ 0.92 **UNMET** | 0.7990 → 0.7970 (W9 trade) → 0.8696 (W11c G1 ratchet) | ≥ 0.8686 |
| `checkerboard__rrect-md__rest` | calibration | `ssimMean` | ≥ 0.92 **UNMET** | 0.9058 → 0.9169 (W11c G1 ratchet) | ≥ 0.9159 |
| `checkerboard__rrect-ml__rest` | calibration | `ssimMean` | ≥ 0.92 **UNMET** | 0.8480 → 0.8468 (W9 trade) → 0.8765 (W11c G1 ratchet) | ≥ 0.8754 |

#### What the floors do and do not buy

They are enforced by `packages/calibration/test/adopted-thresholds.test.ts`,
which additionally proves — as a test, not a promise — that every floor stands on
a bound that was genuinely missed, that no floor is tighter than the measurement
it was pinned from, that none names a cell the gate does not reach, and that the
set is exactly 33 rows (27 after W9, §5.35; 23 after W10, §5.37; 17 after W11a, §5.39; 15 after W11b, §5.40; 12 after W11c G1, §5.42). A floor cannot be added by
accident, and adding one deliberately means editing a count that sits next to
this section's number.

Verified by mutation rather than by inspection: worsening a floored cell fails
CI, improving one passes, and improving one **past its adopted bound** also
passes. That last case matters — a construct that punished the improvement it
exists to invite would be worse than no construct.

What they do not buy is any change to what vitrea claims. Every row above is a
row where the shipped material is measurably not matching Apple's, and eight of
them are on holdout cells. The honest summary of this landing is that the gate
stopped being a statement about quality and became, on these thirty-three rows,
a statement about direction.

### 5.28 ADOPTED — the dark pair's tables, and the predicate on both axes (2026-09-01)

The last two ungated profiles. §5.3's reason for holding them back — no validation
or holdout column to bound against — **expired**: W1's split extension gave
`1x-dark-standard` and `2x-dark-standard` 18 calibration, 2 validation and 6
holdout cells per tier, and the frozen active bed measures all of them on both
tiers.

> **ADOPTED 2026-09-01, user-approved, both parts as proposed.** The tables below
> are enforced by `packages/calibration/test/adopted-thresholds.test.ts`, and
> option (2) of the question this section originally posed was taken: the
> conditioning predicate now carries the coherence rows as well as the shape rows.
> With that, **every profile in the matrix is gated** and `UNGATED_PROFILES` is
> empty for the first time since the gate existed. The section is kept in its
> proposing voice below, with the outcome recorded at the end, because a table is
> easier to trust when the argument that produced it is still visible.

This was written as a proposal in the same form every adoption in this wave took.
Adopting a table is the gate's call at the release; the cascade's job was to
compute it honestly and hand it over.

**How the bounds were derived.** §5.15's declared margin rule, unchanged: for a
`≤` row, the smallest half-step reaching 1.4× the worst measurement (1% step for
the unitless ones); for a `≥` row, 0.02 below the worst, floored to the
hundredth. The worst is taken over **both** columns rather than holdout alone —
holdout still *sets* the bound's honesty, but a table a calibration cell violates
is not enforceable, and one row here needs that (`2x-dark` dom contour p95 reads
2.0 on calibration against 1.0 on holdout).

#### `apple-macos-26.5-1x-dark-standard`

| axis | metric | texture, proposed | dom, proposed | texture cv / ho | dom cv / ho |
| --- | --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.93 | ≥ 0.93 | 0.9807 / 0.9523 | 0.9821 / 0.9523 |
| shape | contour distance mean | ≤ 0.5 px | ≤ 0.5 px | 0.3366 / 0.3024 | 0.3115 / 0.2370 |
| shape | contour distance p95 | ≤ 1.5 px | ≤ 1.5 px | 1.0000 / 1.0000 | 1.0000 / 1.0000 |
| perceptual | SSIM mean | ≥ 0.87 | ≥ 0.83 | 0.9311 / 0.8976 | 0.9069 / 0.8597 |
| perceptual | OKLab ΔE mean | ≤ 0.09 | ≤ 0.09 | 0.0286 / 0.0595 | 0.0308 / 0.0639 |
| perceptual | OKLab ΔE p95 | ≤ 0.17 | ≤ 0.18 | 0.1161 / 0.1156 | 0.1195 / 0.1283 |
| perceptual | edge-weighted mean | ≤ 0.04 | ≤ 0.05 | 0.0102 / 0.0244 | 0.0163 / 0.0305 |

#### `apple-macos-26.5-2x-dark-standard`

| axis | metric | texture, proposed | dom, proposed | texture cv / ho | dom cv / ho |
| --- | --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.93 | ≥ 0.93 | 0.9922 / 0.9509 | 0.9856 / 0.9507 |
| shape | contour distance mean | ≤ 1.0 device px | ≤ 0.5 device px | 0.2948 / 0.4185 | 0.2630 / 0.3321 |
| shape | contour distance p95 | ≤ 1.5 device px | ≤ 3.0 device px | 1.0000 / 1.0000 | 2.0000 / 1.0000 |
| perceptual | SSIM mean | ≥ 0.88 | ≥ 0.85 | 0.9446 / 0.9079 | 0.9280 / 0.8795 |
| perceptual | OKLab ΔE mean | ≤ 0.09 | ≤ 0.09 | 0.0287 / 0.0598 | 0.0308 / 0.0642 |
| perceptual | OKLab ΔE p95 | ≤ 0.17 | ≤ 0.19 | 0.1161 / 0.1168 | 0.1195 / 0.1295 |
| perceptual | edge-weighted mean | ≤ 0.04 | ≤ 0.05 | 0.0110 / 0.0248 | 0.0160 / 0.0301 |

**Every one of the 28 rows passes**, on both columns, with no floor and no
exceedance. That is worth stating plainly because it is unusual in this document:
the dark pair is the *cleanest* pair of profiles the frozen bed measures. The
mechanism §5.26 charters to W9 needs a bright, high-spatial-frequency backdrop to
bite, and the dark bed's backdrops do not supply one.

#### The coherence rows, and the one row NOT proposed

Cross-tier ΔE is comfortable and **is** proposed at the light profiles' own
bound: worst 0.0155 at 1× and 0.0159 at 2×, against ≤ 0.05.

The **interior-level ratio is not proposed**, and the reason is an instrument one
rather than a fidelity one. Both profiles are inside the 0.80…1.25 band on every
cell but one, and that cell is the same on both: `dark-solid__rrect-md__rest`,
reading 1.589 at 1× and 1.855 at 2×.

It is also the cell the conditioning predicate **already excludes on both arms**,
recovering 0.025 of its declared region at 1× and 0.020 at 2× — dark glass over a
dark solid under a dark scheme, which the extractor cannot separate at all. The
interior level is therefore being sampled over roughly two percent of the surface,
and a ratio of two such samples is measuring the instrument.

The clean fix is available and is deliberately left to the gate: **extend the
conditioning predicate to the coherence rows**, which currently carry it only on
the shape rows. That is a new instrument rule, and by this document's standing
practice a new instrument rule belongs to the gate that adopts it, not to the
pass that notices it is needed. With that extension both profiles would pass the
interior-ratio row unmodified.

#### What the gate is being asked

One question, with three defensible answers:

1. **Adopt all 30 rows** (28 fidelity + cross-tier ΔE ×2) and leave the
   interior-ratio row ungated, as §5.13 already left it for tinted cells.
2. **Adopt all 30 and the predicate extension**, gating the interior ratio too.
   Strictly more coverage; costs one new instrument rule.
3. **Adopt nothing yet.** Defensible only if the dark bed is expected to move,
   and nothing measured suggests it is.

The cascade's recommendation is **(2)**, because the predicate extension is
correcting an inconsistency rather than adding a licence: the same cell is already
excluded from the shape rows for the same measured reason, and a gate that trusts
a two-percent sample on one axis while refusing it on another is not one rule.

#### What the gate decided (2026-09-01)

**Option (2), both parts.** The 28 fidelity rows and the cross-tier ΔE row on both
profiles are enforced, and the conditioning predicate extends to the coherence
rows — so the interior-ratio row is enforced for the dark pair too, with the
degenerate cell excluded by the same measurement that already excludes it from the
shape rows.

Landed with three properties worth stating, because each was verified by mutation
rather than by reading:

- **The exclusion is by measurement, never by name.** The pin asserts
  `dark-solid__rrect-md__rest` FAILS a predicate arm and recovers under 5% of its
  region. Make that cell resolvable in a future bed and the pin fails — which is
  correct: the cell would then deserve gating, and nothing should route around
  that.
- **The extension did not empty the row.** A well-conditioned dark cell is still
  gated on its ratio, asserted directly; drifting one out of band fails the suite.
- **No floor was orphaned.** All eight coherence-floored light-standard cells pass
  the predicate, so extending it left §5.27's set at exactly 33.

The enforced suite now gates **six profiles** — 27 cases, 230 assertions' worth of
matrix — against a single bed.

### 5.29 The profile SHA named the file, not the material (2026-09-01)

The landing review returned one finding and it was real. Recorded here because it
is a provenance defect in the instrument, and because the artifacts it affects are
committed and cannot be re-captured.

#### What was wrong

`scripts/capture-web.ts` hashes the calibration profile FILE and writes the digest
into every cell's `capturePath`, under a stated contract: *"A capture whose optics
cannot be reproduced from what the cell records is not a data point."*

But the optics are not the file. They are the renderer's
`DEFAULT_MATERIAL_PROFILE` with the file's `patch` merged over it, and
`withMaterialOverrides` leaves any key the patch omits at its default. So a
constant that moves in the renderer's TypeScript and is not named in the patch
changes the rendered material while leaving the file — and the recorded digest —
untouched.

`sizeOcclusionGain` did exactly that. §5.26 refitted it 0 → 0.05, no profile
named it, and the committed artifacts show the consequence directly:

| artifact | rendered with | light-profile SHA in `capturePath` |
| --- | --- | --- |
| `results/2026-08-31-round-two.json` | `sizeOcclusionGain` = 0 | `2b828ba5d3c2` |
| `results/matrix.json` (frozen bed) | `sizeOcclusionGain` = **0.05** | `2b828ba5d3c2` |

**One label, two materials.** The captures themselves are sound — each was
rendered with whatever the code held at the time — but the record cannot tell the
two apart, which is the one thing it exists to do.

Nor was this catchable by the test that was supposed to catch it.
`tuned-profiles.test.ts` asserted that applying the light patch to the renderer's
default changes nothing, and that assertion passes *whatever* an unnamed constant
is set to, because an omitted key is left at its default by construction. The
guard was structurally blind in exactly the direction the defect travelled.

#### The fix, in two layers

1. **The patch now names every constant the calibration pipeline fitted** — 26 key
   paths, listed as `FITTED_CONSTANTS` in the test — rather than only those that
   happened to differ from a default. For the light profile the patch is still the
   identity; the point is that it is now an identity that *says what it asserts*
   instead of being silent. The dark profile stays a difference document, because
   padding it with values identical to the default would destroy the very
   distinction that makes the light profile's identity claim meaningful.

2. **`resolvedMaterialSha256`** — a digest over the fully resolved material
   (default + patch, keys sorted), recorded in both profiles and recomputed by the
   test. It moves when the rendered material moves, *whatever* moved it and
   wherever that constant lives. This is the layer that needs no maintained list
   and no judgment about what counts as fitted.

Both were verified by mutation rather than by inspection:

| mutation | old guard | new guards |
| --- | --- | --- |
| move a **fitted** default (`sizeOcclusionGain`) | passed | 2 cases fail |
| move an **unnamed** default (`glowGain`) | passed | 1 case fails (the fingerprint) |
| drop a fitted key from the patch | passed | 1 case fails (the named set) |

The middle row is the one worth reading: no list of fitted constants, however
carefully maintained, would have caught a change to `glowGain`. The fingerprint
does, and that is why both layers exist rather than the tidier one.

#### What is NOT repaired, and must not be misread

**The committed matrices still carry `2b828ba5d3c2`.** They are records of
captures that happened, and rewriting a recorded digest to a value that was not
what the file hashed to at capture time would be falsifying provenance to make it
look better. The frozen bed's cells therefore cite a profile file that does not
name every constant they were rendered with.

The correct reading of any `capturePath` digest dated on or before 2026-09-01:
**it identifies the profile file, not the resolved material.** For those artifacts
the material is pinned instead by the commit — `results/matrix.json` was
regenerated at `263f004`, whose tree holds the renderer defaults it was rendered
with. From this section forward the digest identifies both, and the fingerprint is
what makes that true.

Three stale `entries` records in the light profile were corrected while in there:
`tintAlpha` still asserted 0.62 against a shipped 0.46, `blurSigma` still read
"unchanged-deliberately" at 8 against a shipped 3, and `shadowFalloff` still gave
`shadowAlpha` 0.55 against a shipped 0.05. Each keeps its original prose and sweep
tables — a bound's history is part of the claim — under a `supersededValue` that
states what actually ships.

### 5.30 The W9 probe, declared before it runs (2026-09-02)

W9's Decision Log 1 (spec:
`docs/doperpowers/specs/2026-09-02-w9-backdrop-tone-sampling.md`) opens the
next wave probe-first: measure what the reference renders over structured
content as surface size and backdrop pitch vary, before any model is
designed. This section is the declaration — grid, split, scoring
statistics and verdict rules committed before the first capture, in the
§5.24 pattern. The probe fits nothing and freezes no bed; its product is
findings.

#### The grid — 56 cells, one profile, all data-only

Profile: `apple-macos-26.5-1x-light-standard` only. The mechanism §5.26
measured is scale-free in every prior reading, and hypothesis
discrimination does not need the 2x display reconfiguration. All new
backgrounds reuse EXISTING kinds (`checkerboard`, `text-rows`), so nothing
rebuilds and no TCC re-grant happens; the probe runs from its own scenes
file (`apps/reference-apple/scenes-w9-probe.json` via `VITREA_SCENES`) into
its own fixtures dir (`VITREA_FIXTURES`), leaving the frozen bed untouched.

New backgrounds (seven): `checkerboard-4`, `checkerboard-8`,
`checkerboard-32`, `checkerboard-64` (black/white at those cell pitches,
joining the existing 16); `checkerboard-lc16` — cell 16 at LOW contrast,
`a=[128,128,128]`, `b=[229,229,229]`, chosen so its linear mean (0.4997)
matches the black/white pair's 0.5 to 0.06%; `hc-text-7` (rowHeight 7,
barHeight 3 — the existing 14:6 duty exactly) and `hc-text-28` (28/12).

Scenes: the five-component size sweep (`rrect-sm`, `capsule-button`,
`rrect-md`, `rrect-ml`, `rrect-lg`; 21.9× area) over every checkerboard
pitch and the low-contrast pair; the three-component sweep (`rrect-sm`,
`rrect-md`, `rrect-lg`) over `hc-text-{7,14,28}` and the response anchors
`light-solid`, `dark-solid`, `mid-dark-solid` plus `photo` as the broadband
control; `rest-tint-orange` on `capsule-button` over checkerboard
{4, 8, 16, 32, 64}. 56 cells.

#### The split, declared now for the LATER fit

The probe reads everything; the split binds the fit phase that follows it.
Rule first, list second: **any probe cell that duplicates a frozen-bed cell
whose twin was holdout or floored takes the `recorded` role** — readable by
the study, forbidden to every fit and claim — so the frozen bed's floored
rows stay an untouched referee and no spent-holdout geometry re-enters a
fit role. The fit phase fits the pitch law on cells the frozen bed has
never seen.

- **recorded (8):** all five `checkerboard` (16) rest cells + its tint
  capsule (frozen twins floored/holdout), `hc-text__rrect-md__rest` at 14
  (frozen holdout twin), `photo__rrect-lg__rest` (frozen holdout twin).
- **holdout (9):** the ENTIRE `checkerboard-8` column — five rest cells
  plus its tint capsule (an interpolation pitch, never fitted) — and the
  three large-surface extremes `checkerboard-64__rrect-lg`,
  `checkerboard-lc16__rrect-lg`, `hc-text-28__rrect-lg` (corner
  extrapolation). One read, per X1.
- **validation (5):** `checkerboard-4__rrect-ml`,
  `checkerboard-64__capsule-button`, `checkerboard-lc16__rrect-md`,
  `hc-text-7__rrect-md`, `checkerboard-64` tint capsule.
- **calibration (34):** the remainder.

#### The scoring statistics

Interior level `L` per cell: mean linear luminance over the native
capture's interior region under the native silhouette, the coherence
metric's own interior definition (`packages/calibration/src/metrics/`).

**The empirical response curve replaces any vitrea constant in scoring.**
For each anchored component, `R_c(l)` is monotone (PCHIP) interpolation of
the measured interiors over `dark-solid` (linear luminance 0.0117),
`mid-dark-solid` (0.0595) and `light-solid` (0.8910), captured in the
same runs. `R` for `capsule-button` and `rrect-ml` interpolates the
anchored components in log-area. Inputs outside the anchor range clamp to
it — a declared approximation, reported alongside every score it touches.

For a two-level backdrop with linear levels `{l_i}` and weights `{w_i}`,
with `μ = Σ wᵢ lᵢ` and `μ_enc = linear(Σ wᵢ encode(lᵢ))` — where levels
AND weights are **measured from the rendered background raster**, never
assumed from the parameters. (Declared after the dry-run rasters and
before any capture: the canvas does not divide evenly at every pitch —
`checkerboard-64`'s measured linear mean is 0.4720, not 0.5, because
200 px holds 3.125 rows of 64 — and the text-rows duty rounds per pitch,
0.7504 at 7 against 0.7652 at 28. Raster-measured statistics make every
prediction self-consistent with what the reference was actually shown;
the equal-mean pair survives the check at 0.5000 vs 0.4997. Measured,
specifically, UNDER THE INTERIOR MASK — the backdrop behind the surface,
not the whole canvas: a centred `rrect-sm` at pitch 64 sits entirely
inside one checker cell, so its effective backdrop is uniform, and the
footprint histogram degenerates to one level exactly as the material
would see it. The blur kernel does pull surround from beyond the
footprint; that is a declared first-order approximation of the input,
reported with the scores.)

- **P0 — the current model:** `R_c(μ)`.
- **P1 — map-then-average (H1):** `Σ wᵢ R_c(lᵢ)`.
- **P3 — encoded-space averaging (H3):** `R_c(μ_enc)`.
- **P2 — band-limited input (H2):** `mix(P0, P1, g)` with
  `g = smoothstep(0, 1, pitch / (k · span_c))`, `span_c` the component's
  short side, and `k` the ONE free parameter, grid-searched on calibration
  cells only over the declared grid
  `k ∈ {0.005, 0.01, 0.02, 0.04, 0.08, 0.16, 0.32}`.

Score per hypothesis: RMS of `P − L` over the structured, non-`recorded`
rest cells, reported overall and per pitch, next to the raw per-cell
curves. **Verdict rules, declared:** a hypothesis is REJECTED when its RMS
exceeds twice the best hypothesis's AND its residuals are pitch-monotone
(structure, not noise). **H4 (a contrast term) survives** only if the best
luminance-only model's residual on the equal-mean pair
(`checkerboard` 16 vs `checkerboard-lc16`, per component) exceeds three
times the pooled run-to-run σ of those cells' interiors. The tint cells
are descriptive, not scored — the tint pick rides the same input, but its
gamut clip (§5.13) is a confound the rest state does not carry.

#### Protocol and provenance

The DL21 winning protocol verbatim: 6 s bare neutral reset before each
cell, stable order, unlocked + wake attested per cell with the per-cell
audit as the completion criterion, `--min-idle-seconds 45`, bimodality arm
on the five runs; a state-ambiguous cell that a score depends on is topped
up before scoring. Five runs record the confidence they bought (the
seventeen-run bar applies only to a bed freezing into the enforced suite,
which this is not). Every run snapshots whole before anything reads it.
Stop conditions are the W9 spec's: a measurement no hypothesis fits goes
back to the design table as a finding; a two-state epidemic on the new
backdrops reopens the doctrine question before scoring.

### 5.31 The probe, reported: the reference averages in the space this project calls wrong (2026-09-02)

Seven runs — the five declared plus two targeted top-ups the bimodality arm
demanded — every one 56/56 `presentedActive` by the per-cell audit. The
materialized majority-state bed, the per-cell state shares, and the full
score table are committed under
`packages/calibration/results/2026-09-02-w9-probe/`. Scores are byte-stable
between the five-run and seven-run passes.

#### The verdicts, by the declared rules

| hypothesis | RMS | verdict |
| --- | --- | --- |
| P0 — current model, `R(linear mean)` | 0.1070 | **REJECTED** (2.68× best, residuals systematically signed) |
| P1 — map-then-average, `Σ wᵢ R(lᵢ)` | 0.0683 | not rejected by the 2× rule (1.71×); dominated everywhere |
| P2 — band-limited, one fitted `k` | 0.0683 | **no support** — `k` ran to the grid bottom to impersonate P1 |
| P3 — encoded-space mean, `R(linear(Σ wᵢ encode(lᵢ)))` | **0.0400** | **the winner** |

Three structural facts carry more weight than the RMS ranking:

1. **Pitch does not matter.** P3's residual on `rrect-md` is +0.024 ± 0.003
   from pitch 4 to pitch 64 — flat. The response is a function of the
   backdrop's *composition* under the footprint, not of its spatial
   frequency. (Where composition itself changes with pitch — a centred
   `rrect-sm` inside one 64-px cell — the footprint statistics predict the
   jump: measured 0.9632 against 0.9713 predicted, over a uniform white
   cell.) H2 dissolves; the pitch axis was worth capturing precisely
   because it produced this null.
2. **The equal-mean pair is the discriminator it was designed to be — and
   it discriminated in an unplanned direction.** The full-contrast
   checkerboard renders 0.107–0.186 DARKER than its linear-equal-mean
   low-contrast twin, at every size, far beyond run noise. No
   linear-luminance model can produce any gap from equal means without a
   contrast term — but the pair is only equal in linear space. In encoded
   space the two backdrops differ hugely, and P3 predicts the gap's
   direction and 80–90% of its magnitude at every size (−0.148 vs −0.182
   on `rrect-sm`, −0.095 vs −0.107 on `rrect-lg`). What section 5.30 posed
   as a contrast term (H4) is mostly encoded-space averaging wearing a
   disguise.
3. **H4's remainder is second-order.** After P3, the pair residual is
   −0.011 to −0.013 on the three zero-noise components (above their
   degenerate 3σ bar of zero) and inside the bar on the two components
   that have run noise. A real, sign-consistent, ~0.01 extra darkening
   with contrast — recorded, an order of magnitude below the phenomenon
   P3 explains, and no constant is added for it now (the W9 spec's
   standing caution).

The tint rides the same input, descriptively: the orange capsule's interior
is 0.3585–0.3609 across the whole pitch sweep — flat, as a mean-input model
predicts.

#### The sentence this project has to say out loud

`backdrop-tone.ts` converts every texel to linear light before averaging,
documents that choice as correctness, and sizes `SAMPLE_EXTENT` around the
measured five-fold error that encoded-space averaging produced on the
impulse backdrop. The GPU tier's backdrop chain decodes sRGB at import and
keeps every mip level in premultiplied linear float — the same conviction,
enforced in hardware. The probe says the reference's tone response behaves
as if the backdrop were averaged in ENCODED space and the material's
response applied to that. Averaging in the physically-correct space is the
approximation; averaging in the "wrong" space is the reference. (Why the
GPU tier still missed less than the CSS tier: its per-pixel locality is a
partial map-then-average by construction, which lands between P0 and the
reference — exactly the measured ordering.)

This also collapses the §5.24-era trap into a feature: the browser's
`drawImage` downsampling averages in encoded space, which is no longer the
error `SAMPLE_EXTENT` exists to outrun but the model itself. That
simplification is the fit phase's to bank, not this section's.

#### The two-state material, on the new backdrops

Ten of 56 cells drew two byte-states across seven runs — minority share
14–29%, every minority the BRIGHTER, less-adapted attractor, scattered
across runs (no bad run; per-cell draws, the DL20/21 signature on fresh
backdrops). Not an epidemic; the declared stop condition does not fire.
The one that matters most: `dark-solid__rrect-sm__rest` drew its
light-appearance state once (0.7460 against a settled 0.0353) — on a DARK
SOLID, the strongest evidence yet that the attractor pair is the
material's light/dark appearance itself, not a backdrop-measurement
artifact. Majority-state (frequency-settled) aggregation is what every
number above uses; a mean would have dragged that anchor to 0.177 and
poisoned every small-component prediction.

#### What the fit phase inherits

The operational model, one sentence: **the tone axes' input is the encoded-
space mean of the backdrop behind the surface.** Both tiers currently feed
them a linear-space mean (global on CSS, kernel-local on GPU). The
implementation seam, the constants (if any), and the re-fit run under the
W9 spec's phases 2–5: declared protocol on the probe's calibration split,
one read of its holdout, and the thirty-three §5.27 floors as the
untouched referee.

### 5.32 The verification read, and the declared W7 refit (2026-09-02)

The encoded-mean input landed on both tiers and the verification ran: 39
probe calibration+validation cells re-rendered through the standard
pipeline (two contour-degenerate extreme-footprint cells written under
`--write-partial`, named in the run log) against the frequency-settled
probe bed. **The input model is right and the response to it misses**, the
case Decision Log 2's tuned-only-if-verification-misses clause reserved:

- vitrea renders the equal-mean pair nearly identically (0.7320 vs 0.7328
  on the capsule) where the reference gaps them by 0.19 — the corrected
  input (0.214 for the black/white checker) lands ABOVE
  `backdropToneHigh` (0.14), so W7 adaptation is zero exactly where the
  reference still adapts.
- a fresh solid cell exposes a pre-existing size-coupling failure:
  `mid-dark-solid__rrect-sm` renders 0.1375 against the reference's
  0.4561. Solids are invariant under the input swap, so this was always
  wrong and simply never measured — the old bed had no mid-dark small
  cell.
- structured-cell interior deltas fell from the old model's scale to
  +0.04…+0.15, short of the ~0.04 the probe's winning model reaches.

#### The declared refit

Three constants, the sweep script's standing objective (mean over probe
CALIBRATION cells of |Δ interior mean| + |Δ interior stdDev| + |Δ rim
peak|, web − native), declared before running:

- `backdropToneLow` ∈ {0.01, 0.02, 0.03, 0.05}
- `backdropToneHigh` ∈ {0.14, 0.3, 0.5, 0.8}
- `backdropToneSizeBias` ∈ {0.05, 0.13, 0.25, 0.4}

Holdout untouched; validation read after the pick; ONE probe-holdout read
at the end of the round, per X1.

**The falsification condition, stated before the sweep:** the reference's
response strengths, derived from the probe bed, are ≈0.97 at input 0.012,
≈0.41 at 0.06 (small component), with a long ≈0.12 tail at 0.214 — a
steep knee plus a shallow tail. If NO grid point brings the solid and
structured calibration cells inside 0.05 interior-mean error together,
the single-smoothstep form of the W7 response is falsified on this
richer bed, and a form round (Decision Log 3 of the W9 spec) opens with
the probe's own measured response curves as the candidate shape. The
sweep then was not wasted: its best point is the honest measurement of
what the current form can do.

### 5.33 The refit sweep, and the falsification of the mix form (2026-09-02)

The declared 64-point sweep ran to completion on the 32 measurable probe
calibration cells. Best point `Low=0.05 High=0.3 SizeBias=0.25` at
interior objective 0.10633 (spread across the grid 0.106…0.350, 3.29×;
the runner-up `SizeBias=0.4` within 0.0005 — the optimum is a plateau,
not a peak). **The falsification condition fired: zero of the 64 points
bring the solid and structured calibration cells inside 0.05
interior-mean error together.** At the best point the worst solid sits
at 0.0698, 14 of 23 structured cells miss (worst 0.2568,
`photo__rrect-sm`), and the misses run in BOTH directions —
checkerboard capsules render too bright by ~0.10 while photo and lc16
render too dark by up to 0.26. No monotone strength curve over one
argument fixes misses of opposite sign at neighbouring inputs. A
bookkeeping caution for anyone re-reading the ranking: the per-point
measured-cell count drifts (26–31 of 32; contour extraction fails where
a candidate's interior hugs its backdrop), so points are not scored on
identical cell sets — immaterial to the falsification verdict, which no
point passes on the cells it did measure.

#### The endpoint diagnostic: the mix's target is wrong, not its curve

Two diagnostic captures with degenerate constants — strength pinned to 0
(`Low=0.0001 High=0.0002 Bias=0`) and to 1 (`Low=0.98 High=0.99
Bias=0`) — bracket the mix's reachable span per cell. Because compare's
contour step fails exactly on the cells that matter most (dark solids at
pinned strength), all three quantities were re-measured under ONE
interior definition: the probe's own native-mask `interiorLevel`
(§5.30's silhouette from the first run, settled native level by
majority byte-state). Required strength per cell is then
`(native − web₀) / (web₁ − web₀)`:

| encoded input | cell | web₀ (s=0) | web₁ (s=1) | reference | s required |
|---|---|---|---|---|---|
| 0.110 | dark-solid sm | 0.4744 | 0.0117 | 0.0126 | **0.998** |
| 0.110 | dark-solid md | 0.4933 | 0.0117 | 0.4844 | 0.018 |
| 0.110 | dark-solid lg | 0.4922 | 0.0117 | 0.5061 | −0.029 |
| 0.271 | mid-dark sm | 0.4994 | 0.0595 | 0.4561 | 0.098 |
| 0.271 | mid-dark lg | 0.5163 | 0.0595 | 0.5862 | **−0.153** |
| 0.443 | photo sm | 0.5584 | 0.1516 | 0.5559 | 0.006 |
| 0.500 | checker-32 sm | 0.7321 | 0.2160 | 0.6327 | 0.193 |
| 0.500 | checker-32 lg | 0.7434 | 0.2160 | 0.7000 | 0.082 |
| 0.623 | hc-text-7 sm | 0.7852 | 0.5207 | 0.6847 | 0.380 |
| 0.698 | checker-lc16 sm | 0.7365 | 0.4448 | 0.8109 | **−0.255** |
| 0.950 | light-solid sm | 0.9432 | 0.8902 | 0.9713 | **−0.531** |
| 0.950 | light-solid md | 0.9408 | 0.8907 | 0.9373 | 0.070 |

(Full 32-cell table in the diagnostic artefacts; the excerpt carries
every structural fact.) Three of them:

1. **Six cells need strength outside [0, 1].** On lc16, mid-dark md/lg,
   photo-md and light-solid-sm the reference settles BRIGHTER than the
   strength-0 render — outside the mix's entire reachable span. W7's
   full-strength target is the backdrop tone (`mix(backdrop, tint, α)`
   collapses onto the backdrop); the reference's light-solid-sm settles
   at 0.9713, above the white backdrop itself (0.891 linear). The
   adapted appearance is the material's own light-state appearance —
   the same attractor the probe saw as the minority state in two-state
   cells — which merely COINCIDES with the backdrop on dark-solid, the
   one background W7 was originally fitted on. The target is wrong, not
   the strength curve in front of it.
2. **The size response on dark-solid is near-binary** (sm collapses at
   0.998 while md/lg sit at ≈0) where checkerboards show a gentle
   0.19→0.08 decay — no single curve over one biased argument produces
   both.
3. **At equal encoded input the reference's settled interior is
   structure-invariant.** lc16 (bimodal checker, linear mean 0.49) and
   hc-text (text rows, linear mean 0.695) share encoded mean ≈0.69 and
   settle at the same interior ≈0.81 across components — the interior
   tone is a FUNCTION of the encoded mean, which is §5.31's P3 stated
   as a rendering law.

#### The candidate form, evaluated on this bed

The response-curve law the falsification clause named: interior tone
target = `R_size(encodedMean)`, the monotone (Fritsch–Carlson) curve
through the three solid anchors' settled levels per component, log-area
interpolation between anchored components — evaluated with NO fitting
beyond the anchors the probe already measured:

- Solids exact by construction (they ARE the anchors). Overall RMS
  0.0337 against the smoothstep best point's 0.1063.
- 23 of 30 non-tint cells inside 0.05; the 7 misses concentrate on the
  smallest footprints over structured backdrops (photo sm +0.073,
  hc-text-7 sm +0.074, hc-text sm −0.081, hc-text-28 md +0.064,
  checker-4 sm/capsule +0.054/+0.065, checker-32 capsule +0.051) —
  second-order footprint-texture effects beyond the mean, the H4
  territory Decision Log 2 left unmodelled, here larger than the ~0.01
  the equal-mean pair suggested.
- One implementation caution measured here, not deferred: the DARK
  anchor's size dependence is itself a steep knee. Log-area
  interpolation between rrect anchors would give the 44 px capsule a
  smeared dark anchor (0.22) where the canonical reference demands full
  collapse (`dark-solid__capsule-button` byte-identical to its
  background, §5.27). The anchor-level-versus-size functions must carry
  that knee; the smoothstep may yet live THERE, in the size axis of an
  anchor row, where the data actually shows one.
- The tint-orange capsules need required strengths ≈2.5 under the mix —
  under the response-curve law the tone target applies to the neutral
  material's luma and the tint's chroma must ride it; the design of
  that coupling is part of the form change, and tint coherence rides
  the same acceptance (W9 charter).

Diagnostic artefacts: endpoint matrices, native-mask level tables, and
the backdrop-statistics dump live with the job records
(`w9-endpoint-*.json`, `w9-bg-stats.json`, `w9-refit-matrices/`); the
64-point ranking is in the sweep log. The decision this evidence feeds
is the W9 spec's Decision Log 3.

### 5.34 The response-curve law, implemented and read out (2026-09-02)

Decision Log 3 adopted; implemented on both tiers the same day
(renderer commit `cb19a9f`). What landed, in the mechanism's own terms:

- **The tone solve.** Per pixel on the GPU tier (mirrored per source on
  the CSS tier), the scheme neutral's luma is shifted in closed form so
  the composite `mean = (1 − k)·M₀ + k·toneLuma` lands on
  `R(encodedInput, sizeThickness)` — the monotone curve through the
  three solid anchors, thin/thick rows smoothstepped in thickness. Two
  measured corrections shaped the final form: the solve compensates the
  collapse's own mean pull (so the two never double-count), and where
  the light scheme's white neutral clamps an upward shift, the
  remainder is carried by the tint ALPHA — the light attractor is the
  material gone opaque-bright, the same "an adapting material stops
  transmitting" the collapse's alpha half was measured on. Without the
  alpha half, every upward cell (lc16, mid-dark md/lg, photo-md,
  light-solid-sm) rendered byte-identical to its unadapted self.
- **The collapse re-scope.** `low 0.03 → 0.02`, `high 0.14 → 0.055`,
  `sizeBias 0.13 → 0.05`: full collapse at dark-solid for thin
  surfaces including the 44 px capsule, zero by mid-dark-solid. The old
  band's partial collapse at 0.0595 WAS the mid-dark-small overshoot
  §5.32 discovered (0.1375 against 0.4561); under the re-scoped band
  plus the solve that cell reads 0.0086. `impulse__rrect-md`'s argument
  lands at 0.0539 against the new high (k ≈ 0.003 against the old
  band's 0.008 — the unadapted render that cell validated), and the
  solve's authority is zero at impulse's input by the fade-out rule.
- **One WGSL lesson for the file that can't test itself:** `target` is
  a reserved word, and a shader that fails to parse renders nothing
  while every TypeScript suite stays green — the flat-background
  capture was the only symptom. The compile check is cheap; run it.

The three reads, in the declared order, all against the frozen probe
bed at the shipped constants (patch-only profile, no tuning anywhere in
this round):

| read | cells | result |
|---|---|---|
| calibration | 31 measurable | interior objective **0.0691** (falsified form's best: 0.1063; pre-W9 shipped: 0.4340→0.1074 era); mean-term 0.0250; median cell 0.0131; 5 cells > 0.05 |
| validation | 5, never fitted | 0.0003 / 0.0089 / 0.0175 on ml + lc16-md + hc-text-7-md; misses only checker-64 capsule (+0.090) and its tint twin (0.154) |
| holdout | 9, the ONE read | six cells ≤ 0.0122 including all three large extremes; checker-8 sm/capsule +0.054/+0.060; tint twin 0.111 |

Every cell above 0.05, on every set, falls in exactly two classes, both
declared before the reads:

1. **Small footprints over structured backdrops** (+0.05…0.09,
   worsening with pitch): the per-source tone input reads the whole
   backdrop where the reference reads the footprint, plus the
   second-order texture remainder. This is the H4-and-locality
   remainder Decision Log 3 left unmodelled, and the encoded-space
   pyramid (per-footprint GPU means) is the escalation Decision Log 2
   named if the referee demands it.
2. **The tint pathway** (0.11–0.15): the tinted capsules render
   IDENTICALLY before and after the whole W9 change — a full-strength
   author tint displaces the adaptation per the composition contract,
   so these cells never touched the solve. Their miss is pre-existing
   and newly measured on these backgrounds, not a W9 regression; tint
   coherence rides the referee per the charter.

The holdout's error structure matches calibration's exactly — the same
two classes at the same magnitudes, nothing new — which is the
generalization the probe's split was designed to test. The round's
model work is CLOSED; what remains is the referee (§5.27's 33 floors on
the frozen canonical bed) with the constants landed in the profile
document.

### 5.35 The referee: six floors met, one trade, and the mechanism re-attributed (2026-09-02)

The frozen canonical bed was re-measured end to end — six profiles, both
tiers, twelve per-profile compare runs each under its own profile
document, holdout included (the one read of the new frozen
configuration). Three corrective findings surfaced by the first runs are
part of this record, each measured before and after:

1. **The response surface is scheme-scoped.** The anchors are LIGHT
   reference measurements; the dark profiles inheriting them read ΔE
   p95 0.08 → 0.58. `backdropToneResponseStrength` now stands the law
   down where its anchors carry no provenance — the dark profiles set
   0, the collapse still runs, and the dark bed is restored.
2. **The tone COLOUR and the tone LEVEL are different quantities.**
   Decision Log 2's swap had moved the collapse target onto the
   encoded reading; on the impulse grid the two means differ 2.6× and
   the validated capsule read ΔE p95 0.03 → 0.12. The sample now
   carries both (linear colour for the collapse, encoded level for the
   band and the response), and impulse is restored.
3. **The law rides only the un-degraded regime.** The accessibility
   references behave differently (nearly opaque, flat in span — W2),
   and the solve under their folds read reduced-transparency photo ΔE
   0.007 → 0.048 and cross-tier ratio 0.99 → 0.86. Where any policy
   fold touches the tone axis the solve stands down; those profiles
   are restored.

**The verdict on the thirty-three floors:**

- **Six floors MET their adopted bounds** — every ΔE floor on a
  non-glass texture cell, both scales: `photo__rrect-lg` tinted
  (0.0760 → 0.0628 against ≤ 0.07), `light-solid` tinted capsule
  (0.1726 → 0.1032 against ≤ 0.17), and `mid-dark-solid` capsule
  (0.1775 → **0.0095** against ≤ 0.17 — the cell class the wave was
  chartered on, nineteen times better). These claims restore.
- **Seven floors are VIOLATED, all `ssimMean`, all checkerboard
  rrect-lg/ml cells, by 0.0002–0.0072**: the solve lands the interior
  MEAN on the reference (0.7435 → 0.6946 against native 0.6999 on the
  1x texture cell) and pays a sliver of structural similarity for it.
  A measured trade, not an accident — the ratchet construct forbids
  moving a floor without a decision, so this is the round's open
  decision, not a fait accompli.
- **Twenty floors are unmet and essentially unchanged**, in exactly
  three classes, which is the referee's second finding: §5.26's
  attribution of all thirty-three rows to ONE mechanism (tone sampled
  without regard to size) is now partially FALSIFIED by its own cure.
  The tone mechanism owned the ΔE/level rows and fixed all six. What
  it never touched: the six cross-tier ratio floors on TINTED capsules
  (identical to four decimals — a full-strength author tint displaces
  the adaptation, so their miss is the tint pathway's); the
  glass-over-glass rows (pixel-identical — no backdrop tone is
  measured for nested glass, the axis stands down); and the
  checkerboard `ssimMean` rows (a structure metric the tone axis does
  not own — the same rows the trade above brushes). Three mechanisms,
  three future owners; floors stay pinned for all twenty.

Beyond the floors, the whole-bed regression scan against the frozen
matrix: 43 cells move worse by more than 0.005, all ≤ 0.033, all
inside their adopted gates — dominated by light-standard dom-tier
coherence ratios drifting 1.08 → 1.10 (band 0.8…1.25) and dom photo ΔE
p95 tails (+0.013 against gates at 0.17). The measurement predicates
also moved in the good direction: cells previously excluded as
degenerate became well-conditioned (the coherence cell that measured
1.64 reads 1.10), so the gate-coverage literals re-record with the new
bed. Renderer and platform-web suites are green; the golden e2e suite
is green without re-recording (its scenes pin the profile seam and
carry no host tone sample).

### 5.36 The tint pathway, measured: an opaque shade of the seed, not a wash (2026-09-02)

W10 opened on W9's Deferred with the six cross-tier ratio floors on tinted
capsules (1.27–1.64 against 0.80…1.25) and one standing account of them:
§5.13's "the CSS tier clips a saturated tint at 255 and renders it weaker".
The first thing this section records is that the account was measured
against the wrong side. The reference's own interior mean sits on the CSS
tier's side of every one of those ratios — `checkerboard` orange native
0.3603, CSS 0.3440, **GPU 0.4712**; `checkerboard` blue 0.2064 / 0.2347 /
**0.3837**; `hc-text` orange 0.3709 / 0.3835 / **0.4852**. The GPU tier is
the tier that is wrong, by +0.11…+0.18, and the CSS tier lands near the
reference by an accident of its alpha mapping (a tint whose luminance sits
near the reference backdrop level makes `cssTintAlpha`'s solve nearly
ill-conditioned, and it happens to solve high). Nothing about the gamut
boundary is load-bearing.

**What the reference actually renders**, read per pixel from the frozen
bed's fixtures and the W9 probe's tinted cells (native fixture against its
own untinted twin, capsule core eroded 5 px from the silhouette to exclude
the rim):

1. **The tinted material is opaque and hue-preserving.** Over every solid
   backdrop the tinted capsule's core is one colour to the byte — light-solid
   `(254, 148, 0)`, dark-solid and impulse `(255, 148, 0)`, standard
   deviation 0.0000 — and that colour is the seed. Over structured content
   the per-pixel colour is the seed **times a scalar**: the G/R ratio reads
   0.295 on every orange cell at every pitch (the rendered seed's own ratio,
   148/255 → 0.296), and the blue channel stays at exactly 0. A translucent
   tint over a white checker cell would desaturate toward white; the
   reference renders a *brighter orange*, not a paler one.
2. **The scalar is linear in the untinted material's own luminance at the
   same pixel.** With `u` the linear luminance of the untinted twin's pixel,
   `shade = c₀ + c₁·u` fits every light-standard cell at per-pixel RMS
   0.002–0.003:

   | cell | n px | c₀ | c₁ | rms | u range |
   | --- | --- | --- | --- | --- | --- |
   | probe `checkerboard-4` orange | 3540 | 0.539 | 0.477 | 0.0023 | 0.45…0.79 |
   | probe `checkerboard-8` orange | 3540 | 0.533 | 0.483 | 0.0031 | 0.42…0.82 |
   | probe `checkerboard` (16) orange | 3540 | 0.530 | 0.487 | 0.0024 | 0.43…0.81 |
   | probe `checkerboard-32` orange | 3540 | 0.531 | 0.482 | 0.0031 | 0.39…0.87 |
   | probe `checkerboard-64` orange | 3540 | 0.520 | 0.501 | 0.0024 | 0.37…0.80 |
   | canonical `photo` orange (1x) | 3540 | 0.549 | 0.454 | 0.0027 | 0.53…0.66 |
   | canonical `hc-text` orange (1x) | 3540 | 0.541 | 0.470 | 0.0026 | 0.44…0.85 |
   | canonical `checkerboard` blue (1x) | 3540 | 0.561 | 0.454 | 0.0028 | 0.43…0.81 |
   | canonical `photo` blue (1x) | 3540 | 0.576 | 0.430 | 0.0029 | 0.53…0.66 |
   | canonical `light-solid` orange (1x) | 3540 | — | — | — | u = 0.97, shade 0.99 |
   | canonical `checkerboard` orange (**2x**) | ×4 | 0.532 | 0.482 | 0.0030 | — |
   | canonical `hc-text` orange (**2x**) | ×4 | 0.539 | 0.473 | 0.0022 | — |

   Pooled over the 1x cells: `shade = 0.543 + 0.468·u`, RMS 0.0060. The mean
   shade over the checkerboard is **pitch-invariant** (0.821…0.830 from
   4 px to 64 px cells) while its per-pixel spread grows with pitch (sd
   0.025 → 0.099) — exactly what a law linear in a blurred, pitch-invariant
   mean produces. The same law predicts the cells it was not read from:
   `photo__rrect-lg` and `rrect-md` (u 0.686 / 0.665 → interior 0.362 /
   0.357 against native 0.3673 / 0.3650), the accessibility references
   (increased-contrast u 0.98 → shade 0.99, measured 0.990;
   reduced-transparency u 0.89 → 0.96, measured 0.956) **with no regime
   constant** — the folds enter through `u`, which already carries them.
   Hue: the blue cells fit with c₀ higher by ≈0.03; recorded as the law's
   residual on the second hue, not modelled.
3. **Strength composites in encoded space.** `photo` orange-half is, per
   pixel and per channel, the 0.501 mix in **sRGB-encoded** space between
   the untinted twin and the full-tinted twin (RMS 0.0019 at 1x, 0.0018 at
   2x). The same mix in linear light fits at weight 0.70 with RMS 0.0525
   and channel-dependent weights (0.45 / 0.57 / 0.78) — falsified. The tint
   is a layer of one opaque colour composited over the material at the
   author's opacity, in the display's encoded space, which is what a
   Core Animation layer with `opacity` does.
4. **Two regimes where the shade is 1.** The light scheme's collapsed cells
   (dark-solid, impulse — W7's `k = 1`) render the pure seed; and the DARK
   scheme renders the pure seed over checkerboard and photo alike (shade
   1.015, sd 0.008, over an untinted material at u = 0.105 — the law would
   say 0.59). One reading covers both: the shade tracks the material's
   luminance relative to its own opaque body level, and both regimes are
   "a dark body". That reading is a hypothesis — the dark bed has no tinted
   cell over a light backdrop to separate it from "the dark scheme does not
   shade" — so the dark profiles gate the shade off (`tintShadeStrength: 0`,
   the same shape as `backdropToneResponseStrength`) and the light scheme
   folds it by `(1 − k)`. The mid-collapse regime (mid-dark-solid,
   k ≈ 0.65) is unmeasured on tinted cells; the fold is the linear
   interpolation and is declared as such.

**Why vitrea misses.** Both tiers implement the wave's composition contract
literally: the author's colour displaces the adapted neutral and the tint
layer's alpha is the *material's* — `mix(backdrop, seed, α ≈ 0.6…0.7)`. That
is a wash: the checker shows through at full contrast (GPU interior sd 0.148
against native 0.048), the white cells desaturate it, and the mean lands
wherever `(1 − α)·backdrop` puts it. The tone map W3 shipped (`tintTone*`,
fitted to identity in §5.13 because a wash has no tone to fit) was the
right idea aimed at the wrong quantity: Apple's "range of tones mapped to
content brightness underneath" is a range of **shades of an opaque colour**,
from `c₀ ≈ 0.53` of the seed at black content to the seed itself at white,
read off the material's own local luminance.

**The dry run.** Applying the law with (0.53, 0.47) to each tier's *existing*
untinted capture — no code changed — and reading the interior mean over the
native silhouette:

| cell | native | GPU now | CSS now | GPU under law | CSS under law | ratio now | ratio under law |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `checkerboard` capsule orange (cal) | 0.3603 | 0.4712 | 0.3440 | 0.3627 | 0.3498 | 1.370 | **1.037** |
| `checkerboard` capsule blue (val) | 0.2064 | 0.3837 | 0.2347 | 0.2018 | 0.1946 | 1.635 | **1.037** |
| `hc-text` capsule orange (hol) | 0.3709 | 0.4852 | 0.3835 | 0.3714 | 0.3668 | 1.265 | **1.012** |
| `light-solid` capsule orange (cal) | 0.4319 | 0.5585 | 0.4807 | 0.4218 | 0.4241 | 1.162 | 0.995 |
| `photo` capsule orange (cal) | 0.3520 | 0.3245 | 0.3349 | 0.3503 | 0.3640 | 0.969 | 0.962 |
| `photo` capsule blue (cal) | 0.2063 | 0.2380 | 0.2233 | 0.1959 | 0.2036 | 1.066 | 0.963 |
| `photo` rrect-lg orange (hol) | 0.3673 | 0.3387 | 0.3434 | 0.3589 | 0.3727 | 0.986 | 0.963 |
| `photo` rrect-md orange (val) | 0.3650 | 0.3360 | 0.3436 | 0.3581 | 0.3720 | 0.978 | 0.963 |
| `dark-solid` / `impulse` orange (cal) | 0.4257 / 0.4254 | 0.4275 | 0.4268 | 0.4275 | 0.4275 | 1.002 | 1.000 |

Every tinted cell lands within 0.012 of the reference on both tiers and
the six floored ratios read 1.01–1.04 against a band of 0.80…1.25. A
prediction from the untinted captures is not the referee — the tiers'
untinted `u` is itself an approximation, per-source on the CSS tier — but
it is the strongest pre-implementation read this project has had.

**The declared protocol (X1, the fresh-split rule).** The six floored rows
are spent holdout and are never fitted against. The two shade constants are
fitted by per-pixel least squares on the **five probe tinted cells** alone
(`checkerboard-{4,8,16,32,64}` orange capsules, native against native —
vitrea does not enter the fit); every canonical tinted row on every profile
is then the referee, read once from a from-scratch matrix rebuild. The
objective is the per-pixel scalar-shade residual, declared here before the
fit runs. Hue independence rides the blue validation and holdout cells;
size independence rides the photo rrects; scheme independence is *not*
claimed (finding 4).


**The fit, run under the protocol (same day).** 17 700 pixels over the five
probe cells: `shade = 0.5289 + 0.4886·u`, RMS 0.0035 — `tintShadeDark 0.5289`,
`tintShadeLight 1.0175` (clamped at 1 in the law; the clamp bites only above
u = 0.964, past every structured cell's range). Out of sample on the canonical
bed, native against native: `hc-text` orange RMS 0.0034 (bias −0.0002),
`photo` orange 0.0029 (−0.0000), `checkerboard` blue 0.0121 (−0.0108), `photo`
blue 0.0134 (−0.0129). The blue bias is the hue residual, carried to the
referee uncorrected.

### 5.37 The W10 referee: six floors met, the untinted bed byte-identical, one instrument row (2026-09-02)

The frozen canonical bed re-measured end to end — six profiles, both tiers,
twelve per-profile compare runs under their own profile documents, the
holdout read once. One corrective finding surfaced by the first CSS-tier run
is part of the record: the tinted fold had been applied to the node optics
the GPU tier's foreground reads and not to the optics the CSS declarations
are built from (`cssTierDeclarations` applies the policy and size folds
itself, so it takes the pre-policy optics), and the first CSS captures were
the untinted material — `light-solid` tinted at 0.983, the untinted level.
The fold now lands on the declarations' input, with the shade read off the
policy- and size-folded source, and the CSS runs were repeated.

**The verdict on the six floors — all MET, restored as claims:**

| cell | set | ratio before (1x / 2x) | ratio after (1x / 2x) | band |
| --- | --- | --- | --- | --- |
| `checkerboard__capsule-button__rest-tint-blue` | validation | 1.6353 / 1.6377 | **1.0049 / 1.0092** | 0.80…1.25 |
| `checkerboard__capsule-button__rest-tint-orange` | calibration | 1.3695 / 1.3698 | **0.9996 / 1.0037** | 0.80…1.25 |
| `hc-text__capsule-button__rest-tint-orange` | holdout | 1.2651 / 1.2657 | **0.9383 / 0.9410** | 0.80…1.25 |

Every tinted row on every profile reads a ratio of 0.94–1.02, and both tiers
land on the reference rather than on each other: the light-standard 1x bed,
before → after —

| cell | set | tier | interior mean (native) | ΔE mean | ΔE p95 | SSIM |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard` capsule blue | validation | GPU | 0.3837 → 0.2099 (0.2064) | 0.0150 → 0.0034 | 0.1523 → 0.0110 | 0.9501 → 0.9869 |
| | | CSS | 0.2347 → 0.2088 | 0.0101 → 0.0047 | 0.0790 → 0.0145 | 0.9506 → 0.9780 |
| `checkerboard` capsule orange | calibration | GPU | 0.4712 → 0.3717 (0.3603) | 0.0111 → 0.0034 | 0.1061 → 0.0122 | 0.9590 → 0.9859 |
| | | CSS | 0.3440 → 0.3719 | 0.0088 → 0.0048 | 0.0606 → 0.0161 | 0.9556 → 0.9768 |
| `hc-text` capsule orange | holdout | GPU | 0.4852 → 0.3810 (0.3709) | 0.0109 → 0.0032 | 0.1106 → 0.0147 | 0.9733 → 0.9875 |
| | | CSS | 0.3835 → 0.4060 | 0.0064 → 0.0042 | 0.0549 → 0.0237 | 0.9681 → 0.9819 |
| `light-solid` capsule orange | calibration | GPU | 0.5585 → 0.4317 (0.4319) | 0.0111 → 0.0041 | 0.1032 → 0.0215 | 0.9825 → 0.9878 |
| | | CSS | 0.4807 → 0.4316 | 0.0059 → 0.0038 | 0.0352 → 0.0181 | 0.9845 → 0.9844 |
| `photo` capsule blue | calibration | GPU | 0.2380 → 0.2060 (0.2063) | 0.0084 → 0.0023 | 0.0805 → 0.0078 | 0.9822 → 0.9850 |
| `photo` capsule orange | calibration | GPU | 0.3245 → 0.3591 (0.3520) | 0.0076 → 0.0023 | 0.0776 → 0.0065 | 0.9852 → 0.9863 |
| `photo` capsule orange-half | calibration | GPU | 0.4708 → 0.4580 (0.4382) | 0.0070 → 0.0029 | 0.0715 → 0.0152 | 0.9859 → 0.9864 |
| `photo` rrect-lg orange | holdout | GPU | 0.3387 → 0.3652 (0.3673) | 0.0628 → 0.0070 | 0.1398 → 0.0178 | 0.9825 → 0.9931 |
| | | CSS | 0.3434 → 0.3677 | 0.0544 → 0.0124 | 0.1175 → 0.0214 | 0.9253 → 0.9360 |
| `photo` rrect-md orange | validation | GPU | 0.3360 → 0.3656 (0.3650) | 0.0214 → 0.0029 | 0.1023 → 0.0094 | 0.9927 → 0.9960 |

The collapsed cells (`dark-solid`, `impulse`) are unchanged to the digit, as
the `(1 − k)` fold predicts. The blue cells land within 0.004 of the
reference on the GPU tier despite the −0.011 hue residual in the shade,
because the blue seed's luminance is low enough that the residual is worth
0.003 of interior; the hue term stays deferred on that evidence. The
`orange-half` cell carries the largest remaining GPU-tier miss (+0.020),
consistent with the CSS tier's +0.049 on the same cell: both tiers read the
half-strength layer slightly bright, a second-order question for the
strength axis rather than the shade.

**The whole-bed regression scan** against the W9-close matrix: every
UNTINTED cell is byte-identical on both tiers — the untinted path is
untouched by construction and the scan confirms it. Of the tinted readings,
143 moved better by more than 0.005 and 15 moved worse, fourteen of them
contour distances on `photo`-tinted cells (the extractor class below) and one
a 0.012 coherence drift on the increased-contrast tinted capsule
(0.9996 → 0.9876, inside the band).

**One instrument row.** `photo__rrect-md__rest-tint-orange` (1x, GPU tier,
validation) was excluded from the shape rows by the conditioning predicate
(`bodiesWeb` 3 — the wash fragmented its silhouette) and now conditions
(one body, area 0.963, IoU 0.992), so it is gated — and its contour rows miss
(mean 5.89 px against ≤ 2.5, p95 33 px against ≤ 5). The miss is ONE interior
hole: the luminance-delta extractor cuts the silhouette wherever the pixel is
within 0.02 of the backdrop's luminance, and an opaque orange over the
photo's own orange region is exactly that (the native fixture has two such
holes, the web capture four; the 2x twin's holes coincide and read p95 0.0).
By decision (W10 Decision Log 2) the two rows are pinned as floors with the
extractor as their owner — a colour-aware silhouette rule, or a holes arm on
the predicate, is the Deferred charter — and the exclusion list re-records:
three texture rows leave it (the `photo` rrect-lg tinted cells at both
scales and this one) and three join on a single stray fragment each (the
increased-contrast `photo` tinted capsule, the `orange-half` capsule at both
scales). The enforced count reads 23.

Renderer, platform-web and calibration suites are green; the golden e2e suite
is green without re-recording (its scenes carry no author tint).

### 5.38 The remaining twenty-three floors, measured: three mechanisms, one of them a defect (2026-09-02)

The twenty-three rows §5.27 still floors after W10 fall into exactly three
classes by cell — ten on the two `glass-over-glass` cells (four ΔE p95, two
cross-tier ratios, four SSIM), eleven `ssimMean` rows on the checkerboard
rrect cells (`md`, `ml` calibration; `lg` holdout), and the two W10 instrument
rows — and this section measured each class per pixel before any charter was
written. The instrument used is a numpy replica of the compare's SSIM (11×11
Gaussian window, σ 1.5, stride 1, encoded luma, whole crop) that reproduces
every one of the twenty checkerboard rrect rows in `results/matrix.json` to
four decimals, so the decompositions below are of the enforced number, not of
a proxy for it. Native references, backdrop plates and the W9 probe bed
(`results/2026-09-02-w9-probe/`) are the evidence; nothing was recaptured.

#### 1. The SSIM bound is whole-crop, and the size trend is coverage

`ssimMean` averages every window of the 320×200 crop, glass or not. Splitting
it at the component's rectangle:

| `1x-light-standard` | `rrect-sm` | `capsule` | `rrect-md` | `rrect-ml` | `rrect-lg` |
| --- | --- | --- | --- | --- | --- |
| glass share of the windows | 0.036 | 0.092 | 0.265 | 0.493 | 0.768 |
| in-rect SSIM, texture | 0.806 | 0.639 | 0.734 | 0.784 | 0.803 |
| in-rect SSIM, dom | 0.693 | 0.664 | 0.635 | 0.653 | 0.629 |
| whole-crop SSIM, texture (the gated number) | 0.993 | 0.964 | 0.912 | 0.862 | 0.823 |

(2x: texture in-rect 0.840 / 0.693 / 0.841 / 0.891 / 0.914; dom 0.738 / 0.721 /
0.773 / 0.810 / 0.807.) Inside the glass the similarity is **not**
size-monotonic — the capsule is the worst cell on the texture tier and
`rrect-lg` is among the best. §5.26's "degrades monotonically with surface
area" is the glass's share of the crop, and the bound a large surface has to
meet is therefore a bound on the glass itself: for the 1x `rrect-lg` texture
row to read 0.88, its in-rect SSIM must reach ≈ 0.88; for the dom row to read
0.90, ≈ 0.91. Nothing about this changes what is claimed; it changes where the
work is.

#### 2. Where the loss lives: three regions

The whole-crop deficit (1 − SSIM) summed by signed distance from the contour,
as a share of the cell's total (negative is inside):

| cell | deep body (< −24 px) | rim band (−24…0 px) | outside (> 0 px) |
| --- | --- | --- | --- |
| 1x `rrect-lg` texture (0.823) | 39% | 45% | 16% |
| 1x `rrect-lg` dom (0.685) | 45% | 42% | 12% |
| 1x `rrect-ml` texture (0.862) | 29% | 55% | 24% |
| 1x `rrect-md` dom (0.882) | 21% | 58% | 21% |
| 2x `rrect-lg` texture (0.880) | 10% | 38% | 52% |
| 2x `rrect-lg` dom (0.797) | 27% | 39% | 34% |

The **rim band** is the largest term at 1x on both tiers, and within it the
ring 4–8 px inside the contour alone carries 17–25% of a cell's deficit at a
window SSIM of 0.26–0.43. The **outside** band dominates at 2x, where the same
11 px window is half the physical size; it is not the outer shadow's
amplitude — the shadow band's linear level matches the reference to 0.005 on
both tiers and both scales (1x `[4,12)` px below: native 0.423, GPU 0.428, CSS
0.425) — it is the windows that straddle the contour, and on the CSS tier the
contour band itself (0.534 against native 0.398: the 1 px border, no rim).
No phase offset anywhere: every interior correlates best with the plate at
zero shift.

#### 3. The deep body: a heavy blur, a faint sharp leak, and opacity that keeps rising

On the probe bed (five pitches × five spans, native 1x) a single Gaussian
does not fit the reference's interior — jointly across pitches its RMS is
0.023–0.046 of linear luminance and the per-pitch σ is non-monotone (1.5 /
1.2 / 2.5 / 3.5 px at pitches 8 / 16 / 32 / 64 on `rrect-md`). The row
profiles say why: at pitch 16 the `rrect-lg` interior is a ±0.015 swing with
crisp 8 px transitions; at pitch 32 it swings 0.55↔0.84 and at pitch 64
0.46↔0.90 with 24–32 px transitions; pitches 4 and 8 are gone. Two components
fit: **Y = a + t₁·G_σ₁(plate) + t₂·G₁(plate)**, one σ₁ per span, joint over
the five pitches —

| span (1x, native) | σ₁ (CSS px) | a (level) | t₁ (heavy) | t₂ (sharp leak) | RMS |
| --- | --- | --- | --- | --- | --- |
| `rrect-md` 96 | 8.5 | 0.416 | 0.296 | 0.235 | 0.015 |
| `rrect-ml` 128 | 9.0 | 0.438 | 0.335 | 0.171 | 0.0145 |
| `rrect-lg` 160 | 9.0 | 0.464 | 0.363 | 0.112 | 0.016 |

— a heavy blur near σ 9 that does not move past span 96, a sharp leak that
halves from 96 to 160, and a level that keeps rising. (`rrect-sm` and the
capsule are lens band nearly edge to edge and carry no deep body to fit.)
vitrea's body at pitch 16 (per cell, same model): GPU σ 3.8 (nominal 3; the
pyramid chain adds), t 0.41, a 0.485 — **identical at 96, 128 and 160**; CSS σ
3.0 exactly, t 0.563, a 0.362, identical at every span. Contrast survival
(`interiorStdDev` native ÷ backdrop) over the size sweep: reference 0.31 /
0.28 / 0.226 / 0.173 / 0.13; GPU 0.32 / 0.29 / 0.205 / 0.205 / 0.204; CSS
0.35 / 0.33 / 0.33 / 0.33 / 0.33. The size law's scatter facet exists on both
tiers (`sizeScatterGainMax`, the `scatterLod` mix in the optics pass and
`sizeScatterSigmaAt` on the CSS tier) and **ships at the identity**; the band
top at 96 (§5.14) stops the level too. §6.1's "blur sigma is not identifiable
from these backgrounds" is superseded: the probe's pitch axis identifies it.

**The two scales disagree in the reference.** At 1x a large surface is nearly
opaque with a faint crisp checker; at 2x it is a soft, moderate-contrast blur
(2x `rrect-md` fits a single Gaussian at σ 6.0 device px = 3.0 pt, t 0.41, r²
0.985, while 2x `rrect-ml`/`rrect-lg` fit no aligned Gaussian of the plate at
any σ — the structure is there and phase-aligned, correlation 0.92, but its
shape is not Gaussian). The 2x reference also retains more contrast at every
span (0.327 / 0.310 / 0.254 / 0.204 / 0.162). A law written once in CSS px
cannot land both scales; the 2x bed has no probe pitches. Recorded, not
resolved.

#### 4. The dry run: the body law alone meets one floor; the rim band decides the rest

vitrea's capture with its deep body replaced by the reference's fitted law
(the same cell's a, t₁, t₂, σ₁; hue kept), then with the rim band also
replaced by native pixels — whole-crop SSIM, against the adopted bound:

| cell | bound | measured | → body law | → + native rim band |
| --- | --- | --- | --- | --- |
| 1x `rrect-md` texture | 0.88 | 0.912 | 0.926 | 0.983 |
| 1x `rrect-md` dom | 0.90 | 0.882 | 0.898 | 0.972 |
| 1x `rrect-ml` texture | 0.88 | 0.862 | **0.884** | 0.968 |
| 1x `rrect-ml` dom | 0.90 | 0.793 | 0.834 | 0.954 |
| 1x `rrect-lg` texture | 0.88 | 0.823 | 0.871 | 0.972 |
| 1x `rrect-lg` dom | 0.90 | 0.685 | 0.785 | 0.956 |
| 2x `rrect-md` dom | 0.92 | 0.906 | 0.907 | 0.959 |
| 2x `rrect-ml` texture | 0.93 | 0.889 | 0.890 | 0.941 |
| 2x `rrect-ml` dom | 0.92 | 0.847 | 0.858 | 0.930 |
| 2x `rrect-lg` texture | 0.93 | 0.880 | 0.886 | 0.943 |
| 2x `rrect-lg` dom | 0.92 | 0.797 | 0.831 | 0.931 |

The body law is real and moves every 1x cell 0.014–0.10; it discharges one
floor by itself. With the rim band matched every cell sits 0.03–0.10 above
its bound. The CSS tier has no lens by contract (`refraction: "none"`, §4's
coherence wording), so its rim band is a contract question rather than a
fit — but the band arithmetic says the contract is not what keeps the
calibration cells red: with the body and outside bands matched, 1x `rrect-md`
and `rrect-ml` dom would read ≈ 0.92 and ≈ 0.91 against 0.90, and only the
holdout `rrect-lg` (≈ 0.87) and the nested cells would stay under. The lens
band on the GPU tier is a fit (`lensDepth`, the `(1 − depth)²` profile, the
rim-biased LOD, the 4–8 px ring), against the probe's pitch-32/64 cells where
the reference's lens is plainly resolved.

#### 5. Nested glass: the GPU tier's upper pane is a flat constant

Per region, linear luminance, both backdrops and both scales agree to 0.003:

| region (`photo`, 1x) | plate | native | GPU tier | CSS tier |
| --- | --- | --- | --- | --- |
| upper pane, inset 8 pt | 0.191 | **0.893** (σ 0.011) | **0.468** (σ 0.0000) | 0.899 (σ 0.013) |
| base only, upper dilated 12 pt | 0.234 | 0.656 | 0.642 | 0.712 |
| base ∪ upper (the gated interior) | 0.219 | 0.706 | 0.597 | 0.751 |

(`checkerboard`: upper 0.905 / 0.468 / 0.869; base-only 0.671 / 0.671 /
0.625.) The GPU tier's upper pane is the bytes 182,182,182 everywhere. The
mechanism is in the optics pass: a surface whose group has no backdrop source
(`flags.x = 0` — the nested group resolves `css-backdrop` per §6.4, and a
proxy is emitted for it per group) skips the body block, so `backdrop` stays
`vec3f(0)`, `colour = mix(0, adapted, adaptedAlpha)` bakes black in, and
`encode_output(colour, coverage)` writes it **opaque** — a white tint at α 0.46
over black is 0.46 linear, plus the rim and inner-shadow terms, 0.468. The
DOM's blurred base glass beneath the canvas never shows through. A defect,
not a law: the CSS tier, which filters in place, lands the upper pane within
0.006 of the reference on `photo`. It owns the four ΔE p95 rows (0.19 is the
pane), both ratio rows (0.597 ÷ 0.751 = 0.795), and the pane's share of the
four nested SSIM rows. With the pane composited premultiplied over the proxy
at the CSS tier's level, the GPU interior predicts ≈ 0.70 against native
0.706 and the ratio ≈ 0.93. The CSS base pane's +0.056 on `photo` is the dom
tier's standing photo level (0.729 against 0.673 on `rrect-lg`), inside its
bounds and not this class.

#### 6. The extractor: the luminance-delta rule cuts holes on the native side too

`photo__rrect-md__rest-tint-orange`, the same rule the compare applies
(|ΔY_linear| ≥ 0.02 against the plate, inside the declared region, no
morphology):

| side | 1x holes (px) | 2x holes (px) | hole |ΔY| mean | OKLab ΔE at the holes, min |
| --- | --- | --- | --- | --- |
| native | 2 (64, 44) | 6 (1672, 258, 175, …) | 0.010 | 0.124 |
| GPU tier | 4 (430, 65, 50, 1) | 4 (1958, 195, 2, 2) | 0.010 | 0.123 |
| CSS tier | 1 (61) | 1 (234) | 0.009 | 0.120 |

The holes are where an opaque orange's luminance meets the photo's own
(plate 0.37, capture 0.38); the reference's mask has them as well. In OKLab
the same pixels sit ≥ 0.12 from the plate, and the mask's own 1st percentile
is 0.11. **A ΔE rule at 0.02, 0.03 or 0.05 recovers 1.000 of the region with
zero holes on all twelve measured sides**, the `photo` nested cells included
(GPU 4 and 10 holes today). The interior mask is the native silhouette, so
the rule is bed-wide: every cell's shape and material numbers re-read from
the captures on disk (no recapture; SSIM and ΔE are whole-crop and do not
move), the predicate's exclusion list re-derives, and §5.15's published
counts restate.

#### What this section does not do

It fixes nothing and fits nothing. The three classes are chartered as one
composite round with three children in
`docs/doperpowers/specs/2026-09-02-w11-remaining-floors.md`; the order,
the cut and the protocol are that document's Decision Log 1.

### 5.39 W11a: the nested pane composites over the glass beneath it — six floors met, two ratchet up (2026-09-02)

The repair §5.38 §5 predicted, landed and refereed the same day. No
constant moved and nothing was fitted; the two nested cells are holdout and
stayed that way.

**The change.** A group with no pyramid to sample — a `css-backdrop` group
whose frost is a DOM proxy beneath the canvas, or a `none` group over the
page — used to leave the optics pass as the material mixed over BLACK and
written opaque. It now leaves as a **premultiplied layer**: the adapted
colour at the material's alpha, with the author tint, the inner shadow and
the rim each restated in the form that composites to the same thing, and
the outer shadow filling only what the surface's *coverage* leaves. The
browser composites that layer in encoded sRGB — the same space the CSS
tier's `rgba()` lands in — so the pair it is written at is the CSS tier's:
the renderer's own tint at the alpha `cssTintAlpha` solves at the mapping's
reference level (0.665 on the shipped profile), resolved once by the host
(`unsampledMaterial`) and handed through the bridge to exactly the groups
that sample nothing. The optics pass is gated on `flags.x`, so a sampled
group takes the pre-W11a path byte for byte.

**Two corrective findings on the way**, each measured before and after.

1. The first wiring kept the shadow's old fill, `body.a + shadowAlpha·(1 −
   body.a)`, which with an opaque body had always meant "the shadow fills
   the coverage ramp" but with a translucent layer means "the shadow fills
   the layer's own transparency" — the pane read 0.811 instead of 0.873,
   darkened by its own shadow showing through it. A `box-shadow` is clipped
   out of its border box; the shadow now fills `1 − coverage` and nothing
   else, and every sampled cell is unchanged by it (an opaque body's
   coverage and alpha are one quantity).
2. The rim, by arithmetic rather than by a miss. Added light has no
   premultiplied form — a canvas colour may not exceed its alpha — and the
   first layer form took white over the layer at the rim's weight, which is
   short of the additive term by the rim times the whole composite. The
   layer now carries the light in its opacity, `(a·c + rim, a + rim)`,
   which composites to the additive term short of only `rim × dst` — exact
   wherever the layer is opaque, which a full-strength author tint always
   is. What the platform-web GPU suite found on the way was an instrument
   fault, not a shader one: its "the rim is still on it" read on a tinted
   dom-mode panel sampled 2 CSS px inside the contour, outside the 1.5 px
   rim band, and had sat exactly on its threshold of 2 code values since
   W10's brighter shade — before W11a and under every layer form alike. At
   DPR 1 no fully covered pixel is inside the band at all. The read now
   runs at DPR 2 one device pixel inside the straight edge, where the rim's
   white lifts the seed's zero blue channel by more than 8.

**The referee** — the GPU tier re-captured on all six profiles, the CSS
tier on the nested scenes (the dom-tier ratio reads the GPU twin):

- **Byte identity.** 248 of the 254 web captures on disk are byte-identical
  to the W10-close bed. The six that differ are the six nested-scene GPU
  captures (light and dark, both scales) and nothing else — the change
  reaches exactly the path it was aimed at, and the untinted, un-nested bed
  is provably untouched.
- **The pane.** Linear luminance over the upper pane's interior (inset
  8 pt), `photo` 1x: native 0.893, GPU **0.468 → 0.873**, CSS 0.899;
  `checkerboard`: native 0.905, GPU **0.468 → 0.891**, CSS 0.869. The gated
  interior (both panes) on `photo`: native 0.706, GPU 0.597 → 0.689, CSS
  0.751; the 2x cells agree to 0.001. The GPU pane is now the arithmetic
  of the layer over the proxy — E(0.873) = 0.669 + 0.331·E(0.642), where
  0.642 is the GPU tier's own base pane — and the 0.026 it sits under the
  CSS tier is the CSS tier's brighter base (0.712, the dom tier's standing
  `photo` level, §5.38), not the pane.
- **Six floors MET**, both scales: `checkerboard__glass-over-glass__rest`
  texture ΔE p95 0.1909 → 0.1221, `photo__glass-over-glass__rest` texture ΔE
  p95 0.1906 → 0.0744 (1x) and 0.1901 → 0.0759 (2x), against ≤ 0.17; the
  `photo` dom-tier cross-tier ratio 0.7958 → 0.9180 (1x) and 0.7967 →
  0.9184 (2x), against ≥ 0.8. Beside them, on the same cells: texture ΔE
  mean 0.047 → 0.029 and 0.038 → 0.021, edge-weighted mean 0.054 → 0.015,
  `photo` texture SSIM 0.957 → 0.994, the cross-tier ΔE mean 0.039 → 0.022,
  and the `photo` GPU silhouette's four (1x) and ten (2x) holes gone
  (IoU 0.996 → 1.000) — the holes were the flat grey pane meeting the
  photo's level.
- **Two floors ratchet up.** The texture `ssimMean` on the checkerboard
  nested cell improves and stays unmet: 0.8409 → **0.8796** against 0.88 at
  1x (0.0004 short), 0.8762 → 0.8948 against 0.93 at 2x. The floors move to
  0.8786 and 0.8938: a floor records what the bed measures, and a cell that
  improved is held at its improvement. The remainder is the interior
  structure W11c owns — the base pane is a checkerboard rrect like any
  other. The two dom-tier SSIM floors are byte-unchanged (0.8069, 0.8460).
- **An instrument note for W11b.** On the checkerboard nested cell the
  reference's own silhouette carries 10 holes at 1x and 26 at 2x under the
  luminance-delta rule (the pane's lit rim and its white interior meeting
  white squares), and the repaired GPU capture now carries 4 at 2x where it
  had none — a lit pane over white is within 0.02 of the plate. The predicate
  has no holes arm, nothing gates on it, and it is the extractor's question.
- **The dark nested cells** moved by less than a code value — interior mean
  +0.0004, ΔE p95 +0.006 at 1x — inside every dark bound (§5.28); the dark
  pane's alpha is its own profile's through the same mapping.
- **The residual, recorded and not fitted.** The GPU pane sits 0.020 under
  the reference on `photo` and 0.014 on `checkerboard`; back-solving the
  reference's pane against its own base pane gives an effective encoded
  alpha near 0.72 against the mapping's 0.669. Whether that is the size law
  the reference applies to a 56 pt pane, the base's own rim under the pane,
  or a nested tone response (W9's Deferred "nested-glass tone") is a
  question for a calibration cell that does not exist — both nested cells
  are holdout, and the discipline forbids reading the answer off them.

**Enforcement.** Six floors removed and their claims restored in §5.27; two
re-pinned upward; `UNMET_ROWS` 23 → 17; the predicate's exclusion list is
unchanged (the `photo` nested GPU cell already conditioned at 0.996). Golden
e2e: `field-mask` — the one golden on the unsampled path (`noBackdrop`) —
re-recorded, its centre going from an opaque 121 to (121, α 121): the body
alone, no shadow under it; the isolation guard's hash for that scene
re-recorded with the attribution the file demands (the other eight
reproduce unchanged in the same run, `highlight-press-glow` — also unsampled,
captured from the highlight canvas — among them). Unit tests pin the pair's
path end to end: the host resolves it only on a live GPU tier over a proxy
or the page and never on a sampled or CSS-tier group; the bridge forwards it
only beside an unbound source; the renderer writes it, and only it, into
the optics uniform.

> **§6.4 is amended by this section.** "The glass-over-glass cells are a
> mixed-backend claim" described, as a fidelity property, a pane that was
> never rendered. The mixed backend stands — the upper pane's frost is the
> DOM proxy's `backdrop-filter`, sampled by the browser and not the shader,
> and it carries no lens (`refraction: "approximate"`) — but the pane is now
> the material over that frost, and the cells measure as such.

### 5.40 W11b: the silhouette extractor gains a chroma arm — two floors met, twenty-three cells gate (2026-09-02)

An instrument change, declared before it ran (W11 spec, "W11b declaration")
and refereed from the captures on disk: no pixel was rendered or captured,
and every web PNG is the W11a-close byte for byte.

**The rule.** Inside the declared region a pixel is the surface iff
|ΔY_linear| ≥ 0.02 **or** ‖Δab_OKLab‖ ≥ 0.03 against the plate — the
luminance-delta arm exactly as it was, plus an arm on OKLab's a/b plane
that fires where a surface differs from what is behind it in colour at a
matched luminance. The arms are orthogonal, the second is inert wherever
both sides are neutral (a/b are exactly zero), and the rule is a strict
superset of the old one: area cannot fall, holes cannot open, and the one
thing the change could do wrong — admit a stray chroma fragment — is a
declared stop. Shipped as `--silhouette-chroma-threshold`, default 0.03.

**Why not §5.38 §6's rule.** That section measured a pure OKLab-ΔE rule on
`photo` cells alone and reported it recovering every one. It does — and on
the rest of the bed it is a regression, because OKLab lightness is *less*
sensitive to linear luminance than the luminance arm near white
(dL/dY ≈ Y^(−2/3)/3: at Y 0.9 a ΔY of 0.02 is a ΔL of 0.007) and *more*
sensitive near black, where a single code value is ΔL ≈ 0.07. Measured on
the captures on disk at ΔE ≥ 0.03: the light-solid `rrect-md` reference
drops to 0.031 of its region in seven bodies, the light-solid capsule to
0.102, the `hc-text` `rrect-md` reference to 0.948 with four holes, and the
CSS checkerboard `rrect-md` takes 22 holes; at 0.02 the light-solid
`rrect-md` reference still reads 0.060. The union rule leaves every one of
those cells byte-identical. §5.38 §6's finding stands for what it measured
and is superseded as a rule.

**The threshold.** The hole pixels the arm exists for sit at Δab ≥ 0.12 and
the masks' own first percentile at 0.11; 0.03 is a 4× margin. At 0.02,
0.03 and 0.05 every cell measured produces the identical mask — the
outcome is insensitive to the threshold across a 2.5× range, which is what
"not fitted to the bed" looks like as a number.

**The referee** (scratch matrix from the captures on disk, all twelve
profile × renderer runs, compared column by column with the W11a-close
matrix):

- **Stops: none.** No cell's body count rose on either side; no mask
  exceeded its region; every `perceptual` value on all 230 cells is
  byte-identical (whole-crop metrics see no mask).
- **62 cells moved** on a shape, material or coherence value — every
  `photo`-backdrop cell on every profile and tier, untinted included (a
  white material over a saturated pixel differs from it in chroma where it
  happens to match in luminance; those were edge and hole pixels), plus three
  tinted capsules over neutral plates by a sub-pixel contour mean
  (0.033 → 0.022 px). The reference's own masks closed too: the 2x-dark
  untinted `photo` capsule's native holes 17 → 5, the 2x-dark tinted one's
  14 → 0, `photo__rrect-lg` at 2x-dark 41 → 0.
- **The two W10 floors MET**: `photo__rrect-md__rest-tint-orange` 1x
  texture reads IoU 0.9917 → **1.0000**, contour mean 5.889 → **0.000**,
  p95 33 → **0** px. Removed; the claims restored in §5.27.
- **Twenty-three cells LEFT the exclusion list, none joined** (52 → 29):
  the entire `bodiesWeb` tinted family. Before → after on the worst of them:
  `photo__capsule-button__rest-tint-blue` 2x dom, IoU 0.857 → 0.9997, p95
  37.07 → 0, nine web bodies → one; `photo__rrect-lg__rest-tint-orange` 2x
  dom, p95 132 → 0, contour mean 30.4 → 0.03, five bodies → one;
  `photo__rrect-md__rest-tint-orange` 2x dom, p95 68 → 0. Every one of the
  twenty-three reads IoU ≥ 0.995 and p95 ≤ 1 px and **meets every adopted
  shape bound** as an ordinary gated cell — no floor is pinned by this
  change.
- **What the mask moved underneath the material axis:** `interiorMeanNative`
  by at most 0.0047 (the tinted blue capsule, whose mask was 0.71 of its
  region) and by at most 0.0012 on any untinted cell; the cross-tier ratio
  by at most 0.010. The tuning objective's targets on tinted cells are now
  read over the whole surface rather than 70–96% of it.
- **Gated shape cells, calibration + validation, before → after** (§5.15's
  counts restated on the new masks):

  | profile | texture | dom |
  | --- | --- | --- |
  | `1x-light-standard` | 21 → 24 | 21 → 24 |
  | `2x-light-standard` | 18 → 21 | 21 → 24 |
  | `1x-light-reduced-transparency` | 5 → 6 | 5 → 6 |
  | `1x-light-increased-contrast` | 4 → 5 | 4 → 5 |
  | `1x-dark-standard` | 6 → 7 | 6 → 7 |
  | `2x-dark-standard` | 5 → 7 | 6 → 7 |

  (Holdout adds the `photo__rrect-lg` tinted dom cell at each light scale.)
  The 29 exclusions that remain are the `areaNative` family (references
  invisible over near-black; the increased-contrast material over the
  checkerboard's white), the `areaWeb` `hc-text` family (white glass over
  white differs in nothing, in luminance or in chroma), the 2x texture-tier
  checkerboard family, and `hc-text__rrect-md` at 2x — none of them a
  colour question.

**Enforcement.** Two floors removed; `UNMET_ROWS` 17 → 15;
`PREDICATE_EXCLUDES` re-recorded at 29 with the family account above; the
per-profile coverage counts derive from it and moved with it. A unit test
pins the arm: a reddish block within 0.011 of its plate's linear luminance
is invisible to the luminance arm and whole under the chroma arm, while a
neutral block three code values off stays outside both.

**The adoption note.** The scratch matrix the referee read is the one
adopted as `results/matrix.json`: the same twelve `--skip-capture` runs
over the same captures are deterministic to the byte, and re-running them
to write the canonical file would have changed only twelve timestamps.

### 5.41 W11c, gate G1: the body law measured in vitrea's own form, and the declared fit (2026-09-03)

§5.38 §3 described the reference's deep interior over structured content
as a heavy blur plus a sharp leak. This section refits it in the form the
GPU tier can actually render — a body blur mixed toward a coarser chain
level by a per-surface weight — and in the form the CSS tier can render —
one `blur()` widened with span — and declares the fit that lands. The
evidence is the W9 probe bed (native 1x, `checkerboard` at pitches 8 / 16
/ 32 / 64 × spans 32 / 44 / 96 / 128 / 160), the canonical 1x and 2x
captures, and the `photo` family as the null check. Nothing here is a
capture; the referee is §5.42.

#### 1. What the floored cells actually show at pitch 16

Fitting each canonical pitch-16 reference interior on its own to a single
Gaussian of the plate, `Y = a + t·G_σ(P)`:

| 1x, native | σ (CSS px) | t | a | RMS |
| --- | --- | --- | --- | --- |
| `rrect-sm` (32) | 1.25 | 0.340 | 0.444 | 0.011 |
| `capsule` (44) | 1.25 | 0.331 | 0.448 | 0.010 |
| `rrect-md` (96) | 1.25 | 0.246 | 0.556 | 0.012 |
| `rrect-ml` (128) | 1.25 | 0.165 | 0.609 | 0.012 |
| `rrect-lg` (160) | 1.00 | 0.093 | 0.659 | 0.013 |

The reference at pitch 16 is a **sharp, faint** checker — σ ≈ 1.25 and an
amplitude that falls from 0.34 to 0.09 with span — over a rising level.
vitrea's GPU body at the same pitch fits σ 3.8, t 0.41 at every span from
96 up (§5.38 §3); the CSS tier σ 3.0, t 0.56. The structure the SSIM
window compares is a mid-amplitude blur against a low-amplitude edge, and
that, not the mean, is the fifteen floored rows.

Why the sharp component looks faint: the heavy component (σ ≈ 9–10) has
flattened a 16 px checker entirely (contrast factor e^(−2π²σ²/p²) ≈ 0.002),
so it contributes level and nothing else at this pitch, and only the leak's
share of the transmission is visible. At pitch 32 and 64 the heavy
component is resolved and the two add — which is why the probe's pitch
axis identifies both where the canonical bed could identify neither
(§6.1).

#### 2. The reference in vitrea's form

GPU form: `Y = a + t·[(1 − k)·G_σb(P) + k·G_σb·gain(P)]`, one (σb, gain)
for the bed, k per span, (a, t) per span as nuisance (the level laws are
W2's and W9's). CSS form: `Y = a + t·G_σb·(1+(gain−1)k)(P)`. Joint over the
four pitches, all five spans, k = smoothstep(32, spanMax, span) with
spanMax free:

| form | best | RMS | current model |
| --- | --- | --- | --- |
| GPU | σb 2.0, gain 5, spanMax 256 | 0.0236 | 0.0416 (σ 3.8, k = 0) |
| CSS | σb 1.5, gain 5, spanMax 320 | 0.0363 | 0.0387 (σ 3, k = 0) |

The GPU form halves the residual but stays well above the unconstrained
two-component fit (0.016, §5.38 §3), and the per-pitch residual says why:
at pitch 16 the model over-retains contrast (std 0.066 against 0.042 on
`rrect-lg`) and at pitch 8 under-retains it — a σ 2 body is neither the
reference's sharp component nor its heavy one. The two-component fit's
own weights make the shape of the missing constraint explicit: the heavy
component's share is **0.56 at span 96, 0.66 at 128, 0.76 at 160** — a
slow, nearly linear rise that is already above half at the band top the
size law saturates at, and that a smoothstep from zero at 32 cannot
reproduce.

**With a floor** — `k = k₀ + (1 − k₀)·smoothstep(32, spanMax, span)`:

| k₀ | σb | gain | spanMax | RMS (all five spans) |
| --- | --- | --- | --- | --- |
| 0.4 | 1.25 | 8 | 256 | **0.0169** |
| 0.3 | 1.25 | 8 | 256 | 0.0173 |
| 0.5 | 1.25 | 8 | 320 | 0.0174 |
| 0.4 | 1.0 | 10 | 256 | 0.0176 |

— the two-component ideal, reached inside the renderable form. Per span
the weight reads 0.40 / 0.40 / 0.52 / 0.64 / 0.76; the heavy σ is 10 CSS px.
Per pitch on `rrect-lg` the interior std now tracks the reference at every
pitch (0.057 / 0.042 / 0.117 / 0.159 native against 0.039 / 0.053 / 0.109 /
0.163 modelled).

#### 3. The photo family does not pay

The same structure (σb, gain, k(span)) laid over the `photo` plate, with
only (a, t) per span free, against the native `photo` interiors:

| 1x native | current (σ 3.8, k 0) | fitted law |
| --- | --- | --- |
| `rrect-sm` | 0.0046 | 0.0040 |
| `capsule` | 0.0044 | 0.0047 |
| `rrect-md` | 0.0103 | 0.0099 |
| `rrect-ml` | 0.0146 | 0.0132 |
| `rrect-lg` | 0.0178 | 0.0154 |
| overall | 0.0153 | **0.0135** |

A law fitted on checkerboards improves the photo structure slightly. It
rides only structured content by construction (a broadband backdrop is
close to invariant under a change of blur width at these amplitudes), and
the null family confirms it rather than merely tolerating it.

#### 4. The SSIM dry run, body only

vitrea's capture with its deep body replaced by the fitted law at the
reference cell's own level and transmission, rim band and outside
untouched, whole-crop SSIM against the adopted bound:

| cell | bound | before | body law |
| --- | --- | --- | --- |
| 1x `rrect-md` texture | 0.88 | 0.912 | 0.926 |
| 1x `rrect-ml` texture | 0.88 | 0.862 | **0.883** |
| 1x `rrect-lg` texture | 0.88 | 0.823 | 0.870 |

`rrect-ml` meets on the body alone; `rrect-lg` is left with the rim band,
which §5.38 §2 measured at 45% of its deficit — gate G2's. The dom rows
(CSS, single Gaussian) reach 0.893 / 0.820 / 0.769 against 0.90 in the
same dry run: the CSS form cannot carry a sharp leak, and those rows are
G3's question at the referee.

#### 5. The 2x bed disagrees, and the decision on it

The 2x reference interior at pitch 16 fits a single Gaussian at σ 3 CSS
px, t 0.41 on `rrect-md` (r² 0.985) — no sharp leak, moderate contrast —
which is close to vitrea's *current* model (2x `rrect-md` texture SSIM
0.927 against 0.93). The 1x law applied at 2x moves two texture rows
slightly the wrong way in the dry run (`rrect-md` 0.927 → 0.925, `rrect-ml`
0.889 → 0.884) and the dom rows up. No law in CSS px or in device px
produces both beds: in device px the 1x heavy component is σ 9 with a σ 1
leak and the 2x one σ 6 with none. The 2x bed was captured on a virtual
HiDPI display (§6.2's external gate). **Decided (W11 Decision Log 4): the
law is fitted at 1x and predicted at 2x; 2x structure rows that do not
meet are held by decision with the claim narrowed to the 1x bed, and a 2x
regression past a floor stops the adoption.**

#### 6. The declared fit

Fit set: the twenty probe cells at spans 32 / 44 / 96 / 128; `rrect-lg`
held out. Grid: k₀ ∈ {0.2…0.6}, σb ∈ {1.0…2.0}, gain ∈ {4…12}, spanMax ∈
{128…320}.

| | k₀ | σb | gain | spanMax | RMS fit | RMS holdout `rrect-lg` |
| --- | --- | --- | --- | --- | --- | --- |
| **declared** | **0.40** | **1.25** | **8** | **256** | **0.0164** | **0.0174** |
| runner-up | 0.35 | 1.25 | 7 | 256 | 0.0165 | 0.0172 |
| current model | — | 3.8 | 1 | 96 | 0.0457 | 0.0366 |

Each constant sits at a clear minimum of its own sweep with the others
held (σb: 1.0 → 0.0177, 1.25 → 0.0164, 1.5 → 0.0190; k₀: 0.3 → 0.0175, 0.4
→ 0.0164, 0.5 → 0.0194; gain: 6 → 0.0180, 8 → 0.0164, 10 → 0.0191;
spanMax: 192 → 0.0247, 256 → 0.0164, 320 → 0.0174). The holdout falls
from 0.0366 to 0.0174 without having been fitted to.

**What lands** (W11 Decision Log 4): `blurSigma` 3 → 1.25 (K5: one number
on both tiers); `sizeScatterGainMax` 1 → 8; two new constants,
`sizeScatterFloor` 0.4 and `sizeScatterSpanMax` 256, giving the scattering
facet its own curve `k = floor + (1 − floor)·smoothstep(sizeSpanMin,
sizeScatterSpanMax, span)·fold` (the floor unfolded, the rise folded by the
accessibility cap like every facet). `sizeThickness` and the lens,
occlusion, inner-shadow and W9 response rows that ride it are untouched
and must read byte-identical on every solid cell's level. The GPU tier
mixes its body toward a fixed heavy level at σb·gain by the scatter
weight; the CSS tier widens its one blur on the same constants. The
constants are profile fields, so the isolation guard's attribution holds
through the `materialProfile` seam for the constants and is re-recorded
for the shader plumbing beside them.

### 5.42 W11c, gate G1 refereed: three 1x floors met, the 2x rows re-pinned by decision, the CSS contract narrowed (2026-09-03)

**Claim.** The two-component body law §5.41 §6 declared (`blurSigma` 1.25,
`sizeScatterGainMax` 8, `sizeScatterFloor` 0.40, `sizeScatterSpanMax` 256:
the GPU tier mixes a sharp σ 1.25 body toward a σ 10 scatter by `kScatter`,
the CSS tier runs one `blur()` at the mixed σ) was implemented on both
tiers, the bed re-captured on both tiers over all six profiles, and
refereed cell by cell against the W11b close. The three 1x texture-tier
`ssimMean` floors on `checkerboard__rrect-ml`, `__glass-over-glass` and
`__rrect-lg` are MET and removed; every dom-tier floor rose without
meeting and ratchets up; the four 2x texture-tier floors regressed by
0.0015–0.0083 — the direction §5.41 §5 predicted — and are re-pinned by
decision (W11 Decision Log 5). The enforced count is 12. Nothing outside
the structured-backdrop class moved.

#### 1. The referee bed

Twelve `compare.ts` runs (`--material-profile` on the light and dark
profile documents, `--renderer webgpu` and `css`, `--set
calibration,validation,holdout --write-partial`), 254 captures, 230 cells,
both accessibility preferences read 0 on the machine before the capture.
A driver note for X1: a cell's key carries its capture path, and the
capture path names the material profile document; when the document's
content changes, the twelve runs append their rows beside the previous
ones (460 cells) rather than replacing them. The canonical matrix was
reduced to the newest cell per (profile, scene, tier) before any reading —
`rm results/matrix.json` first, as X1 says, is the same thing done
earlier.

#### 2. The declared stops, none fired

| stop (§5.41 §6, Decision Log 4) | reading |
| --- | --- |
| a solid-backdrop cell moves by more than one code value | light-, mid-dark- and dark-solid: every perceptual and material row identical to the W11b close |
| a `photo` cell leaves its bounds | none; max ΔSSIM 0.0033, max Δ(ΔE-mean) 0.0015, max Δ(interior mean) 0.0018 |
| a dark-profile cell leaves its bounds | none; the largest dark move is `checkerboard__glass-over-glass` dom, 0.8597 → 0.8504 against ≥ 0.83 |
| a 2x floor crossed | **four crossed** — §4; the declaration's own prediction, and the decision it asked for |

The `impulse` family moved ≤ 0.0006. No cell newly misses an adopted
bound; the predicate's exclusion list is unchanged (the enforcement test's
`PREDICATE_EXCLUDES` still equals the machine's output).

#### 3. The fifteen floors, before and after

| cell | tier | 1x before → after (bound) | 2x before → after (bound) |
| --- | --- | --- | --- |
| `checkerboard__rrect-md__rest` | texture | 0.9122 → 0.9270 (≥ 0.88; met before and after) | 0.9266 → 0.9234 (≥ 0.93) **re-pinned** |
| `checkerboard__rrect-ml__rest` | texture | 0.8620 → **0.8963 MET** (≥ 0.88) | 0.8893 → 0.8810 (≥ 0.93) **re-pinned** |
| `checkerboard__glass-over-glass__rest` | texture | 0.8796 → **0.8987 MET** (≥ 0.88) | 0.8948 → 0.8896 (≥ 0.93) **re-pinned** |
| `checkerboard__rrect-lg__rest` | texture | 0.8233 → **0.8934 MET** (≥ 0.88) | 0.8800 → 0.8785 (≥ 0.93) **re-pinned** |
| `checkerboard__rrect-md__rest` | dom | 0.8819 → 0.8963 (≥ 0.90) ratchet | 0.9055 → 0.9169 (≥ 0.92) ratchet |
| `checkerboard__rrect-ml__rest` | dom | 0.7929 → 0.8481 (≥ 0.90) ratchet | 0.8468 → 0.8765 (≥ 0.92) ratchet |
| `checkerboard__glass-over-glass__rest` | dom | 0.8069 → 0.8499 (≥ 0.90) ratchet | 0.8454 → 0.8687 (≥ 0.92) ratchet |
| `checkerboard__rrect-lg__rest` | dom | 0.6850 → 0.8372 (≥ 0.90) ratchet | 0.7970 → 0.8696 (≥ 0.92) ratchet |

The structure the floors measure, read through the mask (interior
standard deviation, web against native, 1x): the GPU tier now sits on the
reference at every span — `rrect-lg` 0.102 → 0.064 against 0.065,
`rrect-ml` 0.102 → 0.082 against 0.087, `rrect-md` 0.103 → 0.099 against
0.113, the nested cell 0.132 → 0.123 against 0.132 — where before G1 it
carried a size-invariant 0.10. The texture-tier interior means did not
move (≤ 0.0008 on every cell): the law rides structure only, as declared.

§5.41 §4's dry run predicted 0.926 / 0.883 / 0.870 for the 1x texture
`rrect-md` / `rrect-ml` / `rrect-lg`; the bed reads 0.927 / 0.896 / 0.893.
The dry run replaced the deep body only; the landed law also runs under
the rim band and the outside band, and those windows moved with it.
`rrect-lg` — the holdout, excluded from the fit — meets by 0.013.

#### 4. The 2x rows: the predicted crossing, and the decision

§5.41 §5 predicted `rrect-md` 0.927 → 0.925 and `rrect-ml` 0.889 → 0.884
at 2x; the bed reads 0.9266 → 0.9234 and 0.8893 → 0.8810, and the two
holdout rows go with them (`glass-over-glass` 0.8948 → 0.8896, `rrect-lg`
0.8800 → 0.8785). Every 2x dom row rose, by 0.011–0.073. The 2x
reference's interior is one moderate Gaussian with no sharp leak (§5.41
§5), and the law that reproduces the 1x reference over-resolves it on the
texture tier by these amounts. Decision Log 4 made the crossing a stop;
the user's decision on it (W11 Decision Log 5): **adopt G1 and re-pin the
four floors at the new measurements**, the claim on these rows narrowed to
the 1x bed until a Retina capture exists (the 2x bed was captured on a
virtual HiDPI display, §6.2). The alternative — holding G1 back — would
have surrendered three met floors and every dom improvement against four
regressions under 0.01.

#### 5. The CSS tier: measured, and the contract narrowed (gate G3)

The dom rows rose everywhere and meet nowhere. The measurement behind
that, on the probe bed (native 1x, pitches 8 / 16 / 32 / 64, level and
transmission free per span, shared across pitches):

| span | `kScatter` | GPU law RMS | CSS σ today (mixed) | its RMS | best single σ | its RMS |
| --- | --- | --- | --- | --- | --- | --- |
| 32 | 0.400 | 0.0280 | 4.75 | 0.0708 | 2.25 | 0.0519 |
| 44 | 0.405 | 0.0281 | 4.79 | 0.0784 | 1.50 | 0.0192 |
| 96 | 0.519 | 0.0138 | 5.79 | 0.0615 | 2.00 | 0.0333 |
| 128 | 0.636 | 0.0148 | 6.82 | 0.0491 | 2.50 | 0.0361 |
| 160 | 0.764 | 0.0174 | 7.93 | 0.0376 | 6.00 | 0.0342 |

One Gaussian cannot be both sharp and faint the way the reference's two
components are (§5.41 §1): at the CSS tier's own transmission a sharp σ
renders the checker too strong (the pre-G1 state, σ 3.0 / t 0.56, SSIM
0.882 on `rrect-md`) and the mixed σ renders it too soft (today, 0.896;
interior standard deviation 0.069 against the reference's 0.113 on
`rrect-md`, 0.026 against 0.065 on `rrect-lg`). The best single σ halves
the residual on the probe and stays 2–3× the GPU law's; a dry run at the
reference's own transmission lifts `rrect-md` dom to 0.910, but the tier
does not own that transmission and the number is an upper bound. Two
side-effects of the softer blur are on the record: the CSS tier's interior
mean on the checkerboard cells fell by 0.008–0.012 (`rrect-lg` 0.644 →
0.632 against the reference's 0.707 — an encoded-space `blur()` moves the
linear mean with its σ on a black-and-white plate; §5.40's ΔE-mean on the
same cells still improved, by 0.003–0.015), and the five `hc-text` cells
that moved (X3's out-of-class scan: GPU +0.007 / +0.008, CSS −0.013 /
−0.027 at 1x, all inside bounds; `hc-text__rrect-md` dom reads 0.9029
against ≥ 0.90) are the same fact on text.

**What Chromium can do.** Two sibling elements over the same backdrop —
the first at `backdrop-filter: blur(1.25px)`, the second at `blur(9.92px)`
with `opacity: 0.4` — render 0.6·G₁.₂₅ + 0.4·G₁₀ of the backdrop to RMS
0.0011 in encoded luma (a third of a code value; the mix is taken in
encoded sRGB, as `blur()` itself is). The same second layer as a **child**
of the first renders the first alone: a nested `backdrop-filter` under a
filtered parent is inert. So the law is expressible in CSS, but only as a
second layer drawn after the sharp one and under the host's content —
which is not the tier's in-place, no-proxy form (`css-tier.ts`: the filter
sits on the host element itself and nothing is layered) and puts the rim's
painting order in question. And the dom rows' deficit after the body is
the rim band (§5.38 §2), which no CSS form carries.

**Decided (user, W11 Decision Log 5).** G3 narrows the claim: the CSS
tier's body is the law's single-blur form at the mixed σ, the dom floors
ratchet to the new measurements, and the two-layer form is chartered as
deferred work with the evidence above (W11 spec, Deferred). The dom rows'
adopted bounds stay as claims the tier does not meet.

#### 6. What changed on the tiers

Renderer: `sizeScatterFloor` and `sizeScatterSpanMax` on the material
identity; the aux channel carries the surface's span, and both curves
(`sizeThickness` for the lens, the occlusion and the inner shadow;
`scatterThickness` for the body mix) are computed per pixel in the optics
and highlight passes from uniforms; the heavy tap's LOD is
`log2(sizeScatterGainMax)` above the body's. CSS tier: `scatterThickness`
drives `blur()`'s σ and `sizeThickness` the occlusion alpha — the two
facets no longer share one curve. Five goldens re-recorded
(`refraction-checkerboard`, `lens-size-scaling`, `rim-two-references`,
`concentric-nesting`, `union-pair`), the isolation hashes attributed: the
two checkerboard scenes carry the delta, the gradient scenes move by at
most one code value, the flat and unsampled scenes are byte-identical.
`sizeThickness` and the lens, occlusion and W9 rows are untouched, and the
solid and photo levels in §2 say so.

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
