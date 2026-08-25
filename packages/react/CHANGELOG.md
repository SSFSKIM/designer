# vitrea-react

## 0.1.0

### Minor Changes

- 1595af5: Initial public release.
  
  vitrea is a production-oriented, reference-calibrated material compositor for
  semantic web controls: a TypeScript replication of Apple's Liquid Glass material
  on the web, with real-time size-parameterized lensing, per-element backdrop
  adaptation, container-scoped sampling groups, and shape-to-shape morphing. Glass
  labels stay real DOM — a `GlassButton` is a `<button>`, focusable and announced
  as one.
  
  **Two tiers, and the runtime tells you which one you got.** The WebGPU texture
  tier does vitrea's own shader math over a GPU-owned backdrop; the CSS tier is a
  first-class renderer rather than a degraded path, because WebGPU is not
  everywhere. `useGlassCapabilities()` reports the resolved state per group —
  `configuredSource` survives demotion, every demotion names both a reason and its
  recovery condition, and choosing the CSS tier deliberately resolves healthy
  rather than as a fault.
  
  **Components:** `GlassRoot`, `GlassGroup`, `GlassSurface` (with `asChild`),
  `GlassMorph`, `GlassButton`, `GlassIconButton`, `GlassToolbar`,
  `GlassSegmentedControl`. Backdrops: image, video, canvas, procedural gradient,
  and arbitrary DOM. Accessibility: `prefers-reduced-motion`,
  `prefers-reduced-transparency`, `prefers-contrast` and `forced-colors` each
  resolve to a declared material or motion consequence, the first three
  overridable per root.
  
  **Fidelity is measured, and scoped.** The texture tier is reference-calibrated
  against 30 ScreenCaptureKit captures of Apple's `glassEffect` on macOS 26.5. Full
  claims, and everything that could not be measured, are in
  `docs/doperpowers/specs/c9a-fidelity-claims.md`. Nothing here is pixel-identical
  to Apple's material, no press-state claim is made, and the CSS tier carries a
  Chromium-only figure stated as untuned.
  
  Published unscoped: `npm install vitrea vitrea-react`. The geometry, motion, DOM
  host and WebGPU renderer packages are internal and bundled in, so these two carry
  no transitive runtime dependency beyond React (a peer, `>=19`).

### Patch Changes

- Updated dependencies [1595af5]
  - vitrea@0.1.0
