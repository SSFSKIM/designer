---
"@vitreajs/vitrea": minor
"@vitreajs/vitrea-web": minor
"@vitreajs/vitrea-react": minor
---

Glass can be coloured: a supported tint API on every surface.

Flat fill was the only way to colour a surface, and Apple names exactly that a
character-breaking failure. `tint` is the supported alternative, and it stays
glass.

```tsx
<GlassSurface tint="rgb(255 149 0)">Publish</GlassSurface>
```

- **New `tint` prop** on `GlassSurface` (React), `tint` on `GlassNodeDescriptor`
  and `GlassHostOptions` (core), as any CSS colour. Set it on a `GlassGroup` to
  tint its members; `null` on a surface clears a tint inherited from the group.
- **The colour is a seed, not a fill.** The material maps it to a range of tones
  against the backdrop behind that surface, so a tinted button over dark content
  settles to a shade of the colour rather than sitting on the page as paint.
- **The colour's own alpha is the tint's strength.** `rgb(255 149 0 / 50%)` is a
  half-strength orange. It does **not** change how opaque the material is — that
  stays the calibrated value your accessibility policies and the system glass
  preference operate on, so tinting can never quietly undo a dimming policy.
- **Both tiers**, and the contrast machinery accounts for it, so foreground
  adaptation still picks a legible ink over a tinted surface.

Tint sparingly. Apple's guidance is one emphasised control, not a coloured
toolbar, and the API is shaped for that rather than for theming.
