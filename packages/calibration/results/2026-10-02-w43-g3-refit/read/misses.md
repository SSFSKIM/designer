# W43 G3 (i): candidate c05, the non-holdout misses the ruling puts to the user (Decision Log 5 (e))

Each line is a miss on a GATED row, to be ruled a permitted named miss or a stop before any holdout read. Read from `c05-cuts.json` (the 0.25 cuts, `cuts/cuts.py`). Holdout never read. rrect-lg is marked as its own stratum (Decision Log 7 item 9).

## tables (the 0.5 tables per tier)
- 1x-light css: `checkerboard__rrect-ml__rest` (calibration) ssimMean 0.87367 against ≥ 0.9 — the pre-fit render already missed it at 0.87770; c05 reads it 0.004 lower

## M2, directional (WebGPU): named misses, each toward Apple and not past it
- `1x-light/photo__capsule-button__inactive` named: reference 0.03592 -> 0.04475, Apple 0.05528 (+24.57 %)
- `1x-light/photo__capsule-button__rest` named: reference 0.03941 -> 0.04290, Apple 0.06596 (+8.85 %)
- `1x-light/photo__rrect-md__inactive` named: reference 0.04429 -> 0.05581, Apple 0.07185 (+26.00 %)
- `1x-light/photo__rrect-md__rest` named: reference 0.04854 -> 0.05733, Apple 0.08877 (+18.11 %)
- `1x-light/photo__rrect-ml__rest` named: reference 0.05525 -> 0.06584, Apple 0.10291 (+19.18 %)
- `1x-light/photo__rrect-sm__rest` named: reference 0.02319 -> 0.02372, Apple 0.03912 (+2.31 %)
- `1x-light/photo__toolbar-group__inactive` named: reference 0.06526 -> 0.06972, Apple 0.10328 (+6.83 %)
- `1x-light/photo__toolbar-group__rest` named: reference 0.07230 -> 0.07854, Apple 0.10977 (+8.64 %)
- `2x-light/photo__capsule-button__inactive` named: reference 0.03873 -> 0.05020, Apple 0.05498 (+29.61 %)
- `2x-light/photo__capsule-button__rest` named: reference 0.03688 -> 0.04097, Apple 0.06737 (+11.09 %)
- `2x-light/photo__rrect-md__inactive` named: reference 0.04830 -> 0.06383, Apple 0.07421 (+32.14 %)
- `2x-light/photo__rrect-md__rest` named: reference 0.04638 -> 0.05668, Apple 0.08935 (+22.20 %)
- `2x-light/photo__rrect-ml__rest` named: reference 0.05479 -> 0.06644, Apple 0.10320 (+21.25 %)
- `2x-light/photo__rrect-sm__inactive` named: reference 0.01694 -> 0.01962, Apple 0.02246 (+15.85 %)
- `2x-light/photo__rrect-sm__rest` named: reference 0.01971 -> 0.02062, Apple 0.03918 (+4.58 %)
- `2x-light/photo__toolbar-group__inactive` named: reference 0.06905 -> 0.07780, Apple 0.09980 (+12.67 %)
- `2x-light/photo__toolbar-group__rest` named: reference 0.06789 -> 0.07505, Apple 0.10760 (+10.56 %)

## E2, per cell in absolute codes (WebGPU): 62 of 288 cells moved farther from Apple; mean change over all cells -1.659 codes
- `1x-dark/checkerboard-32__rrect-lg__rest` 14.956 -> 15.702 codes (+0.746) [rrect-lg]
- `1x-dark/checkerboard-32__rrect-md__rest` 16.917 -> 17.324 codes (+0.407)
- `1x-dark/checkerboard-32__rrect-ml__rest` 14.752 -> 15.268 codes (+0.517)
- `1x-dark/checkerboard-4__capsule-button__rest` 23.162 -> 23.216 codes (+0.053)
- `1x-dark/checkerboard-64__rrect-md__rest` 33.032 -> 33.971 codes (+0.938)
- `1x-dark/checkerboard-64__rrect-ml__rest` 22.943 -> 23.698 codes (+0.754)
- `1x-dark/checkerboard__rrect-md__rest` 17.162 -> 17.198 codes (+0.036)
- `1x-dark/dark-solid__rrect-lg__rest` 5.384 -> 5.445 codes (+0.061) [rrect-lg]
- `1x-dark/mid-dark-solid__rrect-lg__rest` 4.379 -> 5.816 codes (+1.436) [rrect-lg]
- `1x-light/checkerboard-32__capsule-button__rest` 15.253 -> 16.906 codes (+1.653)
- `1x-light/checkerboard-32__rrect-lg__rest` 10.657 -> 15.349 codes (+4.692) [rrect-lg]
- `1x-light/checkerboard-32__rrect-md__rest` 10.479 -> 16.078 codes (+5.600)
- `1x-light/checkerboard-32__rrect-ml__rest` 7.557 -> 11.004 codes (+3.446)
- `1x-light/checkerboard-32__rrect-sm__rest` 10.133 -> 13.037 codes (+2.904)
- `1x-light/checkerboard-4__capsule-button__rest` 19.350 -> 19.883 codes (+0.533)
- `1x-light/checkerboard-4__capsule-button__rest-tint-orange` 5.269 -> 5.366 codes (+0.097)
- `1x-light/checkerboard-64__rrect-ml__rest` 26.739 -> 35.617 codes (+8.879)
- `1x-light/checkerboard-8__capsule-button__rest` 28.468 -> 31.852 codes (+3.383)
- `1x-light/checkerboard-8__capsule-button__rest-tint-orange` 6.474 -> 6.951 codes (+0.476)
- `1x-light/checkerboard-8__rrect-lg__rest` 12.390 -> 12.739 codes (+0.349) [rrect-lg]
- `1x-light/checkerboard-8__rrect-md__rest` 17.248 -> 18.623 codes (+1.375)
- `1x-light/checkerboard-8__rrect-sm__rest` 20.812 -> 21.315 codes (+0.503)
- `1x-light/checkerboard-lc16__capsule-button__rest` 9.295 -> 9.332 codes (+0.037)
- `1x-light/checkerboard-lc16__rrect-sm__rest` 6.191 -> 6.278 codes (+0.087)
- `1x-light/checkerboard__capsule-button__rest` 20.907 -> 23.791 codes (+2.884)
- `1x-light/checkerboard__capsule-button__rest-tint-blue` 5.818 -> 5.887 codes (+0.069)
- `1x-light/checkerboard__capsule-button__rest-tint-orange` 5.194 -> 5.470 codes (+0.276)
- `1x-light/checkerboard__rrect-md__rest` 15.752 -> 18.940 codes (+3.188)
- `1x-light/checkerboard__rrect-ml__rest` 9.392 -> 10.540 codes (+1.148)
- `1x-light/checkerboard__rrect-sm__rest` 8.969 -> 11.355 codes (+2.386)
- `1x-light/checkerboard__toolbar-group__rest` 19.420 -> 22.415 codes (+2.995)
- `1x-light/hc-text-28__rrect-lg__rest` 7.980 -> 11.557 codes (+3.577) [rrect-lg]
- `1x-light/hc-text-28__rrect-md__rest` 19.455 -> 24.778 codes (+5.323)
- `1x-light/hc-text-28__rrect-sm__rest` 12.864 -> 16.287 codes (+3.424)
- `1x-light/hc-text-7__rrect-lg__rest` 7.770 -> 9.641 codes (+1.870) [rrect-lg]
- `1x-light/hc-text__rrect-lg__rest` 9.682 -> 12.283 codes (+2.601) [rrect-lg]
- `1x-light/light-solid__rrect-sm__rest` 3.162 -> 3.190 codes (+0.028)
- `2x-dark/checkerboard-32__capsule-button__rest` 35.811 -> 35.828 codes (+0.017)
- `2x-dark/checkerboard-32__rrect-lg__rest` 13.339 -> 14.079 codes (+0.740) [rrect-lg]
- `2x-dark/checkerboard-32__rrect-md__rest` 17.780 -> 18.182 codes (+0.403)
- `2x-dark/checkerboard-32__rrect-ml__rest` 12.744 -> 13.241 codes (+0.497)
- `2x-dark/checkerboard-64__rrect-md__rest` 31.106 -> 32.241 codes (+1.135)
- `2x-dark/checkerboard-64__rrect-ml__rest` 20.434 -> 21.142 codes (+0.708)
- `2x-dark/checkerboard__capsule-button__rest` 32.383 -> 32.389 codes (+0.006)
- `2x-dark/mid-dark-solid__rrect-lg__rest` 4.383 -> 5.787 codes (+1.404) [rrect-lg]
- `2x-light/checkerboard-32__rrect-lg__rest` 9.737 -> 13.972 codes (+4.235) [rrect-lg]
- `2x-light/checkerboard-32__rrect-md__rest` 12.321 -> 14.028 codes (+1.707)
- `2x-light/checkerboard-32__rrect-ml__rest` 8.411 -> 9.550 codes (+1.139)
- `2x-light/checkerboard-4__capsule-button__rest` 25.893 -> 27.176 codes (+1.282)
- `2x-light/checkerboard-4__capsule-button__rest-tint-orange` 6.542 -> 6.814 codes (+0.273)
- `2x-light/checkerboard-4__rrect-sm__rest` 25.392 -> 25.628 codes (+0.236)
- `2x-light/checkerboard-64__rrect-ml__rest` 27.251 -> 36.390 codes (+9.139)
- `2x-light/checkerboard-8__capsule-button__rest` 30.083 -> 32.451 codes (+2.368)
- `2x-light/checkerboard-8__capsule-button__rest-tint-orange` 6.923 -> 7.296 codes (+0.372)
- `2x-light/checkerboard-8__rrect-md__rest` 16.989 -> 17.848 codes (+0.859)
- `2x-light/checkerboard-lc16__rrect-sm__rest` 6.836 -> 6.965 codes (+0.130)
- `2x-light/hc-text-28__rrect-lg__rest` 7.806 -> 10.298 codes (+2.492) [rrect-lg]
- `2x-light/hc-text-28__rrect-md__rest` 18.034 -> 20.771 codes (+2.736)
- `2x-light/hc-text-7__rrect-lg__rest` 7.327 -> 8.609 codes (+1.283) [rrect-lg]
- `2x-light/hc-text__rrect-lg__rest` 7.845 -> 9.921 codes (+2.076) [rrect-lg]
- `2x-light/light-solid__capsule-button__rest` 2.306 -> 2.333 codes (+0.028)
- `2x-light/light-solid__rrect-sm__rest` 3.152 -> 3.166 codes (+0.014)

## S1 as R2 (read in G3, adopted only by the user's ruling at the landing)
- webgpu: pooled median ratio 0.877 (window [0.8, 1.2]), 15 wrong-sign cells:
  - `1x-light/checkerboard-64__capsule-button__rest-tint-orange` V +0.0030 against dA -0.0029
  - `1x-light/checkerboard-lc16__capsule-button__rest` V +0.0247 against dA -0.0061
  - `1x-light/checkerboard-lc16__rrect-sm__rest` V +0.0055 against dA -0.0182
  - `2x-light/checkerboard-4__capsule-button__rest` V +0.0064 against dA -0.0096
  - `2x-light/checkerboard-4__capsule-button__rest-tint-orange` V +0.0013 against dA -0.0032
  - `2x-light/checkerboard-64__capsule-button__rest-tint-orange` V +0.0034 against dA -0.0028
  - `2x-light/checkerboard-8__capsule-button__rest-tint-orange` V +0.0004 against dA -0.0024
  - `2x-light/checkerboard-lc16__rrect-sm__rest` V +0.0049 against dA -0.0170
  - `1x-dark/light-solid__rrect-lg__inactive` V +0.0000 against dA +0.0417
  - `1x-dark/light-solid__rrect-ml__inactive` V +0.0000 against dA +0.0417
  - `1x-dark/photo__capsule-button__inactive-tint-orange` V +0.0001 against dA -0.0016
  - `2x-dark/checkerboard-lc16__rrect-sm__rest` V +0.0000 against dA -0.0083
  - `2x-dark/light-solid__rrect-lg__inactive` V +0.0000 against dA +0.0417
  - `2x-dark/light-solid__rrect-ml__inactive` V +0.0000 against dA +0.0417
  - `2x-dark/photo__capsule-button__inactive-tint-orange` V +0.0001 against dA -0.0014
- css: pooled median ratio 0.874 (window [0.8, 1.2]), 11 wrong-sign cells:
  - `1x-light/checkerboard-4__capsule-button__rest` V +0.0001 against dA -0.0197
  - `1x-light/checkerboard-4__rrect-sm__rest` V +0.0063 against dA -0.0197
  - `1x-light/checkerboard-lc16__rrect-sm__rest` V +0.0037 against dA -0.0182
  - `1x-light/light-solid__capsule-button__rest` V +0.0006 against dA -0.0057
  - `2x-light/light-solid__capsule-button__rest` V +0.0009 against dA -0.0061
  - `2x-light/photo__toolbar-group__rest` V +0.0013 against dA -0.0298
  - `1x-dark/checkerboard-4__capsule-button__rest` V +0.0000 against dA -0.0081
  - `1x-dark/hc-text-28__rrect-md__rest` V +0.0008 against dA -0.0079
  - `1x-dark/light-solid__rrect-lg__inactive` V +0.0000 against dA +0.0417
  - `1x-dark/light-solid__rrect-ml__inactive` V +0.0000 against dA +0.0417
  - `2x-dark/photo__capsule-button__inactive-tint-orange` V +0.0000 against dA -0.0014

## Passing rows (no miss): WebGPU tables, M1, C1, X1, L1 (four dark inactive dark-solid means UNMEASURED, as at 0.5).
