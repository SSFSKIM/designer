W43 G3 (iii), charter clause 14 (§5.201): eye sheets over the whole canonical glass 0.25 bed.

sheets.py draws every cell the four -glass0.25 standard profiles declare (every role, holdout
included, both poses, both tiers) from the PUBLISHED generation files and the CANONICAL capture
tree. Each row: Apple 0.25 fixture | vitrea 0.25 | Apple 0.5 fixture | vitrea 0.5 | the two
differences x4, labelled with role, pose and both renders' L1 level error. It reuses G3 (i)'s
strata, crop and reader (../../2026-10-02-w43-g3-refit/sheets/sheets.py, imported, unmodified) and
admits the 0.25 rows through that wave's cuts/bed.py in sealed mode. The brief named the 0.5
render without its fixture; the 0.5 fixture was added beside it so Apple's two positions are both
on the page, not only inside a difference image.

Re-run, from this directory (reads only; needs the canonical capture tree on disk, which lives in
the main checkout, not in a worktree):

    python3.12 -B sheets.py --out ~/vitrea-w43/g3l-scratch/sheets
    cd ~/vitrea-w43/g3l-scratch/sheets && zip -X -q -r ../w43-g3-landing-sheets.zip .

Options: --captures TREE (default: the main checkout's packages/calibration/web-captures, found
through git's common dir), --tier webgpu,css, --rows 30 (page part size). It refuses, before any
capture pixel is read, if a declared cell has no published 0.25 row, if a published row's file
differs from index.json, or if a capture's cell__<tier>.json does not name its row's capturePath,
sceneId and renderer.

Per-capture capturePath check at the run recorded in sent.txt: 1,842 captures checked (1,124 at
0.25, i.e. every published 0.25 row; 718 at 0.5, every current 0.5 standard row the 0.25 bed
shares), all matched, 0 mismatches; the whole web key was equal on all 1,842. 406 cells have no
current 0.5 row. The run writes the same figures to checks.json beside the pages.
