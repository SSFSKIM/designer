# @vitreajs/vitrea-react

## 0.1.1

### Patch Changes

- Docs: everything the first cold consumer had to discover by reading `.d.ts` and
  WGSL is now in the READMEs.
  
  The texture backdrop's declare-then-supply two-step (`backdrop={{ kind:
  "texture", id }}` then `setBackdropTexture`) with its placement contract — the
  source is cover-fitted over the whole viewport, not the group, so an app that
  also paints the image must use the same mapping. A "Testing your app" section:
  Playwright's bundled headless shell has no working WebGPU, so tests silently run
  the CSS tier; the working recipe is `channel: "chromium"` plus the WebGPU flags,
  and the capabilities readout can be believed either way. The per-tier DOM truth:
  `[data-vitrea-proxy]` elements exist only where the GPU tier samples through the
  browser's backdrop-filter; the CSS tier writes the material on the host itself.
  The surface sizing model (surfaces have no intrinsic size). The react export
  list gains its four missing entries, including `APPLE_LIKE_SMOOTHING`, and the
  `demotionReason` union in the core README gains its missing
  `"no-texture-supplied"` member.
- d85011a: Fix: the published `.d.ts` files typecheck for a consumer with `skipLibCheck: false`.
  
  Both artifacts named WebGPU globals — `GPUDevice`, `GPUTextureView`,
  `GPUPowerPreference` and eleven more — that nothing in the tarball declared. This
  workspace resolved them out of `lib.dom.d.ts`, which only ships the WebGPU
  interfaces from TypeScript 6.0 onward, so a consumer on TypeScript 5 read 29
  `TS2304`s out of `node_modules`.
  
  Each artifact now declares those names itself: the interfaces empty and global, so
  they merge with the consumer's real WebGPU types wherever they have them, and the
  two string-union aliases module-local, because a type alias cannot merge. Nothing
  was added to either package's dependencies, and the emitted JavaScript is
  unchanged. Verified with `skipLibCheck: false` on TypeScript 5.8, 5.9, 6.0 and
  7.0, with the DOM lib, with `@types/web` in place of it, and alongside a
  consumer's own `@webgpu/types`.
- Updated dependencies
- Updated dependencies [d85011a]
  - @vitreajs/vitrea@0.1.1

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
  Chromium-only figure — it converts the material the root carries rather than
  holding one of its own, so a demotion keeps the same material to within 1.3% of
  its interior level in the mean.
  
  Published under the `@vitreajs` scope:
  `npm install @vitreajs/vitrea @vitreajs/vitrea-react`. The geometry, motion,
  DOM host and WebGPU renderer packages are internal and bundled in, so these
  two carry no transitive runtime dependency beyond React (a peer, `>=19`).

### Patch Changes

- Updated dependencies [1595af5]
  - @vitreajs/vitrea@0.1.0
