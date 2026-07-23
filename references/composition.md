# Composition

This file teaches how to choose a named layout pattern from a brief, build its grid, and integrate imagery (photographic or generated) into it. Use it at the "work information architecture and composition" step — after a stance is chosen and its tokens exist (`references/color-engineering.md`, `references/typography.md`), and before real content is written into the layout (`references/voice-copy.md`). Composition decides what is dominant and what is secondary before either tokens or copy fill in the detail: pick a named pattern for the hero, dashboard, content, or commerce surface at hand; choose photography, treatment, or SVG to fill its slots; and — when a reference image is supplied for a surface — reproduce it rather than substituting a personal default.

## Hero archetypes

Real working vocabulary for landing and marketing heroes, not theory.

### 1. Asymmetric split

Copy on one side, a single supporting object (screenshot, product, form) on the other, on an uneven ratio.

**Earned when:** there's a concrete thing to show _and_ a claim to make, and neither wins. SaaS, tools, anything with a UI to preview.

```css
.hero { display: grid; grid-template-columns: minmax(0,1.15fr) minmax(0,0.85fr);
        gap: clamp(2rem,5vw,5rem); align-items: center; }
```

**Collapse:** stack to one column below ~900px, copy first. The image ratio flips from "portrait-ish" to "full-width landscape." **Failure mode:** the two columns end up equal-weight and it reads as a centered layout that forgot to center — no tension, no hierarchy. The ratio has to be _felt_ (60/40 minimum), and the visual side needs to bleed or overflow slightly or the asymmetry looks like a mistake.

### 2. Full-bleed image

Photograph/render fills the viewport; text overlaid.

**Earned when:** the image _is_ the product (travel, food, fashion, physical goods) and the brand can carry emotional-first over informational-first.

```css
.hero { display: grid; grid-template: "stage" min(88svh,720px) / 1fr; }
.hero > * { grid-area: stage; }          /* image + overlay + copy all stack */
.hero .copy { align-self: end; justify-self: start; max-width: 34rem; }
```

**Collapse:** height drops to ~70svh, copy moves from a corner to bottom-full-width, add a scrim gradient so text survives busy photography. **Failure mode:** text illegible over the image's midtones. Never trust a raw photo — a `linear-gradient` scrim or a solid copy-panel is mandatory, and test against the _lightest_ region of the image, not the average.

### 3. Typographic poster

No image. Oversized headline is the entire composition.

**Earned when:** the idea is verbal (agencies, editorial, manifestos, dev tools with attitude) and there's a real typeface with personality. This is the hardest to fake — it lives or dies on the type.

```css
.hero { display: grid; grid-template-columns: repeat(12,1fr);
        min-height: 78svh; align-content: center; gap: 0.5rem 1rem; }
.hero h1  { grid-column: 1 / -1; font-size: clamp(2.5rem,9vw,8rem); }
.hero .sub{ grid-column: 1 / span 7; }   /* asymmetric offset below */
```

**Collapse:** the clamp does most of the work; sub-columns go full width. Keep the headline from wrapping to more than 3 lines. **Failure mode:** a system font at 8rem looks broke, not bold. If the brief doesn't come with a distinctive display face, don't reach for this — it exposes weak type instantly.

### 4. Product-object (centered / spotlight)

One hero object dead-center, symmetric, often floating on a gradient or radial glow.

**Earned when:** there's a single beautiful hero artifact — a phone, a watch, a bottle, a device — and the message is "look at _this_."

```css
.hero { display: grid; place-items: center; min-height: 82svh; text-align: center; }
.hero .stack { display: grid; gap: 2rem; max-width: 40rem; }  /* copy over object */
```

**Collapse:** nearly free — it's already centered. Just shrink the object and tighten vertical gaps. **Failure mode:** centered symmetry with _no_ strong object underneath = generic template hero. If the object can't be rendered convincingly, this pattern has nothing to hold it up.

### 5. Editorial stack

Full-width bands stacked vertically — eyebrow → headline → lede → media strip — each band its own rhythm. Magazine feel.

**Earned when:** the story is sequential and there's a lot of high-quality supporting content; long-form product narratives, launch pages, brand stories.

```css
.hero { display: grid; grid-template-columns:
        [full-start] minmax(1rem,1fr) [content-start] minmax(0,64rem)
        [content-end] minmax(1rem,1fr) [full-end]; row-gap: clamp(2rem,6vw,6rem); }
.hero > *          { grid-column: content; }
.hero > .bleed     { grid-column: full; }   /* let media break the measure */
```

**Collapse:** the named-line gutters shrink to ~1rem; bleed elements stay full. This is the most naturally responsive of the five. **Failure mode:** no anchor — it's all equal bands, so the eye never finds the hero. One band must dominate (scale, color, or a bleed image) or the page reads as a wall.

## Dashboard arrangements

### Primary-metric + rail

One dominant focal zone (chart/map/primary KPI) with a supporting rail of secondary cards.

**Earned when:** there's a clear hero metric and everything else is context. Analytics overviews, single-subject monitoring.

```css
.dash { display: grid; grid-template-columns: minmax(0,1fr) minmax(280px,340px);
        gap: 1rem; }              /* main + right rail */
```

**Collapse:** rail drops below the main panel as a 2-up card grid, then 1-up. **Failure mode:** the rail becomes a junk drawer — 9 cards of equal weight competing with the hero. Cap the rail; if it overflows, the wrong pattern was chosen (table-led is the fix).

### Table-led

A dense data table is the page; filters/summary sit above it.

**Earned when:** the job is _operate on rows_ — orders, users, tickets, transactions.

```css
.dash { display: grid; grid-template-rows: auto auto 1fr; gap: 1rem; }
/* toolbar / summary strip / scrolling table */
```

**Collapse:** table goes horizontal-scroll inside its container (never reflow columns into cards unless the row is genuinely a "record card"). Sticky header + first column. **Failure mode:** trying to make every column responsive — the result is unreadable stacked mush. Horizontal scroll is correct; fighting it is the error.

### Exception-first

The top band surfaces what's _wrong or urgent_; the steady-state data lives below the fold.

**Earned when:** the user opens this to _act on problems_, not browse — ops consoles, on-call, moderation, delivery control.

```css
.dash { display: grid; grid-template-columns: minmax(0,1.6fr) minmax(260px,0.75fr);
        gap: 1rem; }              /* alert hero + supporting metrics */
```

**Collapse:** the exception hero stays first and full-width; metrics stack beneath. **Failure mode:** crying wolf — if nothing's ever actually urgent, the alert zone becomes decorative and users learn to skip the top of the page. The pattern requires a real severity signal.

### Map-led (spatial)

A map/canvas/floorplan is the primary surface; a panel docks beside it.

**Earned when:** the data is inherently spatial — logistics, fleet, real estate, IoT.

```css
.dash { display: grid; grid-template-columns: minmax(0,1fr) minmax(300px,380px); }
.dash .map { min-height: 70svh; }
```

**Collapse:** map to top (fixed height), panel becomes a bottom sheet / stacked list. **Failure mode:** panel and map don't cross-highlight. A map-led layout that doesn't link selection between the two panes is just two unrelated widgets sharing a screen.

### Grid-of-equals (tiles)

Uniform card grid, no hero.

**Earned when:** genuinely peer-level entities — a portfolio of services, a status wall, a bento of small metrics.

```css
.dash { display: grid; grid-template-columns: repeat(auto-fit,minmax(240px,1fr));
        gap: 1rem; }
```

**Collapse:** free — `auto-fit` handles it. **Failure mode:** flatness. When one tile _is_ more important, this pattern actively hides that. Only use when the equality is true.

## Content, detail, and commerce patterns

### Content and detail pages

**Centered measure + bleed.** Single reading column at ~65ch, media allowed to break wider (the same named-line trick as editorial-stack). **Earned when:** long-form reading is the point — articles, docs, posts.

```css
.doc { display: grid; grid-template-columns:
       [full-start] 1fr [wide-start] minmax(0,10rem) [text-start]
       min(64rem,100%) [text-end] minmax(0,10rem) [wide-end] 1fr [full-end]; }
.doc > *        { grid-column: text; }
.doc > figure   { grid-column: wide; }
.doc > .full    { grid-column: full; }
```

**Collapse:** gutters collapse; everything approaches full width with padding. **Failure mode:** line length creeping past ~75ch on large screens because the measure wasn't capped — reading fatigue.

**Doc with persistent TOC rail.** Sticky nav column + content + optional "on this page" third column. **Earned when:** deep reference material users scan and jump around.

```css
.doc { display: grid; grid-template-columns: 240px minmax(0,1fr) 200px; gap: 2rem; }
.doc nav, .doc aside { position: sticky; top: 1.5rem; align-self: start; }
```

**Collapse:** third column drops first, then the nav becomes a drawer/top disclosure. **Failure mode:** three sticky columns fighting for the same scroll — nauseating. Only the outer rails stick; the content scrolls.

**Detail: media + spec** (the "PDP skeleton" for non-commerce). Big media block, adjacent metadata/attributes. **Earned when:** one entity with a hero visual and a structured attribute set — a property, a profile, a media title.

```css
.detail { display: grid; grid-template-columns: minmax(0,1.4fr) minmax(320px,0.6fr);
          gap: clamp(1.5rem,4vw,3rem); align-items: start; }
```

**Collapse:** media on top, spec panel below (and the spec panel's CTA often becomes a sticky bottom bar).

### Commerce

**Product detail (PDP).** Gallery + buy-box, buy-box sticky.

```css
.pdp { display: grid; grid-template-columns: minmax(0,1.5fr) minmax(340px,0.65fr);
       gap: clamp(1.5rem,4vw,4rem); align-items: start; }
.pdp .buybox { position: sticky; top: 1.5rem; }
```

**Collapse:** gallery → swipeable carousel on top; buy-box below with a **sticky add-to-cart bar** pinned to the viewport bottom (the single most important mobile commerce move). **Failure mode:** the buy-box scrolls away on desktop while the user is deep in a tall gallery — price and CTA must stay in view. A non-sticky buy-box is a conversion leak.

**Product listing (PLP).** Filter rail + responsive product grid.

```css
.plp { display: grid; grid-template-columns: 260px minmax(0,1fr); gap: 2rem; }
.plp .products { display: grid;
       grid-template-columns: repeat(auto-fill,minmax(200px,1fr)); gap: 1.25rem; }
```

**Collapse:** filter rail → off-canvas drawer behind a "Filters (n)" button; grid drops to 2-up then keeps 2-up on phones (never 1-up for products — users want to compare). **Failure mode:** `auto-fit` instead of `auto-fill` leaving a lonely stretched card in the last row; and hiding the filter drawer's active-count so users forget a filter is on.

**Editorial commerce (lookbook).** Full-bleed lifestyle bands interleaved with shoppable grids — editorial-stack and PLP spliced together. Earned for fashion/home brands selling a feeling. **Failure mode:** the shopping never surfaces — beautiful, unbuyable.

## How to pick

The grid choice is downstream of two questions, answered from the brief before any layout decision.

**1. What's the hero unit — and is there exactly one?**

- One strong _image/object_ → full-bleed or product-object.
- One strong _claim, weak visuals_ → typographic poster or asymmetric-split.
- One dominant _metric/table/map_ → the matching dashboard pattern.
- _No_ single hero, genuinely peer content → grid-of-equals or editorial-stack.

This is the fork that decides symmetry. **Centered/poster** means the content is self-sufficient and wants reverence — a manifesto, a hero product. **Asymmetric-split** means two forces need to coexist and the layout is creating tension between them — claim vs. proof, copy vs. UI. When a brief gives both a value proposition _and_ a screenshot, that's split — centering it would force one to subordinate the other, and there's no ground for that.

**2. What's the user's verb?**

_Read_ → centered measure. _Operate on rows_ → table-led. _Fix problems_ → exception-first. _Buy_ → PDP/PLP. _Browse a feeling_ → full-bleed/editorial.

Concrete tells that push toward **asymmetric-split over centered-poster**: the brief names a product with a UI ("show the dashboard"), lists a signup/waitlist form in the hero, or pairs a benefit claim with a proof artifact. Concrete tells that push toward **centered-poster**: the brief is all-message with no artifact, ships a distinctive display typeface, uses words like "bold / statement / manifesto," or the single hero object is beautiful enough to carry the fold alone.

The tie-breaker when a brief could go either way: **centered is safer and reads more premium but risks generic; asymmetric is riskier but reads more designed.** Go asymmetric when the brand wants to feel considered and there's real content to justify the tension; go centered when the content is thin enough that asymmetry would just expose the empty side.

## Imagery integration

### Image-search workflow

Don't search for "beautiful images." Search for visual evidence that belongs to the product, its audience, and the specific layout slot.

```text
Brief
  → identify the visual role
  → formulate several narrow queries
  → search broadly enough to compare
  → reject weak candidates quickly
  → select for crop, palette, composition, and narrative fit
  → treat image into the UI system
  → test at the actual slot size
```

Search a stock-photo service when the product needs photography or reference imagery. If the project already contains brand photography, user-uploaded assets, or an imported design with images, those take priority over a fresh search.

### Define the image's job before searching

Before writing a query, classify the slot.

|Image role|What it must do|Search emphasis|
|---|---|---|
|Hero narrative image|Establish world, mood, product subject|Composition, negative space, atmosphere|
|Product evidence|Prove the product or service is real|Specificity, detail, authenticity|
|Contextual support|Make an abstract story concrete|Relevant people/place/process|
|Editorial section image|Create pacing between text blocks|Crop flexibility, tonal fit|
|Card thumbnail|Identify content quickly|Legible subject at small size|
|Background texture|Establish material without competing with content|Low-detail, tonal stability|
|Team/avatar image|Humanize ownership and collaboration|Consistent framing, genuine expression|
|Data/diagram substitute|Explain process or system|Usually SVG/diagram, not photo|

A photo is only useful when it has a clear job.

### Query formulation

Begin with **three to six focused search queries**, not one vague noun phrase.

Weak query:

```text
film production
```

Likely result: generic clapperboards, cinema cameras, red-carpet imagery, staged actors, irrelevant movie-theater shots.

Better query set for a film-production studio dashboard:

|Query|Likely role|
|---|---|
|`film editor dark studio workstation`|Hero or workspace context|
|`film production crew candid location`|Team/process storytelling|
|`cinematographer camera rig daylight`|Product/process evidence|
|`post production color grading monitor`|Editorial visual for post-production|
|`film set equipment natural light`|Atmospheric background or section image|
|`production notebook call sheet desk`|Detail image for operational/craft tone|

Query structure:

```text
[subject] + [activity or environment] + [lighting / visual quality]
```

Examples:

```text
ceramicist hands studio warm daylight
architectural model workshop overhead
field technician industrial equipment overcast
student reading library window light
coastal restaurant kitchen candid
researcher microscope laboratory side light
```

The third clause matters. It prevents results that are technically relevant but tonally wrong.

### Selection criteria

Once results arrive, select for these criteria in order.

**A. Subject authenticity.** Does the image show the actual world of the product? A logistics product needs real loading bays, routes, packages, equipment, people at work. A food product needs ingredients, process, place, product detail. A healthcare product needs care — generic smiling clinicians may be less credible than a calm, specific environment or process.

**B. Compositional usability.** Can the image survive the required crop? Look for clear subject placement, usable negative space, no critical face/object at likely crop edges, a readable silhouette at small size, foreground/background depth, and tolerance for `object-fit: cover`.

**C. Tonal compatibility.** Does it fit the UI's material world? For a warm editorial product: natural light, warm but not orange-heavy images, visible material texture, controlled contrast, muted or earth-adjacent color. For a cool technical product: structured environment, cooler or neutral light, clean shapes, deliberate geometry — not necessarily "blue technology" imagery.

**D. Narrative specificity.** Does it tell something copy cannot — a real production moment, craft in progress, a distinct environment, a process, a physical artifact, a person's role? A weak image is often merely "nice-looking."

**E. Crop resilience.** Test at the actual intended ratio:

```text
wide hero: 16:9, 3:2, 21:9
editorial image: 4:3, 3:4
product thumbnail: 1:1, 4:5
avatar: 1:1
background strip: 3:1 or wider
```

If the image only works at its original ratio, it is not a flexible UI asset.

### What disqualifies an image

Reject an image when it has any of these problems.

1. **Generic stock symbolism** — handshake, generic laptop, smiling office meeting, staged call-center headset, random city skyline.
2. **The wrong cultural or product context** — a generic cinema image for a production workflow product, a Silicon Valley office for a local cultural institution, a laboratory photo for a logistics product.
3. **No crop safety** — the only important subject sits at an edge or will be cut by the intended slot.
4. **Competing visual noise** — busy background, too many faces, cluttered props, high-frequency detail behind text.
5. **Wrong color temperature** — a heavily cyan-and-magenta club image inside a calm paper-based editorial system, unless that contrast is intentional.
6. **Overly literal cliché** — a leaf for sustainability, a lightbulb for ideas, a lock for security, a coffee cup for coffee, unless it is genuinely a product image rather than symbolic filler.
7. **Overprocessed style** — aggressive HDR, artificial blur, heavy color grading, or a trend look that will fight the UI.
8. **Weak subject readability at thumbnail scale** — a beautiful wide landscape may be useless as a 72px content thumbnail.
9. **Text embedded in the image** — unless the image is a documented poster, cover, or artifact where the text itself is required.
10. **Mismatched production quality** — if one image looks like high-end editorial photography and another looks like casual phone photography, the difference must be intentional.

### Crop and aspect rules by layout slot

**Hero: split-layout image.** Typical ratio `3:2`, `4:3`, or `16:10`. Use for product context, craft, place, feature storytelling.

```tsx
<div className="relative aspect-[3/2] overflow-hidden bg-[#D9D2C7]">
  <img
    src="/images/color-grading-suite.jpg"
    alt="Film editor reviewing footage in a color-grading suite"
    className="size-full object-cover object-[62%_center]"
  />
</div>
```

Crop rule: put the key subject on the visual side opposite the primary text. Use `object-position` intentionally; do not accept a browser-default center crop if it cuts the visual story. Maintain one calm region for text or surrounding whitespace. Do not overlay copy on the image unless the image was selected for text legibility.

**Hero: full-bleed background image.** Typical ratio `16:9`, `21:9`, or full viewport. Use for immersive consumer, travel, culture, media, hospitality, visual product launch.

```tsx
<section className="relative min-h-[680px] overflow-hidden bg-[#1A2423]">
  <img
    src="/images/studio-wide.jpg"
    alt=""
    className="absolute inset-0 size-full object-cover object-center"
  />
  <div className="hero-scrim absolute inset-0" />

  <div className="relative mx-auto flex min-h-[680px] max-w-7xl items-end px-6 py-12 lg:px-10 lg:py-16">
    {/* Content */}
  </div>
</section>
```

Crop rule: use only when the image has enough visual depth and negative space. Place the heading in an intentionally quieter area, not on the busiest part of the image. Keep the live text's contrast valid over the **worst part** of the responsive crop, not only the desktop mockup. Avoid full-bleed images for a dense operational dashboard.

**Editorial image beside copy.** Typical ratio `4:5`, `3:4`, or `4:3`. Use for story pacing, case study, cultural content, hospitality, portfolio.

```tsx
<figure className="max-w-[580px]">
  <div className="aspect-[4/5] overflow-hidden bg-[#E5DDD1]">
    <img
      src="/images/call-sheet-location.jpg"
      alt="A producer marking a call sheet beside a camera cart"
      className="size-full object-cover object-center"
    />
  </div>
  <figcaption className="mt-3 font-['DM_Mono'] text-[11px] leading-[1.4] text-[#756D64]">
    Location scout, North Yorkshire · June 2026
  </figcaption>
</figure>
```

Crop rule: the image should have one clear vertical gesture or subject. Avoid an image that only works wide. Give the caption the same metadata system used elsewhere in the interface. Do not make every image the same ratio; variation is useful in editorial pacing when deliberate.

**Product or project card image.** Typical ratio `4:3`, `3:2`, or `1:1`. Use for project identification, product gallery, destination card, story preview.

```tsx
<a
  href="#project"
  className="group block overflow-hidden border border-[#D4CABE] bg-[#FCF9F3]"
>
  <div className="aspect-[4/3] overflow-hidden bg-[#EAE2D7]">
    <img
      src="/images/coastal-lighting-setup.jpg"
      alt="Lighting setup on a coastal film location"
      className="size-full object-cover transition-transform duration-[260ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] group-hover:scale-[1.025]"
    />
  </div>
  <div className="p-5">
    {/* Card copy */}
  </div>
</a>
```

Crop rule: the subject must remain legible at 200px wide. Do not crop a person's head at an awkward line. Use a fixed aspect ratio across a repeated card set unless there is a strong editorial reason not to. Keep image hover zoom at `1.015–1.03`, never dramatic.

**Avatar or contributor portrait.** Typical ratio `1:1`. Use for ownership, collaboration, identity, comments, crew/team context.

```tsx
<img
  src="/images/avatar-mina-okafor.jpg"
  alt="Mina Okafor, director of photography"
  className="size-9 rounded-full object-cover object-[50%_35%] ring-1 ring-[#FFFFFF]"
/>
```

Crop rule: eyes should be near the upper third, not centered vertically by default. Use a consistent portrait style across a team list. Do not mix tiny high-fashion portrait crops with casual distant group shots.

**Dashboard contextual banner.** Typical ratio `3:1`, `4:1`, or `16:5`. Use for a single context-setting visual on a project detail page, not decorative wallpaper.

```tsx
<div className="relative aspect-[16/5] overflow-hidden bg-[#243130]">
  <img
    src="/images/night-shoot-banner.jpg"
    alt="Film crew preparing a night shoot on location"
    className="size-full object-cover object-[50%_45%]"
  />
  <div className="absolute inset-0 bg-[linear-gradient(90deg,rgb(20_30_31_/_60%)_0%,rgb(20_30_31_/_18%)_58%,rgb(20_30_31_/_0%)_100%)]" />
</div>
```

Crop rule: use a banner only when it adds project identity or context. A project dashboard should not need a new banner on every route. Keep enough low-detail space for a possible overlaid project title. Do not hide critical project data inside image treatment.

### Overlay and treatment recipes

The treatment should integrate the image into the palette and solve a specific issue: legibility, tonal fit, material consistency, or subject emphasis.

**Dark text-protection scrim.** Use when white or pale text sits over an image.

```css
.hero-scrim {
  background:
    linear-gradient(
      90deg,
      rgb(17 26 26 / 76%) 0%,
      rgb(17 26 26 / 54%) 34%,
      rgb(17 26 26 / 16%) 66%,
      rgb(17 26 26 / 0%) 100%
    ),
    linear-gradient(
      0deg,
      rgb(17 26 26 / 22%) 0%,
      rgb(17 26 26 / 0%) 46%
    );
}
```

Use when the text is placed on the left of a full-bleed image, the image has uneven brightness, or the stance supports a cinematic, immersive, or media-led hero. Do not use when the product is operational and the image is not necessary, when the overlay becomes so dark that the image no longer has a role, or when the image was selected purely because a heavy overlay can hide its flaws.

**Light editorial wash.** Use to keep a photograph visible while bringing it into a warm paper system.

```css
.editorial-image {
  position: relative;
  overflow: hidden;
  background: #E9E0D4;
}

.editorial-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      rgb(245 240 232 / 22%) 0%,
      rgb(245 240 232 / 5%) 52%,
      rgb(169 70 45 / 10%) 100%
    );
  mix-blend-mode: multiply;
}

.editorial-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.88) contrast(0.96) sepia(0.04);
}
```

Exact effect: saturation reduced to `88%`, contrast reduced to `96%`, a very light sepia shift of `0.04`, and a warm multiply wash at `22% → 5% → 10%` opacity. This is enough to make mismatched photography sit beside warm neutral UI without turning every image brown.

**Cool technical tone matching.** Use for technical products where photography needs to sit in a cool, controlled environment.

```css
.technical-image {
  position: relative;
  overflow: hidden;
  background: #D8E0E1;
}

.technical-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      rgb(18 59 69 / 18%) 0%,
      rgb(39 107 138 / 10%) 55%,
      rgb(244 246 247 / 8%) 100%
    );
  mix-blend-mode: color;
}

.technical-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.78) contrast(1.04);
}
```

Exact effect: saturation reduced to `78%`, contrast increased to `104%`, a cool color blend overlay using the product's deep teal and information blue, and no extreme blue tint. This works for equipment, locations, industrial environments, maps, and workspace photography — it is not a generic "tech photo" filter.

**Duotone treatment.** Use a true duotone only when the product's visual system has a strong graphic or campaign-quality image language. Good fits: cultural event, music platform, activist/civic campaign, youth-oriented consumer experience, editorial storytelling section, brand campaign. Poor fits: account settings, financial tables, generic product dashboards, small card thumbnails where color fidelity matters.

```css
.duotone-image {
  position: relative;
  overflow: hidden;
  background: #1F244A;
}

.duotone-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1) contrast(1.12);
  mix-blend-mode: luminosity;
}

.duotone-image::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(
      135deg,
      #24203D 0%,
      #5A47D5 48%,
      #FFB94D 100%
    );
  mix-blend-mode: color;
}
```

The result preserves tonal information from the image while applying the app's own accent palette.

**Subtle image depth without an overlay.** Sometimes the correct treatment is only crop plus restrained tonal adjustment.

```css
.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.94) contrast(1.02);
  transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}

@media (hover: hover) and (pointer: fine) {
  .product-card:hover .product-image img {
    transform: scale(1.025);
  }
}
```

Use this when image fidelity matters — food, products, art, place, photography portfolios, or anything where the source image itself is part of the value.

### When to use SVG instead of photos

Use SVG when the visual needs to be explanatory rather than atmospheric, consistent across many sizes, tied directly to data or interaction, brand-specific, visually simple at small scale, or impossible/misleading to represent through stock photography.

|Need|Better choice|
|---|---|
|Workflow explanation|Diagram or process graphic|
|Data relationship|Chart, map, timeline, node graph|
|Product architecture|SVG diagram|
|Empty state|Small purposeful illustration or icon|
|Status / category|Icon system|
|Branded pattern or motif|SVG shape/pattern|
|A physical or abstract concept that must remain controllable|Custom illustration|
|A small visual identity moment|Monogram, badge, mark|

Use a photo instead when the user needs proof of a real place, person, product, or process; the subject benefits from authenticity and material detail; the product is selling an experience, place, or physical object; or the image needs emotional specificity a generic illustration cannot provide. A photo of a real production location is better than an SVG clapperboard if the story is "this is the work we make."

The SVG is subordinate to the UI — it should not introduce a new unrelated illustration language on every route. Drawing conventions vary by stance:

- **Precision / operations products:** geometric fills or simple monoweight strokes, `stroke-width="1.5"` or `2` at a `24 × 24` icon scale, square or modest corner joins, low color count, one semantic accent maximum, structured grid alignment, minimal texture, no decorative sparkles or random circles.

```tsx
export function DeliveryFlowGraphic() {
  return (
    <svg
      viewBox="0 0 320 144"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Delivery path from edit to client approval"
      role="img"
      className="h-auto w-full"
    >
      <path d="M44 72H138M182 72H276" stroke="#8FA0A4" strokeWidth="1.5" />
      <path d="M133 67L138 72L133 77" stroke="#8FA0A4" strokeWidth="1.5" />
      <path d="M271 67L276 72L271 77" stroke="#8FA0A4" strokeWidth="1.5" />

      <rect x="16" y="44" width="56" height="56" rx="6" fill="#FFFFFF" stroke="#C7D0D2" />
      <rect x="132" y="44" width="56" height="56" rx="6" fill="#FFFFFF" stroke="#C7D0D2" />
      <rect x="248" y="44" width="56" height="56" rx="6" fill="#FFF9F5" stroke="#D9A888" />

      <path d="M31 61H57V83H31V61Z" stroke="#123B45" strokeWidth="1.8" />
      <path d="M147 61H173V83H147V61Z" stroke="#123B45" strokeWidth="1.8" />
      <path d="M263 62L276 84L289 62H263Z" fill="#D46B2C" />

      <text x="44" y="122" textAnchor="middle" fill="#607076" fontSize="11" fontFamily="Geist Mono">
        EDIT
      </text>
      <text x="160" y="122" textAnchor="middle" fill="#607076" fontSize="11" fontFamily="Geist Mono">
        REVIEW
      </text>
      <text x="276" y="122" textAnchor="middle" fill="#8C3C17" fontSize="11" fontFamily="Geist Mono">
        RELEASE
      </text>
    </svg>
  );
}
```

- **Editorial or craft products:** fewer, larger forms; material references through line rhythm or shape, not fake photorealistic effects; low contrast unless the illustration is the main feature; one drawing vocabulary across every illustration; carefully controlled asymmetry; hand-drawn quality only if it belongs to the product, not as generic charm.
- **Playful consumer products:** larger, friendlier silhouettes; strong shape rhythm; limited bright palette; smooth corners or intentional irregular geometry; minimal interior detail; motion only for feedback, not constant ambient decoration.

General SVG rules: start with the silhouette and major shapes; use negative space deliberately; keep the element count tied to the brief; use one drawing vocabulary per illustration; do not mix outline, glossy 3D, stipple, and gradient fill without a reason; design for the smallest intended rendering size; do not use illustrations as filler for an otherwise weak empty state or hero.

### Distinguished vs. generic hero

A distinguished hero is not defined by visual complexity. It is defined by a clear relationship between proposition, composition, visual evidence, and action.

A generic gradient-blob hero has a recognizable shape: a vague headline ("The future of productivity starts here"), a generic subheading ("Manage your work in one powerful platform"), two default CTA buttons, a large purple-blue gradient with blurred blob shapes, a dashboard mockup with no specific data or task, equal-weight typography and image, and no reason the hero belongs to this product instead of any other SaaS product. The problem isn't that gradients, blur, or glass are inherently bad — it's that none of these elements are tied to a specific product, user, or task.

A distinguished hero swaps decoration for evidence. For a film-production operations platform, the design choices might be:

```text
Stance: quiet editorial operations

Primary visual: real production workspace / practical editing image

Composition: text and dashboard proof have different jobs. The copy block
is not centered because this is not a generic campaign. The visual
provides actual evidence: shoot, crew, budget, and delivery status.

Palette: warm paper ground, deep studio green, oxide urgency accent.

Action: one primary action, one low-emphasis proof link.

Material: no gradient blob, no decorative glass — a restrained image
treatment and border-led composition instead.
```

The photo itself carries a localized, earned overlay — a directional scrim (`linear-gradient(90deg, rgb(37 33 30 / 58%) 0%, rgb(37 33 30 / 18%) 55%, rgb(37 33 30 / 0%) 100%)`) plus `saturate-[0.86] contrast-[0.97]` — and a small glass-like data panel (`bg-[rgb(37_33_30_/_74%)]` with `backdrop-blur-[10px]`) floats over the image's calm region, showing three real numbers (shoot days, budget used, next delivery) instead of a content-free mockup. It is not distinguished because it has a serif, an image, or a glass panel — it is distinct because the copy names a real production problem, the image belongs to the product's actual world, the content proof is specific, the composition is asymmetric for a reason (proposition on one side, operational evidence on the other), the palette maps to the stance, the overlay is localized and earned, the CTA is direct and singular, and there are no decorative blobs trying to substitute for a product point of view.

## Working from a supplied reference

When a brief supplies an image, screenshot, photo, logo, or mockup, treat it as load-bearing design input — it frequently communicates more than the written prompt, so treat it as a first-class source of truth for the surface it covers. This authority is local: it governs the surface it was supplied for, not the rest of the project, and it does not override an explicit brief instruction elsewhere.

### Determine the image's role first

Classify a supplied image before deciding how to use it. Three broad categories cover most cases — reproduce it, draw inspiration from it, or use it as a content asset — but it's worth distinguishing five practical roles:

|Role|Required interpretation|
|---|---|
|**Reference to match**|Reproduce visible layout, hierarchy, component types, and styling fidelity. Deviate only where the reference is incomplete or ambiguous.|
|**Inspiration / vibes**|Match the visual feeling — palette, density, type mood, materiality — but do not copy the exact layout or copy.|
|**Content to use**|Display the photo, illustration, logo, or icon in the app; do not recreate it in code.|
|**Bug report / current state**|Treat the image as evidence of a problem to fix, not a target to reproduce. Ask if the failure is unclear.|
|**Data source**|Read visible table/menu/schedule information and seed the interface with that real data, rather than placeholder text.|

If ambiguous: default UI screenshots to **reference to match**, and default photos/logos/illustrations to **content to use**.

### Scope the actual reference

If the image is low-resolution or blurred, capture broad intent rather than fake pixel-level precision. If cropped or partial, do not invent unseen areas — infer only conservatively when the request clearly requires a fuller build. Separate the actual design subject from browser chrome, OS elements, cursor, surrounding apps, or incidental framing. If a screenshot includes a whole desktop but the request is clearly about one modal, card, or section, recreate the intended subject, not the accidental surrounding frame.

### Inspect before coding

Do not guess from a filename or a one-line description. Inspect the image and extract:

- Main layout and hierarchy
- Primary, secondary, and chrome regions
- Navigation, sidebar, list, card, footer, tab bar, toolbar, and modal roles
- Light/dark palette, surfaces, accents, and text tones
- Serif/sans/display cues and relative type scale
- Visual density
- Readable text content and labels
- Visible controls and affordances

Use real readable text from the image where it carries meaning; paraphrase only obvious filler.

### Reproduction priority order

Build a reference reproduction in this order: **geometry → palette → type → texture.**

1. **Geometry first** — page skeleton and major regions, then hierarchy and grouping, then the correct component type for each region (this is the layout and structure the reference actually shows, not an invented substitute).
2. **Palette second** — once the region structure holds, extract the light/dark palette, surfaces, accents, and text tones, and encode them in shared tokens rather than scattering raw color literals through components.
3. **Type third** — match serif/sans/display cues and the relative type scale, and carry over real readable text and data from the reference rather than placeholder copy.
4. **Texture last** — match spacing, density, and material rhythm, then wire interaction for controls that are clearly interactive so the reproduction behaves like a real surface rather than a static image.

Reference wins over personal defaults for its surface: reproduce its geometry, palette, type, and density even when the hero-archetype or dashboard-arrangement logic above would otherwise point toward a different pattern.

### Rendering a supplied image inside the interface

When an attached image must appear inside the built interface rather than be redrawn: preserve its aspect ratio; use `object-cover` for hero/background imagery and `object-contain` for logos and icons; always provide meaningful alt text; and never recreate an attached photo, logo, illustration, or existing SVG with gradients, `<div>` elements, or new hand-written SVG. Reference the asset the way the project's own toolchain already imports static assets, rather than assuming one scheme — do not hardcode a literal file path if the project's bundler fingerprints assets. If the interface needs additional images beyond what was supplied, search for or generate assets that match the uploaded material's subject, style, and mood — supplementary assets should look like they belong to the same curated set, not like generic stock dropped in beside it.

### Multiple-image interpretation

Multiple screenshots of one app usually indicate different screens or states — build all of them and connect them with routing or tabs. A screenshot plus a logo or photo normally means the screenshot is the layout reference while the logo/photo is content to embed. Two near-identical screenshots may represent before/after or light/dark versions — support both. If image roles remain unclear, state the interpretation briefly and proceed.
