---
"@vitreajs/vitrea-web": minor
---

Hover, focus, press and morph now deepen the lens on the WebGPU tier.

The `lensStrength` channel is documented as `0..1+` and the motion drivers have
always produced it that way — 1 at rest, 1.03 focused, 1.06 hovered, 1.10 while
a morph runs, 1.14 pressed, 0.5 disabled. The renderer clamped it at 1 on its
way into the shader, so `disabled` was the only interaction state that reached
the material at all and every state that deepens the lens arrived
indistinguishable from rest. Two documents disagreed about the channel's range;
the one the clamp was written from was the wrong one.

Nothing is unbounded by the change. The lens depth is still clamped to the
surface's half span in the fragment stage and its magnitude scaled by the same
ratio, so a stronger channel deepens the lens up to that limit and no further.

**A resting surface is byte-identical.** The channel is exactly 1 at idle, where
the two forms agree, and the renderer's golden bed passes unchanged with no
image re-recorded. What you will see move is a surface under the pointer.
