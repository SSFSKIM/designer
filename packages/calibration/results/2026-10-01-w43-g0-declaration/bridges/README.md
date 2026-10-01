# W43 G0 (e): the in-sitting bridge cells

Charter clause 3, Design "The bridges", X43. `declare-bridges.py` writes `bridge-cells.json`
(`check` re-derives it byte for byte). `sentinel-references.py` reads the sentinels' reference frames
from `w42-archive` (probe role, guarded Reader, the raw W42 roots denied) into
`sentinel-references.json`.

| sitting | W42 sentinels at 0.5, long protocol, 3 runs | canonical cells at 0.5, 3 runs | captures |
| --- | --- | --- | ---: |
| G1a | 2 cells x 8 endpoints, at the opening and the close (96) | 6 per pass x 4 passes, at the opening (72) | 168 |
| G1b | 2 cells x 4 endpoints (2x), at the opening and the close (48) | 6 per pass x 2 passes (2x), at the opening (36) | 84 |

Both totals are the charter's priced 168 and 84.

**The tints are refereed here, not pre-flighted.** The four tinted cells are read against W29
fixtures that the original harness tint-attested, which is stricter than the twin test. No W29-style
tint pre-flight runs: a check over 0.5 fixtures says nothing about 0.25 pixels (the parent's ruling).

**The canonical six.** In light: `dark-solid__capsule-button`, `photo__capsule-button` with the
orange tint, and `mid-chroma-solid__rrect-md`. In dark: `dark-solid__rrect-lg`,
`checkerboard__capsule-button` with the orange tint, and `hc-text__rrect-sm`. Each is declared in
both poses at both scales. They add what G0 (b)'s bridge did not cover: uniform backdrops on the
capsule and on the largest span, an author tint over photo and over a checker, the saturated solid,
and text on the smallest shape. None is a holdout or recorded scene. Their fixtures' SHA-256s are in
`bridge-cells.json`.

**The sentinels compare like protocol with like.** In the active pose, W42's long-protocol sentinel
rows and its normal-protocol bed rows of the same cell settle on different frames in five of the
eight active cell-endpoints (`sentinel-references.json`). A sitting's sentinels are therefore read
against the long-protocol rows only. In the receded pose the two protocols agree.

**The metric, run by run** (the coordinator's ruling): a cell agrees only when EVERY one of its runs
agrees with the reference, each run either pixel-identical to it or with every region statistic
within max(1 code, bar) of the reference's. The region statistics are W42's instrument, unchanged
(masks `n` and `w` active, `n` receded); the bar is W39's, and the sentinels take W42 G1's
long-protocol bar (a cell with no measured row reads at the 0.5 floor, one code). The plans carry
each cell's reference in G0 (d)'s `bridge` field (`../bed/sitting-g1a.json`, `sitting-g1b.json`).
The reader on existing evidence is `../bridge/bridge.py`. It compared each fixture with every
state the seven runs produced, so its verdicts already hold run by run.
