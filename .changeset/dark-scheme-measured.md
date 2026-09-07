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

**The CSS tier follows it, over busy backgrounds too.** A browser without WebGPU draws
the same material through `backdrop-filter`, and getting the dark scheme right there
took two corrections that arrived with it. The layer that carries the tint was being
matched to the renderer at one fixed backdrop brightness, a number fitted back when
the light material was; on the dark material every tint sits at that same brightness,
so the match had nothing left to measure and a panel over a checkerboard landed at a
quarter of its level. It is now matched at the backdrop the surface actually sampled.
And the tier chooses between two ways of drawing the tint — one exact but carried
through a filter chain that holds only eight bits, one approximate but carried in the
page's own space — where before it picked by asking how coarse the filter chain was
and nothing else. It now draws whichever of the two lands nearer the renderer, which
over a busy dark background is the exact one by a wide margin and over a near-black
solid is still the other. Measured across the dark bed, the two tiers' interior
brightness now agrees to within 8% where it differed by as much as 3.9x, and the CSS
tier's own colour difference against Apple falls from 0.0116 to 0.0068 on the calibration
scenes and from 0.0434 to 0.0200 on the held-out ones.

One honest limit remains, and it is the instrument rather than the material: on one
held-out scene — a glass panel nested inside another glass panel, over a checkerboard,
at 2x — the measurement that recovers a surface's outline from its backdrop finds a
smaller and more perforated shape than it used to, precisely because the surface now
matches its surroundings as closely as Apple's does. Four shape readings on that one
scene are held at their measured values with the reason recorded; nothing about the
drawn shape moved, and the instrument that reads the drawn shape against its own
declaration still reports it correct to one pixel.

Recorded in `docs/doperpowers/specs/c9a-fidelity-claims.md` §5.87 (the finding),
§5.88–§5.89 (the dark reference measured) and §5.90 (the form declared, dry-run and
landed on both tiers).
