# W13 X6 — the band-windowed rows, and their baseline on the W12 close bed (2026-09-03)

`ssimBand`, `ssimInterior` and `ssimOutside` are now on the perceptual axis of every cell the
compare writes. This is their baseline: what they read on the bed as W12 closed it, before the
depth ramp or the device-pixel widths move anything. No bound is adopted here — W13 G2 adopts one
from these numbers at the landing (contract X6).

Evidence beside this file: `matrix-x6-baseline.json` (the scratch matrix these tables are read
from), `x6-baseline.sh` (the twelve runs that produced it) and `x6-baseline.py` (the determinism
check and every table below).

## 1. Method

**One measurement, windowed four ways.** `ssimMean` has always been the mean of the SSIM map over
the whole crop. The three new rows are that *same* map — the same 11×11 Gaussian window at σ 1.5,
the same K1 / K2 / L constants, on encoded luma — averaged over three sub-populations of its
windows, by the class of each window's centre pixel:

- `ssimBand` — inside the reference silhouette, within the split of its contour;
- `ssimInterior` — inside the silhouette, deeper than the split;
- `ssimOutside` — outside the silhouette, within the split of its contour.

Those three plus the **far field** — outside and farther than the split, which no row carries —
partition the crop exactly. So `ssimMean` is their window-count-weighted mean *including* the far
field, and never the mean of the three rows alone. The far field stays uncounted on purpose: it is
backdrop that neither side's material touches, it is most of the crop on every small span, and
averaging it in is precisely what makes `ssimMean` blind to the material. `measureCell` computes
the map once and hands it to all four figures, so no row can differ from another by anything but
its window. Three separate SSIM calls over three crops would not have been comparable: SSIM's
window straddles whatever crop boundary you introduce.

**The split is a fixed 24 CSS px of depth from the contour**, converted to device px by the
fixture's backing scale (24 at 1x, 48 at 2x), and it is the same constant on both sides. Fixed
rather than per span because the quantity it separates is a fixed depth: the lens's displacement
`D(u)` reaches zero by `u ≈ 20` on every span (claims §5.49 §2), so 24 CSS px contains the whole of
the band on every cell of the bed. A per-span split would move with the lens depth and would hide a
lens change inside a metric change, and a fixed number is one a reader can check against a printed
corner crop (W13 Decision Log 1, question 3).

**Why an outward row.** The eye reads one edge, not two. The band a viewer sees straddles the
contour: the rim's spill, the lens's outermost displacement and the outer shadow are all on the
exterior side. §5 shows that on the large 2x cells the exterior half carries *more* of the
whole-crop deficit than the interior half does, so a `ssimBand` that rose while the exterior fell
would otherwise have read as an improvement.

**The window is the NATIVE silhouette's distance transform.** The reference defines where the band
is. A web-derived window would move as the web side is tuned — the target moving when you tune
against it — and a web silhouette that broke into pieces (which happens on the CSS tier over a
high-contrast backdrop, where the extractor punches interior holes) would carry its own new
contours into the metric. The silhouette is hole-filled before its boundary is taken, for the same
reason `contourDistance` fills it: an extraction hole is not an outline, so it must not be a band.
The outward distance is the same transform read on the other side of the same boundary, so the two
halves of the band are symmetric by construction.

**Absent is a measurement outcome, never zero.** A cell whose native silhouette is empty inside the
declared region gets no rows at all (there is no contour to measure depth from), and a surface
whose half-span is under the split gets no `ssimInterior`. On this bed that is `rrect-sm`
(half-span 16 pt), `capsule-button` (22 pt) and `toolbar-group` (a group of shallow bodies) at both
scales — the split is in CSS px, so a shape that is all band at 1x is all band at 2x as well. The
window counts are recorded beside the means because every comparison made from these rows weighs
them: a mean without its support cannot be pooled across spans.

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

**20 873 metric values compared against the canonical matrix; 20 845 are bit-for-bit identical.**
The 28 that differ sit on two cells, both 1x light-standard CSS captures, and the harness itself
says why: each came back `deterministic: false` — `light-solid__capsule-button__rest` with
`repeatNoise` 1.17e-05 and `photo__capsule-button__rest-tint-orange-half` with 3.91e-06 — where the
canonical rows have `true` and 0. The differences are of that size: `ssimMean` 0.986940890 →
0.986941303 and 0.977242875 → 0.977242879, and the largest of all, `shadow.centroidOffsetXWeb`,
1.0007506 → 1.0000000 (7.5e-4, a centroid quantised by one raster row). An earlier run of the same
script flagged only the first of the two cells, so the noise moves between cells from run to run.
Recorded rather than explained away: 1x CSS captures on this machine are not frame-stable to the
last bit, and the harness's own repeat check is what catches it. The other 228 cells reproduce
exactly, which is what the measurement path had to show.

## 3. The checkerboard cells, light standard

"band share of silhouette deficit" is `(1 − ssimBand)·bandPx` as a fraction of that plus
`(1 − ssimInterior)·interiorPx` — the share *within* the surface, which is what stop S4 is written
against. "outside share of crop deficit" is `(1 − ssimOutside)·outsidePx` as a fraction of all four
regions' deficits, including the far field.

| cell | scale | tier | ssimMean | ssimBand | ssimInterior | ssimOutside | band px | interior px | outside px | band share of silhouette deficit | outside share of crop deficit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rrect-sm | 1x | texture | 0.9988 | 0.9673 | — | 0.9989 | 2000 | — | 6032 | 100.0% | 9.0% |
| rrect-sm | 1x | dom | 0.9853 | 0.6822 | — | 0.9626 | 2000 | — | 6032 | 100.0% | 26.2% |
| rrect-sm | 2x | texture | 0.9978 | 0.9417 | — | 0.9971 | 7980 | — | 24248 | 100.0% | 12.7% |
| rrect-sm | 2x | dom | 0.9883 | 0.7717 | — | 0.9575 | 7980 | — | 24248 | 100.0% | 36.0% |
| capsule-button | 1x | texture | 0.9852 | 0.8815 | — | 0.9663 | 4872 | — | 8704 | 100.0% | 33.6% |
| capsule-button | 1x | dom | 0.9612 | 0.6372 | — | 0.9410 | 4872 | — | 8704 | 100.0% | 22.5% |
| capsule-button | 2x | texture | 0.9836 | 0.8634 | — | 0.9614 | 19462 | — | 34978 | 100.0% | 33.5% |
| capsule-button | 2x | dom | 0.9705 | 0.7272 | — | 0.9453 | 19462 | — | 34978 | 100.0% | 26.4% |
| rrect-md | 1x | texture | 0.9695 | 0.9317 | 0.9817 | 0.9320 | 9964 | 5060 | 13204 | 88.0% | 50.0% |
| rrect-md | 1x | dom | 0.8963 | 0.6238 | 0.8230 | 0.8984 | 9964 | 5060 | 13204 | 80.7% | 22.0% |
| rrect-md | 2x | texture | 0.9517 | 0.9315 | 0.9594 | 0.8584 | 39190 | 20868 | 52946 | 76.0% | 63.1% |
| rrect-md | 2x | dom | 0.9169 | 0.7630 | 0.9482 | 0.8266 | 39190 | 20868 | 52946 | 89.6% | 45.0% |
| rrect-ml | 1x | texture | 0.9482 | 0.9370 | 0.9803 | 0.9085 | 14476 | 13572 | 17508 | 77.3% | 52.6% |
| rrect-ml | 1x | dom | 0.8481 | 0.6824 | 0.8597 | 0.8755 | 14476 | 13572 | 17508 | 70.7% | 24.4% |
| rrect-ml | 2x | texture | 0.9158 | 0.9396 | 0.9589 | 0.8132 | 56891 | 55284 | 70219 | 60.2% | 63.4% |
| rrect-ml | 2x | dom | 0.8765 | 0.8090 | 0.9583 | 0.7821 | 56891 | 55284 | 70219 | 82.5% | 50.4% |
| rrect-lg | 1x | texture | 0.9428 | 0.9395 | 0.9747 | 0.8906 | 18560 | 25252 | 14512 | 63.8% | 47.1% |
| rrect-lg | 1x | dom | 0.8372 | 0.7412 | 0.9013 | 0.8432 | 18560 | 25252 | 14512 | 65.8% | 23.7% |
| rrect-lg | 2x | texture | 0.9113 | 0.9380 | 0.9747 | 0.7832 | 72924 | 102261 | 66543 | 63.6% | 66.2% |
| rrect-lg | 2x | dom | 0.8696 | 0.8400 | 0.9709 | 0.7425 | 72924 | 102261 | 66543 | 79.6% | 53.5% |
| glass-over-glass | 1x | texture | 0.9521 | 0.9445 | 0.9842 | 0.9133 | 14500 | 13600 | 17528 | 79.0% | 53.8% |
| glass-over-glass | 1x | dom | 0.8499 | 0.7001 | 0.8423 | 0.8824 | 14500 | 13600 | 17528 | 67.0% | 23.3% |
| glass-over-glass | 2x | texture | 0.9211 | 0.9386 | 0.9746 | 0.8231 | 56993 | 55404 | 70308 | 71.3% | 64.2% |
| glass-over-glass | 2x | dom | 0.8687 | 0.8104 | 0.9120 | 0.7932 | 56993 | 55404 | 70308 | 68.9% | 45.1% |
| toolbar-group | 1x | texture | 0.9643 | 0.7227 | — | 0.9281 | 4584 | — | 11576 | 100.0% | 39.5% |
| toolbar-group | 1x | dom | 0.9576 | 0.6063 | — | 0.9406 | 4584 | — | 11576 | 100.0% | 27.6% |
| toolbar-group | 2x | texture | 0.9663 | 0.7432 | — | 0.9237 | 18276 | — | 46632 | 100.0% | 43.0% |
| toolbar-group | 2x | dom | 0.9656 | 0.6907 | — | 0.9404 | 18276 | — | 46632 | 100.0% | 32.9% |

The pixel counts show the split behaving: the same shape at 2x carries very nearly four times the
band pixels of 1x (`rrect-sm` 2000 → 7980, `capsule-button` 4872 → 19462), because the band is the
same CSS-px depth around the same CSS-px outline in a raster with twice the pitch.

## 4. `photo` and `hc-text` at `rrect-md`, light standard

| scene | scale | tier | ssimMean | ssimBand | ssimInterior | ssimOutside | band share of silhouette deficit | outside share of crop deficit |
|---|---|---|---|---|---|---|---|---|
| photo rrect-md | 1x | texture | 0.9975 | 0.9910 | 0.9958 | 0.9977 | 81.0% | 20.8% |
| photo rrect-md | 1x | dom | 0.9628 | 0.9063 | 0.9966 | 0.9067 | 98.2% | 56.3% |
| photo rrect-md | 2x | texture | 0.9981 | 0.9928 | 0.9973 | 0.9978 | 83.2% | 24.6% |
| photo rrect-md | 2x | dom | 0.9740 | 0.9422 | 0.9968 | 0.9237 | 97.1% | 63.2% |
| hc-text rrect-md | 1x | texture | 0.9760 | 0.8960 | 0.9673 | 0.9847 | 86.2% | 14.2% |
| hc-text rrect-md | 1x | dom | 0.9029 | 0.6283 | 0.6866 | 0.9686 | 70.0% | 7.3% |
| hc-text rrect-md | 2x | texture | 0.9648 | 0.9292 | 0.9694 | 0.9095 | 81.3% | 55.5% |
| hc-text rrect-md | 2x | dom | 0.9391 | 0.8124 | 0.9336 | 0.8905 | 84.1% | 38.7% |

`photo__rrect-md` is the clearest demonstration of why the rows exist. On the GPU tier the cell
reads 0.9975 / 0.9981 whole-crop, which says "as good as identical", while its band reads 0.9910 /
0.9928 — a deficit an order of magnitude larger than the whole-crop figure suggests, sitting
exactly where the eye looks. On the CSS tier at 2x the interior is 0.9968 and the band 0.9422: the
single `blur()` matches the reference's deep body almost perfectly and misses the band entirely,
which is the CSS tier's known mechanism (one blur, no lens) stated as a number for the first time.

## 5. The four-way split: where the whole-crop loss actually sits

Deficits are `(1 − ssim) × windows`, i.e. SSIM-points × pixels, at light standard. The four columns
sum to the whole crop's deficit, so the percentages sum to 100.

| cell | scale | tier | band | interior | outside | far field | band % | interior % | outside % | far % |
|---|---|---|---|---|---|---|---|---|---|---|
| rrect-sm | 1x | texture | 65 | 0 | 7 | 1 | 89.1% | 0.0% | 9.0% | 1.9% |
| rrect-sm | 1x | dom | 636 | 0 | 226 | 2 | 73.6% | 0.0% | 26.2% | 0.2% |
| rrect-sm | 2x | texture | 465 | 0 | 69 | 13 | 84.9% | 0.0% | 12.7% | 2.4% |
| rrect-sm | 2x | dom | 1822 | 0 | 1029 | 12 | 63.6% | 0.0% | 36.0% | 0.4% |
| capsule-button | 1x | texture | 577 | 0 | 293 | 2 | 66.2% | 0.0% | 33.6% | 0.2% |
| capsule-button | 1x | dom | 1768 | 0 | 513 | 2 | 77.4% | 0.0% | 22.5% | 0.1% |
| capsule-button | 2x | texture | 2659 | 0 | 1351 | 17 | 66.0% | 0.0% | 33.5% | 0.4% |
| capsule-button | 2x | dom | 5309 | 0 | 1913 | 16 | 73.3% | 0.0% | 26.4% | 0.2% |
| rrect-md | 1x | texture | 680 | 93 | 898 | 123 | 37.9% | 5.2% | 50.0% | 6.9% |
| rrect-md | 1x | dom | 3749 | 895 | 1341 | 124 | 61.4% | 14.7% | 22.0% | 2.0% |
| rrect-md | 2x | texture | 2685 | 848 | 7497 | 848 | 22.6% | 7.1% | 63.1% | 7.1% |
| rrect-md | 2x | dom | 9287 | 1080 | 9183 | 856 | 45.5% | 5.3% | 45.0% | 4.2% |
| rrect-ml | 1x | texture | 912 | 267 | 1603 | 267 | 29.9% | 8.8% | 52.6% | 8.7% |
| rrect-ml | 1x | dom | 4598 | 1904 | 2180 | 268 | 51.4% | 21.3% | 24.4% | 3.0% |
| rrect-ml | 2x | texture | 3435 | 2274 | 13114 | 1867 | 16.6% | 11.0% | 63.4% | 9.0% |
| rrect-ml | 2x | dom | 10868 | 2308 | 15302 | 1870 | 35.8% | 7.6% | 50.4% | 6.2% |
| rrect-lg | 1x | texture | 1124 | 638 | 1588 | 19 | 33.3% | 18.9% | 47.1% | 0.6% |
| rrect-lg | 1x | dom | 4803 | 2493 | 2276 | 19 | 50.1% | 26.0% | 23.7% | 0.2% |
| rrect-lg | 2x | texture | 4524 | 2590 | 14428 | 257 | 20.8% | 11.9% | 66.2% | 1.2% |
| rrect-lg | 2x | dom | 11665 | 2980 | 17137 | 257 | 36.4% | 9.3% | 53.5% | 0.8% |
| glass-over-glass | 1x | texture | 805 | 215 | 1519 | 285 | 28.5% | 7.6% | 53.8% | 10.1% |
| glass-over-glass | 1x | dom | 4348 | 2145 | 2062 | 286 | 49.2% | 24.3% | 23.3% | 3.2% |
| glass-over-glass | 2x | texture | 3499 | 1410 | 12440 | 2026 | 18.1% | 7.3% | 64.2% | 10.5% |
| glass-over-glass | 2x | dom | 10805 | 4878 | 14542 | 2031 | 33.5% | 15.1% | 45.1% | 6.3% |
| toolbar-group | 1x | texture | 1271 | 0 | 832 | 2 | 60.4% | 0.0% | 39.5% | 0.1% |
| toolbar-group | 1x | dom | 1805 | 0 | 688 | 3 | 72.3% | 0.0% | 27.6% | 0.1% |
| toolbar-group | 2x | texture | 4694 | 0 | 3560 | 21 | 56.7% | 0.0% | 43.0% | 0.2% |
| toolbar-group | 2x | dom | 5653 | 0 | 2778 | 21 | 66.9% | 0.0% | 32.9% | 0.2% |
| photo rrect-md | 1x | texture | 90 | 21 | 31 | 7 | 60.4% | 14.2% | 20.8% | 4.7% |
| photo rrect-md | 1x | dom | 933 | 17 | 1232 | 7 | 42.6% | 0.8% | 56.3% | 0.3% |
| photo rrect-md | 2x | texture | 281 | 57 | 118 | 23 | 58.7% | 11.9% | 24.6% | 4.8% |
| photo rrect-md | 2x | dom | 2264 | 67 | 4040 | 23 | 35.4% | 1.0% | 63.2% | 0.4% |
| hc-text rrect-md | 1x | texture | 1036 | 165 | 202 | 12 | 73.2% | 11.7% | 14.2% | 0.8% |
| hc-text rrect-md | 1x | dom | 3704 | 1586 | 415 | 12 | 64.8% | 27.7% | 7.3% | 0.2% |
| hc-text rrect-md | 2x | texture | 2775 | 639 | 4794 | 430 | 32.1% | 7.4% | 55.5% | 5.0% |
| hc-text rrect-md | 2x | dom | 7352 | 1386 | 5798 | 430 | 49.1% | 9.3% | 38.7% | 2.9% |

Four readings.

**The two halves of the band together carry 72–99% of the whole crop's deficit on every cell in
this table.** On the GPU tier the band and outside sum to 88% (`rrect-md` 1x), 83% (`rrect-ml` 1x),
80% (`rrect-lg` 1x) and 80–87% at 2x; the far field never exceeds 10.5% anywhere, and the deep
interior — which is most of the surface's pixels on the large spans — never exceeds 19% on the GPU
tier and 28% on the CSS tier. Whatever else `ssimMean` is measuring, it is measuring the edge,
badly diluted.

**Inside the surface, the band carries most of the loss, at every span and both scales** — 60–90%
of the silhouette's deficit over 24 CSS px of depth that is 20–50% of the surface's pixels, and its
share falls with the span (88 → 77 → 64% over md → ml → lg at 1x on the GPU tier) simply because a
larger surface has more interior to dilute with. That is the W13 premise as a measurement: a
uniform sharp share leaves the band wrong, and the interior, which the whole-crop mean is mostly
made of, is the part that already agrees.

**At 2x the exterior half dominates.** On the GPU tier, `outside` goes from 47–54% of the crop's
deficit at 1x to 63–66% at 2x on the four large cells, while the band's own share falls to 17–23%.
`ssimOutside` itself falls from 0.89–0.93 at 1x to 0.78–0.86 at 2x on those cells, while the deep
interior's share of the deficit stays in single figures to low teens. So the 2x deficit is not mainly a body problem at all: it is the
contour's outer neighbourhood — rim spill, the lens's outermost displacement and the shadow —
resolved at twice the pitch. W13 G2 must watch `ssimOutside` at 2x as closely as `ssimBand`; a ramp
that fixed only the inner band would move less than a quarter of what 2x is losing.

**The band mean is scale-neutral where a pooled deficit is not.** `rrect-md` on the GPU tier reads
`ssimBand` 0.9317 at 1x and 0.9315 at 2x — the same band quality — while the deficit that band
contributes quadruples with its pixel count (680 → 2685). A stop written on the *mean*, as S4 is,
is therefore scale-neutral by construction; one written on a pooled deficit would not be.

## 6. The whole bed

### `ssimBand − ssimInterior` by backdrop class and tier

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

Every cell in the bed carries `ssimBand` and `ssimOutside`: no cell lost its native silhouette. 142
of the 230 are band-only, because most of the bed is built on `capsule-button` and `rrect-sm`.

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

### `ssimOutside − ssimBand` by backdrop class and tier: the two halves of one edge

| backdrop | tier | n | min | median | mean | max |
|---|---|---|---|---|---|---|
| checkerboard | texture | 31 | −0.1548 | +0.0367 | +0.0538 | +0.3431 |
| checkerboard | dom | 31 | −0.0976 | +0.1231 | +0.1403 | +0.4585 |
| photo | texture | 42 | −0.0760 | +0.0071 | +0.0187 | +0.1895 |
| photo | dom | 42 | −0.1455 | +0.0021 | +0.0065 | +0.1288 |
| hc-text | texture | 8 | −0.0197 | +0.0647 | +0.0783 | +0.2396 |
| hc-text | dom | 8 | +0.0312 | +0.1704 | +0.1836 | +0.3418 |
| impulse | texture | 8 | −0.0075 | +0.2077 | +0.2616 | +0.6369 |
| impulse | dom | 8 | −0.0184 | +0.2538 | +0.2906 | +0.6762 |
| solid | texture | 26 | −0.0170 | +0.0016 | +0.1194 | +0.6740 |
| solid | dom | 26 | −0.0269 | +0.0101 | +0.1379 | +0.6871 |

Positive means the exterior half of the band scores better than the interior half, which is the
usual case (median positive in all ten classes) and the expected one: half of the exterior window's
pixels are untouched backdrop. The negative tails are where it inverts, and they are the large 2x
`checkerboard` cells from §5 — the minimum, −0.1548 on the texture tier, is exactly the regime
where the outward row is doing the work `ssimBand` alone would have missed.

`impulse` and `solid` on the GPU tier are the null case for the *inner* split — band and interior
within 0.008 of each other — which is the right sanity check on the instrument: where there is no
backdrop structure for a lens to displace, the two inside windows agree.
