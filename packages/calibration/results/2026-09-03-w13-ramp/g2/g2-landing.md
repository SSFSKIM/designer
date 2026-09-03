# W13 G2 — the landing (2026-09-04)

The body's depth ramp, fourth form (claims §5.68), landed on `main`: `c9a9cad` recorded the
predictions first (Decision Log 8 executed on the branch, the dry run read — claims §5.68 §7),
then merge `347af25` (W13 G1, branch `w13-g1-ramp` at `beb823f`), then the canonical rebuild and
the bookkeeping below. The parent ran every step; the one subagent was the review fix wave on the
branch (`beb823f`).

## 1. The rebuild

`g2-rebuild.sh` (this directory) from W14's: workspace build at `347af25` (0 dirty; the built
renderer carries the far anchor), the W14 bed and its captures kept in scratch
(`matrix-before-w13.json`, `web-captures-before-w13` under `~/.claude/jobs/5c70e47f/tmp/w13/g2/`),
`results/matrix.json` removed, then the twelve per-profile runs to the canonical matrix and
captures. `g2-runs.txt` is the driver log: every run `exit=0`, ALL RUNS DONE 01:35:08; 230
cells, 230 captures. GPU custody 01:30:17–01:35:08.

## 2. Against the dry run and the CSS confirmation (`g2-verify-landing.py`)

- **GPU tier, the four standard profiles (98 cells):** every row equal to the dry run's (worst
  |Δ| 0.000000) and every capture **byte-identical to the dry run's, 98 / 98** — holdout
  included, so the dry run's reading (claims §5.68 §7) is the holdout's one reading of this
  configuration and the landing reproduced it rather than re-reading it. `beb823f`'s three
  fixes reached no capture, as predicted.
- **CSS tier, the four standard profiles (98 cells):** every row equal to sweep-4's CSS
  confirmation (`g1/sweep-4/matrix-confirm-css.json`), worst |Δ| 0.000000.
- **The twelve rows of claims §5.68 §4** (`ssimMean`, GPU tier, checkerboard, canonical):

  | cell | 1x | 2x |
  | --- | --- | --- |
  | `rrect-sm` | 0.9990 | 0.9978 |
  | `capsule-button` | 0.9856 | 0.9836 |
  | `rrect-md` | 0.9862 | 0.9840 |
  | `rrect-ml` | 0.9797 | 0.9746 |
  | `glass-over-glass` | 0.9823 | 0.9761 |
  | `rrect-lg` | 0.9743 | 0.9680 |

  `toolbar-group` 0.9642 / 0.9662. The 1x column is the declaration's; the 2x column is the
  W14 bed's (the parenthesised column of §4), the stacked cell one ten-thousandth under it
  for the proxy-padding shift §7 attributes.
- **The accessibility profiles (increased contrast, reduced transparency; 17 cells per tier)
  had no dry-run reference** — the declaration's stops ran on the standard profiles — so they
  are read against the W14 bed here. CSS tier: within 0.0002 on every row. GPU tier: the
  `photo` cells unchanged to four decimals; the checkerboard and `hc-text` cells move —
  `ssimMean` −0.0002 to −0.0004, `ssimBand` −0.0024 / −0.0013 / −0.0033 (checkerboard
  capsule / checkerboard `rrect-md` / `hc-text` capsule) under increased contrast and −0.0024 /
  −0.0013 / −0.0030 under reduced transparency, `ssimOutside` within 0.0001. The ramp under the
  accessibility folds was neither declared nor measured before the landing; no floor is
  touched (§3); carried in W13's Deferred as a gap with its numbers.

## 3. Adopted thresholds (`test/adopted-thresholds.test.ts`)

**31 passed on the rebuilt bed before any edit.** No row fell below a floor or a bound,
`PREDICATE_EXCLUDES` equals the machine's output unchanged, and no floor was removed or
re-pinned: `UNMET_ROWS` stays at W14's 8. The ramp raised every 1x checkerboard band row the
declaration names and left the 2x rows the bed's, which is inside every adopted bound.

## 4. Goldens, behind the isolation proof

The proof and the goldens on the merged tree: **26 passed, no golden moved.** `goldens:regen`
was run on the same code in the branch worktree (at `beb823f`) and rewrote all ten goldens byte
for byte (0 of 96 000 pixels differ on each). The reason, recorded beside `W14_HASHES` in
`isolation.spec.ts`: every golden scene renders at device pixel ratio 2, and at 2x the landing
changes nothing by design — the ramp is a verified null there and the widths are the bed's
(Decision Log 8); the proof's declined renders reproduce the pinned bytes because the named
profile's scatter gain of 1 makes the sharp and heavy components one, so the mix has nothing to
act on. No hash re-recorded. **The gap:** no golden exercises the 1x ramp — Deferred.

## 5. The demo fixture

`apps/demo/e2e/fixtures/checkerboard__capsule-button__rest__webgpu.{png,cell.json}` re-copied
from the canonical captures (the 1x light capsule moved with the ramp: 4 436 → 4 556 bytes);
`reference-panel.gpu.spec.ts` 1 passed.

## 6. The workspace

`pnpm -r lint` clean; `pnpm -r test` green, 1 725 tests — policy 23; motion 162; geometry 149;
renderer-webgpu 384; core 302; platform-web 352; calibration 256; react 97.

## 7. The sheets (`sheets/g2-1x.png`, `g2-2x.png`, `g2-caption.txt`)

`g2-1x.png` is byte-identical to `g1-1x.png`: the 1x configuration did not change between
sweep-4's confirmation and the landing, and the captures reproduce its bytes, so the user's
reading of the G1 sheet stands as S7. `g2-2x.png` shows the landed 2x as the bed — panels 2 and
3 the same bytes on every row — with Apple's heavier 2x interior the visible remainder, the
deep-value gap chartered in Deferred.

## 8. Gaps carried out of this landing

- The stacked cells' proxy padding at 2x follows the 1x ramp's projection while the GPU tier
  draws the bed's law there (claims §5.68 §7) — a term of the 2x charter.
- The ramp under the accessibility folds: band −0.001 to −0.003 on six GPU cells (§2), not
  declared, not measured against the reference's own accessibility material.
- No golden exercises the 1x ramp (§4).
- From the declaration (claims §5.68 §6): the coverage-ramp `ssimOutside` thousandth on the
  `hc-text` capsule (S5 by −0.00105), the far anchor unfittable on the calibration cells, the
  thin anchor 0.08 above G0's read-off, and the 2x deep value with the widths as its second
  term.
