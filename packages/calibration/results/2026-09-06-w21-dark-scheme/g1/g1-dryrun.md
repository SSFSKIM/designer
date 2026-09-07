# W21 G1 — the form declared and dry-run (2026-09-07)

The dark profile document re-recorded from G0's measurements, the two constants the design allows
fitted on rows that separate them, and the result dry-run on the canonical dark bed at both scales,
on both tiers, with the wave's one holdout read spent here (contract X6). Every number below cites
the file beside it. Nothing canonical was written: `results/matrix.json`, `web-captures/`,
`apps/reference-apple/fixtures/` and `scenes.json` are untouched, and the light profile document is
untouched.

**The headline.** On the GPU tier the dark bed's calibration ΔE mean falls from 0.0085 to **0.0041**
at 1x and from 0.0086 to **0.0041** at 2x — inside the parent's clause 5 (below 0.006) with margin —
and the holdout falls from 0.0300 to **0.0161** and from 0.0302 to **0.0160**. No GPU row got worse
on either S1 axis; every tinted cell moved by at most 0.00004; the collapsed capsules did not move
at all; every light-profile capture came back byte-identical (52 of 52). The bed's worst-shaped dark
cell, `dark-solid__rrect-md`, goes from 0.0286 to **0.0040**.

**What did not land.** Two clauses miss, each for a term this gate identified rather than caused,
and one stop fires on a tier the wave does not target:

* **clause 4's flatness, and its left side**, on the two dark cells that draw a rim at all. With
  `specularGain` 0 the top, bottom and right sides land within 0.0163 of the reference everywhere,
  and the LEFT side misses by 0.14 to 0.24. The cause is new and is not the constant that was
  fitted: the highlight pass draws its specular sweep as a stationary band on the left edge of every
  resting surface, in both colour schemes. §4 below has the isolation.
* **clause 3 on the thin rows** — the two canonical capsules over structured backdrops, 0.0386 to
  0.0439 against a 0.010 clause. This is the appearance term W21 Decision Log 2 (a) defers by name.
  It is LARGER than that ruling anticipated and §6 says so with the numbers.
* **stop S1 fires on ten CSS-tier rows** and on none on the GPU tier. The CSS tier's two layers
  derive the response law from one backdrop level, which is right over a solid and much too dark
  over a checkerboard; §7 has the residual per cell.

---

## 1. The form, as recorded

`packages/calibration/profiles/apple-macos-26.5-1x-dark-standard.json` (the one document serves both
dark profiles). Seven constants moved; `resolvedMaterialSha256` 8b9d3d2dbe1755aa → **d86f480c0e136627**,
recomputed by `packages/calibration/test/tuned-profiles.test.ts` and re-recorded with
`$comment-sha-history`'s entry.

| constant | was | now | provenance |
| --- | --- | --- | --- |
| `backdropToneAnchorX` | (unnamed, inherited) | [0.1104, 0.2706, 0.9505] | measured — `g0/anchors.txt`, the three solids' encoded footprint means |
| `backdropToneResponseThin` | (unnamed) | [0.0110, 0.0284, 0.1611] | measured — `rrect-sm` on each solid; the top is `checkerboard-64__rrect-sm` |
| `backdropToneResponseThick` | (unnamed) | [0.0131, 0.0238, 0.1006] | measured — `rrect-md` and `rrect-lg` pooled |
| `backdropToneResponseStrength` | 0 | 1 | W21 Decision Log 2 (a) |
| `optics.regular.specularGain` | 0.55 (inherited) | 0 | **declined**, not fitted — the rows do not separate it |
| `optics.regular.rimAlpha` | 0.18 (inherited) | 0.082 | **fitted** — §3 |
| `optics.regular.tintAlpha` | 0.97 | 0.90 | **fitted** — §5 |

The six anchor levels are measurements and were never tuned (contract X1); every one carries a
majority byte-state σ of 0.0000 across the probe's seven attested runs, and the reader's own
recovery bound is 0.0028 (claims §5.88 §1). The thin row's top anchor is the wave's one genuine
choice between two readings of the same reference and the document's
`entries.backdropToneResponse.thinTopAnchor` states it in full; both readings stay on file in
`g0/anchors-measured.json` and `g0/anchors-footprint-top.json`.

The generated export `packages/platform-web/src/dark-profile.ts` was regenerated from the document
(`pnpm --filter @vitreajs/vitrea-web run profile:dark`), which is what makes contract X7's two tests
green again.

## 2. What the form alone does, before either fit

On the probe grid, mean absolute body error under the declared geometry against the dark reference
(`probe-objective.txt`; 41 untinted cells, the appearance-switch cell apart):

| render | all | thin (11) | thick (30) | the switch cell | tinted (4) |
| --- | --- | --- | --- | --- | --- |
| the shipped document (strength 0) | 0.0277 | 0.0440 | 0.0217 | 0.8922 | 0.0069 |
| the measured anchors, nothing else fitted | 0.0139 | 0.0237 | 0.0103 | 0.8046 | 0.0069 |
| **the landed form (rimAlpha 0.082, tintAlpha 0.90)** | **0.0133** | 0.0245 | **0.0092** | 0.8043 | 0.0071 |

The law does the work and the two fits do not disturb it: the thick body improves by a factor of
2.4 with nothing fitted, and the two constants move it a further 0.0011.

## 3. Fit 1 — `optics.regular.rimAlpha`, on the six solid cells' rim excess per side

Full table: **`fit-rim.txt`**. Script and its declared objective: `fit-rim.py`.

**The rows.** `dark-solid` and `mid-dark-solid` crossed with `rrect-sm`, `-md` and `-lg`. Over a
solid backdrop the rim band carries no backdrop structure, so a side's peak minus that capture's own
body is the rim's whole amplitude. The reference's excess reads 0.0114–0.0187 over `dark-solid` and
0.0333–0.0391 over `mid-dark-solid`.

**The objective, declared before the number.** The mean over the fitted rows of
|excess_web − excess_native|, per SIDE rather than per cell, because `specularGain` 0 makes the four
sides one quantity and the reference agrees to 0.0008–0.0044 across them.

**The one exclusion, and it is a measurement.** The LEFT side is not fitted on — §4.

**The result.** The rim is additive in the shader, so the excess is linear in the constant and two
rendered points determine the line per row. Fitted twice, independently:

| fitted at | pooled minimiser | mean |Δ excess| at it | per-row answers |
| --- | --- | --- | --- | --- |
| `tintAlpha` 0.97 (`rim002-a097`, `rim018-a097`) | 0.0819 | 0.0052 | 0.0441 – 0.0903 |
| `tintAlpha` 0.90, the landed alpha (`rim002-a090`, `rim0082-a090`) | 0.0808 | 0.0051 | 0.0440 – 0.0884 |

**0.082 is adopted**: it sits inside both minimisers, and the 0.0011 between them is 0.0004 in rim
excess, an order of magnitude below the reader's 0.0028 recovery bound. Confirmed by rendering at it
(`fit-reads/rim0082-a090.json`): **mean |Δ excess| 0.0068 over the eighteen fitted rows, worst
0.0167**, every row inside clause 4's 0.03.

**The four sides now agree.** Over the three fitted sides vitrea's flatness is 0.0000–0.0066 where
the reference's is 0.0008–0.0044 — the reference's flatness reproduced, which is what clause 4 asks
for. Over all four sides it is 0.12–0.14, which is §4's term and not this constant's.

**What one constant costs.** The two backdrops disagree: `dark-solid`'s rows want 0.044–0.054 and
`mid-dark-solid`'s want 0.081–0.090. At 0.082 `mid-dark-solid` lands within 0.0025 on every side and
`dark-solid` is left 0.009–0.013 bright. Both are inside the clause; the disagreement is recorded
rather than split, because splitting it would mean a backdrop-dependent rim, which is a second
constant no other row asks for.

**Recorded, not fitted.**

* `dark-solid__rrect-sm` — the one cell vitrea's collapse fires on. The reference keeps a
  0.0150–0.0167 rim excess where vitrea folds the rim out entirely (0.0000 on all four sides).
  Deferred by W21 Decision Log 2 (b) with its number: it is a renderer mechanism for a cell whose
  OKLab ΔE is 0.0008.
* The `light-solid` cells, at the same constant: vitrea is 0.05–0.06 too DIM on top, bottom and
  right (native 0.2345–0.2557, vitrea 0.1740–0.1957) and 0.089 too bright on the left. The
  reference's own horizontal-against-vertical split lives here (claims §5.89 §5) and no canonical
  dark cell shows it. On `light-solid__rrect-sm` — the appearance-switch cell — vitrea draws a rim
  of 0.15 to 0.41 where the reference, drawing its light appearance at body 0.9666, has almost none.

## 4. What the rim fit found and did not fit: a stationary specular sweep on every resting surface

**This is the gate's one genuinely new finding and it is not a dark-scheme fact.**

With `specularGain` 0 the optics pass's rim becomes `rimWeight × rimAlpha`, which has no direction —
and vitrea's left edge still read 0.12–0.15 above its other three sides on every solid. Two renders
isolate it exactly: `sweep0-rim002` and `sweep0-rim018` are the same documents with `sweepGain` 0
and nothing else, and against their twins they move the LEFT side by −0.119 to −0.145 and every
other side by **+0.0000** (`fit-rim.txt`, "the recorded term"). With the sweep off, left equals right
to the fourth decimal and the flatness collapses to 0.002–0.005 — the reference's own flatness.

The mechanism is in `packages/renderer-webgpu/src/wgsl/highlight.ts`: the specular sweep is a
Gaussian band centred at `hu.sweep.x · 2π`, the motion driver's sweep channel, which is 0 at rest
(`render-model.ts`'s `sweep: 0`); 0 radians in the gradient's angular coordinate is the left edge.
So a surface that is not being interacted with carries a stationary shimmer on its left side. The
pass's own doc comment says Reduced Motion turns the gain to zero because "the band is not drawn
stationary, it is not drawn" — at nominal motion it is drawn stationary, and nothing had measured
it.

**It is reported and not taken, on four grounds.** It is not the constant that was fitted. It is not
the dark scheme's — the light bed carries the same term, visible in this gate's own `light-solid`
rows and in the light reference's rim where left equals right and vitrea's does not. Zeroing
`sweepGain` in the dark patch would remove the dark scheme's shimmer ANIMATION as well, which no
fidelity row on a bed of rest states can see, and trading a motion feature for a metric is the kind
of thing this project's own doctrine says not to do silently. And the correct fix — gating the band
on the shimmer actually running — is a renderer mechanism that would move the LIGHT captures this
gate binds byte-identical (contract X3, stop S4), so it cannot land inside G1 at all.

**What it costs, exactly**, so the parent can price the work: on the canonical bed it is the whole
of clause 4's failure. Left side, GPU tier, dry run against the reference —
`dark-solid__rrect-md` +0.1394 (1x) and +0.2445 (2x), `mid-dark-solid__capsule-button` +0.0518 and
+0.0579; the flatness misses by the same amounts. Every other side of every solid cell is inside
0.0163. The two collapsed capsules and the `impulse` capsule are unaffected because the collapse
folds the highlight pass out with everything else.

## 5. Fit 2 — `optics.regular.tintAlpha`, on the passthrough rows

Full table: **`fit-alpha.txt`**. Script and its declared objective and constraint: `fit-alpha.py`.

**The rows.** The checkerboard pitch sweep at fixed component — `rrect-sm`, `rrect-md` and
`rrect-lg` over `checkerboard-4`, `checkerboard` (16), `checkerboard-32` and `checkerboard-64`, ten
rows. A pitch sweep at one component is a modulation-transfer curve, so it separates the alpha (which
scales the curve) from the blur (which changes its shape). Excluded with reasons:
`checkerboard-64__rrect-sm` (its footprint is inside one white checker, `bgSd` 0.0000, `pass`
undefined), `checkerboard-64__rrect-lg` (no such cell), `hc-text__rrect-sm` (4-of-7 bistable,
Decision Log 2 (c) puts it in no fit), and `checkerboard-lc16`, which is the equal-mean CHECK.

**The objective.** Mean over the rows of |ln(pass_web / pass_native)|, directly comparable to the
wave's factor-of-1.5 target (ln 1.5 = 0.405).

**The constraint, and it binds.** Seven alphas were rendered — 0.80, 0.86, 0.88, 0.90, 0.92, 0.94,
0.97 — and the BODY was read at every one, because the whole premise of refitting the alpha is that
the response law now owns the level. It does, over part of the range and not all of it:

| alpha | passthrough factor | worst thick |Δbody| | drift from the clamp-free plateau |
| --- | --- | --- | --- |
| 0.97 | 3.212 | 0.0052 | 0.0010 |
| 0.94 | 2.017 | 0.0059 | 0.0004 |
| 0.92 | 1.632 | 0.0062 | 0.0000 |
| **0.90** | **1.441** | **0.0055** | **0.0008** |
| 0.88 | 1.393 | 0.0119 | 0.0103 |
| 0.86 | 1.383 | 0.0213 | 0.0197 |
| 0.80 | 1.406 | 0.0496 | 0.0481 |

Above 0.92 the thick body is flat in the alpha to 0.0002 — the separation the design assumed, now
measured. Below about 0.895 it climbs steeply as the solve runs out of headroom against the black
clamp, which is exactly the downward remainder G0 measured (claims §5.88 §3).

* unconstrained minimiser: alpha 0.8225, factor 1.368, and it costs 0.039 of body — inadmissible;
* constrained by the wave's 0.010 body clause: the range opens at 0.8850, factor 1.398;
* constrained by the SEPARATION (the body within the reader's 0.0028 recovery bound of its plateau):
  the range opens at 0.8975, factor 1.431.

**0.90 is adopted** — the nearest RENDERED point on the safe side of that boundary. It is 0.010
worse in the factor than the interpolated minimiser and 0.0011 safer in the drift, and it is a
measurement rather than an interpolation onto a cliff edge that was located on the probe grid and
would be applied to a canonical bed whose cells sit elsewhere on the same curve. The constrained
answer and the adopted one are both on the page so the 3 % is visible rather than assumed.

**The result.** Geometric mean factor **1.441**, inside the wave's 1.5. Six of ten rows inside 1.13.
Against the shipped document's 0.97 the passed structure rises by a factor of about four while the
thick body moves by 0.0007.

**The equal-mean pair, the check the fit was not told about.** `checkerboard` and
`checkerboard-lc16` hold the same encoded mean and differ in structure by 0.568. At 0.90 vitrea
reads 0.0374 and 0.0375 on `rrect-md` against the reference's 0.0332 and 0.0287 — it passes the two
boards almost identically where the reference passes the low-contrast one less. That is the lerp
behaving as a lerp and the reference attenuating the low-contrast board by MORE than its contrast
ratio, which claims §5.89 §4 already recorded on the same pair. It is a residual in the blur, not in
the alpha.

**The residual, and why no second constant.** One alpha does not close the sweep. What misses is
(a) every thin row, short by a factor of 1.9 to 3.5, and (b) pitch 4 on every component, short by
1.83 on `rrect-md`. Neither separates a second alpha, which is stop S5's own test:

* the thin rows' body LEVEL is itself wrong by 0.03–0.04 — the deferred appearance term — and the
  standard deviation of a body whose level is off by that much is not a clean read of what the alpha
  passed. A second alpha graded on thickness would be fitting the appearance term through the wrong
  constant;
* the pitch-4 shortfall is the same at every component and is a shortfall in the blur's SHAPE at the
  finest pitch. That is the scatter facet's constant (claims §5.41), not this one.

So one constant, as Decision Log 2 (c) allows and no more.

## 6. The dry run on the canonical bed — clauses 3 and 4 (X6, X2)

Read under the declared geometry by `g0/read.py` against the canonical fixtures, before (the W20
bed's captures) and after (this gate's dry run). Full table: **`g1-clauses.txt`**; the reads are in
`canonical-reads/`. The holdout cells were read here and nowhere else.

### Clause 3 — the body within 0.010, GPU tier, thin and thick apart

| scale | rows | mean |Δbody| | worst | clause 3 |
| --- | --- | --- | --- | --- |
| 1x | 4 thick | **0.0039** | 0.0079 | met on every cell |
| 2x | 4 thick | **0.0039** | 0.0079 | met on every cell |
| 1x | 5 thin | 0.0171 | 0.0433 | met on 3, missed on 2 |
| 2x | 5 thin | 0.0174 | 0.0439 | met on 3, missed on 2 |

Per cell at 1x (2x within 0.0006 on every row), native | before → after:

| cell | thick | native | before | after | \|Δ\| | clause 3 |
| --- | --- | --- | --- | --- | --- | --- |
| `dark-solid__rrect-md` | yes | 0.0153 | 0.0482 | 0.0130 | 0.0023 | met |
| `checkerboard__rrect-md` | yes | 0.0468 | 0.0628 | 0.0475 | 0.0007 | met |
| `photo__rrect-md` | yes | 0.0466 | 0.0547 | 0.0389 | 0.0077 | met |
| `photo__rrect-lg` (holdout) | yes | 0.0454 | 0.0555 | 0.0404 | 0.0050 | met |
| `dark-solid__capsule-button` | no | 0.0110 | 0.0117 | 0.0117 | 0.0007 | met (collapsed) |
| `impulse__capsule-button` (validation) | no | 0.0066 | 0.0037 | 0.0037 | 0.0030 | met (collapsed) |
| `mid-dark-solid__capsule-button` (holdout) | no | 0.0285 | 0.0500 | 0.0286 | 0.0000 | met |
| `checkerboard__capsule-button` | no | 0.1059 | 0.0640 | 0.0673 | 0.0386 | **MISSED** |
| `photo__capsule-button` | no | 0.0961 | 0.0551 | 0.0528 | 0.0433 | **MISSED** |

`checkerboard__glass-over-glass` has no single declared box and the instrument says so rather than
inventing a rectangle; its matrix rows are in §7.

**A correction the parent should have.** W21 Decision Log 2 (e) rules on the thin rows on the
premise that "the canonical bed's capsules over structured and dark backdrops read within 0.02 on
the probe grid". They do not. At the landed constants the probe's own capsule cells read 0.0327
(`checkerboard-4`), 0.0386 (`checkerboard`), 0.0451 (`checkerboard-32`) and 0.0582
(`checkerboard-64`) — rising with the encoded input, the appearance term's signature — and the
canonical bed's two structured capsules read 0.0386 and 0.0433. The direction of the ruling is
unchanged (no constant is added to the law for it, and the term is a scene-level input neither tier
has), but the remainder the parent is ruling on is twice what the ruling quotes. The premise the
ruling rests on is worth restating with these numbers before clause 3 is signed off.

The thin cells barely moved at all: `checkerboard__capsule-button` improves 0.0419 → 0.0386 and
`photo__capsule-button` worsens 0.0410 → 0.0433. Their ΔE improved anyway (§7) because what moved on
them is the rim and the passed structure, not the level.

### Stop S3 — the collapsed capsules, within 0.002 of where they were

Does not fire. `dark-solid__capsule-button` and `impulse__capsule-button` move by **+0.0000** in
body at both scales and on both tiers; their captures are unchanged, which is the collapse keeping
its near-black domain exactly as Decision Log 2 (d) requires.

### Clause 4 — the rim per side within 0.03 and the reference's flatness reproduced, GPU tier

| cell | scale | top | bottom | right | left | flat (native → web) |
| --- | --- | --- | --- | --- | --- | --- |
| `dark-solid__capsule-button` | 1x | −0.0132 | −0.0130 | −0.0044 | −0.0044 | 0.0088 → 0.0000, met |
| `impulse__capsule-button` | 1x | −0.0115 | −0.0107 | −0.0025 | −0.0024 | 0.0103 → 0.0013, met |
| `dark-solid__rrect-md` | 1x | +0.0078 | +0.0077 | +0.0067 | **+0.1394** | 0.0044 → 0.1327, **MISSED** |
| `mid-dark-solid__capsule-button` (holdout) | 1x | −0.0032 | −0.0030 | −0.0005 | **+0.0518** | 0.0047 → 0.0523, **MISSED** |
| `dark-solid__rrect-md` | 2x | +0.0163 | +0.0162 | +0.0133 | **+0.2445** | 0.0070 → 0.2312, **MISSED** |
| `mid-dark-solid__capsule-button` | 2x | +0.0028 | +0.0030 | +0.0003 | **+0.0579** | 0.0113 → 0.0575, **MISSED** |

Every side except the left is met on every cell. The left, and the flatness with it, is §4's
stationary sweep and nothing else: the two collapsed capsules meet the clause on all four sides
precisely because the collapse folds the highlight pass out too. Against the W20 bed this is still
an enormous improvement — `dark-solid__rrect-md`'s four sides were 0.2244 / 0.1021 / 0.2327 / 0.0854
against a reference of 0.0340 / 0.0339 / 0.0296 / 0.0296, and three of them are now inside 0.008.

## 7. The dry run on the canonical bed — the matrix rows (clauses 5 and 6)

Full table: **`g1-tables.txt`**. Dry-run matrix in scratch at
`/Users/new/.claude/jobs/5c70e47f/tmp/w21/g1/dryrun/g1-dryrun.json`; the referee is the canonical
`results/matrix.json`, the W20 bed frozen in the wave's Grounding Baseline.

### GPU tier, OKLab ΔE mean, W20 bed → dry run

| profile | calibration (9) | validation (1) | holdout (3) |
| --- | --- | --- | --- |
| 1x dark | 0.00846 → **0.00410** | 0.00291 → 0.00291 | 0.02996 → **0.01612** |
| 2x dark | 0.00860 → **0.00410** | 0.00329 → 0.00329 | 0.03017 → **0.01596** |

Clause 5's bound (calibration ΔE mean below 0.006 at each scale) is **met at both scales, by 0.0019**.
The validation cell is `impulse__capsule-button`, which is the collapse's domain and byte-identical
by construction (Decision Log 2 (d)).

Per cell at 1x, GPU tier (2x within 0.0006 on every row):

| cell | set | ΔE mean | ΔE p95 | ssimMean |
| --- | --- | --- | --- | --- |
| `dark-solid__rrect-md` | calibration | 0.02861 → **0.00401** | 0.11606 → 0.01326 | 0.93069 → 0.98767 |
| `photo__rrect-md` | calibration | 0.01972 → **0.01313** | 0.10323 → 0.06665 | 0.97505 → 0.99274 |
| `checkerboard__rrect-md` | calibration | 0.01110 → **0.00395** | 0.07769 → 0.01997 | 0.95743 → 0.98697 |
| `photo__capsule-button` | calibration | 0.00774 → 0.00753 | 0.08856 → 0.08900 | 0.99044 → 0.98852 |
| `checkerboard__capsule-button` | calibration | 0.00558 → 0.00503 | 0.03343 → 0.04672 | 0.97413 → 0.99167 |
| `dark-solid__capsule-button` | calibration | 0.00077 → 0.00077 | 0.00511 → 0.00511 | 0.98661 → 0.98661 |
| the three tinted capsules | calibration | 0.00054 / 0.00102 / 0.00104 → 0.00054 / 0.00098 / 0.00101 | unchanged | 0.99708–0.99906 → 0.99750–0.99906 |
| `impulse__capsule-button` | validation | 0.00291 → 0.00291 | 0.03240 → 0.03240 | 0.97976 → 0.97976 |
| **`photo__rrect-lg`** | **holdout** | 0.05720 → **0.03047** | 0.11643 → 0.06901 | 0.94968 → 0.98939 |
| **`checkerboard__glass-over-glass`** | **holdout** | 0.02736 → **0.01765** | 0.09875 → 0.09419 | 0.92945 → 0.95861 |
| **`mid-dark-solid__capsule-button`** | **holdout** | 0.00532 → **0.00025** | 0.06249 → 0.00000 | 0.98082 → 0.99692 |

**The holdout's three cells, named with their movement** (X6's whole point). All three improve at
both scales. `photo__rrect-lg`, the bed's worst dark row, halves. `checkerboard__glass-over-glass`
improves by 36 % and is the PARTIAL the charter predicted: the tone axis stands down over a glass
backdrop (W9 Deferred), and its interior still reads 0.0499 against the reference's 0.0436 where the
other thick cells land within 0.002. `mid-dark-solid__capsule-button` falls to 0.00025, effectively
exact, and its ΔE p95 to 0.00000.

The one GPU row that moved backwards on any axis is `photo__capsule-button`'s `ssimMean`, by 0.0019
at 1x and 0.0017 at 2x — inside S1's 0.005 and beside a ΔE that improved. Its ΔE p95 rose by
0.00044.

### The material axes the wave's own instrument mirrors (GPU tier, 1x, native | bed → dry run)

| cell | interiorMean | interiorStdDev | rimPeakLuminance |
| --- | --- | --- | --- |
| `checkerboard__rrect-md` | 0.0493 \| 0.0683 → 0.0501 | 0.0280 \| 0.0392 → 0.0313 | 0.0728 \| 0.1665 → 0.0796 |
| `photo__rrect-md` | 0.0490 \| 0.0600 → 0.0415 | 0.0177 \| 0.0334 → 0.0208 | 0.0656 \| 0.1575 → 0.0719 |
| `photo__rrect-lg` (holdout) | 0.0464 \| 0.0581 → 0.0413 | 0.0161 \| 0.0253 → 0.0171 | 0.0678 \| 0.1525 → 0.0699 |
| `mid-dark-solid__capsule-button` (holdout) | 0.0289 \| 0.0512 → 0.0291 | 0.0049 \| 0.0169 → 0.0082 | 0.0064 \| 0.0199 → 0.0085 |
| `checkerboard__capsule-button` | 0.1130 \| 0.0732 → 0.0708 | 0.0671 \| 0.0494 → 0.0374 | 0.1066 \| 0.1470 → 0.0572 |
| `dark-solid__rrect-md` | 0.0414 \| 0.2105 → 0.0788 | 0.0051 \| 0.0910 → 0.0695 | — (excluded by the predicate) |

`dark-solid__rrect-md`'s `interiorMean` row is the one claims §5.87 warned about: over a dark solid
the native silhouette is the rim ring in fragments, so both sides of that row measure the RIM. It is
quoted here for continuity and the declared-geometry read in §6 (0.0153 native against 0.0130) is
the reading that means something. The cell remains excluded from the gate by the conditioning
predicate; G2 re-derives `PREDICATE_EXCLUDES` and the native silhouettes do not move.

Note the standard deviation on the capsules FALLING (0.0494 → 0.0374 against a native 0.0671) while
the alpha passes four times more structure. The two are not in contradiction: the silhouette-based
`interiorStdDev` over a capsule includes the rim ring, which shrank by a factor of 2.6, and the
declared-geometry read of the same cells shows the passed structure rising. It is the same
instrument problem in a milder form, and it is why contract X2 exists.

### Clause 6 — the CSS tier's dark rows, derived from the same patch, recorded

| profile | calibration (9) | validation (1) | holdout (3) |
| --- | --- | --- | --- |
| 1x dark | 0.01147 → 0.01163 | 0.00362 → 0.00362 | 0.03623 → 0.04340 |
| 2x dark | 0.01166 → 0.01129 | 0.00401 → 0.00401 | 0.03676 → 0.04183 |

Flat on calibration, worse on the holdout, and the mean hides a clean split. Over a SOLID backdrop
the CSS tier reads the response law correctly and improves enormously —
`dark-solid__rrect-md` 0.03065 → **0.00455**, `mid-dark-solid__capsule-button` 0.00583 → **0.00096**,
`photo__rrect-lg` 0.06211 → 0.05867. Over a STRUCTURED backdrop it over-darkens badly:
`checkerboard__rrect-md` 0.02125 → 0.04164, `checkerboard__glass-over-glass` 0.04074 → 0.07057,
`checkerboard__capsule-button` 0.00946 → 0.01356, `photo__capsule-button` 0.00963 → 0.01114,
`photo__rrect-md` 0.02217 → 0.02373.

The declared-geometry read says why in one number: on `checkerboard__rrect-md` the CSS tier's body
lands at **0.0122** against a reference of 0.0468 and the GPU tier's 0.0475. The CSS tier resolves
the response from ONE backdrop level for the whole surface, which is the right answer over a solid
and much too dark where the footprint's encoded mean is far from what a single `backdrop-filter`
layer can carry. Clause 3 on the CSS tier therefore misses on six rows per scale (thick mean 0.0185,
worst 0.0346; thin mean 0.0264, worst 0.0731) where it met on three.

Clause 4 on the CSS tier is nearly met — every side inside 0.03 except
`mid-dark-solid__capsule-button`'s bottom (−0.0322 at 1x, −0.0382 at 2x) — because the CSS tier's
rim has no stationary sweep to carry.

This is the CSS-only residual wave Decision Log 23 (a) records rather than charters. It is recorded
here with its number and its cause, and the shape of the work that would close it is a per-region
tone resolution on the CSS tier, which the tier's two layers cannot express as they stand.

## 8. Contract X3 — the light profiles byte-identical

**Held.** The 1x light-standard profile was captured on both tiers at this gate's HEAD and every one
of its **52 captures is byte-identical** to the canonical `web-captures/` on the capture machine
(`g1-tables.txt`, X3 section). Nothing in the renderer's defaults moved under this gate's edits, and
the one non-profile source change (the scene server's `VITREA_FIXTURES` resolution, §10) does not
touch a rendered pixel.

## 9. The stops, dispositioned with numbers

| stop | what it watches | cells it applies to | verdict |
| --- | --- | --- | --- |
| **S1** | an untinted dark row worse than the W20 bed by > 0.001 ΔE mean or > 0.005 `ssimMean` | 20 untinted dark rows per tier, both scales | **FIRES on 10 CSS rows; does not fire on any GPU row.** Worst: `checkerboard__glass-over-glass` +0.02982 ΔE / −0.05545 ssim at 1x, `checkerboard__rrect-md` +0.02039 / −0.03008. Every one is CSS. |
| **S2** | a tinted dark cell moved by more than 0.001 | 3 tinted capsules × 2 scales × 2 tiers = 12 | **does not fire.** Largest movement 0.00004 (GPU) and 0.00003 (CSS); five of the twelve moved by 0.00000. |
| **S3** | a collapsed capsule moved by more than 0.002 in body | `dark-solid__capsule-button`, `impulse__capsule-button`, both scales, both tiers | **does not fire.** All eight rows +0.0000. |
| **S4** | any light-profile capture not byte-identical | 52 light captures, both tiers | **does not fire.** 52 / 52. |
| **S5** | a fitted constant whose rows do not separate it | `specularGain`, `rimAlpha`, `tintAlpha`, and any second alpha | **does not fire, and it did work.** `specularGain` was DECLINED under it (its rows say the reference has no light direction at all); a second, thickness-graded alpha was DECLINED under it (§5's residual is the deferred appearance term and the scatter's blur shape, not this constant). The two constants that were fitted carry the rows they were fitted on. |
| **S6** | the encoded-mean law refuted in dark by W9's rule | the probe's 31 scored structured cells | **does not fire.** P3 wins on the thick rows at RMS 0.0078 against P0's 0.0176 and P1's 0.0082 (claims §5.89 §3), and the landed render reaches 0.0092 mean thick body error on the probe and 0.0039 on the canonical bed. On the thin rows no hypothesis is close and the residual is the appearance term, which is deferred by name rather than fitted. |
| **S7** | the user's eye | the sheet | **pending the user.** `sheets/g1-1x.png`, `sheets/g1-2x.png`. |

**S1's disposition, stated for the parent rather than decided here.** The wave's fidelity target is
the GPU tier and the CSS tier derives what its two layers can carry, with a CSS-only residual
recorded rather than chartered (wave Decision Log 23 (a); W21's clause 6 asks only that the CSS rows
be "recorded, moved or not"). S1 as chartered does not say "GPU tier", so it fires; the rows it
fires on are exactly the structured-backdrop cells of §7 and the cause is one identified mechanism.
The parent rules.

## 10. The tooling fix that rides this gate (Decision Log 2 (g))

`packages/calibration/web/vite.config.ts` now `resolve()`s `VITREA_FIXTURES` before it mounts the
directory and before the containment check reads it. The check compares a NORMALISED served path
against the raw environment value, so a value carrying a `..` segment failed its own check and every
background came back 403 with a message about `capture.sh backgrounds` (claims §5.89 §8). G0's
`run-web.sh` had to canonicalise the path itself with a `cd`-and-`pwd` dance and a paragraph
explaining why; this gate's `run-probe-web.sh` does not, and that difference is the fix's test.

## 11. The rows the landing must reproduce byte for byte

`g1-digests.txt` — a SHA-256 per capture over all 104 cells of the dry run, beside the profile
document's own file digest (`ebfb0858…`) and its `resolvedMaterialSha256` (`d86f480c0e136627`).
G2 rebuilds from the main checkout and every dark capture must come back with the same digest; a
byte that moves means a constant or the renderer moved, and the holdout read above would be void.

The dry run is the frozen configuration. Its constants are §1's table; its scratch tree is
`/Users/new/.claude/jobs/5c70e47f/tmp/w21/g1/dryrun/`; its run order and timings are
`g1-dryrun-driver.txt` and `g1-runs.txt`.

## 12. What remains, and where it belongs

1. **The stationary specular sweep at rest** (§4) — NEW, and the largest single thing this gate
   found. Both colour schemes, every resting surface, 0.12–0.24 on one side of every rim. A renderer
   mechanism (gate the sweep's gain on the shimmer actually running), which would move the light
   captures and so cannot ride a wave that binds them byte-identical. Belongs in the W21 spec's
   Surprises and Deferred and in the tracker; it is what stands between clause 4 and green.
2. **The scene-level appearance switch** (claims §5.89 §2; already Deferred by name) — the thin
   rows' residual. This gate measures it larger than Decision Log 2 (e) quotes: 0.039–0.044 on the
   canonical bed's two structured capsules and 0.033–0.058 across the probe's, rising with the
   encoded input. §6 has the correction.
3. **The passthrough one alpha cannot reach** (§5) — every thin row (1.9–3.5×) and the finest pitch
   on every component (1.83×). The first is the appearance term seen through the standard deviation;
   the second is the blur's shape and belongs to the scatter facet.
4. **The collapsed rim** (§3) — +0.0150 to +0.0167 on `dark-solid__rrect-sm`, already Deferred with
   its number; this gate confirms vitrea folds it out to 0.0000 on all four sides.
5. **The CSS tier's structured-backdrop residual** (§7) — NEW as a number: the CSS body reads 0.0122
   against a reference of 0.0468 on `checkerboard__rrect-md`, and ten CSS rows regress. Recorded,
   not chartered (Decision Log 23 (a)).
6. **The nested pane in dark** — partially closed rather than open: `checkerboard__glass-over-glass`
   0.0274 → 0.0177 on the GPU tier with its interior still 0.0499 against 0.0436, and worse on the
   CSS tier. The expected partial, now with its number.
7. **The reference's horizontal-against-vertical rim split over bright backdrops** and vitrea's
   0.05–0.06 shortfall on the `light-solid` rim's top, bottom and right (§3) — recorded; no
   canonical dark cell exercises either.

## 13. One paragraph the parent can lift into claims

W21 G1 re-recorded the dark profile document from the probe's measurements and dry-ran it on the
canonical dark bed at both scales and on both tiers, with the wave's one holdout read spent there.
Seven constants moved and the fingerprint with them (8b9d3d2dbe1755aa → d86f480c0e136627): the
response law stands up at strength 1 on six anchors measured on the dark reference and never tuned;
`specularGain` goes to 0 because the reference's rim has no light direction at all; `rimAlpha` is
fitted at 0.082 on the six solid cells' per-side excess at a mean error of 0.0068 against a 0.03
clause; and `tintAlpha` is refitted at 0.90 on ten passthrough rows, the first time the alpha has
been free to carry the structure it was fitted to carry, at a factor of 1.441 against a target of
1.5 and with the thick body moving 0.0007 while the passed structure rises fourfold. On the GPU tier
the dark calibration ΔE mean falls 0.0085 → 0.0041 at 1x and 0.0086 → 0.0041 at 2x, inside the
wave's 0.006 clause; the holdout falls 0.0300 → 0.0161 and 0.0302 → 0.0160 with all three of its
cells improving; the thick body under the declared geometry lands at 0.0039 mean and 0.0079 worst,
inside the 0.010 clause on every cell; every tinted cell moved by at most 0.00004, the collapsed
capsules by 0.0000, and all 52 light captures came back byte-identical. Two things did not land and
both are named terms rather than misses of the constants that were fitted: clause 4's flatness,
because the highlight pass draws its specular sweep as a stationary band on the left edge of every
resting surface in BOTH colour schemes — isolated here to +0.0000 on the other three sides and
0.12–0.24 on the left, and unfixable inside a wave that binds the light captures byte-identical —
and clause 3 on the thin rows, where the deferred appearance term leaves 0.039–0.044 on the two
canonical capsules over structured backdrops, twice what Decision Log 2 (e) anticipated. Stop S1
fired on ten CSS-tier rows and none on the GPU tier: the CSS tier resolves the response law from one
backdrop level, which is right over a solid (`dark-solid__rrect-md` 0.0307 → 0.0046) and much too
dark over a checkerboard (body 0.0122 against 0.0468), and that is the CSS-only residual wave
Decision Log 23 (a) records rather than charters.
