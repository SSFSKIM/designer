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
| shape | silhouette IoU | ≥ 0.82 | 0.8489 | 0.9620 |
| shape | contour distance mean | ≤ 2.5 px | 1.9336 | 0.5450 |
| shape | contour distance p95 | ≤ 5.0 px | 4.0000 | 2.8284 |
| perceptual | SSIM mean | ≥ 0.88 | 0.9046 | 0.9026 |
| perceptual | OKLab ΔE mean | ≤ 0.07 | 0.0533 | 0.0548 |
| perceptual | OKLab ΔE p95 | ≤ 0.17 | 0.1070 | 0.1337 |
| perceptual | edge-weighted mean | ≤ 0.11 | 0.0573 | 0.0923 |

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
| shape | silhouette IoU | ≥ 0.85 | 0.8987 | 0.9368 |
| shape | contour distance mean | ≤ 2.0 px | 1.2456 | 1.1081 |
| shape | contour distance p95 | ≤ 4.0 px | 2.8284 | 2.2361 |
| perceptual | SSIM mean | ≥ 0.90 | 0.9036 | 0.9205 |
| perceptual | OKLab ΔE mean | ≤ 0.08 | 0.0535 | 0.0560 |
| coherence | cross-tier OKLab ΔE mean | ≤ 0.05 | 0.0124 | 0.0312 |
| coherence | interior level, GPU ÷ CSS | 0.80 … 1.25 | 0.893 … 1.080 | 0.844 … 1.040 |

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
| shape | silhouette IoU | ≥ 0.85 | 0.8768 | 0.9596 |
| shape | contour distance mean | ≤ 5.0 device px | 3.7548 | 1.1849 |
| shape | contour distance p95 | ≤ 10.0 device px | 8.0000 | 5.6569 |
| perceptual | SSIM mean | ≥ 0.93 | 0.9582 | 0.9593 |
| perceptual | OKLab ΔE mean | ≤ 0.07 | 0.0533 | 0.0546 |
| perceptual | OKLab ΔE p95 | ≤ 0.17 | 0.1070 | 0.1333 |
| perceptual | edge-weighted mean | ≤ 0.12 | 0.0537 | 0.1002 |

#### Dom tier, `apple-macos-26.5-2x-light-standard`, Chromium, `renderer: css`

| axis | metric | adopted | worst cal+val | worst holdout |
| --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.85 | 0.8978 | 0.9363 |
| shape | contour distance mean | ≤ 4.0 device px | 2.3744 | 2.2484 |
| shape | contour distance p95 | ≤ 8.0 device px | 5.3852 | 5.0000 |
| perceptual | SSIM mean | ≥ 0.92 | 0.9679 | 0.9509 |
| perceptual | OKLab ΔE mean | ≤ 0.08 | 0.0534 | 0.0559 |
| coherence | cross-tier OKLab ΔE mean | ≤ 0.05 | 0.0128 | 0.0313 |
| coherence | interior level, GPU ÷ CSS | 0.80 … 1.25 | 0.895 … 1.080 | 0.845 … 1.041 |

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
| shape | contour distance mean | ≤ 1.5 px | ≤ 1.5 px |
| shape | contour distance p95 | ≤ 3.5 px | ≤ 3.5 px |
| perceptual | SSIM mean | ≥ 0.96 | ≥ 0.91 |
| perceptual | OKLab ΔE mean | ≤ 0.04 | ≤ 0.04 |
| perceptual | OKLab ΔE p95 | ≤ 0.08 | ≤ 0.07 |
| perceptual | edge-weighted mean | ≤ 0.10 | ≤ 0.11 |

The tightest table in this document, and that is the measurement rather than
ambition: the reduce-transparency material is nearly opaque on both sides, so
there is very little backdrop left for the two to disagree about — worst holdout
ΔE mean 0.0300 against light-standard's 0.0548.

#### `apple-macos-26.5-1x-light-increased-contrast`

| axis | metric | texture | dom |
| --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.85 | ≥ 0.80 |
| shape | contour distance mean | ≤ 1.8 px | ≤ 2.6 px |
| shape | contour distance p95 | ≤ 3.2 px | ≤ 5.5 px |
| perceptual | SSIM mean | ≥ 0.86 | ≥ 0.83 |
| perceptual | OKLab ΔE mean | ≤ 0.06 | ≤ 0.07 |
| perceptual | OKLab ΔE p95 | ≤ 0.10 | ≤ 0.09 |
| perceptual | edge-weighted mean | ≤ 0.17 | ≤ 0.18 |

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

| axis | metric | texture, proposed | dom, proposed | worst cal+val | worst holdout |
| --- | --- | --- | --- | --- | --- |
| shape | silhouette IoU | ≥ 0.88 | ≥ 0.92 | 0.9165 / 0.9677 | 0.9358 / 0.9659 |
| shape | contour distance mean | ≤ 1.5 px | ≤ 1.2 px | 0.5577 / 0.4207 | 0.8255 / 0.5715 |
| shape | contour distance p95 | ≤ 4.0 px | ≤ 3.5 px | 2.8284 / 2.8284 | 3.0000 / 2.0000 |
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
falsified constant, and granted W7's mid-dark miss a documented exceedance. This
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
