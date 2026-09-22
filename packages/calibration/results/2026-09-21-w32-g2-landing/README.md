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

## The review closure (2026-09-22; claims §5.169 §10)

Six files added after the cut, by the closure that landed on this branch before
the merge. Nothing else in this directory moves except `eye.md` and `dry-run.*`,
each corrected or re-run where the closure's findings say so.

| file | provenance |
| --- | --- |
| `contour-stroke.py` / `.txt` | New, finding **B2**. Reads the `0-3` band outward from the declared rect **one DEVICE pixel at a time** along the four straight edges, on the `photo` bed at spans 44 and 160, both poses, over all six macOS 27 profiles — 24 cells. It shares no code with `b4-black-floor.py` beside it. What it decides is the band's SIGN and WIDTH: the native is 14–30 bytes darker at one device pixel on 22 of 24, the two sides agree from two pixels out, and the web is darker than the native on 0 of 24. So the term is Apple's contour hairline standing un-drawn on both poses, not a 3.5–4 CSS px vitrea over-fill. It ends with the literal transect the finding started from |
| `laws-e2e-n3.txt` | New, finding **N3**. The demo's `/laws/` suite re-run after the readout began reading `materialDocument.tuned` — 10 of 10, with the machine reading taken before it (`browser-runs.txt`, `laws-e2e-n3`) |
| `closure-chain.txt` | New. The verification at the closure's head: `freeze.py verify` 1,818 at open and close, build / lint / root eslint exit 0, **2,703 unit tests over 187 files**, the three profile export tests, `publish-shape`, the new React case, the `/laws/` e2e and the rehearsal, with the two gated-count pins unmoved |
| `closure-freeze-open.txt` / `closure-freeze-close.txt` | New. The freeze at the closure's own open and close, kept separately from the cut's pair so neither reading is rewritten |
| `dry-run.txt` | **Re-run**, because Decision Log 5 gives the React package a source change after the cut. Core and web are byte-identical; react is 188,179 B against 187,860 and its export count 37 → 38. `dry-run.sh`'s header said "0.21.0 … §5.165 §5", the version it was copied from, and is corrected to its own gate |
| `eye.md` | **Corrected in place, beside**: §4 and §4b for B2's sign, and §1 for N8 — a CSS-tier `MISSED_27_ROWS` entry was cited to explain a WebGPU panel whose own rows cleared at W31 G3 |

`browser-runs.txt` goes from fourteen X6 readings to **sixteen**, the two new ones
bracketing the `/laws/` re-run. Every one reads RT 0, IC 0, `NSGlassTintAmount` 0.5.

## What is NOT here

No matrix, no profile document, no capture and no fixture: this gate wrote none
of those and moved none of them. The canonical `web-captures/` tree the sheets
read is gitignored and lives on the capture machine; `VITREA_WEB_CAPTURES` points
the scripts at it and `sheets.txt` records which tree they read.
