# W44 G0 — part 1, the mechanism-check protocol, and the part-2 draft (readable twin of `declaration.json`)

Charter `docs/doperpowers/specs/2026-10-03-w44-texture-at-0-25.md` v1.2 (`0ee27ae2`), clause 1 and
X50; ledger §5.202. The machine record is `declaration.json`: it declares each item once, points at
the files that define it and pins every one by SHA-256, the part-2 draft
(`fit-declaration-draft.json`) and the tool that validates part 2 against it (`declare.py`)
included, so one hash covers the protocol and the draft. `declare.py check` re-derives every number
and list below from those files and runs the three red-case suites; `declare.py hash` writes
`declaration.sha256` and refuses once hashed or once a ladder render exists. Part 1's `amend` is
refused once any ladder render exists (`ladders/runs.jsonl` records a launch, or the ladder scratch
holds a matrix), and each part is amended at most once.

## The row

### t1

T1 is the driver's `interiorStdDev` — the luminance SD in linear light over the NATIVE silhouette
bounded to the declared region, rim and lens band included — web against native, read off each row.
One code at a cell is the linear step of one sRGB code at the cell's native interior mean.

- **Population.** Every scene the light 0.25 profiles declare on the eleven structured backdrops, in
  every set, both scales, both tiers: 116 per profile, F 19 (`checkerboard-4`, `-8`, `hc-text-7`),
  C 69 (the pitch-16 family, `-lc16`, `-32`, `-64`, `hc-text`, `hc-text-28`, `impulse`), P 28 (photo).
  Each cell is in one partition: holdout 16, referee 6, gate 94. A stage carries the gate partition
  until the exposure.
- **Outputs.** With n native, c the c05 reading and k the candidate's, B = max(1 code, 2 bar):
  fidelity `within` when |k − n| ≤ B, or n ≥ 1 code and |k/n − 1| ≤ 0.10, else `miss`; change by
  precedence `unchanged` (|k − c| ≤ bar), `overshoot` (crossed native and a miss), `toward` (error
  fell, or an equal-error crossing; g = 0 read to 1e-12), `away`; aggregates per stratum × scale ×
  tier × pose, the median |log((k + ε)/(n + ε))| with ε one code, and the state counts.
- **Gated** on the WebGPU tier of the two light 0.25 profiles; read on their CSS tier, the dark 0.25
  profiles and the 0.5 profiles. The landing scope is WebGPU 2x light, both poses, F ∪ C ∪ P, the
  gate partition; a member with no reading makes the verdict UNMEASURED.
- **Pinned.** The charter's four change-state examples and ten more cases, `cuts/test_t1.py`.
  `cuts/cuts.py` reports T1 beside W43's rows and leaves the referees out of every other population.

### readings

Beside T1 and never gated (`cuts/readings.py`):
- **T1-deep**, the eye sheet's statistic: encoded Rec.709 luma SD on the declared region eroded
  8 CSS px. W43's sheets record no crop of their own, so this one is declared; it reproduces the
  0.25 anchors.
- **T1-fine**: the σ 4 device px residual over the native silhouette eroded 4 CSS px, linear.
- **T1-lattice**: a masked difference of Gaussians, σ 1 to 4 CSS px, over the same eroded silhouette.
  It is added before part 1 because it isolates the receded 2x photo lattice: ×1.32–1.60 on the 2x
  inactive single-shape photo cells, where T1 reads ×0.78–0.91.

## The bar

### bar

Per cell, 0.5 code plus half the largest pairwise separation of the seven G1a runs' native T1
values, read through a port of the driver's interior statistic (`port/interior.py`). The port
matches the recorded `interiorStdDevNative` and `interiorMeanNative` on all 772 rows of the 386
cells it was proven on, worst 2.3e-10 against a 1e-6 tolerance. Every run of every cell is the same
frame as the published fixture, so the separation is 0 and the bar is 0.5 code on all 386 cells
(232 of them gated). No cell's bar exceeds one code, so none is read rather than gated. The archive
is `w43-archive-g1a`, inventory `56489f87…`.

## The rehearsal

### rehearsal

On the published c05 generation T1 reproduces the pinned baseline (`rehearsal/c05-baseline.json`,
committed before any T1 run) on all 464 structured rows, and the three findings on their named
subsets: (i) thin rest medians 0.49–0.86; (ii) the F mid and thick rest median 1.79, with
`checkerboard-8__rrect-md__rest` and both `hc-text-7` cells under 1; (iii) the inactive median 2.81,
with `checkerboard-64` and thick `hc-text` named and two subset cells under 2 named beside them. The
stop does not fire: c05's thick fine-pitch cells sit 4.4 bars or more from Apple's. T1-deep reads
the anchors at 2.87 / 9.08 and 0.29 / 10.49 (0.5: 1.74 / 2.54), where T1 reads ×2.07, ×3.95 and
×0.92. The landing rule's T1 clauses close at the finding on c05 (F aggregate 0.5689, its own; no
cell away) and on the pre-fit render (50 away beyond B); the selection metric prefers c05, 0.3451
against 0.5034, tie 0.0406. The moire is a ring 12–16 CSS px inside the contour, in the lens band;
the lattice is the backdrop's own diagonal one, passed at ×1.32–1.60 in the σ 1–4 CSS px band.

## The referees

### referees

Six probe scenes held out on both light 0.25 profiles, twelve cells (`referees/referees.json`). The
planner derives the pre-gate probe list (81 scenes, `--set probe`) and the exposure list (26 scenes:
the canonical holdout plus the referees, `--set holdout,probe`). The fit loader refuses a candidate
bed carrying one, W43's pre-fit render's referee rows are dropped and never read, and the gate
refuses a stage holding one before the exposure. Fourteen fine scenes per scale are the fit's. The
charter's thirteen counts the coarse referee among the fine.

### ledgerWitness

`configuration.py record … --referees <manifest>` records the manifest's path and SHA-256 as
`refereeManifest`. It is witness-only metadata and never a configuration discriminator. A read
without it writes the entry it wrote before W44.

## The ladders

### ladders

Eight ladders over the protocol's leaves (`ladders/protocol.json`), 29 rungs beside the c05 control:
- L1 `sizeScatterFloor2x`;
- L2 `sizeHeavyTapSigma2x`, at floor 1, device px;
- L3 the second tap's share and 2x width at floor 1, CSS px, its 1x width held at 0;
- L4 `sizeScatterRampStartThin2x`;
- L5 `sizeScatterRampReach2xPx`, device px, at both bases;
- L6–L8 the receded document's own thin start, thick/far pair and heavy width.

Each rung is a complete scratch candidate built from the c05 documents moved on one leaf, from c05 or
from the floor-1 rung. It is keyed `glass0.250`, because candidate mode refuses the shipped 0.25 keys.
It is drawn on 17 fixed cells at 2x and as their 1x twins: three fine pitches, three coarse and the
photo, both poses where a pair exists, no referee and no holdout. The ladders may:
- strike a flat leaf;
- strike a leaf that moves a 1x capture (X48);
- fix family C's inert 1x setting, or strike C;
- narrow a grid to its non-flat range.

Nothing else.

### references

The regression references are the published c05 generations, light `6d18c059eb42` and dark
`d0219cd684bf`, by their files' SHA-256 in `generations/index.json` (X52).

## The draft

### draft

`fit-declaration-draft.json` holds the three moves with their domains, grids, units and predictions,
the search procedure, the selection rule and the landing rule, rehearsed on c05 and the pre-fit
render. Part 2 is this draft plus a `changes` list. `declare.py` applies each change only where
`ladders/results.json` supports it, and refuses any other difference: 15 red cases in
`test_declare.py`.
