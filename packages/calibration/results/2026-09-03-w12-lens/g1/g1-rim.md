# W12 G1 — the near-contour profile and the along-edge magnification (2026-09-03)

Method (`g1b-rim.py`, `rim.json`, `rim.out`; strips `rim-strip-{checkerboard,light-solid}-{1,2}x.png`;
`tangential.out`). `rrect-md`, native against vitrea webgpu. Per straight edge, the mean and the
along-edge standard deviation of linear luminance per pixel row, from 2 px outside the contour to 8 px
inside: 0.5 CSS px rows at 2x (pixel centres at u = 0.25, 0.75, …), 1 px at 1x. Along-edge windows are
whole checker periods (top/bottom x ∈ [104, 200] = 3 periods; left/right y ∈ [80, 112] = 1 period), so
on the checkerboard a row mean is the plate's mean for any pure normal displacement or blur. "Deep" is
the mean over 24 ≤ u ≤ 30 in the same window. The along-edge period is the sub-pixel autocorrelation
lag of the fundamental (32 CSS px in the plate) on the top edge, x ∈ [96, 224].

## 1. The profile, top edge, 2x (linear luminance; u at pixel centres)

| u | light-solid native / vitrea | dark-solid native / vitrea | checkerboard native mean (std) / vitrea mean (std) | photo native / vitrea |
| --- | --- | --- | --- | --- |
| −0.25 | 0.826 / 0.801 | 0.011 / 0.011 | 0.449 (0.448) / 0.448 (0.448) | 0.115 / 0.111 |
| +0.25 | **1.000** / **1.000** | **0.750** / **0.854** | **0.867** (0.032) / **0.977** (0.028) | **0.776** / **0.979** |
| +0.75 | 0.978 / 1.000 | 0.634 / 0.618 | 0.802 (0.100) / 0.822 (0.104) | 0.727 / 0.756 |
| +1.25 | 0.934 / 0.933 | 0.480 / 0.503 | 0.692 (0.107) / 0.703 (0.105) | 0.639 / 0.637 |
| +1.75 | 0.934 / 0.923 | 0.480 / 0.486 | 0.674 (**0.040**) / 0.690 (0.106) | 0.638 / 0.623 |
| +2.25 | 0.934 / 0.923 | 0.480 / 0.491 | 0.660 (0.077) / 0.691 (0.106) | 0.638 / 0.623 |
| +2.75 | 0.934 / 0.923 | 0.480 / 0.491 | 0.654 (0.121) / 0.692 (0.106) | 0.638 / 0.622 |
| +3.25 | 0.934 / 0.923 | 0.480 / 0.491 | **0.652** (0.154) / 0.692 (0.106) | 0.638 / 0.622 |
| +3.75 | 0.934 / 0.923 | 0.480 / 0.491 | 0.652 (**0.158**) / 0.692 (0.106) | 0.637 / 0.622 |
| +4.25 | 0.934 / 0.923 | 0.480 / 0.491 | 0.653 (0.158) / 0.693 (0.107) | 0.636 / 0.622 |
| +4.75 | 0.934 / 0.923 | 0.480 / 0.491 | 0.656 (0.151) / 0.693 (0.106) | 0.635 / 0.622 |
| +5.25 | 0.934 / 0.923 | 0.480 / 0.491 | 0.658 (0.132) / 0.694 (0.105) | 0.633 / 0.622 |
| +5.75 | 0.934 / 0.923 | 0.480 / 0.491 | 0.661 (0.116) / 0.695 (0.103) | 0.631 / 0.622 |
| +6.25 | 0.934 / 0.931 | 0.480 / 0.491 | 0.664 (0.100) / 0.694 (0.092) | 0.629 / 0.622 |
| +6.75 | 0.934 / 0.931 | 0.480 / 0.491 | 0.666 (0.087) / 0.696 (0.075) | 0.627 / 0.621 |
| +7.25 | 0.934 / 0.931 | 0.480 / 0.491 | 0.673 (0.064) / 0.694 (0.059) | 0.625 / 0.621 |
| +7.75 | 0.934 / 0.931 | 0.480 / 0.491 | 0.679 (**0.021**) / 0.695 (0.044) | 0.623 / 0.622 |
| deep (24–30) | 0.934 / 0.932 | 0.480 / 0.497 | 0.681 (0.122 interior std) / 0.701 (0.095) | 0.632 / 0.630 |

The same at 1x (checkerboard, native mean (std) / vitrea): u 0.5: 0.842 (0.054) / 0.905 (0.091); 1.5:
0.712 (0.103) / 0.685 (0.107); 2.5: 0.660 (0.109) / 0.685; 3.5: 0.658 (0.115) / 0.686; 4.5: 0.658
(0.117) / 0.686; 5.5: 0.659 (0.117) / 0.686; 6.5: 0.665 (0.120) / 0.688 (0.086); 7.5: 0.676
(**0.031**) / 0.689 (0.057); deep 0.679 / 0.693.

## 2. The features, named

**The bright rim line.** Native: peak at the first interior row, +0.065 above the deep level on
light-solid (both scales), +0.27 / +0.245 / +0.275 / +0.253 (top / bottom / left / right) on dark-solid
at 2x and +0.218 / +0.199 / +0.220 / +0.204 at 1x; FWHM 1.0 CSS px at 2x (two device rows: 1.000 then
0.978 on light-solid) and 1 px at 1x. Vitrea: FWHM 0.5 CSS px at 2x (one device row), +0.357 / +0.112 /
+0.326 / +0.113 on dark-solid — **vitrea's rim is 3.2:1 top/left against bottom/right; the reference's
is 1.1:1** (light from the top-left on both, but the reference's specular is nearly isotropic).
Vitrea's rim is also 1 device px thin at 2x where the reference's is 2. On the checkerboard and photo
the reference's rim peak is lower than vitrea's on the lit sides (0.867 against 0.977; 0.776 against
0.979) because vitrea's rim is drawn brighter, not because the reference's is darker than its solids.
Rim/specular constants are untouched by charter; these numbers are for whoever owns them.

**The dark line: there is none on a solid backdrop.** Native light-solid runs 1.000 → 0.978 → 0.934 and
stays at 0.934 to u = 8 (dip 0.000); dark-solid 0.750 → 0.634 → 0.480 flat (dip 0.000); at 1x the same.
So the line the eye sees is neither a drawn stroke (a stroke would sit on a solid too) nor a Fresnel
transmission term on a uniform field (a transmission loss would scale the solid's 0.934 or 0.480 and
does not). It appears only where the backdrop has structure: checkerboard row-mean dips of −0.030
(top, at u 3.25), −0.023 (bottom, 1.75), −0.060 (left, 4.75), −0.106 (right, 1.25) at 2x and
−0.021 / −0.018 / −0.051 / −0.047 at 1x; photo −0.001 / −0.010 / −0.004 / −0.039 at 2x. The line is a
lens feature: what sits just inside the rim is a row of the band whose along-edge mean is not the
plate's mean — see §3 for why a period-mean can move at all. Vitrea's small dip (−0.009 to −0.011 on
every backdrop, solids included, from u 1.75 to 5.75, then a step back at 6.25) is its inner shadow,
a term the reference does not have on solids.

**Where the band's first lobe begins.** The along-edge contrast on the checkerboard (2x, native) is
the map: 0.032 at the rim, 0.10–0.11 at u 0.75–1.25, **a null at u ≈ 1.75 (0.040)**, then a rise to
**0.158 at u 3.75–4.25 — higher than the deep interior's 0.122** — falling to **a second null at
u ≈ 7.75 (0.021)** and recovering to the interior's value by u ≈ 10 (`g1-depth-ramp.md` §1b has the
shells beyond). The first lobe is the region between the two nulls: it begins at u ≈ 2, peaks in
contrast at u ≈ 4, and ends at the fold at u ≈ 8. The second null is the fold of the landed law's
reversal (the stationary source coordinate); the first null, one to two pixels inside the rim, is
something the landed law does not produce. Vitrea's contrast is flat at 0.104–0.107 from u 0.75 to
5.75, then falls to 0.044 at 7.75 — one shallow null at the fold, no first null, and no contrast above
its own interior's 0.095. At 1x the native's second null is at u ≈ 7.5 (0.031) and the first is not
resolved by 1-px rows; the band's contrast (0.109–0.120) does not exceed the 1x interior's (0.103) the
way it does at 2x.

## 3. The along-edge period — the band magnifies tangentially

Autocorrelation period of the checker fundamental along the top edge, per row (CSS px; plate 32.0):

| u (2x rows) | native | vitrea | | u (1x rows) | native | vitrea |
| --- | --- | --- | --- | --- | --- | --- |
| 1.25 | **42.2** | 32.3 | | 1.5 | **41.0** | 32.3 |
| 2.25 | 42.5 | 32.2 | | 2.5 | 40.9 | 32.2 |
| 3.25 | 39.8 | 32.2 | | 3.5 | 39.5 | 32.2 |
| 4.25 | 38.0 | 32.2 | | 4.5 | 38.0 | 32.2 |
| 5.25 | 36.8 | 32.2 | | 5.5 | 36.9 | 32.2 |
| 6.25 | 36.0 | 32.3 | | 6.5 | 35.8 | 32.3 |
| 7.25 | 35.2 | 32.4 | | 7.5 | 34.2 (weak) | 32.3 |
| 8.25 | 34.5 | 32.8 | | 8.5 | 34.4 | 34.7 (weak) |
| 10.25 | 33.7 | 32.1 | | 10.5 | 33.5 | 32.1 |
| 12.25 | 33.0 | 32.2 | | 12.5 | 32.9 | 32.2 |
| 14.25 | 32.6 | 32.2 | | 14.5 | 32.5 | 32.2 |
| 16.25 | 32.3 | 32.2 | | 16.5 | 32.2 | 32.2 |
| 18.25 | 32.0 | 32.1 | | 18.5 | 31.9 | 32.1 |

The reference's band is magnified **along** the edge by 1.32× at u ≈ 1–2, 1.19× at 4, 1.13× at 6,
1.08× at 8, 1.05× at 10, 1.03× at 12, 1.02× at 14, 1.01× at 16 and 1.00 by 18 — identical at 1x and
2x in CSS px (a points law), and close to 1 + 0.35·(1 − u/18)² over the whole band. Vitrea's period
is 32.2 at every depth: the landed law has no tangential term, and a normal-only displacement cannot
have one on a straight edge. This is the "cells bend along the edge" of §5.48, measured: the sample
position is pulled toward the midpoint of the edge by a share that peaks at the contour, on top of
the inward pull. At 64 px from the edge's centre and u = 2 the tangential pull is 64·(1 − 1/1.32) ≈
15 CSS px against ≈ 30–35 px inward — the field is anisotropic, roughly 2:1 normal to tangential
there. It is also why a whole-period row mean can move (§2): the window no longer spans whole periods
where the period is 42 px, so the "dark line" on the checkerboard is partly this magnification read
through a fixed window and partly the first null's uniform row; the solids show that nothing else is
there.

For the straight-edge instrument: a normal-only warp will leave this tangential term in its residual
on every line that is not at the edge's centre; lines through the edge midpoint see none of it.

## 4. Numbers to carry

- No dark line on solids (dip 0.000 at both scales, both solids); dips only on structured backdrops.
- Contrast nulls on the native checkerboard band at u ≈ 1.75 and ≈ 7.75 (2x), lobe contrast 0.158 >
  interior 0.122 between them; vitrea: one shallow null at the fold, band contrast ≤ interior.
- Rim: native FWHM 1.0 CSS px at 2x (vitrea 0.5); native anisotropy 1.1:1, vitrea 3.2:1 (dark-solid).
- Tangential magnification 1.32 → 1.00 over u 1 → 18, same at both scales; vitrea 1.00 throughout.
