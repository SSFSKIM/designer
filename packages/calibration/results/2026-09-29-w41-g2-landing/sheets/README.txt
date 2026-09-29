W41 G2 — the standing eye sheets with the candidate column now shipped (c9a §5.193)
===================================================================================

Branch w41-g2-sheets, cut from w41-g2-landing 63089862 (worktree /Users/new/vitrea-w41/g2-sheets).
The sheets are G0's instrument (§5.191: the fixed 2 x 3 table, OKLab ΔE x 8, export-png.py) and
G1's reading of it (§5.192 §19-§20), with the columns renamed for what they now are:

  Native | Shipped pre-W41 | Shipped now (E3)
         | Pre-W41 ΔE x 8  | Now (E3) ΔE x 8

Shipped pre-W41 is the retired light generation: active 85ad7f7e3e0d, receded 30fbe05986ae
(results/generations/85ad7f7e3e0d.json; the receded bytes resolve to ../retired-documents/).
Shipped now is the sealed generation: active 85ad7f7e3e0d, receded 003940b4c7da. Every capture's
cell__webgpu.json must name exactly that pair and the bytes must exist, or the sheet refuses.

Files
-----
examples-declaration.json  the fourteen example identities, committed (7dde9f49) before any
                           pixel of this gate was decoded or viewed.
sheets.ts                  the G2 adapter: sheetHtml (G0's shape, new labels), inspectCapture
                           (document pair + retired-copy resolution + pose), distances, and the
                           `canonical` / `w39` commands. sheets.test.ts: four synthetic tests
                           (tests.txt 4/4; typecheck.txt strict tsc exit 0).
run-w39.json, run-canonical.json   the exact inputs of each run.
verify-w39.py              the per-cell W39 check (below). Output: w39-verification.json.
select-examples.py         copies ONLY declared identities out of a scratch run, byte for byte,
                           into examples/, binding them in examples/selection.json.

From packages/calibration:
  python3.12 -B results/2026-09-29-w41-g2-landing/sheets/verify-w39.py > <scratch>.json
  pnpm exec tsx results/2026-09-29-w41-g2-landing/sheets/sheets.ts w39 results/2026-09-29-w41-g2-landing/sheets/run-w39.json
  pnpm exec tsx results/2026-09-29-w41-g2-landing/sheets/sheets.ts canonical results/2026-09-29-w41-g2-landing/sheets/run-canonical.json
  pnpm exec tsx --test results/2026-09-29-w41-g2-landing/sheets/sheets.test.ts
Outputs go to a fresh directory under /Users/new/vitrea-w41/g2-captures/sheets/ (refused otherwise).

What neither command does: start a browser or capture; write a matrix, generation, profile or
fixture; open a canonical holdout path (a cell's role is read from scenes.json and a holdout cell
is dropped before any path is formed, and the stage's declared set must agree with that role);
open any W39 native except through G1's guarded native.py (Reader.read, calibration/validation
roles, repeat ordinal 0, and the returned PNG must hash to the one G1's sheet recorded); open any
of the 64 blind W39 identity captures.

W39 bed: G1's 536 sheets already show the shipped E3 pixels (w39-verification.json)
----------------------------------------------------------------------------------
verify-w39.py decompresses G1's committed render-inventory.json.gz (checked against its primary
SHA-256 f52dbcb0...) and, for each of the 536 RENDERED W39 cells:
  - the G2 identity capture's metadata names the sealed pair for its scheme (live bytes);
  - its PNG SHA-256 equals the candidate capture G1's sheet was rendered from, and the
    identity/comparison.json entry (status identical);
  - G1's scratch sheet HTML and PNG still hash to what G1's inventory records;
  - the Candidate image EMBEDDED in G1's HTML decodes to exactly the identity PNG's RGBA.
Result: 536 / 536 VERIFIED, 0 failed. The eight phase-*-zero memberships stay UNMEASURED as in
G1. So in G1's W39 sheets the column labelled "Candidate" IS the shipped E3 material and the
column labelled "Shipped WebGPU" is the pre-W41 material; G1's owner-eye-reading of its W39
examples is a reading of the shipped pixels.
The seal moved exactly the 134 light-inactive W39 cells (67 at 1x, 67 at 2x); the 134
light-active and all 268 dark cells are byte-identical between G1's baseline and the identity
capture — the active and dark controls read identical.

W39 examples (13, 14): rendered as G2 sheets from the three sources above
(w39-examples-inventory.json; scratch /Users/new/vitrea-w41/g2-captures/sheets/w39-examples-1/).

Canonical bed
-------------
Pending: the canonical light read's WebGPU passes for the reduced-transparency and
increased-contrast profiles have not completed (canonical/runs.jsonl records exit codes for
the 1x and 2x standard passes only). Examples 1-12 and the canonical inventory follow it.
