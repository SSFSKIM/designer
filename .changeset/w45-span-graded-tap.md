---
"@vitreajs/vitrea-web": minor
---

Refit the macOS 27 clearer glass (`macos27Glass025MaterialProfileDocument`, the Glass slider's 0.25)
at Retina scale, so its light body passes a backdrop's fine structure closer to the way Apple's
does. The default material (the slider's 0.5), the selectable macOS 26.5 material, the 0.25 dark
material and every 1x surface draw exactly what they drew in 0.26.0.

A new material leaf, `sizeHeavySecondShareFar2x`, grades the second heavy blur tap's share by the
surface's span, per pixel, on the curve the scatter's far ramp already follows. Apple's material
passes a 16-device-pixel checker heavily at span 96 and barely at 128–160, where vitrea's tap had
one share at every span. The leaf is signed, unclamped and 0 by default. It reads only where
`sizeHeavySecondShare` opens the second tap, it is 0 at 1x by construction, and the CSS tier
declines it with the tap. Every document except the 0.25 light pair leaves it at 0, so no other
fingerprint moves.

The light 0.25 documents move, at 2x:
- **Active:** `sizeScatterFloor2x` 0.6 → 1, `sizeScatterSpanMax2x` 256 → 128,
  `sizeHeavySecondShare` 0 → 0.5 with `sizeHeavySecondSigma2x` 0 → 2 CSS px,
  `sizeHeavySecondShareFar2x` −0.25, and `sizeScatterRampStartThin2x` 0.46 → 0.65.
- **Receded difference:** `sizeScatterRampStartThin2x` 0.7 → 0.1, `sizeScatterRampStartThick2x`
  and `sizeScatterRampStartFar2x` 0.04 → 0, `sizeHeavyTapSigma2x` 14 → 18, and the share 0.25 and
  `sizeHeavySecondShareFar2x` −0.125, named for the first time.

The fingerprints are `3741b22934f17f4d` (light active, from `50430fa62c1120bd`) and
`c4ca0e1cd6791bde` (light receded, from `5d8680980b7aeb55`). The dark pair stays at
`b074fc6913a91c66` / `280f0fddf014e0f6`.

The CSS tier keeps `sizeScatterFloor2x` 0.6 and `sizeScatterSpanMax2x` 256 for the light 0.25
document. It draws no second tap, so moving those two leaves alone washed out its 2x coarse
checkers. With the hold, one 2x CSS cell of 94 grows its texture error by more than one code
against 0.26.0. An app that sets either leaf to a value of its own still gets that value on both
tiers.

What the refit gains, measured on the WebGPU tier against Apple's own 0.25 render at 2x, over the
94 cells the fit never held out (T1, the body's texture statistic, fidelity claims §5.206):
- the fine-checker stratum's error falls from 0.6462 to 0.2190, below half;
- the coarse checkers' error falls from 0.1720 to 0.0810 (rest) and from 0.8523 to 0.1829
  (receded);
- the fine text's falls from 0.5251 to 0.2365, and the photo's at rest from 0.4193 to 0.3902.

Four fine checkers that missed Apple's texture in 0.26.0 now match it, among them
`checkerboard-8__rrect-md__rest`, the cell the leaf exists for. Of the 116 structured cells per
scale, 157 of 232 still miss and are named.

It ships with its exceptions named rather than gated, by the user's ruling (claims §5.206 §16,
§5.207):
- **Eleven cells whose texture error grew by more than one code against 0.26.0:**
  - the pressed `checkerboard` rrect-md and capsule, 4.27 and 4.25;
  - `checkerboard-32` at the thin and thick spans, 4.18 and 3.34;
  - `checkerboard__rrect-lg__rest`, 3.30;
  - `checkerboard-64__rrect-sm__rest`, 2.22;
  - the receded `hc-text-7` rrect-md, 1.60 on its low band;
  - `checkerboard__glass-over-glass__rest`, 1.57;
  - `checkerboard-8__rrect-lg__rest`, 1.55;
  - the receded `hc-text` rrect-lg, 1.40;
  - the receded photo toolbar group, 1.02.

  The growths are in codes of linear-light texture SD at Apple's level. Five are past three
  codes.
- **The receded photo's structure**: M2 reads four receded photo cells moving away from Apple's
  texture (−4.5 % to −15.0 %). Read on finer bands, the same cells move toward Apple: the
  backdrop's lattice comes off.
- **The receded photo's aggregate texture**, 0.1937 against a bound of 0.1871.

The fine checkers at span 160 still draw more structure than Apple's (`checkerboard-8` ×2.6 at
`rrect-lg`). Apple's narrow term also widens with the span, which a share alone cannot follow.
