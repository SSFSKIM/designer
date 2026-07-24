# svgf-design Skill — Design Spec

## Purpose

Ship `svgf-design`: a Claude Code Agent Skill that turns SVG filters into a designed material system — Apple-Liquid-Glass-class engineered refraction, gooey/organic forms, grain/print texture, and specular lighting — for the design work AI systems reliably avoid. This is deliverable #2 of the SVGF-Design repo, built on top of deliverable #1 (`figma-design`, shipped and verified 2026-07-25 by beating real Figma Make 2–1) together with the research corpus in `docs/research/svg-filter-atlas.md`.

The skill is a **material specialist that composes with figma-design**: invoking it guarantees at least one signature filter-material moment in the output. The invocation itself is the "earning" that `references/effects-policy.md` (deliberately conservative, and explicitly written to be extended by this skill) demands — the effects policy governs *placement and dosage*, never *whether*.

## Locked design decisions (from the 2026-07-25 grill)

1. **Identity** — material specialist composing with figma-design; a signature filter-material moment is mandatory on every invocation; hard runtime dependency on figma-design (fail loudly if absent, never degrade silently).
2. **Home register** — aesthetically neutral briefs default to refined-tech: restrained, physically plausible optics (the Apple-neat family). Other material families unlock only via stance or brief.
3. **Realism** — physical plausibility is the standard: engineered refraction (computed displacement maps, not turbulence wobble), correct specular edges, plausible frost. Boldness spent in one place: one unmistakable signature surface, everything else quiet. Stylized/non-physical looks unlock only when the stance demands them.
4. **Surface policy** — engineered glass may sit on floating interactive chrome (toolbars, tab bars, sheets, palettes — Apple's actual use), under a hard legibility + fallback contract. Decorative wobble/goo on controls and any displacement of body text stay banned.
5. **Motion** — refraction reads as alive via content scrolling beneath it (zero extra cost). Filter parameters may transition on interaction (hover/press morphs, one goo delight moment) via class toggles between precomputed states. No perpetual ambient loops. `prefers-reduced-motion` fallbacks mandatory.
6. **Browser posture** — tiered glass: Chromium ships full engineered refraction (`backdrop-filter: url()` is Chromium-only, verified 2026-07 in the atlas); Safari/Firefox ship premium frosted glass (blur+saturate `backdrop-filter`) with the same geometry, specular edge, and tokens. Both tiers must look designed, not degraded.
7. **v1 material families** — glass/refraction (core) + goo/metaball/organic + grain/paper-print (incl. duotone, halftone, ink bleed) + specular/diffuse lighting (mostly serving glass edges; standalone only for badges/seals/material studies). Squigglevision and standalone color-grading → v2.
8. **North stars** — Apple Liquid Glass (visionOS/iOS-26 material system), kube.io-class engineered web glass, Awwwards-experimental expressive (the goo family's ceiling). The dark-SaaS restraint register (Linear/Vercel) deliberately not a north star.
9. **Glass ban line** — plain frost is legitimate only as (a) the Safari/Firefox fallback tier and (b) quiet supporting surfaces. Banned outright: glass over blank/gray grounds, glass card grids, the translucent-white-fill + 1px-white-border 2021-glassmorphism combo as a default card style.
10. **Grounds** — glass requires a visually rich ground; the skill teaches all three sources: authored SVG/gradient art (guaranteed self-contained baseline), real photography when the environment allows, simulated product content (map, video frame, canvas, chart field — truest to Apple's model).
11. **Eval** — A/B on the same briefs: figma-design alone vs figma-design + svgf-design, same worker model both arms, human-judged side-by-side grid. Success: the svgf arm visibly adds the material dimension without losing the base skill's neatness.

Derived (design-time, user-vetoed nothing): register ceilings — product UI caps at Apple-neat, campaign/brand surfaces may reach the Awwwards ceiling, reusing figma-design's existing brand/product register routing; a stance→material mapping covering all 18 figma-design stances; dosage budget of 1 signature + ≤2 supporting moments; all QA material rules phrased to be mechanically checkable.

## What "done" looks like (acceptance, phrased as behavior)

1. **Triggering.** A session prompted "make a landing page with liquid glass navigation" or "give this a gooey, organic feel" loads svgf-design; a plain "make a landing page" with no material language does not (that's figma-design's territory).
2. **Composition.** Every svgf-design transcript shows the figma-design workflow ran first (sampler, stance commitment, DESIGN.md) and that DESIGN.md contains a material-commitment block immediately after the stance commitment: family, signature surface, dosage budget, ground plan, fallback-tier plan, register ceiling.
3. **Signature guarantee.** Every output contains at least one filter-material moment implemented with actual SVG filter primitives (not CSS `blur()` alone) — verifiable by grepping the artifact for `<filter` / `filter: url(` / `backdrop-filter: url(`.
4. **Engineered glass.** When the family is glass, the displacement map comes from `scripts/make-glass-map.mjs` (self-contained data-URI `feImage` → `feDisplacementMap`, optically flat center) — not hand-tuned `feTurbulence`. The page carries both tiers: Chromium refraction and an `@supports`-gated frost fallback sharing geometry and tokens.
5. **Bans hold.** No output places displacement on body text or decorative wobble on controls; no glass over a blank ground; no glass card grid; the built page passes the mechanical material QA (fallback present, reduced-motion honored, glass-surface contrast re-checked) against its own DESIGN.md law.
6. **Range.** The examples directory demonstrates one brief built as two committed material systems (glass treatment vs goo treatment), each with its DESIGN.md law — proving family choice is a real decision, not a default.
7. **Eval complete.** The A/B eval (4 briefs × 2 arms) ran end-to-end, the grid was reviewed by the user, and the verdict is recorded in this spec.

## Architecture (approved: Approach A — overlay skill + computed-optics script)

### Repo layout

```
svgf-design/
  SKILL.md                      # workflow spine (~1,200–1,800 words)
  references/
    filter-mechanics.md         # atlas §0 primer: filter region, sRGB rule, premultiplied alpha
    materials-map.md            # stance→material map (18 stances), register ceilings, dosage, ban table
    glass.md                    # flagship: tiered glass, script usage, specular bezel, chrome placement
    goo.md                      # metaball/organic; delight-moment budget; interaction morphs
    grain-print.md              # grain, paper, duotone, halftone, ink bleed
    lighting.md                 # specular/diffuse; serving glass edges; badges/seals
    grounds.md                  # three ground sources with recipes
  scripts/
    make-glass-map.mjs          # engineered displacement-map generator (node built-ins only)
    make-glass-map.test.mjs     # node:test suite
  examples/
    # one brief — a music/spatial-audio product (visual model genuinely earns materials) — built twice:
    # glass treatment (engineered chrome over simulated product content) and goo treatment (expressive register),
    # each with its DESIGN.md material law + index.html
```

Installed by symlinking `svgf-design/` into `~/.claude/skills/svgf-design` (same pattern as figma-design). The skill is runtime-neutral: no Claude-specific APIs, plain files.

### SKILL.md workflow (four moves layered on figma-design)

1. **Run figma-design as the base.** Classification, ingredient sampling, stance commitment, DESIGN.md authoring, build discipline, QA — all per that skill. If figma-design is not installed, stop and say so.
2. **Material commitment** — written into DESIGN.md immediately after the stance commitment, as law: chosen family (via `materials-map.md`; refined-tech home register when the brief/stance is neutral), the one signature surface, dosage budget (1 signature + ≤2 supporting), ground plan (which of the three sources), fallback-tier plan, register ceiling (product UI = Apple-neat; campaign/brand = Awwwards ceiling).
3. **Build** — recipes from references; for glass, run `make-glass-map.mjs` and paste its output rather than hand-writing filter stacks.
4. **Material QA** — figma-design's QA plus a mechanical pass against the DESIGN.md material law: signature moment present; `@supports` fallback tier present; `prefers-reduced-motion` honored; glass-surface contrast re-checked; ban greps (no `filter: url` on body-text containers, no glass-card-grid repetition, no backdrop-filter over a blank ground).

### The script: `make-glass-map.mjs`

- **Input:** geometry — width/height (or aspect), corner radius, bezel width, refraction strength, shape (`pill` | `squircle` | `rect`).
- **Method:** kube.io engineered optics — per-pixel refraction vector from the bezel profile's surface normal; optically flat center (R=G=128 neutral); fully opaque map (premultiplied-alpha rule).
- **Output:** ready-to-paste block — PNG data-URI inside `feImage` → `feDisplacementMap`, full filter stack with specular edge, plus paired CSS for both tiers (Chromium refraction + frost fallback).
- **Dependencies:** node built-ins only (zlib for PNG encoding).
- **Tests (`node:test`):** center neutrality, radial symmetry, strength scaling, PNG validity, filter-block snapshot.
- **Risk containment:** this is the project's one real engineering risk → the plan gives it a **spike task with visual browser verification** (rendered glass over a rich ground, eyeballed) before any reference or example depends on it. Promote-or-discard criterion: the rendered refraction must read as curved-glass optics (edge bending, stable center) in Chromium; if the method can't be made to read as optics, fall back to shipping glass.md with the best static recipe from the atlas and record the discard here.

### Eval plan

Four briefs × two arms (figma-design alone vs figma-design + svgf-design), same worker model both arms, browser QA allowed in both arms (glass demands visual verification), side-by-side grid, user judges.

Briefs cover the registers: spatial/media product (home turf — glass), playful consumer (goo), editorial/craft (grain-print), and one deliberately neutral brief (tests the home-register default kicks in). Mechanical assertion set runs alongside human judgment: signature present, tiers present, bans hold, reduced-motion honored.

## Out of scope (this deliverable)

- Squigglevision / animated-displacement wobble and standalone color-grade art directions (duotone as *print* technique is in; duotone as *standalone grade* is v2).
- WebGL, canvas-rendered runtime effects, JS interaction engines (interaction morphs are class toggles between precomputed filter states).
- Component-library richness (shadcn/icon/chart environments — Make's environmental advantage, not a skill concern).
- Changes to figma-design itself beyond what already shipped (its typography Leaks 1 and 3 remain separately deferred).

## Decision Log

- **Approach A (overlay skill + computed-optics script) over B (pure recipe library) and C (full material engine).** B rejected: cannot guarantee the signature moment, and glass quality caps at turbulence-approximated wobble — essentially effects-policy.md again, whose outputs the user already judged as missing the material dimension. C rejected: triple build surface, and it over-mechanizes goo/grain/lighting, which are well-served by recipes plus stance-driven taste; per-family engines would also make v2 families expensive. A puts computation exactly where physics demands it (glass) and taste where taste works (the other families).
- **Invocation-as-earning over keep-the-conservative-gate.** The richer-dial alternative (recipes behind the same earned-effects test) risked reproducing the AI-conservatism the skill exists to escape; a standalone effects-forward designer would duplicate the just-shipped workflow and let two laws drift.
- **Refined-tech home register over stance-neutrality or sampled material family.** The user named the Apple-neat center explicitly; sampling the material family would erase it.
- **Tiered glass over Chromium-only or universal-only.** Chromium-only breaks on Safari — the platform of the aesthetic being chased; universal-only outlaws `backdrop-filter: url()` and with it the flagship effect.
- **Frost-as-supporting-tier over engineered-or-nothing.** Engineered-or-nothing would make the Safari tier self-contradictory and outlaw legitimate quiet frost sheets.
- **Dark-SaaS register (Linear/Vercel) deliberately not a north star** — user kept Apple + kube.io + Awwwards-expressive; the expressive ceiling stays high.
- **One brief → two treatments for examples** (FRAME/MERIDIAN pattern reused) over independent showcase pages: proves material choice is a decision space.

## Surprises & Discoveries

*(running log; seeded empty)*

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-07-25: Initial spec from approved brainstorm (11-question grill + Approach A + six-section design, all user-approved).
