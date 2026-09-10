---
"@vitreajs/vitrea-react": minor
---

`GlassButton` and `GlassIconButton` accept `tint` and `foreground`.

```tsx
<GlassToolbar aria-label="Document actions">
  <GlassButton onClick={publish} tint="#ff9500">Publish</GlassButton>
  <GlassButton onClick={duplicate}>Duplicate</GlassButton>
</GlassToolbar>
```

That example has been in the README since the tint API shipped, and it did not
compile. `GlassButtonProps` built its surface half from an explicit list of
eleven props and both of these were missing from it, so the one control Apple's
tint guidance is actually about — "apply color to the background… one emphasised
control" — was the only surface in the library that could not be tinted. The
material carried the colour end to end the whole time; the prop list stopped
short of it.

`tint={null}` on a button clears a tint inherited from its group, exactly as it
does on a `GlassSurface`, and `foreground` takes the same `ForegroundAdaptation`
the surface takes. Nothing else about the buttons moves.
