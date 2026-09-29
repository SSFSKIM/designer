W42 G0 referees — W41 G2's ported cuts with a candidate-admission mode (charter clause 10)
=========================================================================================

Charter docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md v2.1, clause 10 and
Design "The instrument (G0)": "W41 G2's ported referees refuse a declared document that is not
the file on disk; the mode admits a declared scratch document matched by hash and stamps every
output 'candidate', with a red/green test." Ledger §5.194. Nothing here writes
results/matrix.json, results/generations/, results/superseded/, profiles/ or a capture tree.

What changed against 5b3712f7 (the verbatim copy of ../../../2026-09-29-w41-g2-landing/referees/)
------------------------------------------------------------------------------------------------
`git diff 5b3712f7 -- .` is the whole change. Statistics, bounds, exclusions, the M2
reference generations (light 85ad7f7e3e0d/30fbe05986ae, dark 0eac5b294cc2/5cec8c961201) and
every `--claims` default are W41's; with no --candidate every output keeps the port's bytes.

  paths             the copies sit one directory deeper (results/<dir>/gate/referees), so every
                    HERE.parents[n] moved by one. black-cut's ROOT and e2-regression's ROOT/live()
                    were used only by the guards below and are gone.
  referee_source.py --candidate PATH[=SHA12], repeatable. PATH is named as rows name it:
                    repo-relative, or absolute and shown repo-relative by capture-web's own rule
                    (materialProfileLabel: inside the repo relative, outside it absolute). The
                    SHA-256 is taken from the file's bytes; a given SHA12 that differs refuses; a
                    PATH under packages/calibration/profiles/ refuses (the shipped file); a PATH
                    declared twice refuses. `Source.admitted` = profiles/*.json at their live
                    hash (the owner test's SHIPPED_DOCUMENT_HASHES construction) + each declared
                    candidate at its hash; a declared PATH at any other hash is not admitted.
                    A candidate is read only through a stage: --candidate with no --stage, or a
                    candidate no stage's membership names, refuses, so a stamp never labels
                    shipped rows. Stamps: `Source.stamp` ({"admission": {"mode": "candidate",
                    "documents": [{path, sha256, sha12}]}}, placed after `source`),
                    `Source.at_documents` ("candidate"), `Source.banner()` (stdout's first line,
                    "# CANDIDATE admission: ..."). Base mode: {}, "shipped", nothing printed.
                    --stage DIR is repeatable (a W40 stage holds one active/receded pair, so a
                    candidate over both schemes is two stages). Each stage is validated on its
                    own exactly as W41 validated one (declared documents admitted, every row at
                    the declaration's pair, non-holdout coverage inside a held pair); their
                    replaced (profile, tier) pairs must be disjoint; the union replaces all of
                    them. One stage: `source` is W41's dict, byte for byte. More than one:
                    `source` = {label, stages: [W41's dict per stage]}.
  chroma-cut.py     M1/M2 bed guard reads `source.admitted`; `shippedDocuments` stays the files
                    under profiles/; stamp + atDocuments + banner.
  exterior-cut.py   --at-documents shipped reads `source.admitted` (still the active document
                    only, as W36's did); stamp + atDocuments ("any" stays "any") + banner.
  l1-cut.py         the per-row assert reads `source.admitted`; stamp + atDocuments + banner.
  black-cut.py      the per-row assert reads `source.admitted`; stamp + atDocuments + banner.
  e2-regression.py  the per-row refusal reads `source.admitted`; stamp (e2 has no atDocuments;
                    its keys are sorted) + banner.
  m2-rebaseline.py  reads a cut, not rows: no --candidate; a stamped cut's `admission` is
                    carried after `source`, and stdout opens "# CANDIDATE".
  scratch-union.py  --stage repeatable, --candidate admitted; the union file is a schema-5 matrix
                    and carries no stamp; stdout opens "# CANDIDATE".
  test_admission.py the red/green test (below); admission-test.txt is its output.

A tightening of base mode, deliberate. W41's _stage, black-cut's assert and e2-regression's
refusal asked whether the file at the row's named path hashes to the named digest. A scratch
document at its own repo path satisfies that, so W41's port would have ADMITTED a candidate
stage in base mode through _stage, black-cut and e2 while chroma-cut and exterior-cut dropped
its rows in silence and l1-cut asserted. Here a document outside profiles/ is admitted only by
declaration, so base mode on a candidate stage refuses in _stage with the reason. On the
inputs W41's port reads at shipped documents the outputs are unchanged (proved below on the
current union and on a stage).

Not this mode's reach: the owner test. adopted-thresholds.test.ts reads rows through its own
SHIPPED_DOCUMENT_HASHES / atAShippedDocument (18 uses) and asserts `atDocuments === "shipped"`
on the chroma, exterior, black and l1 cuts, so it drops or refuses a candidate row and a
candidate-stamped cut by design. Clause 10's owner-test run is ../owner/run-owner.py (ed1c4e7a):
the test unmodified in a disposable worktree with the candidates installed at their profiles/
names, where these scripts' base mode applies. A cut stamped `candidate` here is the gate's
reading of the candidate at its own path and is never a pointer the owner test can take.

Run commands (from this directory; export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1)
------------------------------------------------------------------------------------------
Outputs default to this directory and black/l1/e2 open theirs exclusively: pass --out.
CAN=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures   (the default)

Base, the current union (the published generation):
  python3.12 -B chroma-cut.py    --out OUT/chroma-cut.json
  python3.12 -B m2-rebaseline.py --cut OUT/chroma-cut.json --out OUT/m2-rebaseline.json
  python3.12 -B exterior-cut.py  --out OUT > OUT/exterior-cut.txt
  python3.12 -B l1-cut.py        --out OUT/l1-cut.json
  python3.12 -B black-cut.py     --out OUT/black-cut.json
  python3.12 -B e2-regression.py --out OUT/e2-regression.json --bins OUT/e2-regression-bins.json.gz

Base, one stage at the shipped documents (W41's --stage mode, unchanged): add --stage $STAGE
to every row reader, --captures $STAGE_CAPTURES --captures $CAN to black-cut and e2-regression,
and  python3.12 -B scratch-union.py --stage $STAGE --out /tmp/union.json

Candidate, both schemes (G2's shape: one stage per scheme, candidate documents at repo-relative
scratch paths as W41 G1 wrote them; the SHA12s are what the stage's rows name):
  SRC="--stage $LIGHT --stage $DARK \
       --candidate packages/calibration/results/<wave>/.../candidate/<light>.json=<sha12> \
       --candidate packages/calibration/results/<wave>/.../candidate/<light-receded>.json=<sha12> \
       --candidate .../<dark>.json=<sha12> --candidate .../<dark-receded>.json=<sha12>"
  python3.12 -B chroma-cut.py    $SRC --out OUT/chroma-cut.json
  python3.12 -B m2-rebaseline.py --cut OUT/chroma-cut.json --out OUT/m2-rebaseline.json
  python3.12 -B exterior-cut.py  $SRC --out OUT > OUT/exterior-cut.txt
  python3.12 -B l1-cut.py        $SRC --out OUT/l1-cut.json
  python3.12 -B black-cut.py     $SRC --captures $CANDIDATE_CAPTURES --captures $CAN \
                                 --out OUT/black-cut.json
  python3.12 -B e2-regression.py $SRC --captures $CANDIDATE_CAPTURES --captures $CAN \
                                 --out OUT/e2-regression.json --bins OUT/e2-regression-bins.json.gz
  python3.12 -B scratch-union.py $SRC --out /tmp/union.json
A candidate on one scheme only is one --stage with its two --candidate; the other scheme keeps
its current rows. Multi-stage without --candidate (two stages at the shipped documents) is base
mode. Declaring =SHA12 is optional, and recommended: it pins the bytes the rows were rendered
from, so a candidate edited after its render refuses at the argument rather than at the stage.

The test (test_admission.py -> admission-test.txt)
--------------------------------------------------
  OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3.12 -B test_admission.py \
      | tee admission-test.txt
Scratch under /tmp/w42-gate-admission/test; the candidate documents, which must be
repo-relative, are written to .admission-scratch/ here and removed on exit (never committed).
It builds four stages from the four standard macOS 27 profiles' non-holdout WebGPU rows
(holdout declared by key and never held, as a G2 stage will be): control-light/control-dark
naming the shipped documents with each row's raw bytes, and candidate-light/candidate-dark
naming candidates = the shipped bytes plus one "$comment-w42-g0-admission-test" key (asserted
equal to the shipped document once the key is dropped), each row's two document clauses
rewritten in its raw bytes; and a capture tree of the calibration/validation/probe cells whose
metadata names the candidates (PNGs copied, not linked: the readers refuse a payload resolving
outside its root). No canonical holdout or recorded pixel is opened.

What the candidate comparison maps back, and why each is a name or hash and not a reading: the
four candidate paths and 12-hex hashes -> the shipped ones; the candidate stage paths and their
matrix.json SHA-256 -> the control ones; the union's legacy-envelope digest (matrixSha256, a
hash over rows that name the documents); the output directory scratch-union prints. Set aside
with their shape asserted: e2's `captures` roots (candidate [CAN, scratch tree], control [CAN]);
e2's `capturePathsMoved`, which counts rows whose capturePath differs from the frozen pre-W38
baseline's (212 = every cell in candidate mode, 0 in control); exterior-cut's `documents` and
its section-0 list, one entry per document the rows name: the WebGPU rows name the candidates
while the CSS rows still name the shipped documents, so 4 names where the control has 2, the
same 2 once mapped, row counts summing per name.

Result (admission-test.txt; the working tree over ffd9567f, 2026-09-29): all checks pass,
75 ok and 0 FAIL, in about six minutes.
  GREEN base, current union        six scripts byte-identical to W41's port run from its own
                                   folder; chroma-cut.json except generatedAt.
  GREEN base, one stage            control-light (208 rows, 1x/2x light standard WebGPU, holdout
                                   declared and not held): seven scripts byte-identical to W41's,
                                   chroma's generatedAt and the output path scratch-union prints
                                   excepted.
  GREEN base, two stages           control-light + control-dark against the current union: the
                                   JSON differs only at $.source, $.matrixSha256 (the stages hold
                                   no holdout rows) and chroma's $.generatedAt.
  GREEN candidate                  four candidates (f80d5648bb68 / 351d28de9291 light, 00c3c909d380
                                   / edb839eefb99 dark; two declared repo-relative, two absolute,
                                   two with =SHA12): all seven equal to the control once mapped,
                                   every JSON stamped `admission` and atDocuments "candidate"
                                   where it has one, every stdout opening "# CANDIDATE"; the
                                   unions byte-equal after mapping; E2 212 cells, 7,728 bins
                                   within and 1,488 UNMEASURED on both sides, bins file equal.
  RED (x6 row readers each)        R1 a wrong =SHA12; R2 the candidate edited after the rows were
                                   written, declared by path (refused at the stage: "is not the
                                   declared candidate's bytes"); R3 the same, declared with its
                                   original =SHA12 (refused at the argument); R4 base mode on the
                                   candidate stages ("neither a shipped document ... nor a
                                   declared --candidate"); R5 a candidate under profiles/; R6 two
                                   stages replacing the same pair; R7 --candidate with no --stage;
                                   R8 a candidate no stage declares. Every one exits 1 with the
                                   mismatch named and writes nothing.
The W29 freeze reads 1,818 (freeze.py verify, run beside the test).
