---
"@vitreajs/vitrea-react": minor
---

A `GlassGroup` can carry the tint its members inherit.

```tsx
<GlassGroup id="panel" tint="#ff9500">
  <GlassSurface>Inherits the group's colour</GlassSurface>
  <GlassSurface tint={null}>Opts out of it</GlassSurface>
</GlassGroup>
```

The 0.2.0 release notes said "Set it on a `GlassGroup` to tint its members", and
the runtime has resolved a group seed since that release — a member declaring no
tint inherits the group's, and `null` clears it, the way `Glass.tint(nil)` does.
What was missing was the prop: `GlassGroupProps` had no `tint`, so there was no
way to set the thing the notes described.

It takes any CSS colour, with the colour's own alpha as the tint's strength, and
it is parsed once per colour per document rather than per group. A group is one
sampling region and one optics pass and so carries one seed: a group tint plus a
member that overrides it is two, and raises the same dev-mode `tint-mixing`
warning two differently tinted members always have.
