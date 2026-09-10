---
"@vitreajs/vitrea": minor
"@vitreajs/vitrea-web": minor
"@vitreajs/vitrea-react": minor
---

Add authored material presence and the materialize transition (W27d).

`GlassSurface present={false}` and `GlassHostHandle.update({ present: false })`
animate the material to identity without fading or replacing the host. The
`--vitrea-materialization` channel reaches both renderers; presence is independent
of interaction state. `GlassMorph transition="materialize"` crossfades content
while the two materials leave and arrive in their own geometry. The existing
matched-geometry behavior remains the default.

Reduced Motion steps material presence on both tiers rather than animating blur.
The channel's timing and easing are authored, not measured against native motion.
The core minor accompanies the published motion contract's authored-presence
semantics; all three packages remain in the fixed release group.
