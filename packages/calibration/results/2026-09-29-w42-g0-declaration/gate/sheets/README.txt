W42 G0 gate: the standing eye sheets by stratum (charter clause 10; X33, X34; ledger §5.194)
===============================================================================================

Branch w42-g0-gate (worktree /Users/new/vitrea-w42/g0-gate). Clause 10 asks for eye sheets
chosen BY STRATUM (uniform, binary structure, text, impulse, photo, gradient), each showing
native | shipped | candidate with OKLab ΔE × 8, and names the text and gradient strata as
looks, not referees. This folder declares the six strata and extends W41 G2's sheet adapter
(§5.193) to them. It keeps W41 G0's fixed 2 x 3 table, so G0's export-png.py draws it unchanged:

  Native | Shipped            | Candidate
         | Shipped ΔE x 8     | Candidate ΔE x 8

Reused rather than re-derived: W41 G0 sheets.ts (differencePanel, inspectCell, canonicalRole)
and export-png.py; W41 G2 sheets.ts (exportPng, the bounded regular-file exporter, and
g1Inventory, the pinned G1 sheet inventory); W41 G1 sheets/native.py, the guarded W39 bridge.

Files
-----
strata.json         the declaration: the four profiles, each stratum's rule, backgrounds, tinted
                    ruling, role exclusions and resolved cells; the input hashes; the shipped
                    document pair per profile, read from results/generations/index.json; the
                    declared sources. SHA-256 59532bf1425f68e04b26aa1e8cab068195e15aad050cd02d7af1878d33caff23.
sheets.ts           declare / check / render (below). sheets.test.ts: four synthetic tests.
run-identity.json   the demonstration's exact inputs (candidate = the shipped trees).
identity-inventory.json   that run's inventory.json, byte for byte (SHA-256 0cde5d98...c2c3).
tests.txt           4/4 pass, exit 0.  typecheck.txt: strict tsc over both files, exit 0.

Strata and membership (strata.json)
-----------------------------------
Profiles: apple-macos-27.0-{1x,2x}-{light,dark}-standard-glass0.5. WebGPU tier, both poses. A
canonical cell is a scene the profile holds in scenes.json whose background kind matches the
rule and whose split role the rule admits. A W39 cell comes from W39's own wave (split.json and
launch_plan over calibration/validation), so its holdout never enters the plan.

  stratum   rule (background kind; roles)          cells  light/dark  rest/inactive  tinted
  uniform   solid; calibration+validation            40    26 / 14      20 / 20        12
  binary    checkerboard; calibration+validation     38    26 / 12      20 / 18        12
  text      text-rows; PROBE                         48    24 / 24      32 / 16         0
  impulse   impulse; calibration+validation          16    12 /  4       8 /  8         4
  photo     synthetic-photo; calibration+validation  46    34 / 12      24 / 22        20
  gradient  W39 linear-gradient; cal+val, web plan   16     8 /  8       8 /  8         0
  total                                             204   (102 at 1x, 102 at 2x)

Excluded by role, never a path: uniform 12 holdout + 124 probe; binary 12 holdout + 8 recorded +
152 probe; text 12 holdout; impulse 20 probe; photo 18 holdout + 12 recorded + 4 probe; gradient
0 holdout. W39 excluded by its plan: the ref and opaque controls (native-only) and v90-column
(two surfaces; the web side has no column kind).

What the rules resolve to, and one gap in the uniform rule:
- uniform is light-solid and dark-solid only. The brief's mid-*-solid backdrops contribute NO
  calibration/validation cell: mid-dark-solid capsule rest/inactive are holdout and every other
  mid-dark, mid-light and mid-chroma scene is probe. The grey middle (W36's named miss, and
  candidate 2's T) therefore has no uniform sheet. The mid-* probe cells hold rows and captures
  and would be admissible looks under X34, as the text stratum's are; adding them changes the
  declaration, so it is the parent's call and is NOT done here.
- binary is `checkerboard` (16 px, 0/255) only; its pitch series and lc16 are probe.
- text is hc-text rrect-sm/-lg (rest; rrect-sm, rrect-lg inactive), hc-text-7 and hc-text-28
  (rrect-sm/-md/-lg rest, rrect-md inactive), 12 per profile; the hc-text capsule and rrect-md
  cells are holdout.
- gradient is v90-c-c44 and v270-c-c44 in both poses, all W39 calibration.

Tinted, per stratum: included wherever calibration/validation holds them, because the spatial
operators sit before the tint composition and the referees read those cells (L1's two named
misses are light inactive tinted impulse; W41's E3 failure included the tinted photo inactive
cells, §5.193 §3). The text and gradient beds have no tinted cell; hc-text's tinted capsule is
holdout.

Sources and their document pairs
--------------------------------
Shipped pairs, from the generation index's current selection and checked against the live
bytes: light 85ad7f7e3e0d / 30fbe05986ae, dark 0eac5b294cc2 / 5cec8c961201. `render` refuses if
the index has moved since the declaration.

Canonical strata (uniform, binary, text, impulse, photo):
- native: the committed fixture apps/reference-apple/fixtures/<profile>/<scene>.png, opened
  only after scenes.json has given the scene a role its stratum admits.
- shipped: the canonical capture tree, /Users/new/Developer/GitHub/designer/packages/
  calibration/web-captures. All 176 captures it holds for these strata name exactly the shipped
  pair of their profile, and each one is the capture its current generation row names
  (currentRow names-this-capture 176/176).
- text exception, 12 cells: hc-text__rrect-sm__rest, hc-text__rrect-lg__rest and
  hc-text__rrect-sm__inactive in each of the four profiles. They have no current matrix row,
  and NO capture at the shipped pair exists for them anywhere on this machine. The closest is
  W41 G2's light stage (/Users/new/vitrea-w41/g2-captures/canonical-stage). It is light only and
  names 85ad7f7e3e0d / 003940b4c7da (E3, which did not ship). For the two rest scenes only the
  receded clause differs, and W41 G2 found every active-pose control byte-identical across that
  change (122/122), but these cells were not among the controls it compared. The inactive one
  draws E3's body. Nothing exists for dark. It is not admitted: a capture naming another pair is
  refused. Those sheets read NOT-RENDERED (shipped UNMEASURED) until G2 renders the three scenes
  at the shipped pairs on its own base. `canonical.shippedRoots` is an ordered list for that
  purpose, and each root must name the shipped pair.
- runtime base: the canonical tree was measured at its generation's base. Clause 8 proves byte
  identity on a declared sample at G2's base before any candidate render.

Gradient stratum:
- native: the W39 archive (cache /Users/new/.cache/vitrea-archives/489db938.../extracted/archive)
  through W41 G1's native.py, repeat ordinal 0, native generation 58329732.... The PNG must hash
  to the native G1's sheet recorded for the cell (render-inventory.json.gz, primary f52dbcb0...).
- shipped: W41 G1's frozen baseline, /Users/new/vitrea-w41/g1-captures/baseline (freeze
  frozen-baseline.json c921d671..., source revision 014e4104, an ancestor of this branch). All 16
  captures name the shipped pairs above and must be the PNGs the freeze names. W41 G2's identity
  capture re-rendered 12 of them byte-identically at W41 G2's base: the 8 dark, and the 4 light
  active, whose receded clause named E3. The 4 light inactive are attested at G1's base only,
  because G2's identity capture drew E3 there. Checked here by PNG SHA-256, 12 SAME / 4 DIFF.
- runtime base: this bed is outside clause 8's canonical sample, and G1's baseline predates
  0.25.0's frames on demand (399c6bbf; its capsule-radius fix is a vitrea-react patch that the
  calibration page does not load). G2 either re-renders these 16 at
  the shipped pairs on its base and points gradient.shippedRoots there, or states the base
  difference beside the gradient verdict.

Commands (from packages/calibration)
------------------------------------
  pnpm exec tsx results/2026-09-29-w42-g0-declaration/gate/sheets/sheets.ts check
  pnpm exec tsx results/2026-09-29-w42-g0-declaration/gate/sheets/sheets.ts render <run.json>
  pnpm exec tsx --test results/2026-09-29-w42-g0-declaration/gate/sheets/sheets.test.ts
`declare <path>` wrote strata.json and refuses to overwrite. `check` and `render` re-resolve the
declaration and refuse if the committed bytes differ.

run.json fields:
  label               names the candidate in every sheet and index
  outputRoot          absolute, fresh, outside every git work tree (refused otherwise)
  candidateDocuments  {profileKey: [{kind: materialProfile|recededProfile, path, sha256 (12 hex)}]}
                      for all four profiles; paths inside the checkout; bytes must hash to them.
                      Every candidate capture must name exactly this pair, or the run refuses.
  canonical           {shippedRoots: [first root holding the cell wins], candidateRoot}
  gradient            {shippedRoots, candidateRoot, archiveRoot, repeat,
                       g1Inventory: {gzip, sha256}, shippedFreeze?: {path, sha256}}
Capture cells are <root>/<profileKey>/<sceneId>/<sceneId>__webgpu.png beside cell__webgpu.json.
A capture must name the scene, WebGPU and sRGB, the profile's scale and scheme with
accessibility=browser-preferences, and the expected document pair (W41 G0's inspectCell).

Output: <outputRoot>/<stratum>/<profile>__<scene>.{html,png}, <stratum>/index.html (rule, a table
of every declared cell with status and body distances, then the sheets), index.html, and
inventory.json. The inventory binds the run config, strata.json, every native, shipped and
candidate PNG and cell JSON, every sheet HTML/PNG and index by SHA-256. Per cell it also records
the mean OKLab distance to native over the declared body region (componentRegion, no margin) and
over the whole frame, candidate minus shipped, and the body pixels that moved and the share of
them now nearer native. These are a diagnostic beside the eye, not a referee. Statuses: RENDERED,
RENDERED-SHIPPED-ONLY / RENDERED-CANDIDATE-ONLY (the missing column reads UNMEASURED),
NOT-RENDERED (neither web capture), NO-NATIVE.

Tests (tests.txt: 4/4, exit 0)
------------------------------
On a synthetic repository, with one calibration and one holdout scene, both with fixtures and
captures in every tree:
1. a candidate capture naming the shipped pair, a candidate document whose bytes exist nowhere,
   and a shipped capture naming the candidate's receded document are each refused;
2. a holdout cell declared as calibration is dropped on scenes.json's role, and the path trace
   shows no path formed for it; a declared role that disagrees refuses. A mutation that forms a
   path before the drop turns this test red (checked by hand, then restored);
3. the full render draws the five panels through G0's exporter, and the body distances count
   the moved pixels; an identity candidate embeds the same ΔE panel twice; a missing candidate
   keeps the table's shape and reads UNMEASURED;
4. output inside a git work tree, an existing directory or the repository is refused.

Demonstration: candidate = shipped (identity-inventory.json)
-------------------------------------------------------------
run-identity.json points each candidate root at the shipped root and declares the shipped
pairs as candidate documents. Output (60 MB, outside git): /tmp/w42-gate-sheets/identity-1/.

  stratum   declared  sheets  not rendered              candidate == shipped bytes
  uniform      40       40       0                              40
  binary       38       38       0                              38
  text         48       36      12 (no shipped capture)         36
  impulse      16       16       0                              16
  photo        46       46       0                              46
  gradient     16       16       0                              16

In all 192 sheets the embedded Candidate image and ΔE panel are the Shipped ones, byte for
byte. Every recorded input and output hash re-verified. The 16 gradient natives came through
the bridge and matched G1's recorded PNG. No holdout was declared, so none was dropped. Two
sheets were looked at directly: gradient 1x light v90-c-c44 inactive, and text 1x dark
hc-text-7 rrect-md inactive. Both show the three columns and two ΔE panels at original pixel
size.

What this does not do
---------------------
It starts no browser or capture, and it writes no matrix, generation, profile, fixture or
capture. It opens no canonical holdout or recorded path: roles come from scenes.json before any
path is formed, and no stratum admits either role. It opens no W39 native except through G1's
native.py, which admits only calibration/validation and is checked against G1's recorded PNG. It
reads no pixel of the W42 bed; none exists. It gives no verdict: the parent records the eye
verdict per stratum (clause 10: no stratum visibly further from native than shipped), and the
distances are not a bar. It does not fill the 12 text cells' shipped column, the gradient bed's
runtime-base gap or the missing mid-* uniform cells. Those are named above.

Added by the stream owner, 2026-09-29 (the rehearsal, ../rehearsal/README.txt)
-----------------------------------------------------------------------------
The run config takes an optional `only` (a list of stratum names). A stratum left out is drawn
as nothing and every one of its cells is recorded NOT-DRAWN in the inventory, never as a pass.
The rehearsal drew the five canonical strata on the candidate 2 body-swapped tree
(../rehearsal/runs/c2/run-sheets.json; outputs at
~/vitrea-w42/scratch/gate-rehearsal/sheets-rehearsal-c2/, inventory sha256 9092b88d...):
the swap has no W39 gradient render to act on, so the gradient stratum is NOT-DRAWN there.
