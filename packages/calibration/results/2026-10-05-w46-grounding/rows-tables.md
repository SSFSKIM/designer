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
