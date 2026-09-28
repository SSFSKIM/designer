---
"@vitreajs/vitrea-react": patch
---

A capsule surface (`GlassIconButton`, or `capsule` on `GlassButton` or `GlassSurface`) now keeps
the radius its measured box gives it when another prop changes. Changing `tint`, `thickness`,
`present`, `variant` or `order` used to reset it to the default corner radius, so a circular button
turned into a rounded square and stayed that way until its box changed size.
