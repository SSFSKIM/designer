# W15 G2 — the landing (2026-09-04)

The 2x body (claims §5.70; W15 Decision Log 3, the re-form) landed on `main`: merge `8cae88e`
(W15 G1, branch `w15-g1-2x-body` at `138c34c`, its constants the landed defaults), then the
canonical rebuild and the bookkeeping below. The parent ran every step; the workers were the
three implementation rounds on the branch (`3426b0a`, `c746553`, `138c34c`).

## 1. The rebuild

`g2-rebuild.sh` (this directory, from W13's): workspace build at `8cae88e` (three untracked
files — the changeset, this directory, the attribution spec — nothing tracked dirty), the W13
bed and its captures kept in scratch (`matrix-before-w15.json`, `web-captures-before-w15` under
`~/.claude/jobs/5c70e47f/tmp/w15/g2/`), `results/matrix.json` removed, then the twelve
per-profile runs to the canonical matrix and captures. `g2-runs.txt` is the driver log: every
run `exit=0`, ALL RUNS DONE 05:18:47; 230 cells, 230 captures. GPU custody 05:13:52–05:18:47.

## 2. Against the confirmation and the W13 bed (`g2-verify.py`, `g2-verify.txt`)

- **GPU tier, the four standard profiles (98 cells):** every row equal to the re-form's
  confirmation (`g1/confirm-3/`, worst |Δ| 0.000000) and every capture **byte-identical to the
  confirmation's, 98 / 98** — holdout included, so the confirmation's one reading of this
  configuration stands and the landing reproduced it rather than re-reading it.
- **1x, every profile (66 GPU cells): byte-identical to the W13 bed, 66 / 66** — the wave's
  binding rule, verified on the canonical bed itself. The accessibility profiles' 17 GPU cells
  are inside that count (every row 0.0000 against the bed).
- **CSS tier (115 cells):** every row within 0.0002 of the W13 bed and 114 / 115 captures
  byte-identical; the one that differs, `light-solid__rrect-md` at 2x, by ≤ 2 codes on 9 853 px
  with `ssimOutside` +0.00022 — the CSS tier's frame timing on this machine (W13 Surprises; the
  tracker), not the landing: the tier's code path at `CSS_TIER_RAMP_SCALE = 1` reads no
  second-scale term (Decision Log 3).
- **The twelve rows** (`ssimMean`, GPU tier, checkerboard, canonical):

  | cell | 1x | 2x (W13 bed) |
  | --- | --- | --- |
  | `rrect-sm` | 0.9990 | **0.9988** (0.9978) |
  | `capsule-button` | 0.9856 | **0.9860** (0.9836) |
  | `rrect-md` | 0.9862 | **0.9903** (0.9840) |
  | `rrect-ml` | 0.9797 | **0.9860** (0.9746) |
  | `glass-over-glass` | 0.9823 | **0.9843** (0.9761) |
  | `rrect-lg` | 0.9743 | **0.9762** (0.9680) |

  `toolbar-group` 0.9642 / 0.9666 (0.9662). The 1x column is the W13 bed's to the digit.

## 3. Adopted thresholds (`test/adopted-thresholds.test.ts`)

**31 passed on the rebuilt bed before any edit.** No row below a floor or a bound,
`PREDICATE_EXCLUDES` equals the machine's output, no floor removed or re-pinned: `UNMET_ROWS`
stays at 8 — the four CSS 2x floors are unchanged by construction (the tier did not move) and no
GPU 2x floor has existed since W14. Every 2x GPU row rose inside its bound.

## 4. Goldens, behind the isolation proof

**Attributed by measurement before the merge, not re-recorded blind.** `e2e/golden/
w15-attribution.spec.ts` (an instrument that runs only under `VITREA_ATTRIB_OUT`) read back
every golden scene's declined (the proof's named profile) and default renders on the pre-merge
tree (`c9edbb0`) and on the landed one; `attribute-goldens.py` diffed them (`attribution.txt`):
`body-ramp-1x` (the 1x pin, W15 contract X7) **0 of 24 000 pixels**; `field-mask`, the two tint
adaptations and `highlight-press-glow` 0 of 96 000 each; the six dpr-2 scenes over structure
move inside their surfaces with alpha untouched — `refraction-checkerboard` 27 413 px by ≤ 10
codes, `placed-checkerboard` 30 502 by ≤ 19, `lens-size-scaling` 25 610 by ≤ 17, and the three
over flat backdrops (`rim-two-references` 3 118, `concentric-nesting` 1 299, `union-pair` 514) by
exactly 1 code. Pinned as `W15_G2_HASHES` (six scenes) in `isolation.spec.ts` with that record;
`goldens:regen` rewrote exactly those six PNGs; the isolation proof's non-vacuity and fail-before
tests pass. `scenes.spec.ts`'s cover-fit hash re-recorded (`7980eed2…` → `a0cd4e7b…`) with its
reason, and its "different pictures" bound lowered from 24 to 16 codes: the deeper 2x body blurs
the two fits more alike deep inside the surface and they now differ by 22 codes at most on 0.147
of the pixels. Golden suite **29 passed**.

## 5. The demo fixture

`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.{png,cell.json}` re-copied
from the canonical captures: the PNG byte-identical (1x), the `.cell.json`'s capture metadata
moved; `reference-panel.gpu.spec.ts` 1 passed.

## 6. The workspace

`pnpm -r lint` clean (after the attribution spec's one type error, fixed); `pnpm -r test` green,
**1 737** tests — renderer-webgpu 396; platform-web 352; core 302; calibration 256; motion 162;
geometry 149; react 97; policy 23.

## 7. The sheets (`sheets/g2-2x.png`, `g2-1x.png`)

Both **byte-identical to the re-form's dry-run sheets** (`g1r-2x.png`, `g1r-1x.png`; captions
in `g1r-caption.txt`): the landing captures reproduce the confirmation's bytes, so the user's
reading of the dry run — "W15 looks pretty good too" on the first configuration, the re-form's
sheet sent 2026-09-04 — stands as S7 at the landing.

## 8. Gaps carried out of this landing

- `ssimOutside` beyond 0.001 on two cells at 2x (`toolbar-group` −0.0016, the `hc-text` capsule
  −0.0018): the coverage-ramp thousandth W13 recorded on the same statistic.
- The thin spans' interior spread 0.011–0.012 under native at 2x (the capsule and the toolbar)
  where the large spans land within 0.003–0.009: a heavy width one number at spans ≤ 96.
- The 2x gain's top (12.4 device px at span 256) is unobserved above span 160.
- The compare's `interiorStdDev` is a whole-silhouette statistic; as a stop it pulls against the
  band rows (claims §5.70 §4, Surprises).
- The CSS tier at 2x keeps the 1x law by decision; the four-column table (claims §5.70 §5) is
  the two-layer CSS body charter's brief.
- The CSS tier's frame timing on this machine (one 2x solid cell by 2 codes).
