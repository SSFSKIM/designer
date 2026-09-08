---
"@vitreajs/vitrea-web": minor
---

Surfaces at rest stop shimmering, and glass over glass sees the glass beneath it.

**The band at rest is gone.** The highlight pass draws the specular sweep as a
band in the rim's angular coordinate, and that coordinate covers the whole
contour — so its idle phase, 0, is not "nowhere", it is the left edge. Nothing in
v1 ever drove the phase, so every resting surface has been carrying a bright
vertical band on its left side since the pass landed. The band is now gated on an
amplitude instead: `--vitrea-shimmer` joins `--vitrea-sweep` in the channel
vocabulary, is 0 on an undriven surface, and multiplies the sweep's gain, so at
rest the term is exactly zero and the pass writes nothing. A surface whose
shimmer a driver does raise still draws the band at the driven phase. On the
calibration bed the left edge of every dark solid dropped by 0.119–0.145 to meet
its own right edge, and two cells that had missed the rim clause since the dark
scheme landed now meet it at both scales (claims §5.94).

**The light material's rim specular is fitted to 0** (claims §5.96).
`optics.regular.specularGain` was 0.55, fitted three times over across three
waves with the resting band present — and the band was its horizontal signature.
Read per side with the band gone, Apple's light rim is left-equals-right to
0.0002, and eleven of twenty contrast rows on the untinted solids separate the
constant and every one of them minimises at 0. The rim vitrea draws is now the
ambient one alone on both tiers: the CSS tier derives its interior level from the
same term, so its body lightens by 0.0013–0.0053 depending on span and its light
calibration ΔE improves at both scales.

**A group stacked over other glass is handed that glass's tone.** A group whose
backdrop proxy resolved to another vitrea surface's output was getting no
backdrop tone at all, so the tone response never ran on it and an overlay pane
came out a flat mid grey — lighter than the pane beneath it where the reference
draws it darker. Such a group now takes the composite tone of the glass it sits
on, by containment of visible extents, one hop, the author's tint included. The
overlay of a nested pane lands within 0.0021–0.0040 of the reference's own
excess over its base, in both colour schemes and on both tiers, where it sat
0.028 the wrong side of it (claims §5.95).

Nothing here is an API you have to adopt: the shimmer channel is read if you
write it and ignored if you do not, and the material and sampling changes are the
runtime's own defaults moving toward the numbers Apple's renderer produces.
