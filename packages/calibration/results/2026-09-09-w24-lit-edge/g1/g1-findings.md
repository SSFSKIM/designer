# W24 G1 — the collapse's transmission: the read, the mechanism, and what the mechanism does not reach

**Spike; deliverable findings.** Worktree `agent-aa8a0b1f92b46418f`, branched at `b245aef`. The
bed is the landed 0.12.0 one (`408ad2e`, CI green, unpublished). Nothing canonical was written:
no `results/matrix.json`, no `web-captures/`, no fixture, no `scenes.json`, no profile document.
The holdout was neither captured nor fitted; landed holdout captures were not read.

Artefacts beside this file: `read-impulse.py` (the instrument), `read-structure.py`, `psf.py`,
`solve-state.py` and their runners; `transmission-read.txt`, `solve-state.txt`; `ladder.sh`,
`make-candidates.sh`, `read-ladder.sh`; `fingerprints.mts`.

---

## 1. The instrument, and its two validations

`read-impulse.py` locates the fifteen dots in the background fixture itself (connected components,
so a scene that moved a dot would move the read with it), keeps the ones lying fully under the
declared shape eroded 6 CSS px, and reads through the body, on both axes: the profile's **peak**
excess over the local body, its **FWHM** in CSS px, and its **integral** in CSS px units. The local
body is the profile's own mean over an annulus 10–16 CSS px out, clipped to the eroded shape, so a
dot near an edge is never read against the rim. The centre dot — CSS (160, 104), the grid's middle,
four px below the shapes' own centre — is the headline; the others are the check.

**Validated on the background** (`--validate`): a dot reads its own size, peak 1.0000, FWHM 4.00
CSS px, integral 4.000, at both scales, exactly. The fixture also settles a fact the wave's
wording leaves ambiguous: the dots are 4 CSS px at **both** scales, so **4 device px across at 1x
and 8 at 2x** (240 and 960 lit device px over fifteen dots). A width quoted in CSS px therefore
hides a factor of two, and §5 below is what that hid.

**Validated against the parent's own table** (`finding/eye-finding.txt`) on the headline rows:

| cell | parent | this instrument |
| --- | --- | --- |
| light `impulse__capsule-button` 1x native | +0.0065, FWHM 8, 0.050 | **+0.0066, 7.57, 0.0508** |
| light `impulse__capsule-button` 2x native | +0.0254, 4, 0.107 | **+0.0254, 3.80, 0.1074** |
| light `impulse__rrect-md` 2x native | +0.062, 9, 0.65 | +0.0596, 8.65, 0.5763 |
| light `impulse__rrect-md` 2x landed | +0.071, 8, 0.70 | +0.0701, 8.28, 0.6791 |

The capsule rows — the ones G1 fits — agree to the fourth decimal. The `rrect-md` integrals run
wider in the parent's read because its window is wider; that difference is the window, not the
reading, and the peaks and FWHMs agree.

## 2. The read: what the reference passes and what vitrea passes

Full tables in `transmission-read.txt`. The four impulse cells, centre dot, x axis, linear luma:

| cell | native | landed 0.12.0 |
| --- | --- | --- |
| light `impulse__capsule-button` 1x | **+0.0066**, FWHM 7.57, ∫ 0.0508, body 0.0065 | **0.0000**, no width, ∫ 0.0000, body 0.0037 |
| dark `impulse__capsule-button` 1x | +0.0066, 7.57, 0.0508 (the same fixture bytes) | 0.0000, body 0.0037 |
| light `impulse__capsule-button` 2x | **+0.0254**, 3.80, 0.1074, body 0.0065 | **0.0000**, body 0.0033 |
| dark `impulse__capsule-button` 2x | +0.0254, 3.80, 0.1074 | 0.0000, body 0.0033 |
| light `impulse__rrect-md` 1x (uncollapsed) | +0.0510, 8.43, 0.4171, body 0.4342 | +0.1373, 4.91, 0.7526, body 0.4666 |
| light `impulse__rrect-md` 2x (uncollapsed) | +0.0596, 8.65, 0.5763, body 0.4314 | +0.0701, 8.28, 0.6791, body 0.4632 |

The off-centre dots the `rrect-md` covers read the same way as its centre one on both sides, which
is the instrument's third check: the transmission is a property of the material, not of a position.

The dark thin structured cells, and the collapsed stop cells, under the same eroded shape — body,
passed structure (`pass` = body sd / backdrop sd, W21 G0's passthrough) and the body's 8-bit code:

| cell | native body / pass / code | landed body / pass / code | Δcode |
| --- | --- | --- | --- |
| dark `checkerboard__capsule-button` 1x | 0.1056 / 0.1001 / 91.40 | 0.0671 / 0.0505 / 73.26 | **−18.1** |
| dark `checkerboard__capsule-button` 2x | 0.1071 / 0.1105 / 92.03 | 0.0682 / 0.0514 / 73.86 | **−18.2** |
| dark `photo__capsule-button` 1x | 0.0948 / 0.1950 / 86.80 | 0.0522 / 0.0862 / 64.56 | **−22.2** |
| dark `photo__capsule-button` 2x | 0.0953 / 0.2024 / 87.00 | 0.0520 / 0.0915 / 64.49 | **−22.5** |
| dark `impulse__capsule-button` 1x | 0.0066 / 0.0104 / 19.26 | 0.0037 / **0.0000** / 12.00 | −7.3 |
| dark `impulse__capsule-button` 2x | 0.0067 / 0.0205 / 19.34 | 0.0033 / **0.0000** / 11.00 | −8.3 |
| dark `dark-solid__capsule-button` 1x/2x | 0.0110 / — / 27.07 | 0.0117 / — / 28.15 | +1.1 |

The passthrough column is the sharpest statement of the finding: on the collapsed capsule vitrea
passes **exactly none** of the structure on offer where the reference passes a hundredth to a
fiftieth of it, and the body is 7–8 codes too dark besides.

## 3. What removes the transmission: the collapse's TARGET, not the alpha solve

The shader's tone block writes a (colour, alpha) pair. Expanding it:

```
adaptedAlpha = sA + k·(1 − sA)
adapted      = (sN·(1 − k)·sA + target·k) / adaptedAlpha
colour       = mix(backdrop, adapted, adaptedAlpha)
             = (1 − k)·[ (1 − sA)·backdrop + sA·sN ] + k·target
             = (1 − k)·M + k·target
```

with `M` the unadapted composite this pass would otherwise produce and `target` = `toneColour.rgb`,
**the group's mean backdrop colour — one number for the whole surface**. At `k` = 1 the surface is
that number and `backdrop` drops out of the expression entirely.

`solve-state.txt` reads the collapse's and the solve's state off the calibration page's own
publication (`report__webgpu.json`'s `page.groups[].backdropTone`, the honesty core) and evaluates
the shader's arithmetic on it. On every `impulse__capsule-button` cell — both schemes, both scales,
bare and tinted — `k` = **1.0000** exactly (toneX 0.0049 against `backdropToneLow` 0.02), and the
W9 response solve does not run, stood down **twice over**: by its own `toneAdapt < 0.995` gate ("at
k → 1 the collapse owns the pixel outright") and independently by an authority of 0 (the backdrop's
encoded level 0.00375 is below half the dark anchor 0.1104).

So the answer to the child's question is unambiguous and is arithmetic rather than inference:
**the collapse's target removes the dot; `solvedAlpha` is not evaluated on any cell where the dot
is missing.** The shader's comment "an adapting material stops transmitting" describes the
`k`-weighted half of a lerp, not a separate occlusion axis, and it needs no gate of its own — below
`k` 1 the `(1 − k)·M` half transmits already.

The arithmetic also says what W7 could not have seen. `dark-solid` is the backdrop W7 fitted the
collapse on, and there the per-pixel sample **is** the mean; no fit on that bed could tell a target
of "the mean" from a target of "what is under this pixel". The impulse bed can, and it says they
are not the same.

## 4. Clause 3, answered with numbers: a transmitting collapse cannot reach those cells

Parent acceptance clause 3 asks the dark thin structured cells to improve by at least half their
−16 / −19 codes "or the read says why a transmitting collapse does not reach them". **It does not
reach them, and the reason is the collapse's own gate.** From `solve-state.txt`:

| cell | toneX | `backdropToneHigh` | k |
| --- | --- | --- | --- |
| dark `checkerboard__capsule-button` 1x / 2x | 0.2187 / 0.2185 | 0.055 | **0.0000** |
| dark `photo__capsule-button` 1x / 2x | 0.1561 / 0.1548 | 0.055 | **0.0000** |
| dark `mid-dark-solid__capsule-button` | 0.0641 | 0.055 | 0.0000 |
| dark `impulse__capsule-button` | 0.0049 | 0.055 | 1.0000 |

The mechanism is multiplied by `k` at every pixel, so at `k` = 0 it is the identity by
construction. The −18.1 / −18.2 / −22.2 / −22.5 codes measured above are therefore **not the
collapse**: those capsules are drawing the ordinary dark material over a structured backdrop, and
their deficit is that material's own level and its passthrough (0.0505 against 0.1001 on
`checkerboard`, 0.0862 against 0.1950 on `photo` — the material passes about half the structure the
reference does, which is W21 G0's "the passthrough is a lerp holding back three to five times too
much", §5.89, unclosed).

**This corrects the charter on a point of fact.** The wave's Purpose and claims §5.107 §2 identify
the collapse's flattening with "the term W21 and W22 carried as the appearance switch and W23 G0
measured at −16 / −19 codes on the dark `checkerboard` / `photo` capsules". They are two different
terms with one symptom. The impulse capsule's missing dot is the collapse; the structured capsules'
missing codes are the dark material's level and alpha at `k` = 0. Fixing the first cannot move the
second by a code, and the wave should not expect it to. Recommended: clause 3 is met by this read
(its "or why not" branch) and the structured cells' term is carried by name — it is the same term
§5.89 left open and the thick-span composite does not cover it either.

## 5. The kernel, which is a finding and not a fit

The wave's design says: "if the dot's FWHM (8 at 1x, 4 at 2x — a width that does not double with
the scale) asks for a different kernel, that is a finding, not a fit". It does. The dot is a 4 CSS
px box, so the transmitted profile is that box convolved with the material's own blur; `psf.py`
fits a sharp and a heavy Gaussian in **device** px (`transmission-read.txt` §3):

| profile | sharp A | sharp σ (device px) | σ (CSS px) | heavy A | heavy σ (device) |
| --- | --- | --- | --- | --- | --- |
| native `impulse__capsule-button` 1x (collapsed) | 0.01335 | **2.63** | 2.63 | — | — |
| native `impulse__capsule-button` 2x (collapsed) | 0.02390 | **1.30** | 0.65 | 0.00367 | 13.1 |
| native `impulse__rrect-md` 1x (uncollapsed) | 0.10995 | **2.87** | 2.87 | 0.211 | 28.9 |
| native `impulse__rrect-md` 2x (uncollapsed) | 0.02054 | **1.40** | 0.70 | 0.147 | 11.1 |
| landed `impulse__rrect-md` 1x | 0.17627 | 1.68 | 1.68 | 0.182 | 17.9 |
| landed `impulse__rrect-md` 2x | 0.05419 | 4.86 | 2.43 | 0.125 | 9.2 |

Three things follow, all of them worth the record:

1. **The reference's collapsed material transmits through the SAME kernel as its uncollapsed one**
   (σ 2.63 against 2.87 device at 1x; 1.30 against 1.40 at 2x). The collapse changes the level and
   not the blur, which is the direct evidence for the mechanism this child implements: the target
   should be the sample the refraction path already computes, and no second kernel is called for.
2. **That kernel is invariant in neither unit.** σ 2.63 device px at 1x and 1.30 at 2x is a factor
   of two in device px and a factor of four in CSS px. vitrea's own is 1.68 device at 1x and 4.86
   at 2x — the opposite trend. So the SHARE that comes through can be one constant per scale, but
   the WIDTH the dot arrives at cannot be made to match at both scales by any value of it. This is
   a gap in the material's own scatter law and is recorded, not fitted, here. It is why
   `collapseTransmission` takes a second anchor at dpr 2 (`collapseTransmission2x`) on the pattern
   `sizeScatterGainMax2x` established for the body's second scale (§5.69 §1).
3. **The scale ratio of the peak is the dot's own geometry, not a different material.** The 2x dot
   is 8 device px where the 1x dot is 4, so with a kernel of comparable width the 2x peak is ~4×
   the 1x one — measured +0.0254 against +0.0066, a ratio of 3.85. The transmitted ENERGY per
   device px² is nearly equal at the two scales, which is what a single physical transmission
   should look like.

## 6. The mechanism, as implemented

One constant, in the tone block, inert at 0. `packages/renderer-webgpu/src/material.ts`:

```
collapseTransmission   ∈ [0, 1]   default 0
collapseTransmission2x ∈ [0, 1]   default 0, falls back to the 1x constant when a patch names
                                  only that one (`collapseTransmissionAtScale`, `rampAtScale`)
```

`packages/renderer-webgpu/src/wgsl/optics.ts`, immediately before the (colour, alpha) pair:

```wgsl
var toneTarget = ou.toneColour.rgb;
if (ou.flags.x > 0.5) {
  toneTarget = mix(toneTarget, backdrop, clamp(ou.toneRowThick.w, 0.0, 1.0));
}
```

and `ou.toneColour.rgb` in `adapted` becomes `toneTarget`. `backdrop` is the per-pixel value the
refraction path already sampled — the body texture and the scatter chain mixed by `kScatter` at the
refracted UV — so the composite becomes

```
colour = (1 − k)·M + k·[ (1 − c)·toneColour + c·backdrop ]
```

Everything else is untouched, and that is the design's requirement met exactly: the tone axis's
argument is still the group's mean luminance plus the size bias, the response solve still
composites against `toneAnchor.w`, `present = 1 − toneAdapt` still fades the rim and the inner
shadow. **The collapse still collapses the level; it stops flattening the structure.**

Seams:

- `ou.toneRowThick.w` is the tone block's one padding slot (`d[71]`, written as literal `0` until
  now), so the uniform buffer's size is unchanged and the default render is bit-identical.
- **Gated on `flags.x`.** With no pyramid to sample, `backdrop` is the zero vector and this pass
  writes a layer for the browser to composite; lerping the target toward zero there would produce a
  black surface. On that path the CSS tier's own `backdrop-filter` is what carries the transmission
  (§7).
- **Gated on the un-degraded regime** in `renderer.ts`, on the same predicate as the W9 response
  law (`backdropToneUnderPolicy(policy, material) >= 0.999`): the constant is fitted on the
  standard reference, and the accessibility references are a nearly opaque material whose collapsed
  appearance was never read over a textured backdrop. Under any policy fold the target is the mean,
  which is W7's behaviour and what those profiles were fitted on. **The parent may want to revisit
  this**; it is a decision, not an arithmetic necessity.
- `capture-web.ts`'s `MATERIAL_PATCH_KEYS` gains both names, so a sweep can name them as axes.
- W7's "texture collapse" paragraph in `material.ts` is corrected **beside**, not over, in the new
  field's own doc comment: every figure W7 recorded stands; what it did not measure is a backdrop
  with texture in it.

## 7. The CSS tier: `backdrop-filter` can carry this exactly, and needs only an alpha

`platform-web/src/optics.ts`'s `adaptedSourceOptics` builds the same pair over the tier's own
blurred backdrop `B` (which the browser composites through one in-place `backdrop-filter`):

```
A = α + k(1 − α)                                  T = ((1 − k)·α·tint + k·tone) / A
(1 − A)·B + A·T = (1 − k)·M + k·tone              — the renderer's expression, exactly
```

Matching the transmitting composite term by term gives the whole of the CSS mirror:

```
A' = α + k(1 − α) − k·c        =  A − k·c
T' = ((1 − k)·α·tint + k·(1 − c)·tone) / A'
```

So **the tier's collapse needs only its tint layer's alpha reduced by `k·c` and its colour
re-solved against that alpha** — no second layer, no second filter, no new mapping constant. The
blur is already there and already per pixel. At `k` = 1 the collapsed CSS surface stops being
opaque (`A'` = 1 − c), which is precisely the transmission; the border that carries `rimCollapsed`
is a separate channel and is unaffected.

What it cannot carry is the same **width**: the tier's one Gaussian at `blurSigma` is not the
renderer's sharp-plus-heavy mix, so the dot arrives at a different width on the two tiers. That is
an X5 residual to record, not to charter — and it is smaller than the residual §5 already records
against the reference itself. `packages/calibration/test/tier-coherence.test.ts` pins the two tiers
and will need the same term; G2 owns both.

*Not implemented here.* At `c` = 0 the formula above is today's line for line, so landing it is
inert — but it is G2's seam (X5) and touching `platform-web` in a spike would put 114 CSS captures
at risk for no reading.

## 8. The goldens, and the attribution the suite cannot currently give

**`collapsed-tone` will not move at any value of this constant, and the reason is the scene:** its
backdrop is `{ kind: "flat", luminance: 0.01 }` — a solid — so the per-pixel sample equals the
mean everywhere and `mix(toneColour.rgb, backdrop, c)` is the identity. The suite has no scene in
which a collapsed surface stands over a textured backdrop, so the isolation proof's attribution for
`collapseTransmission` would be **vacuous**, exactly as it was for `rimCollapsed` and
`rimCollapsedTinted` before W23 added `collapsed-tone` itself (`isolation.spec.ts` line 591).

**Proposal for G2:** one scene, `collapsed-tone-textured`, the same two groups and the same
declared `backdropTone: [0.01, 0.01, 0.01]` (which is what sets `k`, so the collapse still fires
fully) over `backdrop: { kind: "gradient", from: [0, 0, 0], to: [0.06, 0.06, 0.06] }`. A gradient
rather than a checkerboard because a smooth per-pixel variation survives any kernel, so the scene
attributes the constant and not the blur. Its hash is a first reading under `W24_HASHES` with that
reason recorded, and every other golden must reproduce byte for byte.

## 9. The ladder, the fit and the rows

*(filled in below after the ladder runs; the GPU is G0's until its DONE marker — X4.)*

## 10. The exact diff for G2

| file | change |
| --- | --- |
| `packages/renderer-webgpu/src/material.ts` | `collapseTransmission` and `collapseTransmission2x` on `MaterialProfile` with the correction to W7 beside its paragraph; both defaults 0; both on `MaterialProfilePatch` and in `withMaterialOverrides` (the 2x anchor falling back to the 1x one); `COLLAPSE_TRANSMISSION`, `COLLAPSE_TRANSMISSION_2X`, `collapseTransmissionAtScale` |
| `packages/renderer-webgpu/src/wgsl/optics.ts` | `toneRowThick.w`'s struct comment; `toneTarget` before the pair, and `toneTarget` in place of `ou.toneColour.rgb` in `adapted` |
| `packages/renderer-webgpu/src/passes.ts` | `collapseTransmission` on `OpticsPassArgs`; `d[71]` |
| `packages/renderer-webgpu/src/renderer.ts` | the value under the un-degraded gate, resolved at `dpr` |
| `packages/calibration/scripts/capture-web.ts` | both names in `MATERIAL_PATCH_KEYS` |

**G2 also owns, and G1 did not touch:**

1. **The profile documents.** The resolved-material fingerprint moves because the material gained a
   field, even at the inert default; `tuned-profiles.test.ts` is red in this worktree by exactly
   that one assertion and nothing else. `fingerprints.mts` prints what to re-record:
   `apple-macos-26.5-1x-light-standard` `c426a37744c38cce` → **`0845b5a3c3f2691f`**;
   `apple-macos-26.5-1x-dark-standard` `bf5752ac1b152238` → **`409210076b92222c`** (both at the
   inert default; they move again when the fitted constants land, so re-record after the values).
   G1 does not write committed evidence.
2. **The CSS mirror** (§7) and `tier-coherence.test.ts`.
3. **The textured collapsed golden** (§8).
4. **`FITTED_CONSTANTS`** in `tuned-profiles.test.ts`, if the constant is to be named there.

## 11. Every gap, with numbers

| gap | number | where it belongs |
| --- | --- | --- |
| The reference's transmitted kernel is invariant in neither unit; vitrea's runs the other way | σ 2.63 → 1.30 device px (1x → 2x) native, 1.68 → 4.86 vitrea | claims §5.107; the material's scatter law, a future wave |
| The dark structured thin capsules' body and passthrough at `k` = 0 | −18.1 / −18.2 / −22.2 / −22.5 codes; pass 0.0505 vs 0.1001 and 0.0862 vs 0.1950 | the same term as §5.89's passthrough; carried by name, NOT reachable by this mechanism |
| The collapsed body itself is 7–8 codes dark before any transmission | dark `impulse__capsule-button` 19.26 → 12.00 (1x), 19.34 → 11.00 (2x) | partly closed by the mechanism (the transmitted energy raises the mean); the residual is the collapse's own level |
| The CSS tier transmits through one Gaussian, not the renderer's two components | width only; the share is exact | X5 residual, recorded |
| The mechanism is stood down under every accessibility fold by decision | — | §6; the parent's call |
| The golden suite has no textured collapsed scene | — | §8 |

