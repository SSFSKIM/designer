---
"@vitreajs/vitrea": minor
"@vitreajs/vitrea-web": minor
"@vitreajs/vitrea-react": minor
---

Frames are drawn on demand. A root used to re-arm `requestAnimationFrame` on every frame, so a
page whose glass had not changed kept drawing it sixty times a second. It now draws when
something changes (the scene, a host's box or inline channels, a backdrop source, the
material, a preference or the window's focus). It keeps drawing while a spring, a presence
fade, an adaptation filter, a readback or a live source still needs frames, and stops when
none does. Motion looks the same: a frame after an idle stretch steps by one frame's interval,
not by the whole gap.

- `setBackdropTexture` accepts `live: false` on a canvas, and `root.markBackdropSourceDirty(id)`
  declares a repaint. A canvas supplied that way is re-imported and re-sampled only when marked.
  The default is still `live: true`, which re-imports every frame and keeps the root drawing.
- A paused video is no longer re-imported every frame. Its own events (seeked, loaded, resized,
  played) mark it, and an image supplied before it decoded is marked when it loads.
- On the CSS tier, the backdrop-tone readback reads only the source pixels under the surfaces,
  plus the group's sampling padding, instead of the whole canvas. It happens when a reading is
  due, not on every 250 ms tick. The values are the same bytes the whole-source read produced.
- `root.requestFrame()` asks for a frame, and `root.framePending` reports whether one is owed.
  The ticker from `useGlassTicker()` also has `requestFrame()`.
- A frame listener (`root.subscribe`, `ticker.subscribe`) that returns `false` says it needs no
  further frame. Any other return value, including none, keeps frames coming every frame, so
  existing listeners behave as before. A listener that returns `false` calls `requestFrame()`
  when it has work again.
- Core: `createGlassScene({ onChange })` reports every mutation, and a frame participant can
  declare `pending()`. `FrameScheduler.pending()` aggregates the participants.
