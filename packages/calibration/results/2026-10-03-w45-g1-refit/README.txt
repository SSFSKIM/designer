W45 G1 (claims §5.206; charter 2026-10-03-w45-span-selective-texture.md v1.4, G1 child; branch
w45-g1-refit). What is here, by step.

amendment/   Step 0, part 2's second and final amendment (Decision Log 7): the side branch's tests at
             the merge 6321b965 (39 fit, 26 declare), and after the amendment (43 fit, 38 declare,
             8 seal, 15 builder), check and check-fit consistent, a third amend-fit refused, part 2's
             diff. The record itself is G0's fit-amendments.json (amendment 2) and the third line of
             fit-declaration.sha256 (e6874e02...).
references/  Step 1: c05 cut against itself with W45's cuts; README.txt says what it fixes.
fit/         Step 2, the fit, in scratch, under part 2 e6874e02:
  specs/, candidates/<label>/   every point's spec, four endpoint documents, candidate.json, identity
                                check, and (for a rendered point) cuts.json.gz, cuts.txt, summary.json;
                                a point measured by a content twin (aliases.json) has no cuts of its own
  runs.jsonl, logs/             every build and launch (211 launches, 207 exit 0, 4 partial: the
                                lc16 shape axis), each launch's compare log, each search attempt's log
  path/<lineage>/stage{1,2}.json the decisions search.py wrote; rungs.txt/.json every rung's objective
                                (rungs.py); recovered.json (recover.py); joint.json/.txt (joint.py);
                                finding.json/.txt (finding.py, the selected point) and
                                finding-joint-path.*; x48-c05-path.json, x48-joint-path.json
  search_g1.py                  the ONE correction beside the pinned search: a receded leaf's label
                                mark `rc`, not `R` (the builder's [a-z0-9.-]); stage 2 ran through it
  specs-refused/                the spec the builder refused for that label, kept
  chain.sh, chain2.sh           the drivers that ran the stages in order, resuming after recover.py
sheets/sent.txt  the finding's eye sheets (both final points, 94 cells each), sent to the MacBook.
t1/bands.py      G2 part (i)'s reader, prepared and rehearsed on c05 (rehearsal-c05.txt: 8 of 8 equal
                 to W44 G2's fixture); not run on a candidate (no stage exists).
gate/report.py   the gate report's layout over a stage cut, prepared and read on c05 only.

Scratch on the capture machine: ~/vitrea-w45/g1-scratch/fit/<label>/<scope>/ (matrices, captures),
~/vitrea-w45/g1-scratch/sheets/. G0's census log (results/2026-10-03-w45-g0-operator/census.jsonl)
is append-only and shared by the wave's launches: lines 1-103 are G0's, every line after is G1's.

Steps 3-6, run on the parent's ruling of 2026-10-04 as evidence for the user's decision (claims §5.206 §13):
seal/        the seal's method record, its manifest, and the digests after the freeze (exactly the two
             light 0.25 documents moved).
runtime/     the runtime first: the export, coherence and selection suites and the 34 goldens after the
             0.25 module was regenerated.
stage/       the light stage's launches (stage.py measure, both tiers, the referees and the holdout not
             staged) and X48 on it. The stage is ~/vitrea-w45/g1-stage-light/ (matrix.json, membership.json);
             its captures are this worktree's packages/calibration/web-captures/ (gitignored), which G2
             copies to the canonical path.
cuts/        cut-025-w45.json (and .txt): W45's cuts on the stage with the dark c05 rows, against c05.
gate/        the gate report (report.py), the referee-absence check, the owner test's adapters on the
             scratch union (union.py, owner.py, owner/), tier-coherence.
t1/          t-bands-ebc3d9105a4a.gate.json, the candidate's T-band fixture at the gate (G2 part (i)).
sheets/      sent-gate.txt: the stage's sheets over every T1 cell, sent to the MacBook.
