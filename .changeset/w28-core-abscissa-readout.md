---
"@vitreajs/vitrea": minor
---

Publish the per-surface response input on the resolved group state. `GlassGroupState`
gains an optional `backdropToneAbscissae`, and `SurfaceBackdropToneAbscissa` names one
surface's actual reading: its kind (`source`, `silhouette` or `hint`), the encoded and
linear levels, the sample count and the level and dimensions it was reduced over. It is
observed rather than declared, so it is absent until a frame has produced one, and it
reports the downscaled source a reduction actually ran on rather than the original
raster.
