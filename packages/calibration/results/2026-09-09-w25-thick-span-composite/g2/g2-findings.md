# W25 G2 — the three mechanisms landed inert, and the fit on what the 1x rows identify

Findings, 2026-09-09. The mechanisms are in the code at their defaults, the fits are on scratch, and
the profile documents carry no fitted value: G3 declares. Nothing under `scenes.json`, `fixtures/`,
the canonical `results/matrix.json` or the canonical `web-captures/` was written (X2); every rung of
the ladder rendered into `/Users/new/.claude/jobs/5c70e47f/tmp/w25/g2/` through `capture:web` with
`--out` pointed there.

Files beside this one, each stating what it reads and in which unit: `ladder.sh` (the ladder),
`rows.py` / `rows.json` (span and backdrop level per row), `predict.mjs` with `share-lever.txt`,
`levers.txt` / `levers.json` and `rides.txt` (the analytic levers, through the renderer's own
functions), `read-rung.py` (one rung read by G0's instruments), `fit.py` with `fit-share.txt`,
`fit-level.txt` and `fit-field.txt`, `deltae.py` / `deltae.txt` (OKLab ΔE per cell per rung),
`condition.txt`, `thin-invariance.txt` and `goldens-attribution.txt`. `rung-r0.json` and
`rung-rF.json` are the machine-readable reads behind the baseline and the confirmation — every
width, level and along-side row of the four 1x beds, native and web; the six intermediate rungs
live only in scratch and their numbers are in the fit tables.

Units: sigmas in **device px** (every bed this child read is scale 1, so device and CSS px coincide);
levels in linear Rec.709 luma with differences in 8-bit display codes; ΔE is OKLab, the matrix's own
`oklabDeltaEMean` over the declared component region.

---

## 0. The headline, in seven sentences

1. **The three mechanisms are in the code and they draw nothing.** 33 of 33 renderer goldens pass
   with no golden byte changed, and rung `r0` re-rendered the canonical 1x light and dark beds
   through the committed profiles into scratch: 36 of 36 captures that have a canonical sibling are
   **byte-identical** to the 0.13.0 bed.
2. **The share law reaches the reference's share.** Reader A on `impulse__rrect-md` at 1x reads the
   heavy share 0.233 at the default and **0.434 at a lift of 0.455** against the reference's 0.473 —
   inside clause 2's re-declared bound of 0.05 — with the fitted heavy width rising 9.08 → 13.29
   device px against the reference's 19.52.
3. **The along-side field is the wave's cleanest result.** One constant fitted on 64 straight sides
   gives opposite sides slopes that agree to 0.002 and 0.001 — the antisymmetry the reference has and
   a field linear in position cannot — and at slope 0.45 the corner-to-corner range goes from 0.227
   of the reference's to **0.743**, with the rows asking for no further slope (median residual
   −0.004).
4. **The level term's chartered SHAPE is refuted by its own rows and re-formed.** Decision Log 3 (b)
   put it on the tone response's thin-to-thick blend; measured on the rows above the knee that form
   explains 0.3 % of the residual with the two grids disagreeing in sign. An OFFSET on the response's
   settled level explains 39 % of it on the grid that identifies it, and that is the form that ships.
5. **The level term is scheme-separated, and not in the direction X7 assumes.** The W9 light grid
   fits it at 0.029 encoded and falls 1.486 → 0.977 codes RMS; the W21 dark grid fits it at ~0.001
   and is made 2.5 codes worse by the light grid's value. The dark document has to pin it to 0.
6. **X5 held at every rung.** Worst thin-cell movement 0.000196 ΔE against a stop of 0.001, and
   exactly 0.000000 on all 21 `rrect-sm` cells at every rung. The four laws that ride `sizeThickness`
   are unmoved at any value of any of the three constants.
7. **The mechanisms cost ΔE where they close structure, and that tension is G3's to rule.** At the
   fitted values the canonical 1x beds' mean ΔE rises +0.00042 and the probe grids' +0.00224, against
   parent clause 6's +0.0001; the measured reason is that vitrea's heavy component is 13.3 device px
   at the reference's own share where the reference's is 19.5, so a share of the right size is being
   drawn through a kernel of the wrong width.

---

## 1. What is in the code, and where each mechanism sits

| mechanism | constant | slot | inert because |
| --- | --- | --- | --- |
| the share law | `sizeScatterHeavyShareThick1x` / `…2x` | `scatterDeepThickness`'s `kDeep`, `+ lift · sizeThickness(span)`; shader `ou.thickSpan.x * sizeThick` | `0.0 · x` added to a value already in `[floor, 1]`, under a clamp that is the identity there |
| the level above the knee | `sizeToneLevelFar` | `backdropToneResponse`'s RETURN, `+ levelFar`; shader `tone_response(…, toneLevelFar)` | `sizeToneLevelFar` resolves to `0` at every span, and `+ 0.0` is bit-exact |
| the along-side field | `optics.*.rimAlongSideSlope` | the rim's amplitude, `rw * lit * alongFactor * (…)`; shader `ou.rimLit.w` | `max(1 + 0.0·…, 0)` is exactly `1.0`, and `x * 1.0 == x` |

**The share law's form, and why the thin end stays (X5).** The existing curve is kept whole and the
constant is the thick end's LIFT above it:

```
kDeep(span, dpr) = floor(dpr) + (1 − floor(dpr)) · smoothstep(sizeSpanMin, sizeScatterSpanMax(dpr), span)
                 + heavyShareThick(dpr) · sizeThickness(span)
```

`sizeScatterFloor`, `sizeScatterSpanMax` and the three 1x ramp anchors are **not re-derived**: they
stay as the law's thin end. That is the answer to "say which, and why the thin capsule cannot move".
`sizeThickness` is exactly 0 at and below `sizeSpanMin`, so `rrect-sm` and everything smaller is
bit-identical at any lift, and the capsule at span 44 takes 0.0923 of it — the thin end's whole
exposure, measured at 0.000196 ΔE worst.

**The sharp σ per scale.** The wave asked for it as a named constant. G2's answer is that at 1x it
already is one — `optics.regular.blurSigma`, 1.25 CSS px — and that this wave may not move it. The
reference's own sharp component is **2.62 device px on the collapsed capsule against 2.79 on the
thick rrect** (G0 `widths.txt` Table 1), span-flat to 6 %: there is no thick-only sharp width to
fit, so a sharp constant riding `sizeThickness` would be a constant the reference does not have, and
the shared one is the thin capsule's own width. The second-scale anchor a `blurSigma2x` sibling would
carry has no fixture that identifies it either (§4), so it is not added: a field nothing can fit is
not carried (C9a §6.2). The gap is recorded, not closed — vitrea's sharp component reads 1.67 device
px against the reference's 2.79 at every rung of this ladder, and it does not move.

**The level term's form.** `R(x, span) = R₀(x, sizeK) + sizeToneLevelFar · smoothstep(sizeSpanMax,
sizeScatterSpanMax(dpr), span)`, folded with `sizeK`. It enters the **tone response's own output** —
the law that owns the interior mean (claims §5.33) — and not the blur, not a gain on the mix. §3
below is why it is an offset on the response rather than a continuation of its blend.

**The field's form, and the one place this child diverges from its brief.** The dispatch specified
`1 + slope · sizeThickness · (position along the diagonal, normalised to the surface's half-diagonal)`.
That is a field LINEAR in position, and a linear field gives the top and the bottom side the SAME
slope in x. G0's reader measured them **equal and opposite** — top −0.000192 against bottom +0.000192,
left −0.000379 against right +0.000379 on the 1x dark `dark-solid__rrect-md` — and the reader indexes
each side by image coordinates, not by a traversal around the contour, so the antisymmetry is in the
field and not in the parametrisation. The field that has it is the product of the two normalised
coordinates:

```
alongSide = (x / halfWidth) · (y / halfHeight)          +1 at top-left and bottom-right,
                                                        −1 at the other two, 0 through both axes
factor    = max(1 + rimAlongSideSlope · sizeThickness(span) · alongSide, 0)
```

which is +1 at exactly the corners the reference draws brightest — the same diagonal `rimLitAxis` is
symmetric about, so this is the POSITION half of the light whose DIRECTION half W24 landed, not a
second light. It keeps every clause of the brief: one constant for the slope, riding `sizeThickness`,
zero by default, zero on `rrect-sm` by construction, and W24's lit-edge factor untouched beside it.
The rendered fit then confirmed the form rather than assuming it (§4): opposite sides agree to 0.002.

---

## 2. The share law, fitted (`fit-share.txt`, `condition.txt` §1)

**The condition first.** The heavy share is read by one instrument — reader A, the dot's
two-component PSF — and one backdrop can carry it. On the canonical bed at 1x that is
`impulse__rrect-md` (span 96) and `impulse__capsule-button` (span 44, collapsed, share 0.000 on both
sides, no lever). **One row identifies the 1x share, and it is a validation row.** This is G0 §6's
finding 3 arriving in practice; G1's probe set at both scales is what takes it to 44 rows at five
spans.

**The ladder.** Reader A on `impulse__rrect-md` at 1x, native `2.79 / 19.52 / 0.473`:

| rung | lift | sharp | heavy | share | canonical ΔE vs r0 | grids ΔE vs r0 |
| --- | --- | --- | --- | --- | --- | --- |
| r0 | 0.00 | 1.67 | 9.08 | 0.233 | +0.00000 | +0.00000 |
| rA | 0.24 | 1.68 | 11.76 | 0.325 | −0.00001 | +0.00029 |
| rE | 0.30 | 1.66 | 12.34 | 0.363 | +0.00008 | +0.00044 |
| rB | 0.48 | 1.64 | 15.22 | 0.491 | +0.00041 | +0.00087 |
| **rF** | **0.455** (with the other two) | 1.67 | 13.29 | **0.434** | +0.00042 | +0.00224 |

**The fitted 1x lift is 0.455**, which lands the share at 0.434 against the reference's 0.473 — a
miss of 0.039 inside clause 2's 0.05. The lever is 0.38 share per unit lift near zero and 0.71 near
0.48; the constant is well conditioned in the sense that the quantity moves and badly conditioned in
the sense that one row says so.

**The check off its own rows, and it does not agree.** Reader C's single-Gaussian width over the two
probe grids' structured backdrops runs the other way: the objective (mean |log σ_web/σ_native| over
the thick in-bound rows) is 0.2507 at lift 0, 0.2625 at 0.24, 0.2694 at 0.30, 0.2769 at 0.48. G0
named the reason before the fit ran (§2c): a single-Gaussian width at one pitch is a true reading of
a DIFFERENT PART of a two-component kernel. Raising the share of a too-narrow heavy component adds
structure the reference does not have, and vitrea's heavy component is 13.3 device px at the
reference's own share where the reference's is **19.5**.

**The diagnostic rung, and it settles the obvious next move — negatively.** Rung `rG` carried the
same lift with `sizeScatterGainMax` raised 8 → 10.3, the value that should have taken the heavy
component from 15.2 to 19.5 through the mix's own arithmetic. Reader A read the heavy at **13.29 —
the same number rung rF reads at gain 8**, and the width objective moved from 0.2769 to 0.2768. The
1x heavy width is not a clean lever on `sizeScatterGainMax` because the heavy tap is a mip-chain
level and its effective width does not follow the gain there. That is a finding for the tracker, not
a fix this wave can make, and it is why the wave's own charter to raise the share leaves a residual
the width readers can see.

**The 2x anchor stays at 0 and no row on this bed could move it.** At dpr 2 `sizeScatterFloor2x` is
1, so `kDeep` is already saturated at every span and the lift is clamped away whatever it says; and
G0 §6 finding 1 records that every 2x row that identifies a width is at span 32, 44 or 96. The 2x
share waits for G1's fixtures, exactly as Decision Log 3 (f) anticipated.

---

## 3. The level term above the knee: the chartered shape refuted, and the one the rows chose (`fit-level.txt`)

**The control, first, because it is what made the probe safe.** 77 rows at or below span 96 have a
**rendered lever of 0.000000 codes per unit** — not small, zero to the precision the reader prints.
No value of this constant can move the bed the rest of the material was fitted on.

**The chartered form loses on its own rows.** Decision Log 3 (b) put the term on the tone response's
thin-to-thick BLEND, reasoning that G0's residual "has the shape of the thin-to-thick step continued:
its sign follows the backdrop". Rung `rC` rendered that form at gain 1 and measured it:

| form | rows | joint least-squares gain | RMS before → after | per-row gains |
| --- | --- | --- | --- | --- |
| the blend continued (`rC`) | 31 | −0.0289 | 2.034 → 2.027 codes | −1.13 … +0.24, sd 1.05 |
| an offset on the level (`rC2`) | 31 | +0.0994 (of 0.02) | 1.965 → 1.945 codes | −0.68 … +1.38 |
| an offset, W9 light grid only | 14 | +1.4716 (of 0.02) | 1.486 → **0.977** codes | median +0.909 |

**Why the charter's reading did not survive contact with the rows.** G0's "the sign follows the
backdrop" is a reading of the REFERENCE's absolute grading above 96. What a term has to close is the
residual AGAINST vitrea, and vitrea's own deep value keeps rising to `sizeScatterSpanMax` = 256 over
exactly those spans, so the two gradings largely cancel. What is left is close to
backdrop-independent: `resid(160) − resid(96)` on the W9 light grid reads +3.4 / +2.2 / +3.8 / +4.0 /
+4.2 / +4.2 / +3.8 / +2.6 codes over `checkerboard` at three pitches, `dark-solid`, `hc-text` at two
pitches, `mid-dark-solid` and `photo` — backdrops spanning 0.012 to 0.89 linear — and −0.2 on
`light-solid`. A term whose direction is different at every backdrop level cannot draw that; an
offset can. **The mechanism keeps its charter (one constant, zero by default, exactly zero at and
below `sizeSpanMax`, entering the tone/level composite and not the blur) and changes its shape to the
one the rows identify.**

**The fitted value, and the scheme separation.** `sizeToneLevelFar` = **0.029** in the response's
encoded units, from the W9 light grid's 14 rows, which fall 1.486 → 0.977 codes RMS at it. The W21
dark grid fits ~0.001 and its 14 rows do not move (2.469 → 2.462); rendered at 0.029 in rung `rF`
they get **worse by 2.5 codes RMS**. That is a real separation and not merely an absence of
information, and the reason is G0 §5's: the dark grid's whole collapsed-to-uncollapsed contrast is
six 8-bit codes where the light grid's is a hundred. **X7's ruling on the evidence: the constant
lands on the light material and the dark difference document pins it to 0.** The alternative — hold
the whole term at 0 and record the residual — is stated for G3 below.

Rendered at rF: on the W9 grid the above-knee residual falls 1.486 → 0.977 codes RMS with its mean
moving +0.862 → −0.179; over all beds jointly it rises 1.965 → 4.130, entirely from the dark grid
carrying a light-scheme constant; at or below span 96 it is unchanged (8.857 → 8.863, and that +0.006
is the share law at span 96, not this term).

---

## 4. The along-side field, fitted (`fit-field.txt`)

**64 rows, and the reference's antisymmetry reproduced by one constant.** Every straight side of every
thick cell over a flat solid asks `(native − web₀) / (web₁ − web₀)` — the renderer supplies the
derivative, so no model of the rim's amplitude enters the fit:

```
implied slope over 64 thick sides: median +0.452, mean +0.393, sd 0.235, quartiles +0.247 … +0.597
lever-weighted mean +0.437

  top    n=16 median +0.404        bottom n=16 median +0.402
  left   n=16 median +0.470        right  n=16 median +0.469
```

Opposite sides agree to **0.002 and 0.001**. That is the form validated, not assumed: one field with
one constant reproduces four slopes that a field linear in position could not. The 17 % between the
top/bottom pair and the left/right pair is the box's own aspect — the product form predicts
160/96 = 1.67 for the ratio G0 measured at 1.97, where a metric half-diagonal would have predicted
1.0 — and it is the residual the form leaves.

**The fitted slope is 0.45.** At it, rendered in rung `rF`:

- the corner-to-corner range on the 64 thick sides goes from **0.227** of the reference's to
  **0.743** (medians), and the rows within 20 % of the reference's range go from **2 of 64 to 27**;
- the rows ask for no further slope: re-running the fit with `rF` as the baseline gives a median
  implied residual of **−0.004**, against +0.452 at the default;
- the thin controls move 0.000029 luma per CSS px at span 44 and 0.000000 at span 32.

**Clause (c)'s bound is not met on every row and the miss is honest.** Decision Log 3 (c) asks for the
range within 20 % on the thick solids; 27 of 64 sides reach it and the median lands at 0.743 of the
reference. What the constant closes is the SHAPE — the grading exists, is antisymmetric and sits on
the right diagonal — and what it does not close is the last quarter of the amplitude, which would need
the rim's own amplitude law to move with it. That is recorded, not chartered.

**What the CSS tier carries, and X8's residual.** Nothing, and the reason is exact: the field is odd
under `x → −x` and under `y → −y`, so its integral around the whole contour — straight runs and corner
arcs alike — is zero. `interiorBandLight` integrates the renderer's band, and a term integrating to
zero adds nothing to integrate, so the two tiers' derived interior level is the same number with the
field and without it at every span and every slope. That is why the mirror does NOT gain a
`rimAlongSideSlope` field (a constant nothing reads is not carried, C9a §6.2), and it is written into
`platform-web/src/optics.ts` beside `rimLitExponent`, which IS mirrored precisely because it does not
integrate to zero. **X8's residual is the FEATURE**: the CSS tier draws one inset shadow with one
alpha the whole way round and cannot make a rim brighter at two corners than at the other two.

---

## 5. The four laws that ride `sizeThickness` (`rides.txt`)

Unmoved, at any value of any of the three constants, and the statement is structural rather than
lucky: W25 does not touch `sizeSpanMin`, `sizeSpanMax` or the knee — G0 answered clause 4 in the
landed law's favour — and each mechanism ADDS a term riding the curve rather than re-expressing it.
`predict.mjs rides` evaluates the four at the landed material and at a material with all three
constants set to 1, and every pair is equal to the last digit printed at every span of the bed. The
rendered check is `deltae.txt`: the thin cells the lens, the occlusion and the inner shadow were
fitted on move 0.000000 at span 32 and at most 0.000196 at span 44 at every rung.

---

## 6. What the 2x rows on disk did and did not identify

**They identified nothing this wave can fit.** Every 2x constant stays at its inert default, and the
reasons are three and each is a measurement:

1. `sizeScatterHeavyShareThick2x` — at dpr 2 `sizeScatterFloor2x` is 1, so `kDeep` is 1 at every span
   before the lift is added and the clamp absorbs it entirely. The constant is arithmetically inert
   at that ratio on the landed material, whatever it says.
2. The 2x width above span 96 — G0 §6 finding 1: every 2x row that identifies a width is at span 32,
   44 or 96; `checkerboard__rrect-ml` and `-lg` at 2x read 16.50 and 19.00, past reader C's bound,
   and reader B saturates at 7.3 there. Neither bed shape (i) nor (ii) buys it; shape (iii+) does.
3. A `blurSigma2x` sibling for the sharp σ — the same absence. The reference's sharp component halves
   in device px between the scales (2.79 → 1.40) where vitrea's runs the other way (1.67 → 3.51), so
   the second anchor is a real quantity; but the rows that would fit it are the 2x coarse
   checkerboards, which exist in neither grid and in no profile. The field is not added rather than
   added and left at a value nothing chose.

All three are the same sentence in the end, and it is Decision Log 3 (e)'s: **the grids at both
scales with coarse structured backdrops are the only fixture that identifies the 2x thick material**,
and G1's sitting is what produces it.

---

## 7. The constants G3 would declare, and the fingerprints they would give

The profile documents carry **no fitted value** — G3 declares — but the shape moved, so both
documents' `resolvedMaterialSha256` is re-recorded here with the reason in their `$comment-w25`:

| document | at 0.13.0 | **now (three inert keys)** | at G2's fitted values |
| --- | --- | --- | --- |
| `apple-macos-26.5-1x-light-standard` | `7968a7f8106b10a4` | **`52a633135b9da151`** | `c7c46e69d420a5f4` |
| `apple-macos-26.5-1x-dark-standard` | `0d741cd19cd1243b` | **`2f47777637f8df50`** | `e7f0ccc3b0047046` |

The fitted-value column is over the light patch carrying
`sizeScatterHeavyShareThick1x` 0.455, `sizeToneLevelFar` 0.029 and
`optics.regular.rimAlongSideSlope` 0.45, and the dark patch carrying the same two material constants
with `sizeToneLevelFar` pinned to **0** (§3). Both are computed by the same digest
`tuned-profiles.test.ts` pins, so G3 can check its own declaration against them.

`tuned-profiles.test.ts` records the fingerprint move and says why the three constants are
deliberately absent from `FITTED_CONSTANTS`: no measurement has chosen a value that ships, and the
patch rightly does not name one until G3's declaration.

---

## 8. The chain, and the one thing that is pending

- `pnpm -r build && pnpm -r lint && pnpm -r test` — **green** (renderer 24 files / 420 tests, of which 18 are
  `thick-span.test.ts`; platform-web 33 / 453; calibration 20 / 281, tier coherence 45).
- The renderer's golden suite — **33 of 33, in the foreground, no golden byte changed**, and rung
  `r0`'s canonical captures byte-identical to the 0.13.0 bed (26 of 26 light, 10 of 10 dark).
- **PENDING, and it is one command.** The golden run above was taken before §3's re-form of the level
  term, which moved `+ levelFar` from `tone_response`'s blend to its return. On the shipped material
  `sizeToneLevelFar` resolves to 0 at every span and every ratio, so the change is `+ 0.0` and the
  CPU mirror is pinned bit-exactly by `thick-span.test.ts`'s "leaves the tone response BIT-identical
  at every span on the shipped material" (8 backdrop levels × 4 thicknesses × 11 spans × 4 ratios,
  `toBe`). The WGSL cannot be pinned that way without a GPU, and the parent's sitting holds every
  capture, so the re-run is deferred:

  ```
  cd packages/renderer-webgpu && npx playwright test --grep @golden
  ```

  It is the first thing G3 should run, and this child's expectation, stated before the run, is 33 of
  33 with no golden byte changed.

---

## 9. What G3 has to rule, and what this child recommends

**(a) The share law's landing is a trade between two of the parent's own clauses.** Clause 2 asks for
the share within 0.05 of the reference, which needs a lift of at least ≈ 0.39. Clause 6 asks that the
calibration ΔE mean not rise by more than 0.0001, which caps the lift at ≈ 0.31 on this child's read
of the canonical 1x beds (rA at 0.24 is −0.00001, rE at 0.30 is +0.00008, rB at 0.48 is +0.00041).
The window is empty. **Recommendation: land 0.455 and take the ΔE.** The reason is the wave's own
purpose — Decision Log 3 (a) ruled that "the wave's mechanism is the heavy share", and a share fitted
to the bound of an aggregate metric rather than to the quantity it exists for is the failure mode
claims §5.113 was written to prevent. The cost should be recorded as a claim, and the metric that
carries it is not perceptual noise: it is the too-narrow heavy component (§2), which is the next
wave's constant.

**(b) The level term is scheme-separated.** Recommendation: `sizeToneLevelFar` 0.029 on the light
material with the dark document pinning 0. The fallback, if G3 would rather not carry a
scheme-dependent thick constant on one grid's evidence, is to hold it at 0 and record the +3-code
above-knee residual with the rows that would close it — G1's probe set at both scales, 202–238 level
rows against this child's 31.

**(c) The along-side field is the one landing with no trade in it.** Recommendation: 0.45. It costs
+0.00003 canonical ΔE and +0.00005 on the grids at a slope of 1 — less at 0.45 — closes three quarters of a grading vitrea did not
have at all, and its form is validated by the antisymmetry rather than assumed.

**(d) The user's eye keeps its veto (X6), and this child did not look.** The sheets are G3's and G4's.
The one thing worth pointing the eye at is the rim's corners on a thick panel, because that is where
the along-side field draws and the metrics that moved least are the ones that measure it.

---

## 10. Gaps to macOS this child found or sharpened, each with the work that would close it

1. **vitrea's sharp component is 1.67 device px against the reference's 2.79 at 1x**, at every rung,
   and nothing in this wave moves it: it is `blurSigma`, the thin capsule's own width (§1). Closing it
   needs a sharp width that grades with span, which the reference does not have (2.62 vs 2.79), or a
   re-fit of `blurSigma` against a bed where the thin cells are not the constraint. → a claims entry.
2. **vitrea's heavy component is 13.3 device px at the reference's own share against 19.5**, and
   `sizeScatterGainMax` is not a lever on it: raising it 8 → 10.3 left the reader's heavy reading
   unchanged at 13.29 (§2). The heavy tap is a mip-chain level and its effective width saturates. →
   `specs/tech-debt-tracker.md`, with rung `rG` as the evidence.
3. **The along-side field closes three quarters of the reference's range, not all of it** (0.743 of
   it at the fitted slope, 27 of 64 sides inside 20 %). The last quarter is in the rim's amplitude
   law, which W23 fitted on the straight spans this factor deliberately leaves alone. → the wave's
   Deferred list.
4. **The CSS tier cannot draw the along-side field at all** — one inset shadow, one alpha around the
   contour — while being exactly coherent with the GPU tier's side mean (§4). → X8's residual, under
   Decision Log 23 (a).
5. **The dark probe grid cannot separate a two-code term.** Its whole collapsed-to-uncollapsed
   contrast is six 8-bit codes (G0 §5), which is why the level term reads 0.029 on one grid and 0.001
   on the other. → a claims entry; G1's 2x captures are what change it.
6. **The above-knee level residual is not the reference's grading — it is vitrea's own span curve
   continuing where the reference's stops.** G0 §3 read the reference's WIDTH as flat above 96 while
   vitrea's `kDeep` keeps rising to `sizeScatterSpanMax` = 256. The offset this wave fits is a
   correction for that, not a term the reference has; the term the reference has may be a lower
   `sizeScatterSpanMax`, which is also the thin end's constant and so is X5-entangled. → the wave's
   Deferred list, with the rows (spans 128–256 over the grids' backdrops at both scales).
7. **One row identifies the 1x heavy share, and it is a validation row** (§2). Nothing on the
   canonical bed checks the wave's central constant off its own fit. → G1's probe set; recorded in
   the claims section as the condition the fit was made under.
