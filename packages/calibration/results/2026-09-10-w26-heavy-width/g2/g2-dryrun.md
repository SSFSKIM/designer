# W26 G2 — what the dry run read

`g2-declaration.md` was committed at `6f901f0`, before this child rendered a pixel. Everything below
is what the run then read. The declaration is not amended: where it predicted wrongly, the
prediction stands beside the reading.

**The headline, and it is not the one the declaration expected.** The two constants land cleanly on
the GPU tier — the fidelity target moves by +0.00001 at worst on any calibration group, its angular
rim reads are identical to five decimals, X5 is a fifth of its bound and S15 fires exactly where and
only where the declaration said it would. **The cost is on the CSS tier and it is large: thirteen of
the fourteen thick regression floors go under, and twelve of the thirteen are `dom` rows that only
clause 7 reaches.** The counterfactual is measured rather than argued (§9): with the two constants
landed and clause 7 declined, **one** floor is breached instead of thirteen. That is the ruling this
gate hands the parent, and it is a ruling about the CSS derivation rather than about the width.

Evidence beside this file: `delta-e.txt` and `delta-e-holdout.txt` (the group means),
`byte-identity.txt` (S6, S10), `stops.txt` (S1, S2, S7, S11a), `g2-stops.txt` (S11b, S12, S13, S14),
`probe.txt` (X5 and S14 on both tiers, and the per-span table), `s15.txt` (S15 on the family
reader), `floors.txt` and `floors-gpuonly.txt` (the fourteen floors and the counterfactual),
`gate-calval.txt`, `gate-whole.txt` and `gate-gpuonly.txt` (the gate), `clause3.txt` (W25 clause 3),
`canonical-reads/` (W23's contour reader and W24's angular reader, both beds, both tiers, before and
after), `g2-goldens-attribution.txt` and `g2-goldens-regen.txt`, `g2-digests.txt` and
`g2-digests-probe.txt`, and `sheets/g2-1x.png` and `sheets/g2-2x.png`.

---

## 1. How it ran

Three columns, in the declared order, one capture process at a time, all to scratch under
`/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2/cand/`, everything in **this worktree** so that the
capture is this branch's code by construction:

| column | runs | wall | exits |
| --- | --- | --- | --- |
| the bed, calibration + validation, 6 profiles × 2 tiers | 12 | 11:13–11:18 | 12 × 0 |
| the probe set, 4 standard profiles × 2 tiers | 8 | 11:18–11:29 | 3 × 0, 5 × 1 |
| **the holdout, once (X3)**, 6 profiles × 2 tiers | 12 | 11:34–11:36 | 11 × 0, 1 × 1 |

The non-zero exits are the bed's own and not this run's: the GPU probe runs refuse a
declaration-conformance reading on rows whose backdrop has no resolvable step edge, and W26 G1c's
ladder produced the same pattern at every rung; the one holdout non-zero is
`1x-light-increased-contrast / css` on `hc-text__capsule-button__rest`, which W25 G4 recorded as the
bed's one expected non-zero exit. Every cell is written in all three columns.

A fourth run preceded them and is the one control this wave did not already have: `c0css`, the probe
set on the **CSS tier at the 0.14.0 code**, captured before the landing edit. G1c's `c0p` is the GPU
control and its `c0b` the bed's, both captured on this machine at the 0.14.0 material.

Nothing canonical was written: `packages/calibration/results/matrix.json`, `web-captures/`,
`apps/reference-apple/fixtures/` and `scenes.json` were read-only throughout, and the canonical
`web-captures/` in the shared checkout was READ as the control for the holdout column and for
W25 clause 3, since no scratch rung of this wave has a holdout capture.

## 2. The stops

| stop | reading | verdict |
| --- | --- | --- |
| **S1** untinted row ΔE +0.001 / ssim −0.005 | worst **+0.00122 / −0.00632**, on two rows, both CSS `checkerboard__rrect-ml` (1x and 2x light) | **FIRES on 2 of 340 rows** |
| **S2** tinted body 0.002 | worst **0.00045** | clear |
| **S3** calibration ΔE group mean +0.0001 | GPU worst **+0.00001**; CSS 1x dark **+0.00013** and reduced-transparency **+0.00017** | **FIRES on 2 CSS groups; clear on every GPU group** |
| **S4** a golden moved for another reason | 0 pixels off any surface on any of the thirteen scenes; the seven movers are the seven with structured backdrops | clear |
| **S5** a constant whose rows do not separate it | the ladder's mapping, slope 0.995–1.111, rms 0.03–0.06 device px over seven rungs, the two off-diagonal rungs separating the scales exactly (claims §5.122 §3) | clear |
| **S6** a CSS capture moved without an explanation | 44 of 85 moved, 41 held; the holds are the flat solids and the dpr-2 cells at span ≤ 96 where the width moves 1 % (4.455 → 4.500 CSS px). No alpha channel moved anywhere | clear |
| **S7** collapsed body 0.002 | worst **0.00003** | clear |
| **S8** the user's eye | `sheets/g2-1x.png`, `sheets/g2-2x.png` | the user's |
| **S10** a cell the constants cannot reach that moves | 63 of 85 GPU captures moved; **the 22 that held are exactly the flat-solid backdrops** (`dark-solid`, `light-solid`) plus one tinted capsule — a flat backdrop reads the same through a 13.418 px kernel and a 9 px one | clear |
| **S11a** W23's straight spans, 0.005 | worst **0.00113** | clear |
| **S11b** W24's angular bins, 0.005 | worst **0.02560**, 11 bins, **all of them on ONE cell of the CSS tier** (1x light `dark-solid__rrect-md`). Every GPU row is identical to five decimals before and after. Read as ERROR the firing cell IMPROVES (mean 0.05690 → 0.05505) | **FIRES on movement, improves on error** |
| **S12 / X5** a thin cell moved by 0.001 ΔE | canonical bed worst **+0.000190** over 114 thin cells; probe set worst **0.00021** (GPU) and **0.00033** (CSS) over 81 thin cells each, 0 firing | clear, on both tiers |
| **S13** a golden moved off a surface | **0** on every scene | clear |
| **S14** a probe row worse by 0.002 ΔE | **33 of 408 rows fire**, worst **+0.02377** (2x dark `checkerboard-32__rrect-lg`, CSS); GPU worst **+0.01590** (1x dark `checkerboard-64__rrect-lg`) | **FIRES, as declared for the dark scheme, and on 2x light large spans besides** |
| **S15** the heavy σ further from the reference's on the family reader | **2 of 6 fitted cells**, both `rrect-md` at dpr 2 (light 0.0641 → 0.1185, dark 0.0315 → 0.0918); the mean over six cells 0.2750 → **0.0693** | **FIRES on exactly the two the declaration named** |

### 2.1 S15, cell by cell — the reading the mechanism is answerable to

`s15.txt`. The reference is re-read on this run's own captures and it reproduces claims §5.122 §4 to
the digit, which is the check that the dry run and the rung are the same measurement:

| surface | dpr | scheme | ref σ | ref sharp | 0.14.0 | candidate | \|log\| before | after | S15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | 1 | light | 9.300 | 1.30 | 13.450 | **8.800** | 0.3690 | **0.0553** | clear |
| `rrect-lg` | 1 | light | 8.050 | 1.55 | 13.400 | **8.500** | 0.5096 | **0.0544** | clear |
| `rrect-md` | 2 | light | 7.550 | 1.35 | 8.050 | 8.500 | 0.0641 | 0.1185 | **FIRES** |
| `rrect-lg` | 2 | light | 9.200 | **4.00** | 12.300 | **8.500** | 0.2904 | **0.0791** | unconditioned |
| `rrect-md` | 1 | dark | 9.150 | 1.30 | 13.450 | **9.000** | 0.3852 | **0.0165** | clear |
| `rrect-md` | 2 | dark | 7.800 | 1.40 | 8.050 | 8.550 | 0.0315 | 0.0918 | **FIRES** |

The `rrect-lg` 2x light row is UNCONDITIONED by Decision Log 4 (a)'s own test — its reference
two-component fit returns a sharp component of 4.00 device px, so the reader has split one wide
kernel — and S15 does not apply to it; it improves anyway. The two firings are the 2x span grading
one width per source cannot carry, measured at 1.66 device px (claims §5.122 §3) and chosen
knowingly at Decision Log 2 (f). **The width is right at dpr 1 on every cell and at dpr 2 on the
large span; it is 10–12 % wide on the 96-span surface at dpr 2.**

## 3. The bed, group by group

`delta-e.txt`, against G1c's `c0b` — the 0.14.0 material captured on this machine, both tiers.

| profile | GPU calibration | GPU validation | CSS calibration |
| --- | --- | --- | --- |
| 1x light | 0.00321 → **0.00321** | 0.00241 → 0.00240 | 0.00709 → 0.00717 |
| 2x light | 0.00326 → **0.00326** | 0.00248 → 0.00248 | 0.00738 → 0.00744 |
| 1x dark | 0.00393 → **0.00393** | 0.00244 → 0.00244 | 0.00633 → 0.00646 |
| 2x dark | 0.00395 → **0.00390** | 0.00297 → 0.00300 | 0.00657 → 0.00657 |
| 1x light reduced-transparency | 0.00171 → 0.00173 | 0.00110 → 0.00110 | 0.00447 → 0.00464 |
| 1x light increased-contrast | 0.00793 → 0.00794 | 0.00862 → 0.00862 | 0.01301 → 0.01293 |

**The GPU tier is where the wave declared its fit and it does not move the canonical bed at all** —
no calibration group by as much as 0.00001, and 2x dark improves by 0.00005. That is not a null
result: the canonical bed carries four thick spans and 34 thin or mid cells per profile, and the
width's effect concentrates where the backdrop has structure at the span the size law calls thick.
The probe set is where it shows.

### 3.1 The per-span table, on both tiers

`probe.txt`, mean over the span's untinted probe cells, control → candidate. The GPU rows reproduce
claims §5.122 §5c **to the digit** on all twelve entries, which is the reproduction check that the
landing draws what the rung drew.

| profile | tier | span 96 | span 128 | span 160 |
| --- | --- | --- | --- | --- |
| 1x light | GPU | 0.00475 → **0.00420** | 0.00672 → **0.00583** | 0.00905 → **0.00855** |
| 1x light | CSS | 0.01634 → **0.01624** | 0.02276 → **0.02259** | 0.02212 → 0.02222 |
| 2x light | GPU | 0.00395 → 0.00395 | 0.00603 → **0.00590** | 0.00812 → 0.00934 |
| 2x light | CSS | 0.01659 → 0.01659 | 0.02329 → 0.02373 | 0.02179 → 0.02406 |
| 1x dark | GPU | 0.00447 → 0.00520 | 0.01703 → 0.01892 | 0.02173 → 0.02404 |
| 1x dark | CSS | 0.01406 → 0.01478 | 0.02953 → 0.03205 | 0.03259 → 0.03564 |
| 2x dark | GPU | 0.00612 → 0.00628 | 0.02116 → 0.02242 | 0.02582 → 0.02923 |
| 2x dark | CSS | 0.01525 → 0.01525 | 0.03434 → 0.03647 | 0.03617 → 0.04093 |

The light scheme improves at every thick span at dpr 1 on both tiers; the dark scheme worsens at
every thick span on both, which is Decision Log 6 (e) reproduced with the CSS tier's column beside
it for the first time. **The dark bed's thick-span error is two to three times the light bed's
before and after**, and what the 13.418 was masking there is still not identified.

## 4. The fourteen thick regression floors — 13 breached, 1 held

`floors.txt`. **This is the gate's own table read directly off the matrices**, because
`adopted-thresholds.test.ts` stops at the first failing assertion per profile and reported three
where thirteen are under. The direction is the metric's: `ssimMean` and `silhouetteIoU` are `≥`
floors, `contourDistance*` are `≤` floors.

| tier | set | scene | profile | metric | floor | 0.14.0 | candidate | |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dom | calibration | `checkerboard__rrect-md` | 2x light | ssimMean | 0.9142 | 0.91539 | 0.91539 | **held** |
| dom | calibration | `checkerboard__rrect-ml` | 1x light | ssimMean | 0.8748 | 0.87608 | 0.87037 | BREACHED |
| dom | calibration | `checkerboard__rrect-ml` | 2x light | ssimMean | 0.8779 | 0.87894 | 0.87262 | BREACHED |
| dom | holdout | `checkerboard__glass-over-glass` | 1x light | ssimMean | 0.8604 | 0.86355 | 0.86005 | BREACHED |
| dom | holdout | `checkerboard__glass-over-glass` | 2x light | ssimMean | 0.8677 | 0.86870 | 0.86330 | BREACHED |
| dom | holdout | `checkerboard__rrect-lg` | 1x light | ssimMean | 0.8693 | 0.87056 | 0.85993 | BREACHED |
| dom | holdout | `checkerboard__rrect-lg` | 2x light | ssimMean | 0.8712 | 0.87233 | 0.84943 | BREACHED |
| dom | holdout | `checkerboard__glass-over-glass` | 1x dark | silhouetteIoU | 0.9070 | 0.90804 | 0.84120 | BREACHED |
| dom | holdout | `checkerboard__glass-over-glass` | 1x dark | contourDistanceMean | 1.0658 | 1.03304 | 1.26287 | BREACHED |
| dom | holdout | `checkerboard__glass-over-glass` | 1x dark | contourDistanceP95 | 8.3500 | 8.25000 | 9.00000 | BREACHED |
| **texture** | holdout | `checkerboard__glass-over-glass` | 2x dark | silhouetteIoU | 0.9257 | 0.92707 | 0.90362 | BREACHED |
| dom | holdout | `checkerboard__glass-over-glass` | 2x dark | silhouetteIoU | 0.9038 | 0.92878 | 0.85742 | BREACHED |
| dom | holdout | `checkerboard__glass-over-glass` | 2x dark | contourDistanceMean | 1.8602 | 1.28921 | 2.14273 | BREACHED |
| dom | holdout | `checkerboard__glass-over-glass` | 2x dark | contourDistanceP95 | 13.1000 | 10.00000 | 16.00000 | BREACHED |

**Thirteen of the fourteen, and exactly one is a `texture` row.** The one that held is the only CSS
cell in the table at a span the width barely moves at that scale: 2x span 96, where the composed
heavy layer goes 4.455 → 4.500 CSS px and the capture is byte-identical.

Four of the breached rows are on cells that have LEFT the shape gate at the candidate (the dark
nested pane on the CSS tier at both scales), so the gate itself reports them as floors nothing
reaches rather than as breaches. They are counted here because a floor nothing reaches is not a
floor that held, and their underlying readings are worse in every case.

## 5. The gate

`gate-calval.txt` and `gate-whole.txt`, `VITREA_MATRIX_PATH` pointed at the dry run.

- **Over calibration and validation** (the candidate's rows beside the canonical holdout rows, as
  G1's `g1-gate.py` assembles them): **36 of 38 pass**, and the two failures are the two
  `checkerboard__rrect-ml` dom floors of §4.
- **`PREDICATE_EXCLUDES` MOVES**, which the declaration said it would not, on G1c's evidence. G1c
  gated its calval rows beside the CANONICAL holdout rows and read 38 of 38 with the file untouched;
  it was right about its own column. On this column **one cell enters, 31 → 32**:
  `dom / calibration / checkerboard__capsule-button__rest / 1x-light-reduced-transparency`, whose
  `silhouetteHolesWeb` goes **0 → 6** with the native's still 0. The mechanism is written into the
  file and **the entry is not**: `PREDICATE_EXCLUDES` is read against the COMMITTED
  `results/matrix.json`, which is still the 0.14.0 bed, so a file naming 32 would disagree with the
  only matrix CI has. Re-deriving it belongs to the canonical rebuild, as it did at W25 G3 → G4, and
  the cell is written down so that the rebuild reproduces a stated reading rather than discovers
  one. The mechanism: under `frost: "increased"` the old CSS derivation
  multiplied the heavy width by the frost as well, so on that profile the heavy layer goes
  **24.15 → 9.000 CSS px**, and less blur leaves more of the checkerboard inside the surface for the
  extractor's threshold to read as holes.
- **Over the whole bed including this run's own holdout**: 30 of 38. Three more cells leave the
  shape gate — `dom / holdout / checkerboard__glass-over-glass` at 1x and 2x dark, and
  `texture / holdout / checkerboard__rrect-lg / 2x light` — taking six pinned dom floors out of
  reach, so `PREDICATE_EXCLUDES` would read **35** there. **That file is NOT edited to 35**, because
  no exclusion list makes this gate green: the six orphaned floors fail the
  `every regression floor stands on a genuinely unmet bound` case whatever the predicate says, and
  dropping a floor is a user decision.

## 6. The holdout, read once (X3)

`delta-e-holdout.txt`, against the canonical committed `results/matrix.json`.

| profile | tier | before | after | | profile | tier | before | after |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1x light | webgpu | 0.00898 | 0.00900 | | 1x light | css | 0.01576 | 0.01599 |
| 2x light | webgpu | 0.00895 | 0.00930 | | 2x light | css | 0.01616 | 0.01706 |
| 1x dark | webgpu | 0.01325 | 0.01330 | | 1x dark | css | 0.01735 | 0.01802 |
| 2x dark | webgpu | 0.01311 | 0.01338 | | 2x dark | css | 0.01739 | 0.01896 |
| 1x light reduced-transparency | webgpu | 0.00343 | 0.00351 | | 1x light reduced-transparency | css | 0.00751 | 0.00804 |
| 1x light increased-contrast | webgpu | 0.02042 | 0.02043 | | 1x light increased-contrast | css | 0.04561 | **0.04503** |

**Eleven of the twelve holdout groups are worse and one improves.** The GPU tier's worst rise is
+0.00035 (2x light) and the CSS tier's +0.00157 (2x dark). The holdout is where the bed's LARGE
spans live — `rrect-lg`, `glass-over-glass`, `hc-text__rrect-md`, `photo__rrect-lg` — so this is the
same reading as §3.1's 2x light span-160 column and §4's floors, on the rows nothing was fitted on.

**This is the wave's one holdout read (X3), taken at the constants of §1 and on nothing else. A
ruling that moves either constant, or that declines clause 7, voids it and needs another.**
Decision Log 6 (d)'s sentence stands beside it: G1b validated its instrument on three holdout
scenes, so this is an untouched check of the FIT and not of the INSTRUMENT.

## 7. W25's carried clauses

**Clause 3 — the nested pane's base: NOT MET, and it moves away.** `clause3.txt`, W25 G0's reader C
(the σ-match) with reader B beside it, on `checkerboard__glass-over-glass__rest`, read once at the
holdout read because the split makes it holdout-only (claims §5.122 §6c) — so this is the wave's
only reading of it and nobody else's.

| profile | native (C) | GPU 0.14.0 | GPU candidate | CSS 0.14.0 | CSS candidate |
| --- | --- | --- | --- | --- | --- |
| 1x light | 1.50 | 2.10 | **2.20** | 1.70 | 1.90 |
| 1x dark | 1.50 | 2.10 | **2.20** | 1.90 | 2.00 |
| 2x light | 16.50 `>bound` | 7.25 | 9.50 `>bound` | 5.75 | 6.00 |
| 2x dark | 20.00 `>bound` | 7.25 | 10.00 `>bound` | 5.50 | 5.75 |

At 1x the base reads 2.10 → **2.20** device px against a reference of 1.50 — 40 % over before and
47 % over after, so the clause is missed and the miss grows. At 2x the reference itself is past the
reader's validated bound on this backdrop (4 device px at 1x, 8 at 2x), which is what W25 recorded
and this wave does not change. **The GPU rows' residual is 0.78–0.82 of the region's own standard
deviation**, so those σ are weakly identified and are quoted with that; the CSS rows are better
conditioned (0.10–0.40) and move the same way.

**Clause 4 — the collapsed dot: not met at the control either**, carried from claims §5.122 §6b
(reference 6.167 CSS px, control 4.037, candidate 4.262 at 1x). Not re-read here: it is an
`impulse__capsule-button` reading and nothing in this run moves it beyond what G1c measured.

## 8. The goldens

`g2-goldens-attribution.txt`, taken before a golden byte was rewritten; `g2-goldens-regen.txt` for
the regeneration. Seven of thirteen scenes moved, by 1–3 code values, all of it on a surface:
**`off` is 0 on every scene**, which is S13. The six that held are the flat or nearly flat backdrops
— a width can only be seen where there is structure to blur — and `highlight-press-glow` holds at 0
pixels for the thirteenth wave running. `W26_HASHES` records the seven with that reasoning;
`W25B_HASHES` and `W25_HASHES` stay beside it. `PLACED_CHECKERBOARD_COVER_HASH` moves with them.
`test:golden` **33 of 33** before and after the regeneration, in the foreground, GPU guard clear.

### 8.1 And what the sheets actually show, which the metrics do not agree with everywhere

`sheets/g2-1x.png` and `sheets/g2-2x.png`, four panels: native | GPU at 0.14.0 | GPU at the
candidate | CSS at the candidate, on the canonical thick cells and on the coarse-checkerboard probe
rows the width was fitted on, with the nested base at 2× and the impulse dot at 4× again beneath
them.

**On the coarse checkerboards the candidate is visibly closer to Apple, at both scales.** The native
panel shows the pattern still legible through a 160-span surface; 0.14.0 washes it appreciably
flatter; the candidate shows it about as legibly as the native does. That is the fit, in a picture,
and it is the same direction on both tiers.

**And it is worth writing down that the CSS panel does not look wrong on the rows whose floors it
breaks.** On the 2x `checkerboard-32__rrect-lg` row the CSS tier passes slightly more structure than
the GPU tier does and sits, by eye, no further from the native than the GPU panel; its `ssimMean`
nevertheless falls 0.87233 → 0.84943. SSIM on a checkerboard interior is sensitive to exactly the
structure this wave restores, so the floors of §4 measure a real change and are not, on their own, a
statement that the picture got worse. **This is the user's to rule (S8, X6)** and it is the reason
the eye's row is on the sheet next to the number.

## 9. The counterfactual, because the floors' verdict asks for one

`g2-gpuonly.py`, `floors-gpuonly.txt`, `gate-gpuonly.txt`. The two tiers render independently and a
CSS capture does not read the GPU tier's material — it reads the profile document, and the two
constants reach the CSS tier ONLY through clause 7's code change. So the bed a landing without
clause 7 would produce is not a hypothesis: it is this run's texture rows beside the 0.14.0 bed's own
dom rows, and it can be gated.

| landing | thick floors breached | of 14 |
| --- | --- | --- |
| the two constants **and** clause 7 (what this gate ran) | **13** | 1 held |
| the two constants **without** clause 7 | **1** | 13 held |

The one that survives either way is `texture / holdout / checkerboard__glass-over-glass / 2x dark ::
silhouetteIoU`, 0.92707 → 0.90362 against a floor of 0.9257 — the GPU tier's own, on a cell whose
web silhouette already carried **39 holes against the native's 0** at 0.14.0 and now carries 45. The
extractor was refusing on that cell in all but name before this wave; the tracker already carries
"the contour instrument's refusal on flat-cornered dark squares".

(The counterfactual matrix's cross-tier coherence rows are stale by construction — a dom cell's
coherence axis was measured against the 0.14.0 GPU capture — and its four coherence failures are
that and not a reading. Nothing in `REGRESSION_FLOORS` or in the adopted bounds reads that axis.)

## 10. What this hands the parent

The wave's charter is the least possible gap to macOS, the GPU tier is the fidelity target (wave
Decision Log 23), and clause 7 asks the CSS tier to derive what it can. On this evidence those two
pull apart for the first time, and the choice is the parent's and the user's:

1. **Land both, and re-pin the twelve dom floors.** The CSS tier would then draw the GPU tier's own
   width — one quantity across the seam for the first time — at the price of a user decision on
   twelve floors and of four cells leaving the shape gate. Every one of those rows already MISSES
   its adopted bound and is held by decision, with the rim band the CSS tier has no lens to draw
   recorded as the mechanism (claims §5.72 §5); this would deepen a miss rather than create one.
2. **Land the two constants and decline clause 7 this wave.** One floor moves instead of thirteen,
   nothing leaves the shape gate on the calibration column, and the CSS tier keeps deriving its
   heavy width from three constants that grade nothing on the tier it has to agree with — which is
   an incoherence to record in the ledger and to charter, not to hide.
3. **Land nothing and re-open the width.** The evidence against this is §2.1 and §3.1: the width is
   right at dpr 1 on every cell of the instrument of record, the objective falls 0.275 → 0.069, and
   the light bed improves at every thick span at dpr 1 on both tiers. What is wrong is not the
   number.

**This child does not rule it.** The dry run's job is to declare, run and read; the landing is G3's
and the user's (X6). What is recorded beside the choice: the holdout read of §6 belongs to
configuration (1) and would have to be re-taken for (2), because a CSS capture that does not move
still changes the bed the holdout's group means are taken over.

## 11. What could not be read

- **The 2x reference's own heavy width on the nested pane**, and its σ-match at either scale at 2x:
  the reference is past reader C's validated bound on that backdrop (§7), as W25 recorded.
- **Why the dark bed prefers a heavy component half again wider than its own reference's** (§3.1,
  Decision Log 6 (e)) — unchanged and unidentified, now with the CSS tier's column beside it.
- **Whether the accessibility frost should reach the heavy width.** This wave measured that it does
  not, on either tier, and that the CSS capsule on the reduced-transparency profile leaves the shape
  gate as a result (§5). It did not measure what folding it in would do, because that is a material
  change no rung of this wave declared or fitted.
- **The sharp component** (1.30–1.55 device px against vitrea's ≈1.6), recorded and not fitted —
  Decision Log 5 (e) gives it to the wave after this one.
- **What no convolution explains**: about one display code RMS of Apple's interior, unchanged by any
  width fitted on this bed (claims §5.121 §6).

## 12. The digests

`g2-digests.txt` — both profile documents' file digests
(`ceeeb3863d3f5fce…` light, `e89110b46797b0c8…` dark), their resolved fingerprints
(`b2b570e4adcea8fb` and `eee7294f409966d7`) and the full resolved patch of each, then the sha256 of
every one of the **229** canonical captures at the frozen configuration, none missing.
`g2-digests-probe.txt` carries the **408** probe captures the same way. G3 reproduces both sets from
the main checkout.
