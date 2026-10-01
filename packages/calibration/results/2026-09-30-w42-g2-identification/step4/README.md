# W42 G2 steps 4–5 — the landing candidates rendered and refereed, before the exposure (2026-10-01)

Charter `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`, clauses 7–10 and Decision
Logs 5a–5f and 7; the improvement-landing addendum (`../improvement-landing-addendum.md`, SHA-256
`0398c9c8…`, committed at `034594ab`); the hashed G0 declaration `f04ae95b…`. The code is
`w42-g2-impl` at `b92bfb1f` (the perf wave's compute stage and its review fixes), merged here as
`d012ac6a`. **Clause 11 was not entered:** no H prediction is frozen, no receipt opened, and H was
never requested from the archive's guarded reader.

## The verdict

**Neither candidate passes rule 4 in any endpoint, so no candidate reaches the exposure.** H stays
sealed. Clause 10 was not owed to either candidate; it was run on candidate 2 anyway, as evidence
for the next decision, and candidate 2 would fail it in every endpoint as well.

| | light active | light receded | dark receded |
| --- | --- | --- | --- |
| clause 7 (both beds) | c1 pass (≤ 1.00), c2 pass (≤ 0.21) | c1 pass (≤ 1.00), c2 pass (≤ 0.07) | c1 pass (0.00), c2 pass (≤ 0.28; canonical ≤ 0.44) |
| rule 4 (a), c1 | **FAIL** 7 of 17 strata | pass | **FAIL** colour checker s = 96 |
| rule 4 (b), c1 | **FAIL** 831 statistics, 31 cells, worst +17 | **FAIL** 867, 11 cells, worst +10 | **FAIL** 1,350, 31 cells, worst +19 |
| rule 4 (a), c2 | **FAIL** grey checker s = 160 (3.746 vs 3.732) | pass | pass |
| rule 4 (b), c2 | **FAIL** 558, 4 cells, worst +14 | **FAIL** 862, 10 cells, worst +10 | **FAIL** 842, 7 cells, worst +12 |
| clause 10, c2 (informational) | **FAIL** Stop H, E2 | **FAIL** M2, Stop P | **FAIL** M2 |

"worst +N" is how many codes the candidate's error exceeds the shipped render's on one statistic
(the bar is +2).

## Clause 8, the runtime base (`runtime-base.json`)

- `check-capture-tree` on the main checkout's tree (read only) exits 0: 1,900 captures, 1,893 match,
  7 have no row.
- The 40 cells of `bed/runtime-base-sample.json`, rendered with the shipped documents at this base,
  are **40/40 PNG byte-identical** to the tree. Chromium 151.0.7922.34, `apple/metal-3`, no CSS
  fallback, deterministic over two loads.
- The shipped scratch stages rendered for clause 10 widen this: all 386 WebGPU cells of the six gated
  profiles' current membership (772 PNGs, alpha captures included) are byte-identical to the tree,
  and their 386 `compare` rows equal the current generation's rows field for field, `capturedAt`
  apart.

## The documents (`documents.ts` → `documents/`)

- `c1`: LT at the addendum's least-squares point over the landed solve, with the shader's
  black-join bridge. Light receded adds E3 with W41's sealed gains and F (receded document
  `003940b4c7da`) and the F extension. Dark active is the shipped file.
- `c2`: LT with the native-T table and the landing chroma scales (0.976496 / 0.987365 / 0.909586)
  on W41 G1's least-squares gains. E3 is off; dark active is the shipped file.
- `c1ref`: clause 7's light-receded reference, E3 with its extended F alone.

Every document passes `readMaterialProfileFile` / `readRecededProfileFile` and
`withMaterialOverrides`, and records its own rule-2 digest. The same digest function reproduces the
four shipped digests.

**One departure, recorded and not hidden.** The runtime's `bodyToneTableCodes` is one 5 × 11 row set
read on encoded luma (`body_table_codes`), but the addendum names one row set per channel. `c2`
therefore carries the Rec.709 combination of the three row sets (`bodyToneTableCodesRec709`), which
keeps each grey's output luma. A grey's channel departs from its own row set by at most 0.79 / 0.93
/ 0.79 codes (light active / light receded / dark receded). The only verdict inside that margin is
c2's light-active rule 4 (a), at 0.014 rms, and (b) fails there regardless. Candidate 2 as written
needs a per-channel table, which is a size change in the runtime, before it could ever be sealed.

## Rule 4 and clause 7 on the W42 bed (`rule4.py` → `rule4.json`, `rule4.txt`)

**The read.**
- 284 web-plannable calibration/validation cell-passes. The strata reproduce the addendum's section 5
  counts exactly (85 / 92 / 107).
- Each cell was rendered three times (shipped, c1, c2) through `render.py bed`. The fixture root is
  the side bundle's own backgrounds (`bed/side-check`), checked raster by raster against
  `backgrounds-verification.json`.
- All renders were read with the declared instrument against Apple's plurality frames through step
  2's guarded reader (pins verified, raw root denied).
- The full per-statistic table is in scratch, named by SHA-256 in `rule4.json`.

**Where the (b) failures fall against the addendum's section 7 named gaps.** This is a description
for the parent; rule 4 has no exemption.

**Candidate 2:**
- **Light active:** all 558 failing statistics lie on rrect-lg cells: the 1x pitch-8 class (a)
  checker (+14), and class (b), +3, on 2x pitch-8, 1x pitch-32 and the 1x impulse grid.
- **Light receded:** class (a) (+8.5), class (b) (+6.5) and family E chroma (+10). Also 24
  statistics outside every named gap: the pitch-64 rrect-md checkers b-p2, b-p3 and b-p5, worst +5.
  There the law flattens the checker: on b-p2 Apple reads 181 / 200 (knee / far), shipped 182 / 198,
  c2 187 / 194.
- **Dark receded:**
  - 2x bp-p1-c64-rrect-ml, +12. This is class (b) and the native-T dark completion at s = 128
    (gap 3): Apple 107, shipped 109, c2 93.
  - Class (a), +9.
  - Family E chroma, +8.
  - Outside the named gaps, only 3 statistics on b-p4-c16-rrect-md, +3.

**Candidate 1** adds the landed T's level misses that the declaration predicted:
- the grey-middle miss in light active, for example the impulse surround at +17 to +18;
- the black-end dip in dark receded, for example 1 code where Apple reads 22.

**Clause 7 on the canonical uniform cells, c2** (`clause7_canonical.py`, `clause7-canonical.json`):
24 untinted cells against `bodyToneTableCodesAt`, worst 0.44. Candidate 1 was not rendered on the
canonical bed.

## Clause 10 on candidate 2 (informational; `clause10.sh`, `clause10/c2/`)

Scratch stages (`stage.py`) hold the current generation's non-holdout WebGPU membership of the six
gated profiles. The base is the shipped stages above, rendered on this base.

- **Owner test** (`owner-summary.json`):
  - The base passes 109/109. The candidate passes 107; its 2 new failures are both M2.
  - **M2 failures:**
    - Dark receded: photo rrect-md inactive, 1x and 2x, past Apple by +3.7 % and +2.3 %.
    - Light receded: photo rrect-sm inactive, 1x and 2x, flattened away from Apple (−5.1 % and
      −16.9 % per wave).
    - Light receded: 2x toolbar inactive, past Apple by +3.6 %.
  - Sixteen M2 moves toward Apple are named (Decision Log 5a).
  - **L1:**
    - Growth fails only on the four Decision Log 5d tinted cells, which are named: +0.0069 / +0.0102
      / +0.0062 / +0.0094.
    - The existing named miss, the 1x light tinted impulse inactive cell, is re-recorded at 0.0551.
    - Its 2x twin closes.
  - **M1, C1, X1:** all pass. X1 reads 0 pixels above native black on 218 cells.
- **Stop H** (15/16): fails on 1x light impulse rrect-md rest, light active. The peak reads Apple
  25.2, shipped 33.0, c2 15.3.
- **Stop P** (24/26): fails on two light-receded cells:
  - 1x toolbar inactive M: Apple 12.59, shipped 14.07, c2 10.13 (× 1e-3);
  - 2x rrect-md inactive F: Apple 3.453, shipped 3.494, c2 3.081.
- **E2 per cell** (Decision Log 5e; `e2cell.py`): 11 of 212 cells fail, all light active on the
  capsule, with means worse by 0.001–0.24 code. There are 34 named-miss bins on 7 cells, worst 1.5.
- **Eye sheets** (`sheets-inventory.json`; outputs at `/tmp/w42-g2-step4/sheets/c2/`; `run-sheets.json`):
  - All 204 sheets are rendered. The text stratum's 12 cells that have no rows, and the 16 gradient
    cells, were re-rendered at the shipped pair on this base (`render.py looks`).
  - The candidate's body reads nearer native in every stratum and pose. Two examples of the mean
    body ΔE: light binary inactive 0.040 → 0.013, dark photo inactive 0.086 → 0.038.
  - The only cells farther from native are the tinted cells of Decision Log 5d and the tinted
    capsule cells, by ≤ 0.0033.
  - By eye, the light-active impulse dot is softer than native, the opposite side from shipped,
    which is Stop H's cell.

## Reproduce

```bash
cd packages/calibration && pnpm exec tsx results/2026-09-30-w42-g2-identification/step4/documents.ts
cd results/2026-09-30-w42-g2-identification/step4
python3.12 -B render.py base-proof
python3.12 -B render.py bed shipped; python3.12 -B render.py bed c1; python3.12 -B render.py bed c2
python3.12 -B render.py bed c1ref --families=A 2x-light-receded 1x-light-receded
python3.12 -B rule4.py
python3.12 -B render.py canon shipped; python3.12 -B render.py canon c2
python3.12 -B render.py looks shipped; python3.12 -B render.py looks c2
python3.12 -B stage.py shipped; python3.12 -B stage.py c2; ./clause10.sh c2
(cd ../../.. && pnpm exec tsx results/2026-09-29-w42-g0-declaration/gate/sheets/sheets.ts render \
  results/2026-09-30-w42-g2-identification/step4/clause10/c2/run-sheets.json)
```

Scratch lives under `/tmp/w42-g2-step4`; `runs.jsonl` logs every browser launch with X6's settings
facts. No profile, generation, matrix or canonical capture changed, and nothing was published.
