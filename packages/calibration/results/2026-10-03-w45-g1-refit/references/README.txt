W45 G1 step 1: the one reference (charter clause 6; X52).

c05, the published 0.25 generation, is the reference for every regression row and for T1's change:
6d18c059eb42 (light, file sha256 in results/generations/index.json) and d0219cd684bf (dark). W45's
cuts (results/2026-10-03-w45-g0-operator/cuts/cuts.py, as pinned by part 2 e6874e02) read it against
itself, rows from the generation files and captures from the canonical tree, which
check-capture-tree holds to those rows:

  cd packages/calibration/results/2026-10-03-w45-g0-operator
  python3.12 -B cuts/cuts.py --published 6d18c059eb42 --published d0219cd684bf \
    --captures /Users/new/Developer/GitHub/designer/packages/calibration/web-captures \
    --out <scratch>/c05-cuts.json --text ../2026-10-03-w45-g1-refit/references/c05-cuts.txt   (exit 0)

c05-cuts.json.gz is that output. Against G0's own c05 cut (rehearsal/c05-cuts.json.gz) it differs
in nine leaves and no reading: cutsSource's rule.py and bed.py hashes (both moved by part 2's first
amendment and G0's bed pin), and the seven groups' `gateCells` field, which the first amendment's
rule fix added (§5.205 §13 item 4). Every row, cell, verdict and rule output is equal: the cuts are
rehearsed once more on c05 and reproduce it.

What it fixes for the gate (c05 read against itself):
- M2, L1, E2: re-baselined on c05 (their reference is c05's rows and captures); 0 misses, L1's
  four dark inactive dark-solid cells UNMEASURED as at W43/W44.
- T1's change on c05: 94 of 94 gate cells `unchanged`; the W45 rule reads NEITHER (11 F cells not
  within, the F aggregate not halved), the budget at 0, every gated aggregate holding.
- The c05 aggregates the landing rule compares against (2x light WebGPU, gate cells): F 0.6462
  pooled (F rest 0.6334, F inactive 1.2903 reported), T rest 0.5251 (T1-fine), C rest 0.1720,
  C inactive 0.8523, P rest 0.4193, P inactive 0.1393; selection metric 0.3458.
- The other adopted rows at c05: tables pass on WebGPU (CSS: 1x light checkerboard rrect-ml ssim
  0.87367, a named miss), M1, M2, C1 (WebGPU), L1, X1 (WebGPU), E2 pass; S1 misses (read, adopted
  only by ruling).
