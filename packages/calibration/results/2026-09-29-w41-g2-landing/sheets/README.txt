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
                           pixel of this gate was decoded or viewed; examples-amendment.json
                           withdraws 12 and adds 15-18 at the owner's request (9202f2cc).
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

Canonical bed (canonical-inventory.json)
----------------------------------------
The G2 owner's go-ahead changed the brief's precondition. The canonical light read finished
WebGPU for the two standard profiles only: 1x and 2x, 144 cells each (stage
/Users/new/vitrea-w41/g2-stage-light, membership b0d78e3c..., matrix.json rows). X6 refused
the reduced-transparency and increased-contrast launches (a foreign playwright-cli daemon),
and the owner ruled that RT, IC and the CSS tier are not read in G2. run-canonical.json
records them under notCapturedInG2; no path of theirs is formed.

Every rendered capture must be the one its stage row names: the row's capturePath must equal
the capture's cell__webgpu.json. Pre-W41 is the main checkout's canonical tree, which must name
the retired pair. Native is the committed fixture.

  declared WebGPU cells                 390  (4 light profiles)
  holdout, dropped by role unopened      48
  NOT-CAPTURED-IN-G2 (RT, IC)            54
  RENDERED (native | pre-W41 | now)     208  = 104 at 1x + 104 at 2x
    active-pose controls                122  byte-identical pre-W41 = now: 122 / 122
    light-inactive                       86  byte-identical: 3 (tinted capsules over solids)
  RENDERED-NOW-ONLY                      80  recorded (8) + probe (32) per scale, no capture
                                             at the retired pair; the pre-W41 column says so
  G1 canonical-diagnostic overlap        98  new PNG byte-identical to G1's candidate: 98 / 98

So for the 98 standard calibration/validation cells, G1's canonical diagnostic sheets and G1's
owner-eye-reading of examples 06/07 are readings of the shipped pixels. The full 288 HTML +
PNG set (81 MB) stays outside git at /Users/new/vitrea-w41/g2-captures/sheets/canonical-1/;
canonical-inventory.json (byte-identical to that run's inventory.json, SHA-256 b21c2228...)
binds every input PNG and output HTML/PNG by SHA-256, plus a distances diagnostic per cell.

texture.py -> body-texture.json (radius 6 px at 1x), body-texture-r3/r12/r24.json:
  python3.12 -B results/2026-09-29-w41-g2-landing/sheets/texture.py <inventory.json> [radius] [erode]
It re-reads each light-inactive cell's three PNGs (hash-checked), takes the moved pixels
eroded away from the rim, and splits each body into fine structure and broad miss, in L and in
chroma. This separates the case where E3 adds texture from the case where E3 removes a broad
offset and reveals texture that was already there.

Examples and the eye draft
--------------------------
examples/ holds 17 PNG + HTML, byte-identical to scratch, bound in examples/selection.json:
1-11 and 13-14 as declared. Example 12 (the RT control) is withdrawn: RT was not captured in
G2. Examples 15-18 are post-declaration additions requested by the owner after the referees
stopped the landing (examples-amendment.json, 9202f2cc), made before any canonical pixel
was viewed in this gate. owner-eye-draft.json is the draft reading, for the owner, who writes
the reading of record.

tests.txt: 4/4 synthetic tests; typecheck.txt: strict tsc exit 0 (re-run after the RT/IC
and stage-row changes). No browser or capture was started by this gate.
