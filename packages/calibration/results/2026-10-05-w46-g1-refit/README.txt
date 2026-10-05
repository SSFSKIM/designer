W46 G1 (claims §5.209; charter 2026-10-05-w46-dark-texture-at-0-25.md v1.4, Decision Logs 8 and 9;
branch w46-g1-refit). What is here, by step.

diagnosis/   Step 0 (Decision Log 8 item 1): impulse__capsule-button__inactive at receded tintAlpha 0.89,
             0.8 and 0.7, both dark profiles, attributed per pixel (render.sh, mask.ts, attribute.py;
             attribution.json/.txt). The rise is the transmission of the scattered impulse dot over the
             cell's 16 / 64 px L1 mask, not a stand-down. Decision Log 9 rules on it.
census-gate.py, with-gpu.sh, census.jsonl   G1's census log (G0's gate and lock, run unchanged).
amendment/   Part 2's one amendment (Decision Log 9, ac642fea): check, check-fit, a further amend refused.
             The record itself is G0's fit-amendments.json and the second line of fit-declaration.sha256.
references/  Step 1: d0219cd684bf (with ebc3d9105a4a) cut by W46's cuts; identical to G0's rehearsal cut.
fit/         Step 2, the fit under part 2 ac642fea (G0's fit.py / search.py / joint.py, pinned):
  specs/, candidates/<label>/   every point's spec, endpoints, candidate.json and identity, and each scale
                                twin's scale-<s>x.json and cuts-<s>x.json.gz. A point's composed summary.json
                                is committed only for the decisive points (the stages' landed points, the
                                branches', A and B): every other is recomposed by fit.compose from the
                                committed scale readings (about 1,340 summaries, 360 MB, are left on the
                                machine).
  runs.jsonl, logs/             every build and launch; logs/*.census-refused-*.txt the launches the census
                                refused while another session drove Chrome (kept; runs.jsonl exit 3).
  path/d0219/stage{1,2}.json    the decisions; stage2.json carries the two-point protocol's three branches
                                and points A and B; joint.json/.txt both joint points.
  drive.py, chain-gate.sh       the drivers (a pinned command rerun across census refusals; the chain to
                                the gate). search-logs/ their output.
stage/       X60 by render: the light strict-mode stage's 138 non-withheld scenes per scale, both tiers
             (x60-light.py, x60-light-cells.json, x60-light/), IDENTICAL (x60-render.json).
gate/        Step 5, the freeze-free gate (Decision Log 9): gate.py renders a point's 104 non-withheld dark
             scenes per scale on both tiers, and the light profiles' 138, in candidate mode, and cuts them
             against d0219cd684bf; <label>/cut.json.gz and cut.txt per point (start-d0219: the candidate-mode
             control, identical to the published rows and captures on both tiers); report.py lays out the
             gate report (gate-report.json/.txt, points A and B); stage1-budget-reading.txt reads the landing
             budget over every stage-1 point's rest cells.

Scratch on the capture machine: ~/vitrea-w46/g1-scratch/{diagnosis,fit,gate,sheets}/, the X60 stage
~/vitrea-w46/g1-stage-x60-light/. Nothing is sealed, staged in strict mode on dark bytes, exposed or
published: the freeze waits for the parent's naming of the point (Decision Log 9).
