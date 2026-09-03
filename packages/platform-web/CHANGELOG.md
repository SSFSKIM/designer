# @vitreajs/vitrea-web

## 0.5.0

### Minor Changes

- c00f89e: On Retina displays the glass body now matches Apple's at its own scale.
  
  Every previous release fitted the body's blur at 1x and drew the same law at 2x,
  where it was wrong three ways at once: the two blur widths were CSS-pixel
  quantities where Apple's kernel is one kernel in device pixels, so on a Retina
  display vitrea blurred twice as wide; the deep interior kept a share of sharp
  backdrop that Apple's has let go of by mid-depth; and the depth ramp that
  sharpens the rim at 1x could not act at 2x because the interior beneath it was
  already sharper than Apple's contour. This release measures the 2x body on
  Apple's own captures and gives every term its second scale.
  
  **What you see at 2x.** Behind a surface the backdrop's structure now reads the
  way it does on macOS: crisp at the rim, dissolving toward the centre, and
  dissolving further on larger surfaces — the heavy blur is six device pixels on a
  control and grows with the surface past the thickness knee, which is what keeps
  a large platter's centre as soft as Apple's while a button stays legible. The
  whole-crop similarity to Apple's captures rises on every checkerboard cell
  measured, most on the mid and large spans, and the interior's spread of backdrop
  structure lands within about 0.01 of Apple's on every calibration span.
  
  **What you see at 1x.** Nothing. Every second-scale term is interpolated from
  the 1x value and is inert below a device pixel ratio of one; the 1x captures are
  byte-identical to the previous release, and a golden at 1x now pins that.
  
  **Between 1x and 2x** (a 1.5x display, or a window mid-drag between monitors)
  the terms interpolate linearly, so nothing jumps.
  
  **The CSS tier is unchanged at every scale.** Its single `backdrop-filter` blur
  keeps the 1x law; the measured shape of Apple's single-blur ceiling at 2x is
  recorded and handed to the tier's own next design round.
  
  Nothing in your code changes. If you pass a material profile of your own, the
  scattering facet gains its second-scale constants — the heavy gain at 2x and its
  top past the knee, the deep value's floor and span top at 2x, and the ramp's 2x
  anchors, which were provisional before and are fitted now — and a profile that
  does not name them gets the measured values.
  
  Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.69 and
  §5.70.

### Patch Changes

- @vitreajs/vitrea@0.5.0

## 0.4.0

### Minor Changes

- 492168b: The frost inside glass now sharpens toward the edge, the way Apple's does.
  
  Vitrea blurred the content behind a surface at one mix of sharp and heavy
  scatter across the whole surface, chosen by the surface's size. Apple's material
  does not: measured through its own lens, the sharp share is highest just inside
  the contour and fades toward the centre over a fixed distance, so the backdrop
  reads crisply where the eye lands — at the rim, where the lens bends it — and
  softens deeper in. This release carries that ramp.
  
  **What you see at 1x.** Inside the contour the pattern behind a surface is
  crisper than before and closer to Apple's, and the interior of a large platter
  shows more of what is behind it: a 280 px card's centre used to be 17% softer
  than Apple's and is now 12% crisper, with the band at the edge closer on every
  size measured. Small controls change least; large surfaces most.
  
  **What you see at 2x.** Nothing, in this release. On a Retina display Apple's
  interior is heavier than vitrea's on every size, so the gap there is in the
  body's deep value rather than in any ramp above it, and that is its own
  measurement. The ramp's 2x anchors are carried in the profile and are inert.
  
  **Both tiers carry it.** The WebGPU tier mixes per pixel by depth. The CSS tier
  has one `backdrop-filter` blur per surface and mixes it at the ramp's average
  over the surface, so a surface reads the same overall weight on either tier;
  the CSS tier's width is the 1x law at every device scale.
  
  **The body's widths are CSS pixels at every device scale, on both tiers.** A
  reading that made them device-pixel quantities on the WebGPU tier was carried
  into this wave, measured against Apple's heavier 2x interior, and withdrawn
  before landing; the 2x body is unchanged from 0.3.0.
  
  Nothing in your code changes. If you pass a material profile of your own, the
  scattering facet gains eight named constants — the ramp's start at a thin and
  a thick span and past the thickness knee, and its reach, each at 1x and 2x —
  and a profile that does not name them gets the measured ones.
  
  Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.61 and
  §5.68.
- 492168b: The refraction band at the edge of glass now has the shape of Apple's, not only
  its strength.
  
  Look closely at the rim of a Liquid Glass surface over a checkerboard and the
  band is a set of crisp lobes: the rows behind it reversed and compressed, a
  sharp fold where the bend is steepest, distinct lobes at the corners, a dark
  line inside the rim. Vitrea's band had the magnitude of that bend without its
  shape — the same depth of displacement spread as a smooth curve. This release
  carries the shape, measured from Apple's own field rather than assumed from
  its description.
  
  **A steeper profile.** The displacement across the band is one steep power
  along the material's own span law, so most of the bend sits in a narrow fold
  just inside the contour with the interior nearly still, which is what produces
  the reversed rows and the fold.
  
  **An ovalized direction.** On thick surfaces the bend runs along a direction
  blended toward the ellipse inscribed in the surface, so the band is magnified
  along the edge and the corners carry their own lobes; on thin controls the
  direction stays the rounded rectangle's. The change is a band between the two
  spans, continuous through a morph.
  
  WebGPU tier only, at 1x and 2x: the CSS tier has no lens (a `backdrop-filter`
  cannot displace), and it is unchanged. Every checkerboard size measured moved
  toward Apple's at both scales.
  
  Nothing in your code changes. If you pass a material profile of your own, the
  lens gains `lensProfileExponent`, `lensOvalization` and the two spans that
  grade it; a profile that does not name them gets the measured values.
  
  Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.49–§5.52
  and §5.59.
- 99ea455: The shadow under glass now changes with the content behind it, and adds light as
  well as removing it.
  
  Every glass surface cast one shadow at one strength, whatever it was standing
  over and however large it was. Apple's does not. Measured across its own
  material, the shadow is two things composited on one falloff, and this release
  carries both.
  
  **It reads the backdrop.** Below the size law's knee the shadow's depth is keyed
  on how light the content behind the surface is — full strength across the whole
  ordinary range, about a third of that over a near-white backdrop, and nothing at
  all over a black one. A small control on a white card was casting a shadow more
  than twice as dark as Apple's; that was the single largest visible error in the
  facet and it is gone.
  
  **It grows with the surface.** Above the knee the shadow deepens with the
  casting span rather than sitting at one amplitude, which is what "larger glass
  casts a deeper, richer shadow" means in practice.
  
  **It carries the backdrop's own light.** On the WebGPU tier a large surface's
  shadow adds a blurred copy of the light behind it underneath the darkening,
  which is why Apple's big platters do not read as a flat gray smudge. The CSS
  tier cannot paint that light — a `box-shadow` cannot reach the backdrop outside
  its own element — so it derives the single darkening that matches the pair,
  subtracting the light it cannot add from the depth it can, at the backdrop level
  it already reads. The two tiers therefore land on the same shadow over a flat
  backdrop and differ only in how they resolve a structured one.
  
  **Under Reduce Transparency the shadow goes flat**, at the one level Apple's
  does: the preference removes the adaptation, so every surface over every
  backdrop gets the same shadow rather than a scaled version of the adaptive one.
  
  Nothing in your code changes. If you pass a material profile of your own, the
  shadow's amplitude is now six named constants plus the second term's four rather
  than a single `outerShadow.occlusion`, and a profile still naming the retired
  one is refused with a message that names its replacements rather than silently
  rendering the shipped shadow.
  
  Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.62.

### Patch Changes

- @vitreajs/vitrea@0.4.0

## 0.3.0

### Minor Changes

- The tone glass settles to over its backdrop now follows the reference's measured
  response curve.
  
  0.2.0 gave glass a backdrop-luminance axis: a surface over dark content settles
  toward dark. The axis was right and its reading was wrong in two ways that only
  showed over structured content — a photograph, a pattern, text. Both tiers
  averaged the backdrop in linear light and fed that mean to a non-linear response,
  and an average taken before a non-linearity is not the average after it. And the
  response itself was a two-ended mix between "adapted" and "not", where the
  reference, measured across a sweep of solid and pitched backdrops, settles onto a
  curve of the backdrop's level whose ends move with surface size.
  
  Both are replaced.
  
  - **The reading is the encoded-space mean** — the average taken in sRGB, as the
    reference takes it. On the WebGPU tier the per-pixel path is corrected by the
    ratio of the two means, so adaptation stays local to each surface while its mean
    matches the model exactly. On the CSS tier the read stays one mean per backdrop
    source, now taken in that space.
  - **The response is a curve, not a switch.** The interior tone is a monotone curve
    through three measured anchors (dark, mid and light solid backdrops), with the
    anchors' settled levels as functions of surface size. Nothing was fitted beyond
    those anchors: on the probe's calibration bed the curve lands within 0.034 RMS
    where the previous form's best refit was 0.106.
  
  **What you will see.** Surfaces over mid-tone and busy content land closer to the
  reference's level; the near-black collapse, which was already right, is byte for
  byte what it was. The smallest surfaces over structured content keep a known
  residual, recorded rather than tuned away.
  
  Reduce-transparency and increase-contrast keep the behaviour they were fitted to:
  the response law rides only the un-degraded material.
  
  Through the material-profile seam the law is four named constants:
  `backdropToneAnchorX`, `backdropToneResponseThin`, `backdropToneResponseThick`
  and `backdropToneResponseStrength`.
- What you see through the glass is sharper and hazier at once.
  
  Everything inside a surface was one Gaussian blur of the backdrop at a single
  width. The reference, measured per pixel across the interior and the rim band, has
  two components: a **sharp** blur that keeps the structure of the content behind
  (the edges of text, the cells of a pattern) and a much wider **scatter** that lays
  a haze over it, mixed by an amount that grows with the surface's size on the same
  size law the thickness facets ride. One blur cannot be both, and refitting the
  single width could only trade one loss for the other.
  
  **This changes how every existing surface looks.** Content behind small controls
  reads through more clearly than before; large panels keep that legibility under a
  deeper haze. Both tiers move: the WebGPU tier mixes the two components per pixel;
  the CSS tier, which has one `backdrop-filter` blur, takes a single width at the
  mixed value, so its interior level matches the GPU tier's while its structure
  stays the tier's known limit.
  
  Nothing new to call. Through the material-profile seam the sharp width is
  `blurSigma` (now 1.25 CSS px on the light material), the scatter is
  `sizeScatterGainMax` on it, and the mix is `sizeScatterFloor` and
  `sizeScatterSpanMax`, both new.
- The refracting rim on the WebGPU tier is stronger, and it shows the content behind
  it rather than a blurrier copy.
  
  The rim band displaced the backdrop inward on the reference's lens profile — a
  (1 − depth)² curve over the lens depth — but at too small a magnitude, and it
  sampled the blur chain at a coarser level near the edge so the band came out
  softer than the interior. Measured per one-pixel depth shell around the whole
  contour, the reference's band is the same lens geometry at 1.6 times the
  displacement, reading the same two-component body as the interior: no extra blur,
  no sharper rim, no darkening. The shader now samples the body at the displaced
  position with one gain constant, `lensRefractionGain` (1.6), and the two rim-LOD
  constants (`lensBodyLodPerPx`, `lensRimLodBias`) are retired from the
  material-profile seam.
  
  **What you will see** on the WebGPU tier: a more pronounced refraction at every
  edge, with the displaced content as legible as the interior. The CSS tier carries
  no lens and is unchanged here. The refraction policy's three rungs — `none`,
  `approximate`, `true` — keep their meaning; the gain scales the lens they select.
- A texture backdrop is sampled where it sits on the page, not stretched over the viewport.
  
  Until now the WebGPU tier fitted every registered image, canvas or video to the whole plane
  with a cover fit, so a backdrop smaller than the viewport was sampled magnified and offset —
  a 320 px raster behind a control on a 1440 px page was stretched four and a half times, and
  the glass over it refracted the wrong pixels. The calibration harness never saw it because
  its texture is the whole stage, which made the fit an identity; the demo did, and rendered a
  flat slab where the harness rendered translucent glass over the same scene.
  
  `setBackdropTexture` now tracks the element you hand it — an `<img>`, `<canvas>` or `<video>`
  in the document — through the same batched read protocol the hosts use, and the shader maps
  the plane onto that box every frame, following scroll and resize. A source without a box
  (an `ImageBitmap`, an `OffscreenCanvas`, a detached element) can declare one:
  
  ```ts
  root.setBackdropTexture("hero", { kind: "image", image: bitmap, placement: { kind: "rect", rect } });
  ```
  
  With neither, the old cover fit still applies and a dev-mode finding names the rule. Blur and
  lens widths now read the texture's real density (texels per CSS px), so a 2× raster displayed
  at half size blurs by the same CSS width as a 1× one. Outside the box the edge texel is
  clamped; a surface hanging past its backdrop's edge is recorded as a known limit.
- A tinted surface is now an opaque shade of its colour, the way the reference's is.
  
  0.2.0's `tint` laid the seed colour over the material as a translucent wash at the
  material's own alpha. The reference, read per pixel, does something else: it
  renders an **opaque, hue-preserving shade of the seed** whose brightness follows
  the untinted material's own local luminance — darker where the glass sits over
  dark content, the seed itself over light — and composites that shade over the
  material at the strength the author gave. Between the wash and the shade the two
  tiers disagreed on a tinted interior's level by 27–64% over textured content, and
  no tone constant could close it, because a wash has no tone to fit.
  
  **This changes how every tinted surface looks**: more saturated and more solid,
  less like a stain on the glass. The API does not change — `tint` on a surface or a
  group, as any CSS colour, its alpha as the strength — but one sentence of 0.2.0's
  promise does. A tint no longer leaves the surface's opacity alone: at full
  strength it is an opaque shade, because the reference's is, and at half strength
  the surface is half shade and half material. What stays fixed is the material's
  own opacity — the value reduce-transparency and increase-contrast operate on —
  and the policies still resolve before the tint is composited, so a tint can never
  quietly undo a dimming policy.
  
  - Both tiers render the same law. On the CSS tier the author layer folds into the
    material's single `rgba()` layer exactly, which also removes the gamut clip a
    saturated seed could hit on that tier: the fold is convex and cannot leave the
    gamut.
  - On the dark scheme the layer is the pure seed: the reference shades the tint
    only on the light material.
  
  Through the material-profile seam the tone-map constants of 0.2.0
  (`tintToneFloor`, `tintToneCeilMix`, `tintToneLow`, `tintToneHigh`) are gone,
  replaced by `tintShadeDark`, `tintShadeLight` and `tintShadeStrength`; the
  exported helpers follow them (`TINT_TONE` → `TINT_SHADE`, `tintTone` →
  `tintShade`, `resolvedTintTone` → `resolvedTintShade`, `TintToneConstants` →
  `TintShadeConstants`).

### Patch Changes

- A WebGPU-tier surface that samples nothing now composites over what is beneath it.
  
  When the WebGPU tier draws a surface without a captured backdrop — over another
  glass surface's DOM proxy, or over the page itself — it used to write the material
  mixed over black, opaque, so whatever was beneath never showed through. Glass
  nested over glass was the visible case: the upper pane rendered at a flat 0.47
  luminance against the reference's 0.89. It now leaves the optics pass as a
  premultiplied layer at the material's alpha, with the outer shadow clipped to the
  surface's coverage, and the browser composites it in the same encoded space the
  CSS tier's `rgba()` lands in. A surface that samples a texture takes the previous
  path byte for byte.
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
