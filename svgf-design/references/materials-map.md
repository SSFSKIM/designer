# Materials map

Everything in `svgf-design` routes through this file. figma-design's workflow
commits a **stance** first (`references/stances.md`, figma-design's); this
file is the step immediately after — it turns that stance into a **material
family** (`glass.md`, `goo.md`, `grain-print.md`, `lighting.md`), a **register
ceiling**, and a **dosage budget**, and it is the only place in the skill that
defines the register mechanism at all (figma-design has no named
brand-vs-product register — see the spec's Derived paragraph). Read the
sibling chapter for whatever family this file routes to before building
anything; this file only says which chapter and how much.

## Register classifier

Run this as a decision test on the surface being built, in order — not a
vibe check:

1. **Does a person operate this surface to accomplish something** — enter
   data, navigate a flow, complete a transaction, work a dashboard, manage a
   record? If yes: this is **product UI**. Ceiling is **Apple-neat**:
   engineered glass (frost + refraction tiers) on floating chrome, quiet
   grain as a page/section ground, CSS specular rims. **Goo is banned on
   this surface, no exception** — locked decision 4, regardless of stance.
2. **Is the surface's entire job to communicate, announce, or sell** — a
   landing page, campaign site, event page, editorial feature, hero-led
   marketing moment — with no transactional flow of its own? If yes: this is
   **campaign/brand**. Ceiling is **Awwwards-expressive**: goo signatures,
   halftone imagery, duotone/riso ink treatments, and lit hero materials are
   all in scope, up to the dosage budget below.
3. **Does the page contain both** (a store's hero next to its checkout, a
   product page next to its settings)? Classify **per surface, not per
   page** — re-run steps 1–2 separately for each distinct surface. A
   campaign-ceiling hero and a product-UI-ceiling checkout can sit on the
   same page; the ceiling never crosses that boundary in either direction.

If step 1 answers yes for a surface, stop — don't also apply step 2 to the
same surface. A surface gets exactly one ceiling.

## Stance → material map

**Neutral-brief rule.** If neither the stance nor the brief carries any
material signal (no mention of glass, texture, grain, gloss, ink, print,
relief, and the stance itself doesn't imply one), default to the **refined-tech
home register**: engineered glass, home tier, over a **simulated-content** or
**authored** ground (`grounds.md`) — never a blank one. One signature surface,
nothing louder. This is the fallback when a stance carries no signal of its
own; every stance below already does carry one, from figma-design's own
committed character for that name, so the neutral-brief rule is the
exception this table routes around, not the typical case.

| Stance | Default family | Signature-surface suggestion | Families explicitly OFF |
|---|---|---|---|
| `archival` | grain-print | Full-page paper ground (mono grain + vignette) with a duotone treatment unifying mixed-source photography, paced by numbered sections. | goo, glass, lighting |
| `brutalist` | grain-print | Rough-outline or ink-bleed treatment on the stark, hot-accent display headline/numeral. | goo, glass, lighting |
| `data-dense` | glass | A floating filter/inspector toolbar (frost-forward, minimal refraction) over live tabular or simulated-content ground. | goo, grain-print, lighting |
| `editorial` | grain-print | Duotone photo treatment on the lead feature image, low-opacity mono luminosity grain elsewhere. | goo, glass, lighting |
| `kinetic` | glass | A dark hero glass panel whose refraction reads alive via scrolling ground content, with a strength morph on hover/press. | goo, grain-print, lighting |
| `maximalist` | grain-print | Colored paper-field grain plus a rough-outline badge or stamp layered into the scrap-and-tape collage. | goo, glass, lighting |
| `memphis` | goo | A static hero identity mark of merged pastel primary-shape blobs, in the stance's own accent hues. | glass, grain-print, lighting |
| `minimalist` | glass | One hero engineered-glass element — the single floating control the stance's "one hero element" rule asks for. | goo, grain-print, lighting |
| `swiss` | glass | A restrained floating toolbar, frost-forward with a plain CSS specular rim, function before spectacle. | goo, grain-print, lighting |
| `warm` | grain-print | Full-page warm paper ground (colored grain, warm tint, vignette) behind tactile product photography, or an earth-tone duotone. | goo, glass, lighting |
| `risograph` | grain-print | The full riso register: colored grain, a hard two-ink duotone pair, halftone on imagery, ink bleed on display type. | goo, glass, lighting |
| `terminal` | glass | A floating command-palette/status bar with a phosphor-accent specular rim over a near-black simulated-content ground. | goo, grain-print, lighting |
| `bauhaus` | glass | A functional floating tab bar (frost + specular rim only, no showy refraction) over primary-color-blocked geometry. | goo, grain-print, lighting |
| `y2k-web` | glass | A glossy rounded-chrome hero navigation pill (full refraction, strong specular, aqua tint) — the stance's own named exception to the no-gloss default. | goo, grain-print |
| `luxury-fashion` | glass | A single hairline glass panel (frost-quiet, thin specular edge only) over full-bleed monochrome photography. | goo, grain-print, lighting |
| `deco` | lighting | An embossed metallic gold/brass seal or crest (the emboss recipe) as the deco monogram. | goo, glass |
| `vernacular` | grain-print | A rough-outline decorative border around a hand-painted-style badge or sign, with colored paper-field grain. | goo, glass, lighting |
| `topographic` | lighting | An embossed terrain-relief badge/seal (contour-line artwork through the emboss recipe) as a wayfinding mark. | goo, glass |

Three rows leave a fourth family off the "Families explicitly OFF" list on
purpose, because that family is a permitted **supporting** material for the
stance — never a default, and still bounded by the Dosage budget below:

- `y2k-web` permits `lighting` (a matching glossy chrome badge) — the
  stance's own named exception to the no-gloss default.
- `deco` permits `grain-print` (a quiet aged-paper/ink ground under the
  embossed metallic seal) — Art Deco's poster-lithography heritage
  (`scripts/ingredients.json`'s `deco` description) makes a muted printed
  ground a natural quiet companion to the lighting signature, not an
  unreviewed gap.
- `topographic` permits `grain-print` (a quiet printed-quadrangle paper
  ground under the embossed contour seal) — USGS/hiking-map heritage
  (`scripts/ingredients.json`'s `topographic` description) makes the same
  paper-ground pairing defensible here.

Every other row's "Families explicitly OFF" column is exhaustive — the three
families not named as that row's default are all OFF, with no silent fourth
exception. (`memphis`'s `glass` was previously missing from its OFF column;
it is OFF like the other two non-default families — Memphis's flat,
non-photorealistic geometric energy doesn't support glass's engineered-depth
optics as even a quiet supporting material.)

## Dosage

- **One signature surface** per build: the single moment that satisfies the
  invocation guarantee (a real `<filter>`/`feDisplacementMap`/`feComponentTransfer`
  chain, never CSS `blur()` alone). It is the loudest material moment on the
  page, and it is what every row above names in its "signature-surface
  suggestion" column.
- **Up to two supporting moments**, and each must read quieter than the
  signature: smaller, further from the primary interaction path, fewer
  filter primitives, or a plainer tier of the same family (frost-only glass
  instead of refraction, mono grain instead of colored, a CSS specular rim
  instead of a full `feSpecularLighting` pass).
- **The budget is shared across families, not per-family.** Goo does not get
  its own separate allowance (`goo.md`'s Dosage says the same); a stance's
  supporting slots can mix families — e.g. `y2k-web`'s glass signature plus a
  `lighting` supporting badge — or stay in one family, but the total never
  exceeds 1 signature + 2 supporting.
- When a row lists a family in the signature suggestion and a second family
  is used alongside it, the second is a supporting moment by construction —
  never a second signature. A page never carries two signatures.

## Ban table

One row per ban, copied verbatim from its source chapter's own bold lead
line, plus the global bans this skill adds on top. Check type is honest: a
plain string or attribute search is `grep`; anything that requires rendering
the page (an ancestor relationship, a rendered ground, a moving state) is
`visual`.

| Ban | Source | Check type |
|---|---|---|
| No glass over a blank or flat-gray ground. | `glass.md:153` | visual |
| No glass card grids. | `glass.md:155` | visual |
| No glass-as-default-card (including the translucent-white-fill + 1px-white-border 2021-glassmorphism combo as a default card style). | `glass.md:158` + `docs/doperpowers/specs/2026-07-25-svgf-design-skill-design.md:19` (locked decision 9) | visual |
| Frost alone ships only as the fallback tier or a quiet supporting surface, never as the intended primary look. | `glass.md:161` | visual |
| Goo never appears on interactive controls or body text. | `goo.md:220` | visual |
| No goo as a section-divider default. | `goo.md:223` | visual |
| No perpetual ambient loops (goo). | `goo.md:227` | visual |
| Never re-parametrize the goo filter itself per animation frame. | `goo.md:229` | grep |
| State shown by a goo merge must also exist as text or ARIA. | `goo.md:234` | grep |
| Never animate grain. | `grain-print.md:346` | grep |
| Grain is page/section-scoped, never per-card. | `grain-print.md:349` | visual |
| Disable grain under `prefers-contrast: more`. | `grain-print.md:352` | grep |
| Halftone is for imagery and illustration only, never body text. | `grain-print.md:354` | visual |
| Ink bleed and edge roughening never appear on body text. | `grain-print.md:356` | visual |
| Duotone as standalone color-grade art direction is out of scope for this file (locked decision 7, v2). | `grain-print.md:358` | visual |
| Never use lighting primitives on buttons, cards, inputs, or navigation chrome. | `lighting.md:181` | visual |
| One light direction per page. | `lighting.md:184` | visual |
| No `filter: url` on body-text containers. | `docs/doperpowers/specs/2026-07-25-svgf-design-skill-design.md:31` | grep |
| No perpetual ambient filter loops (global — applies to every material family, not only goo). | `docs/doperpowers/specs/2026-07-25-svgf-design-skill-design.md:15` | visual |
| No filter on `body` or full-viewport wrappers. | `docs/doperpowers/specs/2026-07-25-svgf-design-skill-design.md:31` | grep |
