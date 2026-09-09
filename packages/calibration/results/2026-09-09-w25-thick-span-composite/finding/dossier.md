# The thick-span composite — grounding dossier

Assembled 2026-09-09 from the repository at `4c6b321` (0.13.0 published, W24 recomposed).
Read-only; nothing here is new measurement. Paths are relative to
`/Users/new/Developer/GitHub/designer`. Numbers are quoted as recorded.

---

## 1. What the term was defined to be, and every restatement

**Origin — wave Decision Log 23 (c)**, `docs/doperpowers/specs/2026-08-28-post-v1-wave.md:992`
(the ruling) and `:1027` (the clause):

> "…then **the thick-span composite with a bed amendment that puts large spans into calibration**
> (`photo__rrect-lg` holdout ΔE 0.036; large spans four to six times the capsule's); then the
> coverage charters…"

Read in its context (`:992–1008`): (a) fidelity waves are chartered on the **GPU tier's** gap to
Apple, the CSS tier derives from the same profile and a CSS-only residual is recorded rather than
chartered; (b) the queue's drops and keeps; (c) the GPU wave order — W20 capsule corner, W21 dark
scheme, **then the thick-span composite**, then the coverage charters.

So as chartered the term has two halves: **a bed amendment** (large spans into calibration — today
`rrect-lg` and `glass-over-glass` are wholly holdout) and **the material work on thick surfaces**.

**Later restatements, in order** (each adds a named term, none narrows the original):

| where | what it added |
| --- | --- |
| `2026-09-06-w21-dark-scheme.md:297`, `:402`, `:704` | ordering only: W21 first, the composite after the 0.10.0 cut |
| `2026-09-08-w22-resting-sweep.md:52–56`, `:174–175`, `:305–306`, `:376–377` | **the base pane's haze** in the nested pane "belongs to it; G0 hands it the per-pane blur reading" |
| `c9a-fidelity-claims.md:13127` (§5.94 §5), `:13135` | the haze with its number: `blurSigmaNative` 4.84 px at 2x against web 0.69, fit residual 1.81 |
| `2026-09-08-w23-collapsed-rim.md:18`, `:332–333`, `:713`; claims `:13567–13570` (§5.99) | the user's eye names it again — "Apple's bottom glass is very slightly less transparent" |
| `2026-09-09-w24-lit-edge.md:218`; claims §5.111 `:14422` | "next, on the user's word" |
| `tech-debt-tracker.md:1003` (W24 G2 entry) | **the scatter kernel's width is the thick-span composite's** |
| `2026-09-09-w24-lit-edge.md:297–300`, `:433–434` | the along-side rim variation on thick panels named a **thickness term**, deferred |

**Recording gap worth knowing before the charter.** Three of the composite's own items are
**spec-only and absent from `tech-debt-tracker.md`**: the base pane's haze, the along-side thickness
term, and the CSS tier's large-span table. `tech-debt-tracker.md:1062` cross-references "the seven
nested-pane floors' entry", which does not exist as a heading.

---

## 2. Every recorded gap on thick surfaces

Thick components (`apps/reference-apple/scenes.json:107–143`): `rrect-md` 160×96 r20,
`rrect-ml` 224×128 r27, `rrect-lg` 280×160 r34, `toolbar-group` 3×(44×44) spacing 12,
`glass-over-glass` base rrect 220×130 r24 + overlay rrect 120×56 r16 at offset [0,−8].

### 2a. The base pane's haze — `checkerboard__glass-over-glass__rest`, holdout

| reading | scheme/scale | reference | vitrea | where |
| --- | --- | --- | --- | --- |
| `blurSigmaNative` (matrix's edge-spread fit on a checker step), texture/webgpu | dark 2x | **4.839670772780068**, residual **0.35754451750162586** | **0.6920140408270664**, residual **1.8113307236677878** | `results/matrix.json` cells[136]; claims §5.94 §5 (`:13127`); W22 spec `:54` |
| same, dom/css | dark 2x | 4.839670772780068 / 0.35754… | **1.23932712697578**, residual **1.181588860561356** | `results/matrix.json` cells[135] |
| σ-match (`blurSigmaMatchPx`, whole-region) | dark 2x | **16.00** (the search ceiling) | **8.00** | claims §5.94 §5 (`:13254`); `results/2026-09-08-w22-resting-sweep/g0/stack.txt` |
| σ-match, `checkerboard` | light 2x | 16.00 | **7.50** (GPU), 5.75 (CSS) | `g0/stack.txt` |
| σ-match, `photo` | light 2x | 16.00 | **12.50** (GPU), 13.25 (CSS) | `g0/stack.txt` |
| σ-match, `checkerboard` | light/dark 1x | **1.50** | **2.20** (GPU), 1.70/2.00 (CSS) | `g0/stack.txt` |
| base body (declared reader, eroded 6 px) | dark 1x/2x | 0.0467 / 0.0475 | 0.0470 / 0.0475 (GPU) | `g0/stack.txt` |

Unchanged by W22 G3's overlay fix — claims §5.96 §5 (`:13431–13432`): "the base pane's haze is
unchanged (σ-match 16.00 native against 8.00 web at 2x dark) and remains the thick-span composite's."
The 1x reading (native 1.50 vs web 2.20) runs the **opposite** way from the 2x reading. Note the two
instruments disagree in kind: `blurSigmaNative` is an edge-spread fit on a checker step;
`blurSigmaMatchPx` is a whole-region σ that saturates at the search ceiling 16.00
(`g0/read-stack.py:118–141`, grid `0…4.0` step 0.1 then `4.0…16.0` step 0.25).

**Two corrections the charter must carry.** (i) The "fit residual 1.81" quoted at claims `:13127`
is **`blurFitResidualWeb`**, not the native residual — the native fit's residual is
**0.35754451750162586**. (ii) `packages/calibration/src/report.ts:391–397` defines that field as the
residual "as a fraction of the step height. **Large means σ is not identifiable.**" So vitrea's
0.692 at 2x dark is an **unidentifiable** width, not a measurement of a sharp material; the CSS
sibling reads 1.239 at residual 1.182 on the same fixture. The reference's own fit at residual
0.358 is the trustworthy half of the pair. The whole-region σ-match exists (`read-stack.py`'s
docstring says so explicitly) to avoid exactly this confusion, and its native value 16.00 is the
**grid's ceiling** — the reference's haze is ≥ 16 px and the residual ≥ 8 px
(`g0/g0-findings.md` §6.4). Max `blurSigmaNative` anywhere in `results/matrix.json` is 5.0938.

### 2b. The scatter kernel's width, and the transmitted dot's FWHM

`impulse__capsule-button` (validation; collapsed) and `impulse__rrect-md` (validation; uncollapsed).
`results/2026-09-09-w24-lit-edge/g1/psf.py` fits box⊗(sharp+heavy) Gaussians in **device** px
(`g1/g1-findings.md:157–164`, `g1/transmission-read.txt` §3):

| profile | sharp σ (device px) | σ (CSS px) | heavy σ (device) |
| --- | --- | --- | --- |
| native `impulse__capsule-button` 1x (collapsed) | **2.63** | 2.63 | — |
| native `impulse__capsule-button` 2x (collapsed) | **1.30** | 0.65 | 13.1 |
| native `impulse__rrect-md` 1x (uncollapsed) | **2.87** | 2.87 | 28.9 |
| native `impulse__rrect-md` 2x (uncollapsed) | **1.40** | 0.70 | 11.1 |
| landed `impulse__rrect-md` 1x | **1.68** | 1.68 | 17.9 |
| landed `impulse__rrect-md` 2x | **4.86** | 2.43 | 9.2 |

Three findings recorded beside (`g1/g1-findings.md:166–185`): the reference's collapsed material
transmits through the **same** kernel as its uncollapsed one; that kernel is invariant in **neither**
CSS nor device px (2.63 → 1.30 device, a factor 2 in device px and 4 in CSS px) while **vitrea's runs
the other way** (1.68 → 4.86); the 2x/1x peak ratio 3.85 is the dot's own geometry.

Resulting dot width (`tech-debt-tracker.md:995–1006`; W24 spec `:225–227`; claims §5.111 `:14411`):

| cell | scale | reference FWHM | vitrea FWHM |
| --- | --- | --- | --- |
| `impulse__capsule-button` | 1x | **7.57 CSS px** | **4.99** (clause 2's ±2 missed by 0.58) |
| `impulse__capsule-button` | 2x | **3.80** | **4.64** (met) |

Peak met at both scales: +0.0067 / +0.0256 against +0.0066 / +0.0254 (claims §5.108 §2).
`collapseTransmission` 0.017 (1x) / `collapseTransmission2x` 0.070 — a factor of four, needed
**because** the widths disagree (W24 Decision Log 2 (d), `:303–310`).

### 2c. The along-side rim variation on thick panels — the thickness term

`2026-09-09-w24-lit-edge.md:297–300` (Decision Log 3 (c)) and `:433–434` (Surprises); claims §5.108
§1 (`c9a-fidelity-claims.md:14225–14229`):

> 2x dark `dark-solid__rrect-md`, **top edge 0.0442 → 0.0158**, silhouette straight to **0.06 px**,
> interior uniform; **flat on the capsule and `rrect-sm`, graded on `rrect-md` and `rrect-lg`** — a
> thickness term, deferred.

No vitrea counter-number: vitrea's rim is constant along a straight side by construction (the lit
edge factor `pow(|dot(n,axis)|·√2, p)` is exactly 1 on every straight side, claims §5.108 §1).
Angular table for the same cell, `c9a-fidelity-claims.md:14126–14131`: 2x dark `dark-solid__rrect-md`
by segment native `0.033 0.006 0.032 0.042 0.033 0.006 0.032 0.041` against landed
`0.037 0.028 0.036 0.030 0.036 0.028 0.036 0.030`.

### 2d. Body levels

| cell | scheme/scale | reference | vitrea | where |
| --- | --- | --- | --- | --- |
| `dark-solid__rrect-md` (thick) | dark, both scales | **0.01527** | **0.01299** = **−2.93 codes** | claims §5.100 §7 (`:13744`); W23 `:127`, `:336–338`, `:456–458` |
| collapsed body, `impulse__capsule-button` | both schemes, 1x/2x | — | **−0.0029 / −0.0033 linear** below | tracker `:1001–1006`; W24 `:225–227` |
| `checkerboard__capsule-button` (thin, for contrast) | dark | — | **−16.05 codes** | claims §5.100 §7; tracker `:864–872` |
| `photo__capsule-button` (thin) | dark | — | **−19.05 codes** | same |

Recorded ruling: no scalar separates the thick cell from `mid-dark-solid__capsule-button` at 0.02 of
a code; `adaptiveTintDark` is named as the constant a body wave would fit (W23 `:456–458`).

### 2e. The nested pane's shape floors (the "seven")

All on `checkerboard__glass-over-glass__rest`, from
`packages/calibration/test/adopted-thresholds.test.ts`:

| line | tier | scheme/scale | metric | measured | floor |
| --- | --- | --- | --- | --- | --- |
| 715 | dom | 1x dark | `silhouetteIoU` | 0.90804 | 0.9070 |
| 716 | dom | 1x dark | `contourDistanceMean` | 0.96579 (moved 1.03304) | 1.0658 |
| 717 | dom | 1x dark | `contourDistanceP95` | 8.25 | 8.35 |
| 718 | texture | 2x dark | `silhouetteIoU` | 0.92673 | 0.9257 |
| 719 | dom | 2x dark | `silhouetteIoU` | 0.90482 | 0.9038 |
| 720 | dom | 2x dark | `contourDistanceMean` | 1.76018 | 1.8602 |
| 721 | dom | 2x dark | `contourDistanceP95` | 13.0 | 13.1 |

Cause: `tech-debt-tracker.md:650–663` — the luminance-delta extractor perforates a silhouette that
agrees with its backdrop over a checkerboard; 34 interior holes at 2x dom (texture 40; light bed
none), while W20's conformance row reads `declaredIoUWeb` 0.99919 with a one-pixel contour. W23's
three 1x pins: 13 holes, `declaredIoUWeb` 0.99886. W24 re-pinned two of them under a 0.00005-linear
level move (`tech-debt-tracker.md:1049–1063`) — the user's to undo.

### 2f. The CSS tier's large spans (recorded residual, not chartered under Decision Log 23 (a))

`docs/doperpowers/specs/2026-09-04-w16-css-two-layer-body.md:158–193`, dom tier, light standard,
checkerboard — interior standard deviation web / native:

| cell | span | set | 1x ssim (floor) | 1x std web/native | 2x ssim (floor) | 2x std web/native |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 96 | calib | 0.8963 (0.8952) | 0.0767 / 0.1131 | 0.9174 (0.9159) | 0.0771 / 0.1272 |
| `rrect-ml` | 128 | calib | 0.8515 (0.847) | 0.0591 / 0.0865 | 0.8808 (0.8754) | 0.0593 / 0.1018 |
| `toolbar-group` | 44×3 | calib | 0.9584 (≥0.90) | 0.1332 / 0.1481 | 0.9656 (≥0.92) | 0.1321 / 0.1581 |
| `glass-over-glass` | 130/56 | holdout | 0.8516 (0.8489) | 0.1279 / 0.1321 | 0.8709 (0.8677) | 0.1267 / 0.1401 |
| `rrect-lg` | 160 | holdout | 0.8448 (0.8361) | 0.0375 / 0.0650 | 0.8760 (0.8686) | 0.0377 / 0.0810 |

"The tier's interior spread is **32–54 % under the reference on the four large spans at 1x and
39–63 % at 2x**" (W16 `:178–190`). The cost is the **space**: claims `:10084` — the CSS tier's
forward-model residual is "2.4–2.8× on the thick spans, and no σ, share or mask can move it";
`backdrop-filter: url(#f)` with linearRGB reads 1.17×/1.10×/1.50×/1.41×/1.20× of the GPU law at
dpr 1 and 0.99×/1.01×/0.97×/0.99×/1.03× at dpr 2 (claims `:10086–10090`).
W14's separate thick-span finding, since fixed: claims `:9137–9145`.

### 2g. Other thick-surface rows on record

- **Outer-shadow lift**: encoded lift `0.0000 at spans 32 and 44, 0.0290 at 96, 0.0439 at 128,
  0.0448 at 130 (glass-over-glass), 0.0479 at 160`; 2x `0.0000/0.0000/0.0292/0.0445/0.0454/0.0487`;
  vitrea read 0.0000 everywhere before W14. Above/below ratio **0.41 on every thick span**
  (claims `:8859–8872`).
- **Resting sweep (fixed at W22)**: on the dark bed the whole of W21 clause 4's miss was
  `dark-solid__rrect-md` +0.1394 at 1x, +0.2445 at 2x on the left side (`tracker:678–701`).
- **CSS dark over structure**: `checkerboard__rrect-md` ΔE 0.0213 → 0.0416; CSS body 0.0122 against
  the reference's 0.0468 and the GPU tier's 0.0475 (`tracker:703–718`).
- **Lit arcs move two thick 2x light calibration cells out of the shape gate** on the topology arm:
  `checkerboard__rrect-md` bodiesWeb 1 → 2, `checkerboard__toolbar-group` 3 → 4; every shape row
  still inside its bound (`tracker:1083–1096`; `adopted-thresholds.test.ts:1276–1287`).

---

## 3. The current mechanism

**One curve.** `sizeThickness(span) = smoothstep(sizeSpanMin, sizeSpanMax, span)` —
`packages/renderer-webgpu/src/material.ts:2863–2869`, doc at `:530–561`. Exactly 0 at or below
`sizeSpanMin` (32) and exactly 1 at or above `sizeSpanMax` (96). Gains on it: the lens depth
(`lensSizeGainMax` 2.6, now the **inner shadow's** depth only — the lens reads its own span law since
W12 G2, `:567–576`), `sizeOcclusionGain`, `sizeShadowGainMax`.

**The size law's argument is the SHORT SIDE of the surface, in CSS px.**
`packages/renderer-webgpu/src/instances.ts:204`:
`const spanPx = Math.min(shape.channels.size[0], shape.channels.size[1]);`
Not a thickness, not an area, not the long side. So `rrect-md` 160×96 has span **96** — exactly
`sizeSpanMax`, where the curve saturates — and `rrect-ml` (128), `rrect-lg` (160),
`glass-over-glass` base (130) all read `sizeThickness` = **1**, identical. `toolbar-group`'s members
are 44×44, so span 44 — the toolbar is *not* a thick surface to the size law at all, only to the
sampling group. This saturation is a recorded defect of the form:
`2026-09-03-w13-body-depth-ramp.md:601` and `:792` — "`sizeThickness` saturates at 96, so every thick
span…"; `material.ts:847–858` records the same and is why the scatter ramp's start grew a **third**
anchor (`far`) declining on `smoothstep(sizeSpanMax, sizeScatterSpanMax, span)`.

**How it reaches the shader.** `instances.ts:380` writes `data[o + 16] = s.spanPx` — the per-pixel
slot carries the **span**, not the factor, and the fragment stage evaluates both curves from it
(`instances.ts:92–102`, `wgsl/optics.ts:27–39`, `wgsl/highlight.ts:142–149`). Band constants
(`sizeSpanMin`/`Max` in `scatter.zw`, the scatter floor, the ramp's thin/thick/far starts, the heavy
gains) and the accessibility fold arrive as **group uniforms** (`wgsl/optics.ts:97–190`). Occlusion
and inner shadow are multiplied by `sizeK` so both are inert at `sizeK = 0`; scattering is applied
by `kScatter`, per pixel.

**The scattering rides its own law, not `sizeThickness`.**
`sizeScatterSigma(sigma, span, profile, dpr, extents)` → `sizeScatterSigmaAt(sigma, scatter, …)`
returns `sigmaPx · (1 + (gain − 1)·mix)` (`material.ts:3119–3132`, `:3574–3588`). One function for
both tiers: `platform-web` mirrors it to write `blur()`, the GPU tier lerps its body sample toward
the chain level whose blur is that σ (`material.ts:594–598`, `:3100–3118`). The ramp's start
`s₀(span, dpr) = thin + (thick − thin)·sizeThickness(span) + (far − thick)·smoothstep(sizeSpanMax,
sizeScatterSpanMax(dpr), span)` — `material.ts:3140–3188`.

**Per-scale constants already** (interpolated by `rampAtScale`, held outside [1,2]):
`sizeScatterGainMax2x`, `sizeScatterFloor2x`, `sizeScatterSpanMax2x`, `sizeScatterGainFar2x`,
the three ramp starts ×2, `sizeScatterRampReach{1x,2x}Px`, plus (outside the size law)
`rimWidth2x` and `collapseTransmission2x`.

**Landed values** (`packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json`, `.patch`):

```
blurSigma 1.25 (regular) / 4 (clear)      sizeSpanMin 32   sizeSpanMax 96
sizeScatterGainMax 8    sizeScatterFloor 0.4    sizeScatterSpanMax 256
sizeScatterGainMax2x 4.8  sizeScatterFloor2x 1  sizeScatterSpanMax2x 256  sizeScatterGainFar2x 9.9
sizeScatterRampStartThin1x 0.72  Thick1x 0.52  Far1x 0.2
sizeScatterRampStartThin2x 0.46  Thick2x 0.21  Far2x 0.21
sizeScatterRampReach1xPx 80      Reach2xPx 100
sizeOcclusionGain 0.05  sizeShadowGainMax 1  lensSizeGainMax 2.6
lensRefractionGain 0.745  lensHeightPerSpan 0.25  lensHeightMax 20
lensAmountPerSpan 0.8  lensAmountMax 60  lensThicknessReference 8
lensExtentGain 1.337  lensProfileExponent 3.69
lensOvalization 0.8  lensOvalizationSpanMin 64  lensOvalizationSpanMax 72
backdropToneLow 0.02  backdropToneHigh 0.055  backdropToneMax 1  backdropToneSizeBias 0.05
collapseTransmission 0.017  collapseTransmission2x 0.07
outerShadow.thickOcclusionAt96 0.37 / At128 0.448 / At160 0.479
```

Note `sizeScatterFloor2x` = 1: at dpr 2 the deep sharp share is 0 and the ramp is the whole body
(`material.ts:882–885`) — i.e. **the deep-value span curve is inert at 2x**, and the only span
grading of the 2x kernel is `sizeScatterGainFar2x` 9.9 against `sizeScatterGainMax2x` 4.8, set from
W15 G0's independent per-span reading of **8 device px at span 96 and 11 at 160**
(`material.ts:1836–1839`).

**How a "thick span" is classified for the collapse.** Not by `sizeThickness`. The tone collapse
gates on the backdrop: `backdropToneSizeBias` **0.05** enters the response curve's **argument**, not
its amplitude — "a thicker surface behaves as though its backdrop were brighter"
(`material.ts:1099–1117`). Recorded evidence for it: over `dark-solid` the reference's 44 px capsule
adapts completely while its 96 px rrect keeps three quarters of its own appearance, on both scales
agreeing to three decimals. `scenes.json:50–68` states the argument as
`backdropLuminance + 0.09·sizeThickness(span)` with smoothstep edges 0.14 / 0.02.
W24 G1 read `k` = **1.0000** on every `impulse__capsule-button` cell and **0.0000** on the dark
`checkerboard` / `photo` capsules (toneX 0.219 / 0.155 against `backdropToneHigh` 0.055) — claims
§5.108 §2.

**Contradicting evidence on record:** `tech-debt-tracker.md:874–882` — in the dark reference's probe
grid `dark-solid__rrect-sm` (32) and `dark-solid__rrect-lg` (160) both draw the collapsed appearance
(body 0.0110, rim +0.0201 / +0.0196) while `dark-solid__rrect-md` (96) between them does **not**
(body 0.0153, rim +0.0256). "A size law that collapses the small and the large surface and not the
middle one is not a size law." Read by nothing; a native re-capture of the three at one sitting
would tell.

---

## 4. Which bed rows are thick surfaces, per set / scheme / scale

`apps/reference-apple/scenes.json` — split declared as scene-id arrays at `:376–473`
(calibration 20 `:444–466`, validation 6 `:435–443`, holdout 10 `:421–434`, recorded 4 `:467–472`).

| component | calibration | validation | holdout |
| --- | --- | --- | --- |
| `rrect-md` (96) | `light-solid`, `dark-solid`, `checkerboard`, `photo` | `impulse`; `photo…-tint-orange` | `hc-text` |
| `rrect-ml` (128) | `light-solid`, `checkerboard`, `photo` | — | — |
| `rrect-lg` (160) | — | — | `checkerboard`, `photo`, `photo…-tint-orange` |
| `toolbar-group` | `checkerboard` | `photo` | — |
| `glass-over-glass` (130/56) | — | — | `checkerboard`, `photo` |

Schemes/scales (`:241–373`): six profiles — 1x/2x light-standard (scenes `"all"`), 1x/2x
dark-standard (an explicit 14-scene list, identical at both scales, the **only** profiles carrying
`glass-over-glass`), 1x light reduced-transparency (9) and 1x light increased-contrast (10) — the
two a11y profiles carry `photo__toolbar-group` and `photo__rrect-lg` but **no `rrect-ml`, no
`rrect-sm`, no `glass-over-glass`**. There are no dark a11y profiles.

This is exactly what Decision Log 23 (c)'s "bed amendment that puts large spans into calibration"
addresses: `rrect-lg` and `glass-over-glass` — the two largest and the only stacked case — are
**wholly holdout**, so every thick constant to date was fitted on `rrect-md`/`rrect-ml` and read out
on the others once per frozen configuration.

**Thick rows currently excluded by `PREDICATE_EXCLUDES`** (31 entries,
`packages/calibration/test/adopted-thresholds.test.ts:1292–1324`; shape rows only, perceptual rows
still gate) — 11 of 31 are thick, all `rrect-md` or `toolbar-group`:

| line | tier | set | scene | scheme/scale |
| --- | --- | --- | --- | --- |
| 1294 | dom | calibration | `checkerboard__rrect-md` | 1x dark |
| 1295 | dom | calibration | `checkerboard__rrect-md` | 1x light inc-contrast |
| 1296 | dom | calibration | `checkerboard__rrect-md` | 2x dark |
| 1305 | texture | calibration | `checkerboard__rrect-md` | 1x light inc-contrast |
| 1306 | texture | calibration | `checkerboard__rrect-md` | 2x dark |
| 1307 | texture | calibration | `checkerboard__rrect-md` | 2x light |
| 1308 | texture | calibration | `checkerboard__toolbar-group` | 2x light |
| 1313 | texture | calibration | `dark-solid__rrect-md` | 1x dark |
| 1314 | texture | calibration | `dark-solid__rrect-md` | 2x dark |
| 1317 | texture | holdout | `hc-text__rrect-md` | 2x light |

(Plus `dom / calibration / checkerboard__rrect-md / 1x-light-increased-contrast` at 1295.)
**No `rrect-ml`, `rrect-lg` or `glass-over-glass` row is excluded** — all were admitted (W22 at
`:1215–1222`, W23 G2 at `:1240–1243`). `NO_SHAPE_AXIS_SCENES` additionally carries
`dark-solid__rrect-md__rest` on the dom tier of both dark profiles (`:1024`, `:1028`).

**Floors.** `UNMET_ROWS = 14` (`:748`) and **every one of the 14 is a thick surface, all over
`checkerboard`**: 1× `rrect-md` (dom 2x light `ssimMean` 0.91521 / 0.9142, `:547`), 2× `rrect-ml`
(dom 1x/2x light `ssimMean` 0.87585 / 0.8748 and 0.87893 / 0.8779, `:555–556`), 2× `rrect-lg`
(dom 1x/2x light 0.87039 / 0.8693 and 0.87220 / 0.8712, `:559–560`), 9× `glass-over-glass`
(2 light `ssimMean` `:557–558`, plus the seven dark shape floors of §2e).
`UNMET_ROWS` history `:724–748`: 33 → … → 7 (W16) → 11 (W21 G2c) → **14 (W23 G2)**.

---

## 5. The instruments that exist

| instrument | what it measures | recorded output |
| --- | --- | --- |
| `packages/calibration/results/2026-09-09-w24-lit-edge/g1/psf.py` | The kernel the dot arrives through. The background dot is a 4 CSS px box; fits box⊗(sharp + heavy Gaussian) + offset in **device** px along a horizontal profile at CSS (160, 104), half-window 20·scale, body at \|offset\| ≥ 14 CSS px. **Bounds are load-bearing** — sharp σ ∈ [0.05·s, 4·s], heavy σ ∈ [4·s, 30·s], offset ±0.01; without them an unbounded pair fits any profile as a large positive and a large negative Gaussian of the same width, and did so on the 1x rows. Runner `run-psf.sh`, 8 cells, light-standard only | `g1/transmission-read.txt` §3; table at `g1/g1-findings.md:157–164` (reproduced in §2b) |
| `.../g1/read-impulse.py` | The dot's peak excess over the body, FWHM and integral per CSS px through the surface; a dot on the bare background reads 1.0000 / 4.00 / 4.000 exactly. `psf.py` and `read-structure.py` both import it | `g1/transmission-read.txt`; claims §5.107 table |
| `.../g1/read-structure.py` | Two readings under the declared shape eroded 6 CSS px: **body** (mean linear luma, native vs web, converted to 8-bit codes) and **passthrough** = body sd / backdrop sd — "the fraction of the structure on offer that the material let through". Separates level from structure; a collapsed material reads passthrough 0 however right its level | `g1/transmission-read.txt`; `g1/g1-findings.md:81` |
| `.../g1/solve-state.py`, `fit-transmission.py`, `ladder.sh` | The published group state (`k`, `toneAdapt`, authority) read off the renderer; the transmission constants fitted on the ladder | `g1/solve-state.txt`, `g1/ladder.txt` |
| `.../g0/read-angular.py` (parent's `finding/angular-read.py`) | Peak excess over the body along the inward normal at ≥ 720 boundary points, binned into 16 × 22.5°. The instrument that made the along-side thickness term visible | `g0/angular-read.txt`, `g0/tables.txt`, `g0/fit-law.txt`, `g0/along-span.txt` |
| `packages/calibration/results/2026-09-08-w22-resting-sweep/g0/read-stack.py` | The nested pane per pane: base = base box eroded 6 CSS px with the overlay's box dilated 6 px cut out; overlay = its box eroded 6 px; each with its own 3 px rim band per side. **`blurSigmaMatchPx`** (`:118–141`) = the Gaussian σ at which the raster background under the pane, blurred then affinely rescaled (gain + offset solved in closed form per σ), best fits the pane's body. Grid 0…4.0 by 0.1 then 4.0…16.0 by 0.25 — **ceiling 16.00**. Explicitly "NOT the matrix's `blurSigmaNative`, which is an edge-spread fit on a checker step" | `g0/stack.txt` (24 rows, both tiers, both scales, both schemes) |
| `.../g0/predict-overlay.py` | The response law evaluated term by term at the overlay's true backdrop | `g0/overlay-prediction.txt` |
| `.../g3/read-stack-web.py` | The same stack read on the web after the overlay fix | claims §5.96 §5 |

**Permanent (committed) instruments that measure a width**, for contrast with the wave-local ones:

- `packages/calibration/src/metrics/material.ts:102` `blurEdgeSpread` — the edge-spread function in
  linear light over a known step in the **backdrop**, alternating golden-section on centre and σ
  against a `normalCdf` model with a closed-form gain/offset per step. σ search `[0.05,
  sigmaCeiling]` with `sigmaCeiling = max(length/2, sigmaGuess·4)` (`:187–193`); reports `sigmaPx`,
  `edgeCentrePx`, `residualRms` (`:206–208`); throws on a flat region. `findStepEdgeRegion` (`:216`)
  refuses scenes with no single resolvable step — which is why `blur*` is absent on solids.
- `material.ts:652` `rimIntensity` — radial profile by distance transform: `peakLuminance`,
  `peakDistancePx`, `fwhmPx` (`:708`) and `fwhmResolved` (false ⇒ the FWHM is a lower bound).
- `src/metrics/shadow.ts:375–376` `falloffSigmaPx` / `falloffSigmaResidual` — the outer shadow's
  Gaussian falloff from the declared contour, four sides.
- `test/material.test.ts:30–85` recovers known σ (4, ≈5, Gaussian 3.46 vs an equivalent box) and
  asserts the throw on a solid region.

Earlier wave-local width fitters worth reusing rather than rewriting, all under `results/`:
`2026-09-03-w12-lens/g3/{g3_kernel,g3_depth}.py` (sharp σ and amplitude by 8 px depth band);
`2026-09-03-w13-ramp/g0/{g0_ramp,g0_smallspan,g0_impulse,g0_validate}.py` (sharp share per 4 px
depth window with σ_heavy swept in device px; the heavy width on small spans against the layer
tree's 5.33 device px floor; the W24 impulse instrument's ancestor; instrument validation against a
known k(u) before any reference read); `2026-09-04-w15-body-2x/g0/g0a_width.py` (scores the
reference's heavy σ at 2x — 9 vs 16 vs 11 device px); `2026-09-03-w14-shadow/g0/g0_blur.py`.

The probe grids are rendered by wave-local scripts only (`tech-debt-tracker.md:884–892`).

---

## 6. Open questions a charter would have to answer

1. **What is the composite's scope?** Decision Log 23 (c) named two things (a bed amendment + thick
   spans); five waves have since attached four more (the base pane's haze, the scatter kernel's
   width at both scales, the along-side thickness term, the collapsed body's level). Evidence: §1's
   table. A charter that takes all six is a large wave; one that takes the kernel alone may still
   move the haze, since both are the same scatter law.
2. **Is the size law's argument right?** It is `min(width, height)` (`instances.ts:204`) and it
   saturates at 96, so `rrect-md`, `rrect-ml`, `rrect-lg` and the nested base are one number to
   `sizeThickness`. Evidence for the defect: `2026-09-03-w13-body-depth-ramp.md:601`, `:792`;
   `material.ts:847–858` (the `far` anchor exists precisely to route around the saturation).
   Moving `sizeSpanMax` moves the lens, the occlusion, the inner shadow and W9's tone bias at once
   (`material.ts:662–664`).
3. **What unit is the reference's kernel in?** σ 2.63 device px at 1x and 1.30 at 2x — a factor of 2
   in device px and 4 in CSS px, invariant in neither; vitrea's runs 1.68 → 4.86, the opposite way
   (`g1/g1-findings.md:166–185`). Any refit must decide the unit before it decides the value.
4. **Is the haze even measured yet?** The two reads are different instruments with different signs
   at 1x (native 1.50 vs web 2.20). `blurSigmaMatchPx` 16.00 native is at the grid ceiling — a lower
   bound, not a value (`g0/read-stack.py:125–126`). `blurSigmaNative`'s web side carries residual
   1.81 (dom sibling 1.18), which `src/report.ts:391–397` defines as *not identifiable*. So the
   headline "4.84 against 0.69" is **one identified number and one unidentified one**, and a charter
   that opens on it should first say what instrument gives the reference's haze a value with a
   residual it trusts — `psf.py` on a dot, an edge-spread on a resolvable step, or a σ-match with a
   ceiling above 16.
5. **What keys the collapse?** `backdropToneSizeBias` 0.05 enters the curve's argument, and the dark
   probe grid collapses `rrect-sm` (32) and `rrect-lg` (160) but not `rrect-md` (96) between them
   (`tech-debt-tracker.md:874–882`). Either the fixture carries a state flip (claims §5.17
   bistability) or the reference keys on something other than span. Unread; a native re-capture of
   the three at one sitting settles it.
6. **Can the thick constants be identified at all on the current bed?** `rrect-lg` and
   `glass-over-glass` are wholly holdout (`scenes.json:421–434`); the light bed has two fittable
   solid cells and the dark bed one (`tech-debt-tracker.md:884–892`); the collapsed body's constant
   is fittable only on `impulse__capsule-button`, whose independence W24 already spent
   (W24 Decision Log 2 (e)). Decision Log 23 (c)'s bed amendment is therefore a **precondition**,
   not a nicety — and it interacts with the probe-grid-as-harness-set item.
7. **What happens to the fourteen floors?** All fourteen are thick-surface rows and the seven
   nested-pane ones are an **extractor** artefact, not a material miss (the same tier reads
   `declaredIoUWeb` 0.99919 with a one-pixel contour, `tech-debt-tracker.md:650–663`). A material
   change here will move them; whether the wave also fixes the extractor is a scope call. Two W23
   first-reading floors were already re-pinned at W24 under the standing instruction and are the
   user's to undo (`tech-debt-tracker.md:1049–1063`).
8. **Where does the CSS tier stop?** Its interior spread is 32–63 % under the reference on the four
   large spans (W16 `:178–190`) and the residual is the encoded space, 2.4–2.8× on the thick spans,
   which no σ, share or mask moves (claims `:10084`). Under Decision Log 23 (a) that is recorded,
   not chartered — but a wider GPU kernel will widen the gap the coherence pin measures
   (`crossTierOklabDeltaEMean ≤ 0.05`, `adopted-thresholds.test.ts:221–224`; the dom checkerboard
   cells already read 0.023 / 0.037 / 0.043 / 0.035 at 1x).
9. **Does the along-side variation belong to this wave?** It is graded on `rrect-md` and `rrect-lg`
   and flat on the capsule and `rrect-sm` (W24 `:297–300`) — by shape, a thickness term. But it is a
   **rim** quantity, and every rim law to date was fitted per side or per bin; a new reader may be
   the precondition. No vitrea number exists for it.
10. **What does the eye say?** The user's eye named the base pane's haze twice ("Apple's bottom glass
    is very slightly less transparent", claims §5.99 §1; W23 `:332–333`) and it is the only item of
    the composite the eye has independently confirmed. CLAUDE.md's rule stands: put the capture next
    to the native fixture and look, because SSIM scores well on a blurred interior.
