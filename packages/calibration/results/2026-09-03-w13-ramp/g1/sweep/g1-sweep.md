# W13 G1 — the runtime sweep of the depth ramp's four constants (2026-09-03)

The binding rule executed: the four PROVISIONAL constants
(`sizeScatterRampStart1x`, `…Start2x`, `…Reach1xPx`, `…Reach2xPx`) turned through the real
GPU renderer on the calibration cells at both scales, and scored on the rows this wave
turns on. Commands, base and provenance: `README.md` beside this file.

**Headline. The declared form does not reach the wave's stops at either scale, and the
reason is structural, not a matter of finding a better point in the grid.** 81 points over
both scales: `ssimBand` never rises on all five checkerboard cells (S4) at either scale;
`interiorStdDev` at 2x is never within 0.005 of the reference on the five spans (S3, best
0.0151 against a tolerance of 0.005); the 2x `rrect-ml` row never rises above its
W12-close floor (S2). S1 (no 1x row down by more than 0.002) is met at three 1x points, and
the best of them is the recommendation below. The mechanism is in §4: a ramp with a start
and a device-pixel reach projects onto a **much weaker span law** than the
`sizeScatterFloor` + `sizeScatterSpanMax` smoothstep it retires, and the bed's span
dependence is what that smoothstep was carrying.

## 1. What was swept, and against what

Points: 1x 43 (`1x-startA` 5, `1x-grid` 30, `1x-flat` 12, `1x-frontier` 4, overlaps
de-duplicated), 2x 38 (`2x-grid` 30, `2x-flat` 9, one overlap). Two-dimensional grids
rather than the charter's coordinate descent, because a point costs 22 s at 1x and 100 s at
2x and the start/reach pair trades off along a valley a coordinate path would report as a
surface. The coordinate-descent readings are the columns of the grids and agree with it:
`1x-startA` is the charter's first step verbatim (the start at the provisional reach 110)
and its ordering — 0.7 best, then 0.8, 0.6, 0.5, 0.4 on the objective — is the ordering
the grid's reach-110 column reproduces.

The reference row in every table is the **W12 close bed with the X6 band rows**,
`../../g0/matrix-x6-baseline.json` — the canonical `results/matrix.json` predates X6 and
carries no `ssimBand`; the two agree cell for cell on `ssimMean` and `interiorStdDev`.
`NATIVE` is the fixture's own `interiorStdDevNative` on that bed.

Cells scored: the four checkerboard calibration spans (`rrect-sm`, `capsule-button`,
`rrect-md`, `rrect-ml`), `checkerboard__toolbar-group` (also a calibration cell at both
scales, so five checkerboard cells not four), and `photo__rrect-md`. `ssimInterior` is
absent on `rrect-sm`, `capsule-button` and `toolbar-group`: no pixel of those silhouettes
is deeper than the 24 CSS px band split, so those surfaces are all band.

**One caveat on the 2x comparison.** The branch carries the device-pixel body widths
(§5.56 §1) as well as the ramp, and the W12 close does not, so a 2x row's movement is the
two changes together. At 1x the widths are identical (dpr 1) and the movement is the ramp
alone. §5.58 §2's widths-only readings are quoted in §3 as the second 2x reference.

## 2. The 1x fit

Stops at 1x: S1 binds (no row below its W12-close `ssimMean` by more than 0.002) and S4
binds (`ssimBand` rises on every checkerboard cell). S2 and S3 are 2x stops; the columns
for them are printed at 1x as information, not as a verdict.

#### 1x — all 43 points, ranked by mean ssimBand rise

```
start reach         obj  bandRise  S1 minΔssimMean  S2 Δml ssimMean  S3 max|Δisd|  S4 minΔband
0.65 450        0.05339   -0.0013        -0.0112 F        -0.0112 F      0.0330 F    -0.0131 F
0.65 600        0.05358   -0.0014        -0.0135 F        -0.0135 F      0.0359 F    -0.0145 F
0.6  600        0.05379   -0.0015        -0.0072 F        -0.0072 F      0.0266 F    -0.0045 F
0.65 300        0.05316   -0.0017        -0.0071 F        -0.0071 F      0.0276 F    -0.0109 F
0.6  450        0.05373   -0.0022        -0.0056 F        -0.0056 F      0.0275 F    -0.0048 F
0.7  200        0.05254   -0.0029        -0.0074 F        -0.0074 F      0.0291 F    -0.0173 F
0.6  300        0.05380   -0.0030        -0.0024 F        -0.0024 F      0.0294 F    -0.0051 F
0.7  150        0.05242   -0.0031        -0.0037 F        -0.0037 F      0.0218 F    -0.0148 F
0.7  600        0.05313   -0.0034        -0.0205 F        -0.0205 F      0.0452 F    -0.0250 F
0.7  300        0.05296   -0.0035        -0.0136 F        -0.0136 F      0.0373 F    -0.0223 F
0.7  450        0.05310   -0.0037        -0.0182 F        -0.0182 F      0.0426 F    -0.0245 F
0.55 600        0.05473   -0.0044        -0.0023 F        -0.0023 F      0.0369 F    -0.0113 F
0.6  200        0.05418   -0.0047        -0.0008 P        +0.0004 P      0.0328 F    -0.0093 F
0.55 450        0.05477   -0.0052        -0.0011 P        -0.0011 F      0.0377 F    -0.0126 F
0.7  110        0.05267   -0.0052        -0.0038 F        -0.0038 F      0.0197 F    -0.0120 F
0.55 300        0.05504   -0.0070        -0.0013 P        +0.0009 P      0.0393 F    -0.0158 F
0.6  150        0.05457   -0.0075        -0.0024 F        -0.0001 F      0.0353 F    -0.0145 F
0.8  110        0.05297   -0.0079        -0.0083 F        -0.0083 F      0.0303 F    -0.0315 F
0.8  80         0.05216   -0.0085        -0.0118 F        -0.0118 F      0.0179 F    -0.0255 F
0.8  150        0.05440   -0.0091        -0.0142 F        -0.0142 F      0.0406 F    -0.0372 F
0.7  80         0.05338   -0.0098        -0.0172 F        -0.0172 F      0.0261 F    -0.0133 F
0.8  200        0.05537   -0.0104        -0.0210 F        -0.0210 F      0.0484 F    -0.0423 F
0.55 200        0.05542   -0.0106        -0.0023 F        +0.0012 P      0.0421 F    -0.0215 F
0.5  600        0.05614   -0.0107        -0.0020 P        +0.0006 P      0.0464 F    -0.0238 F
0.5  450        0.05618   -0.0121        -0.0021 F        +0.0013 P      0.0473 F    -0.0254 F
0.8  300        0.05651   -0.0123        -0.0289 F        -0.0289 F      0.0565 F    -0.0478 F
0.8  60         0.05241   -0.0123        -0.0283 F        -0.0283 F      0.0153 F    -0.0225 F
0.6  110        0.05571   -0.0127        -0.0088 F        -0.0088 F      0.0393 F    -0.0226 F
0.5  300        0.05638   -0.0143        -0.0025 F        +0.0021 P      0.0495 F    -0.0297 F
0.5  200        0.05764   -0.0190        -0.0050 F        -0.0003 F      0.0519 F    -0.0369 F
0.7  60         0.05551   -0.0196        -0.0365 F        -0.0365 F      0.0334 F    -0.0271 F
0.6  80         0.05779   -0.0231        -0.0287 F        -0.0287 F      0.0449 F    -0.0384 F
0.5  150        0.05879   -0.0249        -0.0087 F        -0.0071 F      0.0547 F    -0.0449 F
0.5  110        0.06017   -0.0343        -0.0238 F        -0.0238 F      0.0590 F    -0.0582 F
0.4  300        0.06096   -0.0403        -0.0097 F        -0.0036 F      0.0687 F    -0.0691 F
0.6  60         0.05976   -0.0404        -0.0480 F        -0.0480 F      0.0516 F    -0.0613 F
0.4  200        0.06204   -0.0485        -0.0145 F        -0.0127 F      0.0719 F    -0.0797 F
0.5  80         0.06183   -0.0505        -0.0442 F        -0.0442 F      0.0643 F    -0.0796 F
0.4  150        0.06306   -0.0569        -0.0263 F        -0.0263 F      0.0745 F    -0.0911 F
0.4  110        0.06423   -0.0711        -0.0444 F        -0.0444 F      0.0781 F    -0.1092 F
0.5  60         0.06327   -0.0757        -0.0611 F        -0.0611 F      0.0704 F    -0.1104 F
0.4  80         0.06556   -0.0949        -0.0617 F        -0.0617 F      0.0833 F    -0.1381 F
0.4  60         0.06670   -0.1271        -0.0733 F        -0.0733 F      0.0888 F    -0.1775 F
```

Eight points in detail — the provisional point (0.6, 110), the S1-clearing band maximum
(0.6, 200), the unconstrained band maximum (0.65, 450) and its neighbour (0.65, 300), the
two the charter's coordinate-descent path reaches (0.7, 110) and (0.7, 200), the
`rrect-ml`-favouring (0.55, 450), and the interior objective's own winner (0.8, 80):

#### 1x — interiorStdDev, web

```
point               obj       sm     caps       md       ml       tb   pho-md
main                  —   0.1408   0.1206   0.0994   0.0769   0.1227   0.0461
NATIVE                —   0.1549   0.1424   0.1131   0.0865   0.1481   0.0572
0.6  110        0.05571   0.1281   0.1044   0.0913   0.0813   0.1087   0.0458
0.6  200        0.05418   0.1327   0.1120   0.1041   0.0971   0.1153   0.0464
0.65 300        0.05316   0.1451   0.1246   0.1192   0.1141   0.1282   0.0471
0.65 450        0.05339   0.1470   0.1269   0.1233   0.1196   0.1304   0.0473
0.7  110        0.05267   0.1475   0.1227   0.1092   0.0987   0.1284   0.0467
0.7  200        0.05254   0.1534   0.1311   0.1225   0.1157   0.1357   0.0473
0.55 450        0.05477   0.1270   0.1084   0.1044   0.1005   0.1104   0.0463
0.8  80         0.05216   0.1629   0.1349   0.1172   0.1045   0.1427   0.0471
```

#### 1x — ssimBand

```
point               obj       sm     caps       md       ml       tb   pho-md
main                  —   0.9673   0.8815   0.9317   0.9370   0.7227   0.9910
0.6  110        0.05571   0.9548   0.8589   0.9234   0.9352   0.7047   0.9909
0.6  200        0.05418   0.9623   0.8722   0.9313   0.9357   0.7152   0.9910
0.65 300        0.05316   0.9692   0.8825   0.9318   0.9261   0.7219   0.9909
0.65 450        0.05339   0.9704   0.8843   0.9316   0.9240   0.7233   0.9909
0.7  110        0.05267   0.9675   0.8784   0.9270   0.9250   0.7161   0.9908
0.7  200        0.05254   0.9711   0.8848   0.9287   0.9197   0.7216   0.9909
0.55 450        0.05477   0.9588   0.8689   0.9331   0.9393   0.7143   0.9910
0.8  80         0.05216   0.9688   0.8817   0.9201   0.9115   0.7157   0.9907
```

#### 1x — ssimInterior

```
point               obj       sm     caps       md       ml       tb   pho-md
main                  —     —        —      0.9817   0.9803     —      0.9958
0.6  110        0.05571     —        —      0.9204   0.9455     —      0.9950
0.6  200        0.05418     —        —      0.9750   0.9847     —      0.9957
0.65 300        0.05316     —        —      0.9826   0.9626     —      0.9959
0.65 450        0.05339     —        —      0.9796   0.9473     —      0.9959
0.7  110        0.05267     —        —      0.9638   0.9786     —      0.9955
0.7  200        0.05254     —        —      0.9833   0.9684     —      0.9959
0.55 450        0.05477     —        —      0.9809   0.9742     —      0.9958
0.8  80         0.05216     —        —      0.9554   0.9592     —      0.9954
```

#### 1x — ssimMean

```
point               obj       sm     caps       md       ml       tb   pho-md
main                  —   0.9988   0.9852   0.9695   0.9482   0.9643   0.9975
0.6  110        0.05571   0.9983   0.9833   0.9627   0.9395   0.9629   0.9974
0.6  200        0.05418   0.9986   0.9844   0.9688   0.9486   0.9637   0.9975
0.65 300        0.05316   0.9988   0.9853   0.9694   0.9411   0.9641   0.9975
0.65 450        0.05339   0.9989   0.9854   0.9692   0.9371   0.9642   0.9975
0.7  110        0.05267   0.9988   0.9849   0.9670   0.9445   0.9636   0.9974
0.7  200        0.05254   0.9989   0.9855   0.9689   0.9408   0.9641   0.9975
0.55 450        0.05477   0.9985   0.9841   0.9696   0.9472   0.9636   0.9975
0.8  80         0.05216   0.9988   0.9852   0.9649   0.9365   0.9635   0.9974
```


**Reading.**

- **No 1x point raises `ssimBand` on all five cells.** The two ends of the bed pull
  opposite ways: `rrect-sm`, `capsule-button` and `toolbar-group` want a **high** start
  (their band peaks at 0.7–0.8) and `rrect-md` and `rrect-ml` want a **low** one (0.5–0.6).
  Each cell can be raised alone — `rrect-sm` to 0.9732 (main 0.9673), `capsule-button` to
  0.8872 (0.8815), `toolbar-group` to 0.7240 (0.7227), `rrect-md` to 0.9345 (0.9317),
  `rrect-ml` to 0.9423 (0.9370) — and never together. The best mean rise over the five is
  **−0.0013** at (0.65, 450).
- **The reach runs to the flat limit.** At a fixed start the band improves monotonically
  with the reach out to 450–600 device px and then stops moving: at start 0.65 the mean
  rise is −0.0017 / −0.0013 / −0.0014 at reach 300 / 450 / 600. A reach that long makes
  s(u) nearly constant over every calibration surface (the deepest point of `rrect-ml` is
  64 CSS px). **The 1x bed prefers a ramp that is barely a ramp**, which is the opposite of
  what G0's measured reach of 108–144 CSS px predicted, and the flatness means the reach is
  only weakly identified above ≈ 200 device px.
- **S1 is met at exactly three points** — (0.6, 200) at −0.0008, (0.55, 450) at −0.0011 and
  (0.55, 300) at −0.0013 — and `rrect-ml` is the row that fails it everywhere else. At
  (0.6, 200) `rrect-ml`'s whole-crop `ssimMean` actually *rises*, by 0.0004.
- **`interiorStdDev` improves at 1x**, which the wave's baseline predicted (the 1x interior
  is blurrier than the reference). Main sits at 83–91% of native; (0.6, 200) sits at
  86–112% and (0.7, 200) at 99–134%, i.e. past it on the large spans. The improvement is
  not uniform in span: the ramp closes `rrect-sm` and over-closes `rrect-ml`.
- **The interior objective and the band row disagree, and by a lot.** The objective's
  winner over the 43 points is **(0.8, 80) at 0.05216**, whose band mean rise is −0.0085
  and whose `ssimMean` on `rrect-ml` is 0.0118 below the W12 close. The band's winner
  (0.65, 450) reads 0.05339 on the objective, 2.4% worse. The objective is a
  silhouette-interior quantity and cannot see the band, which is why X6 added these rows.
- `photo__rrect-md` moves by at most 0.0004 in `ssimBand` and 0.0001 in `ssimMean` across
  the whole 1x grid: the ramp is invisible on a smooth backdrop, as S5 expects.

## 3. The 2x fit

#### 2x — all 38 points, ranked by mean ssimBand rise
```
start reach         obj  bandRise  S1 minΔssimMean  S2 Δml ssimMean  S3 max|Δisd|  S4 minΔband
0.55 200        0.07154   -0.0012        -0.0102 F        -0.0102 F      0.0344 F    -0.0373 F
0.55 350        0.06959   -0.0016        -0.0192 F        -0.0192 F      0.0263 F    -0.0458 F
0.45 200        0.07641   -0.0018        -0.0057 F        -0.0057 F      0.0535 F    -0.0203 F
0.55 500        0.06912   -0.0027        -0.0252 F        -0.0252 F      0.0235 F    -0.0503 F
0.55 140        0.07376   -0.0034        -0.0090 F        -0.0090 F      0.0425 F    -0.0315 F
0.65 200        0.06727   -0.0078        -0.0185 F        -0.0185 F      0.0151 F    -0.0593 F
0.45 140        0.07845   -0.0085        -0.0076 F        -0.0073 F      0.0609 F    -0.0191 F
0.65 350        0.06758   -0.0106        -0.0317 F        -0.0317 F      0.0281 F    -0.0692 F
0.55 100        0.07630   -0.0110        -0.0106 F        -0.0106 F      0.0524 F    -0.0294 F
0.35 200        0.08116   -0.0121        -0.0070 F        -0.0051 F      0.0730 F    -0.0157 F
0.65 500        0.06799   -0.0126        -0.0381 F        -0.0381 F      0.0363 F    -0.0740 F
0.75 200        0.06859   -0.0192        -0.0298 F        -0.0298 F      0.0284 F    -0.0836 F
0.55 80         0.07802   -0.0223        -0.0118 F        -0.0118 F      0.0602 F    -0.0339 F
0.45 100        0.08057   -0.0227        -0.0108 F        -0.0096 F      0.0702 F    -0.0304 F
0.35 140        0.08287   -0.0241        -0.0103 F        -0.0077 F      0.0796 F    -0.0339 F
0.75 350        0.07133   -0.0245        -0.0452 F        -0.0452 F      0.0473 F    -0.0948 F
0.75 500        0.07257   -0.0271        -0.0516 F        -0.0516 F      0.0556 F    -0.0998 F
0.25 200        0.08548   -0.0340        -0.0111 F        -0.0073 F      0.0920 F    -0.0516 F
0.45 80         0.08207   -0.0351        -0.0122 F        -0.0105 F      0.0767 F    -0.0485 F
0.55 60         0.08022   -0.0390        -0.0131 F        -0.0124 F      0.0701 F    -0.0497 F
0.35 100        0.08459   -0.0408        -0.0123 F        -0.0094 F      0.0874 F    -0.0603 F
0.25 140        0.08658   -0.0483        -0.0130 F        -0.0091 F      0.0978 F    -0.0728 F
0.45 60         0.08389   -0.0500        -0.0133 F        -0.0109 F      0.0844 F    -0.0688 F
0.35 80         0.08558   -0.0510        -0.0132 F        -0.0100 F      0.0927 F    -0.0743 F
0.25 100        0.08765   -0.0606        -0.0142 F        -0.0101 F      0.1036 F    -0.0889 F
0.55 40         0.08329   -0.0608        -0.0144 F        -0.0125 F      0.0825 F    -0.0803 F
0.35 60         0.08689   -0.0625        -0.0144 F        -0.0107 F      0.0992 F    -0.0892 F
0.15 200        0.08926   -0.0640        -0.0148 F        -0.0104 F      0.1094 F    -0.0949 F
0.45 40         0.08606   -0.0662        -0.0150 F        -0.0118 F      0.0960 F    -0.0911 F
0.25 80         0.08829   -0.0671        -0.0150 F        -0.0108 F      0.1071 F    -0.0974 F
0.15 140        0.08963   -0.0718        -0.0158 F        -0.0114 F      0.1128 F    -0.1044 F
0.35 40         0.08817   -0.0727        -0.0160 F        -0.0121 F      0.1075 F    -0.1024 F
0.25 60         0.08905   -0.0730        -0.0160 F        -0.0118 F      0.1112 F    -0.1048 F
0.15 100        0.09009   -0.0768        -0.0166 F        -0.0122 F      0.1157 F    -0.1104 F
0.25 40         0.08975   -0.0791        -0.0173 F        -0.0131 F      0.1155 F    -0.1122 F
0.15 80         0.09030   -0.0793        -0.0172 F        -0.0128 F      0.1171 F    -0.1130 F
0.15 60         0.09059   -0.0820        -0.0177 F        -0.0134 F      0.1184 F    -0.1162 F
0.15 40         0.09086   -0.0846        -0.0182 F        -0.0140 F      0.1196 F    -0.1188 F
```
#### 2x — interiorStdDev, web

```
point               obj       sm     caps       md       ml       tb   pho-md
main                  —   0.1372   0.1189   0.0973   0.0746   0.1203   0.0488
NATIVE                —   0.1636   0.1552   0.1272   0.1018   0.1581   0.0591
0.35 100        0.08459   0.0920   0.0689   0.0585   0.0525   0.0707   0.0502
0.45 200        0.07641   0.1217   0.1019   0.0864   0.0774   0.1046   0.0507
0.55 140        0.07376   0.1353   0.1127   0.0928   0.0827   0.1172   0.0508
0.55 200        0.07154   0.1410   0.1208   0.1041   0.0938   0.1244   0.0511
0.55 350        0.06959   0.1466   0.1292   0.1181   0.1108   0.1317   0.0514
0.65 200        0.06727   0.1605   0.1401   0.1227   0.1116   0.1443   0.0515
0.65 350        0.06758   0.1667   0.1488   0.1372   0.1299   0.1520   0.0518
```

#### 2x — ssimBand

```
point               obj       sm     caps       md       ml       tb   pho-md
main                  —   0.9417   0.8634   0.9315   0.9396   0.7432   0.9928
0.35 100        0.08459   0.9056   0.8031   0.8908   0.9153   0.7006   0.9928
0.45 200        0.07641   0.9539   0.8724   0.9210   0.9193   0.7435   0.9930
0.55 140        0.07376   0.9598   0.8769   0.9152   0.9081   0.7422   0.9930
0.55 200        0.07154   0.9637   0.8846   0.9158   0.9023   0.7470   0.9931
0.55 350        0.06959   0.9658   0.8886   0.9132   0.8938   0.7500   0.9931
0.65 200        0.06727   0.9650   0.8871   0.9037   0.8803   0.7445   0.9930
0.65 350        0.06758   0.9652   0.8873   0.8984   0.8704   0.7448   0.9931
```

#### 2x — ssimInterior

```
point               obj       sm     caps       md       ml       tb   pho-md
main                  —     —        —      0.9594   0.9589     —      0.9973
0.35 100        0.08459     —        —      0.8914   0.9428     —      0.9969
0.45 200        0.07641     —        —      0.9342   0.9557     —      0.9971
0.55 140        0.07376     —        —      0.9242   0.9533     —      0.9970
0.55 200        0.07154     —        —      0.9513   0.9540     —      0.9972
0.55 350        0.06959     —        —      0.9441   0.9229     —      0.9973
0.65 200        0.06727     —        —      0.9500   0.9406     —      0.9973
0.65 350        0.06758     —        —      0.9254   0.8918     —      0.9974
```

#### 2x — ssimMean

```
point               obj       sm     caps       md       ml       tb   pho-md
main                  —   0.9978   0.9836   0.9517   0.9158   0.9663   0.9981
0.35 100        0.08459   0.9966   0.9789   0.9393   0.9064   0.9633   0.9980
0.45 200        0.07641   0.9982   0.9844   0.9476   0.9101   0.9663   0.9981
0.55 140        0.07376   0.9984   0.9847   0.9457   0.9068   0.9661   0.9981
0.55 200        0.07154   0.9985   0.9853   0.9481   0.9056   0.9664   0.9981
0.55 350        0.06959   0.9985   0.9856   0.9471   0.8966   0.9667   0.9981
0.65 200        0.06727   0.9985   0.9855   0.9459   0.8973   0.9661   0.9981
0.65 350        0.06758   0.9985   0.9855   0.9430   0.8841   0.9661   0.9981
```


**Reading.**

- **Every 2x stop fails at every point.** S2: `rrect-ml`'s whole-crop `ssimMean` is below
  its W12-close floor at all 38 points, best −0.0057 at (0.45, 200). S3: the largest
  `interiorStdDev` departure from native over the five spans is 0.0151 at its best point
  (0.65, 200), three times the 0.005 tolerance, and the departure is never small on more
  than two of the five cells at once. S4: the band falls on `rrect-md` and `rrect-ml` at
  every point, by 0.016 to 0.100.
- **The same split as at 1x, in the same direction.** `rrect-sm`, `capsule-button` and
  `toolbar-group` rise (up to +0.024, +0.026 and +0.007 in `ssimBand`); `rrect-md` and
  `rrect-ml` fall. The best mean rise over the five is −0.0012 at (0.55, 200).
- **The ramp costs the 2x interior that the widths alone had won.** §5.58 §2 recorded the
  device-pixel widths without a ramp putting `interiorStdDev` on the reference at every 2x
  span — 0.1647 / 0.1500 / 0.1260 / 0.1029 against native 0.1636 / 0.1552 / 0.1272 /
  0.1018 on `rrect-sm` / `capsule-button` / `rrect-md` / `rrect-ml`. Adding the ramp at any
  point in this grid moves that away: the best 2x point for S3, (0.65, 200), reads 0.1605 /
  0.1401 / 0.1227 / 0.1116, and the band-optimal (0.55, 200) reads 0.1410 / 0.1208 / 0.1041
  / 0.0938. **The ramp and the 2x interior are in direct conflict under this form**, which
  is the S3 failure stated as a mechanism.
- `ssimInterior` at 2x saturates at 0.8914 / 0.9428 (`rrect-md` / `rrect-ml`) across most of
  the grid: with a reach of 200 device px or less the deep interior sits past the ramp's
  zero, so the sharp term is gone there and every point below that reach renders the same
  deep interior. That saturation is why the 2x objective and band both climb with the reach.
- The 2x interior objective's winner is **(0.65, 200) at 0.06727**, the band's is
  **(0.55, 200) at −0.0012 mean rise**; they differ, and (0.65, 200) is 0.0066 worse on the
  band mean.

## 4. Why: the ramp's span law is much weaker than the one it retires

The ramp's projection onto one number per surface — `scatterRampAreaMean`, the closed-form
area average the branch already computes for the CSS tier and the proxy padding — is the
honest summary of how heavy a surface is on average. Against the `sizeScatterFloor` +
`sizeScatterSpanMax` smoothstep the ramp replaces (`k = 0.4 + 0.6 · smoothstep(32, 256,
span)`), at the recommended constants:

| cell | span | retired span law `k` | ramp `k̄`, 1x (0.60, 200) | ramp `k̄`, 2x (0.55, 200) |
| --- | --- | --- | --- | --- |
| `rrect-sm` | 64 | 0.433 | 0.433 | 0.517 |
| `toolbar-group` | 44 | 0.405 | 0.437 | 0.523 |
| `capsule-button` | 120 | 0.605 | 0.448 | 0.547 |
| `rrect-md` | 160 | 0.764 | 0.496 | 0.642 |
| `rrect-ml` | 224 | 0.967 | 0.530 | 0.706 |
| `rrect-lg` | 280 | 1.000 | 0.562 | 0.752 |
| `glass-over-glass` | 220 | 0.958 | 0.530 | 0.707 |

The retired law runs from 0.41 to 1.00 across the bed; the ramp's projection runs from 0.43
to 0.56 at 1x and 0.52 to 0.75 at 2x. **The ramp is nearly span-flat where the bed is
strongly span-graded.** Everything above follows from it: the small spans, which the
retired law left too heavy, improve; the large spans, which it made almost fully heavy,
become far too sharp; and no start/reach pair can be both, because the family has no free
parameter that grades with span faster than the perimeter integral allows. It shows most
plainly on the largest span in the confirmation run below: `checkerboard__rrect-lg` at 1x
reads `interiorStdDev` 0.0938 against a reference of 0.0650, where the W12 close read
0.0540 — the ramp overshoots the reference by more than the W12 close undershot it.

This is a statement about the **form**, not about G0's measurement. G0 measured a real ramp
(§5.61 §2) and this sweep does not contradict it; what the sweep shows is that a ramp with
a start and a reach and **nothing else** cannot carry the span dependence the bed needs at
the same time, because in this form the span dependence is a consequence of the reach and
the reach is pinned by the band.

## 5. The recommendation

Ranked as the charter asks — on the band row's mean rise, subject to the stops — no point
qualifies at either scale, so the recommendation is the best point under the stops that can
still be met, with the ones that cannot named beside it.

| | 1x | 2x |
| --- | --- | --- |
| **recommended** | `sizeScatterRampStart1x` **0.60**, `sizeScatterRampReach1xPx` **200** | `sizeScatterRampStart2x` **0.55**, `sizeScatterRampReach2xPx` **200** |
| band mean rise | −0.0047 | −0.0012 (grid maximum) |
| interior objective | 0.05418 | 0.07154 |
| stops | S1 **met** (min ΔssimMean −0.0008; `rrect-ml` +0.0004); S4 missed | S2, S3, S4 all missed at every point |
| band's own maximum | (0.65, 450), rise −0.0013, S1 missed by 0.0112 on `rrect-ml` | (0.55, 200) — the same point |
| objective's own winner | (0.80, 80), 0.05216, band rise −0.0085 | (0.65, 200), 0.06727, band rise −0.0078 |

At 1x the recommendation is **not** the band's maximum: (0.65, 450) raises the band mean by
0.0034 more but drops `rrect-ml`'s whole-crop `ssimMean` by 0.0112, and S1 is a declared
stop while S4 is unreachable in this form. Only three 1x points meet S1 at all — (0.60,
200), (0.55, 450) and (0.55, 300) — and (0.60, 200) is the best of the three on the band.
At 2x the recommendation is the band's maximum outright.

**The 2x reach in device pixels equals the 1x one at the recommended point: both 200.**
That is the declaration's hypothesis, and it is *supported but weakly identified*. Support:
the 2x band optimum is at 200 device px on its own, and the 1x recommendation is at 200
device px on its own once S1 is imposed. Weakness: at both scales the objective and the
band are nearly flat in the reach above ≈ 200 device px — at 1x, start 0.65 gives a band
mean rise of −0.0017 / −0.0013 / −0.0014 at reach 300 / 450 / 600, a spread of 0.0004 over
a factor of two — so the equality is a point the data permits rather than one it picks out.
Neither scale's optimum is anywhere near G0's measured reach (110 device px at 1x, 100 at
2x): the runtime wants roughly twice that at 1x and twice that at 2x, and the unconstrained
1x optimum wants four times it.

The **starts** do not collapse: 0.60 at 1x against 0.55 at 2x, where G0 measured ≈ 0.6 and
≈ 0.35. The 2x start the runtime wants is much higher than the measurement's, and it is at
the top of the charter's declared 2x range (0.15–0.55); the extension sweep to 0.65 and 0.75
went past the band optimum, so 0.55 is an interior maximum in the extended grid and not an
edge artefact.

## 6. The confirmation run at the chosen constants

One run per profile at `sizeScatterRampStart1x` 0.60, `…Start2x` 0.55, `…Reach1xPx` 200,
`…Reach2xPx` 200 over `calibration,validation,holdout`, GPU tier, into
`matrix-confirm.json`:

    npx tsx cli/compare.ts --profile <key> --material-profile chosen-light.json \
      --renderer webgpu --set calibration,validation,holdout --write-partial \
      --out-matrix matrix-confirm.json

with `--profile` in turn `apple-macos-26.5-{1x,2x}-light-standard` (document
`chosen-light.json`) and `apple-macos-26.5-{1x,2x}-dark-standard` (document
`chosen-dark.json`). The dark document is a **difference** document — the committed
`profiles/apple-macos-26.5-1x-dark-standard.json` names only the constants that differ from
the light default and does **not** name the four ramp constants, so the dark run would have
rendered the branch's provisional values had they not been added to the copy. They are
added; that is the only difference between `chosen-dark.json` and the committed dark
document (plus the stripped fingerprint).

Every value below is the confirmation run's, with its change from the W12 close bed in
parentheses. `isd` is `interiorStdDev`, web against the fixture's native.


#### apple-macos-26.5-1x-light-standard

```
cell                                                   set           ssimMean           ssimBand       ssimInterior        ssimOutside      isd web/native
checkerboard__capsule-button__rest             calibration   0.9844 (-0.0008)   0.8722 (-0.0093)          —           0.9663 (+0.0000)       0.1120/0.1424
checkerboard__capsule-button__rest-tint-blue    validation   0.9888 (-0.0001)   0.9264 (-0.0013)          —           0.9655 (-0.0000)       0.0363/0.0526
checkerboard__capsule-button__rest-tint-orange calibration   0.9891 (-0.0002)   0.9276 (-0.0024)          —           0.9668 (+0.0000)       0.0390/0.0481
checkerboard__glass-over-glass__rest               holdout   0.9516 (-0.0005)   0.9414 (-0.0031)   0.9858 (+0.0016)   0.9130 (-0.0003)       0.1351/0.1321
checkerboard__rrect-lg__rest                       holdout   0.9347 (-0.0081)   0.9239 (-0.0156)   0.9680 (-0.0067)   0.8892 (-0.0013)       0.0938/0.0650
checkerboard__rrect-md__rest                   calibration   0.9688 (-0.0008)   0.9313 (-0.0004)   0.9750 (-0.0067)   0.9314 (-0.0006)       0.1041/0.1131
checkerboard__rrect-ml__rest                   calibration   0.9486 (+0.0004)   0.9357 (-0.0013)   0.9847 (+0.0044)   0.9075 (-0.0010)       0.0971/0.0865
checkerboard__rrect-sm__rest                   calibration   0.9986 (-0.0002)   0.9623 (-0.0050)          —           0.9989 (-0.0000)       0.1327/0.1549
checkerboard__toolbar-group__rest              calibration   0.9637 (-0.0006)   0.7152 (-0.0076)          —           0.9281 (+0.0000)       0.1153/0.1481
dark-solid__capsule-button__rest               calibration   0.9872 (+0.0000)   0.4044 (+0.0000)          —           0.9430 (+0.0000)                —   
dark-solid__capsule-button__rest-tint-blue         holdout   0.9850 (+0.0000)   0.9291 (+0.0000)          —           0.9383 (+0.0000)       0.0004/0.0326
dark-solid__capsule-button__rest-tint-orange   calibration   0.9847 (+0.0000)   0.9357 (+0.0000)          —           0.9327 (+0.0000)       0.0006/0.0304
dark-solid__rrect-md__rest                     calibration   0.9984 (+0.0000)   0.9953 (+0.0000)   0.9999 (+0.0000)   0.9968 (+0.0000)       0.0294/0.0346
hc-text__capsule-button__rest                      holdout   0.9840 (-0.0006)   0.8608 (-0.0069)          —           0.9699 (+0.0001)       0.0977/0.1153
hc-text__capsule-button__rest-tint-orange          holdout   0.9900 (-0.0001)   0.9320 (-0.0011)          —           0.9710 (+0.0000)       0.0347/0.0457
hc-text__rrect-md__rest                            holdout   0.9745 (-0.0015)   0.8896 (-0.0064)   0.9663 (-0.0010)   0.9832 (-0.0015)       0.1004/0.1078
impulse__capsule-button__rest                   validation   0.9770 (+0.0000)   0.4851 (+0.0000)          —           0.8942 (+0.0000)       0.0000/0.0038
impulse__capsule-button__rest-tint-orange      calibration   0.9836 (+0.0000)   0.9337 (+0.0000)          —           0.9262 (+0.0000)       0.0006/0.0324
impulse__rrect-md__rest                         validation   0.9978 (-0.0000)   0.9912 (-0.0006)   0.9971 (+0.0008)   0.9979 (+0.0000)       0.0312/0.0373
light-solid__capsule-button__rest              calibration   0.9897 (+0.0000)   0.9683 (+0.0000)          —           0.9513 (+0.0000)       0.0076/0.0094
light-solid__capsule-button__rest-tint-orange  calibration   0.9878 (+0.0000)   0.9463 (+0.0000)          —           0.9507 (+0.0000)       0.0274/0.0395
light-solid__rrect-md__rest                    calibration   0.9969 (-0.0000)   0.9922 (-0.0000)   1.0000 (+0.0000)   0.9945 (-0.0000)       0.0117/0.0121
light-solid__rrect-ml__rest                    calibration   0.9957 (+0.0000)   0.9922 (+0.0000)   1.0000 (+0.0000)   0.9938 (-0.0000)       0.0102/0.0107
mid-dark-solid__capsule-button__rest               holdout   0.9841 (+0.0000)   0.9324 (+0.0000)          —           0.9311 (+0.0000)       0.0335/0.0426
photo__capsule-button__rest                    calibration   0.9860 (-0.0000)   0.9380 (-0.0002)          —           0.9406 (-0.0000)       0.0463/0.0461
photo__capsule-button__rest-tint-blue          calibration   0.9848 (-0.0000)   0.9276 (-0.0000)          —           0.9384 (-0.0000)       0.0344/0.0477
photo__capsule-button__rest-tint-orange        calibration   0.9862 (+0.0000)   0.9351 (+0.0000)          —           0.9439 (-0.0000)       0.0332/0.0360
photo__capsule-button__rest-tint-orange-half   calibration   0.9865 (-0.0000)   0.9374 (-0.0001)          —           0.9446 (-0.0000)       0.0367/0.0385
photo__glass-over-glass__rest                      holdout   0.9951 (-0.0001)   0.9896 (-0.0002)   0.9932 (-0.0000)   0.9978 (-0.0000)       0.1158/0.1234
photo__rrect-lg__rest                              holdout   0.9946 (-0.0002)   0.9911 (-0.0006)   0.9959 (-0.0001)   0.9967 (-0.0000)       0.0501/0.0617
photo__rrect-lg__rest-tint-orange                  holdout   0.9931 (-0.0001)   0.9869 (-0.0001)   0.9987 (-0.0000)   0.9911 (-0.0000)       0.0227/0.0237
photo__rrect-md__rest                          calibration   0.9975 (-0.0000)   0.9910 (-0.0000)   0.9957 (-0.0001)   0.9977 (-0.0000)       0.0464/0.0572
photo__rrect-md__rest-tint-orange               validation   0.9960 (-0.0000)   0.9855 (-0.0000)   0.9987 (+0.0000)   0.9939 (-0.0000)       0.0280/0.0288
photo__rrect-ml__rest                          calibration   0.9958 (-0.0001)   0.9906 (-0.0002)   0.9956 (+0.0000)   0.9976 (-0.0000)       0.0515/0.0627
photo__rrect-sm__rest                           validation   0.9992 (-0.0000)   0.9877 (-0.0002)          —           0.9972 (+0.0000)       0.0441/0.0477
photo__toolbar-group__rest                      validation   0.9603 (+0.0000)   0.8227 (+0.0000)          —           0.8689 (-0.0000)       0.0633/0.0618
```

#### apple-macos-26.5-2x-light-standard

```
cell                                                   set           ssimMean           ssimBand       ssimInterior        ssimOutside      isd web/native
checkerboard__capsule-button__rest             calibration   0.9853 (+0.0017)   0.8846 (+0.0213)          —           0.9615 (+0.0001)       0.1208/0.1552
checkerboard__capsule-button__rest-tint-blue    validation   0.9892 (+0.0002)   0.9412 (+0.0020)          —           0.9575 (-0.0000)       0.0406/0.0582
checkerboard__capsule-button__rest-tint-orange calibration   0.9896 (+0.0002)   0.9431 (+0.0028)          —           0.9593 (-0.0000)       0.0425/0.0524
checkerboard__glass-over-glass__rest               holdout   0.9111 (-0.0101)   0.9013 (-0.0373)   0.9694 (-0.0051)   0.8222 (-0.0009)       0.1347/0.1401
checkerboard__rrect-lg__rest                       holdout   0.8890 (-0.0222)   0.8743 (-0.0636)   0.9685 (-0.0062)   0.7803 (-0.0029)       0.0879/0.0810
checkerboard__rrect-md__rest                   calibration   0.9481 (-0.0035)   0.9158 (-0.0157)   0.9513 (-0.0081)   0.8568 (-0.0016)       0.1041/0.1272
checkerboard__rrect-ml__rest                   calibration   0.9056 (-0.0102)   0.9023 (-0.0373)   0.9540 (-0.0049)   0.8117 (-0.0016)       0.0938/0.1018
checkerboard__rrect-sm__rest                   calibration   0.9985 (+0.0007)   0.9637 (+0.0221)          —           0.9971 (-0.0000)       0.1410/0.1636
checkerboard__toolbar-group__rest              calibration   0.9664 (+0.0001)   0.7470 (+0.0038)          —           0.9227 (-0.0009)       0.1244/0.1581
dark-solid__capsule-button__rest               calibration   0.9911 (+0.0000)   0.3238 (+0.0000)          —           0.9643 (+0.0000)                —   
dark-solid__capsule-button__rest-tint-blue         holdout   0.9876 (+0.0000)   0.9355 (+0.0000)          —           0.9493 (+0.0000)       0.0003/0.0386
dark-solid__capsule-button__rest-tint-orange   calibration   0.9883 (+0.0000)   0.9490 (+0.0000)          —           0.9466 (+0.0000)       0.0005/0.0315
dark-solid__rrect-md__rest                     calibration   0.9987 (+0.0000)   0.9949 (+0.0000)   0.9999 (+0.0000)   0.9981 (+0.0000)       0.0334/0.0369
hc-text__capsule-button__rest                      holdout   0.9855 (+0.0016)   0.8779 (+0.0240)          —           0.9670 (-0.0020)       0.1027/0.1243
hc-text__capsule-button__rest-tint-orange          holdout   0.9907 (+0.0003)   0.9472 (+0.0040)          —           0.9648 (-0.0000)       0.0381/0.0492
hc-text__rrect-md__rest                            holdout   0.9629 (-0.0019)   0.9115 (-0.0177)   0.9857 (+0.0163)   0.9071 (-0.0024)       0.0990/0.1004
impulse__capsule-button__rest                   validation   0.9772 (+0.0000)   0.2632 (+0.0000)          —           0.9001 (+0.0000)       0.0000/0.0046
impulse__capsule-button__rest-tint-orange      calibration   0.9880 (+0.0000)   0.9486 (+0.0000)          —           0.9443 (+0.0000)       0.0005/0.0329
impulse__rrect-md__rest                         validation   0.9985 (+0.0001)   0.9928 (+0.0004)   0.9986 (+0.0009)   0.9988 (-0.0000)       0.0347/0.0403
light-solid__capsule-button__rest              calibration   0.9934 (-0.0000)   0.9817 (-0.0000)          —           0.9654 (-0.0000)       0.0074/0.0078
light-solid__capsule-button__rest-tint-orange  calibration   0.9912 (+0.0000)   0.9617 (+0.0000)          —           0.9613 (+0.0000)       0.0312/0.0406
light-solid__rrect-md__rest                    calibration   0.9982 (+0.0000)   0.9973 (+0.0000)   1.0000 (+0.0000)   0.9954 (+0.0000)       0.0113/0.0096
light-solid__rrect-ml__rest                    calibration   0.9976 (+0.0000)   0.9970 (+0.0000)   1.0000 (+0.0000)   0.9953 (+0.0000)       0.0102/0.0087
mid-dark-solid__capsule-button__rest               holdout   0.9877 (-0.0000)   0.9460 (-0.0000)          —           0.9444 (-0.0000)       0.0384/0.0486
photo__capsule-button__rest                    calibration   0.9889 (+0.0000)   0.9513 (+0.0001)          —           0.9495 (+0.0000)       0.0506/0.0499
photo__capsule-button__rest-tint-blue          calibration   0.9889 (-0.0000)   0.9458 (-0.0000)          —           0.9529 (+0.0000)       0.0385/0.0528
photo__capsule-button__rest-tint-orange        calibration   0.9896 (-0.0000)   0.9516 (-0.0001)          —           0.9544 (-0.0000)       0.0363/0.0399
photo__capsule-button__rest-tint-orange-half   calibration   0.9891 (+0.0000)   0.9488 (-0.0000)          —           0.9522 (+0.0000)       0.0401/0.0433
photo__glass-over-glass__rest                      holdout   0.9963 (-0.0000)   0.9917 (+0.0001)   0.9955 (-0.0000)   0.9978 (-0.0000)       0.1174/0.1235
photo__rrect-lg__rest                              holdout   0.9958 (-0.0000)   0.9925 (-0.0001)   0.9976 (+0.0000)   0.9966 (-0.0000)       0.0536/0.0629
photo__rrect-lg__rest-tint-orange                  holdout   0.9951 (-0.0000)   0.9899 (-0.0000)   0.9992 (-0.0000)   0.9944 (-0.0000)       0.0263/0.0254
photo__rrect-md__rest                          calibration   0.9981 (+0.0000)   0.9931 (+0.0002)   0.9972 (-0.0001)   0.9978 (-0.0000)       0.0511/0.0591
photo__rrect-md__rest-tint-orange               validation   0.9972 (-0.0000)   0.9888 (-0.0000)   0.9990 (+0.0000)   0.9960 (-0.0000)       0.0328/0.0308
photo__rrect-ml__rest                          calibration   0.9968 (-0.0000)   0.9923 (+0.0000)   0.9973 (+0.0000)   0.9974 (-0.0000)       0.0556/0.0641
photo__rrect-sm__rest                           validation   0.9993 (+0.0000)   0.9876 (+0.0000)          —           0.9976 (-0.0000)       0.0517/0.0497
photo__toolbar-group__rest                      validation   0.9698 (-0.0000)   0.8740 (-0.0001)          —           0.8907 (-0.0000)       0.0670/0.0675
```

#### apple-macos-26.5-1x-dark-standard

```
cell                                                   set           ssimMean           ssimBand       ssimInterior        ssimOutside      isd web/native
checkerboard__capsule-button__rest             calibration   0.9619 (-0.0006)   0.6099 (-0.0075)          —           0.9606 (-0.0000)       0.0356/0.0671
checkerboard__capsule-button__rest-tint-orange calibration   0.9897 (+0.0000)   0.9368 (+0.0000)          —           0.9660 (+0.0000)       0.0273/0.0291
checkerboard__glass-over-glass__rest               holdout   0.9153 (+0.0073)   0.8936 (+0.0249)   0.8312 (+0.0052)   0.9413 (+0.0000)       0.0384/0.0233
checkerboard__rrect-md__rest                   calibration   0.9495 (+0.0002)   0.8361 (+0.0089)   0.8393 (-0.0151)   0.9629 (-0.0000)       0.0398/0.0280
dark-solid__capsule-button__rest               calibration   0.9868 (+0.0000)   0.3937 (+0.0000)          —           0.9417 (+0.0000)                —   
dark-solid__capsule-button__rest-tint-orange   calibration   0.9849 (+0.0000)   0.9356 (+0.0000)          —           0.9339 (+0.0000)       0.0006/0.0304
dark-solid__rrect-md__rest                     calibration   0.9311 (+0.0000)   0.5190 (+0.0000)          —           0.8596 (+0.0000)       0.0910/0.0051
impulse__capsule-button__rest                   validation   0.9770 (+0.0000)   0.4854 (+0.0000)          —           0.8943 (+0.0000)       0.0000/0.0038
mid-dark-solid__capsule-button__rest               holdout   0.9752 (+0.0000)   0.8937 (+0.0000)          —           0.8883 (+0.0000)       0.0090/0.0049
photo__capsule-button__rest                    calibration   0.9811 (-0.0000)   0.8917 (-0.0001)          —           0.9324 (+0.0000)       0.0342/0.0318
photo__capsule-button__rest-tint-orange        calibration   0.9865 (+0.0000)   0.9335 (+0.0000)          —           0.9461 (+0.0000)       0.0273/0.0255
photo__rrect-lg__rest                              holdout   0.9516 (+0.0002)   0.9327 (+0.0004)   0.9778 (+0.0001)   0.9285 (+0.0000)       0.0254/0.0161
photo__rrect-md__rest                          calibration   0.9763 (+0.0000)   0.9334 (+0.0001)   0.9818 (-0.0001)   0.9520 (-0.0000)       0.0336/0.0177
```

#### apple-macos-26.5-2x-dark-standard

```
cell                                                   set           ssimMean           ssimBand       ssimInterior        ssimOutside      isd web/native
checkerboard__capsule-button__rest             calibration   0.9704 (+0.0008)   0.7115 (+0.0097)          —           0.9528 (-0.0000)       0.0405/0.0701
checkerboard__capsule-button__rest-tint-orange calibration   0.9904 (+0.0000)   0.9538 (+0.0000)          —           0.9585 (+0.0000)       0.0308/0.0323
checkerboard__glass-over-glass__rest               holdout   0.9139 (+0.0031)   0.9147 (+0.0136)   0.8730 (-0.0004)   0.8804 (-0.0000)       0.0445/0.0259
checkerboard__rrect-md__rest                   calibration   0.9553 (+0.0010)   0.8797 (+0.0112)   0.9038 (-0.0091)   0.9245 (-0.0000)       0.0433/0.0291
dark-solid__capsule-button__rest               calibration   0.9910 (+0.0000)   0.2896 (+0.0000)          —           0.9636 (+0.0000)                —   
dark-solid__capsule-button__rest-tint-orange   calibration   0.9885 (+0.0000)   0.9489 (+0.0000)          —           0.9477 (+0.0000)       0.0005/0.0315
dark-solid__rrect-md__rest                     calibration   0.9446 (+0.0000)   0.5225 (+0.0000)          —           0.8901 (+0.0000)       0.1466/0.0095
impulse__capsule-button__rest                   validation   0.9772 (+0.0000)   0.2632 (+0.0000)          —           0.9001 (+0.0000)       0.0000/0.0046
mid-dark-solid__capsule-button__rest               holdout   0.9828 (+0.0000)   0.9137 (+0.0000)          —           0.9266 (+0.0000)       0.0363/0.0088
photo__capsule-button__rest                    calibration   0.9860 (+0.0000)   0.9174 (+0.0002)          —           0.9475 (+0.0000)       0.0392/0.0324
photo__capsule-button__rest-tint-orange        calibration   0.9898 (+0.0000)   0.9513 (+0.0000)          —           0.9558 (+0.0000)       0.0308/0.0289
photo__rrect-lg__rest                              holdout   0.9611 (+0.0001)   0.9416 (+0.0003)   0.9788 (+0.0001)   0.9530 (-0.0000)       0.0296/0.0164
photo__rrect-md__rest                          calibration   0.9822 (+0.0000)   0.9446 (+0.0002)   0.9836 (-0.0000)   0.9651 (-0.0000)       0.0390/0.0185
```

### The holdout rows, predicted

| row | W12 close | at the chosen constants | against the floor |
| --- | --- | --- | --- |
| `checkerboard__rrect-lg` 1x `ssimMean` | 0.9428 | **0.9347** (−0.0081) | falls; S1 would fail on a holdout row |
| `checkerboard__glass-over-glass` 1x `ssimMean` | 0.9521 | **0.9516** (−0.0005) | holds within S1 |
| `checkerboard__rrect-lg` 2x `ssimMean` | 0.9113 | **0.8890** (−0.0222) | **below its ratcheted floor**; S2 fails |
| `checkerboard__glass-over-glass` 2x `ssimMean` | 0.9211 | **0.9111** (−0.0101) | **below its ratcheted floor**; S2 fails |

Band and interior on the same four: `rrect-lg` 1x `ssimBand` 0.9239 (−0.0156) and
`ssimInterior` 0.9680 (−0.0067); `glass-over-glass` 1x 0.9414 (−0.0031) and 0.9858
(+0.0016); `rrect-lg` 2x 0.8743 (−0.0636) and 0.9685 (−0.0062); `glass-over-glass` 2x
0.9013 (−0.0373) and 0.9694 (−0.0051). `interiorStdDev` on `rrect-lg`: 1x 0.0938 against a
reference of 0.0650 (W12 close 0.0540) and 2x 0.0879 against 0.0810 (W12 close 0.0525) —
the 2x large span is the one place the ramp lands the interior on the reference, and the 1x
one overshoots it by 44%.

**The holdout confirms the calibration cells' verdict and sharpens it.** The two largest
surfaces on the bed are the two the ramp's weak span law hurts most, and they are both
holdout, so the calibration set alone understates the cost. This is one holdout read at one
frozen configuration.

### The dark scheme

The dark rows move the other way, modestly and almost everywhere upward. At 1x dark:
`glass-over-glass` `ssimMean` 0.9153 (+0.0073) and `ssimBand` 0.8936 (+0.0249);
`checkerboard__rrect-md` 0.9495 (+0.0002) and band 0.8361 (+0.0089), with `ssimInterior`
0.8393 (−0.0151); `checkerboard__capsule-button` 0.9619 (−0.0006) and band 0.6099
(−0.0075). At 2x dark every checkerboard row rises: `capsule-button` 0.9704 (+0.0008) with
band +0.0097, `rrect-md` 0.9553 (+0.0010) with band +0.0112, `glass-over-glass` 0.9139
(+0.0031) with band +0.0136, and `ssimInterior` on `rrect-md` −0.0091. The dark bed is 13
cells and carries no `rrect-ml` or `rrect-lg` checkerboard cell, so it does not test the
span law where the light bed fails; its improvement should not be read as evidence for the
form.

### The nulls (S5)

The solids, the impulse cells, every tinted cell and every `photo` cell move by **0.0001 or
less** in every metric at every scale and in both schemes, which is S5's first clause met
outright: the ramp is invisible where there is no backdrop structure for the sharp term to
carry. `ssimOutside` is **not** a clean null: it moves by more than S5's 0.001 on five
light-scheme cells — 2x `rrect-lg` −0.0029, 2x `rrect-md` and `rrect-ml` −0.0016, 1x
`rrect-lg` −0.0013, 1x `hc-text__rrect-md` −0.0015 — all inside the 24 CSS px exterior ring
where the lens's refraction of the checker still lands. Small, one-sided and worth naming
in the declaration rather than absorbing.

## 7. What this asks of the declaration

Three findings the parent's declaration has to answer, stated as this instrument found
them and not as a proposal:

1. **The form as implemented cannot meet S2, S3 or S4 at any point, at either scale**, and
   the reason is that its projected span law is far weaker than the one it retires (§4).
   The stops are not close: S3's best is 3× its tolerance, S2's best is 0.0057 short at 2x
   on the calibration cell and 0.0101–0.0222 short on the holdout rows.
2. **The 2x interior the device-pixel widths won is spent by the ramp.** §5.58 §2's
   widths-only reading is the best 2x `interiorStdDev` on record and every ramp point is
   worse. If S3 is the stop it says it is, the ramp needs a form that leaves the deep
   interior where the widths put it.
3. **The declared alternative already in W13's Risks — "a ramp with a floor" — is the shape
   the data asks for**, in a specific sense the sweep can name: the ramp's *deep* value
   wants to be the span-graded heavy share the retired law supplied, not zero, while its
   *near-contour excursion* wants to be the sharp term the band asks for. The four constants
   in the branch cannot express that (their deep value is forced to 1 − max(0, s₀ − u/U),
   which reaches 1 at every span at the same absolute depth), so no sweep of them can find
   it. Whether that is one more constant on the ramp's floor or the retired span law kept
   underneath the ramp is a declaration question, not a fitting one.

The recommended constants stand as the best the declared four can do and as the numbers the
declaration's twelve-row prediction should be written from if the form is declared as-is:
`sizeScatterRampStart1x` 0.60, `sizeScatterRampStart2x` 0.55, `sizeScatterRampReach1xPx`
200, `sizeScatterRampReach2xPx` 200.
