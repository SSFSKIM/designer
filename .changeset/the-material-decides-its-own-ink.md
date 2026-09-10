---
"@vitreajs/vitrea-web": minor
---

An untinted surface's ink is decided by the material it is drawing, not by the
colour scheme.

**What changes.** A surface with no author tint and no backdrop hint used to
publish `--vitrea-foreground: light-dark(#1c1c1e, #f5f5f7)` and let
`color-scheme` pick between the two. It now publishes the ink the material's own
level decides, on both tiers. For the regular variant that is the dark ink over
every backdrop there is; the clear variant still publishes `light-dark()`,
because at its opacity the backdrop genuinely does decide and there is no single
answer to prefer.

**Why it was wrong.** The runtime already brackets the level behind the glyphs
over every backdrop a surface can sit on, and takes the decision wherever the
whole bracket lands on one side of the crossover. That was wired to
author-tinted surfaces only, on the reasoning that a tint is a declaration to
honour while the profile's own neutral tint is a calibration constant. True, and
not the distinction that governs: at the material's measured opacity the neutral
white tint dominates what a reader sees behind the text exactly as an author's
colour would. What was left behind was the colour scheme choosing the ink for a
body it knows nothing about — in a dark scheme, the light ink on a near-white
surface.

**If you were relying on the old behaviour**, an explicit `foreground` on the
surface or the group still wins, and your own `color` rule on the host still
beats the runtime's, unchanged.
