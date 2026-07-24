---
name: svgf-design
description: Use this skill when a design or build request names a material or surface-physics effect — liquid glass, glassy, frosted, refraction, lens, translucent chrome (glass); gooey, organic, blob, metaball, liquid/fluid shapes (goo); grain, paper texture, riso, halftone, duotone, ink, print texture (grain-print); metallic, specular, embossed, lit material, wet (lighting); or generic material language like premium material, texture-rich, material design system in the physical sense — not Google's Material Design. Plain UI-design requests without any of this material language stay with figma-design; this skill is invoked for the material dimension layered on top of it.
version: 0.1.0
---

# SVGF Design

Engineered material effects — real glass optics, organic merges, print texture, and specular lighting — layered on top of a figma-design build, never in place of one. This skill supplies the material dimension; it does not repeat classification, stance, tokens, composition, or copy, all of which stay figma-design's job. A request for "premium material" or "texture-rich" without any figma-design-owned decision already settled is still a figma-design brief first — run that skill's workflow, then come back here for the material layer. Work through the four moves below in order.

## 1. Run figma-design as the base

Check that `~/.claude/skills/figma-design/SKILL.md` exists before doing anything else. If it does not, **stop** and tell the user this skill requires figma-design installed as a sibling skill — do not degrade to building material effects without a stance to hang them on.

If it exists, execute figma-design's full workflow: classify the deliverable, sample ingredients, commit to one stance, and author `DESIGN.md`. Everything below assumes that stance and that `DESIGN.md` already exist.

## 2. Material commitment

Immediately after figma-design's stance commitment — in the same `DESIGN.md`, before any UI code — append a `## Material law` block. Every line is checkable law, not a mood description: something a later reader, human or agent, can hold the finished build against without re-deriving the reasoning, the same way figma-design's own stance commitment works.

- **Family.** Read `references/materials-map.md` now. Run its `## Register classifier` on the surface being built (product UI vs. campaign/brand — classify per surface, not per page), then use `## Stance → material map` to pick the family from the committed stance. If the brief or stance is neutral, default to the refined-tech home register (engineered glass, Apple-neat).
- **The one signature surface.** Name the single moment carrying a real `<filter>`/`feDisplacementMap`/`feComponentTransfer` chain — never `blur()` alone standing in for it.
- **Dosage.** 1 signature + up to 2 supporting moments, each visibly quieter than the signature (smaller, fewer primitives, a plainer tier). Budget is shared across families, not per-family — see `references/materials-map.md`'s `## Dosage`.
- **Ground plan.** Which of the three sources in `references/grounds.md` carries the signature surface: `## Authored SVG/gradient grounds`, `## Real photography`, or `## Simulated product content`. Glass and lighting need a ground with real content to bend or catch light — never a blank or flat-gray field.
- **Fallback-tier plan.** What ships to engines without the primary mechanism (frost-only for glass, static art for goo/lighting where the interaction path isn't supported).
- **Register ceiling.** Apple-neat for product UI, Awwwards-expressive ceiling for campaign/brand, per `references/materials-map.md`'s `## Register classifier`. Goo is banned on product UI, no exception.

## 3. Build

Open the reference for the chosen family and follow its recipes: `references/glass.md`, `references/goo.md`, `references/grain-print.md`, or `references/lighting.md`. For any question about the underlying filter pipeline, filter regions, the sRGB rule, or premultiplied alpha, go to `references/filter-mechanics.md`.

**For glass, never hand-write a displacement filter.** Generate the optics:

```
node <skill-dir>/scripts/make-glass-map.mjs --width … --height … --radius … --bezel … --strength … --shape pill|squircle|rect
```

Paste its output as-is — it emits the full sibling-layer markup, the paired CSS for both tiers, and the filter block together. Displacement maps do not auto-track element size: they are generated at a fixed intrinsic width, and a container stretched more than roughly 20% beyond that width needs a regenerated map — re-run the CLI at the new size rather than letting CSS stretch the existing one.

One architectural rule to hold while building any glass, regardless of source: the refraction layer must always be a **sibling** of the frost layer under an unfiltered parent, never nested inside a filtered or transformed ancestor — an ancestor with its own filter or `backdrop-filter` becomes the backdrop root for its descendants and the refraction goes invisible. `references/glass.md` and `references/filter-mechanics.md` carry the full mechanism and the why; this is the one sentence to hold before touching markup.

Glass belongs on floating chrome sitting over a rich, changing ground — toolbars, tab bars, sheets, command palettes, inspectors — never over a blank or flat-gray field, and never as the default treatment for a content-card grid. Goo, grain-print, and lighting each carry their own dosage, motion, and ban rules in their own reference; read the relevant one before building rather than improvising from the family name alone.

## 4. Material QA

Run this after figma-design's own QA pass, against the `## Material law` block just written, and cross-check the built page against `references/materials-map.md`'s `## Ban table` directly — the bullets below are drawn from it but the table also carries the checks specific to goo, grain, and lighting that a glass-only build won't hit. Fix violations before delivery — the law is the page's own `DESIGN.md`, not this file.

**Grep-checkable:**
- The signature moment is present: `<filter`, `filter: url(`, or `backdrop-filter: url(` appears.
- A frost `@supports (backdrop-filter: blur(1px))` block is present.
- `@supports (backdrop-filter: url(` does **not** appear anywhere — that gate gives a false positive in Firefox and Safari and must never gate the refraction tier.
- `prefers-reduced-motion` and `prefers-reduced-transparency` blocks are both present.
- Every `<filter` element carries explicit, tight region attributes.
- No filter or backdrop-filter is applied to `body` or a full-viewport wrapper.
- No `filter: url` sits on a body-text container.

**Visual, in the browser:**
- No glass sits over a blank or flat-gray ground.
- No glass-card-grid repetition.
- Controls read undistorted — refraction never warps something a user has to click or read precisely.
- Text laid over glass holds contrast via the scrim (tint) layer, not the blur — verify with the scrim present, not assumed.

## Performance floor

Regardless of family: prefer a CSS shorthand (`blur()`, `drop-shadow()`, `saturate()`) over an equivalent SVG filter chain whenever one exists, since browsers fast-path the shorthand harder. Keep every filter region tight and explicit around the smallest wrapper that needs it — never `<body>`. If a displacement map or light-position filter needs to react to resize, rebuild it on resize only, debounced; animate a cheap attribute on the existing chain rather than regenerating the map every frame. `references/filter-mechanics.md`'s `## Performance floor` has the full detail.

## Reference routing

| Reference | Read it for |
|---|---|
| `references/materials-map.md` | Register classifier, stance-to-family map, dosage budget, and the full ban table. |
| `references/glass.md` | Engineered glass: the tier system, generating optics, where glass may live, legibility. |
| `references/goo.md` | Organic merges: the mechanism, registers, dosage, motion, static and interaction recipes. |
| `references/grain-print.md` | Grain, duotone, halftone, and ink-bleed print recipes. |
| `references/lighting.md` | Specular and diffuse lighting recipes: embossed seals, wet/lit hero material. |
| `references/filter-mechanics.md` | The filter pipeline, filter regions, the sRGB rule, premultiplied alpha, performance floor. |
| `references/grounds.md` | The three ground sources a signature surface can sit on. |
| `scripts/make-glass-map.mjs` | The glass optics generator — see move 3 for its CLI. |
