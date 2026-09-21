# W32 G2 — the landing: what is in this directory, and where each file came from

Claims **§5.169**. The gate adopts `C1`, re-states `B3` under Decision Log 3 (a),
re-baselines `M2` under Decision Log 4, builds the `/laws/` shadow stage under
Decision Log 1 (d), sweeps the docs, runs the chain and prepares **0.22.0**. No
material change, no native capture, nothing re-read, no matrix row moved.

## The cuts and the stops

| file | provenance |
| --- | --- |
| `exterior-cut.py` / `.json` / `.txt` | **W32 G0's, copied byte for byte** and re-run here against the matrix W32 G1's read left. That re-run is the adopting gate's obligation under claims §5.162 §9 finding B-1; `adopted-thresholds.test.ts`'s C1 clause reads this JSON and then re-derives every reading in it from `results/matrix.json` |
| `b3-stop.py` / `.txt` | W32 G1's `b3-window.py` **generalised**: that file printed the statistic as a decomposition and said it had no bar, and Decision Log 3 (a) gave it one. Prints the statistic, the bound (0.000056) and PASS/FAIL, exits nonzero on a fail, and prints the per-pose and per-bed decomposition so the pooled number hides no bed |
| `departure-stat.py` / `.json` / `.txt` | W32 G1's, copied and re-run at the same generation, so the superseded whole-exterior form keeps its last reading (0.00072) beside the re-stated one |
| `chroma-cut.py` / `.json` / `.txt` | W31 G4's by way of W32 G1's, with **one change**: `REFERENCE_ACTIVE_DOCUMENTS` names the generation W32 G1 read rather than W31's pre-fit bed, the field is `interiorStdDevWebReference`, and the guard that the baseline predates the chroma instrument is INVERTED rather than dropped |
| `m2-rebaseline.py` / `.txt` | New. The per-wave table Decision Log 4 asks the ledger to carry: all 26 gated cells at three generations, with the per-wave column M2 bounds and the cumulative-from-W31-pre-fit column beside it |
| `cut-discrimination.sh` / `.txt` | New, in W31 G4's shape. Five perturbations, each reverted before the next, including by name the seeded bogus excuse Decision Log 4 asks this gate to prove. The three perturbed files' SHA-256 are printed at the end against copies taken before the first |

## The sheets and the eye

| file | provenance |
| --- | --- |
| `sheets.ts` / `.txt`, `sheet__*.png` (31) | W31 G4's by way of W32 G1's, bed changed to this wave's, **one panel of arithmetic added**: the one-byte count over the exterior beside every ΔE × 8 panel (§5.168 §10, finding B-4). The per-cell shipped-bytes assertion and the refusal are kept |
| `halo.py` / `.txt` | New. W29 G3b's far-exterior band and amplification, computed from the fixtures and the capture trees rather than read back off a PNG, at the 0.21.0 generation and at the shipped bytes |
| `demo-sheet.py` / `.txt`, `demo-beside-harness-*.png` (3) | New; replaces W31 G4's `sheet.py` for one wave, because the row has a third thing in it — the harness native, the harness WebGPU, the `/laws/` stage and the site's material stage |
| `laws-shot.mjs`, `laws-shadow-*.png` (4) | New, in W31 G4's `demo-shot.mjs` shape. The `/laws/` shadow stage at spans 96 and 160 in both poses, with the readout printed beside each |
| `demo-shot.mjs` | W31 G4's, copied, reason updated: the site's material stage is three spans of one authored thickness side by side |
| `laws-pin-discrimination.txt` | New. Two seeded defects in `law.ts` against the stage's e2e pin, each reverted |
| `eye.md` | The look, written from all of the above |

## The chain

`chain.sh` is W31 G4's with this gate's paths and **`check-capture-tree` added as
a step**, which is where W32 G0b's own record said the checker joins. It ran
**twice**. `chain-run-1/` is the first run, whole, red on `pnpm -r lint`, with its
own README saying what the red found; the files beside this one are the second
run at the fixed head, thirteen steps of thirteen at exit 0. `browser-runs.txt`
carries all fourteen X6 readings, both runs' and this gate's own.

`dry-run.sh` / `.txt` is the publish rehearsal at 0.22.0, W29 G4's script by way
of W30 G4's and W31 G4's. `gated-count.py` is W32 G1's, copied.
`record-machine.sh` is W31 G4's, unchanged.

## What is NOT here

No matrix, no profile document, no capture and no fixture: this gate wrote none
of those and moved none of them. The canonical `web-captures/` tree the sheets
read is gitignored and lives on the capture machine; `VITREA_WEB_CAPTURES` points
the scripts at it and `sheets.txt` records which tree they read.
