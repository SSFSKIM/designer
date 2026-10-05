# W46 grounding: the gap to Apple over the whole current macOS 27 bed (2026-10-05)

A READ of the published rows. Nothing was captured, no holdout was read (holdout members are taken
from their already-published rows only and kept in their own column), no runtime or document byte
moved. The motivating rule: tabulate the published rows' own statistic over the whole bed before
chartering a refit.

**What was read.** The four current macOS 27 generations in `results/generations/index.json`
(file SHA-256 and row count checked): light 0.5 `85ad7f7e3e0d` (509 rows, the two accessibility
profiles included), dark 0.5 `0eac5b294cc2` (277), light 0.25 `ebc3d9105a4a` (656) and dark 0.25
`d0219cd684bf` (468). Every arithmetic is imported by path from the committed cuts, not rewritten:
W44 G1's `cuts/t1.py` (T1), W44 G1's `cuts/cuts.py` (tables via `owner_tables`, `chroma_member`,
`cut_c1`, `cut_x1`, `cut_e2`, `well_conditioned`) and W44 G1's `readings.py` (T1-fine and T1-low).
Captures were read from the canonical tree
(`/Users/new/Developer/GitHub/designer/packages/calibration/web-captures`), read-only; `cuts.capture`
checks each capture's metadata against its row's `capturePath`, and every one matched.

**Cross-checks that passed.** On the 772 cells of the 0.25 generations, the T1 readings and
fidelity verdicts here equal W45's landing cut (`cut-025-w45-landing.json`), which is the cut the
owner test pins. On light 0.25, the 1x+2x WebGPU T1 misses come to 157 of 232, matching
`MISSED_27_ROWS`. The T-stratum bands read here equal W45's band fixture `t-bands-ebc3d9105a4a.json`
to 0.0 on its 8 cells. In every profile and tier, the gated table misses equal `MISSED_27_ROWS`'s
table entries. C1 and X1 on the 0.25 generations equal the landing cut's per bed and span.

Scripts (all `python3.12 -B`, from this directory, with `VITREA_WEB_CAPTURES` set to the canonical
tree): `t1_union.py` → `t1-union.json`, `t1-cells.csv`, `t1-aggregates.csv`; `t1_tables.py` →
`t1-tables.md` (full, accessibility profiles included), `t1-tables-memo.md`; `rows_union.py` →
`rows-union.json`; `rows_tables.py` → `rows-tables.md`; `gaps.py` → `gaps.json`, `gaps.txt`;
`rank.py` → `rank.json`, `rank.txt`.

## 1. T1 over the whole union

**Definition, unchanged from W44/W45.** For each cell, T1 compares `interiorStdDevWeb` with
`interiorStdDevNative` (linear light, over the native silhouette). B = max(1 code, 2·bar). A cell
is **within** if |web − native| ≤ B, or if native ≥ 1 code and |web/native − 1| ≤ 10 %. A T cell
reads its fidelity on T1-fine (the σ 4 device px residual, with the native silhouette eroded
4 CSS px). Raw T1 is kept beside it in `t1-cells.csv`. **A** is W45's aggregate: the median of
|log((web + ε)/(native + ε))|, with ε set to each cell's own code. Each cell of the table below
reads `within/count ×median(web/native) A`.

**Strata, by backdrop (W44 G1):**
- **F** = `checkerboard-4` and `checkerboard-8` (15 scenes per profile).
- **T** = `hc-text-7` (4 scenes, every one a probe).
- **C** = `checkerboard`, `checkerboard-lc16`, `checkerboard-32`, `checkerboard-64`, `hc-text`,
  `hc-text-28` and `impulse`.
- **P** = `photo`.

**Bar per generation.**
- **Light 0.25 and dark 0.25.** Measured by W44 G0's `bar/t1-bar.json`: 0.5 code on every cell,
  with a run-to-run separation of 0 across seven pixel-identical G1a runs (116 cells per light
  scale, 77 per dark scale).
- **Light 0.5, dark 0.5 and the two accessibility profiles.** No bar was ever measured. These cells
  are read at the floor of 0.5 code (`barFloorAssumed`), so B = 1 code, the same as at 0.25.

**Non-holdout members, standard profiles.** These are calibration, validation, recorded and probe
members. Light 0.25 includes W44's twelve referees (6 per scale), which were spent at read 7.

| generation | scale | tier | pose | F | T | C | P | all |
|---|---|---|---|---|---|---|---|---|
| light 0.5 | 1x | webgpu | rest | 4/12 ×0.93 A 0.18 | 1/3 ×1.59 A 0.39 | 7/30 ×1.21 A 0.19 | 0/9 ×0.63 A 0.39 | 12/54 ×1.01 A 0.26 |
| light 0.5 | 1x | webgpu | inactive | 1/3 ×1.25 A 0.19 | 0/1 ×4.39 A 0.91 | 5/19 ×1.07 A 0.41 | 0/9 ×0.68 A 0.33 | 6/32 ×0.97 A 0.33 |
| light 0.5 | 1x | webgpu | both | 5/15 ×1.04 A 0.18 | 1/4 ×1.91 A 0.47 | 12/49 ×1.20 A 0.25 | 0/18 ×0.68 A 0.34 | 18/86 ×1.00 A 0.30 |
| light 0.5 | 1x | css | both | 0/15 ×0.19 A 1.21 | 2/4 ×0.46 A 0.53 | 10/49 ×0.78 A 0.25 | 0/18 ×0.44 A 0.70 | 12/86 ×0.52 A 0.55 |
| light 0.5 | 2x | webgpu | rest | 5/12 ×0.73 A 0.27 | 1/3 ×1.04 A 0.30 | 5/30 ×0.78 A 0.23 | 0/9 ×0.59 A 0.47 | 11/54 ×0.73 A 0.28 |
| light 0.5 | 2x | webgpu | inactive | 3/3 ×0.96 A 0.03 | 1/1 ×1.82 A 0.20 | 8/19 ×1.19 A 0.30 | 1/9 ×0.75 A 0.25 | 13/32 ×1.03 A 0.25 |
| light 0.5 | 2x | webgpu | both | 8/15 ×0.83 A 0.14 | 2/4 ×1.43 A 0.25 | 13/49 ×0.85 A 0.23 | 1/18 ×0.71 A 0.31 | 24/86 ×0.79 A 0.26 |
| light 0.5 | 2x | css | both | — | — | 1/19 ×0.52 A 0.80 | 1/17 ×0.40 A 0.76 | 2/36 ×0.46 A 0.77 |
| dark 0.5 | 1x | webgpu | rest | 4/12 ×0.94 A 0.24 | 1/3 ×1.03 A 0.23 | 6/24 ×0.76 A 0.25 | 0/3 ×0.45 A 0.72 | 11/42 ×0.77 A 0.26 |
| dark 0.5 | 1x | webgpu | inactive | 0/3 ×2.02 A 0.59 | 0/1 ×1.88 A 0.50 | 0/14 ×1.97 A 0.71 | 0/4 ×0.28 A 1.08 | 0/22 ×1.59 A 0.73 |
| dark 0.5 | 1x | webgpu | both | 4/15 ×1.03 A 0.41 | 1/4 ×1.19 A 0.37 | 6/38 ×0.88 A 0.36 | 0/7 ×0.29 A 1.06 | 11/64 ×0.88 A 0.44 |
| dark 0.5 | 1x | css | both | 2/15 ×0.25 A 1.07 | 1/4 ×0.70 A 0.38 | 7/38 ×0.35 A 0.90 | 0/7 ×0.23 A 1.24 | 10/64 ×0.32 A 0.95 |
| dark 0.5 | 2x | webgpu | rest | 4/12 ×0.77 A 0.42 | 2/3 ×0.64 A 0.45 | 3/24 ×0.62 A 0.41 | 0/3 ×0.37 A 0.86 | 9/42 ×0.62 A 0.44 |
| dark 0.5 | 2x | webgpu | inactive | 0/3 ×3.58 A 1.01 | 1/1 ×2.96 A 0.42 | 1/14 ×1.53 A 0.48 | 0/4 ×0.28 A 1.07 | 2/22 ×1.53 A 0.70 |
| dark 0.5 | 2x | webgpu | both | 4/15 ×1.04 A 0.47 | 3/4 ×1.80 A 0.44 | 4/38 ×0.77 A 0.43 | 0/7 ×0.32 A 0.99 | 11/64 ×0.72 A 0.47 |
| dark 0.5 | 2x | css | both | — | — | 2/8 ×0.23 A 1.21 | 0/6 ×0.26 A 1.14 | 2/14 ×0.25 A 1.15 |
| light 0.25 | 1x | webgpu | rest | 1/12 ×0.82 A 0.36 | 0/3 ×1.14 A 0.38 | 23/37 ×1.04 A 0.09 | 0/11 ×0.65 A 0.38 | 24/63 ×0.97 A 0.13 |
| light 0.25 | 1x | webgpu | inactive | 1/3 ×2.18 A 0.63 | 0/1 ×3.98 A 0.89 | 8/22 ×1.31 A 0.32 | 0/11 ×0.79 A 0.23 | 9/37 ×1.10 A 0.27 |
| light 0.25 | 1x | webgpu | both | 2/15 ×0.86 A 0.38 | 0/4 ×2.37 A 0.63 | 31/59 ×1.07 A 0.11 | 0/22 ×0.73 A 0.30 | 33/100 ×1.00 A 0.21 |
| light 0.25 | 1x | css | both | 0/15 ×0.18 A 1.51 | 2/4 ×0.55 A 0.65 | 12/59 ×0.73 A 0.34 | 1/22 ×0.55 A 0.52 | 15/100 ×0.60 A 0.46 |
| light 0.25 | 2x | webgpu | rest | 3/12 ×0.97 A 0.21 | 0/3 ×1.33 A 0.24 | 23/37 ×1.02 A 0.08 | 0/11 ×0.65 A 0.39 | 26/63 ×0.99 A 0.17 |
| light 0.25 | 2x | webgpu | inactive | 1/3 ×1.73 A 0.41 | 0/1 ×3.13 A 0.56 | 5/22 ×1.19 A 0.19 | 0/11 ×0.82 A 0.18 | 6/37 ×1.13 A 0.19 |
| light 0.25 | 2x | webgpu | both | 4/15 ×1.04 A 0.22 | 0/4 ×2.23 A 0.40 | 28/59 ×1.07 A 0.13 | 0/22 ×0.76 A 0.28 | 32/100 ×1.03 A 0.18 |
| light 0.25 | 2x | css | both | 2/15 ×0.43 A 0.92 | 1/4 ×1.41 A 0.62 | 10/59 ×0.85 A 0.40 | 2/22 ×0.64 A 0.42 | 15/100 ×0.76 A 0.44 |
| dark 0.25 | 1x | webgpu | rest | 3/12 ×0.80 A 0.47 | 0/3 ×0.67 A 0.35 | 5/29 ×0.63 A 0.42 | 0/4 ×0.48 A 0.60 | 8/48 ×0.65 A 0.44 |
| dark 0.25 | 1x | webgpu | inactive | 0/3 ×2.88 A 0.87 | 0/1 ×1.92 A 0.52 | 1/15 ×1.35 A 0.54 | 0/5 ×0.25 A 1.19 | 1/24 ×1.46 A 0.71 |
| dark 0.25 | 1x | webgpu | both | 3/15 ×0.93 A 0.52 | 0/4 ×1.08 A 0.43 | 6/44 ×0.72 A 0.45 | 0/9 ×0.37 A 0.88 | 9/72 ×0.72 A 0.52 |
| dark 0.25 | 1x | css | both | 3/15 ×0.22 A 1.15 | 1/4 ×0.62 A 0.57 | 3/44 ×0.26 A 1.18 | 0/9 ×0.21 A 1.33 | 7/72 ×0.25 A 1.18 |
| dark 0.25 | 2x | webgpu | rest | 3/12 ×0.61 A 0.44 | 1/3 ×0.33 A 0.79 | 3/29 ×0.54 A 0.51 | 0/4 ×0.37 A 0.80 | 7/48 ×0.55 A 0.51 |
| dark 0.25 | 2x | webgpu | inactive | 0/3 ×3.28 A 0.94 | 1/1 ×2.45 A 0.36 | 3/15 ×1.12 A 0.49 | 0/5 ×0.26 A 1.14 | 4/24 ×1.19 A 0.63 |
| dark 0.25 | 2x | webgpu | both | 3/15 ×0.96 A 0.49 | 2/4 ×1.39 A 0.62 | 6/44 ×0.60 A 0.51 | 0/9 ×0.33 A 0.97 | 11/72 ×0.60 A 0.57 |
| dark 0.25 | 2x | css | both | 2/15 ×0.37 A 0.76 | 2/4 ×0.44 A 0.71 | 4/44 ×0.30 A 1.03 | 0/9 ×0.26 A 1.17 | 8/72 ×0.27 A 1.07 |

**Holdout members** (their published rows; spent, and never an input to a fitting or chartering
decision; see §4):


| generation | profile | tier | pose | F | T | C | P | all |
|---|---|---|---|---|---|---|---|---|
| light 0.5 | 1x-light | webgpu | both | — | — | 2/10 ×1.30 A 0.24 | 1/6 ×0.63 A 0.39 | 3/16 ×1.15 A 0.30 |
| light 0.5 | 1x-light | css | both | — | — | 2/10 ×0.83 A 0.34 | 1/6 ×0.46 A 0.71 | 3/16 ×0.63 A 0.41 |
| light 0.5 | 2x-light | webgpu | both | — | — | 1/10 ×0.90 A 0.33 | 2/6 ×0.67 A 0.36 | 3/16 ×0.77 A 0.36 |
| light 0.5 | 2x-light | css | both | — | — | 2/10 ×0.57 A 0.51 | 2/6 ×0.55 A 0.55 | 4/16 ×0.56 A 0.53 |
| dark 0.5 | 1x-dark | webgpu | both | — | — | 1/2 ×1.42 A 0.26 | 0/3 ×0.30 A 1.04 | 1/5 ×0.34 A 0.95 |
| dark 0.5 | 1x-dark | css | both | — | — | 0/2 ×0.52 A 0.56 | 0/3 ×0.22 A 1.28 | 0/5 ×0.25 A 1.16 |
| dark 0.5 | 2x-dark | webgpu | both | — | — | 1/2 ×1.33 A 0.24 | 0/3 ×0.32 A 0.99 | 1/5 ×0.32 A 0.98 |
| dark 0.5 | 2x-dark | css | both | — | — | 1/2 ×0.61 A 0.48 | 0/3 ×0.27 A 1.13 | 1/5 ×0.31 A 1.02 |
| light 0.25 | 1x-light | webgpu | both | — | — | 3/10 ×1.26 A 0.21 | 1/6 ×0.72 A 0.31 | 4/16 ×1.03 A 0.23 |
| light 0.25 | 1x-light | css | both | — | — | 2/10 ×0.72 A 0.40 | 1/6 ×0.52 A 0.61 | 3/16 ×0.63 A 0.47 |
| light 0.25 | 2x-light | webgpu | both | — | — | 4/10 ×1.15 A 0.13 | 2/6 ×0.76 A 0.26 | 6/16 ×0.97 A 0.19 |
| light 0.25 | 2x-light | css | both | — | — | 1/10 ×0.88 A 0.40 | 2/6 ×0.63 A 0.43 | 3/16 ×0.72 A 0.40 |
| dark 0.25 | 1x-dark | webgpu | both | — | — | 0/2 ×1.24 A 0.38 | 0/3 ×0.25 A 1.19 | 0/5 ×0.30 A 1.07 |
| dark 0.25 | 1x-dark | css | both | — | — | 0/2 ×0.45 A 0.74 | 0/3 ×0.19 A 1.40 | 0/5 ×0.23 A 1.27 |
| dark 0.25 | 2x-dark | webgpu | both | — | — | 0/2 ×1.03 A 0.25 | 0/3 ×0.27 A 1.13 | 0/5 ×0.28 A 1.11 |
| dark 0.25 | 2x-dark | css | both | — | — | 0/2 ×0.48 A 0.69 | 0/3 ×0.23 A 1.26 | 0/5 ×0.27 A 1.14 |

**Accessibility profiles (light 0.5, 1x; no F or T scenes are declared).** Reduced transparency is
within on 0 of 12 cells on WebGPU (×0.69) and 0 of 12 on CSS (×0.33). Increased contrast (coupled)
is within on 1 of 14 on WebGPU and runs **×3.27 over**: its rest pose reads ×0.73 and its inactive
pose ×3.54. On CSS it is within on 0 of 14 (×0.41). See `t1-tables.md`.

**What the table says, in four lines.**
1. **Fine-checker over-structure at thick spans** (`checkerboard-8` on `rrect-ml`/`rrect-lg` at
   rest) is not a 2x light 0.25 property. It reads ×2.34/×2.60 at 2x light 0.25 and ×2.72/×2.52 at
   1x light 0.25. At 0.5 it reads ×2.41/×1.17 at 1x light, and ×1.6–1.9 in dark at both positions
   and both scales. Only 2x light 0.5 is within (×1.12/×1.05).
2. **Thin-span fine under-structure is near-universal on WebGPU.** On untinted `checkerboard-4`/`-8`
   capsule and `rrect-sm` at rest, the ratio runs ×0.34–0.99 in light and ×0.23–0.63 in dark, in
   every generation and at both scales. The one exception is 1x light 0.5's `checkerboard-8` thin
   cells, at ×1.03–1.12.
3. **The dark scheme is the widest WebGPU gap, and it is the same at both positions.**
   - P reads ×0.25–0.48 in both poses: the flat dark photo body.
   - At rest, C reads ×0.54–0.76: under-structured.
   - Inactive, F reads ×2.0–3.6 and C ×1.1–2.0: the receded fine body is over-structured.
4. **The CSS tier is under-structured everywhere.** F at rest reads ×0.13–0.25 in all four
   generations, and P ×0.21–0.64.

## 2. Every other adopted row, by generation, scale and tier

#### The tables (ssim / ΔE / edge / silhouette / contour; the owner test's bounds)

Gated = the owner test's bed (no probe, no recorded, rest pose; holdout INCLUDED and counted apart); not gated = the same table on the probe, recorded and inactive rows.

| generation | profile | tier | gated cells | gated misses (non-holdout / holdout) | worst gated | not-gated cells | not-gated misses | worst not gated |
|---|---|---|---|---|---|---|---|---|
| light 0.5 | 1x-light-increased-contrast-coupled | css | 9 | 0 / 0 |  | 9 | 0 |  |
| light 0.5 | 1x-light-increased-contrast-coupled | webgpu | 9 | 0 / 0 |  | 9 | 0 |  |
| light 0.5 | 1x-light-reduced-transparency | css | 8 | 0 / 1 | photo__rrect-lg__rest ssimOutside 0.8270 vs ≥ 0.83 | 8 | 0 |  |
| light 0.5 | 1x-light-reduced-transparency | webgpu | 8 | 0 / 0 |  | 8 | 0 |  |
| light 0.5 | 1x-light | css | 36 | 0 / 2 | checkerboard__rrect-lg__rest ssimMean 0.8842 vs ≥ 0.9 | 88 | 3 | checkerboard-8__rrect-lg__rest ssimMean 0.8536 vs ≥ 0.9 |
| light 0.5 | 1x-light | webgpu | 36 | 0 / 0 |  | 88 | 4 | checkerboard-8__rrect-ml__rest ssimMean 0.8257 vs ≥ 0.88 |
| light 0.5 | 2x-light | css | 36 | 0 / 0 |  | 33 | 0 |  |
| light 0.5 | 2x-light | webgpu | 36 | 0 / 0 |  | 88 | 2 | photo__rrect-lg__inactive-tint-orange oklabDeltaEP95 0.1752 vs ≤ 0.17 |
| dark 0.5 | 1x-dark | css | 13 | 0 / 1 | photo__rrect-lg__rest oklabDeltaEP95 0.2009 vs ≤ 0.18 | 70 | 10 | mid-chroma-solid__rrect-lg__inactive oklabDeltaEP95 0.3151 vs ≤ 0.18 (3 UNMEASURED: metric absent) |
| dark 0.5 | 1x-dark | webgpu | 13 | 0 / 0 |  | 70 | 14 | impulse__rrect-lg__inactive ssimMean 0.3203 vs ≥ 0.87 (3 UNMEASURED: metric absent) |
| dark 0.5 | 2x-dark | css | 13 | 0 / 1 | photo__rrect-lg__rest oklabDeltaEP95 0.1947 vs ≤ 0.19 | 15 | 3 | photo__rrect-lg__inactive oklabDeltaEP95 0.1968 vs ≤ 0.19 (2 UNMEASURED: metric absent) |
| dark 0.5 | 2x-dark | webgpu | 13 | 0 / 0 |  | 70 | 14 | checkerboard-64__rrect-lg__inactive contourDistanceP95 7.6158 vs ≤ 1.5 (3 UNMEASURED: metric absent) |
| light 0.25 | 1x-light | css | 36 | 1 / 2 | checkerboard__glass-over-glass__rest ssimMean 0.8647 vs ≥ 0.9 | 128 | 17 | checkerboard-4__rrect-ml__rest ssimMean 0.8204 vs ≥ 0.9 |
| light 0.25 | 1x-light | webgpu | 36 | 0 / 1 | checkerboard__rrect-lg__rest ssimMean 0.8641 vs ≥ 0.88 | 128 | 17 | checkerboard-8__rrect-lg__rest ssimMean 0.5543 vs ≥ 0.88 |
| light 0.25 | 2x-light | css | 36 | 0 / 1 | checkerboard__glass-over-glass__rest ssimMean 0.9199 vs ≥ 0.92 | 128 | 3 | mid-chroma-solid__rrect-lg__rest oklabDeltaEMean 0.0970 vs ≤ 0.08 |
| light 0.25 | 2x-light | webgpu | 36 | 0 / 0 |  | 128 | 15 | checkerboard-8__rrect-lg__rest ssimMean 0.8505 vs ≥ 0.93 |
| dark 0.25 | 1x-dark | css | 13 | 0 / 1 | photo__rrect-lg__rest oklabDeltaEP95 0.2060 vs ≤ 0.18 | 104 | 27 | mid-chroma-solid__capsule-button__inactive oklabDeltaEP95 0.3230 vs ≤ 0.18 (7 UNMEASURED: metric absent) |
| dark 0.25 | 1x-dark | webgpu | 13 | 0 / 0 |  | 104 | 32 | impulse__rrect-lg__inactive ssimMean 0.3220 vs ≥ 0.87 (7 UNMEASURED: metric absent) |
| dark 0.25 | 2x-dark | css | 13 | 0 / 1 | photo__rrect-lg__rest oklabDeltaEP95 0.2007 vs ≤ 0.19 | 104 | 21 | checkerboard-64__capsule-button__rest contourDistanceP95 5.1992 vs ≤ 3.0 (7 UNMEASURED: metric absent) |
| dark 0.25 | 2x-dark | webgpu | 13 | 0 / 0 |  | 104 | 24 | checkerboard-64__capsule-button__rest contourDistanceP95 5.1992 vs ≤ 1.5 (7 UNMEASURED: metric absent) |

Every gated miss count above equals `MISSED_27_ROWS`'s entries for that profile, tier and table metric (`tablesVsMissed27` in rows-union.json: all agree).

#### M1, C1, X1, L1 (absolute), E2 (absolute), per generation and tier

| generation | tier | M1 (median active / inactive; cells outside [0.6, 1.4]) | C1 worst bed x span (≤ 0.0042) | X1 failing / cells | L1 abs misses / measured (max error) | E2 median / max mean-abs codes | gated? |
|---|---|---|---|---|---|---|---|
| light 0.5 | webgpu | 1.049 / 1.023; 3 of 18 (worst 1x-light-standard-glass0.5/photo__rrect-sm__inactive 1.539) | 2x light span 128 0.0021 (0 of 6 bed-spans over) | 0 / 118 (12 no row) | 2 / 98 (0.0661) | 8.56 / 34.16 (122 cells) | yes |
| light 0.5 | css | 1.118 / 1.064; 2 of 18 (worst 2x-light-standard-glass0.5/photo__rrect-sm__rest 1.574) | 2x light span 128 0.0050 (1 of 5 bed-spans over) | 47 / 76 (54 no row) | 2 / 98 (0.0654) | 7.95 / 26.61 (87 cells) | no (CSS read only) |
| dark 0.5 | webgpu | 0.997 / 1.006; 0 of 8 | 2x dark span 128 0.0038 (0 of 6 bed-spans over) | 0 / 100 (12 no row) | 0 / 38 (0.0493) | 11.03 / 38.57 (90 cells) | yes |
| dark 0.5 | css | 0.970 / 1.027; 0 of 8 | 1x dark span 128 0.0054 (2 of 4 bed-spans over) | 37 / 58 (54 no row) | 0 / 38 (0.0478) | 12.03 / 42.69 (55 cells) | no (CSS read only) |
| light 0.25 | webgpu | 0.973 / 0.953; 0 of 18 | 2x light span 128 0.0021 (0 of 6 bed-spans over) | 0 / 130 | 0 / 98 (0.0451) | 9.24 / 39.02 (164 cells) | yes |
| light 0.25 | css | 1.183 / 1.123; 0 of 18 | 1x light span 128 0.0034 (0 of 6 bed-spans over) | 84 / 130 | 0 / 98 (0.0472) | 9.06 / 47.45 (164 cells) | no (CSS read only) |
| dark 0.25 | webgpu | 1.055 / 1.066; 0 of 8 | 2x dark span 128 0.0038 (0 of 6 bed-spans over) | 0 / 112 | 0 / 38 (0.0491) | 13.58 / 51.14 (124 cells) | yes |
| dark 0.25 | css | 1.026 / 1.082; 0 of 8 | 1x dark span 128 0.0054 (2 of 6 bed-spans over) | 74 / 112 | 0 / 38 (0.0475) | 13.88 / 56.62 (124 cells) | no (CSS read only) |

#### Regression rows read off the pinned cuts (reference generations differ per gate)

| generation | tier | M2 misses (named / failure) | L1 growth misses | E2 failing / named-miss cells | source |
|---|---|---|---|---|---|
| light 0.5 | webgpu | 0 (0 / 0) | 0 | not gated (no reference) | W36 chroma-cut (reference W33 6e509c7f76cc / eab099cc6698) |
| dark 0.5 | webgpu | 0 (0 / 0) | 0 | not gated (no reference) | W36 chroma-cut (reference W33 6e509c7f76cc / eab099cc6698) |
| light 0.25 | webgpu | 8 (4 / 4) | 0 | 52 / 49 | W45 landing cut (reference c05 light / d0219 dark) |
| light 0.25 | css | 5 (2 / 3) | 0 | 16 / 17 | W45 landing cut (reference c05 light / d0219 dark) |
| dark 0.25 | webgpu | 0 (0 / 0) | 0 | 0 / 0 | W45 landing cut (reference c05 light / d0219 dark) |
| dark 0.25 | css | 0 (0 / 0) | 0 | 0 / 0 | W45 landing cut (reference c05 light / d0219 dark) |

Notes on rows that need a sentence:
- **Tables.** No WebGPU table misses on a gated non-holdout cell in any generation. The gated
  misses that do exist sit on holdout cells or on CSS. The rest of the misses fall on the not-gated
  bed, chiefly:
  - `checkerboard-8` thick rest: ssimMean 0.55 at 1x light 0.25 and 0.83–0.85 at 2x;
  - dark inactive `impulse__rrect-lg` and `mid-chroma-solid` (ssim 0.32, ΔE p95 0.32);
  - dark probe contours on `checkerboard-64` (cP95 5.2–7.6 against 1.5).

  The 0.5 bed lacks rows for 14 T1 scenes per light profile and 8 per dark profile (WebGPU), plus
  most of the 2x CSS bed. Those cells are absent, not passing.
- **M2, L1 growth and E2** are regression rows against a reference that each gate re-baselines.
  Their counts are those of the cut the owner test pins: W36's for 0.5 (M2 against W33, so 0
  moves), and W45's landing for 0.25. E2 has no reference at 0.5, so it is computed here only as an
  absolute reading and is not gated.
- **L1 over every set (not gated).** The gated L1 passes everywhere except the two light 0.5
  impulse tint-orange inactive cells (0.066). Read over every non-holdout set instead,
  |web − native| > 0.055 on:
  - **light 0.5:** 7 WebGPU cells and 4 CSS;
  - **dark 0.5:** 8 and 4;
  - **light 0.25:** 20 and 26;
  - **dark 0.25:** 19 and 20.

  All are probe or recorded cells. They concentrate on `mid-chroma-solid` (dark 0.25 inactive
  −0.19 to −0.21 linear, the W36/W39 chroma and middle named miss) and on `checkerboard-4`,
  `hc-text-28` and `hc-text-7`.
- **S1 at 0.25** (W45 landing cut, not recomputed). Per-profile medians on WebGPU are 0.94 (1x
  light), 0.98 (2x light), 0.31 (1x dark) and 0.31 (2x dark). On CSS, the dark medians are 0.08 and
  0.12.

## 3. The ranked gap table

**How the table is built.**
- **Unit.** Every candidate (a)–(f) is about texture, so all are read on T1.
- **Weight.** S = the sum, over a candidate's **non-holdout missing** cells, of
  |log((web + ε)/(native + ε))|. This is cells × magnitude in W45's own aggregate term; a cell
  within T1's bound adds nothing.
- **Holdout.** Holdout misses and S including holdout are shown beside each row, never ranked on.
- **Candidate (g)** is a level and tint reading with no T1 term, so it is listed after the ranked
  rows.
- **Holdout status.** No canonical holdout or referee is unspent for any current document bytes
  (§4). A candidate that produces new document bytes may take one read of the canonical holdout
  under the configuration ledger.

| rank | candidate | cells (non-holdout miss / count) | S | typical gap (median web/native of misses) | where | holdout / referee for these bytes |
|---|---|---|---|---|---|---|
| 1 | (d) the 0.5 generation's texture, light + dark | 236 / 300 | 117.95 | ×0.76 (light ×0.79, dark ×0.65) | 0.5, 1x + 2x, WebGPU, all strata | holdout spent (read 5, W36); 34/42 holdout cells miss; frozen by X41 |
| 2 | (e) CSS fine-pitch under-structure | 81 / 90 | 96.05 | ×0.20 | every generation, CSS, F | holdout spent per generation; no F holdout scene exists |
| 3 | (b) dark scheme at 0.25 | 124 / 144 | 85.85 | ×0.59; P ×0.33–0.37, rest C ×0.54–0.63, inactive F ×2.9–3.3 | dark 0.25, 1x + 2x, WebGPU | holdout spent (read 6, W43 G3; bytes also in read 7's set); 10/10 holdout cells miss |
| 4 | (c) 1x light 0.25 texture | 67 / 100 (79 / 116 with holdout) | 26.65 | ×0.88; F rest ×0.82, P ×0.65–0.79, C inactive ×1.31 | light 0.25, 1x, WebGPU | holdout spent (read 7); referees spent (read 7) |
| 5 | (a) per-span tap WIDTH at 2x light 0.25 | 16 / 29 | 6.11 | ×1.31; `checkerboard-8` lg/ml rest ×2.60/×2.34, md/lg inactive ×2.43/×1.73 | light 0.25, 2x, WebGPU, F ∪ C mid/thick | holdout spent (read 7; 4/4 holdout cells miss); referees spent |
| 6 | (f) the eleven W45 regressions | 9 / 9 (11 / 11 with holdout) | 3.85 | ×1.22 | light 0.25, 2x, WebGPU | spent (read 7) |
| — | (g) light 0.25 photo thin rest level; receded tint L | 6 + 20 | n/a | photo +0.032 to +0.045 linear (within L1's 0.055); tint +0.0234 OKLab L (no adopted bound) | light 0.25, 1x + 2x, WebGPU | spent (read 7) |

Context rows. These are overlapping re-cuts of the candidates above and are not ranked against
them.

| context | non-holdout miss / count | S | median ratio of misses |
|---|---|---|---|
| (d) light half, light 0.5 | 130 / 172 | 50.82 | ×0.79 |
| (d) dark half, dark 0.5 | 106 / 128 | 67.13 | ×0.65 |
| **dark scheme at both positions ((b) + (d) dark half)** | **230 / 272** | **152.98** | **×0.62** |
| (a)'s shape over every generation and scale | 101 / 151 | 55.22 | ×1.73 |
| the CSS tier, every stratum and generation | 473 / 544 | 429.60 | ×0.35 |

Per-candidate detail (cell lists in `gaps.txt`, `rank.json`):
- **(a)** `checkerboard-8__rrect-lg__rest` reads ×2.60 and `__rrect-ml__rest` ×2.34. Apple's
  fine thick native SD is 0.022–0.026 and the web's is 0.058–0.061. The same two cells read
  ×2.52/×2.72 at 1x light 0.25. At 2x light 0.5 they read ×1.05/×1.12 (within).
  - **Operator shape:** a tap width that grows with span, at both scales. A 2x-only operator leaves
    the 1x twin.
- **(b)** Dark 0.25 WebGPU stratum by stratum (miss / count, A):

  | stratum | 1x | 2x |
  |---|---|---|
  | F | 12/15, A 0.52 | 12/15, A 0.49 |
  | T | 4/4, A 0.43 | 2/4, A 0.62 |
  | C | 38/44, A 0.45 | 38/44, A 0.51 |
  | P | 9/9, A 0.88 | 9/9, A 0.97 |

  - **Rows that pass:** level L1 (0/38, max 0.049), M1 (median 1.055/1.066), C1, X1.
  - **S1** medians are 0.31.
  - **Dark 0.5 shows the same picture**, with P ×0.28–0.45 and inactive F ×2.0–3.6.
  - **Operator shape:** the tracker's dark transmission refit (dark `tintAlpha` 0.9 transmits a
    tenth), declared against photo and checker structure together, plus a receded dark fine-scatter
    term for the inactive over-structure.
- **(c)** 1x light 0.25 WebGPU: 79 of 116 cells miss, with holdout. By stratum and pose (miss /
  count, A):

  | stratum | rest | inactive |
  |---|---|---|
  | F | 11/12, A 0.36 | 2/3, A 0.63 |
  | T | 3/3 | 1/1 |
  | C | 17/42, A 0.09 | 18/27, A 0.35 |
  | P | 13/14, A 0.37 | 14/14, A 0.24 |

  Worst cells: `checkerboard__rrect-md__inactive-pressed` ×4.77, `checkerboard-64__rrect-sm__rest`
  ×0.25, and `checkerboard-4` thin ×0.34–0.35.
  - **Operator shape:** the W45 span-graded tap's 1x twin. The W45 leaf is 0 at dpr ≤ 1 by
    construction, and W45's 1x rows are byte-identical to c05.
- **(d)** Is the fine-checker gap present at 0.5? At 2x light 0.5, the thick fine cells are within
  and thin F is under (×0.52–0.79). At 1x light 0.5, `checkerboard-8` ml/md read ×2.41/×1.68 over.
  In dark 0.5, the inactive fine cells read ×1.7–3.8 over and untinted thin F ×0.33–0.63 under. So yes at 1x
  and in dark; no at 2x light.
  - **X41:** X41 froze the 0.5 generation's documents, so moving them is a user ruling, not a
    technical choice.
- **(e)** CSS F at rest reads ×0.13–0.25 in every generation, against WebGPU's ×0.61–0.97. The CSS
  tier draws no second tap, and W45's hold keeps its 2x floor. Decision Log 23 makes a CSS-only
  residual a ledger entry, not a wave, so this is ranked but is not a chartering candidate under
  the current doctrine.
- **(f)** Current ratios against native, 2x light 0.25 WebGPU:

  | cell | ratio |
  |---|---|
  | `checkerboard__rrect-md__pressed` | ×1.24 |
  | `checkerboard__capsule-button__pressed` | ×1.22 |
  | `checkerboard-32__rrect-sm__rest` | ×1.23 |
  | `checkerboard-32__rrect-lg__rest` | ×1.17 |
  | `checkerboard__rrect-lg__rest` (holdout) | ×1.40 |
  | `checkerboard-64__rrect-sm__rest` | ×0.19 |
  | `hc-text-7__rrect-md__inactive` (referee) | ×0.82 on T1-low |
  | `checkerboard__glass-over-glass__rest` (holdout) | ×1.17 |
  | `checkerboard-8__rrect-lg__rest` | ×2.60 |
  | `hc-text__rrect-lg__inactive` | ×0.84 |
  | `photo__toolbar-group__inactive` | ×0.72 |

  All eleven miss.
- **(g)** The photo thin rest cells read +0.0347 / +0.0451 / +0.0340 at 1x and +0.0327 / +0.0417 /
  +0.0317 at 2x (`capsule-button` / `rrect-sm` / `toolbar-group`). That is c05's +0.034/+0.044
  unmoved at 1x, and within L1's bound. The receded tint ΔL reads +0.0234 over 20 tinted inactive
  cells, identical to c05.
  - **Operator shape:** the tracker's one-sided term and a one-leaf `tintShadeLight` step.

## 4. Facts checked

- **Fields.** Every generation's rows carry `interiorStdDevWeb`, `interiorStdDevNative` and
  `interiorMeanNative`. The only rows without them are the `dark-solid` rows: 11 in dark 0.5 and 28
  in dark 0.25, which are L1's known UNMEASURED black means. No T1 member lacks a field.
- **Rows the 0.5 bed does not carry.** It has no row for some T1-declared members. Light 0.5
  WebGPU lacks 14 per scale: the pressed cells, `hc-text` sm/lg, and `impulse` rest sm/ml/lg. Dark
  0.5 WebGPU lacks 8 per scale. On CSS, 2x light 0.5 lacks 64 and 2x dark 0.5 lacks 58. These are
  listed as `missing` in `t1-union.json`.
- **A degenerate native.** The 2x dark `impulse__capsule-button__inactive` cell has a native SD of
  exactly 0 at both positions, so its ratio is undefined; its log error is read at ε = 1 code.
- **Holdout status, from the cross-gate ledger** (`results/holdout-configuration/configuration-log.json`):

  | generation | holdout spent by |
  |---|---|
  | light 0.5 `85ad7f7e3e0d` / `30fbe05986ae`, dark 0.5 `0eac5b294cc2` / `5cec8c961201` | read 5 (2026-09-24, c9a §5.179, W36) |
  | dark 0.25 `d0219cd684bf` / `f0b36a71772a` | read 6 (2026-10-02, c9a §5.201, W43 G3, `glass0.25`); its bytes are also in read 7's document set |
  | light 0.25 `ebc3d9105a4a` / `12712d534b78` | read 7 (2026-10-03, c9a §5.206, W45 exposure), together with W44's twelve referees |

  **Every canonical holdout and referee is spent for the current bytes.** The unspent held-out
  material is W42's holdout H (`w42-archive`, the four window states) and W39's holdout. Both are
  native archives on other beds, not the canonical T1 population.

## Recommendation

Charter the dark scheme's texture first, opening at 0.25. It is the largest WebGPU gap at both
positions — 230 of 272 non-holdout cells miss, S 153 against 51 for light 0.5 — and it has one
coherent shape: a flat photo body (×0.25–0.48), under-structured rest checkers, and over-structured
receded fine checkers. It also sits on the fidelity-target tier, its transmission lever is a leaf
move at 0.25 needing no X41 ruling (the receded fine term may need an operator), and what it finds
can be carried to the shipped-default dark 0.5 once the user lifts the freeze. Its risk is
identification rather than holdout, because the dark calibration set is 19 scenes at spans 44 and
96 only, with no fine-pitch scene (every dark F and T cell is a probe), and no bar was ever measured
at 0.5. The charter should therefore declare its calibration cells and referee split before any
fit; W42's unspent H can serve as the referee if its backdrops carry structure. The per-span tap
width (a, S 6) is better chartered later, as a both-scales operator alongside (c).
