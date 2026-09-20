---
"@vitreajs/vitrea-web": minor
---

Grade the outer shadow's blur by the casting surface, and condition the dark
material's diffusion on the backdrop it stands over.

macOS 27 blurs a surface's outer shadow wider under a wider surface. macOS 26.5
did not — its σ is constant within 15.4–15.9 CSS px from a 32 px control to a
160 px panel, which is a positive measurement and not an absence — so vitrea
carried one width and, on macOS 27, drew a small control's shadow about six times
too wide and a large panel's about a third too narrow. It now draws a line in the
caster's own span, held flat below a knee, evaluated per caster on both tiers:
the WebGPU tier reads the casting surface's span per pixel, and the CSS tier
writes one `box-shadow` blur radius per surface from the same law. A 44 px
control's shadow goes from 22 CSS px of blur to 4.3, and a 160 px panel's from 22
to 34.7.

The six occlusion anchors and the lift are refitted beside it, because their
values carried the compensation for the single width: a small control's shadow
was three and a half times too dim over six times too wide an area, and the two
cancelled in every mean anybody had taken. The thick regime's largest anchor is
fitted rather than extrapolated for the first time.

The **dark** material's diffusion also gains a term keyed on the backdrop's own
measured spatial scale, which moves how much of a structured backdrop survives
the body toward what Apple's material passes. The light material declines it, and
the ledger records the measurement behind the decline rather than the decline
alone.

Grading the blur reached a width no shipped material had, and found a latent
defect in the shader that had been there since the facet was built. The outer
shadow's falloff is a `tanh` of a cubic in the distance to the shadow's
silhouette measured in σ, and a GPU backend that evaluates `tanh` through
`exp(2t)` — Metal's fast-math path does — overflows 32-bit float about ten σ
inside that silhouette and returns NaN, which travelled into the composite's
alpha and left a **horizontal strip of the surface undrawn**. At every σ vitrea
had ever shipped, ten σ was further out than any surface is deep, so nothing
reached it; at the new thin-caster σ of 2.13 CSS px, a 44 px control's own centre
line is past it. The argument is now clamped to a range where `tanh` has already
saturated to exactly 1, which is the identity at every input the unclamped form
evaluated at all — the renderer's 34 goldens are byte-identical across the fix —
and a capture case at a thin σ asserts that a control and a toolbar draw their
whole declared region.

What moves for an app:

- **Nothing in this package's own constants.** The renderer's defaults are
  unchanged; what moved is the four macOS 27 profile documents the default
  material document is assembled from, and the module generated from them.
- **Surfaces smaller than about 96 CSS px cast a tighter, slightly stronger
  shadow**, and surfaces larger than about 128 CSS px cast a wider one. A layout
  that packed controls against a neighbour on the assumption of the old, broader
  falloff will see the gap read as larger; one that placed a large panel near a
  viewport edge will see its shadow reach further.
- **The sampling geometry moves with it, in both directions.** A group's shadow
  reach — what a scissor and a clip are sized from — falls about 36 % at a 44 px
  caster and rises about 35 % at a 160 px one, and keeps rising above that. Groups
  whose members differ in span take the law at the widest member, which bounds
  every member's rather than naming any one's.
- **Selecting `macos26MaterialProfileDocument` keeps exactly what 0.18.0 drew.**
  That material's own σ is span-invariant and its three new leaves are zero, where
  they are the measurement.

`@vitreajs/vitrea` and `@vitreajs/vitrea-react` carry no change of their own; they
move because the three published packages are versioned as one fixed group.
