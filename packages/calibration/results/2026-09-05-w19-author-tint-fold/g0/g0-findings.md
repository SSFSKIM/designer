# W19 G0 — the author-tint fold, measured on both tiers and verified in the closed form (spike findings)

The charter (`docs/doperpowers/specs/2026-09-05-w19-author-tint-fold.md`) opens this wave on a defect
the W18 post-landing review found by hand: on Chromium's linear path the sharp layer's transfer table
is solved for the overlay at the contrast floor, and L3 paints the author's layer at the author's own
strength, so a tinted surface below full strength composites off the material by
`(1 − s)·α₃/(1 − α₃)` of the material-to-tint gap. This spike measures that, on the code and on
pixels, and verifies the fold the charter's Design proposes.

**The charter's mechanism is confirmed and it is not the whole of the defect. A second term is
larger, and the charter does not name it: the transfer table SATURATES.** `cssTierTintTable` clamps
its samples into [0, 1] because an `feComponentTransfer type="table"` cannot carry a value outside
that range, and today the table is solved against the FOLDED tint colour — which on an orange seed is
near zero in blue and on a blue seed near zero in red. The remainder
`(E(M) − α₃·E(T_folded))/(1 − α₃)` then exceeds 1 on that channel over most of the ladder, and the
clamp swallows the excess. On the captured cells **0.1 % to 14.2 % of the masked channel samples are
in the clamp** at 1x, rising with strength; analytically the clamp costs up to **0.083 of encoded
value** on the seed's darkest channel. It matters beyond bookkeeping for two reasons: the clamp makes
the table non-affine, so its loss does NOT pass through L2's Gaussian unchanged the way W17's
derivation requires, and it is a HUE error rather than a level error, which an interior-mean metric
under-reports. **The fold removes it: under the fold the table is solved on the untinted `T` and the
clamp share is 0.000 on every cell of the ladder at both scales.**

Everything else the charter predicted holds. The composite error's closed form is exact wherever the
table does not saturate (worst residual 8.3e−8 encoded on the 133 of 180 unsaturated channel cells).
The fold is exact: `(1 − α″)·F + α″·C″ = (1 − s)·E(M) + s·E(L)` to **8.9e−8 encoded / 1.6e−7 in
linear luminance** at every strength, backdrop and seed. `α″ ≥ α₃` everywhere with the least margin
**+0.0733** at `s = 0.1`. At `s = 1` the L3 declaration is byte-identical to today's on all ten
sweep cells. **No cell of the captured ladder changes form** — `cssTint` reads `linear` on 20 of 20
scenes at 1x, 20 of 20 at 2x and 4 of 4 under each fold profile — which is what the boundary being
read at the material's composite level predicts.

Every web-side reading below is a capture taken on this machine's `apple / metal-3` adapter through
Playwright's full Chromium binary at the scene's pixel size, into scratch capture roots under
`/Users/new/.claude/jobs/5c70e47f/tmp/w19/g0/`. Nothing canonical was written. The native ladder is
§5: the grant is live, twelve cells at 1x, seven attested runs, the three recorded twins
byte-identical to the canonical fixtures.

## 0. The instrument

**The closed form (a, d).** `closed-form.ts` over `surface.ts`. `surface.ts` is `root.ts`'s chain from
the profile to one surface's declarations — `sizeThickness`, `sizeThicknessUnderPolicy`,
`occlusionAlphaUnderPolicy`, `sizeOcclusionAlphaAt`, `backdropToneAdaptation`,
`toneRespondedSourceOptics`, `adaptedSourceOptics`, `interiorShadowKeep`,
`innerShadowedSourceOptics`, `interiorBandLight`, `cssOpticsFromSource`, `authorTintLayer`,
`tintedCssOptics` — every step the shipped function in the shipped order, with one literal
(`DEFAULT_HOST_SHAPE.thickness` = 8 CSS px, which the calibration pages never override). It is one
module because two scripts need it and a second copy of a fourteen-step chain is a second set of
numbers to drift. `closed-form.ts` then calls `cssTierDeclarations` itself and composes the
declarations it gets back, so what is evaluated is the tier's own output rather than a restatement of
it. The surface is the bed's `capsule-button` read from the scenes file it is given.

**The bed (b).** `make-scenes.mjs` derives a twenty-scene scratch bed from
`apps/reference-apple/scenes.json`: the canonical capsule over `photo` and `checkerboard`, untinted
and at nine tint ids — `orange-010`, `orange-020`, `orange-035`, `orange-half`, `orange-075`,
`orange`, `blue-020`, `blue-050`, `blue`. Six registry entries are new; three and the two untinted
controls are the canonical bed's own, at the canonical ids, so those cells still carry native
fixtures and the ladder's reader can put the native silhouette beside the declared region on them.
`run-ladder.sh` drove eight `capture-web` runs, one at a time on the shared adapter, GPU tier first:
the standard light profile on both tiers at 1x and 2x (20 scenes each), and the two fold profiles at
1x on both tiers over the photo (4 scenes each: untinted, `orange-020`, `orange-half`, `orange`).
Every run exit 0, every scene byte-identical over two independent page loads, 0 fell back to the CSS
tier, 0 carried problems. `compare` is deliberately not the driver, for W18 G0's reason: fifteen of
the twenty scenes have no native fixture and the quantity under test needs no reference.

**The masks, both stated.** Where the canonical bed has a fixture for the scene id AND declares the
same geometry, the reading is under the **native silhouette**, the mask every Grounding Baseline
number is under. Everywhere else it is under the **declared component region**, rasterised by
pixel-centre containment at margin 0 — the same region that bounds the native extractor's own
search. On the 1x controls the two masks are the same 4 872 pixels and give the same mean to 0.0e+00;
at 2x they differ by 7 pixels of 19 468 and by 0.00002 of the mean.

**The prediction (b).** `predict.ts` carries the closed form onto the captured cells with no second
model of the body: on the linear form the untinted surface's table and its floor overlay composite
back to `E(M)` exactly — that identity is what W17 G1 solved the table for — so **the untinted CSS
capture IS the tier's own `E(M)` per pixel**, with its own body, kernel, mask and two-layer mix
already inside it. Only `α₃`, `T`, `T_folded` and `(L, s)` come from the profile. §4 reads what that
prediction is worth.

## 1. (a) — the four quantities, in code terms

All per channel; `E` is `srgbEncode`, `D` is `srgbDecode`, `b` the filtered backdrop in linear light
that the sharp layer's reference filter sees.

| symbol | in code |
| --- | --- |
| `M` | the renderer's interior composite, `(1 − α)·b + α·tint + X` in linear light, where `(α, tint, X)` is the `CssTierInterior` `root.ts` builds — `innerShadowedSourceOptics(adaptedSourceOptics(toneRespondedSourceOptics(occluded, …), …), interiorShadowKeep(…))` for the pair and `interiorBandLight` for `X`. `cssTierTintTransfer` carries exactly this triple, clamped into [0, 1] as `cssTierTintTable` clamps it. |
| `T` | the UNTINTED conversion's overlay colour: `cssOpticsFromSource(baseOptics, shadowedSource, mapping).tint / 255`, already encoded (`cssTintColor` writes an encoded `Rgb255`). |
| `T_folded` | `tintedCssOptics(cssOpticsFromSource(...), …).tint / 255` — **what the tier uses today**, because `root.ts` (~1918) passes the folded optics to `cssTierDeclarations` as `optics` and the declarations take `floorEncoded` from `optics.tint`. |
| `L`, `s` | `authorTintLayer(policySource, seed, tintBackdrop, tintGrip).color / 255` and `.strength` — the seed at the shade the material's luminance puts it at, encoded. |
| `α₃` | `cssTierFloorAlpha(optics)` = `CSS_TIER_TINT_FLOOR_ALPHA` = **0.2668228970218852**. |

Today's chain, and the renderer's expression beside it:

```
F(b)      = D( clamp01( (E(M) − α₃·E(T_folded)) / (1 − α₃) ) )    the table, inside the sharp filter
composite = D( (1 − s)·E(F(b)) + s·E(L) )                          L3's rgba(L, s) over it
intended  = D( (1 − s)·E(M) + s·E(L) )                             tintedMaterialColour's expression
```

Subtracting in encoded space, where the residue is exact:

```
E(composite) − E(intended) = (1 − s)·α₃/(1 − α₃)·(E(M) − E(T_folded))        [unsaturated]
```

## 2. (a) — the sweep

`closed-form.ts` on the shipped light profile, the canonical 120 × 44 capsule, over a UNIFORM grey
backdrop at each level (where the group's sampled tone and the filtered backdrop are one number; the
captured ladder in §3 is where the two part company). The interior `root.ts` resolves:

| `b` | `interior.tintAlpha` | `interior.tint` | `X` | composite level | form |
| --- | --- | --- | --- | --- | --- |
| 0.15 | 0.5463 | 0.9944 | 0.00928 | 0.6206 | linear |
| 0.30 | 0.6203 | 0.9951 | 0.00928 | 0.7404 | linear |
| 0.45 | 0.6514 | 0.9953 | 0.00928 | 0.8145 | linear |
| 0.60 | 0.6681 | 0.9955 | 0.00928 | 0.8735 | linear |
| 0.80 | 0.6927 | 0.9956 | 0.00928 | 0.9448 | linear |

**Today minus the intended expression, in linear luminance** (orange seed above, blue below; the
closed form's own value in parentheses):

| `s` \ `b` | 0.15 | 0.30 | 0.45 | 0.60 | 0.80 |
| --- | --- | --- | --- | --- | --- |
| 0.10 | **−0.0697** (−0.0433) | −0.0423 (−0.0233) | −0.0233 (−0.0119) | −0.0056 (−0.0026) | +0.0123 (+0.0066) |
| 0.20 | −0.0379 (−0.0232) | −0.0141 (−0.0071) | +0.0031 (+0.0026) | +0.0165 (+0.0099) | +0.0272 (+0.0181) |
| 0.35 | −0.0072 (−0.0021) | +0.0123 (+0.0100) | +0.0236 (+0.0171) | **+0.0328** (+0.0229) | +0.0201 (+0.0290) |
| 0.50 | +0.0082 (+0.0101) | +0.0213 (+0.0187) | +0.0293 (+0.0240) | +0.0318 (+0.0285) | +0.0136 (+0.0330) |
| 0.75 | +0.0107 (+0.0134) | +0.0170 (+0.0180) | +0.0187 (+0.0203) | +0.0128 (+0.0222) | +0.0055 (+0.0245) |
| 1.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

| `s` \ `b` (blue) | 0.15 | 0.30 | 0.45 | 0.60 | 0.80 |
| --- | --- | --- | --- | --- | --- |
| 0.10 | **−0.0555** (−0.0352) | −0.0289 (−0.0161) | −0.0098 (−0.0050) | +0.0076 (+0.0041) | +0.0246 (+0.0136) |
| 0.20 | −0.0178 (−0.0108) | +0.0064 (+0.0049) | +0.0242 (+0.0147) | +0.0374 (+0.0219) | +0.0336 (+0.0303) |
| 0.35 | +0.0153 (+0.0141) | +0.0362 (+0.0268) | +0.0452 (+0.0338) | **+0.0498** (+0.0397) | +0.0238 (+0.0459) |
| 0.50 | +0.0279 (+0.0275) | +0.0393 (+0.0362) | +0.0445 (+0.0421) | +0.0361 (+0.0460) | +0.0157 (+0.0506) |
| 0.75 | +0.0190 (+0.0258) | +0.0229 (+0.0301) | +0.0197 (+0.0328) | +0.0135 (+0.0348) | +0.0058 (+0.0371) |
| 1.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

Three readings out of this table:

1. **The error is not one-signed.** It crosses zero along a curve running from about
   `(s = 0.35, b = 0.21)` to about `(s = 0.1, b = 0.65)` on the orange seed; the bed's one sub-unit cell (`orange-half` over the photo) sits close
   to that crossing, which is exactly why it reads −0.0008 against the GPU tier and why eleven of
   twelve tinted cells said nothing. The worst readings on this sweep are **−0.070 at `s = 0.1`,
   `b = 0.15`** and **+0.050 at `s = 0.35`, `b = 0.6`** (blue).
2. **The review's numbers reproduce in shape and differ in size, for a stated reason.** The review's
   scratch test held the interior at a literal `(0.62, 0.78, 0.004)` at every backdrop; `root.ts`
   resolves `α` from 0.546 to 0.693 and a near-white tint at 0.995. Same sign pattern, same
   crossings, larger magnitudes at low strength.
3. **The closed form is exact where the table does not saturate**, and only there — §2.1.

### 2.1 The saturation the charter does not name

`cssTierTintTable` clamps its samples into [0, 1]. On **47 of 180 channel cells** of this sweep the
argument `(E(M) − α₃·E(T_folded))/(1 − α₃)` exceeds 1 and the clamp fires; the closed form's residual
there runs to **−0.0831 encoded** (orange, `s = 0.5`, `b = 0.8`, blue channel) and is zero to
8.9e−8 on the other 133. The pattern is exactly the seed's darkest channel — channel 2 for orange
and channel 0 for blue — because `T_folded` on that channel is near zero and the divisor
`(1 − α₃)` = 0.7332 is less than one.

| seed | channel | cells in the clamp | worst residual (encoded) |
| --- | --- | --- | --- |
| orange | 2 (blue) | 13 of 30 | −0.0831 |
| orange | 1 (green) | 5 of 30 | −0.0253 |
| blue | 0 (red) | 13 of 30 | −0.0788 |
| blue | 1 (green) | 5 of 30 | −0.0317 |

**Why it is worse than a bias.** W17 G1's whole derivation rests on the transfer being an AFFINE in
linear light, which passes through L2's Gaussian unchanged and reaches the composite exactly once. A
clamped table is not affine, so the clamp fires per pixel BEFORE the heavy blur and before the mask
mixes the two bodies, and its loss is not recoverable from the composite. §4 measures the cost of
that on the captured cells. And because the clamp is per channel on the seed's darkest channel, its
signature is a hue shift toward the material's neutral, which an interior-mean-of-luminance metric
sees only as a fraction of.

**The fold removes it.** Under the fold the table is solved on the untinted `T`, which is near white
(0.995 linear), so the argument is `(E(M) − 0.2668·E(T))/0.7332` and stays inside [0, 1] except
within 0.4 % of white. Measured on the captured ladder: the clamp share is **0.000 on every one of
the 18 tinted cells at 1x and at 2x** (§4).

## 3. (b) — the captured ladder

Interior mean of linear luminance, whole component, under the **declared component region** (the
native silhouette agrees to 0.00002 on the five cells that have a fixture). `cssTint` was `linear` on
every CSS cell of every table below.

### dpr 1, standard light

| scene | tint `s` | GPU | CSS | CSS − GPU |
| --- | --- | --- | --- | --- |
| `photo__capsule-button__rest` | — | 0.6178 | 0.6189 | +0.0011 |
| `photo…-tint-orange-010` | 0.10 | 0.5807 | 0.5122 | **−0.0684** |
| `photo…-tint-orange-020` | 0.20 | 0.5463 | 0.5055 | **−0.0408** |
| `photo…-tint-orange-035` | 0.35 | 0.4996 | 0.4875 | −0.0121 |
| `photo…-tint-orange-half` | 0.50 | 0.4587 | 0.4579 | −0.0008 |
| `photo…-tint-orange-075` | 0.75 | 0.4025 | 0.4052 | +0.0027 |
| `photo…-tint-orange` | 1.00 | 0.3595 | 0.3594 | −0.0001 |
| `photo…-tint-blue-020` | 0.20 | 0.4947 | 0.4727 | **−0.0220** |
| `photo…-tint-blue-050` | 0.50 | 0.3503 | 0.3649 | **+0.0146** |
| `photo…-tint-blue` | 1.00 | 0.2029 | 0.2015 | −0.0014 |
| `checkerboard__capsule-button__rest` | — | 0.6783 | 0.6789 | +0.0006 |
| `checkerboard…-tint-orange-010` | 0.10 | 0.6347 | 0.6021 | **−0.0325** |
| `checkerboard…-tint-orange-020` | 0.20 | 0.5940 | 0.5824 | **−0.0117** |
| `checkerboard…-tint-orange-035` | 0.35 | 0.5386 | 0.5394 | +0.0008 |
| `checkerboard…-tint-orange-half` | 0.50 | 0.4900 | 0.4919 | +0.0020 |
| `checkerboard…-tint-orange-075` | 0.75 | 0.4232 | 0.4224 | −0.0008 |
| `checkerboard…-tint-orange` | 1.00 | 0.3719 | 0.3703 | −0.0016 |
| `checkerboard…-tint-blue-020` | 0.20 | 0.5393 | 0.5443 | +0.0050 |
| `checkerboard…-tint-blue-050` | 0.50 | 0.3765 | 0.3929 | **+0.0164** |
| `checkerboard…-tint-blue` | 1.00 | 0.2100 | 0.2083 | −0.0017 |

### dpr 2, standard light

| scene | tint `s` | GPU | CSS | CSS − GPU |
| --- | --- | --- | --- | --- |
| `photo__capsule-button__rest` | — | 0.6179 | 0.6198 | +0.0018 |
| `photo…-tint-orange-010` | 0.10 | 0.5808 | 0.5136 | **−0.0673** |
| `photo…-tint-orange-020` | 0.20 | 0.5464 | 0.5068 | **−0.0397** |
| `photo…-tint-orange-035` | 0.35 | 0.4998 | 0.4882 | −0.0116 |
| `photo…-tint-orange-half` | 0.50 | 0.4588 | 0.4584 | −0.0004 |
| `photo…-tint-orange-075` | 0.75 | 0.4025 | 0.4054 | +0.0029 |
| `photo…-tint-orange` | 1.00 | 0.3596 | 0.3595 | −0.0001 |
| `photo…-tint-blue-020` | 0.20 | 0.4949 | 0.4737 | **−0.0212** |
| `photo…-tint-blue-050` | 0.50 | 0.3505 | 0.3653 | **+0.0148** |
| `photo…-tint-blue` | 1.00 | 0.2032 | 0.2015 | −0.0016 |
| `checkerboard__capsule-button__rest` | — | 0.6847 | 0.6948 | +0.0101 |
| `checkerboard…-tint-orange-010` | 0.10 | 0.6403 | 0.6110 | **−0.0294** |
| `checkerboard…-tint-orange-020` | 0.20 | 0.5991 | 0.5861 | **−0.0130** |
| `checkerboard…-tint-orange-035` | 0.35 | 0.5430 | 0.5404 | −0.0026 |
| `checkerboard…-tint-orange-half` | 0.50 | 0.4935 | 0.4929 | −0.0006 |
| `checkerboard…-tint-orange-075` | 0.75 | 0.4256 | 0.4224 | −0.0032 |
| `checkerboard…-tint-orange` | 1.00 | 0.3735 | 0.3703 | −0.0031 |
| `checkerboard…-tint-blue-020` | 0.20 | 0.5445 | 0.5448 | +0.0003 |
| `checkerboard…-tint-blue-050` | 0.50 | 0.3794 | 0.3914 | **+0.0120** |
| `checkerboard…-tint-blue` | 1.00 | 0.2109 | 0.2083 | −0.0026 |

### The scratch bed reproduces the Grounding Baseline

The five cells this bed shares with the canonical one, against the charter's table (canonical
`results/matrix.json`):

| cell | scale | bed | this run | difference |
| --- | --- | --- | --- | --- |
| `photo__capsule-button__rest-tint-orange-half` | 1x | −0.0008 | −0.0008 | 0.0000 |
| | 2x | −0.0003 | −0.0004 | 0.0001 |
| `checkerboard__capsule-button__rest-tint-orange` | 1x | −0.0016 | −0.0016 | 0.0000 |
| | 2x | −0.0031 | −0.0031 | 0.0000 |

The scratch bed's numbers are the bed's numbers; the ladder's new rungs stand on the same ground.

### The fold profiles, dpr 1, over the photo

| profile | scene | `s` | GPU | CSS | CSS − GPU |
| --- | --- | --- | --- | --- | --- |
| reduced transparency | untinted | — | 0.8956 | 0.8886 | −0.0070 |
| | `orange-020` | 0.20 | 0.7662 | 0.7662 | −0.0000 |
| | `orange-half` | 0.50 | 0.6046 | 0.6183 | **+0.0137** |
| | `orange` | 1.00 | 0.4172 | 0.4174 | +0.0002 |
| increased contrast | untinted | — | 0.5950 | 0.6314 | **+0.0364** |
| | `orange-020` | 0.20 | 0.5448 | 0.5322 | **−0.0126** |
| | `orange-half` | 0.50 | 0.4843 | 0.5029 | **+0.0186** |
| | `orange` | 1.00 | 0.4212 | 0.4245 | +0.0032 |

Two things here are not this wave's. The **untinted** increased-contrast capsule over the photo reads
**+0.0364**, which is a whole-profile gap on an untinted surface and therefore nothing the author-tint
fold can move; the reduced-transparency untinted cell reads −0.0070. The tinted rows carry those
offsets plus the tint's own term, so on the fold profiles the charter's `within 0.01` clause is a
claim about a sum this wave owns only part of. §7 carries it as a `[parent-impact]`.

## 4. (b) — the closed form on the captured cells, and what it is worth

`predict.ts` predicts the tinted CSS capture from the tier's own untinted CSS capture and the four
resolved quantities, per pixel, and reads the same mask. `predToday` is today's chain, `predFold` the
candidate's, `share` = `predFold − predToday` (the movement G1's S5 will hold each cell to).

### dpr 1

| scene | `s` | measured CSS | `predToday` | residual | `predFold` | share | clamp share today / fold |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `photo…orange-010` | 0.10 | 0.5122 | 0.5147 | +0.0025 | 0.5811 | **+0.0664** | 0.001 / 0.000 |
| `photo…orange-020` | 0.20 | 0.5055 | 0.5102 | +0.0047 | 0.5456 | +0.0354 | 0.003 / 0.000 |
| `photo…orange-035` | 0.35 | 0.4875 | 0.4920 | +0.0045 | 0.4978 | +0.0058 | 0.011 / 0.000 |
| `photo…orange-half` | 0.50 | 0.4579 | 0.4647 | +0.0068 | 0.4573 | −0.0073 | 0.041 / 0.000 |
| `photo…orange-075` | 0.75 | 0.4052 | 0.4091 | +0.0040 | 0.3996 | −0.0095 | 0.097 / 0.000 |
| `photo…orange` | 1.00 | 0.3594 | 0.3555 | −0.0039 | 0.3555 | +0.0000 | 0.115 / 0.000 |
| `photo…blue-020` | 0.20 | 0.4727 | 0.4773 | +0.0046 | 0.4931 | +0.0158 | 0.009 / 0.000 |
| `photo…blue-050` | 0.50 | 0.3649 | 0.3716 | +0.0067 | 0.3473 | −0.0243 | 0.054 / 0.000 |
| `photo…blue` | 1.00 | 0.2015 | 0.1972 | −0.0043 | 0.1972 | +0.0000 | 0.107 / 0.000 |
| `checkerboard…orange-010` | 0.10 | 0.6021 | 0.6085 | +0.0064 | 0.6336 | +0.0251 | 0.001 / 0.000 |
| `checkerboard…orange-020` | 0.20 | 0.5824 | 0.5916 | +0.0092 | 0.5921 | +0.0005 | 0.030 / 0.000 |
| `checkerboard…orange-035` | 0.35 | 0.5394 | 0.5526 | +0.0133 | 0.5356 | −0.0171 | 0.051 / 0.000 |
| `checkerboard…orange-half` | 0.50 | 0.4919 | 0.5066 | **+0.0147** | 0.4870 | −0.0197 | 0.086 / 0.000 |
| `checkerboard…orange-075` | 0.75 | 0.4224 | 0.4302 | +0.0078 | 0.4186 | −0.0116 | 0.114 / 0.000 |
| `checkerboard…orange` | 1.00 | 0.3703 | 0.3664 | −0.0038 | 0.3664 | +0.0000 | 0.141 / 0.000 |
| `checkerboard…blue-020` | 0.20 | 0.5443 | 0.5571 | +0.0128 | 0.5376 | −0.0194 | 0.029 / 0.000 |
| `checkerboard…blue-050` | 0.50 | 0.3929 | 0.4070 | +0.0142 | 0.3734 | −0.0336 | 0.088 / 0.000 |
| `checkerboard…blue` | 1.00 | 0.2083 | 0.2040 | −0.0043 | 0.2040 | +0.0000 | 0.142 / 0.000 |

At 2x the same shape with a larger residual on the checkerboard: **+0.0023…+0.0064 on the photo**
and **+0.0102…+0.0250 on the checkerboard**, `−0.0039…−0.0043` at `s = 1` on both backgrounds.

**The residual is not noise and it is attributable, in two parts.**

1. **A constant −0.0038…−0.0043 at `s = 1`, on every cell and both scales.** At full strength L3 is
   opaque and the prediction is a flat colour, so this is precisely everything the model does not
   carry: the rim, the drawn border, the highlight and the outer shadow, painted outside the table,
   and the mask's antialiased contour. It is a property of the surface, not of the strength.
2. **A positive term that tracks the clamp share** (+0.0025 at 0.1 % clamped, +0.0147 at 8.6 %,
   falling again as `s → 1` where L3 covers the table's output). This is §2.1's mechanism: the
   prediction clamps on the composite, where the tier clamps per pixel before L2's Gaussian, so the
   two cannot agree on a cell whose backdrop has variance. The checkerboard (σ ≈ 0.14 against the
   photo's 0.04) is where it is largest, at 1x and more so at 2x.

**So the acceptance's "the closed form reproduces the measured error within 0.002 per cell" is NOT
met as written**, and it cannot be met by a form evaluated on a composite: the mechanism it would
have to model happens before a blur, inside a filter. What IS available to 0.002 is the fold's own
prediction, which does not clamp; §7 puts the choice to the parent.

## 5. (c) — the native ladder

**The Screen Recording grant is live; the ladder was captured.** `apps/reference-apple/scenes-w19-probe.json`
(written by `make-probe-scenes.mjs` from the canonical bed) through `VITREA_SCENES` into
`results/2026-09-05-w19-author-tint-fold/probe/` through `VITREA_FIXTURES`, 1x light standard only,
twelve cells: the canonical capsule over `photo` and `checkerboard` at strengths 0.1, 0.2, 0.35, 0.5,
0.75 and 1.0. The app was launched from the MAIN checkout's bundle, whose identity the grant is keyed
to. Nothing canonical was written.

**The runs, by W9's rule** (claims §5.30; `probe/provenance.json`):

| run | idle at start / end (s) | audit | kept |
| --- | --- | --- | --- |
| w19-probe-1 | 2 671 / **7** | 8/12 | **no** — HID activity during the run; four checkerboard cells not `presentedActive` |
| w19-probe-2 | 96 / 218 | 12/12 | yes |
| w19-probe-3 | 219 / 338 | 12/12 | yes |
| w19-probe-4 | 339 / 459 | 12/12 | yes |
| w19-probe-5 | 459 / 578 | 12/12 | yes |
| w19-probe-6 | 578 / 699 | 12/12 | yes |
| w19-probe-7 | 700 / 818 | 6/12 | **no** — six cells not `presentedActive` with the machine idle throughout: the session denied the window activation, not a user |
| w19-probe-8 | 819 / 938 | 12/12 | yes |
| w19-probe-9 | 970 / 1 089 | 12/12 | yes (the replacement) |
| w19-probe-10 | 1 089 / 1 209 | 12/12 | attested, not needed — seven runs were taken before it |

Ten runs taken, eight attested, seven materialised (`cli/materialize.ts --frequency-settle --apply`).
Nine cells unanimous over the seven; three frequency-settled at a 6/7 majority — `photo…orange-020`,
`photo…orange-035` and `photo…orange-075`, each a single minority state in one run. Provenance:
seven runs, 72.2 % confidence at a one-in-six minority.

**The controls.** The three cells this bed shares with the frozen one —
`photo__capsule-button__rest-tint-orange`, `photo…-tint-orange-half` and
`checkerboard__capsule-button__rest-tint-orange` — are **byte-identical to the canonical fixtures**
(sha256 equal, 0 px changed). The native capture path reproduces to the byte across the five days
since the frozen bed was taken.

### Apple's curve, and the renderer's law against it

Interior mean of linear luminance under the native silhouette, from `compare` on both web tiers
against this bed (scratch matrix; the captures under scratch). Standard light profile, 1x.

| cell | `s` | native | GPU | CSS | GPU − native | CSS − native | CSS − GPU |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `photo…orange-010` | 0.10 | 0.5511 | 0.5807 | 0.5122 | +0.0295 | **−0.0389** | −0.0684 |
| `photo…orange-020` | 0.20 | 0.5191 | 0.5463 | 0.5055 | +0.0272 | −0.0135 | −0.0408 |
| `photo…orange-035` | 0.35 | 0.4783 | 0.4996 | 0.4875 | +0.0214 | +0.0092 | −0.0121 |
| `photo…orange-half` | 0.50 | 0.4385 | 0.4587 | 0.4579 | +0.0201 | +0.0193 | −0.0008 |
| `photo…orange-075` | 0.75 | 0.3908 | 0.4025 | 0.4052 | +0.0116 | +0.0143 | +0.0027 |
| `photo…orange` | 1.00 | 0.3524 | 0.3595 | 0.3594 | +0.0071 | +0.0071 | −0.0001 |
| `checkerboard…orange-010` | 0.10 | 0.5852 | 0.6347 | 0.6021 | +0.0495 | +0.0170 | −0.0325 |
| `checkerboard…orange-020` | 0.20 | 0.5481 | 0.5940 | 0.5824 | +0.0459 | +0.0343 | −0.0117 |
| `checkerboard…orange-035` | 0.35 | 0.5020 | 0.5386 | 0.5394 | +0.0366 | +0.0374 | +0.0008 |
| `checkerboard…orange-half` | 0.50 | 0.4578 | 0.4900 | 0.4919 | +0.0322 | +0.0341 | +0.0020 |
| `checkerboard…orange-075` | 0.75 | 0.4040 | 0.4232 | 0.4224 | +0.0193 | +0.0185 | −0.0008 |
| `checkerboard…orange` | 1.00 | 0.3603 | 0.3719 | 0.3703 | +0.0116 | +0.0100 | −0.0016 |

**Does the encoded-space mix fit Apple's curve? Yes, to 0.003.** `native-ladder.ts` tests the
INTERPOLATION alone and assumes nothing about Apple's own shade: the two endpoints are Apple's own
captures — the untinted capsule from the canonical bed and the full-strength tinted capsule from this
probe — and the hypothesis is `D((1 − s)·E(untinted) + s·E(s = 1))`, per pixel and per channel. The
linear-light mix is computed beside it as the alternative that would be refuted.

| cell | `s` | native | encoded mix | residual | linear mix | residual |
| --- | --- | --- | --- | --- | --- | --- |
| `photo…orange-010` | 0.10 | 0.5511 | 0.5499 | **−0.0012** | 0.5601 | +0.0089 |
| `photo…orange-020` | 0.20 | 0.5191 | 0.5184 | **−0.0007** | 0.5371 | +0.0180 |
| `photo…orange-035` | 0.35 | 0.4783 | 0.4765 | **−0.0017** | 0.5025 | +0.0242 |
| `photo…orange-half` | 0.50 | 0.4385 | 0.4406 | **+0.0021** | 0.4679 | +0.0293 |
| `photo…orange-075` | 0.75 | 0.3908 | 0.3904 | **−0.0005** | 0.4102 | +0.0194 |
| `checkerboard…orange-010` | 0.10 | 0.5852 | 0.5834 | **−0.0017** | 0.5949 | +0.0097 |
| `checkerboard…orange-020` | 0.20 | 0.5481 | 0.5477 | **−0.0004** | 0.5685 | +0.0204 |
| `checkerboard…orange-035` | 0.35 | 0.5020 | 0.5010 | **−0.0010** | 0.5297 | +0.0277 |
| `checkerboard…orange-half` | 0.50 | 0.4578 | 0.4610 | **+0.0032** | 0.4909 | +0.0331 |
| `checkerboard…orange-075` | 0.75 | 0.4040 | 0.4033 | **−0.0007** | 0.4254 | +0.0215 |

**The renderer's law is Apple's shape.** The encoded mix is within **0.0032 on all ten** intermediate
rungs and within 0.0017 on eight of them; the linear-light mix misses by **+0.0089 to +0.0331**, an
order of magnitude worse and one-signed. Claims §5.36 finding 3 chose the encoded space from a single
half-strength cell; the ladder makes it a curve and it holds.

**What does NOT fit is the level the law interpolates from, and that is the renderer's known item.**
`GPU − native` runs from +0.0071 at `s = 1` to +0.0295 at `s = 0.1` on the photo and from +0.0116 to
+0.0495 on the checkerboard — it grows as the strength falls, because at low strength the composite is
mostly the untinted material, whose level is already +0.035 (photo) and +0.055 (checkerboard) over
native on this span (claims §5.55 §3, W18 §5.77 §6 reading 2). Scaled by `(1 − s)` that term predicts
+0.031 / +0.017 / +0.009 on the photo at 0.1 / 0.5 / 0.75 against the measured +0.0295 / +0.0201 /
+0.0116. **So the strength axis costs the renderer nothing of its own: the whole of the sub-unit gap
to Apple is the thin-span level gap, faded in by `(1 − s)`, plus a small +0.007…+0.012 that survives
at full strength.** The bed's single reading of "+0.020 over native at strength 0.5" (charter's
Grounding Baseline) is that curve at one point, and it does not indicate a defect in the law.

**And the tier's defect is visible against Apple, in the opposite direction.** On the photo at
`s = 0.1` the CSS tier reads **−0.0389 under native** where the renderer reads +0.0295 over it; the
tier crosses Apple's curve at about `s = 0.3` and the renderer never does. The fold removes the tier's
half of that, leaving the renderer's own item.

## 6. (d) — the exact fold, verified

`closed-form.ts` evaluates the candidate's declarations beside today's at every `s`, `b` and seed.

**The identity.** With the table kept on the untinted pair `(T, α₃)` and L3 painting
`α″ = 1 − (1 − s)(1 − α₃)`, `C″ = ((1 − s)·α₃·E(T) + s·E(L))/α″`:

| quantity | worst over 60 cells |
| --- | --- |
| `(1 − α″)·F + α″·C″` against `(1 − s)·E(M) + s·E(L)`, encoded, real-valued | **8.885e−8** |
| the same in linear luminance | **1.558e−7** |
| the same with `C″` written as `tintedCssOptics` writes it — eight bits | **2.847e−3** |
| least `α″ − α₃` | **+0.0733** (at `s = 0.1`; `α″` = 0.3401) |
| form flips (`cssTintFormAt` on the candidate against today) | **0** |

The 1e−6 clause is met with four orders of magnitude to spare in the real-valued arithmetic. The
third row is not the fold's error: it is the eight-bit quantum of an `rgba()` declaration, which
today's `rgba(L, s)` carries in the same measure — `tintedCssOptics` rounds `C″` to `Rgb255` because
that is what a CSS colour is. It is systematic per cell rather than averaged away over pixels, and it
puts a **±0.003 floor in linear luminance under any per-cell identity claim at these levels**. §7.

**The floor.** `α″ = 1 − (1 − s)(1 − α₃) ≥ α₃` for every `s ∈ [0, 1]`, with equality at `s = 0`;
measured least margin +0.0733. Today's painted alpha is `s` itself, so **today the floor is breached
on every surface with `s < 0.2668`** — on this bed the `orange-010` rungs (painted alpha 0.1
against a floor of 0.2668) and the `orange-020` and `blue-020` rungs (0.2 against 0.2668). Two of
the six charter strengths, six of the eighteen captured tinted cells.

**At `s = 1`.** `α″` = 1 and `C″` = `E(L)`, so the L3 declaration is byte-identical to today's on all
ten sweep cells (`rgba(235, 137, 0, 1)` … `rgba(10, 131, 253, 1)`). **The transfer is NOT identical**:
its `floorEncoded` moves from `T_folded` to `T`, so the table's output differs by up to **0.4898**
and the `<filter>`'s id changes with it. Wherever L3's own coverage is 1 that output is invisible;
where the element's antialiasing makes the coverage fractional both L3 and the filter layers are
covered by the same fraction, so it should still be invisible — but "should" is a claim about
Chromium's compositing of a shared shape and not a reading. §7 asks G1 to verify S3's byte-identity
at `s = 1` by capture rather than by declaration.

**The boundary.** `cssTintFormAt` is read at the MATERIAL's composite level
(`(1 − interior.tintAlpha)·b + interior.tintAlpha·luminance(interior.tint) + interior.addedLight`),
and neither the author layer nor the fold touches `interior`. So the fold cannot move the form, and
it does not: 0 flips over the 60 sweep cells, and the captured ladder drew `linear` on 20 of 20
scenes at 1x, 20 of 20 at 2x and 4 of 4 under each fold profile — `orange-010` included.

### Where G1 should apply it

Read `root.ts` 1907–1932 and `css-tier.ts` 1042–1071. Today:

```ts
// root.ts
const authorLayer = authorTintLayer(policySource, seed, tintBackdrop, tintGrip, tintShade);
const nodeBaseOptics = tintedCssOptics(
  cssOpticsFromSource(baseOptics, shadowedSource, cssMapping),
  policySource, seed, tintBackdrop, tintGrip, tintShade,
);
// … cssTierDeclarations({ optics: nodeBaseOptics, authorLayer, interior, … })

// css-tier.ts
const transfer = tintForm === "linear" && interior !== undefined
  ? cssTierTintTransfer(interior, floorAlpha, [optics.tint[0] / 255, …]) : undefined;
const overlayTint = transfer === undefined ? tint
  : authorLayer === undefined ? rgba(optics.tint, floorAlpha)
  : rgba(authorLayer.color, authorLayer.strength);
```

**The recommendation (q3 (a)): apply it in `cssTierDeclarations`, and give that function the
untinted conversion beside the folded one.** Concretely, the smallest change that is also the honest
one:

1. `root.ts` computes `cssOpticsFromSource(baseOptics, shadowedSource, cssMapping)` once — it already
   does, inline inside the `tintedCssOptics` call — and passes it to `cssTierDeclarations` as a new
   optional field, say `untintedOptics`, beside the `optics` it passes today. `nodeBaseOptics` stays
   exactly what it is: `nodeOptics` is derived from it for the RENDERER's input, and the encoded form
   and every plain-`blur()` engine still need the whole-material fold. Nothing else in `root.ts`
   moves.
2. `css-tier.ts`, in the `tintForm === "linear"` branch only, takes the transfer's `floorEncoded`
   from `untintedOptics.tint` rather than `optics.tint`, and builds `overlayTint` from
   `tintedCssOptics({ ...untintedOptics, tintAlpha: floorAlpha }, …)` rather than from
   `rgba(authorLayer.color, authorLayer.strength)`. The fold's algebra is already in
   `tintedCssOptics`; with `{tint: T, tintAlpha: α₃}` as its `css` argument it IS this fold, so no
   new expression enters the tier.
3. Everything outside that branch is untouched by construction: `tintForm === "encoded"` still reads
   `optics` (the folded material) and still writes `rgba(optics.tint, optics.tintAlpha)`, and an
   engine without `referenceFilterInBackdrop` never reaches the branch at all (X9).

Two variants were considered and are worse. Folding in `root.ts` and passing the result as `optics`
would break the encoded form and the other engines, which need the whole-material fold on the same
object. Passing the *pair* `(T, α₃)` as a bare colour would hide that the second argument is the
floor the tier already computes from `optics` (`cssTierFloorAlpha`), and the two would be free to
disagree.

One inconsequence worth naming as a benefit: under the fold a tinted surface's transfer is the same
transfer an untinted surface at the same backdrop builds, so `referenceFilterId` collapses the two
and a tinted group stops needing its own `<filter>` definition.

## 7. `[parent-impact]`

1. **The charter's mechanism is not the whole defect: the table saturates, and the saturation is
   larger than the term the charter names.** `cssTierTintTable` clamps into [0, 1]; solved against
   `T_folded` the argument exceeds 1 on the seed's darkest channel over most of the ladder — 47 of
   180 analytic channel cells, up to −0.083 encoded, and 0.1–14.2 % of masked channel samples on the
   captured cells. It is a hue error and it fires before L2's Gaussian, so it violates the affine
   premise W17 G1's derivation rests on. **The fold removes it entirely (clamp share 0.000 on every
   captured cell).** The charter's Purpose and its Grounding Baseline should say so; the wave's
   claim is larger and better than it was written.
2. **The acceptance's "the closed form reproduces the measured error within 0.002 per cell" is not
   met and cannot be, as written.** Measured: +0.0025…+0.0147 at 1x and +0.0023…+0.0250 at 2x, in
   two attributable parts — a constant −0.004 of unmodelled decoration at `s = 1` and a positive term
   proportional to the clamp share. Modelling the clamp needs the filtered backdrop per pixel, which
   no composite carries. **Recommendation:** re-declare the clause against the fold's prediction,
   which does not clamp, with the `s = 1` decoration constant read per cell as its own control — or
   re-declare the tolerance at 0.005 on the photo and 0.02 on the checkerboard with the clamp share
   beside each row. A parent decision, and it also decides S5's shape for G1.
3. **The eight-bit `rgba()` declaration puts a ±0.003 floor under any per-cell identity claim.**
   The fold is exact to 1.6e−7 in real arithmetic and to 2.85e−3 once `C″` is rounded to `Rgb255`.
   Today's `rgba(L, s)` carries the same quantum, so nothing regresses — but a 0.002 clause on a
   tinted cell is under the quantum of the declaration it is testing.
4. **S3's byte-identity at `s = 1` must be verified by capture.** The L3 declaration is byte-identical
   (verified, ten cells), but the transfer's `floorEncoded` moves and the table's output differs by
   up to 0.4898. It should be invisible under an opaque L3 of the same shape; that is an argument
   about Chromium's compositing, not a reading, and G1 has the capture that settles it.
5. **The fold profiles' clause is a claim about a sum this wave owns part of.** The UNTINTED
   increased-contrast capsule over the photo reads **+0.0364** CSS − GPU at 1x and the
   reduced-transparency one **−0.0070**; the tinted rows there carry those offsets plus the tint's
   term. A `within 0.01` clause on the fold profiles' tinted cells is therefore not a statement about
   the author tint. Recommend re-declaring it as the tinted cell's movement relative to its own
   untinted control on the same profile (which W18 §7 already carries as the fold's own gap).
6. **The floor is breached today on two of the charter's six strengths.** Painted alpha `s` against
   `α₃` = 0.2668: `s = 0.1` and `s = 0.2` are under it, six of eighteen captured tinted cells. The
   fold's least margin is +0.0733. This is the doctrine clause q2 (a) settles and it is now measured.
7. **The renderer's own law is 0.0000…+0.0084 above the tier's intended expression** across the
   sweep, rising with strength and with the backdrop, because `tintedMaterialColour` reads the
   shade's luminance per pixel off the material while `authorTintLayer` reads it once per source.
   That is the tier's known granularity, not a defect this wave introduces, but it means the tier's
   target `(1 − s)·E(M) + s·E(L_css)` and the renderer's `tintedMaterialColour` are not the same
   expression to better than 0.008. G1's X7 coherence pin should be stated against the tier's own
   `L`, or its tolerance should carry this.

8. **The renderer's strength law is Apple's shape, and the charter's Deferred entry for it should be
   rewritten rather than carried.** The encoded-space mix fits Apple's own curve to −0.0017…+0.0032
   across ten intermediate rungs on two backgrounds; the linear-light alternative misses by +0.0089
   to +0.0331. The whole of the sub-unit `GPU − native` gap is the thin-span material level gap
   (+0.035 photo, +0.055 checkerboard) faded in by `(1 − s)`, plus +0.007…+0.012 that survives at
   full strength. The charter's Deferred entry reads "both tiers +0.020 over native at strength 0.5;
   the native ladder makes it a curve. The renderer's item." It is a curve now, and it is **not** a
   defect of the strength law — it is §5.55 §3's level, which the renderer's ledger already carries.
   The one part that is new is the +0.007…+0.012 residue at `s = 1`, where the material is the tint
   and the level gap should have vanished: that is the tint shade's own gap to Apple and it has no
   entry anywhere yet.
9. **The harness's activation attestation failed twice in ten runs with the machine idle throughout.**
   Run 7 lost six of twelve cells to `presentedActive: false` at 700–818 s of HID idle — no user was
   near it. W18 saw one such run and attributed it to HID activity; this wave has one of each, so the
   non-interactive session denying the window activation is a distinct and reproducible failure mode.
   It costs runs rather than correctness (the protocol catches it), but a probe now needs about ten
   runs to bank seven. A tracker line, not this wave's work.

## 8. What did not close

- **The 2x native ladder** — the charter's Deferred list; this bed is 1x only.
- **The fold profiles' own tinted composite** under a policy fold: `predict.ts` resolves the surface
  under `NOMINAL_ACCESSIBILITY_POLICY`, so the closed form is not carried onto the reduced-transparency
  and increased-contrast rows. Their measured CSS − GPU is in §3 and their attribution is not.
- **The clamp's cost as a colour** rather than as a luminance: §2.1 reports the clamp per channel and
  §4 its share per cell, but no ΔE was taken on the ladder's cells. The hue error is the part an
  interior mean under-reports and it is the part a reader would see.
- **The blue seed at 0.1, 0.35 and 0.75**, and every seed on the fold profiles at those strengths:
  the captured ladder carries blue at 0.2, 0.5 and 1.0 only, as the charter scoped it.
- **The blue seed natively**: the probe bed is orange only, as the charter scoped it, so the encoded
  mix is confirmed on one hue. A second hue is the cheap next probe if anyone doubts the shape.
- **Apple's own shade**, as a colour: the mix test uses Apple's `s = 1` capture as its endpoint, so it
  says nothing about whether `tintShadeLayer` lands where Apple's fully-tinted material does. The
  +0.007…+0.012 residue at `s = 1` is the luminance half of that question and the hue half is not
  taken.
