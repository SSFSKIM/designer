# Grain & print

The editorial/craft family. Read `filter-mechanics.md` first for the sRGB,
filter-region, and premultiplied-alpha rules — this file assumes all three.
This chapter **extends, not replaces,** `effects-policy.md`'s Grain section
(root `references/effects-policy.md`, figma-design's) — its numbers are the
base every recipe here still honors: opacity `0.025–0.08`, a fixed tile of
`128–256px`, applied once per page or major section rather than per card,
never animated, disabled under `prefers-contrast: more`. Where that file
stops at "here's a safe background texture," this one goes deeper: grain
variants, duotone as an actual ink-mapping technique (not a mood filter),
halftone dot-screens for imagery, and the letterform-level ink-bleed and
rough-edge treatments print stances reach for.

## Grain

The mechanism is a **baked-tile static `feTurbulence`** — `type="fractalNoise"`,
`baseFrequency` in `0.6–0.9` for this family's film/paper-grain register,
`stitchTiles="stitch"` so the tile repeats seamlessly, and a **fixed `seed`**
that is never scripted. It renders once at paint, then sits in the compositor
as a cached background texture — see filter-mechanics.md's Performance floor.

```html
<svg width="0" height="0" aria-hidden="true" style="position:absolute">
  <filter id="svgf-grain" color-interpolation-filters="sRGB"
          x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="3"
                  seed="7" stitchTiles="stitch" result="noise"/>
    <feColorMatrix in="noise" type="saturate" values="0"/>
  </filter>
</svg>
```

Two variants, same base chain:

- **Luminosity-only grain** (the default above) — the trailing
  `feColorMatrix type="saturate" values="0"` desaturates the raw turbulence
  output. Raw `fractalNoise` is colored RGB static; left alone it reads as
  cheap TV-noise, not film grain. Use this everywhere the effects-policy
  base recipe already applies.
- **Colored paper fields** — drop the `feColorMatrix` step and keep the
  saturated noise. The channel variance carries a warm or cool cast that
  interacts with the tinted ground underneath (`mix-blend-mode: multiply` or
  `overlay`), reading as dyed or aged stock rather than neutral texture.
  Push opacity toward the low end (`~0.03`) here — colored noise is busier
  than mono at the same opacity.

Never animate either variant — no seed stepping, no `baseFrequency`
transition. That's squigglevision territory (atlas §2.4), a different family
with a real per-frame CPU cost; grain here is a texture, not a motion effect.

## Duotone as print technique

Duotone here means a **two-ink mapping**: desaturate to gray, then run each
channel through a `feComponentTransfer` table ramp from a shadow ink to a
highlight ink — `feColorMatrix`/`feComponentTransfer` chained per the atlas's
color-grading recipes (§2.7), with table values that are never picked by
eye: they're the ink pair's hex, converted to `0–1` fractions per channel.

The in-repo precedent: the vs-Make eval's film-festival page
(`figma-design-workspace/comparison-vs-make/prompt-2-film-festival/`)
shipped a riso two-ink look — deep marine `#152230` as the shadow ink, flare
orange `#F0632E` as the highlight ink — as its entire photography treatment.
That pair is the worked example below; the register it serves (riso,
letterpress, screenprint — a physical two-ink process) is exactly what this
section is for.

Conversion, done explicitly so it's checkable — divide each hex channel by
255:

| Ink | R | G | B |
|---|---|---|---|
| `#152230` (shadow) | `21/255 = 0.0824` | `34/255 = 0.1333` | `48/255 = 0.1882` |
| `#F0632E` (highlight) | `240/255 = 0.9412` | `99/255 = 0.3882` | `46/255 = 0.1804` |

```html
<feColorMatrix type="saturate" values="0" result="gray"/>
<feComponentTransfer in="gray">
  <feFuncR type="table" tableValues="0.0824 0.9412"/>
  <feFuncG type="table" tableValues="0.1333 0.3882"/>
  <feFuncB type="table" tableValues="0.1882 0.1804"/>
</feComponentTransfer>
```

Three or more `tableValues` per channel gives a tritone (a third ink at the
midtone); two is the standard duotone.

**The v1/v2 boundary (locked decision 7), stated explicitly:** duotone **as
a print technique** — an explicit ink pair, tied to a two-ink production
register, mapped via a real `feComponentTransfer` table — is in scope for
this file. Duotone **as standalone color-grade art direction** — picking two
brand colors to mood-grade a hero photo with no ink/print register behind
the choice — is **v2, out of scope here.** If a brief wants "duotone" purely
as a color treatment with no editorial/craft/archival/riso stance backing
it, that's a different (future) chapter, not this recipe reused off-label.

## Halftone

The dot-screen chain, from the atlas §2.9, Chromium-safest of the paper/print
family:

```html
<filter id="svgf-halftone" color-interpolation-filters="sRGB"
        x="0" y="0" width="100%" height="100%">
  <!-- one 8x8 dot cell, tiled -->
  <feFlood flood-color="black" result="ink"/>
  <feImage href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='8' height='8'%3E%3Ccircle cx='4' cy='4' r='3' fill='black'/%3E%3C/svg%3E"
           x="0" y="0" width="8" height="8" result="cell"/>
  <feTile in="cell" result="screen"/>
  <!-- gray the source, sum against the screen, then threshold to 1-bit dots -->
  <feColorMatrix in="SourceGraphic" type="saturate" values="0" result="gray"/>
  <feComposite in="gray" in2="screen" operator="arithmetic"
               k1="0" k2="1" k3="1" k4="-0.5" result="sum"/>
  <feComponentTransfer in="sum">
    <feFuncR type="discrete" tableValues="0 1"/>
    <feFuncG type="discrete" tableValues="0 1"/>
    <feFuncB type="discrete" tableValues="0 1"/>
  </feComponentTransfer>
</filter>
```

Principle: gray plus a dot ramp, thresholded — where the source is dark,
more of each dot cell survives. **Chromium-safest caveat:** `feImage` +
`feTile` interop varies across engines (atlas §1.4/§1.5); treat this as a
Chromium-verified enhancement, not a cross-engine guarantee. Where
portability matters more, the atlas's turbulence-based alternative
(`feTurbulence` high-frequency → arithmetic → discrete) gives a
mezzotint/risograph texture instead of a clean screen, and renders
consistently everywhere.

**Halftone is for imagery and illustration only, never body text.** A dot
screen coarse enough to read as halftone at photo scale turns text into
moiré noise at reading size — apply it to a `<img>`/illustration layer, not
a text node, ever.

## Ink bleed and edge roughening

Two related letterform-level moves, both display-type only.

**Ink bleed** — `feTurbulence` feeding a **low-scale** `feDisplacementMap` on
the glyph's own alpha, simulating ink spreading into paper fiber at the edge
of a printed letterform:

```html
<filter id="svgf-ink-bleed" color-interpolation-filters="sRGB"
        x="-15%" y="-15%" width="130%" height="130%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2"
                seed="3" stitchTiles="stitch" result="noise"/>
  <feDisplacementMap in="SourceGraphic" in2="noise" scale="4"
                     xChannelSelector="R" yChannelSelector="G"/>
</filter>
```

`scale` stays **≤4** here — an order of magnitude gentler than the atlas's
`5–15` deckled-edge scale for shape outlines (§2.9), because letterform
legibility degrades far faster with displacement than a photo edge does.
Apply only to display type set at roughly `24px` and up (the research atlas's
§3.1 text-filtering note, `docs/research/svg-filter-atlas.md`) — a headline,
a wordmark, a pull-quote initial, a poster numeral.

**Ink bleed and edge roughening never appear on body text.** Any paragraph,
label, or reading-size run of text stays outside this filter's `<g>` — the
same displacement that reads as "hand-printed headline" at 60px reads as
"blurry, hard-to-read paragraph" at 16px.

**Rough-outline variant** — `feMorphology` dilation, then turbulence-displace
the dilated silhouette before coloring it, per the atlas's rough/organic
border move (§2.6):

```html
<filter id="svgf-rough-outline" color-interpolation-filters="sRGB"
        x="-20%" y="-20%" width="140%" height="140%">
  <feMorphology in="SourceAlpha" operator="dilate" radius="2" result="fat"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2"
                seed="5" stitchTiles="stitch" result="wobble"/>
  <feDisplacementMap in="fat" in2="wobble" scale="6"
                     xChannelSelector="R" yChannelSelector="G" result="rough"/>
  <feComposite in="rough" in2="SourceAlpha" operator="out" result="ring"/>
  <feFlood flood-color="#1a1a1a" result="paint"/>
  <feComposite in="paint" in2="ring" operator="in" result="border"/>
  <feMerge>
    <feMergeNode in="border"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

The `-20%/140%` region matches the atlas's own sticker-border padding for a
comparable dilate radius — enough bleed for `radius="2"` dilation plus
`scale="6"` displacement (worst case ~8px of reach) without clipping.

## Registers

Four stances this family serves, each pulling a different subset of the
sections above:

- **Editorial** — mono luminosity grain at the low end of the opacity range,
  duotone photography when the brief has a real two-ink identity, no ink
  bleed (editorial type stays crisp).
- **Craft** — colored paper-field grain, warmer tints, occasional rough
  outlines on badges or stamps; texture is allowed to show more than
  editorial's restraint permits.
- **Archival** — mono grain plus a vignette (the paper-ground recipe below),
  duotone on photography to unify a mixed-source image set, minimal or no
  ink bleed.
- **Riso** — the fullest expression: colored grain, a hard two-ink duotone
  pair, halftone on imagery, ink bleed on display type. This is
  `references/stances.md`'s `risograph` entry in filter form — "grainier,"
  "flat, fully saturated spot-ink colors," "printed rather than
  screen-native."

All four pair with `grounds.md`'s **Authored SVG/gradient grounds** —
grain-print treatments are themselves an authored, abstract surface, not a
photographic or live-product ground, so they layer on top of that ground
family rather than real photography or simulated product content.

## Recipe: full-page paper ground

Tile plus tint plus vignette, complete and paste-ready — the page-level
material a riso or archival stance sits on top of.

```html
<div class="svgf-paper-ground">
  <!-- page content -->
</div>

<style>
  .svgf-paper-ground {
    position: relative;
    min-height: 100vh;
    background-color: #ede6d8;
    isolation: isolate;
  }

  .svgf-paper-ground::before {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.06;
    mix-blend-mode: multiply;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n' color-interpolation-filters='sRGB' x='0' y='0' width='100%25' height='100%25'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='3' seed='7' stitchTiles='stitch' result='noise'/%3E%3CfeColorMatrix in='noise' type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 200px 200px;
  }

  .svgf-paper-ground::after {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background: radial-gradient(120% 90% at 50% 40%, transparent 55%, rgb(20 15 8 / 18%) 100%);
  }

  .svgf-paper-ground > * {
    position: relative;
    z-index: 1;
  }

  @media (prefers-contrast: more) {
    .svgf-paper-ground::before {
      display: none;
    }
  }
</style>
```

Tile: the `::before` layer, a self-contained data-URI (no page-level `<svg>`
defs needed) — the same luminosity-grain chain from Grain above, at `200px`
(inside `128–256px`) and `0.06` opacity (inside `0.025–0.08`). Tint: the
flat `#ede6d8` warm-paper `background-color`. Vignette: the `::after` radial
gradient, darkening the corners without a second filter. One wrapper, one
grain layer, one vignette — section-scoped by construction, never per card.

## Recipe: duotone photo treatment

Ink-pair tokens in `:root`, plus the marine→flare duotone filter from
Duotone above, applied to a self-contained mock still so the recipe renders
fully offline with no network fetch. Swap the mock `<g>` for a real `<img>`
(via `grounds.md`'s `images.unsplash.com` pattern) in production — the
filter attaches identically either way: `filter: url(#svgf-duotone-marine-flare)`
in CSS on an `<img>`, or `filter="url(#svgf-duotone-marine-flare)"` inline
on an SVG `<g>`.

```html
<style>
  :root {
    --ink-marine: #152230;
    --ink-flare: #f0632e;
  }

  .duotone-frame {
    max-width: 480px;
    background: var(--ink-marine);
    padding: 12px;
  }

  .duotone-frame figcaption {
    margin: 8px 0 0;
    font-family: ui-monospace, monospace;
    font-size: 13px;
    letter-spacing: 0.02em;
    color: var(--ink-flare);
  }
</style>

<figure class="duotone-frame">
  <svg viewBox="0 0 480 320" width="480" height="320"
       xmlns="http://www.w3.org/2000/svg" role="img"
       aria-label="Mock festival still, marine-to-flare duotone treatment">
    <defs>
      <!-- tableValues are --ink-marine / --ink-flare above, converted to 0-1
           fractions per channel (see Duotone as print technique); SVG
           attribute lists don't accept var(), so keep these two in sync
           by hand whenever the ink pair changes -->
      <filter id="svgf-duotone-marine-flare" color-interpolation-filters="sRGB"
              x="0" y="0" width="100%" height="100%">
        <feColorMatrix type="saturate" values="0" result="gray"/>
        <feComponentTransfer in="gray">
          <feFuncR type="table" tableValues="0.0824 0.9412"/>
          <feFuncG type="table" tableValues="0.1333 0.3882"/>
          <feFuncB type="table" tableValues="0.1882 0.1804"/>
        </feComponentTransfer>
      </filter>
    </defs>
    <g filter="url(#svgf-duotone-marine-flare)">
      <rect width="480" height="320" fill="#dcdcdc"/>
      <rect y="200" width="480" height="120" fill="#8a8a8a"/>
      <circle cx="360" cy="90" r="46" fill="#f4f4f4"/>
      <polygon points="120,230 150,180 180,230" fill="#3a3a3a"/>
      <rect y="290" width="480" height="30" fill="#1a1a1a"/>
    </g>
  </svg>
  <figcaption>DIR. — VENUE, 2026</figcaption>
</figure>
```

The mock still spans near-black (`#1a1a1a`) to near-white (`#f4f4f4`) so the
full duotone ramp is visible; a real photograph carries the same range
naturally. `figcaption` styles off `--ink-flare` directly, so the ink pair
is a real, reusable token set — not just numbers baked into one filter.

## Bans

- **Never animate grain.** No seed stepping, no `baseFrequency` transition —
  bake the tile once and let the compositor cache it, per the base recipe in
  `effects-policy.md`.
- **Grain is page/section-scoped, never per-card.** Repeating a grain layer
  across a card grid multiplies paint cost and reads as noise wallpaper, not
  a surface material.
- **Disable grain under `prefers-contrast: more`.** Contrast-sensitive users
  get a clean surface, not a textured one fighting for legibility.
- **Halftone is for imagery and illustration only, never body text.** A dot
  screen at photo scale turns reading-size text into moiré noise.
- **Ink bleed and edge roughening never appear on body text.** Display type
  only, roughly `24px` and up — a headline or wordmark, never a paragraph.
- **Duotone as standalone color-grade art direction is out of scope for
  this file (locked decision 7, v2).** Every duotone recipe here is tied to
  an explicit two-ink print register; a mood-graded photo with no ink
  register behind it isn't this technique.
