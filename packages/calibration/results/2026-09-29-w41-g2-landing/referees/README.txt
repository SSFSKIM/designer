W41 G2 referees — the adopted rows' cuts, ported to W40's generation store (c9a §5.193)
=========================================================================================

Branch w41-g2-referees, cut from the seal f5760e17. Nothing here writes results/matrix.json,
results/generations/, results/superseded/, profiles/ or a capture tree. Freeze 1,818.

The scripts
-----------
W36's five cut scripts, copied verbatim (commit d782e120) and then ported; `git diff
d782e120 -- .` is the whole port. Logic and output are W36's. What moved is where rows come
from (referee_source.py), plus the inputs the brief names:

  chroma-cut.py     M1/M2   rows from the store; M2's reference a (active, receded) PAIR
                            resolved by load_generation (default: the generation current when
                            the gate opened — light 85ad7f7e3e0d/30fbe05986ae, the one this read
                            retires; dark 0eac5b294cc2/5cec8c961201, which W41 leaves in place,
                            so it is its own reference and its per-wave change is zero by
                            construction). The cut gains referenceGeneration.*.recededDocumentSha256.
  m2-rebaseline.py  M2 table  W31 pre-fit origin resolved by pair; per-wave reference from the cut.
  exterior-cut.py   C1      rows from the store; --against names generations by pair.
  black-cut.py      X1      rows from the store; PNGs from --captures roots (below).
  l1-cut.py         L1      rows from the store; W33 baseline resolved by pair; matrixSha256 is
                            the legacy-envelope digest the owner test takes; the shipped check
                            reads both documents against the files on disk, as the test does.
  e2-regression.py  E2      new. e2.py's population() / reference() / compute() imported, not
                            forked; per bin against the frozen e2-baseline.json.gz under E2's
                            1-code bound; LOST and absent captures fail, UNMEASURED is counted and
                            never passed; PNG identity shown per cell, not assumed; cells the rule
                            admits outside the frozen 212 are named UNMEASURED (no baseline).
  referee_source.py       the one row source. Default: the current union (canonical matrix path
                          passed explicitly, so VITREA_MATRIX_PATH cannot redirect it).
                          --stage DIR: the current union with every (profile, tier) pair the stage
                          HAS rows for replaced by them; declared pairs it holds no row for keep
                          their current rows, and every output records both lists. A declared
                          non-holdout cell missing inside a replaced pair refuses (--partial
                          overrides for a scratch look). --captures ROOT (repeatable): each cell
                          is read from the root whose cell__webgpu.json names the row's exact
                          capturePath; a tree holding another generation is refused, not read.
  scratch-union.py        writes a stage's scratch union as one schema-5 file whose SHA-256 is
                          the L1 cut's matrixSha256, for VITREA_MATRIX_PATH.
  reproduce.py            the port's proof (below).

Run commands (from this directory; export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1)
------------------------------------------------------------------------------------------
STAGE=/Users/new/vitrea-w41/g2-stage-light
G2=/Users/new/vitrea-w41/g2-captures/canonical-stage/
CAN=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures

$G2 is the stage captures' archive. They were read from this worktree's web-captures/,
which was removed at the close (../close/). Every --stage command refuses at the branch head:
the stage declares the sealed receded document 003940b4c7da, the revert 15478e0f put
30fbe05986ae back on disk, and referee_source.py refuses a declared document that is not the
file on disk. Replay stop-reading/ from the pre-revert commit ee859b5a instead:
  git worktree add --detach /tmp/w41-g2-replay ee859b5a
  cd /tmp/w41-g2-replay/packages/calibration/results/2026-09-29-w41-g2-landing/referees
  python3.12 -B black-cut.py --stage $STAGE --captures $G2 --captures $CAN --out OUT/black-cut.json
black-cut.json comes out byte-identical to stop-reading/'s (fa1c50df…). So do l1-cut.json and
exterior-cut.txt with the commands below; chroma-cut.json differs only in generatedAt, and
e2-regression.json only in the captures root it records.

Stage (before publication):
  python3.12 -B chroma-cut.py    --stage $STAGE --out OUT/chroma-cut.json
  python3.12 -B m2-rebaseline.py --cut OUT/chroma-cut.json --out OUT/m2-rebaseline.json
  python3.12 -B exterior-cut.py  --stage $STAGE --out OUT > OUT/exterior-cut.txt
  python3.12 -B l1-cut.py        --stage $STAGE --out OUT/l1-cut.json
  python3.12 -B black-cut.py     --stage $STAGE --captures $G2 --captures $CAN --out OUT/black-cut.json
  python3.12 -B e2-regression.py --stage $STAGE --captures $G2 --captures $CAN \
                                 --out OUT/e2-regression.json --bins OUT/e2-regression-bins.json.gz
  python3.12 -B scratch-union.py --stage $STAGE --out /tmp/union.json   # for the owner test
Published (after `matrix publish` and the capture tree's copy to $CAN): the same commands
without --stage, and without --captures (the default is $CAN). Outputs default to this
directory, which is where the drafted test pointers look.

Reproduction (reproduce.py -> reproduction.json)
------------------------------------------------
Run from the pre-seal main 4f43d2dc with this directory copied in: its generation store is
byte-identical to the seal's, and its light receded file is still the 30fbe05986ae the
pre-W41 rows name. (At f5760e17 the shipped guards refuse those rows — the seal interval:
chroma drops the light cells, black-cut and l1-cut assert, e2-regression refuses; the
exterior cut, whose guard reads the active document only, is unchanged.) With W36's inputs:
  black-cut.json   byte-identical (328f18dc…)
  l1-cut.json      byte-identical to W36 G2's (ca14c7ac…); matrixSha256 7df96c92… is W36's
  m2-rebaseline    byte-identical when fed W36's chroma cut; from the ported cut, identical
                   once the added recededDocumentSha256 is set aside
  chroma-cut.json  identical once generatedAt (a wall clock) and the added
                   recededDocumentSha256 (per scheme) are set aside
  exterior-cut     identical once `source` is set aside (W36 recorded its worktree's path)
  e2-regression    212/212 PNGs and rows identical to the frozen baseline, 7,728 measured
                   bins at delta 0, 1,488 UNMEASURED, e2.summary equal to e2-summary.json.
The drafted test changes with these reproduced cuts at the drafted paths: 118/118 pass at
4f43d2dc (adopted-thresholds + generation-stage, canonical captures).

stop-reading/ — every referee in --stage mode (manifest.json holds hashes)
---------------------------------------------------------------------------
Stage 3558cee9… (288 WebGPU rows, 1x/2x light standard; RT/IC and CSS refused by X6 and
kept from the current union). adopted-thresholds-at-stage.txt is the owner test run with
VITREA_MATRIX_PATH=scratch union, a merged capture tree and pointers at these cuts: 91 pass,
10 fail. E3's own failures: M2 (8 light-inactive photo cells, +14.6 % to +44.6 %, with the
8 matching MISSED_27_ROWS additions), L1 absolute (12 inactive checkerboard cells,
0.111–0.148) and L1 growth (17 cells). Not E3: the stage holds no holdout yet (gated light
counts 72 -> 66, texture tier 36 -> 30: 10 holdout out, 4 recorded in) and it reads every
manifest fixture — 64 probe and 16 recorded light WebGPU cells W36's generation never
carried — so C1's CONTRIBUTING_CELLS (light span 96 10 -> 12, span 160 7 -> 8), W20
conformance on recorded checkerboard__capsule-button__pressed 1x (declaredContourMaxWeb 2)
and the conditioning predicate (+ recorded photo__rrect-md__pressed 2x) move. Pass: M1,
C1's twelve statistics, X1 on 230 cells, E2 on its 212.

drafts/ — prepared, not applied
-------------------------------
adopted-thresholds.test.ts.patch  the four cut pointers -> this directory; the chroma
                                  reference loaded by pair (post-publication the light
                                  active hash owns two files and the unqualified call throws).
generation-stage.test.ts.patch    the recorded-capture case reads the current generation from
                                  the index instead of naming 85ad7f7e3e0d / 30fbe05986ae.
publisher-list-alias.patch        src/generation-stage.ts writes every byDocumentSha256 alias
                                  as a list; with the plain publisher the first new hash is a
                                  bare string, which W40's Python adapter refuses, so every
                                  Python reader of the index (e2.py, these scripts) stops at the
                                  first publication. Red then green in generation-stage.test.ts.
python-adapter-string-alias.patch the adapter reads a bare-string alias as a one-item list, as
                                  the TypeScript reader does (needed only if a publication
                                  lands before the publisher patch).
