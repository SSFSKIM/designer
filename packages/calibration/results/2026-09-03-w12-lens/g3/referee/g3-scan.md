cells: 0.3.0 bed 230  main 230  G3 230
  rows on main missing from G3: 0 []
  rows in G3 not on main: 0


######## AGAINST THE MATERIAL ON main (webgpu ω 0.8, css G2) ########

== class summary (max |Δ| over cells): class, tier, n, ΔSSIM, Δ(ΔE mean), Δ(ΔE p95), Δlevel
  checkerboard  css     n= 31  ΔSSIM 0.0045  ΔΔE 0.0009  ΔΔEp95 0.0097  Δlevel 0.0036
  checkerboard  webgpu  n= 31  ΔSSIM 0.0122  ΔΔE 0.0046  ΔΔEp95 0.0072  Δlevel 0.0006
  hc-text       css     n=  8  ΔSSIM 0.0065  ΔΔE 0.0009  ΔΔEp95 0.0031  Δlevel 0.0028
  hc-text       webgpu  n=  8  ΔSSIM 0.0020  ΔΔE 0.0012  ΔΔEp95 0.0152  Δlevel 0.0061
  impulse       css     n=  8  ΔSSIM 0.0001  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  impulse       webgpu  n=  8  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  photo         css     n= 42  ΔSSIM 0.0001  ΔΔE 0.0002  ΔΔEp95 0.0009  Δlevel 0.0007
  photo         webgpu  n= 42  ΔSSIM 0.0001  ΔΔE 0.0006  ΔΔEp95 0.0015  Δlevel 0.0012
  solid         css     n= 26  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  solid         webgpu  n= 26  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000

== cells with |ΔSSIM| > 0.005 (profile, renderer, scene: before → after)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__glass-over-glass__rest           0.9211 → 0.9090 (-0.0122)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-ml__rest                   0.9158 → 0.9041 (-0.0117)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-md__rest                   0.9517 → 0.9451 (-0.0066)
  apple-macos-26.5-2x-light-standard           css    hc-text__rrect-md__rest                        0.9391 → 0.9456 (+0.0065)
  apple-macos-26.5-2x-dark-standard            webgpu checkerboard__glass-over-glass__rest           0.9108 → 0.9057 (-0.0051)
  [5 cell(s) past 0.005]

== worst movers on the other axes (top 5 by |Δ| each)
  ΔE mean         checkerboard__rrect-ml__rest@-2x-light-standard=+0.0046; checkerboard__glass-over-glass__rest@-2x-light-standard=+0.0041; checkerboard__rrect-md__rest@-2x-light-standard=+0.0025; checkerboard__rrect-lg__rest@-2x-light-standard=+0.0024; hc-text__rrect-md__rest@-2x-light-standard=+0.0012
  ΔE p95          hc-text__capsule-button__rest@-2x-light-standard=-0.0152; checkerboard__capsule-button__rest@-2x-light-standard=-0.0097; checkerboard__toolbar-group__rest@-2x-light-standard=-0.0081; checkerboard__rrect-md__rest@-2x-dark-standard=+0.0072; checkerboard__glass-over-glass__rest@-2x-light-standard=+0.0064
  interior level  hc-text__rrect-md__rest@-2x-light-standard=+0.0061; checkerboard__capsule-button__rest@-2x-light-standard=+0.0036; checkerboard__toolbar-group__rest@-2x-light-standard=+0.0034; checkerboard__rrect-md__rest@-2x-light-standard=+0.0033; checkerboard__rrect-sm__rest@-2x-light-standard=+0.0033
  silhouette IoU  checkerboard__rrect-md__rest@-2x-light-standard=-0.0008; checkerboard__capsule-button__rest@-2x-light-standard=-0.0007; checkerboard__rrect-sm__rest@-2x-light-standard=-0.0005; checkerboard__rrect-ml__rest@-2x-light-standard=-0.0005; checkerboard__toolbar-group__rest@-2x-light-standard=-0.0005
  contour p95     checkerboard__capsule-button__rest@-2x-light-standard=+1.0000; checkerboard__rrect-sm__rest@-2x-light-standard=+1.0000; checkerboard__capsule-button__rest@-1x-dark-standard=+0.0000; checkerboard__capsule-button__rest-tint-orange@-1x-dark-standard=+0.0000; checkerboard__glass-over-glass__rest@-1x-dark-standard=+0.0000

== checkerboard texture rows, main → G3 (webgpu, light standard)
  1x rrect-sm          0.9988 → 0.9988  (+0.0000)
  1x capsule-button    0.9852 → 0.9852  (+0.0000)
  1x rrect-md          0.9695 → 0.9695  (+0.0000)
  1x rrect-ml          0.9482 → 0.9482  (+0.0000)
  1x rrect-lg          0.9428 → 0.9428  (+0.0000)
  1x glass-over-glass  0.9521 → 0.9521  (+0.0000)
  1x toolbar-group     0.9643 → 0.9643  (+0.0000)
  2x rrect-sm          0.9978 → 0.9975  (-0.0003)
  2x capsule-button    0.9836 → 0.9830  (-0.0006)
  2x rrect-md          0.9517 → 0.9451  (-0.0066)
  2x rrect-ml          0.9158 → 0.9041  (-0.0117)
  2x rrect-lg          0.9113 → 0.9078  (-0.0034)
  2x glass-over-glass  0.9211 → 0.9090  (-0.0122)
  2x toolbar-group     0.9663 → 0.9664  (+0.0001)

== checkerboard texture rows, main → G3 (css, light standard)
  1x rrect-sm          0.9853 → 0.9853  (+0.0000)
  1x capsule-button    0.9612 → 0.9612  (+0.0000)
  1x rrect-md          0.8963 → 0.8963  (+0.0000)
  1x rrect-ml          0.8481 → 0.8481  (+0.0000)
  1x rrect-lg          0.8372 → 0.8372  (+0.0000)
  1x glass-over-glass  0.8499 → 0.8499  (+0.0000)
  1x toolbar-group     0.9576 → 0.9576  (+0.0000)
  2x rrect-sm          0.9883 → 0.9882  (-0.0002)
  2x capsule-button    0.9705 → 0.9708  (+0.0003)
  2x rrect-md          0.9169 → 0.9164  (-0.0006)
  2x rrect-ml          0.8765 → 0.8810  (+0.0045)
  2x rrect-lg          0.8696 → 0.8720  (+0.0024)
  2x glass-over-glass  0.8687 → 0.8712  (+0.0025)
  2x toolbar-group     0.9656 → 0.9657  (+0.0001)

== photo rows at 2x, main → G3
  webgpu -2x-dark-standard                  photo__capsule-button__rest                  0.9860 → 0.9860 (+0.0000)
  webgpu -2x-dark-standard                  photo__capsule-button__rest-tint-orange      0.9898 → 0.9898 (+0.0000)
  webgpu -2x-dark-standard                  photo__rrect-lg__rest                        0.9610 → 0.9610 (+0.0001)
  webgpu -2x-dark-standard                  photo__rrect-md__rest                        0.9822 → 0.9822 (-0.0000)
  webgpu -2x-light-standard                 photo__capsule-button__rest                  0.9889 → 0.9888 (-0.0000)
  webgpu -2x-light-standard                 photo__capsule-button__rest-tint-blue        0.9889 → 0.9889 (-0.0000)
  webgpu -2x-light-standard                 photo__capsule-button__rest-tint-orange      0.9896 → 0.9896 (+0.0000)
  webgpu -2x-light-standard                 photo__capsule-button__rest-tint-orange-half 0.9891 → 0.9891 (-0.0000)
  webgpu -2x-light-standard                 photo__glass-over-glass__rest                0.9963 → 0.9963 (-0.0000)
  webgpu -2x-light-standard                 photo__rrect-lg__rest                        0.9959 → 0.9958 (-0.0000)
  webgpu -2x-light-standard                 photo__rrect-lg__rest-tint-orange            0.9951 → 0.9951 (-0.0000)
  webgpu -2x-light-standard                 photo__rrect-md__rest                        0.9981 → 0.9980 (-0.0000)
  webgpu -2x-light-standard                 photo__rrect-md__rest-tint-orange            0.9972 → 0.9972 (+0.0000)
  webgpu -2x-light-standard                 photo__rrect-ml__rest                        0.9968 → 0.9967 (-0.0001)
  webgpu -2x-light-standard                 photo__rrect-sm__rest                        0.9993 → 0.9993 (-0.0000)
  webgpu -2x-light-standard                 photo__toolbar-group__rest                   0.9698 → 0.9698 (-0.0000)
  css    -2x-dark-standard                  photo__capsule-button__rest                  0.9840 → 0.9840 (+0.0000)
  css    -2x-dark-standard                  photo__capsule-button__rest-tint-orange      0.9853 → 0.9853 (-0.0000)
  css    -2x-dark-standard                  photo__rrect-lg__rest                        0.9428 → 0.9428 (+0.0000)
  css    -2x-dark-standard                  photo__rrect-md__rest                        0.9712 → 0.9712 (+0.0000)
  css    -2x-light-standard                 photo__capsule-button__rest                  0.9836 → 0.9836 (-0.0000)
  css    -2x-light-standard                 photo__capsule-button__rest-tint-blue        0.9851 → 0.9851 (-0.0000)
  css    -2x-light-standard                 photo__capsule-button__rest-tint-orange      0.9845 → 0.9845 (-0.0000)
  css    -2x-light-standard                 photo__capsule-button__rest-tint-orange-half 0.9837 → 0.9837 (-0.0000)
  css    -2x-light-standard                 photo__glass-over-glass__rest                0.9508 → 0.9508 (+0.0000)
  css    -2x-light-standard                 photo__rrect-lg__rest                        0.9530 → 0.9529 (-0.0001)
  css    -2x-light-standard                 photo__rrect-lg__rest-tint-orange            0.9551 → 0.9551 (+0.0000)
  css    -2x-light-standard                 photo__rrect-md__rest                        0.9740 → 0.9740 (+0.0000)
  css    -2x-light-standard                 photo__rrect-md__rest-tint-orange            0.9753 → 0.9753 (+0.0000)
  css    -2x-light-standard                 photo__rrect-ml__rest                        0.9631 → 0.9631 (+0.0000)
  css    -2x-light-standard                 photo__rrect-sm__rest                        0.9902 → 0.9902 (-0.0000)
  css    -2x-light-standard                 photo__toolbar-group__rest                   0.9747 → 0.9746 (-0.0000)

== captures: max code-value delta per class, main → G3
  checkerboard  css    n= 31 changed= 13 max code value=20
  checkerboard  webgpu n= 31 changed= 12 max code value=10
  hc-text       css    n=  8 changed=  3 max code value=9
  hc-text       webgpu n=  8 changed=  3 max code value=16
  impulse       css    n=  8 changed=  1 max code value=4
  impulse       webgpu n=  8 changed=  1 max code value=9
  photo         css    n= 42 changed= 17 max code value=9
  photo         webgpu n= 42 changed= 15 max code value=5
  solid         css    n= 26 changed=  0 max code value=0
  solid         webgpu n= 26 changed=  6 max code value=1


######## AGAINST THE 0.3.0 BED — the W12 stops of claims §5.51 §3 ########

== class summary (max |Δ| over cells): class, tier, n, ΔSSIM, Δ(ΔE mean), Δ(ΔE p95), Δlevel
  checkerboard  css     n= 31  ΔSSIM 0.0045  ΔΔE 0.0009  ΔΔEp95 0.0097  Δlevel 0.0036
  checkerboard  webgpu  n= 31  ΔSSIM 0.0175  ΔΔE 0.0034  ΔΔEp95 0.0038  Δlevel 0.0006
  hc-text       css     n=  8  ΔSSIM 0.0065  ΔΔE 0.0009  ΔΔEp95 0.0031  Δlevel 0.0028
  hc-text       webgpu  n=  8  ΔSSIM 0.0147  ΔΔE 0.0006  ΔΔEp95 0.0157  Δlevel 0.0231
  impulse       css     n=  8  ΔSSIM 0.0001  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  impulse       webgpu  n=  8  ΔSSIM 0.0000  ΔΔE 0.0001  ΔΔEp95 0.0000  Δlevel 0.0005
  photo         css     n= 42  ΔSSIM 0.0001  ΔΔE 0.0002  ΔΔEp95 0.0009  Δlevel 0.0007
  photo         webgpu  n= 42  ΔSSIM 0.0002  ΔΔE 0.0007  ΔΔEp95 0.0026  Δlevel 0.0018
  solid         css     n= 26  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  solid         webgpu  n= 26  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000

== cells with |ΔSSIM| > 0.005 (profile, renderer, scene: before → after)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-ml__rest                   0.9307 → 0.9482 (+0.0175)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__glass-over-glass__rest           0.9345 → 0.9521 (+0.0175)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-md__rest                   0.9538 → 0.9695 (+0.0157)
  apple-macos-26.5-1x-light-standard           webgpu hc-text__rrect-md__rest                        0.9613 → 0.9760 (+0.0147)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-lg__rest                   0.9286 → 0.9428 (+0.0142)
  apple-macos-26.5-1x-light-standard           webgpu hc-text__capsule-button__rest                  0.9729 → 0.9845 (+0.0117)
  apple-macos-26.5-2x-light-standard           webgpu hc-text__capsule-button__rest                  0.9738 → 0.9820 (+0.0082)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__capsule-button__rest             0.9770 → 0.9852 (+0.0082)
  apple-macos-26.5-2x-light-standard           webgpu hc-text__rrect-md__rest                        0.9550 → 0.9630 (+0.0080)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-lg__rest                   0.9013 → 0.9078 (+0.0066)
  apple-macos-26.5-2x-light-standard           css    hc-text__rrect-md__rest                        0.9391 → 0.9456 (+0.0065)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-md__rest                   0.9389 → 0.9451 (+0.0062)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__capsule-button__rest             0.9777 → 0.9830 (+0.0053)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__toolbar-group__rest              0.9591 → 0.9643 (+0.0052)
  [14 cell(s) past 0.005]

== worst movers on the other axes (top 5 by |Δ| each)
  ΔE mean         checkerboard__rrect-ml__rest@-2x-light-standard=+0.0034; checkerboard__glass-over-glass__rest@-2x-light-standard=+0.0028; checkerboard__rrect-md__rest@-2x-light-standard=+0.0016; checkerboard__rrect-lg__rest@-2x-light-standard=+0.0015; checkerboard__glass-over-glass__rest@-1x-light-standard=-0.0013
  ΔE p95          hc-text__capsule-button__rest@-2x-light-standard=-0.0157; checkerboard__capsule-button__rest@-2x-light-standard=-0.0097; checkerboard__toolbar-group__rest@-2x-light-standard=-0.0081; checkerboard__glass-over-glass__rest@-2x-light-standard=+0.0064; checkerboard__capsule-button__rest@-1x-light-standard=-0.0038
  interior level  hc-text__capsule-button__rest@-1x-light-standard=+0.0231; hc-text__capsule-button__rest@-2x-light-standard=+0.0204; hc-text__rrect-md__rest@-2x-light-standard=+0.0086; hc-text__capsule-button__rest-tint-orange@-1x-light-standard=+0.0052; hc-text__capsule-button__rest-tint-orange@-2x-light-standard=+0.0044
  silhouette IoU  hc-text__capsule-button__rest@-1x-light-standard=+0.0177; hc-text__capsule-button__rest@-2x-light-standard=+0.0090; hc-text__rrect-md__rest@-1x-light-standard=-0.0065; checkerboard__rrect-md__rest@-1x-light-standard=+0.0020; hc-text__rrect-md__rest@-2x-light-standard=+0.0018
  contour p95     hc-text__capsule-button__rest@-1x-light-standard=-1.0000; checkerboard__capsule-button__rest@-2x-light-standard=+1.0000; checkerboard__rrect-sm__rest@-2x-light-standard=+1.0000; hc-text__rrect-md__rest@-2x-light-standard=-1.0000; checkerboard__capsule-button__rest@-1x-dark-standard=+0.0000

== checkerboard texture rows, 0.3.0 bed → G3 (webgpu, light standard)
  1x rrect-sm          0.9981 → 0.9988  (+0.0007)
  1x capsule-button    0.9770 → 0.9852  (+0.0082)
  1x rrect-md          0.9538 → 0.9695  (+0.0157)
  1x rrect-ml          0.9307 → 0.9482  (+0.0175)
  1x rrect-lg          0.9286 → 0.9428  (+0.0142)
  1x glass-over-glass  0.9345 → 0.9521  (+0.0175)
  1x toolbar-group     0.9591 → 0.9643  (+0.0052)
  2x rrect-sm          0.9969 → 0.9975  (+0.0006)
  2x capsule-button    0.9777 → 0.9830  (+0.0053)
  2x rrect-md          0.9389 → 0.9451  (+0.0062)
  2x rrect-ml          0.9023 → 0.9041  (+0.0017)
  2x rrect-lg          0.9013 → 0.9078  (+0.0066)
  2x glass-over-glass  0.9076 → 0.9090  (+0.0013)
  2x toolbar-group     0.9630 → 0.9664  (+0.0034)


######## THE SIX STOPS (claims §5.56 §4) ########

--- STOP 1: every cell past 0.005 against the 0.3.0 bed named; no bound or floor regressed; no solid capture differing by a code value at either scale
  cells past 0.005 against 0.3.0: 14 (named in the section above)
  solid captures differing by a code value: 6 [(('apple-macos-26.5-2x-dark-standard', 'webgpu', 'dark-solid__rrect-md__rest'), 1), (('apple-macos-26.5-2x-light-standard', 'webgpu', 'dark-solid__rrect-md__rest'), 1), (('apple-macos-26.5-2x-light-standard', 'webgpu', 'light-solid__capsule-button__rest'), 1), (('apple-macos-26.5-2x-light-standard', 'webgpu', 'light-solid__rrect-md__rest'), 1), (('apple-macos-26.5-2x-light-standard', 'webgpu', 'light-solid__rrect-ml__rest'), 1), (('apple-macos-26.5-2x-light-standard', 'webgpu', 'mid-dark-solid__capsule-button__rest'), 1)]
  (bounds and floors: see the adopted-thresholds run beside this file)

--- STOP 2: every 1x row within 0.002 of main, and predicted +0.0000
  1x rows compared: 132
  1x rows that moved AT ALL: 1; largest |ΔSSIM| 0.000000
    -1x-light-standard                 css    photo__capsule-button__rest-tint-orange-half 0.977243 → 0.977243 (+0.000000)  capture max code delta=1
  VERDICT: PASS — 0 row(s) past 0.002
  1x captures differing by a code value: 1 [(('apple-macos-26.5-1x-light-standard', 'css', 'photo__capsule-button__rest-tint-orange-half'), 1)]

--- STOP 3: the 2x GPU texture rows within ±0.003 of the prediction, none below main
  rrect-md  main 0.9517 → G3 0.9451  predicted 0.9545 (Δ -0.0094, within ±0.003 False); not below main False; clears 0.93 True
  rrect-ml  main 0.9158 → G3 0.9041  predicted 0.9219 (Δ -0.0178, within ±0.003 False); not below main False; clears 0.9013 True
  rrect-lg  main 0.9113 → G3 0.9078  predicted 0.9164 (Δ -0.0086, within ±0.003 False); not below main False; clears 0.9002 True
  VERDICT: FAIL

--- STOP 4: no 2x CSS row more than 0.002 below main
  VERDICT: PASS — 0 row(s) past 0.002 below
  the three named 2x CSS dom rows (predicted 0.9187 / 0.8795 / 0.8700):
    rrect-md  0.9169 → 0.9164 (-0.0006)
    rrect-ml  0.8765 → 0.8810 (+0.0045)
    rrect-lg  0.8696 → 0.8720 (+0.0024)

--- STOP 5: renderer goldens — see the golden run recorded in the round's report
--- STOP 6: by eye — the user's, on the sheets beside this file

  (done)
