# Grounds

Refraction only bends what's beneath it. A glass surface is a lens, not a
paint color — remove the thing being lensed and the effect has nothing left
to prove it's there. **Glass over a blank or flat-gray ground is banned.**
The ground is not a backdrop decision made after the glass; it's decided
alongside it. Name the ground plan in the DESIGN.md material commitment the
same way the glass treatment itself is named — which of the three sources
below, and why it fits the surface's register.

Three sources cover the space. Pick one per surface; don't mix without a
reason.

## Authored SVG/gradient grounds

The guaranteed baseline — no network, no asset pipeline, works in a
zero-dependency single file. Use this whenever real photography isn't
available (offline builds, restricted environments, a component that must
stay self-contained) or when the brand wants abstract atmosphere rather than
a literal scene.

The requirement is **edges, not just color**. Refraction reads by displacing
a boundary — a hue transition, a band edge, a shape outline — through the
lens. A field with nothing but soft color has nothing for the displacement
map to grab, so it renders as a faint tint shift at best. Two rules make an
authored ground refraction-worthy:

- **≥3 hue stops.** One or two colors read as a single wash; three or more
  distinct hues, layered as separate gradients, guarantee that some part of
  the frame is always crossing a hue boundary, wherever the glass sits.
- **Structural geometry.** At least one repeating or large-scale shape layer
  — `repeating-linear-gradient` bands, big SVG blobs, a diagonal stripe field
  — on top of the color. Gradients alone are still soft; geometry is what
  supplies hard, close-together edges for the lens to bend visibly.

Copy-adapt this block directly (it's the proven ground from the project's
glass displacement-map spike — same structure, rename the hues to fit the
brand):

```css
.svgf-ground {
  min-height: 100%;
  background:
    radial-gradient(60% 40% at 20% 10%, #ff9d5c 0%, transparent 60%),
    radial-gradient(50% 60% at 80% 30%, #4c7dff 0%, transparent 55%),
    radial-gradient(70% 50% at 50% 80%, #b04cff 0%, transparent 60%),
    repeating-linear-gradient(45deg, #141a33 0 40px, #0b0e1a 40px 80px);
}
```

Three radial hues (orange, blue, purple) supply the color variety; the
`repeating-linear-gradient` diagonal band stack supplies the structural edges
— 40px-wide stripes are close enough together that a glass element of almost
any size sits across several of them. Swap the hex values for the brand's
palette; keep the layer count and the repeating-band layer.

The trap to name explicitly: a **pure two-stop vertical gradient is still
"blank" for refraction purposes**, even though it isn't a flat color.

```css
/* BANNED as a refraction ground — a smooth wash, nothing to bend */
.flat-ground { background: linear-gradient(180deg, #1a1f35 0%, #0b0e1a 100%); }
```

Two color stops with no geometry produce a slope so gradual that a
displacement map finds no local contrast to redirect — the glass will look
like it's sitting on a solid panel, not lensing anything. If a ground is
"just a gradient," check it against the two rules above before shipping it
under glass.

**Choose authored grounds when:** the environment can't fetch images, the
brand wants abstract/atmospheric rather than literal, or the ground itself
is the fastest path to something rich enough to refract.

## Real photography

When the environment allows fetching images, real photography is the
richest ground available — genuine depth of field and lighting give
refraction far more to work with than any authored gradient.

Select for three properties, in order:

- **Depth-of-field layers.** A sharp subject against a soft background (or
  vice versa) gives the lens a near/far contrast to bend differently across
  the glass — flat, evenly-focused photography doesn't.
- **High local contrast.** Bright-against-dark detail near where the glass
  will sit — this is what makes the bezel's edge-bending actually visible,
  the same requirement structural geometry serves in an authored ground.
- **Diagonal structure.** A horizon, a rail, a shoreline, a beam of light —
  a diagonal line crossing the glass shows off angular displacement in a way
  a symmetric or perfectly axis-aligned scene doesn't.

Use the `images.unsplash.com` URL pattern this project's vs-Make eval arms
verified end-to-end (every URL curl-checked to a 200 before shipping):

```text
https://images.unsplash.com/photo-<id>?w=<width>&q=80&auto=format&fit=crop
```

Pick `<width>` for the actual render size (don't ship a 2200px image behind
a 360px glass pill), and keep `q=80&auto=format&fit=crop` — the compression
and crop params that kept the eval arms' pages fast.

Once the photo is chosen, extract its dominant hue into a `:root` custom
property and let the glass tint reference it, so the frost/tint color
harmonizes with the ground instead of fighting it:

```css
:root { --ground-hue: #2b4a63; }        /* sampled from the photo's dominant tone */
.glass { background: rgb(from var(--ground-hue) r g b / 40%); }
```

**Choose real photography when:** the environment permits fetching images
and the brand is campaign- or lifestyle-forward — travel, hospitality,
fashion, editorial — where a literal scene sells the mood faster than
abstraction can.

## Simulated product content

The ground **is** the product — this is the truest reading of Apple's own
model, where a glass control floats over the map you're navigating, the
video you're watching, or the waveform of the audio playing. There's no
separate "background" to source; the interface's real content supplies the
richness, and getting that content right is a design problem, not an asset
hunt.

Map tiles, a paused video frame, a chart field with live-looking series, a
waveform canvas — all qualify. Mock it with the same discipline the
figma-design skill uses for realistic content elsewhere in a build:
plausible values, plausible density, plausible shape — never lorem-ipsum
flatness or a single placeholder block standing in for what should be a rich
field. A mocked map with three generic gray blobs is exactly as "blank" as
the two-stop gradient above; a mocked map needs road-like line density and
label clutter before it earns the glass on top of it.

Worked sketch — a spatial-audio waveform field as layered SVG paths, the
kind of ground a "now playing" control's glass pill would sit over:

```svg
<svg viewBox="0 0 800 200" preserveAspectRatio="none" aria-hidden="true">
  <defs>
    <linearGradient id="wf-back" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3a4a8f"/>
      <stop offset="100%" stop-color="#171c38"/>
    </linearGradient>
    <linearGradient id="wf-front" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7fb2ff"/>
      <stop offset="100%" stop-color="#2d5bff"/>
    </linearGradient>
  </defs>
  <!-- ambient bed: low-amplitude, muted — reads as "room" -->
  <g fill="url(#wf-back)" opacity="0.55">
    <rect x="0"  y="86" width="6" height="28"/>
    <rect x="12" y="70" width="6" height="60"/>
    <rect x="24" y="94" width="6" height="12"/>
    <!-- … repeat at 12px pitch, amplitude drawn from a real render's RMS curve -->
  </g>
  <!-- foreground channel: the active track, saturated, taller peaks -->
  <g fill="url(#wf-front)">
    <rect x="0"  y="40" width="6" height="120"/>
    <rect x="12" y="60" width="6" height="80"/>
    <rect x="24" y="20" width="6" height="160"/>
    <!-- … amplitude bars, bar/gap ratio and peak variance modeled on a real track -->
  </g>
</svg>
```

Two layers — a muted back channel and a saturated front channel — give the
scene depth the way a photo's depth-of-field does; the bar edges give the
lens hard, closely-spaced boundaries to bend, same job the repeating bands
do in the authored ground. Drive bar heights from an actual amplitude curve
(even a plausible synthetic one — a voice-shaped hump, not uniform noise) so
the field reads as real audio, not a decorative pattern.

**Choose simulated product content when:** the surface's whole point is to
show the product's own data — a player, a map, a dashboard field — and
inventing a generic background beside it would be less honest than showing
the real thing.

**Ground choice by register.** The three sources aren't interchangeable
defaults; the surface's register picks one:

- **Product UI** prefers simulated product content — the ground IS the
  product, which is the closest match to Apple's own usage and the most
  honest choice for an interface whose job is to show real data.
- **Campaign/brand** surfaces prefer authored art or photography — a hero,
  a launch page, an editorial moment has no "real data" to be truthful to,
  so atmosphere (authored gradients) or scene (photography) carries the
  weight instead.

Whichever source is picked, it must still clear the edges test above — a
simulated map with no road detail, a campaign photo with no depth-of-field,
or an authored field with no structural geometry are all the same failure
wearing different clothes: a ground with nothing for the glass to refract.
