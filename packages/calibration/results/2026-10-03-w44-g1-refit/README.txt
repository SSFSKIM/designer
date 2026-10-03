W44 G1 — the refit of the light -glass0.25 2x texture, read and closed at the finding (claims §5.203)
==========================================================================================

Branch w44-g1-refit off 08994111 (the charter v1.3 merge). The parent ruled on 2026-10-03, option
(a): G1 closes at the finding under Decision Log 4's "Otherwise". Nothing was sealed, shipped,
staged or published; no holdout or referee cell was rendered or read.

Layout
------
cuts/        G0's cuts copied and extended: t1.py (the text stratum T, T1-fine / T1-low as its
             outputs, the moves' clauses), readings.py (T1-low), test_t1.py (29 pass), bed.py (reads
             G0's referees, bar and port in place), cuts.py (one reference, the published c05
             generation, X52). Part 2's amendment pins t1.py, readings.py and test_t1.py.
references/  every cut on c05 against itself (the step 1 rehearsal).
fit/         the measuring loop (fit.py), the declared search (search.py), the joint reading
             (joint.py), the finding (finding.py), the recovered objectives (recover.py), the
             builder and its red cases (pinned by the amendment); every candidate under
             candidates/<label>/ with its spec, documents, identity check, cuts and summary; the
             decisions and readings under path/ (move1..3.json, joint.*, finding.*, rungs.txt,
             recovered.json, move1-recovered.json, x48-joint.txt); every launch in runs.jsonl and
             logs/. The joint point m3-t0.1 also carries its scratch renders under
             candidates/m3-t0.1/scratch/ (matrices gzipped, captures as written; manifest.json):
             the next wave's rehearsal material.

Prepared for steps 3-8 and NOT RUN
----------------------------------
The wave closed at the finding before step 3, so none of these was ever executed. None of them
touched a profile document, the runtime module, a stage or a capture tree (`git diff 08994111 --
packages/calibration/profiles packages/platform-web` is empty; no stage was declared). They are
committed as the next wave's to reuse, and are untested:

  seal/seal.ts       step 3: freeze a landed candidate as the two LIGHT -glass0.25 documents, the
                     dark two untouched; refuses unless each file it replaces is the published c05
                     document; the receded document may name sizeHeavySecondShare (Decision Log 7).
  stage/stage.py     steps 5 and 7: declare and read the light publication stage in strict mode; the
                     probe pass through the planner's pre-gate list, the exposure through its
                     exposure list after the holdout ledger's committed record.
  stage/x48.py       step 5: the stage's 1x light rows and captures against the published c05
                     generation, byte for byte (X48).
  sheets/sheets.py   steps 6 and 8: native | c05 | candidate | difference eye sheets.
