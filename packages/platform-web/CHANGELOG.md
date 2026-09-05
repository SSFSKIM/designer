# @vitreajs/vitrea-web

## 0.8.0

### Minor Changes

- 4e7e75b: An author tint below full strength now draws the material it always meant to on
  the CSS tier.
  
  **What you see.** Give a glass surface a tint whose alpha is less than 1 —
  `rgba(255, 149, 0, 0.2)`, say — and on Chromium the CSS tier drew a surface that
  did not match the WebGPU tier drawing the same profile, by up to 0.068 of interior
  level at strength 0.1 and with a hue shift on top of it. At full strength the two
  tiers agreed exactly, which is why the ten strengths in between went unmeasured
  for four releases. They agree now: the tier's composite is the renderer's own
  expression, `(1 − s)·material + s·layer` in the page's own space, at every
  strength. Measured over both seeds, six strengths, two backgrounds and two device
  pixel ratios, the tier is within 0.005 of the WebGPU tier on every cell, and the
  cross-tier colour difference falls by 0.003 to 0.032 of OKLab ΔE on every tinted
  cell below full strength.
  
  Two things were wrong and both are fixed by putting the right colour in one place.
  The transfer table that carries the material inside the tier's filter was solved
  against the tint-folded colour rather than the material's own, which on a
  saturated seed drove the table past the end of its range on one channel — a
  per-channel loss, inside the filter, that no downstream stage can undo. And the
  author's layer was drawn at the author's own opacity over a table solved for a
  different overlay, so the two composed to the intended material only where the
  layer was opaque. The table is now solved on the untinted material, and the
  author's layer is folded over the tier's contrast-floor overlay before it is
  written.
  
  **The contrast floor holds at every strength now.** The tier keeps a real element
  paint under its filters so that an engine which reports support and renders no
  filter still leaves a surface rather than nothing. A tint at strength 0.1 used to
  replace that paint with one at alpha 0.1, well under the floor of 0.2668; the
  folded overlay's alpha is 0.34 there and is never below the floor at any strength.
  
  **What does not change.** The WebGPU tier is byte-identical. An untinted surface's
  declarations are byte-identical, and so is a tinted surface at full strength. The
  dark scheme and any surface whose composite puts it on the encoded form keep the
  whole-material fold they had, as do Firefox and Safari, which have no reference
  filter to carry the material in. No public API moves and no layer or filter
  primitive is added — a tinted surface's filter is now the untinted surface's, so a
  tinted group needs one definition fewer than before.
  
  **The named gaps.** Under increased contrast the tinted composite sits within 0.006 of
  the WebGPU tier at full strength; the untinted material on that profile sits 0.023 to
  0.026 above it, which is the preference fold's own standing gap, unchanged by this
  work. The tint's shade is read once per surface on this tier and per pixel on the
  WebGPU tier. Over a photograph or a checkerboard that is worth under 0.003 of interior
  level; over black text on white it is 0.013, because the WebGPU tier's shade darkens
  under each glyph and this tier's does not. Both tiers sit above Apple's own capture
  there, the WebGPU tier by 0.017, so the item is recorded against Apple and not only
  across the tiers.
- 2d11305: The CSS tier's outer shadow leaves its own blurred backdrop.
  
  **What you see.** A group of glass surfaces stops darkening itself. Until now the
  tier drew each surface's outer shadow on the host element, and the host's three
  filter layers are that host's own children — so every surface blurred its own
  shadow into its own body, and a surface later in the document blurred its earlier
  neighbours' shadows in as well. On a three-button toolbar over a patterned page
  that cost 0.012 to 0.015 of the material's interior level against the WebGPU tier
  drawing the same profile; it now costs 0.003 to 0.009. The shadow itself is
  unchanged in colour, offset, spread, blur and reach — it is the same shadow, in
  the same place, painted after the filters that used to read it instead of before
  them.
  
  Two carriers do it, and which one a group got is on the resolved state as
  `GlassGroupState.cssShadow`. A lone surface puts its shadow on the tier's own
  overlay layer (`"layer"`). A group with more than one member paints every
  member's shadow from the group's last-painted host, one inert child per member,
  clipped out of every member's body (`"group"`). A host whose own `overflow` clips
  its children keeps the shadow where it was, because a shadow on a clipped child is
  not a dimmer shadow but no shadow at all (`"host"`).
  
  **What does not change.** The WebGPU tier is byte-identical on all six calibration
  profiles at both scales. No public API moves; nothing is added to a lone surface's
  DOM; the added elements are `aria-hidden`, not hit-testable and not focusable, and
  the frame-cost knee is where it was. Every accessibility regime and forced colors
  behave as before.
  
  **The named gaps.** What is left after the removal is the CSS filter reading the
  element's own border box rather than the page around it, which shows on small
  boxes over structured backdrops: about 0.005 of interior level on a 44 px square
  at 1x, near zero on a 120 x 44 capsule, and sign-flipped at 2x. It is carried as a
  measured bound per box and scale, not as a fitted correction.
  `checkerboard__capsule-button` at 2x sits at +0.0102 of cross-tier level for that
  reason. Under reduced transparency and increased contrast the three-up cell is
  +0.0139 and -0.0281 against the WebGPU tier, both outside the 0.01 the wave asked
  for and both recorded. The stacked-glass scene is unmoved: its residual is the
  WebGPU tier's own unsampled material on a DOM-sourced group, not this tier's.

### Patch Changes

- @vitreajs/vitrea@0.8.0

## 0.7.0

### Minor Changes

- 5868672: The CSS tier's interior now sits at the same level as the WebGPU tier's.
  
  Since 0.6.0 the CSS tier has drawn the glass body the way the WebGPU tier does, but
  its interior read lighter: 0.02 to 0.06 above the WebGPU tier and above Apple's on
  structured backdrops, because the tint was laid over the blurred backdrop as an
  encoded overlay while the renderer lerps toward the tint in linear light, and one
  overlay alpha cannot match a linear lerp in both level and slope. Two smaller
  defects sat underneath: the tier applied the size law's occlusion after the tone
  response where the shader applies it before, and it did not carry the renderer's
  inner shadow at all.
  
  **What you see.** Behind a surface on a light or structured backdrop the CSS tier's
  glass now reads at the same brightness as the WebGPU tier's and as macOS's, where
  it used to read whiter. On Chromium the tint's lerp runs inside the linear-light
  filter the tier already uses, exact per pixel, over a thin element-painted tint that
  keeps the tier's contrast floor; the mirror computes its alpha in the shader's order
  and carries the inner shadow. Measured against the WebGPU tier, the interior level
  is within 0.01 on every light calibration cell but two, similarity rises on every
  light checkerboard row, and cross-tier colour difference falls on the fitted
  profiles. The reduced-transparency capsule that lost its silhouette in 0.6.0
  conditions again.
  
  **What does not change.** The WebGPU tier is byte-identical on every capture. Dark
  composites keep the encoded overlay, because the filter's eight-bit linear
  intermediate would posterize them; the group state reports which form drew as
  `cssTint: "linear" | "encoded"`, beside `cssBody`. Firefox and WebKit keep the
  encoded overlay at the corrected alpha. The host element, its children and the
  accessibility tree are as in 0.6.0; the cost knee is unmoved.
  
  **Known gaps, named.** Surfaces whose contour is a union of several shapes (a
  toolbar group, glass over glass on a photo) still read 0.01 to 0.015 darker than
  the WebGPU tier; the cause is measured to the box arrangement and not yet
  attributed. Three light solids and one text cell now sit so close to their
  background that the calibration's silhouette extractor cannot condition them; they
  are named in the predicate list and still gate on every perceptual row.
  
  Nothing in your code changes. The material profile is read as before; no new
  constant is fitted. The mapping's declared reference backdrop level is no longer
  read on the Chromium path.
  
  Measured against macOS 26.5 and the WebGPU tier and recorded in
  `c9a-fidelity-claims.md` §5.74 to §5.76.

### Patch Changes

- @vitreajs/vitrea@0.7.0

## 0.6.0

### Minor Changes

- 64457d0: The CSS tier now draws the glass body the way the WebGPU tier does.
  
  Every previous release drew the CSS tier's body as one `backdrop-filter` blur on
  the host element at a single width, the area average of the material's law. Apple's
  body is two components — a sharp one that keeps the backdrop legible and a heavy
  one that dissolves it — mixed by a ramp that fades the sharp share from the rim
  inward, and the WebGPU tier has drawn it that way since 0.3.0. On the CSS tier
  one blur cannot carry a sharp component, so behind a mid or large surface the
  backdrop's structure read 30 to 60 percent flatter than Apple's.
  
  **What you see.** The CSS tier creates three children inside your host element,
  below its content: a sharp filtered layer, a heavy filtered layer over it whose
  share follows the material's depth ramp as a raster mask, and the tint with the
  press glow and the rim above both. Behind a surface the backdrop's structure now
  reads the way it does on macOS and on the WebGPU tier: crisp at the rim,
  dissolving toward the centre. On Chromium the two blurs run through an SVG filter
  in linear light, which is the space Apple blurs in; on other engines they are
  plain `blur()` filters. The whole-crop similarity to Apple's captures rises on
  every checkerboard cell at 1x, holdout included, and the interior's spread of
  backdrop structure lands within 0.007 of Apple's at 1x and 0.016 at 2x on every
  calibration span.
  
  **What does not change.** The WebGPU tier is byte-identical on every capture. The
  host element keeps its box, its radius, its outer shadow and its tokens; the
  children are absolutely positioned, `aria-hidden`, and take no pointer events, so
  layout, hit testing and the accessibility tree are as before. Both blur widths are
  device-pixel quantities through the live ratio, as the WebGPU tier's are, and take
  the renderer's effective kernel width measured on its own captures.
  
  **Two things to know.** The CSS tier's interior reads lighter than Apple's and the
  WebGPU tier's on structured backdrops by 0.06 to 0.09 in level: an encoded CSS
  overlay cannot match the renderer's linear composite in both mean and slope with
  one alpha, and the conversion that closes it needs a renderer measurement that is
  its own item. And a group whose two filtered layers would cover more than 0.4
  million device pixels per frame collapses to one layer, the previous single-blur
  form, which `GlassGroupState.cssBody` reports as `"collapsed"`; below that budget
  it reports `"two-layer"`. The conformance table gains `maskOnBackdropFilter`,
  and the mask and the linear-light filter are gated on it: an engine that has not
  been verified draws two plain blurs at flat opacity.
  
  Nothing in your code changes. If you read the host's `backdropFilter` style in a
  test, read the first child's instead.
  
  Measured against macOS 26.5 and recorded in `c9a-fidelity-claims.md` §5.71 to
  §5.73.

### Patch Changes

- @vitreajs/vitrea@0.6.0

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
