# W26 G2 spike — the extractor's asymmetry on the nested pane, measured

**Deliverable: findings. No instrument change lands on this branch.** The spec, the ledger and
`src/silhouette.ts` / `src/metrics/shape.ts` are untouched; everything here is scratch beside the
evidence it reads. Every canonical input — `results/matrix.json`, `web-captures/`, `fixtures/`,
`scenes.json` — was read and never written. The candidate column is G2b's scratch capture of the
ruled configuration at `/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2/g2b/web-captures`, also
read-only.

The cell: `texture / holdout / checkerboard__glass-over-glass__rest /
apple-macos-26.5-2x-dark-standard`, `silhouetteIoU` 0.92707 → 0.90362 against a floor of 0.9257
(Decision Log 7 (f)–(g); `g2-dryrun.md` §14.5).

## 0. The instrument, transcribed and proved

`w26extractor.py` is a Python transcription of `component-region.ts`, `silhouette.ts` and the shape
metrics of `metrics/shape.ts`. It exists because the rule has to be scanned over parameters the TS
harness only exposes through a full capture run, and it is worth nothing unless it is the same
instrument. `validate.py` recomputes **every one of the 613 shape-bearing cells of the committed
0.14.0 `results/matrix.json`** from the canonical captures and compares seven rows per cell:

```
cells matched  613
cells differing 0
cells skipped (captures absent / size mismatch) 0
worst IoU |delta| 0.000e+00
```

Areas, hole counts, `silhouetteIoU`, `contourDistanceMean` and `contourDistanceP95` reproduce
bit-for-bit. Everything below is measured through that replica (`validate.txt`).

## 1. The rule, stated

There is **one** extractor and both sides go through it (`cli/measure.ts` builds `extractor` once
and calls `extractSilhouette` twice). Where a background raster exists — it does on every cell of
this bed — the rule is:

> a pixel is inside iff it lies in the **declared component region** (`componentRegion`, the scene's
> own geometry rasterised by pixel-centre containment, margin 0) **and** `|Y(pixel) − Y(background
> pixel)| ≥ 0.02` in linear Rec.709 luma, **or** its OKLab a/b differs from the background's by
> ≥ 0.03 (the W11b chroma arm, exactly inert on a neutral capture over a neutral plate — which this
> cell is).

Nothing else. No fill, no morphology, no seed, no per-channel arm, no background estimate, and
**nothing keyed on the native**: the native fixture is not read when the web mask is built, nor the
other way round. The only downstream asymmetry in the axis is that `contourDistance` hole-fills both
masks before tracing (claims §5.15) while `silhouetteIoU` deliberately does not (claims §5.14:
"a hole is a genuine set difference even when it is not an outline difference"). That single choice
is where the whole floor lives.

## 2. The premise in §14.5 is wrong, and the correction is the finding

**The extractor does not recover a hole-free mask from the native.** The committed matrix says so
itself: `silhouetteHolesNative` is **14** on this cell, on both tiers, and the native's silhouette
is the *smallest* of the three — 106 876 px against 0.14.0's 109 698 and the candidate's 107 058, of
a declared region of 112 416 (`anatomy.txt`).

The "native's under-threshold count is higher yet it has no holes" reading in `g2b-nested.txt` came
from a proxy: it thresholded `|luma − 0.5|`, i.e. distance from the checkerboard's *mean*, over a
hand-cut base-pane rectangle. The extractor thresholds against the **background raster pixel by
pixel**, and the checkerboard is exactly 128 000 px at linear 0 and 128 000 px at linear 1 with no
intermediate seam pixel at all (`zones.txt`). The two counts are different quantities; the proxy's
one is not the extractor's.

So there is no asymmetric rule to find. What there is:

| mask | area | excluded inside region | excluded components | holes | largest excluded run |
| --- | --- | --- | --- | --- | --- |
| native | 106 876 | 5 540 | 31 | 14 | 818 |
| 0.14.0 | 109 698 | 2 718 | 51 | 39 | 135 |
| candidate | 107 058 | 5 358 | 57 | 45 | 311 |

and the two excluded sets are **nearly disjoint**: native ∩ candidate = **33 px** out of ~5 400 on
each side. IoU pays for both: `(112 416 − 5 540 − 5 358 + 33) / (112 416 − 33) = 0.90362`, which is
the floor breach to the fifth decimal.

## 3. Where they sit, and why they are disjoint

`masks-4x.png` (native | 0.14.0 | candidate, capture on top, mask below at 4× per CSS px; green =
inside, magenta = a region pixel the extractor excluded) and `zones.txt`:

- **100 % of every column's excluded pixels lie over a BLACK checker cell.** Over a cell at linear
  0 the rule `|own − base| ≥ 0.02` degenerates to `own ≥ 0.02` — an **absolute brightness test**,
  and a dark-scheme glass over black is legitimately that dark. This is the tracker's
  "surface agrees with its backdrop" mechanism in its sharpest form: the backdrop is zero, so
  agreement means darkness.
- **The native loses them under the inner overlay pane** (5 487 of 5 540, 99 %), where its
  double-glazed dark-cell transmission has a median of **0.02029** — one 8-bit code above the rung.
- **Both vitrea columns lose them on the single-glazed base** (0 % under the inner pane), whose
  dark-cell cores dip under while the native's do not; vitrea's inner pane transmits 0.02315 and
  keeps every pixel the native drops there.

Two implementations whose dark-cell floors differ by two thousandths of linear luma, on opposite
sides of the same fence in opposite zones of the same scene. Nothing in the instrument prefers
either.

## 4. The drop is a fence effect, not a shape change — scanned

`scan.txt` scans the extractor's threshold with the native re-extracted at each rung:

```
    thr  nat area  0.14 area  cand area  nat holes  0.14 holes  cand holes  IoU 0.14  IoU cand     Δ IoU
  0.012    112382     112393     112393          0           0           0   0.99990   0.99990   0.00000
  0.014    112374     112392     111304          0           0          33   0.99984   0.99016  -0.00968
  0.016    112369     112389     109290          0           0          43   0.99982   0.97228  -0.02754
  0.018    111663     111923     108298          4          16          42   0.98946   0.95721  -0.03226
  0.020    106876     109698     107058         14          39          45   0.92707   0.90362  -0.02346
  0.024     99996      98318      95648         29          66          69   0.87979   0.86847  -0.01132
  0.030     90858      83716      83232         75          76          76   0.91736   0.91209  -0.00527
  0.040     73420      72603      72465         87          89          88   0.95752   0.95682  -0.00070
  0.080     57825      57085      57932         58          54          54   0.97977   0.98343  +0.00366
```

**Not monotone, and not even single-signed.** The candidate is identical to 0.14.0 below 0.012,
worst at 0.018 (−0.0323, forty per cent worse than at the adopted rung), back inside a thousandth by
0.040 and **better** by 0.080. A real shape difference does not switch sign as a segmentation
threshold sweeps past it; a population crossing a fence does exactly this. The adopted rung 0.02 is
one rung of a spike, and both columns' IoU falls off a cliff there (0.9999 → 0.927 / 0.904) purely
because that is where the dark cells' cores are.

The same scan on hole-filled masks is flat at 0.9998 ± 0.0002 across every rung from 0.002 to 0.035,
with the candidate at or above 0.14.0 at every one.

## 5. The proposed fix

**Take `silhouetteIoU` over a population that excludes every pixel enclosed by a hole of *either*
mask** — the pixels where the extractor's own premise ("anything differing from the background is
the surface") is false, and which it therefore cannot decide. Symmetric by construction, keyed on
neither side, one call site (`cli/measure.ts` passes the region it already has). `silhouetteHoles*`
stay on every cell unchanged, so the artefact is still reported; it simply stops being priced as a
set difference of the surface. That is the same correction claims §5.15 already made for
`contourDistance`, and the tracker's own fix shape ("a hole-fill step declared as part of the
silhouette's definition with its own recovery check", W21 G2c entry).

Three rules were measured against it, all symmetric (`blast.py`, `blast.txt`):

| rule | what it does | cells moved of 613 | Δ min | Δ max | cells DOWN |
| --- | --- | --- | --- | --- | --- |
| `fill` | hole-fill both masks, then IoU | 125 | −0.28657 | +0.35514 | 10 |
| **`drop`** | **IoU over the region minus both masks' holes** | **121** | **+0.00000** | **+0.34606** | **0** |
| `hyst` | hysteresis at extraction: `≥ t`, or `≥ t/2` and 4-connected to such a pixel | 415 | −0.34167 | +0.75300 | 46 |

`fill` is rejected on measurement: hole-filling is a *topological* operation and the two sides'
exclusions differ in topology, not only in position. On `texture / probe /
checkerboard-64__rrect-md__rest / 2x dark` the native's exclusions are 19 206 px enclosed and the
web's 560 px open to the region edge, so filling adds a third of the region to one mask and nothing
to the other: IoU 0.92516 → 0.63859. `hyst` moves two thirds of the bed and drags 46 cells down,
including gated ones (`dark-solid__capsule-button__rest` 0.58333 → 0.24167) — it changes extraction,
so it changes areas, hole counts and the conditioning predicate too. `drop` changes one metric.

## 6. Blast radius of `drop` over the committed 0.14.0 bed

Recomputed from the canonical captures on all 613 shape-bearing cells (`blast.txt`,
`blast-rows.json`).

- **Rows that move: `silhouetteIoU` only.** Extraction is untouched, so `silhouetteArea*`,
  `silhouetteHoles*`, `silhouetteBodies*`, `componentRegionArea`, `contourDistance*` and
  `cornerCurvature*` are bit-identical by construction, and the **conditioning predicate reads areas
  only** — `PREDICATE_EXCLUDES` membership cannot move. So is `ssimBand` / `ssimInterior`, whose
  window is the native silhouette as extracted.
- **121 of 613 cells move, every one of them up**; 492 do not move at all. Median move of the movers
  +0.0032, largest +0.34606. The movers are exactly the artefact class: `checkerboard`,
  `checkerboard-32`, `checkerboard-64`, `checkerboard-lc16`, `hc-text` and the two `mid-dark-solid`
  cells — cells that carry interior holes.
- **No adopted bound moves.** The worst well-conditioned cell of the gated sets per profile and tier
  — the cell each `silhouetteIoU ≥ x` bound is actually set against — is unchanged on eleven of
  twelve rows and rises 0.99481 → 0.99681 on the twelfth. Margins before were 0.06–0.20; nothing is
  near a bound either way.

| profile | tier | bound | base | drop |
| --- | --- | --- | --- | --- |
| 1x light standard | texture / dom | 0.82 / 0.85 | 0.99215 / 0.99840 | unchanged |
| 2x light standard | texture / dom | 0.85 / 0.85 | 0.99037 / 0.99913 | unchanged |
| 1x reduced-transparency | texture / dom | 0.87 / 0.89 | 0.97373 / 0.99672 | unchanged |
| 1x increased-contrast | texture / dom | 0.85 / 0.80 | 0.99713 / 1.00000 | unchanged |
| 1x dark standard | texture / dom | 0.93 / 0.93 | 0.99548 / 0.99548 | unchanged |
| 2x dark standard | texture / dom | 0.93 / 0.93 | 0.99481 / 0.99507 | 0.99681 / 0.99707 |

- **Three of the fourteen `UNMET_ROWS` floors come off, and they are the three the file itself calls
  "the extractor's contrast and not the material's":**

| floor row | floor | base | drop |
| --- | --- | --- | --- |
| `dom / holdout / …glass-over-glass… / 1x dark :: silhouetteIoU` | 0.9070 | 0.90804 | **0.97319** |
| `texture / holdout / …glass-over-glass… / 2x dark :: silhouetteIoU` | 0.9257 | 0.92707 | **0.99980** |
| `dom / holdout / …glass-over-glass… / 2x dark :: silhouetteIoU` | 0.9038 | 0.92878 | **0.98289** |

  All three clear ≥ 0.93, the gate's own adopted bound for the dark profiles, so they stop being
  floors at all and `UNMET_ROWS` would read **11**. The four `contourDistance` floors on the same
  cell and the seven `ssimMean` floors are untouched — `contourDistance` already fills, and SSIM
  never read this.

- **The W26 cell at the candidate, under each rule** (`candidate.txt`):

| rule | 0.14.0 | candidate | Δ | against the 0.9257 floor |
| --- | --- | --- | --- | --- |
| base | 0.92707 | 0.90362 | −0.02346 | **under** |
| fill | 0.99980 | 0.99982 | +0.00002 | over |
| **drop** | **0.99979** | **0.99980** | **+0.00001** | **over** |
| hyst | 0.99989 | 0.99990 | +0.00001 | over |

  Under `drop` the candidate is not merely above the floor, it is marginally **better** than 0.14.0
  — which is what the level reading said all along (the pane's interior level moves 0.00001 and the
  picture 0.19 of an 8-bit code). The two dom siblings are unaffected: their CSS captures in G2b's
  scratch run are byte-identical to the canonical ones, verified here independently
  (`dom-floors.txt`), and read 0.97319 / 0.98289 at both configurations.

## 7. What this does not buy, and what could not be determined

- **`drop` never lowers an IoU on this bed, and a rule that only ever raises one is worth
  suspecting.** The defence is that it removes only pixels the instrument cannot decide, and that
  the two rows built to see them stay: `silhouetteHoles{Native,Web}` on every cell, and W20's
  `declaredIoUWeb` — the tier's own alpha over a transparent page, with no background differencing
  at all — which reads 0.99915 on this very cell and is the honest answer to "did the tier draw
  there". But a tier that genuinely punched an interior hole would now score full IoU, and whether
  that trade is right for the ledger is a decision, not a measurement.
- **It does not fix the extractor**, only the metric that was hostage to it. The tracker's charter
  — a silhouette rule that separates surface from backdrop by something other than luminance — is
  untouched, and so is the reason `silhouetteAreaNative` is 5 % under the declared region here.
- **Whether the native's 0.02029 is real.** The reference's dark-cell transmission under the inner
  pane sits one 8-bit code over the rung. Whether that is Apple's material or ScreenCaptureKit
  quantisation cannot be settled from one fixture, and it decides whether the native's 14 holes are
  a property of the reference or of the capture.
- **The 1x-light and 2x-light siblings of this cell** move by +0.00193…+0.00317 under `drop` and
  were never floored; this spike looked for bounds and floors that move, not for every recorded
  reading in past waves that would need restating beside its original. The 24 committed cells with
  no shape axis were not recomputed (there is nothing to recompute).
- **`PREDICATE_EXCLUDES` at the W26 candidate** was not re-derived; G2b describes it and does not
  commit it, and `drop` cannot move it because the predicate reads areas.

## The files

| file | what it is |
| --- | --- |
| `w26extractor.py` | the harness's extractor and shape metrics, transcribed |
| `validate.py`, `validate.txt` | the transcription proved against all 613 committed cells |
| `anatomy.py`, `anatomy.txt` | the floor cell's three masks, counted and located |
| `zones.py`, `zones.txt` | what the excluded pixels sit over, and in which pane |
| `masks-sheet.py`, `masks-4x.png` | native \| 0.14.0 \| candidate at 4× per CSS px, mask overlaid |
| `scan.py`, `scan.txt` | the threshold scan, raw and hole-filled |
| `blast.py`, `blast.txt`, `blast-rows.json` | four rules over the whole committed bed |
| `candidate.py`, `candidate.txt` | the floor cell at the candidate under each rule |
| `dom-floors.txt` | the two dom floors at the candidate, CSS byte-identity verified |

Run with `/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python` from this directory.
