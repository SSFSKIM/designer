# @vitreajs/vitrea-web

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
- 0ffd246: Glass now adapts to how light or dark the content behind it is.
  
  Apple's material continuously changes its appearance with backdrop luminance — a
  light-scheme capsule over black content settles to near-black. vitrea had no such
  axis at all: material profiles were discrete per colour scheme, so a surface
  looked the same over a photograph and over a black field. That was this project's
  largest measured fidelity gap.
  
  **This changes how your existing surfaces look over dark or busy backdrops**, and
  it is continuous rather than a two-state switch — intermediate backdrops land
  between the ends, on a measured curve.
  
  Where each tier gets its answer, because they differ and the difference is worth
  knowing:
  
  - **The WebGPU tier** reads the pixels it is already sampling to refract, so
    adaptation is local to each surface's own neighbourhood.
  - **The CSS tier** has no pixels. It asks, in order: an explicit
    `backdropLuminance` you set on the surface; then the backdrop source you have
    already handed over via `GlassGroup`'s `backdrop` prop, read once and averaged;
    then nothing at all, in which case it does not adapt. It never guesses a level.
  
  So on the CSS tier the adaptation is one reading per backdrop **source**, not per
  surface — two surfaces over different corners of the same image get the same
  answer. If you need better than that on that tier, set `backdropLuminance`
  yourself.
  
  Accessibility policies still win: reduce-transparency and increase-contrast
  resolve after adaptation, not before.
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
- 5ac6cc3: A host with four different corner radii now says so, at registration.
  
  Per-corner radii are still post-v1 (X8 rider 3: v1's corner algebra is
  mirror-symmetric by construction). What changed is that the limit is honest at
  the boundary that accepts it. `CornerRadii` is a Vec4 in every type along the
  path and the CSS tier renders four radii correctly through `border-radius`, so
  four different radii look supported right up until the WebGPU tier resolves the
  shape against the first one — or `@vitrea/geometry` throws from inside a frame,
  on a shape that no longer names the registration that produced it.
  
  The new `non-uniform-radii` diagnostic fires in dev mode from `registerHost` and
  from any `update` that patches radii, names both tiers' answers, and dedupes per
  surface. It is a warning: the surface still draws, and taking a page down over a
  corner would be the wrong trade for a limit the roadmap intends to lift.
- 0ffd246: Glass surfaces now cast an outer shadow.
  
  The reference material casts one and vitrea rendered zero across its entire
  footprint — by canvas coverage, the largest visible gap the project had measured.
  Every glass surface now sits on the page instead of being pasted onto it.
  
  **This changes how every existing surface looks.** The shadow is drawn on both
  tiers from the same profile constants: a `box-shadow` on the CSS tier, and
  field-derived occlusion outside the component on the WebGPU tier.
  
  Two properties are worth knowing because they are what makes it read as a shadow
  rather than as a grey halo:
  
  - **It darkens, it does not paint.** The shadow multiplies what is behind it
    rather than laying grey over it, so it takes a lot from a bright ground and
    almost nothing from a dark one — the same behaviour a real shadow has, and
    measured against the reference rather than assumed.
  - **It is coupled to the size law.** A larger, thicker surface casts a deeper
    shadow, on the same single thickness curve the other size-derived facets ride.
  
  It respects the accessibility policies, and it goes away with the glass under
  forced colours rather than surviving as decoration on a flattened surface.
  
  Cost, stated because it is not free: on the mobile bench the facet measures
  2.79× frame time. A dedicated low-resolution shadow pass is the known optimisation
  and has not been built yet — the current GPU path rasterises the enlarged rect at
  full resolution to feed the blur.
- 0ffd246: Large surfaces now read as thicker glass, the way the reference does.
  
  Apple derives five separate facets from a surface's thickness and size; vitrea
  implemented one of them (lensing depth). The remaining four are now coupled to
  the same curve, so a wide surface refracts deeper, scatters more softly, occludes
  more of its backdrop and casts a deeper inner shadow than a small one cut from
  the same material.
  
  **This changes how your existing surfaces look**, and the change is by design. It
  is larger the wider the surface is: below about 32 CSS px on the shorter side
  nothing moves, and above about 96 px the facets are at full strength. A row of
  small controls will look essentially as it did; a large panel will look
  noticeably deeper.
  
  One mechanism drives all four, not four independent knobs — a single smoothstep
  between those two spans, with each facet taking a gain on it. That is deliberate:
  the reference has one size law, and two curves would have been two mechanisms it
  does not have.
  
  Nothing new to call. `thickness` on a surface still means what it meant, and the
  span the law reads is the surface's own measured box. If you need the old
  behaviour for a specific surface, the gains are reachable through the material
  profile seam.

### Patch Changes

- Updated dependencies [0ffd246]
- Updated dependencies [aca1d25]
- Updated dependencies [c1cee6e]
- Updated dependencies [b0392eb]
  - @vitreajs/vitrea@0.2.0
