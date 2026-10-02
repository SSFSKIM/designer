## 5.201 W43 G3 (i), the refit in scratch: the 0.25 cuts first, the unmoved endpoint read on them, and candidate c05 fitted on the WebGPU tier with the CSS tier derived; every gated miss listed for the user before any freeze (2026-10-02)

*DRAFT for the parent, written by G3 (i). Nothing here is sealed or published, no stage exists,
and the holdout was never read.*

Evidence directory: `results/2026-10-02-w43-g3-refit/`, on branch `w43-g3-refit` off `e2a32591`.
Charter: clause 10, steps 1–3; clauses 11 and 14; Decision Logs 5 and 7 as RULED by the user on
2026-10-02, "Adopt all eleven recommendations", folded into the charter in the branch's first commit
(`cfa5a95c`). The raw renders stay on the capture machine under `~/vitrea-w43/g3-scratch/`
(the pre-fit and every candidate's matrix and PNGs). The repository holds:
- the cuts (`cuts/`);
- the pre-fit render's driver, record and gzipped matrix (`prefit/`);
- the rehearsal (`rehearsal/`);
- the fit's tooling, every candidate's documents, specs and logs (`fit/`);
- the chosen candidate's reading and its misses (`read/`);
- the sheet script and its dispatch record (`sheets/`);
- the close checks (`close-checks.txt`).

The sitting's three HOLDs (G1b, and twice for clause 6's positive capture) stopped two render passes
in flight. Each is logged as stopped and was relaunched as a new labelled pass. A third pass was
refused by X6 on a peer session's Playwright Chrome and resumed after it exited.

### 1. The cuts, implemented before any candidate (`d2dea12e`)

`cuts/cuts.py` re-instantiates every ruled row over the four `-glass0.25` standard profiles. Each row
is gated on its adopted tier and read descriptively on the other.

- **The tables.** The 0.5 tables' values per tier, read out of `adopted-thresholds.test.ts` by
  following each `*_27_*` alias to the 26.5 literal it equals, so nothing is transcribed by hand.
  They are read on the owner test's gated bed (active, calibration and validation, no probe or
  recorded) with its conditioning predicate on the shape rows. There is no floor.
- **M1** as adopted. **M2** directional: `structureVerdict` transcribed, its reference the pre-fit
  render.
- **C1**: `deriveClause` restated, read beside the pre-fit render and the shipped 0.5 generation.
- **X1** from the bed's own capture tree.
- **L1**: ≤ 0.055 absolute, with growth ≤ 0.005 against the pre-fit render's error.
- **E2** per cell in absolute codes (W42 Decision Log 5e as declared in `activeBandAndE2`), over
  W38's bins and population rule restated for the 0.25 rows. A bin worse by more than 1 code is
  listed and never gated.
- **S1 as R2**, over the fixed population (183 WebGPU and 125 CSS cells on `interiorMean`): sign on
  every cell, and the median ratio pooled over the four profiles per tier in [0.8, 1.2].

`cuts/bed.py` is W42's candidate-admission mode carried to W43's two scratch beds. W43 G0 (f) made a
candidate a complete declaration that `compare` refuses into a stage, so neither bed can be a stage.
- **prefit:** every row stamped `crossPosition=shipped-glass0.5-against-glass0.25` and naming the two
  shipped 0.5 documents at their live hash.
- **candidate:** every row naming one declared candidate document at its hash, with its endpoint
  files re-hashed.

Holdout rows refuse.

### 2. The pre-fit render (`f2d9fcb2`)

- **The route.** The shipped 0.5 documents were drawn on all 1,016 non-holdout cells of the four
  0.25 profiles, on both tiers, in **strict shipped mode under `--cross-position`** with the
  canonical recipe's flags.
  - The charter's "in candidate mode" was not available: candidate mode refuses a candidate whose
    name or endpoint keys are a shipped document's, by design ("A shipped material is read in strict
    mode").
  - G0's relabelled 0.5 content under scratch 0.25 keys would draw the same pixels but erase the
    stamp X45 requires on exactly this comparison.
- **The runtime-base identity.** 610 of 610 comparable captures are byte-identical to the canonical
  0.5 web tree. The 406 others are cells the 0.5 generation never read: the recorded cells and the
  unread probe cells.
- **The anti-null, measured.** G2's offline unmoved-endpoint reading equals the rendered
  `interiorMeanWeb` on 599 of 599 cells, worst difference 0.0.

### 3. The rehearsal: the unmoved endpoint on every cut (`f2d9fcb2`)

**WebGPU:**
- the tables, M1, M2, C1, X1 and E2 pass;
- L1 has 27 absolute misses, all light, worst 0.1056. That is Apple's darker 0.25 body and the
  fit's target;
- S1/R2 fails as an unmoved endpoint must: 145 of 183 wrong sign, median ratio −0.000. G2's
  perfect endpoint passes beside it at 1.056.

**C1** reproduces the shipped 0.5 readings cell for cell. Span 160 gains one contributing cell per
bed at 0.25, 8 against 7.

**CSS, descriptive:**
- one table row was already missed: 1x light `checkerboard__rrect-ml__rest`, ssimMean 0.8777
  against ≥ 0.9;
- C1 reads 0.0054 at dark span 128, as the shipped 0.5 CSS rows do;
- X1's integer mask is missed on 158 cells (the analytic mask is clean).

**No cut fails by construction.**
- Against a perfect endpoint every row is stated relative to Apple and passes, except S1 as
  chartered, which R2 already restates.
- No pre-fit failure rests on a leaf the ruling holds.

So there was no STOP.

### 4. The fit (`950ae6d3`, `553968f0`)

Fitted on the calibration set, with validation as the transfer. The path, every step rendered:
- c01 (the light tone rows moved by Apple's own change at each knot);
- the probes c01a (`tintAlpha`), c01s, c01d and c01g (scatter);
- nine Jacobian probes j-* (+0.02 on one tone ordinate in both light documents);
- c02, c03a and c03b;
- **c05**.

c04 was stopped before any row because it named one leaf at its own 0.5 value. The comparison twin
c05t is c05 without the structure step. What the probes measured:

- **`tintAlpha` moves structure, not level.** −0.12 raised the light interior spread and transfer
  slope ×1.18–1.22 everywhere, and moved the level by under 0.001: the tone solve holds the level.
- **One tone function cannot follow Apple on both photo and the thin checkers.** The thin row's
  anchor at 0.425 governs both the photo and the pitch-16 checkerboard thin cells, with J ≈ 0.95 for
  each.
  - Apple's 0.25 darkens the photo thin body by 0.037–0.043 and leaves the thin checkers almost
    unmoved (−0.0025).
  - Following the photo (c01) took the thin checkers to −0.054/−0.057, an L1 absolute and growth
    miss.
  - The constrained solve (`fit/solve_tone.py`, L1's clauses as constraints with a 0.003 margin)
    holds that anchor 0.005 below its 0.5 value. The photo thin rest cells stay +0.034/+0.044 too
    bright.
  - This is the structural miss the charter predicted (Design, "The w-test"): Apple's hinge lifts a
    checker's dark squares toward the wide term, and vitrea's two-sided form has no such term.
- **The impulse anchor and the black branch are not identified on calibration**, because the
  untinted impulse cells are validation cells. They keep c01's value, Apple's own change at that
  knot (−0.0527 / −0.0542). On validation the light impulse cells read −0.006 / +0.014 (rest) and
  −0.012 / −0.002 (receded).
- **The dark thick row is bounded by L1's growth clause.** c02's knot-2 step (+0.0098) failed
  growth on three dark checkerboard rrect-md cells (+0.0086 / +0.0065 / +0.0089). c05 takes +0.004
  active and +0.003 receded, and +0.0064 at knot 1.
- **The dark scatter is held at its 0.5 values.** The probes and c02 found no net gain:
  - log-structure error at rest went 0.895 → 0.883 / 0.839, and receded 0.864 → 0.875 / 0.912;
  - c02's step raised the dark receded thick checker structure to ×1.74;
  - c02's step failed E2 on dark checkers.

  The dark photo body's flatness (×0.2–0.4 of Apple's structure) is the held `tintAlpha` 0.9, as
  at 0.5.
- **The structure step stays.**
  - The step is `tintAlpha` 0.46 → 0.30, `sizeScatterFloor2x` 1.0 → 0.6 and the light receded
    `sizeScatterFloor` 0.7 → 1.0.
  - The 1x floor stays at 0.25: c02's 0.15 added E2 failures on 1x checkers.
  - The receded thin ramp starts stay at 0.55 / 0.7: c03a's lower values failed M2 on the 1x photo
    rrect-sm inactive cell, moved away from Apple.
  - The twin c05t reads worse on every gated row: L1 2 absolute misses, M2 2 failures, E2 65
    failing, S1 0.814.

**Decision Log 7 items 4 and 5 hold.** M1 passes (WebGPU medians 0.984 / 0.935 light, 1.055 /
1.066 dark), so `bodyChromaRetention` holds. No tint cell misses a gate, so `tintShadeLight` holds.
The light receded tint residual falls from +0.053 to +0.023 OKLab L by the tone alone, and is named
in §6. Every rim, highlight, outerShadow and lens leaf holds. C1 reads identically to the pre-fit on
every cell.

### 5. Candidate c05

The four documents are patches over the unmoved `DEFAULT_MATERIAL_PROFILE`; each receded one is a
difference over its scheme's new active document. Each names exactly its 0.5 twin's leaves (X44,
pinned by the extended export test), at the `-glass0.25` keys. Declaration
`fit/candidates/c05/candidate.json`, sha256 `95388218f94d…`.

| endpoint | file sha256 | resolvedMaterialSha256 | leaves moved from the 0.5 twin |
| --- | --- | --- | --- |
| active light | `23ccc6959a2e…` | `50430fa62c1120bd` | `backdropToneResponseThin` [0.214, 0.2835, 0.5383, 0.937] → [0.1613, 0.2201, 0.5336, 0.9366]; `…Thick` [0.242, 0.3074, 0.5554, 0.957] → [0.1871, 0.2338, 0.5159, 0.9401]; `backdropToneBlackThin`/`Thick` 0.23074 → 0.17804; `optics.regular.tintAlpha` 0.46 → 0.30; `sizeScatterFloor2x` 1.0 → 0.6 |
| active dark | `54f94dffbe8f…` | `b074fc6913a91c66` | `backdropToneResponseThick` [0.031, 0.035, 0.169, 0.196] → [0.031, 0.0414, 0.173, 0.196] |
| receded light | `d4e316d942ec…` | `5d8680980b7aeb55` | `backdropToneResponseThin` [0.1647, 0.2809, 0.4775, 0.8293] → [0.1105, 0.2045, 0.4217, 0.8117]; `…Thick` [0.1442, 0.2823, 0.4695, 0.832] → [0.0894, 0.231, 0.4288, 0.8086]; black 0.23455 → 0.18035; `sizeScatterFloor` 0.7 → 1.0 |
| receded dark | `57f5f31f866e…` | `280f0fddf014e0f6` | `backdropToneResponseThick` [0, 0.0155, 0.164, 0.186] → [0, 0.0155, 0.167, 0.186] |

The CSS mapping is the 0.5 one, unchanged.

### 6. Every cut on c05, both tiers (`read/c05-cuts.*`)

| cut | tier | 1x light | 2x light | 1x dark | 2x dark | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| tables | WebGPU | 0 / 26 | 0 / 26 | 0 / 10 | 0 / 10 | PASS |
| tables | CSS | 1 / 26 | 0 / 26 | 0 / 10 | 0 / 10 | 1 miss (pre-existing) |
| M1 | WebGPU | R 0.86–1.30 | 0.84–1.22 | 0.83–1.14 | 0.97–1.20 | PASS |
| M2 | WebGPU | 8 named | 9 named | 0 | 0 | 17 named, 0 failures |
| C1 | WebGPU | 0.0006 / 0.0021 / 0.0004 | 0.0007 / 0.0021 / 0.0006 | 0.0013 / 0.0035 / 0.0012 | 0.0012 / 0.0038 / 0.0011 | PASS, = pre-fit |
| X1 | WebGPU | 0 / 65 | 0 / 65 | 0 / 56 | 0 / 56 | PASS |
| L1 | WebGPU | max 0.0451, growth +0.0030 | 0.0439, −0.0004 | 0.0453, +0.0035 | 0.0491, +0.0036 | PASS, 4 UNMEASURED (as at 0.5) |
| E2 | WebGPU | 28 / 82 | 17 / 82 | 9 / 62 | 8 / 62 | 62 fail; mean −1.66 codes |
| S1 (R2) | WebGPU | 0.942, 3 wrong | 0.992, 5 wrong | 0.314, 3 wrong | 0.311, 4 wrong | pooled 0.877, 15 wrong sign |
| S1 (R2) | CSS | 0.936, 4 wrong | 1.051, 2 wrong | 0.082, 4 wrong | 0.117, 1 wrong | pooled 0.874, 11 wrong sign |

On the CSS tier the descriptive readings are as follows:
- M1 medians are 1.18 / 1.12 light;
- M2 has 17 named misses and 1 failure: 2x light `photo__rrect-sm__inactive`, ungated on this tier;
- L1 has three CSS-only misses, among them a growth of +0.028 on 1x light
  `photo__toolbar-group__inactive`;
- X1's integer mask is missed on the same 158 cells as at the pre-fit.

**The misses put to the user** (`read/misses.md`), before any freeze or holdout:
- the CSS table row above;
- the 17 M2 named misses, each toward Apple and none past it;
- the 62 E2 cells, 14 of them rrect-lg. The tone change alone fails 65 (the twin), so they are the
  body moving at the edge, not the structure step;
- S1's 15 / 11 wrong-sign cells. S1 is adopted only at the landing.

### 7. The CSS tier, derived; the pins extended

The CSS tier draws c05 from the same four documents, with the 0.5 crossing unchanged; no CSS
constant was refit.

`tier-coherence.test.ts` gains a block over the candidate `fit/final.json` names (c05):
- the merged receded patch resolves to the renderer's material;
- one tone target on both tiers, black end included;
- one scatter thickness and σ per span, scale and fold;
- the tint shade mirrored;
- each endpoint's retention a recorded CSS residual.

`macos27-profile-export.test.ts` gains a block holding each candidate endpoint to exactly its 0.5
twin's leaves at the 0.25 key, its digests reproduced by the driver's reader, and one crossing. The
generated module's own pin lands with the module at the landing.

### 8. Clause 11 (`close-checks.txt`)

- The 26.5 freeze reads 1,818 and X41 reads 911.
- The six shipped digests are unchanged: `be13dae45098fc89` / `2a4323f33df8d799` /
  `b0d0d8dacc6a03af` / `7c454858a3cbad5b` and `b2b570e4adcea8fb` / `874be66ea501621b`.
- 34 of 34 goldens pass on the real adapter, and `tuned-profiles.test.ts` 14 of 14.
- The calibration package reads 857 passed and 1 skipped; lint exits 0.
- `profiles/`, every `src/`, `apps/` and the generation files are unchanged against `origin/main`.

### 9. Gaps, each recorded

- **The photo thin body follows Apple's darkening only to the extent L1 allows.** The light photo
  thin rest cells stay +0.034/+0.044 too bright, and S1's photo-thin cells under-follow. The cause is
  one tone function for two backdrops Apple separates by a one-sided hinge (§4). That is the next
  structure wave's.
- **The dark scheme under-follows Apple's slider change** (S1 per-profile medians 0.31). Apple's
  dark body brightened at spans 128 and 160, by +0.042 on the light-solid inactive cells, which are
  probe cells. The dark thick row at the light-solid anchor and the span law beyond 96 are not
  identified on the calibration set.
- **The dark photo body is flat** (×0.2–0.4 of Apple's structure on both positions): `tintAlpha`
  0.9 is held by the ruling. This is a 0.5-era gap, unmoved.
- **The light receded checkers are over-structured**, ×2.1–2.2 of Apple's 0.25 (×1.4–1.6 at the
  pre-fit; ×1.8–2.9 at 0.5). The receded document inherits the active `tintAlpha` and names no
  transmission leaf of its own (X44). Lowering its thin ramp starts fails M2.
- **The light receded tint** reads +0.023 OKLab L too light on average (+0.053 at the pre-fit).
  `tintShadeLight` is held because no tint cell misses a gate (item 5).
- **The black branch and the impulse anchor are unidentified on calibration** and carry Apple's
  measured change.
- **The rrect-lg exterior edge** (G2's up to 112 codes, the capture-scale step): 14 of the 62 E2
  failures are rrect-lg.
- **E2's per-cell rule has no tolerance.** A body change fails a cell by any increase, including
  +0.002 codes on 2x dark checkers. Its bins are recorded.

### 10. What is not claimed

- No document is sealed and no stage exists. The holdout was never read.
- c05 is a scratch candidate. The freeze, the final stages, the gate on them and the holdout are
  the landing's, after the user rules the misses in §6.
- No accessibility state at 0.25 was read; the accessibility leaves carry over unmeasured.
