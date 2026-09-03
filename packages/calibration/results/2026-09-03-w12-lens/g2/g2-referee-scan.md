cells: old 230 new 230; missing in new: [] (0); extra: 0

== class summary (max |Δ| over cells): class, tier, n, ΔSSIM, Δ(ΔE mean), Δ(ΔE p95), Δlevel
  checkerboard  css     n= 31  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  checkerboard  webgpu  n= 31  ΔSSIM 0.0194  ΔΔE 0.0015  ΔΔEp95 0.0064  Δlevel 0.0005
  hc-text       css     n=  8  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  hc-text       webgpu  n=  8  ΔSSIM 0.0202  ΔΔE 0.0009  ΔΔEp95 0.0019  Δlevel 0.0232
  impulse       css     n=  8  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  impulse       webgpu  n=  8  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0004
  photo         css     n= 42  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  photo         webgpu  n= 42  ΔSSIM 0.0003  ΔΔE 0.0001  ΔΔEp95 0.0010  Δlevel 0.0006
  solid         css     n= 26  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000
  solid         webgpu  n= 26  ΔSSIM 0.0000  ΔΔE 0.0000  ΔΔEp95 0.0000  Δlevel 0.0000

== cells with |ΔSSIM| > 0.005 (profile, renderer, scene: before → after)
  apple-macos-26.5-1x-light-standard           webgpu hc-text__rrect-md__rest                        0.9613 → 0.9815 (+0.0202)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__glass-over-glass__rest           0.9345 → 0.9539 (+0.0194)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-ml__rest                   0.9307 → 0.9498 (+0.0191)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-md__rest                   0.9538 → 0.9709 (+0.0171)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__rrect-lg__rest                   0.9286 → 0.9442 (+0.0156)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__glass-over-glass__rest           0.9076 → 0.9221 (+0.0145)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-ml__rest                   0.9023 → 0.9164 (+0.0141)
  apple-macos-26.5-2x-light-standard           webgpu hc-text__rrect-md__rest                        0.9550 → 0.9682 (+0.0133)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-md__rest                   0.9389 → 0.9521 (+0.0131)
  apple-macos-26.5-1x-light-standard           webgpu hc-text__capsule-button__rest                  0.9729 → 0.9845 (+0.0117)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__rrect-lg__rest                   0.9013 → 0.9116 (+0.0103)
  apple-macos-26.5-2x-light-standard           webgpu hc-text__capsule-button__rest                  0.9738 → 0.9839 (+0.0101)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__capsule-button__rest             0.9770 → 0.9852 (+0.0082)
  apple-macos-26.5-2x-light-standard           webgpu checkerboard__capsule-button__rest             0.9777 → 0.9836 (+0.0059)
  apple-macos-26.5-1x-light-standard           webgpu checkerboard__toolbar-group__rest              0.9591 → 0.9643 (+0.0052)

== checkerboard texture rows before → after (prediction)
  1x rrect-sm          0.9981 → 0.9988   predicted —
  1x capsule-button    0.9770 → 0.9852   predicted 0.985
  1x rrect-md          0.9538 → 0.9709   predicted 0.97
  1x rrect-ml          0.9307 → 0.9498   predicted 0.946
  1x rrect-lg          0.9286 → 0.9442   predicted 0.942
  1x glass-over-glass  0.9345 → 0.9539   predicted —
  1x toolbar-group     0.9591 → 0.9643   predicted —
  2x rrect-sm          0.9969 → 0.9978   predicted —
  2x capsule-button    0.9777 → 0.9836   predicted 0.983
  2x rrect-md          0.9389 → 0.9521   predicted 0.95
  2x rrect-ml          0.9023 → 0.9164   predicted 0.918
  2x rrect-lg          0.9013 → 0.9116   predicted 0.918
  2x glass-over-glass  0.9076 → 0.9221   predicted —
  2x toolbar-group     0.9630 → 0.9663   predicted —

== captures: max code-value delta per class/renderer, and CSS identity
  checkerboard  css    n= 31 changed=  0 max code value=0
  checkerboard  webgpu n= 31 changed= 29 max code value=45
  hc-text       css    n=  8 changed=  0 max code value=0
  hc-text       webgpu n=  8 changed=  8 max code value=40
  impulse       css    n=  8 changed=  0 max code value=0
  impulse       webgpu n=  8 changed=  2 max code value=17
  photo         css    n= 42 changed=  0 max code value=0
  photo         webgpu n= 42 changed= 40 max code value=15
  solid         css    n= 26 changed=  0 max code value=0
  solid         webgpu n= 26 changed=  1 max code value=1
  CSS captures that differ: []
  solid GPU captures that differ by > 1: []

== small-span texture rows (stop: below the 0.3.0 SSIM by > 0.005)
  (done)
