---
"@vitreajs/vitrea-react": minor
"@vitreajs/vitrea-web": minor
---

Tell the React bindings which material document the root selected, so a toolbar
opens its split at its own material's blur.

`GlassRoot` has taken a `materialProfileDocument` since 0.19.0, and nothing below
it could read the answer. `GlassToolbar` derives the minimum width of a spacer
from the sampling padding its members' material actually requires — a constant
would be wrong under Reduce Transparency, which is exactly the preference that
enlarges the blur — and with no way to name the selected document it asked that
question of the default one. A page pinned to `macos26MaterialProfileDocument`
therefore opened its splits at the macOS 27 material's blur: about twice the room
that material needs, at the one size a reader is least likely to notice.

- **`GlassRootHandle` now carries `materialProfileDocument`**, beside `root`,
  `ticker` and `profile`. It is the document the runtime SELECTED, not the prop's
  current value: `createGlassRoot` reads the document once at construction and a
  later prop change does not move the material the page draws, so reporting the
  prop would name a material nothing is drawing. It is readable before the mount
  effect has run, which is what a layout needs — the toolbar derives its first
  gap on its first render, when `root` is still `null`.
- **A toolbar's gap follows the resolved colour scheme.** One document's two
  schemes do not ask for the same room — the macOS 27 dark endpoint wants about
  8 % more than the light one — and the gap was taking the light endpoint's
  number under both, which is an under-pad on a dark root. The scheme is polled
  rather than read once, because `colorScheme="auto"` is resolved inside the
  runtime against `prefers-color-scheme` and moves while the prop stands still.
  The window pose is deliberately not an axis: a gap that changed when the window
  lost focus would reflow the toolbar on blur.
- **`samplingPaddingFor` distinguishes an absent `profile` from an undefined
  one.** One shipped endpoint carries no patch at all — the macOS 26.5 light
  active material IS the renderer's own constants — so a caller holding a
  document has to be able to say so. Omit the key for the material a default root
  draws; pass it as `undefined` for an endpoint that names no patch. Callers that
  pass a profile, or pass neither key, are unaffected.

What moves for an app: a React toolbar on a non-default material document opens
narrower splits, by the difference between the two materials' blurs; one on the
default document is unchanged in the light scheme and opens a few pixels wider in
the dark one, where it was previously a little too narrow for its own material.
