cells: 0.3.0 bed 230  G2 230  G2b 115 (webgpu only)
  webgpu cells in G2 missing from G2b: [] (0); extra in G2b: 0


######## AGAINST THE G2 LANDING (ω 0.6) — the A/B ########

== class summary (max |Δ| over cells): class, tier, n, ΔSSIM, Δ(ΔE mean), Δ(ΔE p95), Δlevel
  checkerboard  webgpu  n= 31  ΔSSIM 0.0019  ΔΔE 0.0002  ΔΔEp95 0.0000  Δlevel 0.0001
  hc-text       webgpu  n=  8  ΔSSIM 0.0055  ΔΔE 0.0004  ΔΔEp95 0.0000  Δlevel 0.0007
  impulse       webgpu  n=  8  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0001
  photo         webgpu  n= 42  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0007  Δlevel 0.0001
  solid         webgpu  n= 26  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000

== cells with |ΔSSIM| > 0.005 (profile, renderer, scene: before → after)
  apple-macos-26.5-1x-light-standard           webgpu hc-text__rrect-md__rest                        0.9815 → 0.9760 (-0.0055)

== worst movers on the other axes (top 5 by |Δ| each)
  ΔE mean         hc-text__rrect-md__rest@-1x-light-standard=+0.0004; hc-text__rrect-md__rest@-2x-light-standard=+0.0003; checkerboard__rrect-md__rest@-1x-light-standard=+0.0002; checkerboard__rrect-md__rest@-2x-light-standard=+0.0002; checkerboard__rrect-ml__rest@-2x-light-standard=+0.0002
  ΔE p95          photo__glass-over-glass__rest@-1x-light-standard=-0.0007; photo__glass-over-glass__rest@-2x-light-standard=-0.0007; photo__rrect-ml__rest@-2x-light-standard=-0.0005; photo__rrect-ml__rest@-1x-light-standard=-0.0004; photo__rrect-lg__rest@-2x-light-standard=-0.0002
  interior level  hc-text__rrect-md__rest@-2x-light-standard=-0.0007; hc-text__rrect-md__rest@-1x-light-standard=-0.0007; checkerboard__rrect-md__rest@-2x-light-standard=-0.0001; checkerboard__rrect-md__rest@-1x-light-standard=-0.0001; impulse__rrect-md__rest@-2x-light-standard=+0.0001
  silhouette IoU  hc-text__rrect-md__rest@-2x-light-standard=+0.0004; checkerboard__glass-over-glass__rest@-1x-light-standard=-0.0003; checkerboard__rrect-ml__rest@-1x-light-standard=-0.0002; checkerboard__rrect-lg__rest@-1x-light-standard=-0.0002; checkerboard__glass-over-glass__rest@-2x-light-standard=-0.0002
  contour p95     checkerboard__glass-over-glass__rest@-1x-light-standard=+1.0000; checkerboard__rrect-lg__rest@-1x-light-standard=+1.0000; checkerboard__rrect-ml__rest@-1x-light-standard=+1.0000; hc-text__rrect-md__rest@-2x-light-standard=-0.4142; checkerboard__capsule-button__rest@-1x-dark-standard=+0.0000

== checkerboard texture rows, G2 (ω 0.6) → G2b (webgpu, light standard)
  1x rrect-sm          0.9988 → 0.9988  (+0.0000)
  1x capsule-button    0.9852 → 0.9852  (+0.0000)
  1x rrect-md          0.9709 → 0.9695  (-0.0013)
  1x rrect-ml          0.9498 → 0.9482  (-0.0015)
  1x rrect-lg          0.9442 → 0.9428  (-0.0014)
  1x glass-over-glass  0.9539 → 0.9521  (-0.0019)
  1x toolbar-group     0.9643 → 0.9643  (+0.0000)
  2x rrect-sm          0.9978 → 0.9978  (+0.0000)
  2x capsule-button    0.9836 → 0.9836  (+0.0000)
  2x rrect-md          0.9521 → 0.9517  (-0.0004)
  2x rrect-ml          0.9164 → 0.9158  (-0.0006)
  2x rrect-lg          0.9116 → 0.9113  (-0.0003)
  2x glass-over-glass  0.9221 → 0.9211  (-0.0009)
  2x toolbar-group     0.9663 → 0.9663  (+0.0000)

== captures: max code-value delta per class, and the CSS tier
  checkerboard  webgpu n= 31 changed= 14 max code value=29
  hc-text       webgpu n=  8 changed=  2 max code value=29
  impulse       webgpu n=  8 changed=  2 max code value=3
  photo         webgpu n= 42 changed= 20 max code value=7
  solid         webgpu n= 26 changed=  0 max code value=0
  solid GPU captures that differ by > 1: []
  CSS tier: not re-captured this round — no lens on that tier by contract; the G2 referee proved it byte-stable under the far larger G2 lens change.


######## AGAINST THE 0.3.0 BED — the W12 stops of claims §5.51 §3 ########

== class summary (max |Δ| over cells): class, tier, n, ΔSSIM, Δ(ΔE mean), Δ(ΔE p95), Δlevel
  checkerboard  webgpu  n= 31  ΔSSIM 0.0175  ΔΔE 0.0013  ΔΔEp95 0.0064  Δlevel 0.0005
  hc-text       webgpu  n=  8  ΔSSIM 0.0147  ΔΔE 0.0006  ΔΔEp95 0.0019  Δlevel 0.0232
  impulse       webgpu  n=  8  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0005
  photo         webgpu  n= 42  ΔSSIM 0.0002  ΔΔE 0.0001  ΔΔEp95 0.0017  Δlevel 0.0006
  solid         webgpu  n= 26  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000

== cells with |ΔSSIM| > 0.005 (profile, renderer, scene: before → after)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-ml__rest                   0.9307 → 0.9482 (+0.0175)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__glass-over-glass__rest           0.9345 → 0.9521 (+0.0175)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-md__rest                   0.9538 → 0.9695 (+0.0157)
  apple-macos-26.5-1x-light-standard           webgpu hc-text__rrect-md__rest                        0.9613 → 0.9760 (+0.0147)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-lg__rest                   0.9286 → 0.9428 (+0.0142)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__glass-over-glass__rest           0.9076 → 0.9211 (+0.0135)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-ml__rest                   0.9023 → 0.9158 (+0.0135)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-md__rest                   0.9389 → 0.9517 (+0.0127)
  apple-macos-26.5-1x-light-standard           webgpu hc-text__capsule-button__rest                  0.9729 → 0.9845 (+0.0117)
  apple-macos-26.5-2x-light-standard           webgpu hc-text__capsule-button__rest                  0.9738 → 0.9839 (+0.0101)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-lg__rest                   0.9013 → 0.9113 (+0.0100)
  apple-macos-26.5-2x-light-standard           webgpu hc-text__rrect-md__rest                        0.9550 → 0.9648 (+0.0099)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__capsule-button__rest             0.9770 → 0.9852 (+0.0082)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__capsule-button__rest             0.9777 → 0.9836 (+0.0059)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__toolbar-group__rest              0.9591 → 0.9643 (+0.0052)

== worst movers on the other axes (top 5 by |Δ| each)
  ΔE mean         checkerboard__glass-over-glass__rest@-1x-light-standard=-0.0013; checkerboard__glass-over-glass__rest@-2x-light-standard=-0.0013; checkerboard__rrect-ml__rest@-2x-light-standard=-0.0011; checkerboard__rrect-ml__rest@-1x-light-standard=-0.0011; checkerboard__rrect-md__rest@-1x-light-standard=-0.0010
  ΔE p95          checkerboard__capsule-button__rest@-2x-light-standard=-0.0064; checkerboard__rrect-md__rest@-2x-dark-standard=-0.0040; checkerboard__capsule-button__rest@-1x-light-standard=-0.0038; checkerboard__toolbar-group__rest@-2x-light-standard=-0.0031; checkerboard__toolbar-group__rest@-1x-light-standard=-0.0027
  interior level  hc-text__capsule-button__rest@-2x-light-standard=+0.0232; hc-text__capsule-button__rest@-1x-light-standard=+0.0231; hc-text__capsule-button__rest-tint-orange@-1x-light-standard=+0.0052; hc-text__capsule-button__rest-tint-orange@-2x-light-standard=+0.0048; hc-text__rrect-md__rest@-1x-light-standard=+0.0028
  silhouette IoU  hc-text__capsule-button__rest@-1x-light-standard=+0.0177; hc-text__capsule-button__rest@-2x-light-standard=+0.0090; hc-text__rrect-md__rest@-1x-light-standard=-0.0065; checkerboard__rrect-md__rest@-1x-light-standard=+0.0020; hc-text__rrect-md__rest@-2x-light-standard=+0.0014
  contour p95     hc-text__capsule-button__rest@-1x-light-standard=-1.0000; hc-text__rrect-md__rest@-2x-light-standard=-1.0000; checkerboard__capsule-button__rest@-1x-dark-standard=+0.0000; checkerboard__capsule-button__rest-tint-orange@-1x-dark-standard=+0.0000; checkerboard__glass-over-glass__rest@-1x-dark-standard=+0.0000

== checkerboard texture rows, 0.3.0 bed → G2b (webgpu, light standard)
  1x rrect-sm          0.9981 → 0.9988  (+0.0007)
  1x capsule-button    0.9770 → 0.9852  (+0.0082)
  1x rrect-md          0.9538 → 0.9695  (+0.0157)
  1x rrect-ml          0.9307 → 0.9482  (+0.0175)
  1x rrect-lg          0.9286 → 0.9428  (+0.0142)
  1x glass-over-glass  0.9345 → 0.9521  (+0.0175)
  1x toolbar-group     0.9591 → 0.9643  (+0.0052)
  2x rrect-sm          0.9969 → 0.9978  (+0.0009)
  2x capsule-button    0.9777 → 0.9836  (+0.0059)
  2x rrect-md          0.9389 → 0.9517  (+0.0127)
  2x rrect-ml          0.9023 → 0.9158  (+0.0135)
  2x rrect-lg          0.9013 → 0.9113  (+0.0100)
  2x glass-over-glass  0.9076 → 0.9211  (+0.0135)
  2x toolbar-group     0.9630 → 0.9663  (+0.0033)

== STOP: small-span texture cells below their 0.3.0 SSIM by more than 0.005
  (none)

== STOP: any 1x row below its G2-landing SSIM by more than 0.002
  BELOW ('apple-macos-26.5-1x-light-standard', 'webgpu', 'hc-text__rrect-md__rest') 0.9815 → 0.9760

  (done)

== adopted-bound enforcement (hand note, not scan output)
`test/adopted-thresholds.test.ts` was run against `matrix-g2b-merged.json` (this round's webgpu
rows over the G2 landing's CSS rows, built by `g2b-merge.py`); the log is
`g2b-adopted-thresholds.txt`. 23 of 27 assertions pass, including every adopted bound and every
regression floor. The four failures are all the same self-consistency cross-check on
`checkerboard__glass-over-glass` — "the recorded GPU-over-CSS interior-level ratio must equal the
two tiers' own levels, divided" — and they are an artefact of the merge: the ratio each webgpu row
recorded was divided by the CSS level of ITS OWN run, while the merged bed carries the G2 run's CSS
row, whose level differs in the fifth decimal (1e-5 capture noise on the DOM proxy). No bound and
no floor moved. A whole twelve-run rebuild would remove the artefact; this round did not run the
CSS tier because it has no lens.
