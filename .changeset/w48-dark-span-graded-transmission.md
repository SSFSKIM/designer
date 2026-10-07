---
"@vitreajs/vitrea-web": minor
---

Refit the macOS 27 clearer glass's dark body (`macos27Glass025MaterialProfileDocument`, the Glass
slider's 0.25, dark scheme), so a thin dark surface lets more of its backdrop's structure through
while a large one stays as dense as Apple's. The default material (the slider's 0.5), the selectable
macOS 26.5 material and the 0.25 light material draw exactly what they drew in 0.27.0.

Two material leaves now take effect. Both landed in 0.27.0's source at their identity:
- **`tintAlphaFar1x` / `tintAlphaFar2x`, the span-graded transmission.** They grade the body's base
  transmission by the surface's span, on the curve the scatter's far ramp already follows:
  `clamp(tintAlpha + rampAtScale(tintAlphaFar1x, tintAlphaFar2x, dpr) · farS, 0, 1)`. The WebGPU tier
  reads it per pixel, before the occlusion term the tone solve reads; the CSS tier mirrors it per
  surface. Identity 0. Every document except the dark 0.25 pair leaves both at 0, so no other
  fingerprint moves.
- **`sizeFineTapShare` with `sizeFineTapSigma` / `sizeFineTapSigma2x`, the receded fine-body tap.**
  Still 0 in every document: the refit found it improved nothing on top of the receded scatter it
  chose, so it ships inert and unfitted.

The dark 0.25 documents move:
- **Active:** `optics.regular.tintAlpha` 0.9 → 0.7, `tintAlphaFar1x` / `…2x` 0 → 0.2,
  `sizeScatterSpanMax` / `…2x` 256 → 160 (a surface at span 160 or more is drawn at 0.9, as before),
  and `sizeScatterScaleGain` −2 → −0.5. `sizeOcclusionGain`, `sizeScatterFloor2x` and the thin ramp
  starts are now named at their inherited values.
- **Receded difference:** `tintAlpha` 0.89 → 0.8; the receded scatter refitted (`sizeScatterFloor`
  0.5, `sizeScatterScaleGain` 0, `sizeScatterRampStartThin1x` / `…2x` 1 → 0.4,
  `sizeScatterRampStartThick1x` 0.3 → 0.15); and the second heavy blur tap at share 0.25 with widths
  5 / 5 CSS px. The CSS tier declines that tap, as it does the light receded document's.

The fingerprints are `791cde91d97acbc7` (dark active, from `b074fc6913a91c66`) and
`be472bc8e42b618d` (dark receded, from `280f0fddf014e0f6`). The light pair stays at
`3741b22934f17f4d` / `c4ca0e1cd6791bde`.

What the refit gains. These are measured on the WebGPU tier against Apple's own dark 0.25 render
over all 77 structured cells per scale, the holdout included (T1, the body's texture statistic;
fidelity claims §5.213):
- the coarse checkers' error at rest halves: 0.39 → 0.19 (1x) and 0.51 → 0.20 (2x);
- the receded fine checkers' halves at 1x (0.87 → 0.38), and falls at 2x (0.94 → 0.54);
- the photo's falls, 1.10 → 0.76 and 1.12 → 0.72, but does not halve. The dark photo body is still
  flatter than Apple's;
- the body's level holds (worst error 0.0505 against the 0.055 bound) and the exterior's shape is
  unchanged.

It ships with its exceptions named rather than gated, by the user's ruling (fidelity claims §5.213,
§5.214):
- **Seventeen cells whose texture error grew by more than one code against 0.27.0** (1x / 2x,
  codes of linear-light texture SD at Apple's level):
  - the receded thick coarse checkers: `checkerboard-64__rrect-lg__inactive` 8.94 / 12.53 and
    `checkerboard-32__rrect-lg__inactive` 3.20 / 6.04;
  - the receded thick photo, `photo__rrect-lg__inactive`, 2.64 / 2.90;
  - the thick and mid-span coarse checkers at rest: `checkerboard-32__rrect-lg__rest` 2.98 / 2.71,
    `checkerboard-lc16__rrect-md__rest` 2.66 / 2.91, `checkerboard-64__rrect-lg__rest` 1.55 / 1.71;
  - `hc-text-28__rrect-lg__rest`, 1.39 / 1.34;
  - `impulse__capsule-button__rest` 2.26 at 1x;
  - the receded `checkerboard__capsule-button` 2.79 and its orange tint 1.93, at 2x.
- **The photo texture at both scales and the receded fine checkers at 2x**: they did not halve.
- **The CSS tier**: two of the five structured dark holdout cells per scale draw their texture
  slightly farther from Apple's, and the dark holdout photo panel's colour error grows slightly at
  both scales.

By eye, the receded `checkerboard-32` and `checkerboard-64` panels at `rrect-lg` draw nearly
uniform, where Apple's keep a blurred checker. The next operator is a span-graded receded scatter.
