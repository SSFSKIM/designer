---
"@vitreajs/vitrea-web": minor
---

The dark material is measured against Apple's own dark renderer instead of inherited
from the light one.

**What you see in dark mode.** A surface's interior now follows the backdrop it sits
over the way Apple's does: thin controls lift over a photograph or a busy page where
they used to stay flat and dark, thick panels settle darker over the same content,
and over a near-black background the surface all but disappears into it, as it should.
The rim loses a light direction it never had — Apple's dark rim is the same faint
brightness on all four sides, and vitrea's was drawing the light scheme's two-light
rim at seven to ten times the reference's strength, weighted toward the top-left. And
the backdrop's own structure shows through: the surface used to trade the pattern
away to hold its level, and now that the level is solved for, the checkerboard, the
photograph and the text behind a panel read through it about four times more
strongly, which is what Apple's does.

Nothing about this is a taste choice. The response curve's six anchors are readings
taken off macOS 26.5's own renderer on a 56-cell probe, unmodified; two constants were
fitted on the rows that separate them, and a third was declined because its rows did
not. Over the calibration bed the OKLab colour difference against Apple's captures
falls from 0.0085 to 0.0041 on the WebGPU tier at both device pixel ratios, and on the
held-out scenes — read once, after the constants were frozen — from 0.0300 to 0.0161,
with all three cells improving; the worst dark cell in the bed, a large panel over a
photograph, halves.

One honest limit. On the CSS tier the dark material is right over a solid background
and still too dark over a busy one: two layers resolve the response from a single
backdrop level for the whole surface, so a panel over a checkerboard lands well below
where the WebGPU tier and Apple both put it. The WebGPU tier is the fidelity target
and the CSS tier derives what its layers can carry; the residual is recorded with its
cause and the diagnosis is named work, not a mystery.

Recorded in `docs/doperpowers/specs/c9a-fidelity-claims.md` §5.87 (the finding),
§5.88–§5.89 (the dark reference measured) and §5.90 (the form declared and dry-run).
