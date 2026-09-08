# W22 G1 — the form declared and dry-run: `specularGain` fitted to 0 on the light profile, the holdout read once

Findings, not spec text. The parent writes the claims section and the Decision Log from this file.
Every number here is a reading taken in this gate; nothing canonical was written. The tables live
beside this file as `.txt`, the scripts that produced them beside those, and the scratch root is
`/Users/new/.claude/jobs/5c70e47f/tmp/w22/g1/`.

Worktree branch `worktree-agent-a929b7db2ba66befd`; the frozen configuration is main at `3e88921`
(W22 G0's shimmer gate and G3's backdrop-stack fix both merged) plus the one constant this gate
fits. The dry run ran at worktree `HEAD bd751f0` — a merge of main that carries `3e88921` and adds
no vitrea code, only spec, claims and plugin files (`git diff --stat 3e88921 HEAD` touches nothing
under `packages/` or `apps/`).

---

## 0. What was run, and what was deliberately not

| step | what | where |
| --- | --- | --- |
| the fit | eight documents differing in `optics.regular.specularGain` alone, on the five untinted solid calibration cells, both light scales | `g1-ladder-capture.sh` → `ladder-reads/`, `fit-specular.py` |
| the form | `material.ts`, `platform-web/src/optics.ts`'s mirror, the light profile document, `tuned-profiles.test.ts` | the code commit |
| the suites | `pnpm -r build`, `pnpm -r lint`, `pnpm -r test` (1 880 tests over 129 files) | all green |
| the goldens | the attribution capture, then `goldens:regen` behind the isolation proof | `attribute-w22-goldens.py`, `goldens-attribution.txt` |
| the dry run | six profiles × two tiers × (calibration + validation, then holdout), `--alpha --write-partial` | `g1-dryrun-run.sh` → scratch |
| the reads | clause 2 per side, ΔE per tier, byte identity, the stack per pane, S2/S3, the floors, the shadow rows | `g1-clauses.py`, `delta-e.py`, `byte-identity.py`, `stack-tables.py`, `stops.py`, `shadow-rows.py` |
| the gate | `adopted-thresholds` over the FULL scratch matrix, both tiers, all six profiles, all three sets | §7 |
| the sheets | native \| GPU before \| GPU after \| CSS after, both schemes, both scales | `../sheets/g1-{1x,2x}.png` |

**Not run, on purpose:** a second holdout read. X5 spends the wave's one holdout read here, and the
ladder above therefore fits on CALIBRATION cells only — `mid-dark-solid__capsule-button` is a
holdout scene and could not be a fit row. It is read once, in the dry run, and reported in §5.

**Nothing canonical was written.** `--out-matrix` and `VITREA_WEB_CAPTURES` both point at scratch
throughout; `results/matrix.json`, `web-captures/`, `apps/reference-apple/fixtures/` and
`scenes.json` are untouched in this worktree and in the main checkout. The canonical matrix was
copied to scratch to be read as the "before" column.

---

## 1. The fit, declared

### 1.1 The objective, per contrast, before the number

W22 Decision Log 2 (b) rules the constant is fitted on `T−B` and `L−R` per untinted solid cell at
both scales, never on a mean pooled over sides. The reason is measured, not stylistic (claims §5.94
§3): the pooled mean PREFERS the shipped 0.55, because the specular lifts `dark-solid__rrect-md`'s
top row from −0.061 to +0.062 against a reference of +0.047 while leaving its bottom at −0.061
against the same +0.047. It buys one side of a pair by breaking the other, and only a contrast can
see that. The two contrasts are also the only clean ones the instrument has: the declared box's rim
band is a rectangle's band and a rounded shape does not fill it, so a side's peak mixes rim with
background at a weight that differs between the horizontal and the vertical pair, and `L−R` / `T−B`
compare sides of identical geometry, where the mixture cancels exactly.

**The rows.** `light-solid__{capsule-button,rrect-md,rrect-ml}` and
`dark-solid__{capsule-button,rrect-md}`, at 1x and 2x — twenty contrast rows. **The ladder.** Eight
documents at `specularGain` 0, 0.025, 0.05, 0.10, 0.15, 0.25, 0.40, 0.55, each the shipped light
document with that one leaf overridden (`g0/make-candidates.mjs`). **Separation.** A row separates
the constant when its objective moves across the ladder by more than 0.000625, G0's measured
recovery floor for this instrument.

### 1.2 The answer: 0, and every separating row agrees

| ladder point | 0.000 | 0.025 | 0.050 | 0.100 | 0.150 | 0.250 | 0.400 | 0.550 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mean objective, 11 separating rows | **0.00097** | 0.00251 | 0.00365 | 0.00695 | 0.00959 | 0.01570 | 0.02346 | 0.03102 |
| mean on `T−B`, 7 separating rows | **0.0015** | 0.0039 | 0.0056 | 0.0108 | 0.0149 | 0.0244 | 0.0365 | 0.0482 |
| mean on `L−R`, 4 separating rows | **0.0001** | 0.0001 | 0.0002 | 0.0003 | 0.0004 | 0.0004 | 0.0007 | 0.0009 |

Monotone in the gain on both contrasts. **Eleven of the twenty contrast rows separate the constant,
and every one of them minimises at 0.** No row's own minimiser is anything else: the one row whose
argmin is 0.55 (`2x light-solid__capsule-button` `T−B`) has a span of 0.0006, below the separation
floor, and does not separate.

The separating rows, with their spans:

| contrast | dpr | cell | argmin | span |
| --- | --- | --- | ---: | ---: |
| `T−B` | 1x | `dark-solid__rrect-md` | 0.000 | 0.1233 |
| `T−B` | 2x | `dark-solid__rrect-md` | 0.000 | 0.1813 |
| `T−B` | 2x | `light-solid__rrect-md` | 0.000 | 0.0083 |
| `T−B` | 2x | `light-solid__rrect-ml` | 0.000 | 0.0076 |
| `T−B` | 1x | `light-solid__rrect-md` | 0.000 | 0.0029 |
| `T−B` | 1x | `light-solid__rrect-ml` | 0.000 | 0.0027 |
| `T−B` | 1x | `light-solid__capsule-button` | 0.000 | 0.0013 |
| `L−R` | 2x | `dark-solid__rrect-md` | 0.000 | 0.0009 |
| `L−R` | 1x | `dark-solid__rrect-md` | 0.000 | 0.0008 |
| `L−R` | 1x | `light-solid__capsule-button` | 0.000 | 0.0008 |
| `L−R` | 2x | `light-solid__capsule-button` | 0.000 | 0.0007 |

The load-bearing row is `dark-solid__rrect-md` `T−B` at both scales: the reference splits top from
bottom by **+0.0002** there and 0.55 splits them by **+0.1237** (1x) and **+0.1817** (2x), an order
of magnitude and a half. `dark-solid__capsule-button` is dead in the fit at both scales (span
0.0000, the collapse folds the rim out entirely) and is printed as context.

**S5 does not fire.** Full table: `fit-specular.txt`; the reads it runs on: `ladder-reads/`.

### 1.3 What moved in the code, and what did not

| file | what |
| --- | --- |
| `packages/renderer-webgpu/src/material.ts` | `DEFAULT_MATERIAL_PROFILE.optics.regular.specularGain` 0.55 → **0**, with the rationale in the doc comment beside it |
| `packages/platform-web/src/optics.ts` | `MATERIAL_SOURCE_OPTICS.regular.specularGain` 0.55 → 0 — the mirror `tier-coherence.test.ts` pins in both directions |
| `packages/calibration/profiles/apple-macos-26.5-1x-light-standard.json` | `patch.optics.regular.specularGain` 0 (named for the first time); `entries.rimIntensity` re-recorded; `resolvedMaterialSha256` **b1ff51ad15273736 → f6c54a1ea236447a**; `$comment-w22`; the sha history appended |
| `packages/calibration/test/tuned-profiles.test.ts` | `optics.regular.specularGain` added to `FITTED_CONSTANTS` and asserted by name |

**The `clear` variant's `specularGain` 0.45 does not move.** No scene on the calibration bed declares
that variant, so it has no rows and nothing to be fitted on. Recorded in the profile and in the code
comment rather than left silent.

**The dark profile does not move, verified rather than assumed.** Its patch has pinned
`specularGain` 0 explicitly since W21 G1, so the resolved dark material is unchanged:
`resolvedMaterialSha256` stands at **d86f480c0e136627**, `tuned-profiles.test.ts` is green on both
profiles, and `pnpm --filter @vitreajs/vitrea-web run profile:dark` regenerates
`platform-web/src/dark-profile.ts` with an **empty `git diff`** (X7).

**The CSS tier is not decorative here.** `interiorBandLight` carries the specular term into the CSS
tier's derived interior LEVEL, so the mirror is load-bearing: at full presence the band's light falls
by 0.0013 on the widest calibration surface (`rrect-ml` 224 × 128) and 0.0053 on the narrowest
(`rrect-sm` 64 × 32) — 0.0040 on the canonical capsule. This is why 81 CSS renders move in §6 where
G0's gate moved none.

**Three unit cases had to be re-recorded, and none of them by rewriting a recorded number:**

- `platform-web/test/interior-level.test.ts` pins the band's light against W17 G0's evaluation,
  which was taken at 0.55. G0's numbers stand; the reproduction is now asserted at the constants G0
  held, and the value the shipped constant derives is recorded **beside** it as `bandLightW22`
  (0.004619 → 0.002849, 0.009300 → 0.005326, 0.003389 → 0.002055) and asserted in its own right,
  with the ambient's share of G0's term (0.574–0.617) bounded so a derivation that lost the ambient
  too could not pass.
- The same file's "reads the profile's own constants, patch included" doubled `rimAlpha` and
  `specularGain` and expected exactly 2×. Twice nothing is nothing, so the doubling is now stated
  off the mirror's own values and the specular channel is asserted separately — a patch that revives
  the term must still reach this tier, which is the K5 gap the case exists to catch.
- `platform-web/test/w19-fold-cases.ts` fed the LIVE mirror into a bed whose expected bytes are
  `w19-pre-fold-declarations.json`, recorded on the pre-W19 tree. That tree cannot be re-run, so the
  file can never be re-recorded and its bytes are the whole of the "nothing else moved" claim. The
  bed now names the constants the recording depended on (`RECORDED_SOURCE_OPTICS`, `specularGain`
  0.55) and freezes them: what it asserts is a DIFFERENCE, and a difference is stated at fixed
  constants or not at all.

---

## 2. The goldens: ten moved, one could not, and the attribution is exact

**S4 does not fire.** S4 fires when *a golden moved and the attribution failed*. Ten moved and the
attribution held — and it is a stronger attribution than the file has been able to make since W8,
because this wave's delta IS expressible through the profile seam. Both columns are renders of the
SAME tree with `specularGain` 0.55 injected through `materialProfile` in one of them, so nothing but
that constant can be in the difference by construction. No second worktree was needed.

`w15-attribution.spec.ts` was generalised by one optional field (`VITREA_ATTRIB_PATCH`) to make that
possible; the capture is otherwise W15's.

| scene | px moved | of | max \|Δ\| rgb | max \|Δ\| a | band px | upper share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `body-ramp-1x` | 166 | 24 000 | 34 | 0 | 1.41 | 1.000 |
| `concentric-nesting` | 1 005 | 96 000 | 51 | 0 | 2.24 | 0.998 |
| `field-mask` | 857 | 96 000 | 97 | **97** | 2.24 | 1.000 |
| `lens-size-scaling` | 928 | 96 000 | 42 | 0 | 2.24 | 0.984 |
| `placed-checkerboard` | 853 | 96 000 | 42 | 0 | 2.24 | 1.000 |
| `refraction-checkerboard` | 857 | 96 000 | 44 | 0 | 2.24 | 0.999 |
| `rim-two-references` | 1 261 | 96 000 | 50 | 0 | 2.24 | 0.998 |
| `tint-adaptation-dark` | 849 | 96 000 | 57 | 0 | 2.00 | 1.000 |
| `tint-adaptation-light` | 841 | 96 000 | 40 | 0 | 2.00 | 0.994 |
| `union-pair` | 773 | 96 000 | 50 | 0 | 2.24 | 0.999 |
| **`highlight-press-glow`** | **0** | 96 000 | 0 | 0 | — | — |

(`declined` column — the isolation proof's named profile. The `default` column agrees on every scene
to within a few pixels; its one outlier is `lens-size-scaling` at an upper share of 0.676, whose two
surfaces of different sizes share one bounding box so "upper half" splits the smaller surface's own
band, not the term reaching downward.)

Three properties identify the mover and they are the whole of the attribution:

1. **It is a band.** The largest distance from a moved pixel to an unmoved one is **1.41–2.24 device
   px** on every scene, against a `rimWidth` of 1.5 CSS px. Nothing moved in an interior.
2. **It is lit from above.** 98–100 % of the moved luminance sits in the upper half of the moved
   region — the signature of `lightDirection`'s −0.9285 y-component through `clamp(n · l)^6`.
3. **The one scene that could not move did not.** `highlight-press-glow` captures the HIGHLIGHT
   canvas; the rim's specular is the OPTICS pass's. Its hash is byte-identical to the 2026-08-25
   original, through C9a, W8, the post-v1 wave, W11a, W11c, W12, W14, W15 and this.

Alpha moved on exactly one scene, `field-mask`, by up to 97. It is the only scene with
`noBackdrop: true`, and on that path the optics pass writes a premultiplied LAYER rather than an
opaque pixel (W11a's entry in the same file), so light added to the rim is light added to alpha
there. Every other scene's alpha is untouched.

**Re-recorded, behind the proof:** `W22_HASHES` in `e2e/golden/isolation.spec.ts` (ten scenes, a new
dated table with the reason and the measurement, superseding nothing above it), the ten golden PNGs
via `goldens:regen`, and `PLACED_CHECKERBOARD_COVER_HASH` in `scenes.spec.ts`
(`a0cd4e7b…` → `7e57804f…`; the cover-fit render draws the same rim as the placed one, which is the
fourth time that constant has followed a material change and the note says so). **29 of 29 goldens
pass** after the re-record.

---

## 3. The dry run — the wave's one holdout read (X5)

Six profiles × two tiers × `calibration,validation` then `holdout`, GPU tier before CSS within each
column, `--alpha --write-partial`, all to scratch. **229 cells**, exactly the canonical bed's
composition — every (profile, tier, set) count matches `results/matrix.json` cell for cell.

**All six profiles, not W21's three.** W21's dry run took the two dark profiles and one light one
because only the dark document moved. This wave's constant is on the LIGHT document, which the two
light standard profiles and BOTH accessibility profiles resolve through, so four of the six move —
and the gate cannot be run over a partial bed at all (G0 §4: the cross-tier identity check fails on
any partial rebuild).

**One run exited non-zero, and it is pre-existing.** `1x-light-increased-contrast / css / holdout`
returned 1 on `hc-text__capsule-button__rest`: *"contourCurvature: a 0.00px contour sampled 512
times at σ=3 carries no curvature"*. The canonical matrix has no `dom` cell for that scene and
profile either, so the canonical rebuild returns the same code on the same run; nothing about it is
this gate's. G2 should expect it.

**Digests:** `g1-digests.txt` — 230 captures, no MISSING, with both profile documents' file sha256,
`resolvedMaterialSha256` and full patch recorded above them. The light document is
`9360d73bd071…` / `f6c54a1ea236447a`; the dark is `ebfb08586af0…` / `d86f480c0e136627`, unchanged.
G2 must reproduce these bytes.

---

## 4. Clause 2 — the rim per side, both beds, both scales (`g1-clauses.txt`)

### 4.1 W21 clause 4's two open cells close, at both scales

| cell | dpr | `L−R` before → after | left \|Δ\| against the reference | verdict |
| --- | --- | --- | ---: | --- |
| `dark-solid__rrect-md` | 1x | +0.1327 → **+0.0000** | 0.0067 | met |
| `dark-solid__rrect-md` | 2x | +0.2312 → **+0.0000** | 0.0133 | met |
| `mid-dark-solid__capsule-button` | 1x | +0.0523 → **+0.0000** | 0.0005 | met |
| `mid-dark-solid__capsule-button` | 2x | +0.0575 → **+0.0000** | 0.0003 | met |

`mid-dark-solid__capsule-button` is a holdout cell and this is its first per-side reading; the fit
did not see it.

### 4.2 The whole clause, moved

**GPU tier: 5 sides newly MET, 1 newly MISSED, 90 unchanged.**

| | scheme | dpr | cell | side | native | before → after |
| --- | --- | --- | --- | --- | ---: | --- |
| newly MET | light | 1x | `impulse__rrect-md` | left | 0.3876 | 0.4277 → 0.3580 |
| newly MET | dark | 1x | `dark-solid__rrect-md` | left | 0.0296 | 0.1690 → 0.0363 |
| newly MET | dark | 1x | `mid-dark-solid__capsule-button` | left | 0.0622 | 0.1140 → 0.0617 |
| newly MET | dark | 2x | `dark-solid__rrect-md` | left | 0.0322 | 0.2767 → 0.0455 |
| newly MET | dark | 2x | `mid-dark-solid__capsule-button` | left | 0.0623 | 0.1201 → 0.0626 |
| newly MISSED | light | 1x | `impulse__rrect-md` | **top** | 0.4949 | 0.5191 → 0.4052 |

**CSS tier: 0 newly met, 0 newly missed, 96 unchanged.** Every one of the CSS tier's 15 standing
misses is inherited from the W21 bed, including the two `L−R` misses
(`light 1x mid-dark-solid__capsule-button` −0.0563 and `light 2x dark-solid__rrect-md` +0.0393),
which read identically before and after.

**On the dark bed the GPU tier misses nothing.** All 18 standing GPU misses are in the LIGHT scheme
and all of them are on the three cells where the light material sits over a DARK backdrop —
`dark-solid__rrect-md`, `impulse__rrect-md`, `mid-dark-solid__capsule-button`. That is G0's recorded
open cell (claims §5.94 §3, the W22 spec's Deferred: *the collapsed rim in light*), now read on
three cells and at both scales because two of them are holdout and validation and G0 could not open
them.

### 4.3 The one newly missed side, honestly

`light 1x impulse__rrect-md` top went from +0.0242 over the reference to −0.0898 under it. It is the
pair-breaking coincidence the Decision Log named, seen from the other side: the specular was lifting
one side of a rim that is 0.05–0.11 too dim on all four, so removing it makes the cell symmetrically
wrong where it had been asymmetrically half-right. The same cell's `T−B` goes +0.1092 → −0.0048
against a reference of +0.0001, and its `L−R` +0.0696 → +0.0000 against −0.0001. The underlying
defect — the light material's rim over a dark backdrop, whose rows demand a `rimAlpha` of 2.4–2.9 —
is unchanged and is not this wave's constant.

---

## 5. Clause 4 — the bed, before → after (`delta-e.txt`, `moved-rows.txt`)

OKLab ΔE mean, per profile, per set, per tier. `before` is the canonical matrix at the 0.10.0
landing (the W21 bed); `after` is this dry run. **The before → after span includes W22 G0's shimmer
gate and G3's backdrop-stack fix as well as this gate's constant** — those two are already on main
and are part of the frozen configuration.

| profile | tier | calibration | validation | holdout |
| --- | --- | --- | --- | --- |
| 1x light standard | **webgpu** | 0.00329 → 0.00330 (**+0.00001**) | 0.00259 → 0.00261 | 0.00911 → 0.00914 |
| 2x light standard | **webgpu** | 0.00334 → 0.00333 (−0.00000) | 0.00263 → 0.00263 | 0.00906 → 0.00906 |
| 1x dark standard | **webgpu** | 0.00410 → 0.00404 (−0.00007) | 0.00291 → 0.00291 | 0.01612 → **0.01326** |
| 2x dark standard | **webgpu** | 0.00410 → 0.00403 (−0.00007) | 0.00329 → 0.00329 | 0.01596 → **0.01301** |
| 1x light increased-contrast | webgpu | 0.00798 → 0.00793 | 0.00867 → 0.00862 | 0.02043 → 0.02042 |
| 1x light reduced-transparency | webgpu | 0.00173 → 0.00172 | 0.00111 → 0.00113 | 0.00343 → 0.00341 |
| 1x light standard | css | 0.00707 → 0.00699 | 0.00546 → 0.00544 | 0.01615 → 0.01581 |
| 2x light standard | css | 0.00737 → 0.00727 | 0.00566 → 0.00563 | 0.01654 → 0.01618 |
| 1x dark standard | css | 0.00682 → 0.00682 | 0.00362 → 0.00362 | 0.01999 → **0.01732** |
| 2x dark standard | css | 0.00699 → 0.00699 | 0.00401 → 0.00401 | 0.01992 → **0.01724** |
| 1x light increased-contrast | css | 0.01293 → 0.01300 (+0.00006) | 0.01524 → 0.01531 | 0.04531 → 0.04557 (+0.00025) |
| 1x light reduced-transparency | css | 0.00446 → 0.00442 | 0.00470 → 0.00473 | 0.00756 → 0.00752 |

The dark holdout's −0.0027 to −0.0030 on both tiers and both scales is G3's nested-pane fix arriving
in the matrix for the first time.

### 5.1 S1, evaluated row by row

**S1 would fire on zero rows.** Bounds: an untinted row worse than the W21 bed by more than 0.001 in
`oklabDeltaEMean` or 0.005 in `ssimMean`.

| row | most negative (better) | most positive (worse) | S1 |
| --- | --- | --- | --- |
| `oklabDeltaEMean` | −0.008537, 2x dark `checkerboard__glass-over-glass` (0.017586 → 0.009048) | **+0.000252**, 1x light increased-contrast `photo__rrect-lg` (0.045314 → 0.045565) | 0 rows |
| `ssimMean` | **−0.001787**, 1x light `photo__capsule-button__rest-tint-blue` (0.996378 → 0.994591) | +0.021467, 1x dark `checkerboard__glass-over-glass` (0.958614 → 0.980081) | 0 rows |
| `interiorMeanWeb` | −0.041724, 2x dark `dark-solid__rrect-md` (0.097608 → 0.055884) | +0.014693, 2x light `photo__glass-over-glass` (0.673856 → 0.688549) | — |
| `rimPeakLuminanceWeb` | −0.101271, 2x light `dark-solid__rrect-md` (0.152584 → 0.051313) | +0.004249, 1x light `light-solid__capsule-button` (0.000000 → 0.004249) | — |

The worst wrong-direction ΔE row is a quarter of S1's bound and the worst wrong-direction SSIM row a
third of it. **891 rows moved and 451 did not** over the six named rows and 229 cells;
`rimPeakDistanceWeb` moved on 13 (the peak's position; the band never moved it before, and it moves
now only where the peak statistic changes row).

### 5.2 The one stop that fires: S3, at the sixth decimal

**S3 fires on `1x-light-standard` / webgpu / calibration: 0.0032930 → 0.0033010, +0.0000080.** It is
the only GPU calibration column that is not flat or better; 2x light is −0.0000038, both dark
columns are −0.00007, and every CSS light column improves.

The +0.0000080 is two cells:

| cell | ΔE before → after | Δ |
| --- | --- | ---: |
| `dark-solid__rrect-md` | 0.0030416 → 0.0031518 | **+0.0001102** |
| `photo__capsule-button__rest-tint-blue` | 0.0010949 → 0.0011690 | +0.0000741 |
| `checkerboard__rrect-ml` | 0.0046520 → 0.0046838 | +0.0000318 |
| `checkerboard__toolbar-group` | 0.0023397 → 0.0023670 | +0.0000273 |
| `photo__rrect-ml` | 0.0231688 → 0.0231951 | +0.0000263 |
| eleven cells improve, worst −0.0000237 (`photo__capsule-button`) | | |

`dark-solid__rrect-md` is §4.3's cell — the light material's rim over a dark backdrop, the deferred
residual — and it carries the largest share. The movement is 1/125 of S1's own per-row bound.

**This is a stop as literally written and the ruling is the parent's.** What the gate can say: no
per-row bound is at risk, the 2x column of the same scheme improves, both dark columns improve, and
the driver is a cell the wave has already deferred by name.

### 5.3 S2 and S3-in-spirit (`stops.txt`)

- **S2, the tinted cells:** 60 tinted readings across both tiers, both schemes, both scales. **0 past
  the 0.002 stop.** Worst 0.00160 (`photo__capsule-button__rest-tint-orange-half`, CSS, both scales);
  worst on the GPU tier 0.00010.
- **The collapsed cells:** 20 readings, **every one moved by 0.00000**. The `impulse` and
  `dark-solid` capsules are byte-identical between the two beds on the GPU tier in both schemes
  (§6) — `present` scales the whole band term, so a material that has taken its backdrop's tone has
  no lit edge to lose.

---

## 6. Clause 6 — every capture against the canonical W21 bed, byte for byte (`byte-identity.txt`)

460 captures in both beds (a render and an `__alpha` conformance capture per cell per tier):
**176 identical, 284 moved.**

| group | moved | identical |
| --- | ---: | ---: |
| webgpu, render | 99 | 16 |
| webgpu, alpha | 99 | 16 |
| css, render | 81 | 34 |
| css, alpha | **5** | 110 |

**Clause 6 as the charter wrote it does not hold, and the reason is this gate's own constant.** The
charter expected the CSS tier byte-identical because the CSS tier draws no sweep — true of G0's
gate, and G0 verified it. It is not true of a `specularGain` fit: the CSS tier derives its interior
LEVEL from the same profile through `interiorBandLight`, whose term includes
`specularGain × specular`, so its level falls by 0.0013–0.0053 and its renders move. Every mover is
named:

- **81 CSS renders moved: the derived interior level.** The 34 that did not are exactly the cells
  where `present` is 0 — the whole dark bed's untinted cells (the dark patch has pinned
  `specularGain` 0 since W21, so the dark document's derived level never held the term) and every
  collapsed `dark-solid` / `impulse` capsule in the light scheme. The CSS light calibration ΔE
  improves at both scales (§5), so the movement is toward the reference.
- **4 of the 5 CSS alpha captures are the two stacked scenes** in both schemes — W22 G3's
  backdrop-stack fix, which landed after the canonical bed was built and is part of the frozen
  configuration (Decision Log 3 (c) predicted the light nested pane's CSS rows would recover
  0.056–0.069; §7 measures 0.0531–0.0669).
- **The fifth is `1x-light-increased-contrast / photo__toolbar-group__rest`**: 19 pixels of 64 000,
  max 4 code values in rgb and **1 in alpha**, in a 23 × 50 px box. Under the increased-contrast
  occlusion lift the interior alpha sits near the top of its range, and a 0.001-scale level change
  crosses one 8-bit step there. It is the derived level again, at the resolution of the encoding.
- **99 GPU renders moved** and 16 did not; the 16 are precisely the collapsed capsules
  (`dark-solid__capsule-button`, `impulse__capsule-button`, tinted and untinted) in both schemes and
  at both scales.

**S6 does not fire:** every moved CSS capture has a named mechanism.

---

## 7. The nested pane, per pane, at the corrected input (`stack.txt`, `stack-reads/`)

The first reading of these holdout cells against the reference. G0 could take none — both
`glass-over-glass` cells are holdout and X5 reserves the read for this gate — so its table had a
native column and the canonical W21 capture and no "after" at all.

**X3, re-validated on this gate's own run:** known levels injected into a copy of a capture and
recovered through the same masks and the same peak statistic — both bodies exact, eight rim peaks
within **0.000625**. The placement is asserted, not assumed: base 220 × 130 at (50, 35), overlay
120 × 56 at (100, 64).

`excess` = overlay body − base body.

| profile | tier | scene | native | before | after | \|after − native\| |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 1x dark | webgpu | `checkerboard__gog` | **−0.0260** | +0.0023 | **−0.0232** | 0.0028 |
| 2x dark | webgpu | `checkerboard__gog` | **−0.0267** | +0.0018 | **−0.0246** | 0.0021 |
| 1x dark | css | `checkerboard__gog` | −0.0260 | +0.0048 | **−0.0220** | 0.0040 |
| 2x dark | css | `checkerboard__gog` | −0.0267 | +0.0025 | **−0.0244** | 0.0023 |
| 1x light | webgpu | `checkerboard__gog` | +0.2371 | +0.2291 | +0.2292 | 0.0079 |
| 2x light | webgpu | `checkerboard__gog` | +0.2375 | +0.2252 | +0.2252 | 0.0123 |
| 1x light | webgpu | `photo__gog` | +0.2439 | +0.2423 | +0.2423 | 0.0016 |
| 2x light | webgpu | `photo__gog` | +0.2441 | +0.2421 | +0.2420 | 0.0021 |
| 1x light | css | `checkerboard__gog` | +0.2371 | +0.1784 | **+0.2341** | 0.0030 |
| 2x light | css | `checkerboard__gog` | +0.2375 | +0.1766 | **+0.2297** | 0.0078 |
| 1x light | css | `photo__gog` | +0.2439 | +0.1861 | **+0.2517** | 0.0078 |
| 2x light | css | `photo__gog` | +0.2441 | +0.1866 | **+0.2535** | 0.0094 |

**The sign agrees with the reference on all twelve rows.** The dark inversion the user's eye found
is gone on both tiers and both scales, and the overlay now sits 0.0021–0.0040 from the reference's
own excess where it sat 0.028 the wrong side of it. The light CSS rows recovered **0.0531–0.0669**,
inside Decision Log 3 (c)'s predicted 0.056–0.069. The light GPU rows do not move (≤0.0001), as
predicted. The base pane is right to 0.0001–0.0013 in dark and 0.0035–0.0207 in light.

The base pane's haze is unchanged and remains the thick-span composite's: the whole-region σ match
reads native 16.00 (the search ceiling) against web 8.00 at 2x dark and 16.00 against 7.50 / 12.75 in
light — G0's numbers, reproduced.

**The four W21 instrument floors on the 2x dark nested pane, re-read** (the first gate that could):

| tier | row | floor | W21 measured | this run | verdict |
| --- | --- | ---: | ---: | ---: | --- |
| texture | `silhouetteIoU` | ≥ 0.9257 | 0.92673 | **0.92732** | held |
| dom | `silhouetteIoU` | ≥ 0.9038 | 0.90482 | **0.90493** | held |
| dom | `contourDistanceMean` | ≤ 1.8602 | 1.76018 | 1.76018 | held |
| dom | `contourDistanceP95` | ≤ 13.1 | 13.0 | 13.0 | held |

Two improve slightly, two are bit-identical; none goes inert. G2 re-reads them at the landing.

---

## 8. The gate over the full scratch matrix

`adopted-thresholds.test.ts` with `VITREA_MATRIX_PATH` on this gate's own matrix — both tiers, all
six profiles, all three sets, 229 cells. **31 of 33 pass; 2 fail, and both are the same fact.**

```
× gates the texture-tier apple-macos-26.5-2x-light-standard cells against TEXTURE_TIER_2X_LIGHT
  texture / silhouetteIoU: the gate must cover every applicable cell:
  expected [ … ] to have a length of 29 but got 33
× machine-checks the well-conditioned predicate and names every cell it excludes
  expected [ …(29) ] to deeply equal [ …(33) ]
```

**`PREDICATE_EXCLUDES` re-derives to 29 lines, four fewer.** Four 2x light-standard texture cells the
conditioning predicate used to refuse are now well-conditioned:

```
texture / calibration / checkerboard__rrect-md__rest   / apple-macos-26.5-2x-light-standard
texture / calibration / checkerboard__rrect-ml__rest   / apple-macos-26.5-2x-light-standard
texture / holdout     / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-light-standard
texture / holdout     / checkerboard__rrect-lg__rest   / apple-macos-26.5-2x-light-standard
```

The reason is measurable. The resting specular band was fragmenting the 2x light silhouette, and the
predicate refuses a mask in pieces:

| cell | bodies before → after | holes | IoU before → after | contour mean before → after | P95 |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__rrect-md` | 2 → **1** | 0 → 0 | 0.99792 → 0.99953 | 0.1335 → 0.0302 | 1 → 0 |
| `checkerboard__rrect-ml` | 3 → **1** | 0 → 0 | 0.99861 → 0.99981 | 0.1202 → 0.0164 | 1 → 0 |
| `checkerboard__glass-over-glass` | 3 → **1** | 4 → **0** | 0.99750 → 0.99803 | 0.1068 → 0.0031 | 1 → 0 |
| `checkerboard__rrect-lg` | 4 → **1** | 0 → 0 | 0.99885 → 0.99993 | 0.1199 → 0.0075 | 1 → 0 |

**With those four lines removed, the gate passes 33 of 33** (verified by running it, then reverting
the edit — the file is untouched in the commit, because `pnpm -r test` runs it against the CANONICAL
matrix, which still carries the old rows until G2 rebuilds).

- **`UNMET_ROWS` stays 11.** No floor goes inert; the four W21 floors hold (§7); the floors test is
  green.
- **No adopted bound was widened and none is at risk.** The four newly gated cells meet every bound
  they now carry, with room.
- **The gate got stricter, not looser.** Four cells that could not be read now are.
- **The dom-tier `interiorLevelRatioGpuOverCss` identity check passes**, which is the failure G0 saw
  on a merged matrix and the reason this run captured both tiers together.

**G2's edit list, from this run:** remove the four `PREDICATE_EXCLUDES` lines above; leave
`UNMET_ROWS` at 11; re-read the four W21 floors' `measured` values (two moved: 0.92673 → 0.92732 and
0.90482 → 0.90493).

---

## 9. `lightDirection` declined — the shadow rows read beside it (`shadow-rows.txt`)

Decision Log 2 (b) declines `lightDirection` on the rim rows and asks for the shadow rows before the
number is touched, because the direction feeds the inner shadow through `platform-web`'s `light.xy`
and the matrix's shadow axis is where it would show. The direction did not move this wave, and the
reading says the rows agree with that.

The matrix carries no field named `shadowPeakDarkening`, `shadowPeakDistance` or
`shadowDecayLength`; those are the charter's words for schema 5's `strengthPeakWeb`,
`strengthPeakDistanceWeb` and `falloffLengthWeb`, read here under their real names.

**The direction-carrying rows are unmoved on every one of the 229 cells:** `offsetXWeb`,
`offsetYWeb`, `extentAboveWeb`, `extentBelowWeb`, `extentLeftWeb`, `extentRightWeb`. The shadow's
placement and its four reaches are bit-identical to the W21 bed's.

What did move, and why: the rows whose sample sits just outside the contour, where the rim's own
blur shoulder reaches.

| row | cells moved (of 229) | largest \|Δ\| |
| --- | ---: | ---: |
| `strengthPeakWeb` | 71 | 0.014125 |
| `falloffLengthWeb` | 67 | 0.286281 |
| `falloffSigmaWeb` | 67 | 0.223435 |
| `falloffAmplitudeWeb` | 67 | 0.002078 |
| `meanDepartureWeb` | 176 | 0.000054 |
| `strengthPeakDistanceWeb` | **3** | 5.0 |
| `centroidOffsetXWeb` / `YWeb` | — | 0.944 / 0.276 |

`strengthPeakDistanceWeb`'s three movers all go **to 0**: `1x light checkerboard__toolbar-group` and
`1x light light-solid__rrect-ml` 1 → 0, and `2x light hc-text__capsule-button__rest-tint-orange`
5 → 0. The exterior peak now sits at the contour rather than a few pixels out, which is the same
brightening of the contour the rim rows report. The shadow axis is not gated (claims §5's own note),
so none of this crosses a bound.

---

## 10. By eye (X6), before the user's

The sheets are `../sheets/g1-1x.png` and `../sheets/g1-2x.png` — native | GPU before | GPU after |
CSS after, thirteen rows each (every untinted solid in both schemes, both stacked scenes in both
schemes, the dark `impulse` capsule), whole canvas, zoom 2 at 1x and 1 at 2x. Both sent to the
MacBook by Taildrop: **g1-1x.png 521 920 bytes, g1-2x.png 1 035 849 bytes.**

What this gate sees in them:

- **The dark nested pane.** Native draws an overlay darker than its base; the before column draws it
  lighter; the after column and the CSS column both draw it darker. The inversion the user's eye
  found is gone, and it is gone on both tiers.
- **The resting band.** In the before column a bright vertical band sits on the left edge of every
  surface on both beds — clearest on the dark `mid-dark-solid` capsule and on the nested pane's base.
  It is absent from every after panel.
- **`dark-solid__rrect-md` in light** is the one cell where the after column is not simply closer.
  Native draws a bright ring on top AND bottom; the before column drew a bright top and a dark
  bottom; the after column is symmetric and uniformly dimmer than native. It reads as a more
  coherent surface with a rim that is too faint — which is exactly the deferred residual, and is why
  §4.3's one newly missed side is worth recording rather than hiding.
- **The dark `impulse` capsule** is unchanged and still flat where Apple's passes a glow and draws a
  ring. That is Decision Log 2 (d)'s charter, not a regression, and it is on the sheet so the user
  can see what was chartered.

**S7 is the user's and is open.**

---

## 11. The stops, dispositioned

| stop | what it says | reading | verdict |
| --- | --- | --- | --- |
| **S1** | any untinted row worse than the W21 bed by > 0.001 ΔE or > 0.005 `ssimMean` | worst wrong-direction ΔE **+0.000252**, worst `ssimMean` **−0.001787** | **does not fire** |
| **S2** | any tinted cell moved by more than 0.002 in body | 60 readings, worst **0.00160** (CSS), 0.00010 (GPU) | **does not fire** |
| **S3** | a light or dark calibration ΔE mean above the W21 bed's | 1x light standard / webgpu / calibration **0.0032930 → 0.0033010 (+0.0000080)**; every other GPU calibration column flat or better | **FIRES — the parent rules** |
| **S4** | a golden moved — the attribution failed | ten moved, the attribution held exactly (one tree, one seam constant, band ≤ 2.24 px, upper share ≥ 0.98, control 0 / 96 000) | **does not fire** |
| **S5** | a fitted constant whose rows do not separate it | 11 of 20 contrast rows separate above the 0.000625 floor; every one minimises at 0 | **does not fire** |
| **S6** | a CSS capture moved without an explanation | 81 renders + 5 alpha moved; the derived interior level, G3's stacked scenes, and one 19-px encoding step, each named | **does not fire** |
| **S7** | the user's eye | sheets sent | **open** |

---

## 12. Gaps, blocks and notes for the ledger

1. **S3's +0.0000080** (§5.2). The only stop that fires, on the 1x light GPU calibration column, at
   the sixth decimal, driven by a cell the wave has already deferred. The ruling is the parent's;
   this gate recommends taking it, with the number in the claims section rather than smoothed away.
2. **A new open side:** `light 1x impulse__rrect-md` top, +0.0242 → −0.0898 (§4.3). Same term as the
   deferred collapsed rim in light; recorded so the count of that residual's cells is right.
3. **The collapsed rim in light is three cells, not one.** `dark-solid__rrect-md`,
   `impulse__rrect-md` and `mid-dark-solid__capsule-button`, at both scales, 18 sides missing clause
   2 by 0.031–0.093. Two of the three could not be read before this gate opened the holdout and the
   validation set. The spec's Deferred entry names one cell and should name three.
4. **Clause 6's wording is wrong for a material fit** (§6). "The CSS tier has no sweep, so its
   captures are expected byte-identical" is true of a sweep gate and false of anything that moves
   `interiorBandLight`'s arguments. The clause's intent — every CSS mover explained — is met.
5. **`PREDICATE_EXCLUDES` loses four lines and the gate gets stricter** (§8). G2's edit; the four
   cells' before/after silhouette bodies are recorded above so the reason is attributable.
6. **The CSS tier under increased contrast is 0.00006–0.00025 worse in ΔE** (§5) while its GPU twin
   improves. Small, one profile, the CSS tier only; a CSS-only residual for the ledger, not a
   charter.
7. **`1x-light-increased-contrast / css / holdout` exits 1 on `hc-text__capsule-button__rest`**
   (§3), pre-existing and reproducible from the canonical bed. Not this gate's, and G2 will see it.
8. **The fit could not use `mid-dark-solid`.** It is holdout, X5 reserves the one read for the dry
   run, and the ladder is therefore fitted on five calibration cells. The cell was read once,
   afterwards, and agrees: `L−R` +0.0523 → +0.0000 with the left within 0.0005 of the reference.
9. **The `clear` variant is unfitted and stays that way.** No scene on the bed declares it; recorded
   in the profile and the code rather than left silent.

---

## 13. Recommendation for the landing

Land it. The constant is fitted on rows that separate it, agrees across scales and contrasts,
closes W21's two open cells outright, nets four met sides on the GPU tier, improves every dark
column and both CSS light columns, moves no floor, widens no bound, and makes the gate cover four
more cells than it could before. The one stop that fires does so at the sixth decimal on a column
whose driver is an already-deferred cell.

For G2: rebuild from the main checkout with `rm results/matrix.json` first (the light document's
hash moves, so a cell's key moves with it), both tiers, all six profiles, `--alpha --write-partial`,
calibration and validation before the holdout; referee every capture against `g1-digests.txt` byte
for byte; remove the four `PREDICATE_EXCLUDES` lines of §8; re-read the four W21 floors' measured
values; the changeset is a `@vitreajs/vitrea-web` minor (0.11.0).

---

## 14. Files

| file | what |
| --- | --- |
| `g1-ladder-capture.sh` | the eight-point ladder on the light bed, both scales, to scratch |
| `run-ladder-reads.sh`, `ladder-reads/` | the ladder read under the declared geometry |
| `fit-specular.py`, `fit-specular.txt` | §1 — the fit, per contrast |
| `attribute-w22-goldens.py`, `goldens-attribution.txt` | §2 — the goldens' attribution |
| `g1-dryrun-run.sh` | §3 — the dry run, six profiles, both tiers, the holdout once |
| `g1-digests.py`, `g1-digests.txt` | §3 — the bytes G2 must reproduce, and both documents' digests |
| `read-canonical.sh`, `canonical-reads/` | the declared-geometry reads, before and after, both tiers |
| `g1-clauses.py`, `g1-clauses.txt` | §4 — clause 2 per side, and what moved across it |
| `delta-e.py`, `delta-e.txt` | §5 — ΔE per profile, per set, per tier |
| `moved-rows.txt` | §5 — every moved row and S1 (produced by `../g0/moved-rows.py`, whose banner names G0 because the script is G0's; the numbers are this gate's) |
| `stops.py`, `stops.txt` | §5.3, §7 — S2, the collapsed cells, the four W21 floors |
| `byte-identity.py`, `byte-identity.txt` | §6 — every capture against the canonical bed |
| `run-stack.sh`, `stack-tables.py`, `stack.txt`, `stack-reads/` | §7 — the nested pane per pane, with X3's injection |
| `shadow-rows.py`, `shadow-rows.txt` | §9 — the shadow rows beside `lightDirection`'s declination |
| `../sheets/make-sheet.py`, `../sheets/g1-{1x,2x}.png` | §10 — the by-eye sheets |
