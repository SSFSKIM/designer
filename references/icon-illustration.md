# Single-mark deliverables

The brief asks for one primary graphic artifact, not a composed page. The page-stance taxonomy does not apply — pick drawing vocabulary, geometry, and palette that fit the specific mark on its own terms.

## Read the brief along five axes

Every brief specifies five things, explicitly or by silence:

1. **Subject** — the noun set, named tradition, or named object
2. **Treatment** — line vs. fill, monoweight vs. weighted, halftone, woodcut, stippled, iso, etc.
3. **Aesthetic register** — the emotional and cultural tone (precision, gravity, whimsy, warmth, austerity)
4. **Use context** — where the mark appears, at what size, against what ground
5. **Constraints** — explicit do's, don'ts, and hard requirements

Where the brief is silent, the silence is information: choose intentionally rather than fall to your default. Name the default you would have chosen by reflex, then ask whether the brief gives you a reason to pick something less obvious. If yes, deviate.

## Hierarchy of perception

A vector mark is read in three layers, in this order:

1. **Silhouette** — the outer contour
2. **Major positive and negative shapes** — what kind of thing this is
3. **Interior detail** — read last, often invisible at use scale

Spend your design budget in this order. Strong silhouette plus restrained interior beats weak silhouette plus elaborate interior at every scale. Most failed marks invert this — energy invested in details that disappear at use scale.

## Subject literacy: break your default before drawing

When the brief names a specific subject — an object, a profession, a cultural tradition, a historical period, a named style — your trained default for that word is almost certainly a generic composite, not the specific thing the brief implies. The default is sticky and will reassert itself unless you actively work against it. The instruction "be specific" is not enough; you need a structured pause.

Before drawing, run this in order:

1. **Sketch your default.** State the obvious first idea you would draw if working from instinct. Be concrete — the silhouette, the major shapes, the proportions.
2. **Name three features that distinguish the named version from that default.** Use shape-language, not adjectives. Reach for axes like proportion (*elongated rather than compressed*), adjacency (*elements interlock rather than abut*), stroke treatment (*weighted rather than monoweight*), termination (*tapered rather than blunt*), or symmetry (*off-axis rather than mirrored*).
3. **Apply the inversion test to each feature.** Ask: would this same feature also be true of a *generic* version of the noun, or of an adjacent member of the same category? If yes, the feature isn't distinguishing — it's a category trait, and you need to go one level deeper. Example: for "thatched roof," naming "overlapping bundled material" doesn't distinguish thatch from any other organic roof; pushing deeper gets you fan-shaped fronds, shaggy unfinished ends, and a thicker ridge cap. **If you can't produce three features that survive the inversion test, the brief is asking for visual literacy you may not have. Stop and pick a *named* reference** (a specific era, designer, regional tradition, or canonical example) and design from that reference rather than from the abstract subject. Do not proceed with category-level features as if they were specific.
4. **Verify your sketch against the three features.** If your sketch matches your default on any of the three, redesign that feature before continuing.

This explicit deviate-from-default pass is the single highest-leverage move on subject-named briefs. Skipping it is the most common failure.

## Element budget: 1:1 with the brief

Match visible elements 1:1 with the brief's explicit nouns. If the brief lists two things, the output has two things.

Before adding any element the brief did not name, run this test: *can I justify this from the brief, or only with phrases like "to add visual interest", "to balance the composition", "to fill space"?* If only the latter, the composition is wrong — fix the composition rather than add ornament.

Each unrequested ornament dilutes the primary forms by a measurable amount. Default rejections, unless the brief explicitly requests:

- Text labels, names, taglines, or wordmarks under or around the mark. Exception: brand-mark briefs that contain the brand name as a primary deliverable will say so explicitly.
- Decorative particles — stars, sparkles, ambient dots, floating accents
- Glow or drop-shadow filters beyond one subtle one
- Specular highlights or hot spots on lens, gem, or glass forms
- "Preview on context" mounts — the mark sitting on a card on a background. Render the mark only.

## Composition: optical, not mathematical

Mathematical center is the safe default and the generic default. Stronger marks usually do at least one of:

- Place heavy elements slightly above mathematical center (optical centering — the eye reads center as higher than the geometric midpoint)
- Anchor a primary heavy form off-axis and counter-balance with lighter elements (tension via asymmetry)
- Construct on rule-of-thirds, golden-ratio, or regular-polygon grids

Optical adjustments to apply by eye after construction:

- Round forms overshoot the geometric grid (a circle next to a square at the same nominal size reads smaller — extend the circle ~2–4%)
- Sharp corners and pointed forms under-extend (a triangle apex aligned to a square's edge reads as sticking out)
- Heavy elements pull perceived center; place them counter-weighted, not symmetrically

Mathematical alignment is wrong as often as it's right. Adjust by eye.

## Negative space is form

The empty regions inside and around the mark are part of the design. Test by inverting figure and ground: if the negative space is shapeless, the mark is incomplete. Strong marks have legible negative space — the empty shape reads as something deliberate.

This implies overlap and interlock over scatter-placement. When the brief lists multiple elements, ask whether one can notch into, occlude, or merge with another, rather than sit beside it on an empty field.

## Treatment and palette: one of each

Pick one drawing vocabulary — monoweight outline, geometric fill, halftone, woodcut, stippled, isometric — and hold it across every form in the mark. Mixing treatments reads as confusion unless the contrast is clearly motivated by the brief (e.g. all primary forms outlined, all secondary forms filled, with that contrast itself meaningful).

Default to monochrome plus one neutral. Add a second hue only when the brief or subject motivates it. Multi-stop gradients usually fight a mark's clarity — reach for them only when use context demands depth (an app-icon tile with explicit gradient brief; a logo for a brand whose identity includes gradient).

## Scale floor

Identify the smallest size at which the mark will be displayed and design to that floor:

- Favicon / browser tab: 16px
- Mobile homescreen icon: ~60px
- Desktop dock or row icon: ~32–48px
- Logo small instance: ~48px
- Print or large display: floor effectively unbounded

If the brief is silent on use context, infer the floor from the artifact type — an app-icon brief implies homescreen scale, a brand-logo brief implies favicon scale. Detail that does not survive at the floor does not belong in the design. Test by mentally rendering at the floor before declaring done.

## Output mechanics

- Render one self-contained `<svg>` in whatever file the project calls for (a standalone `.svg`, an inline component, or an HTML page); do not fragment a single mark across files.
- Single `<svg>` with a declared `viewBox` matching the brief's stated canvas dimensions.
- If the brief implies a tile (rounded square, circle badge, pin), render the tile as the first `<rect>` or `<circle>` *inside* the SVG, not as an outer `<div>`.
- Do not nest `<svg>` inside absolutely-positioned `<div>` wrappers — they fight on scale and produce unpredictable rendering.
- The page background should match the mark's own background so there is no visible seam at the canvas edge.

## Final check before declaring done

Run all four:

1. **Scale-floor render** — at the smallest use size, is the silhouette legible and the subject identifiable?
2. **Element count** — does every visible element map to an explicit brief noun, or has ornament drifted in?
3. **Negative space** — are the empty regions deliberate shapes, or accidental?
4. **Default check** — for each silent dimension and each named subject, did you actively deviate from your trained default, or did you fall to it?

If any answer is no, simplify or redesign before shipping.

## Execution mechanics

The sections above decide what the mark is and how it's composed. This section covers the mechanics of turning that decision into SVG: the coordinate grid, the choice between primitives and paths, stroke-vs-fill math, and how to verify optical balance in code rather than by eye alone.

### Grid construction

Default to a `0 0 64 64` viewBox unless the use context calls for something else:

|Use|Typical viewBox|
|---|---|
|Utility / UI icon|`0 0 24 24`|
|Small app or logo mark|`0 0 48 48` or `0 0 64 64`|
|App icon tile|`0 0 64 64`, `0 0 96 96`, or `0 0 128 128`|
|Crest / badge|`0 0 100 100` or `0 0 120 120`|
|Large standalone illustration|`0 0 256 256` or a composition-specific canvas|

A 64-unit viewBox against a 16px scale floor gives a four-to-one coordinate relationship (64 SVG units = 16 rendered pixels, 4 SVG units = 1 rendered pixel) — enough precision to make optical adjustments while still forcing simplicity.

Work in two grid layers, not one:

- **Structural grid** — major geometry lands on 4- or 8-unit increments (`x = 8, 16, 24, 32, 40, 48, 56`). This keeps the mark coherent.
- **Optical adjustment** — final coordinates deviate 0.5–2 units from the structural grid wherever the eye requires it (`x = 31.5, 47.8, 54.1`). This keeps it from feeling stiff. The shipped path data reflects the finished optical geometry, not the construction diagram.

### Primitives versus paths

Use a primitive when it remains visually true to the form: `<circle>`, `<ellipse>`, `<rect>` (including `<rect rx>` for a rounded capsule), or `<polygon>` when its vertices are meaningful. Reach for `<path>` when the silhouette itself is the identity — a custom mark, an organic interlocking form, or a negative-space cutout (via `mask`, `clipPath`, or an even-odd fill rule). Do not convert a circle or rectangle to a path just to make the source look more "designed" — it only makes the file harder to maintain.

Compute path coordinates at whichever of three levels the form calls for: geometric construction (`x = cx + r × cos(θ)`, `y = cy + r × sin(θ)` for points on a circle or polygon), proportional construction (anchor relationships first — silhouette top, bottom, optical center, left/right safe edges, primary mass center — then derive points from those anchors), and optical revision (the final 1–2 unit nudges: overshoot on a circular body, pull-back on a pointed top, a shift on a heavy lower-right mass, an off-center seam). For Bézier joins, establish endpoints before control points, match tangents at each end, keep smooth continuity across segments, reserve the quarter-circle constant (`k = 0.55228475`, handle distance `k × r`) for true circular arcs, and prefer 4–8 decisive outer-curve segments over a dozen tiny adjustments.

### Stroke versus fill

Choose fill when the mark must hold up at a 16px floor, the silhouette carries more identity than interior structure, or the subject reads through positive/negative mass alone. Choose stroke when the mark needs a diagrammatic, technical, or calligraphic feel, the floor is at least 24–32px, or it belongs to a monoweight UI icon system. Combine fill and stroke only when the stroke has a specific structural role — a keyline around a badge, a border defining a tile — not to make the mark look more elaborate.

The stroke width actually rendered depends on the canvas, not the number in the source. The formula:

```text
strokeWidth (SVG units) = desired rendered stroke width (px) × viewBox size ÷ rendered icon size (px)
```

Equivalently, check any candidate `strokeWidth` against its rendered result at the floor: `strokeWidth ÷ canvas × displaySize`. For a `64 × 64` viewBox targeting a 1.5–2px rendered stroke:

|Rendered size|SVG stroke width|
|---|---|
|16px|`6–8`|
|24px|`4–5.33`|
|32px|`3.5–4`|
|48px|`2.67–3.33`|
|64px|`2.5–3`|

At a 16px floor, favor fills and negative-space cuts over thin outlines — a stroke thin enough to look right at large sizes usually disappears or aliases badly at the floor.

### Optical-balance verification

Code can surface problems that eyeballing misses, but it cannot fully determine balance on its own — verify with rendered checks, not just the numbers:

- **Structural guide overlay.** During development, add a temporary `<g>` of centerlines, thirds, and safe bounds (low-opacity dashed strokes) over the mark, and remove it before shipping.
- **Render at real scale, not only large scale.** Render the same mark at the actual scale floor and adjacent sizes (16/24/32/48/64px) side by side. At the floor, check: does the silhouette remain distinct, is the subject still identifiable, is any internal cut still visible, does it read as centered, and does the negative space stay open rather than collapsing into a blob?
- **Inversion test.** Render the mark in both polarities — light mark on dark ground and dark mark on light ground. If the negative space goes shapeless, or a seam disappears, in either polarity, revise the mark rather than the rendering.
- **Bounding-box and visual-center check.** Don't blindly trust the geometric center of the viewBox. Compare it against where the filled mass actually sits and where the negative-space cutout pulls the eye; a heavy lower-right mass commonly needs the whole shape nudged 1–2 SVG units up or left.

### Worked example: coastal coffee roastery mark, 16px floor

Brief: "Create a mark for a coastal coffee roastery. It must work at 16px."

**Default-breaking pass.** The generic first idea — a coffee cup, plus steam lines, plus a wave underneath, plus a small sun or seagull — is disqualified before drawing: it's a familiar category-level coffee logo, it stacks too many separate nouns and decorative elements, at 16px the cup/steam/wave/sun would merge into noise, and it reads as "coffee near the ocean" rather than a distinctive roastery. Three differentiators replace it, each checked against the inversion test:

1. **Coffee bean as the main silhouette**, not a cup — a tall, tapered seed form with a heavier upper-left shoulder and a lower-right taper. A bean is more specific to roasting than a cup, and the outer silhouette alone carries identity at 16px.
2. **The bean's internal seam becomes a shoreline/tide cut**, not a centered symmetric crease — it begins narrow and high, sweeps low and broad like a shoreline, then rises back toward the lower-right edge. A generic bean seam is centered and symmetric; this asymmetric sweep implies coastal without a separate wave symbol.
3. **Weathered asymmetry instead of nautical decoration** in the outer contour itself — the left side more compressed, the upper-right shoulder fuller, the lower-right edge resolving into a narrower, wind-shaped taper. A generic bean icon is mirrored and vertically centered; this asymmetry carries the coastal, weathered feeling through the silhouette alone, with no literal sun, ship, anchor, bird, or wave added.

Construction plan: `64 × 64` canvas, 16px scale floor, a filled custom bean silhouette as the primary form, one negative-space tide seam as the secondary form, one ink color with transparent negative space, no stroke on the main silhouette, no gradients, shadows, text, or decorative particles. Safe bounds: left 9, right 55, top 7, bottom 58. The shape sits slightly above geometric center on purpose — geometric center is `y = 32`, but the perceived center of the heavy form is pulled up to about `y = 30.5` so the bean's lower body doesn't read as visually low.

Final SVG source:

```tsx
type CoastalRoasteryMarkProps = {
  className?: string;
  title?: string;
};

export function CoastalRoasteryMark({
  className,
  title = "Coastal coffee roastery mark",
}: CoastalRoasteryMarkProps) {
  const titleId = "coastal-roastery-mark-title";

  return (
    <svg
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-labelledby={titleId}
      className={className}
    >
      <title id={titleId}>{title}</title>

      <defs>
        <mask id="coastal-bean-mask">
          {/* Black hides; white reveals. */}
          <rect width="64" height="64" fill="black" />

          {/* Main coffee-bean silhouette. */}
          <path
            d="
              M31.5 7
              C44 6.5 53.2 17.1 54.1 28.7
              C55.2 41.4 46.9 55.1 34.4 57.3
              C22.5 59.4 10.3 50.6 9.4 38.2
              C8.5 25.7 17.3 8.5 31.5 7
              Z
            "
            fill="white"
          />

          {/* Negative-space seam: coffee crease + shoreline sweep. */}
          <path
            d="
              M30.5 12.3
              C22.6 20.4 17.8 30.3 19.6 39.4
              C21.7 49.9 31.8 53.7 40.3 48.7
              C43.3 46.9 46.2 43.6 47.8 40.2
            "
            fill="none"
            stroke="black"
            strokeWidth="6.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </mask>
      </defs>

      {/* currentColor lets the mark work in ink, white, or brand color. */}
      <rect
        width="64"
        height="64"
        fill="currentColor"
        mask="url(#coastal-bean-mask)"
      />
    </svg>
  );
}
```

Key coordinate decisions, condensed from the full construction:

- **Top anchor `M31.5 7`** — not `y = 8` or `y = 10`. The heavier lower body pulls visual mass downward, so the top needs a little upward overshoot; `x = 31.5` avoids a mechanically centered feel.
- **Upper-right shoulder `C44 6.5 53.2 17.1 54.1 28.7`** — the fullest part of the silhouette. The near-horizontal start toward control point `(44, 6.5)` creates a calm, shallow shoulder rather than a peak, giving the bean a wind-shaped asymmetry; the endpoint stays broad enough to survive at 16px.
- **Lower-right taper `C55.2 41.4 46.9 55.1 34.4 57.3`** — deliberately does not mirror the upper-right curve; it narrows and pulls inward so the seam has somewhere to resolve without becoming a symmetrical bean slit, landing at `y = 57.3` for a 6.7-unit bottom margin.
- **Left compression `C22.5 59.4 10.3 50.6 9.4 38.2` / `C8.5 25.7 17.3 8.5 31.5 7`** — slightly more compressed than the right side, counterbalancing the fuller upper-right shoulder; perfect symmetry would read as generic, restrained asymmetry keeps it readable.
- **The seam/tide line `M30.5 12.3 C22.6 20.4 17.8 30.3 19.6 39.4 C21.7 49.9 31.8 53.7 40.3 48.7 C43.3 46.9 46.2 43.6 47.8 40.2`** — the mark's central conceptual move: it begins near the upper third, drifts left and down as though entering a coastal inlet, broadens through the lower half, and returns upward toward the right without closing into a centered coffee-bean split.
- **Stroke-width check on the seam mask** — `strokeWidth="6.5"` on a 64-unit canvas rendered at 16px is `6.5 ÷ 64 × 16 = 1.625px`, thick enough to stay legible as a negative-space cut.
- **Mask instead of a background-colored stroke** — the seam is cut with a `<mask>` rather than painted in a specific paper color, so it renders correctly against any background: the cutout always reveals whatever sits behind the mark, which is what lets the same component work in ink-on-paper and paper-on-ink polarities without a separate variant.

At the 16px floor, the expected read is: primary, a distinctive coffee bean; secondary, a flowing internal split; tertiary, a coastal, weathered asymmetry. If the mark reads only as "an oval with a line," the fix is to revise the silhouette or the seam — not to add a sun, wave, or coffee cup.
