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

**The metric.** A cell agrees when one of its runs is pixel-identical to the reference frame.
Otherwise it agrees when every region statistic of its plurality frame lies within max(1 code, bar)
of the reference's. The region statistics are W42's instrument, unchanged; the bar is W39's. The
reader on existing evidence is `../bridge/bridge.py`.
