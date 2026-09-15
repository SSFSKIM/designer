# The 26.5 freeze (W29 clause 1, X1) — written 2026-09-16 on macOS 26.5.2, before the update

`sha256.txt` is one line per byte-unit of 26.5 evidence: 619 fixture PNGs across the six
`apple-macos-26.5-*` directories, the 32 backgrounds, `fixtures/manifest.json`, the three 26.5
profile documents, and one canonical hash per 26.5-keyed row of `results/matrix.json` (1,107 rows).
`python3 freeze.py verify` re-derives and diffs it; it is run at every W29 merge and at close.
The list was written and verified on the same machine minutes apart, before macOS 27 was installed,
so it is the last 26.5 state a 26.5 machine ever attested.
