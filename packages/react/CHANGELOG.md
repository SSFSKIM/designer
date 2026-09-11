# @vitreajs/vitrea-react

## 0.16.0

### Minor Changes

- 9bb6beb: A `GlassGroup` can carry the tint its members inherit.
  
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
- 1ed0a24: A toolbar can split its shared glass background, the way every system bar does.
  
  **What is new.** `GlassToolbar`'s children are now partitioned into sampling
  groups at each `<GlassToolbarSpacer />` and at each item that declares
  `sharedBackground="hidden"` — Apple's `ToolbarSpacer` and
  `sharedBackgroundVisibility(.hidden)`, which turn out to be one rule. The result
  is one `role="toolbar"` with N groups, never N toolbars: the row keeps its single
  tab stop and its arrow-key order across the split, and the flex layout is
  untouched, because a group renders no DOM. What changes is what shares a proxy,
  a blur and a union.
  
  ```tsx
  <GlassToolbar aria-label="Document actions">
    <GlassButton onClick={share}>Share</GlassButton>
    <GlassButton onClick={duplicate}>Duplicate</GlassButton>
    <GlassToolbarSpacer kind="flexible" />
    <GlassButton onClick={publish} sharedBackground="hidden" tint="#ff9500">
      Publish
    </GlassButton>
  </GlassToolbar>
  ```
  
  This is also how two tints coexist in one toolbar. A group carries one seed, so a
  tinted primary action beside a tinted bar is two groups by construction — and the
  item that steps out can carry `groupProps` of its own for anything else that
  group needs.
  
  **The gap is derived, not chosen.** Two adjacent groups each sample a padded
  region around their own shapes, and where one group's padded box covers the
  other's shapes the backdrop filter applies twice over the overlap. A spacer
  therefore opens the sampling padding the material actually requires under the
  resolved accessibility policy, and never less than the advisory the scene model
  checks a layout against: turn *Reduce Transparency* on, the frost thickens, and
  the material's own requirement rises past that advisory on a normal-height bar.
  Your own `gap`, margin or width adds to it, and an explicit `style` of your own
  still wins. The material's half of that number is now exported from
  `@vitreajs/vitrea-web` as `samplingPaddingFor({ members, material })`, which is
  what a host-level app splitting a toolbar over the framework-agnostic entry
  reaches for — groups are already the primitive there, so nothing else was needed.
  
  **Nothing about the material moves.** The frame loop resolves each group's blur
  through the same composition it always did, now named `proxySamplingSigma` and
  shared with the derivation above rather than written out twice.
- 9bb6beb: `GlassButton` and `GlassIconButton` accept `tint` and `foreground`.
  
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
- 9bb6beb: Four named ink levels on every glass host, on both tiers.
  
  ```css
  .panel__title   { color: var(--vitrea-foreground); }
  .panel__caption { color: var(--vitrea-foreground-secondary); }
  .panel__meta    { color: var(--vitrea-foreground-tertiary); }
  .panel__rule    { border-color: var(--vitrea-foreground-quaternary); }
  ```
  
  `--vitrea-foreground-secondary`, `-tertiary` and `-quaternary` join
  `--vitrea-foreground`: Apple's four label levels, as reduced-alpha versions of
  the ink the runtime resolved for this surface. Until now there was one token, so
  an app with a caption or a disabled row either wrote it at full strength or
  invented a scale against a material it cannot see.
  
  **The alphas are not Apple's copied flat, and that is the point.** 60% is where
  the platform's ink reaches WCAG's 4.5 body-text floor over the platform's white
  background — and glass is never a white background. Sixty percent of vitrea's
  dark ink reaches 4.49 over an encoded level of 1.0 and 3.21 over the regular
  material's darkest. So **secondary is raised to whatever holds 4.5 against the
  colour this surface is actually drawing**, and is Apple's 60% wherever that
  already clears it, which is most of the dark appearance.
  
  The colour and not a brightness: a ratio is not a function of luminance once
  either side is chromatic, so a tinted surface is measured against its tint. And
  where the backdrop is not known — the `light-dark()` case, where the browser
  picks the ink by colour scheme rather than by level — the floor is solved
  against both ends of the range the surface can reach and the harder answer
  taken, so the guarantee does not turn on which backdrop shows up.
  
  On a surface whose primary ink cannot hold 4.5 either, secondary collapses onto
  the primary rather than publishing a level that is not readable. Secondary is
  never worse than primary, and holds 4.5 wherever primary can.
  
  **Tertiary and quaternary carry no floor**, deliberately: they are Apple's
  supporting and decorative tiers, they are not body text, and lifting them to 4.5
  would collapse the scale onto one value. Quaternary is the one Apple warns about
  by name — too low-contrast on a thin material — and in dev mode a page whose CSS
  uses it while a surface resolves below the material's thin/thick knee now gets a
  diagnostic saying so. It changes nothing: the token is published either way.
  
  Under forced colours all four are `CanvasText`, and under increased contrast all
  four are the near-monochrome ink. A preference that asked for more contrast does
  not get three dimmer answers.
- 736c7cd: Add authored material presence and the materialize transition (W27d).
  
  `GlassSurface present={false}` and `GlassHostHandle.update({ present: false })`
  animate the material to identity without fading or replacing the host. The
  `--vitrea-materialization` channel reaches both renderers; presence is independent
  of interaction state. `GlassMorph transition="materialize"` crossfades content
  while the two materials leave and arrive in their own geometry. The existing
  matched-geometry behavior remains the default.
  
  Reduced Motion steps material presence on both tiers rather than animating blur.
  The channel's timing and easing are authored, not measured against native motion.
  The core minor accompanies the published motion contract's authored-presence
  semantics; all three packages remain in the fixed release group.

### Patch Changes

- Updated dependencies [1ed0a24]
- Updated dependencies [9bb6beb]
- Updated dependencies [d247346]
- Updated dependencies [b86eb83]
- Updated dependencies [9bb6beb]
- Updated dependencies [736c7cd]
- Updated dependencies [9bb6beb]
  - @vitreajs/vitrea-web@0.16.0
  - @vitreajs/vitrea@0.16.0

## 0.15.0

### Patch Changes

- Updated dependencies [f477c9e]
  - @vitreajs/vitrea-web@0.15.0
  - @vitreajs/vitrea@0.15.0

## 0.14.0

### Patch Changes

- Updated dependencies [99a74a0]
  - @vitreajs/vitrea-web@0.14.0
  - @vitreajs/vitrea@0.14.0

## 0.13.0

### Patch Changes

- Updated dependencies [4a2f766]
  - @vitreajs/vitrea-web@0.13.0
  - @vitreajs/vitrea@0.13.0

## 0.12.0

### Patch Changes

- Updated dependencies [843ecc7]
  - @vitreajs/vitrea-web@0.12.0
  - @vitreajs/vitrea@0.12.0

## 0.11.0

### Patch Changes

- Updated dependencies [6a0b8f1]
  - @vitreajs/vitrea-web@0.11.0
  - @vitreajs/vitrea@0.11.0

## 0.10.0

### Minor Changes

- c017625: A page in dark mode can ask for the dark material.
  
  **What you get.** `createGlassRoot({ colorScheme })` and `<GlassRoot colorScheme>`
  take `"light" | "dark" | "auto"`. `"dark"` draws the material vitrea measured
  against Apple's own renderer in dark mode rather than the light one over a dark
  page; `"auto"` follows `prefers-color-scheme` and re-derives both tiers when the
  system flips, without rebuilding the root, so a theme toggle costs no
  registrations. `root.colorScheme` reports which of the two is actually drawing and
  `root.setColorScheme(...)` changes it on a live root. The default is `"light"`,
  which is the material the runtime's own constants already are, so nothing moves
  for an app that upgrades.
  
  Until now the dark numbers existed only as a calibration document inside this
  repository: a host in dark mode got the light material, and the only way out was
  to copy constants nobody exported. `@vitreajs/vitrea-web` now exports them as
  `darkMaterialProfile`, generated from that document with a test pinning the two
  together, so an app that resolves its own scheme somewhere vitrea cannot see can
  pass the patch directly — and an app that wants the dark material with a tuning of
  its own can pass both, because the scheme selects the base and `materialProfile`
  merges over it leaf by leaf.
  
  One distinction worth keeping: a group's backdrop `hint` states the tone of what
  is behind the surface, and `colorScheme` states which material the surface is made
  of. They are different questions, and a dark page can honestly hand a light hint
  to a surface over a white card. Your page's own background stays yours either way
  — the runtime does not write your tokens, so an app offering "follow the system"
  reads the query for its own colours as well as passing `"auto"` here.

### Patch Changes

- Updated dependencies [794a99d]
- Updated dependencies [c017625]
  - @vitreajs/vitrea-web@0.10.0
  - @vitreajs/vitrea@0.10.0

## 0.9.0

### Patch Changes

- Updated dependencies [bc7706e]
  - @vitreajs/vitrea-web@0.9.0
  - @vitreajs/vitrea@0.9.0

## 0.8.0

### Patch Changes

- Updated dependencies [4e7e75b]
- Updated dependencies [2d11305]
  - @vitreajs/vitrea-web@0.8.0
  - @vitreajs/vitrea@0.8.0

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
