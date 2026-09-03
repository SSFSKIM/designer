# W13 X6 — the band-windowed rows, and their baseline on the W12 close bed (2026-09-03)

`ssimBand` and `ssimInterior` are now on the perceptual axis of every cell the compare writes.
This is their baseline: what they read on the bed as W12 closed it, before the depth ramp or the
device-pixel widths move anything. No bound is adopted here — W13 G2 adopts one from these numbers
at the landing (contract X6).

Evidence beside this file: `matrix-x6-baseline.json` (the scratch matrix these tables are read
from), `x6-baseline.sh` (the twelve runs that produced it) and `x6-baseline.py` (the determinism
check and every table below).

## 1. Method

**One measurement, windowed three ways.** `ssimMean` has always been the mean of the SSIM map over
the whole crop. `ssimBand` and `ssimInterior` are that *same* map — the same 11×11 Gaussian window
at σ 1.5, the same K1 / K2 / L constants, on encoded luma — averaged over two sub-populations of
its windows. `measureCell` computes the map once and hands it to all three, so no row can differ
from another by anything but its window. Three separate SSIM calls over three crops would not have
been comparable: SSIM's window straddles whatever crop boundary you introduce.

**The split is a fixed 24 CSS px of depth from the contour**, converted to device px by the
fixture's backing scale (24 at 1x, 48 at 2x). Fixed rather than per span because the quantity it
separates is a fixed depth: the lens's displacement `D(u)` reaches zero by `u ≈ 20` on every span
(claims §5.49 §2), so 24 CSS px contains the whole of the band on every cell of the bed. A per-span
split would move with the lens depth and would hide a lens change inside a metric change, and a
fixed number is one a reader can check against a printed corner crop (W13 Decision Log 1,
question 3).

**The window is the NATIVE silhouette's distance transform.** The reference defines where the band
is. A web-derived window would move as the web side is tuned — the target moving when you tune
against it — and a web silhouette that broke into pieces (which happens on the CSS tier over a
high-contrast backdrop, where the extractor punches interior holes) would carry its own new
contours into the metric. The silhouette is hole-filled before its boundary is taken, for the same
reason `contourDistance` fills it: an extraction hole is not an outline, so it must not be a band.

**A window belongs to the class of its centre pixel.** Windows centred outside the silhouette are
in neither class, so the two rows partition the *surface*, not the crop, and do not average back to
`ssimMean`. §5 below is about exactly that gap.

**Absent is a measurement outcome, never zero.** A cell whose native silhouette is empty inside the
declared region gets neither row (there is no contour to measure depth from), and a surface whose
half-span is under the split is all band and gets no `ssimInterior`. On this bed that is
`rrect-sm` (half-span 16 pt), `capsule-button` (22 pt) and `toolbar-group` (a group of shallow
bodies) at both scales — the split is in CSS px, so a shape that is all band at 1x is all band at
2x as well. The window counts are recorded beside the means because every comparison made from
these rows weighs them: a mean without its support cannot be pooled across spans.

**Schema.** `RESULT_MATRIX_SCHEMA_VERSION` does not move. The rows are an addition that changes no
existing quantity, they are optional in the same "absent means not measured" sense the axes already
use, and no adopted bound reads them. Bumping would also have widened the deliberate gap between
this constant and the committed matrix's own version, which wave Decision Log 15 ruling 3 pins for
an unrelated reason.

## 2. The bed, and its determinism check

Twelve compare runs (six profiles × two renderers, `--set calibration,validation,holdout`) from the
`w13-x6-band-rows` worktree to a scratch matrix and scratch captures; the canonical
`results/matrix.json` and `web-captures/` were not touched. 230 cells, exactly the canonical bed's
230, no cell missing and none extra.

**20 873 metric values compared against the canonical matrix; 20 858 are bit-for-bit identical.**
The 15 that differ are all on one cell —
`apple-macos-26.5-1x-light-standard / light-solid__capsule-button__rest / css` — and the harness
itself says why: that capture came back with `deterministic: false, repeatNoise 1.17e-05`, where
the canonical row has `deterministic: true, repeatNoise 0`. The differences that follow are of that
size: `ssimMean` 0.986940890 → 0.986941303, `oklabDeltaEMean` 0.0029862603 → 0.0029862134, and the
largest of them, `shadow.centroidOffsetXWeb`, 1.0007506 → 1.0000000 (7.5e-4, a centroid quantised
by one raster row). Nothing in this measurement path changed on that cell, and no other cell moved
at all. Recorded rather than explained away: one 1x CSS light-solid capture on this machine is not
frame-stable to the last bit, and the harness's own repeat check is what caught it.

## 3. The checkerboard cells, light standard

`ssimOutside` is not a recorded row — it is derived here, as the mean over the windows the two rows
do *not* cover, from `ssimMean` and the two window counts. It is in the table because §5 needs it.
"band share of deficit" is `(1 − ssimBand)·bandPx` as a fraction of that plus
`(1 − ssimInterior)·interiorPx`, i.e. the share within the silhouette.

| cell | scale | tier | ssimMean | ssimBand | ssimInterior | band px | interior px | band share of deficit | ssimOutside | outside px |
|---|---|---|---|---|---|---|---|---|---|---|
| rrect-sm | 1x | texture | 0.9988 | 0.9673 | — | 2000 | — | 100.0% | 0.9999 | 56900 |
| rrect-sm | 1x | dom | 0.9853 | 0.6822 | — | 2000 | — | 100.0% | 0.9960 | 56900 |
| rrect-sm | 2x | texture | 0.9978 | 0.9417 | — | 7980 | — | 100.0% | 0.9997 | 237720 |
| rrect-sm | 2x | dom | 0.9883 | 0.7717 | — | 7980 | — | 100.0% | 0.9956 | 237720 |
| capsule-button | 1x | texture | 0.9852 | 0.8815 | — | 4872 | — | 100.0% | 0.9945 | 54028 |
| capsule-button | 1x | dom | 0.9612 | 0.6372 | — | 4872 | — | 100.0% | 0.9905 | 54028 |
| capsule-button | 2x | texture | 0.9836 | 0.8634 | — | 19462 | — | 100.0% | 0.9940 | 226238 |
| capsule-button | 2x | dom | 0.9705 | 0.7272 | — | 19462 | — | 100.0% | 0.9915 | 226238 |
| rrect-md | 1x | texture | 0.9695 | 0.9317 | 0.9817 | 9964 | 5060 | 88.0% | 0.9767 | 43876 |
| rrect-md | 1x | dom | 0.8963 | 0.6238 | 0.8230 | 9964 | 5060 | 80.7% | 0.9666 | 43876 |
| rrect-md | 2x | texture | 0.9517 | 0.9315 | 0.9594 | 39190 | 20868 | 76.0% | 0.9550 | 185642 |
| rrect-md | 2x | dom | 0.9169 | 0.7630 | 0.9482 | 39190 | 20868 | 89.6% | 0.9459 | 185642 |
| rrect-ml | 1x | texture | 0.9482 | 0.9370 | 0.9803 | 14476 | 13572 | 77.3% | 0.9394 | 30852 |
| rrect-ml | 1x | dom | 0.8481 | 0.6824 | 0.8597 | 14476 | 13572 | 70.7% | 0.9207 | 30852 |
| rrect-ml | 2x | texture | 0.9158 | 0.9396 | 0.9589 | 56891 | 55284 | 60.2% | 0.8878 | 133525 |
| rrect-ml | 2x | dom | 0.8765 | 0.8090 | 0.9583 | 56891 | 55284 | 82.5% | 0.8714 | 133525 |
| rrect-lg | 1x | texture | 0.9428 | 0.9395 | 0.9747 | 18560 | 25252 | 63.8% | 0.8935 | 15088 |
| rrect-lg | 1x | dom | 0.8372 | 0.7412 | 0.9013 | 18560 | 25252 | 65.8% | 0.8479 | 15088 |
| rrect-lg | 2x | texture | 0.9113 | 0.9380 | 0.9747 | 72924 | 102261 | 63.6% | 0.7917 | 70515 |
| rrect-lg | 2x | dom | 0.8696 | 0.8400 | 0.9709 | 72924 | 102261 | 79.6% | 0.7533 | 70515 |
| glass-over-glass | 1x | texture | 0.9521 | 0.9445 | 0.9842 | 14500 | 13600 | 79.0% | 0.9414 | 30800 |
| glass-over-glass | 1x | dom | 0.8499 | 0.7001 | 0.8423 | 14500 | 13600 | 67.0% | 0.9238 | 30800 |
| glass-over-glass | 2x | texture | 0.9211 | 0.9386 | 0.9746 | 56993 | 55404 | 71.3% | 0.8915 | 133303 |
| glass-over-glass | 2x | dom | 0.8687 | 0.8104 | 0.9120 | 56993 | 55404 | 68.9% | 0.8757 | 133303 |
| toolbar-group | 1x | texture | 0.9643 | 0.7227 | — | 4584 | — | 100.0% | 0.9846 | 54316 |
| toolbar-group | 1x | dom | 0.9576 | 0.6063 | — | 4584 | — | 100.0% | 0.9873 | 54316 |
| toolbar-group | 2x | texture | 0.9663 | 0.7432 | — | 18276 | — | 100.0% | 0.9843 | 227424 |
| toolbar-group | 2x | dom | 0.9656 | 0.6907 | — | 18276 | — | 100.0% | 0.9877 | 227424 |

The band px column also shows the split behaving: the same shape at 2x carries very nearly four
times the band pixels of 1x (`rrect-sm` 2000 → 7980, `capsule-button` 4872 → 19462), because the
band is the same CSS-px depth around the same CSS-px outline in a raster with twice the pitch.

## 4. `photo` and `hc-text` at `rrect-md`, light standard

| scene | scale | tier | ssimMean | ssimBand | ssimInterior | band px | interior px | band share | ssimOutside |
|---|---|---|---|---|---|---|---|---|---|
| photo__rrect-md | 1x | texture | 0.9975 | 0.9910 | 0.9958 | 9964 | 5060 | 81.0% | 0.9991 |
| photo__rrect-md | 1x | dom | 0.9628 | 0.9063 | 0.9966 | 9964 | 5060 | 98.2% | 0.9718 |
| photo__rrect-md | 2x | texture | 0.9981 | 0.9928 | 0.9973 | 39188 | 20868 | 83.2% | 0.9992 |
| photo__rrect-md | 2x | dom | 0.9740 | 0.9422 | 0.9968 | 39188 | 20868 | 97.1% | 0.9781 |
| hc-text__rrect-md | 1x | texture | 0.9760 | 0.8960 | 0.9673 | 9964 | 5060 | 86.2% | 0.9951 |
| hc-text__rrect-md | 1x | dom | 0.9029 | 0.6283 | 0.6866 | 9964 | 5060 | 70.0% | 0.9903 |
| hc-text__rrect-md | 2x | texture | 0.9648 | 0.9292 | 0.9694 | 39194 | 20868 | 81.3% | 0.9719 |
| hc-text__rrect-md | 2x | dom | 0.9391 | 0.8124 | 0.9336 | 39194 | 20868 | 84.1% | 0.9665 |

`photo__rrect-md` is the clearest demonstration of why the rows exist. On the GPU tier the cell
reads 0.9975 / 0.9981 whole-crop, which says "as good as identical", while its band reads 0.9910 /
0.9928 — a deficit an order of magnitude larger than the whole-crop figure suggests, sitting
exactly where the eye looks. On the CSS tier at 2x the interior is 0.9968 and the band 0.9422: the
single `blur()` matches the reference's deep body almost perfectly and misses the band entirely,
which is the CSS tier's known mechanism (one blur, no lens) stated as a number for the first time.

## 5. Where the whole-crop loss actually sits

Deficits are `(1 − ssim) × windows`, i.e. SSIM-points × pixels, on the four large checkerboard
cells at light standard. "band / silhouette" is the band's share within the surface — the number
X6 asked for — and "band / crop" is the same band against the whole crop's deficit including the
windows the two rows do not cover.

| scale | cell | tier | band | interior | outside | band / silhouette | band / crop |
|---|---|---|---|---|---|---|---|
| 1x | rrect-md | texture | 680 | 93 | 1021 | 88.0% | 37.9% |
| 1x | rrect-md | dom | 3749 | 895 | 1465 | 80.7% | 61.4% |
| 1x | rrect-ml | texture | 912 | 267 | 1869 | 77.3% | 29.9% |
| 1x | rrect-ml | dom | 4598 | 1904 | 2448 | 70.7% | 51.4% |
| 1x | rrect-lg | texture | 1124 | 638 | 1607 | 63.8% | 33.3% |
| 1x | rrect-lg | dom | 4803 | 2493 | 2295 | 65.8% | 50.1% |
| 1x | glass-over-glass | texture | 805 | 215 | 1804 | 79.0% | 28.5% |
| 1x | glass-over-glass | dom | 4348 | 2145 | 2348 | 67.0% | 49.2% |
| 2x | rrect-md | texture | 2685 | 848 | 8345 | 76.0% | 22.6% |
| 2x | rrect-md | dom | 9287 | 1080 | 10039 | 89.6% | 45.5% |
| 2x | rrect-ml | texture | 3435 | 2274 | 14981 | 60.2% | 16.6% |
| 2x | rrect-ml | dom | 10868 | 2308 | 17172 | 82.5% | 35.8% |
| 2x | rrect-lg | texture | 4524 | 2590 | 14685 | 63.6% | 20.8% |
| 2x | rrect-lg | dom | 11665 | 2980 | 17394 | 79.6% | 36.4% |
| 2x | glass-over-glass | texture | 3499 | 1410 | 14466 | 71.3% | 18.1% |
| 2x | glass-over-glass | dom | 10805 | 4878 | 16573 | 68.9% | 33.5% |

Three readings, and the third is a warning about how S4 must be written.

**Inside the surface, the band carries most of the loss, at every span and both scales** — 60–90%
of the silhouette's deficit over 24 CSS px of depth that is 20–50% of the surface's pixels. That is
the W13 premise as a measurement: a uniform sharp share leaves the band wrong, and the interior,
which the whole-crop mean is mostly made of, is the part that already agrees. It is strongest where
the wave says it should be: on the GPU tier at 1x `rrect-md` the band holds 88% of the loss, and
the band's share falls as the span grows (88 → 77 → 64% over md → ml → lg) simply because a larger
surface has more interior to dilute with.

**The band deficit grows with scale even where `ssimBand` barely moves.** `rrect-md` texture reads
0.9317 at 1x and 0.9315 at 2x — the same band quality — but the 2x band holds four times the
pixels, so the deficit it contributes quadruples (680 → 2685). Any stop written on the *mean* is
therefore scale-neutral by construction, which is the property S4 wants; a stop written on a pooled
deficit would not be.

**The rows do not see the outside of the contour, and on the large 2x cells that is where most of
the whole-crop deficit is.** `ssimOutside` on `checkerboard__rrect-lg` at 2x texture is 0.7917 over
70 515 windows — 14 685 points of deficit against the band's 4524 and the interior's 2590. Those
windows are the exterior half of the same band: the contour's outer edge, the rim's spill and the
outer shadow, all of which the eye reads as one edge with the inner band. X6 defines `ssimBand`
over the silhouette's pixels, and this baseline implements exactly that, so a landing that fixes
the inner band and disturbs the outer one would show as a rise in `ssimBand` and a fall in
`ssimMean`. **Recorded as a gap** (W13 Deferred): an outward companion row — the same map over the
band of exterior pixels within 24 CSS px of the contour — would close it, and until one exists, S4
must be read together with `ssimMean` rather than instead of it, and the X5 corner crops remain the
arbiter of the outer edge.

## 6. The whole bed: `ssimBand − ssimInterior` by backdrop class and tier

Negative means the band is the worse of the two windows. "band-only" counts cells where the surface
is shallower than the split, so no interior exists to difference against.

| backdrop | tier | cells with both rows | min | median | mean | max | band-only cells | cells with no rows |
|---|---|---|---|---|---|---|---|---|
| checkerboard | texture | 14 | −0.1868 | −0.0356 | −0.0339 | +0.0426 | 17 | 0 |
| checkerboard | dom | 14 | −0.2132 | −0.1365 | −0.1214 | +0.0070 | 17 | 0 |
| photo | texture | 20 | −0.2153 | −0.0072 | −0.0337 | −0.0019 | 22 | 0 |
| photo | dom | 20 | −0.2281 | −0.0824 | −0.0816 | +0.0024 | 22 | 0 |
| hc-text | texture | 2 | −0.0713 | −0.0557 | −0.0557 | −0.0402 | 6 | 0 |
| hc-text | dom | 2 | −0.1212 | −0.0897 | −0.0897 | −0.0583 | 6 | 0 |
| impulse | texture | 2 | −0.0053 | −0.0049 | −0.0049 | −0.0045 | 6 | 0 |
| impulse | dom | 2 | −0.1043 | −0.0850 | −0.0850 | −0.0657 | 6 | 0 |
| solid | texture | 6 | −0.0078 | −0.0048 | −0.0051 | −0.0027 | 20 | 0 |
| solid | dom | 6 | −0.0993 | −0.0411 | −0.0485 | −0.0240 | 20 | 0 |

Every cell in the bed carries the rows: no cell lost its native silhouette, and 142 of the 230 are
band-only, because most of the bed is built on `capsule-button` and `rrect-sm`.

The band is the worse window on 82 of the 88 cells that have both. All six exceptions are
`glass-over-glass`, five of them on a dark ground (the largest, +0.0426 and +0.0276, are the 1x and
2x dark texture cells) plus `photo__glass-over-glass` at 2x dom, +0.0024. That is the one composite
scene on the bed — glass over glass — where the "interior" of the outer surface contains the inner
surface's own contour, so the deep window is not a quiet interior at all. It is a property of the
scene rather than of the material, and it is worth knowing before S4 is written against
`glass-over-glass`.

The ordering by tier is the expected one and is now a number: the CSS tier's band–interior gap is
larger than the GPU tier's on every backdrop class — 1.6× on `hc-text`, 2.4× on `photo`, 3.6× on
`checkerboard`, and an order of magnitude on the solids (9.5×) and `impulse` (17×) — because one
`backdrop-filter` reproduces a deep body and cannot reproduce a lens.

`impulse` and `solid` on the GPU tier are the null case — band and interior within 0.008 of each
other — which is the right sanity check on the instrument: where there is no backdrop structure for
a lens to displace, the two windows agree.
