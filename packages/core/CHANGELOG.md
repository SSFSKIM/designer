# @vitreajs/vitrea

## 0.6.0

## 0.5.0

Version-locked with `@vitreajs/vitrea-web` 0.5.0 and `@vitreajs/vitrea-react` 0.5.0; no
change in this package. The material law that moved in 0.5.0 — the glass body's second
scale, fitted on Apple's 2x captures — lives in the browser host and its bundled renderer;
see `@vitreajs/vitrea-web`'s changelog.

## 0.4.0

Version-locked with `@vitreajs/vitrea-web` 0.4.0 and `@vitreajs/vitrea-react` 0.4.0; no
change in this package. The material laws that moved in 0.4.0 — the lens band's shape, the
body's depth ramp and the outer shadow's two terms — live in the browser host and its
bundled renderer; see `@vitreajs/vitrea-web`'s changelog.

## 0.3.0

Version-locked with `@vitreajs/vitrea-web` 0.3.0 and `@vitreajs/vitrea-react` 0.3.0; no
change in this package. The material laws that moved in 0.3.0 live in the browser host and
are listed in its changelog.

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
- b0392eb: Glass inside an `overflow: scroll` ancestor is now cropped by it.
  
  `GlassNodeRecord.clip` was declared, documented and populated by nobody: the
  read phase never passed it and nothing ever read it, so the pipeline believed
  the border box — which `getBoundingClientRect` reports wherever a surface has
  scrolled to, including entirely outside the scroller (Decision Log #41(k)).
  
  Three things follow, and all three were wrong before:
  
  - **The proxy is cropped.** A group's backdrop proxy lives in the plane layer,
    not inside the app's scroller, so nothing crops it on the browser's behalf: a
    surface straddling a scroller's edge had its glass painted in full, hanging
    outside the container. The proxy's painted region and its sampling box are now
    the visible extent, and a corner the crop cut is drawn square rather than
    round.
  - **`same-plane-overlap` stops firing between surfaces that cannot touch.** It is
    a hard error, and a surface scrolled out of view was raising it against every
    surface whose box it passed over.
  - **`group-proxy-overlap`'s predicate is true again.** It rests on "a proxy
    paints only inside its own clip union", and a union built from unclipped boxes
    made that sentence false under any scroller.
  
  The cost is one extra rect read per clipping ancestor per measurement. The
  computed-style walk that finds which ancestors clip runs once per host and is
  cached, so a scroll costs rects and not styles, and the zero-reads-at-steady-state
  guarantee is unchanged.
  
  `GlassScene.setNodeBounds(id, bounds, clip?)` has carried the third argument
  since v1; `clipRect(rect, clip)` is exported for a consumer that holds both.
  Rounded clipping ancestors are folded as their bounding boxes — stated in
  `clipRect`'s own documentation, and always erring towards reporting more surface
  rather than less.

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
