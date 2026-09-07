# W21 G2b — the diagnosis, the derivation that follows from it, and why nothing landed (2026-09-07)

G2 left the gate red on thirteen rows, all one mechanism on the CSS tier, and W21 Decision Log 3 (a)
deferred the bounded diagnosis by name. This is that diagnosis, the fix it implies, the measurement
of that fix, and the measurement of the constraint the fix then ran into. **Nothing landed.** The
canonical bed is exactly as G2 left it, the source tree is at `794a99d`, and the two candidates are
kept beside this file as patches with their captures' numbers attached.

The short version, in three sentences. The mechanism is (ii) of the three the brief named — the
mapping's conversion is solved against a backdrop level that is not this cell's, and on the dark
scheme it degenerates twice over — and the clamp of (i) costs 0.0018, not the residual. Anchoring
the conversion at the surface's own sampled backdrop halves or better every dark CSS cell's ΔE
against Apple and lands six of the eight coherence ratios, but it overshoots on the checkerboard
family, because **one level per surface cannot carry a mean over a distribution**, which is (iii)
arriving by a different road than the brief expected it. What does carry it is not an anchor at all:
where the tier draws its whole tint in the page's encoded space it cannot reproduce a linear-light
lerp over a structured backdrop at any alpha, and the surfaces in question only draw that form
because of a boundary declared at W17 against a light bed where crossing it cost nothing.

---

## 1. The diagnosis (`diagnosis.txt`, `table.txt`, `diag.mjs`)

Read `diagnosis.txt` in full; it carries the table and the arithmetic. The three verdicts, in brief:

**Not (i), the clamp's missing downward remainder.** The clamp binds on exactly one cell of the bed,
`checkerboard__rrect-md`. The solve's target there is 0.0468 — the native reading to four places —
the nominal composite is 0.0927, and the neutral is driven to −0.0051 and truncated at black. The
composite the renderer then draws is 0.0486, so the truncated remainder is **0.0018 of linear
luminance** and the GPU tier's row is inside every adopted bound carrying it. A downward alpha
branch would recover 0.0018 on one cell and would move the GPU tier, which this gate forbids.
`toneRespondedSourceOptics`'s one-sided comment is still true as written.

**(ii), and in two distinct ways.** The conversion agrees with the renderer at one declared level,
`referenceBackdropLuminance` = 0.02, fitted on the light scheme's cross-tier difference. Every
neutral the dark solve produces lands in 0.0000 … 0.0352 — that is, *on* the anchor — while the
cells' backdrops sit at 0.0037 … 0.5000. So on `photo__rrect-md` and `photo__rrect-lg` the span
`E(tint) − E(0.02)` is 0.0005, under `minimumTintContrast`, the guard fires and the renderer's
linear-light alpha 0.9053 is emitted verbatim as an encoded-space `rgba()` alpha; and on
`checkerboard__rrect-md` the neutral is black, the span is the whole of `−E(0.02)`, and the solved
0.8388 stands where 0.505 would have landed the renderer's own composite over that backdrop. The
guard's own doc comment says its case is "only reachable from a profile that tints to the reference
level" — the dark profile is exactly such a profile.

**And a second level nobody was carrying.** The renderer lerps over the backdrop's LINEAR mean; the
`rgba()` sits over `backdrop-filter`'s output, which is the ENCODED mean. On a solid these are one
number; on the checkerboard they are 0.5000 and 0.2140 in linear light. `BackdropToneSample` has
measured both since W9 (claims §5.31), so the pair costs no new reading.

The diagnosis is not a model of the tier — it is the tier. `diag.mjs` replays `root.ts`'s chain off
the shipped exports of `packages/platform-web/dist/index.js`, and its predictions reproduce
`g2/canonical-reads/`'s measured bodies to 0.003 on eight of nine cells on both tiers.

## 2. Candidate A — the anchor (`candidate-anchor.patch`, `read-anchor.txt`, `gate-matrix.txt`)

`cssTintAlpha`, `cssTintColor` and `cssOpticsFromSource` gain an optional `CssTintAnchor`, the PAIR
of means the two pipelines see, defaulting to the mapping's fitted level in both spaces — which is
arithmetically the form they had, so every caller that does not pass one is byte-unchanged.
`root.ts` passes the surface's own sample where `cssTintFormAt(cssTierCompositeLevel(...))` is
`"encoded"`, which is a SUFFICIENT condition for the encoded form and therefore reaches no surface
drawing the linear form. `cssTierCompositeLevel` is lifted into `optics.ts` so `css-tier.ts` and
`root.ts` read one expression. A pin was added to `tier-coherence.test.ts` at the dark profile over a
0.5 backdrop, with the anchor-independence at α = 1 asserted beside it.

**Contracts held.** GPU tier untouched: **13 / 13** 1x-dark `webgpu` captures byte-identical to
`g1/g1-digests.txt`. Contract X3: **89 / 89** light CSS captures across all four light profiles and
both scales byte-identical to the canonical bed — and not by luck, by arithmetic, because the only
light cells that draw the encoded form are at full backdrop adaptation where α = 1 and the
conversion is anchor-independent (`cssTintAlpha` returns 1 and `cssTintColor` returns `E(tint)`
whatever the anchor is).

**Fidelity against Apple: every dark CSS cell improved, most of them sharply** (OKLab ΔE mean,
1x, W20 bed → G2 landed → candidate A):

| cell | W20 | G2 | A |
| --- | --- | --- | --- |
| `photo__rrect-lg` (holdout) | 0.06211 | 0.05867 | **0.02222** |
| `photo__rrect-md` | 0.02217 | 0.02373 | **0.01098** |
| `checkerboard__capsule-button` | 0.00946 | 0.01356 | **0.00623** |
| `checkerboard__glass-over-glass` (holdout) | 0.04074 | 0.07057 | **0.05952** |
| `checkerboard__rrect-md` | 0.02125 | 0.04164 | **0.03353** |
| `photo__capsule-button` | 0.00963 | 0.01114 | **0.00776** |
| `mid-dark-solid__capsule-button` (holdout) | 0.00583 | 0.00096 | **0.00066** |

The tinted, collapsed and solid cells move by less than 0.00003, as the arithmetic requires. 2x is
the same table to three places (`g2b-verify.txt`).

**And it is not green.** Six of the eight `interiorLevelRatioGpuOverCss` rows land — `photo__rrect-md`
1.4975 → 0.9628, `photo__rrect-lg` 1.4860 → 0.9316, `photo__capsule-button` 1.2772 → 0.9673, and
their 2x twins — and the checkerboard family overshoots to the other side of the gate:
`checkerboard__capsule-button` 2.0705 → **0.6403**, `checkerboard__rrect-md` 3.8995 → **0.5192**,
`checkerboard__glass-over-glass` 2.4743 → **0.5730**. The nested pane's `crossTierOklabDeltaEMean`
falls 0.0624 → 0.0508 and 0.0578 → 0.0525 against ≤ 0.05, still over; its dom `ssimMean` goes
0.80048 → 0.82221 (1x, against ≥ 0.83, still under) and 0.83543 → **0.85878** (2x, against ≥ 0.85,
now over). Four predicate rows RECOVER — the CSS tier's own extractor sees the material over a
checkerboard again — which returns `PREDICATE_EXCLUDES` to 30 lines and puts those cells' ratios
back inside the gate rather than outside it.

**Why it overshoots, and why no anchor fixes it.** The metric is a mean of linear luminance over the
box, and an encoded-space `rgba()` at alpha α′ multiplies EVERY pixel's encoded value by (1 − α′) —
which under the transfer function's power law multiplies every pixel's LINEAR value by
(1 − α′)^2.4, and therefore the mean by (1 − α′)^2.4. A point solve at any single level cannot
reproduce a gain on a distribution; the two anchors bracket the answer (0.02 gives α′ = 0.839 and
a ratio of 3.90; the cell's own gives 0.518 and 0.519) and the truth is near 0.62, which is where
the pure gain law puts it. Over a solid there is no distribution and the point solve is exact, which
is why every solid and photo cell lands and only the checkerboards do not. **That is (iii), reached
by a road the brief did not name: not "one level per surface", but "one level at all".**

## 3. What actually carries it — three probes on the form boundary

The surfaces in question composite their whole tint in the page's encoded space because
`cssTintFormAt` says so: the linear chain's eight-bit quantum is coarser than one encoded code below
0.244 in linear light, and the whole dark scheme composites below that (2.5 codes at 0.047). W17
Decision Log 4 (c) declared that boundary against the light bed, where crossing it cost nothing.
Three probes, each a full re-capture of the two dark profiles on the CSS tier into scratch, with the
gate run over the result:

| probe | what changed | forms drawn on the dark bed | gate |
| --- | --- | --- | --- |
| `probe-linear` | tolerance → ∞ | all `linear` | 4 red |
| `probe-tol4` | tolerance → 4 codes | `linear` but the three darkest cells | 3 red |
| `probe-error` | the boundary as a comparison of the two forms' ERRORS | `linear` but `impulse`, both `dark-solid` cells and `mid-dark-solid` | 3 red |

`probe-linear` shows what the linear form is worth and what the boundary is for at once. Every
structured cell lands on the renderer — `checkerboard__rrect-md` 0.0455 against the GPU's 0.0475 and
the reference's 0.0468, `photo__rrect-md` 0.0383 against 0.0389, `checkerboard__capsule-button`
0.0698 against 0.0673 — and the two cells the chain cannot hold go dark exactly as W17 measured:
`impulse__capsule-button` 0.0037 → **0.0009** and `dark-solid__capsule-button` 0.0117 → **0.0085**,
which costs `impulse`'s dom `ssimOutside` 0.67089 against a bound of ≥ 0.78.

`probe-error` is the same partition reached without choosing a number, and it is the one worth
reading. The boundary's own doctrine — "a filter chain that cannot hold a value the page could is
drawing a different material rather than a more precise one" — compares the chain's quantum to the
page's and never weighs it against the error of the OTHER form. Weighing both is parameter-free: the
linear form's worst representation error is half the chain's step, 1/510 in linear light, and the
encoded form's error is its conversion's residual at this surface's own backdrop, which the tier can
evaluate with what it already has (`cssTierForegroundLevel` against `cssTierCompositeLevel`). Draw
whichever is nearer the renderer. That rule puts `impulse`, both `dark-solid` cells and
`mid-dark-solid` on the encoded form — where their residual is at or near zero because a solid
backdrop IS the point the solve is exact at — and everything else on the linear form.

**Under that rule, with `PREDICATE_EXCLUDES` re-derived (34 → 33), the gate is down to two rows,
neither of them the CSS tier's level:**

  * `texture / holdout / checkerboard__glass-over-glass__rest / 2x-dark`, `silhouetteIoU` 0.92673
    against ≥ 0.93 — G2's row, unmoved by anything here, the GPU tier's nested pane sitting nearer
    its own backdrop so the extractor recovers a smaller set;
  * `dom / holdout / checkerboard__glass-over-glass__rest / 2x-dark`, `silhouetteIoU` 0.90482
    against ≥ 0.93 — a cell that stops being degenerate under the fix and then misses a shape bound
    it was never measured against, which is the same extractor in the same place.

Every coherence row, every perceptual row and every other shape row passes.

## 4. Why nothing landed, and what the ruling has to reach

The brief's rule is that a red gate is not landed and that the remainder is a user decision. It
holds here twice over. Candidate A alone is red on the checkerboard family and would need the bed
rebuilt to carry it; and the thing that makes the gate green is not the derivation the brief
chartered but the FORM BOUNDARY, which is a declared boundary with its own Decision Log entry (W17
Decision Log 4 (c)) and moves only by a recorded ruling. Both candidates are kept as patches beside
this file with their captures' numbers, and the canonical bed and the source tree are untouched.

Three things a ruling can reach, in the order this work would recommend them:

1. **Re-rule the form boundary as a comparison of errors** (`probe-error`). Derivable, no fitted
   constant, reproduces the boundary's own intent, and it is what makes the dark scheme's CSS tier
   agree with the renderer at all. It needs its own X3 re-capture, since it also decides the form on
   the ten light cells that draw the encoded form today — those are at α = 1 with a residual of
   zero, so they should stay encoded, but that is an arithmetic expectation and not yet a
   measurement.
2. **Take candidate A with it or without it.** With the form boundary re-ruled the anchor is inert
   on almost every cell that motivated it, because those cells stop drawing the encoded form; it
   still improves the three cells that keep it, and it removes a degeneracy (`minimumTintContrast`
   firing on a real profile) that will recur on any scheme whose neutral sits near the fitted anchor.
   It is a smaller change than it looks and it can be ruled on separately.
3. **The two `silhouetteIoU` rows on the nested pane at 2x.** Neither is the material's level and
   neither is this gate's; they are the extractor reading a surface that now sits nearer its
   backdrop, which is W17's and W18's mechanism in a third place. A floor with a §5.27 row, or a
   narrowed claim, or the extractor.

## 5. The artefacts

  * `diagnosis.txt`, `table.txt` — the diagnosis and its table; `diag.mjs`, `model.mjs`, `run.mjs`,
    `table.mjs`, `backdrops.json` reproduce them off the shipped exports and the fixture backgrounds.
  * `g2b-capture.sh`, `g2b-runs.txt` — the scratch read: the two dark profiles and all four light
    profiles on the CSS tier, calibration and validation then holdout, plus the 1x dark GPU profile
    for the digest check. This is the CSS tier's first holdout read at this configuration and it was
    taken once per configuration, as the charter requires.
  * `g2b-verify.py`, `g2b-verify.txt` — the referee: the GPU digests, contract X3, every dark CSS
    row's ΔE against the W20 bed and against G2, and the thirteen gate rows before and after.
  * `read-anchor.txt`, `read-linear.txt`, `read-tol4.txt`, `read-error.txt` — the declared-geometry
    read (body, sd, per-side rim) of each candidate's captures.
  * `gate-matrix.txt`, `gate-probe-*.txt` — `adopted-thresholds.test.ts` over each scratch matrix.
  * `candidate-anchor.patch`, `candidate-form-error.patch` — the two candidates, applying to
    `794a99d`.
