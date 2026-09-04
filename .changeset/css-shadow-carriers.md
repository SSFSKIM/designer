---
"@vitreajs/vitrea-web": minor
---

The CSS tier's outer shadow leaves its own blurred backdrop.

**What you see.** A group of glass surfaces stops darkening itself. Until now the
tier drew each surface's outer shadow on the host element, and the host's three
filter layers are that host's own children — so every surface blurred its own
shadow into its own body, and a surface later in the document blurred its earlier
neighbours' shadows in as well. On a three-button toolbar over a patterned page
that cost 0.012 to 0.015 of the material's interior level against the WebGPU tier
drawing the same profile; it now costs 0.003 to 0.009. The shadow itself is
unchanged in colour, offset, spread, blur and reach — it is the same shadow, in
the same place, painted after the filters that used to read it instead of before
them.

Two carriers do it, and which one a group got is on the resolved state as
`GlassGroupState.cssShadow`. A lone surface puts its shadow on the tier's own
overlay layer (`"layer"`). A group with more than one member paints every
member's shadow from the group's last-painted host, one inert child per member,
clipped out of every member's body (`"group"`). A host whose own `overflow` clips
its children keeps the shadow where it was, because a shadow on a clipped child is
not a dimmer shadow but no shadow at all (`"host"`).

**What does not change.** The WebGPU tier is byte-identical on all six calibration
profiles at both scales. No public API moves; nothing is added to a lone surface's
DOM; the added elements are `aria-hidden`, not hit-testable and not focusable, and
the frame-cost knee is where it was. Every accessibility regime and forced colors
behave as before.

**The named gaps.** What is left after the removal is the CSS filter reading the
element's own border box rather than the page around it, which shows on small
boxes over structured backdrops: about 0.005 of interior level on a 44 px square
at 1x, near zero on a 120 x 44 capsule, and sign-flipped at 2x. It is carried as a
measured bound per box and scale, not as a fitted correction.
`checkerboard__capsule-button` at 2x sits at +0.0102 of cross-tier level for that
reason. Under reduced transparency and increased contrast the three-up cell is
+0.0139 and -0.0281 against the WebGPU tier, both outside the 0.01 the wave asked
for and both recorded. The stacked-glass scene is unmoved: its residual is the
WebGPU tier's own unsampled material on a DOM-sourced group, not this tier's.
