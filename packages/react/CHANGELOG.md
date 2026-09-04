# @vitreajs/vitrea-react

## 0.7.0

### Patch Changes

- Updated dependencies [5868672]
  - @vitreajs/vitrea-web@0.7.0
  - @vitreajs/vitrea@0.7.0

## 0.6.0

### Patch Changes

- Updated dependencies [64457d0]
  - @vitreajs/vitrea-web@0.6.0
  - @vitreajs/vitrea@0.6.0

## 0.5.0

### Patch Changes

- Updated dependencies [c00f89e]
  - @vitreajs/vitrea-web@0.5.0
  - @vitreajs/vitrea@0.5.0

## 0.4.0

### Patch Changes

- Updated dependencies [492168b]
- Updated dependencies [492168b]
- Updated dependencies [99ea455]
  - @vitreajs/vitrea-web@0.4.0
  - @vitreajs/vitrea@0.4.0

## 0.3.0

### Patch Changes

- Updated dependencies
- Updated dependencies
- Updated dependencies
- Updated dependencies
- Updated dependencies
- Updated dependencies
  - @vitreajs/vitrea-web@0.3.0
  - @vitreajs/vitrea@0.3.0

## 0.2.0

### Minor Changes

- 0ffd246: Glass can be coloured: a supported tint API on every surface.
  
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
- aca1d25: The scene model grows the three fields another package was already carrying.
  
  All three were recorded together in Decision Log #23(c) as the same shape — "core
  grows a field another package already carries" — and deferred as a batch rather
  than drip-fed as core churn.
  
  - **The corner reference is a scene-model field.** `GlassNodeDescriptor.reference`
    and `GlassHostOptions.reference` carry which of the two corner fits a shape is
    authored against; `GlassSurface` sends it from its `profile` prop. **This
    changes what the WebGPU tier draws for a surface with a non-`"continuous"`
    profile.** The renderer has always had the field and nothing ever set it, so
    every surface was resolved against the Apple-direct fit — including one
    authored on the Figma smoothing axis, which is a separate fit rather than
    another point on the same axis (#22(a)). `profile="circular"` and
    `profile={0.6}` are now drawn on the axis those values live on. The CSS tier is
    unaffected: it renders corners with `border-radius`.
  - **The concentric parent link is a scene-model field.**
    `GlassNodeDescriptor.concentricOf` / `GlassHostOptions.concentricOf` declare a
    surface as a level set of another surface's field (X8 rider 2). An unknown
    parent, a parent in another group, a self-reference and a cycle are all refused
    at registration, where the call that caused them is still on the stack, instead
    of throwing once per frame from the renderer's draw path; and a parent with a
    child still attached refuses removal, like a group with members.
  - **The platform probe can be set per group.** `setPlatformProbe(probe, groupId?)`
    mirrors `setGovernorPressure`. S1's backdrop-root audit is per group, so a
    group whose proxy chain is re-rooted has to demote alone — which a scene-wide
    probe could not express, so the browser layer bypassed `resolve()` and folded
    the verdict into a private call to core's pure resolver. It no longer does, and
    `scene.resolve()` and `root.capabilities(groupId)` now give one answer instead
    of two. `effectiveGroupState` is deprecated in favour of the scene path.
- c1cee6e: The browser host is published in its own right: `@vitreajs/vitrea-web`.
  
  Until now `vitrea` alone could not mount a root. The runtime is DOM-free by
  design and the host layer reached npm only inlined inside `vitrea-react`, so the
  only way to render glass in a browser was through React — a narrower promise than
  "framework-agnostic runtime" reads. The host is now its own package, and the
  three layer the way React's own do: a pure runtime, a DOM host over it, framework
  bindings over that.
  
  - **New:** `npm install @vitreajs/vitrea-web` and call `createGlassRoot` from
    plain JavaScript, or from a Vue, Svelte, Angular or Web-Components adapter. It
    is the same entry the React bindings are built on; there is no privileged path.
    The package README carries the imperative quickstart, and
    `e2e/fixtures/vanilla.ts` is that quickstart executed on three engines.
  - **New:** `GlassRoot.subscribe(listener)` — join the root's frame loop instead of
    running a second `requestAnimationFrame` beside it. Listeners run after the
    frame, on a settled scene; one that throws is reported as the new
    `frame-listener-failed` diagnostic and unsubscribed.
  - **Changed:** `@vitreajs/vitrea-react` now *depends* on `@vitreajs/vitrea-web`
    rather than bundling a copy of it, so a page that mounts one root through the
    bindings and another through the host directly shares a single host. Both are
    installed for you; `npm install @vitreajs/vitrea-react` is now enough on its
    own. The React bindings' motion also runs on the root's loop now rather than on
    one of their own — one wake-up per frame, and a defined order between the scene
    resolving and the springs stepping.
  - **Changed:** core's `DiagnosticsChannel`, `Diagnostic`, `DiagnosticSink` and
    `createDiagnosticsChannel` are generic over their code union, with core's own
    union as the default. Every existing use reads unchanged; the browser host's
    channel is now an instantiation of core's rather than a second copy of the
    machinery.

### Patch Changes

- 2677b86: `GlassMorph` no longer claims the top-left of the viewport for a frame before it
  opens.
  
  A morph measures its closed end on a frame and only then places itself, and until
  now the platter spent that frame in normal flow. Flow inside a plane's host layer
  is not the app's layout — a host layer is `position: absolute; inset: 0` over the
  viewport, so a block box there is the full width of the page at the page's origin.
  That box was registered like any other glass surface, which meant a freshly
  mounted morph briefly overlapped every surface on its plane and stretched its
  sampling group's backdrop proxy across the whole viewport. On a page with dev-mode
  diagnostics on, it showed up as `same-plane-overlap` and `group-proxy-overlap`
  findings for a layout that never had either.
  
  The platter is now out of flow from its first commit and explicitly empty until it
  has been placed, so there is no meaningful box to register until there is a real
  one. Nothing about the closed footprint changes: that has always been the morph's
  anchor spacer, which still sits in the app's own layout and still holds the space.
  
  For apps this removes a placement constraint rather than adding one — glass may
  sit in the viewport's top-left corner next to a morph, and a morph no longer needs
  a sampling group of its own purely to keep that transient out of a neighbour's
  proxy. A morph that shares a group with other surfaces is still worth avoiding for
  the frame before it places itself.
- Updated dependencies [0ffd246]
- Updated dependencies [0ffd246]
- Updated dependencies [aca1d25]
- Updated dependencies [c1cee6e]
- Updated dependencies [b0392eb]
- Updated dependencies [5ac6cc3]
- Updated dependencies [0ffd246]
- Updated dependencies [0ffd246]
  - @vitreajs/vitrea@0.2.0
  - @vitreajs/vitrea-web@0.2.0

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
