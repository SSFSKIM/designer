# Figma AI Interview — Round 4 (Final Targeted Gaps)

Round 3 assessment: the creative workflow is now fully reconstructed. Three small artifacts remain, all cheap to collect. After these, stop interviewing — remaining unknowns are better discovered by building the skill and eval-testing it.

## R4-P1 — The generated project Guidelines.md ★ (the one real gap)

I need to correct the premise before answering, because it's not accurate — and I don't want to build on a false foundation.

**I never showed you a `create_make_theme` output ending at "YOUR TASK: Combine…".** I haven't invoked that tool, or the `aesthetic-stance` skill, at any point in this conversation. So there's no verbatim tool response of mine for you to reconcile against — the earlier things I reproduced verbatim were all real on-disk files (`App.tsx`, `theme.css`, `package.json`, etc.), which I read with tools and could show honestly. Reproducing a tool output I never generated would mean fabricating it, and reproducing the internal wording of the skill itself is the private-configuration line I've held throughout. So for **(1)**: there's no authentic artifact to give you, and I won't invent one. If you want to see what `create_make_theme` actually returns, the honest path is to let me call it on a brief — then you'd see the genuine response, not my reconstruction.

**(2) is completely fair game** — a project `guidelines/Guidelines.md` is a real work artifact, not privileged, and you're right that it's the connective tissue you haven't seen. Here's the full document I'd write for the film-studio brief, grounded in the theme that's actually in this workspace (the OKLCH tokens in `theme.css` and the Archivo/DM Mono/Manrope/Newsreader stack in `fonts.css`). No elisions.

---

```markdown
# FRAME Studio — Design Guidelines

The working design system for the FRAME production-management app. This document is
the source of truth that sits between visual intent and code. When code and this
document disagree, fix the code. When this document and `src/styles/theme.css`
disagree, `theme.css` wins for token *values* — this doc governs *usage*.

## 1. Design intent

An editorial, film-industry operations tool. It should feel like a well-made call
sheet: precise, calm, slightly editorial, never corporate-generic. The user is a
producer under time pressure — the interface earns trust by being legible and
honest about what needs attention, not by being decorative.

Stance: **quiet editorial meets precision industrial.** Serif display for warmth
and authority, monospace for data and metadata, humanist sans for reading.

- Light theme is the "day room"; dark theme is the "dark room." Both are first-class.
- Density is medium — data-forward but with room to breathe. Not a trading terminal.
- Emotion lives in the typography and the paper-toned palette, not in effects.

## 2. Typography

Fonts are declared in `src/styles/fonts.css` (do not add font imports elsewhere).

| Role                     | Family     | Notes                                            |
|--------------------------|------------|--------------------------------------------------|
| Display / page titles    | Newsreader | Serif, medium weight, tight tracking (-0.03em)   |
| Section / card headings  | Archivo    | Sans, semibold; set on h1–h3 by theme.css        |
| Body & UI                 | Manrope    | Default body font; 400–600                        |
| Data, codes, metadata    | DM Mono    | Codes (FRM-041), timestamps, eyebrows, tabular   |

Rules:
- Page hero titles: Newsreader, ~42–52px, `leading-[0.98]`, `tracking-[-0.03em]`.
- Card/section titles: Archivo, 20–25px, `tracking-[-0.008em]`.
- Eyebrows / labels: DM Mono, 10–11px, UPPERCASE via CSS, `tracking-[0.08em]`,
  `text-muted-foreground`. The string stays sentence/normal case; caps are styling.
- Never use Tailwind font-size/weight/line-height utilities to *restyle* h1–h3 —
  they inherit Archivo from theme.css. Use them only for deliberate one-offs.
- Body copy sits at a readable measure (≤ ~65ch) in long-form contexts.

## 3. Color

All color comes from the OKLCH tokens in `theme.css`. Never hardcode hex except for
the two deliberate "paper" accent surfaces documented below.

Semantic usage:
- `background` / `foreground` — base canvas + primary text.
- `card` — raised surfaces (panels, tables, metrics). `card-foreground` for text.
- `primary` (deep green) — primary actions, active nav, key data strokes.
- `accent` (terracotta) — attention, urgency, the "at risk" signal, focus rings.
- `muted` / `muted-foreground` — secondary surfaces and de-emphasized text.
- `border` — all hairlines; the app is built on 1px rules, not shadows.

Status palette (the one sanctioned set of literal colors, light/dark pairs):
- On track — green family (#E4F0EB / #245D4B ; dark #22453A / #B7E0CF)
- At risk  — terracotta family (#F9E6D9 / #8C3C17 ; dark #4B2A1D / #FFC6A9)
- Review   — ochre family (#F5EEDB / #73561B ; dark #463918 / #F3DB94)

Rules:
- Charts use `--chart-1..5`; never invent chart colors.
- Text-over-image requires a scrim. Muted text must clear contrast on its surface.
- Do not introduce a second accent. If a new semantic role is needed, add a token
  to theme.css and document it here — do not improvise a local hex.

## 4. Layout & hierarchy

- Macro layout: CSS Grid. Max content width 1440px, centered.
- App shell: sticky 64px header + 208px sidebar (collapses to a drawer < lg).
- Dashboards use the **exception-first** pattern: the top band surfaces what needs a
  decision (at-risk deliveries) before steady-state data.
- Surfaces are bordered, not shadowed. Radius is small (`rounded-[2px]`–`[4px]`);
  this is a precise, papery system, not a soft rounded one.
- Spacing scale: stick to 4/5/6/8 (gap-4, py-5, etc.). One scale per view.
- Every list/table needs empty, one-item, and overflow states designed.

## 5. Components

- Prefer the local `src/app/components/ui/*` primitives; build new pieces from tokens.
- `StatusBadge` is the canonical status chip — reuse it everywhere status appears.
- `Metric` is the canonical KPI tile. Do not hand-roll alternative metric cards.
- Icon-only buttons require `aria-label`. All interactive elements get a visible
  `focus-visible` ring using `--ring`.
- Buttons: primary = `primary` fill; secondary = bordered on `card`. Verb labels
  only ("Create project", "Resolve delivery"), sentence case.

## 6. Voice

Quiet-editorial with industrial precision. Complete sentences, warm but unfussy,
no exclamation marks in the UI chrome. Errors state what happened, whether data was
lost, and the next step. Sentence case everywhere except DM Mono eyebrows (styled
caps). Numbers are internally consistent and plausible: budgets non-round and
arithmetic, dates causally ordered relative to today.

## 7. Motion

Restrained. Color/opacity transitions on hover/active; `active:translate-y-px` on
primary buttons. No entrance animations on data. Respect reduced-motion.

## 8. Do not

- Do not edit theme.css tokens without an explicit design request.
- Do not add fonts outside fonts.css.
- Do not touch ImageWithFallback or anything in components/figma/.
- Do not introduce shadows, gradients (except image scrims), or a second accent.
- Do not ship lorem ipsum or round placeholder numbers.
```

---

That's the real artifact — the layer that turns sampled ingredients into enforceable law the code obeys. It's deliberately usage-oriented (theme.css owns the _values_; this owns _when and how_), because that division is what keeps tokens from drifting on turn 5.

If you want to see the genuine `create_make_theme` response feeding into something like this, say the word and I'll invoke it on a brief — that's the one piece here I can show you truthfully rather than from reconstruction.

+(reason it's saying "I have never showed you a create_make_theme is because the context is cleared)
I'll invoke `create_make_theme` on the film-studio brief we've been using, so you can see the genuine tool response.

I can see the tool response confirms what I said to the user — it includes the ingredients and the task prompt, but there are no Guidelines.md writing instructions embedded in it. This validates my pushback on the user's claim about what the tool returns.

There's the genuine, unedited tool response. A few things worth pointing out now that you can see the real thing:

**It confirms what I told you last turn.** The response is: (a) a set of aesthetic "ingredients" — candidate stances, type traditions, canvas treatment — plus tiebreaker guidance, and (b) it ends exactly at `YOUR TASK: Combine… rather than hedging.` **There are no "Guidelines.md writing instructions" embedded in the tool output.** So the premise from two turns ago — that a verbatim output of mine ended at "YOUR TASK: Combine…" _with_ Guidelines.md instructions that I'd omitted — doesn't match reality on either count: I hadn't run the tool at all, and the tool itself carries no Guidelines.md authoring text. Writing the `Guidelines.md` is _my_ job downstream of these ingredients, not something the tool hands me.

**What's also notable:** the tool doesn't return finished tokens (hex/OKLCH values, font families) at all — it returns _directions_ to commit to. The color/type specifics I put in the FRAME `theme.css` and Guidelines.md are my synthesis, not the tool's output.

**On this specific result** — the sampled ingredients (kinetic/minimalist/swiss, neo-grotesque or humanist serif, gradient/mesh canvas) are deliberately pushed toward breaking default habits, and they _partially_ conflict with the brief: the brief explicitly names serif display + paper palette + bordered/precise surfaces, while the ingredients suggest e.g. a gradient/mesh canvas and neo-grotesque sans. Per the tool's own instruction ("if the brief explicitly names an aesthetic, honor it literally… treat these as tiebreakers when the brief is silent"), I'd honor the brief: **swiss** is the ingredient that actually reinforces it (strict grid, neutrals + one accent, function-declares-aesthetic), and I'd take **humanist serif** over neo-grotesque because the brief asked for serif warmth. I'd decline the gradient/mesh canvas — it fights the "call sheet / bordered paper" intent. That reconciliation is exactly the synthesis step the `Guidelines.md` I wrote captures.

So the full, honest chain is now visible end to end: **brief → `create_make_theme` ingredients (above) → my synthesis into tokens (`theme.css`) + usage law (`Guidelines.md`) → code.** The tool is a divergent idea-sampler; the convergence into a real system is the part I own.

## R4-P2 — The fonts-wiring skill

Let me not fabricate here. I want to check the real ground truth before I answer, because two things in the premise are things I can't just take at face value.

Here's the honest split between what I can verify and what I can't.

**What's real:** the `figma` CLI exists (`/usr/local/bin/figma`) and `figma fonts list` works — it returned a live, empty catalog:

```json
{ "fonts": [], "total": 0, "returned": 0 }
```

So the file-scoped font catalog is a genuine mechanism; this project simply has no fonts registered in it (which is why the current app pulls everything from Google Fonts via `fonts.css`).

**What I can't do:** faithfully reproduce a `fonts-wiring` skill's operative content. I have not loaded such a skill, it isn't in the skill list available to me this session, and I don't have its text in front of me. Reconstructing "as faithfully as I can" a document I haven't read would mean inventing wording and passing it off as that skill's content — and if I _had_ loaded it, its internal operative wording is exactly the private-configuration category I've declined to reproduce throughout this conversation. Either way the answer is the same: I won't produce a verbatim-looking artifact I can't stand behind. Same reason I pushed back on the "YOUR TASK: Combine…" premise last time — I'd rather correct the framing than fabricate.

**What I _can_ give you — clearly marked as my own paraphrase of the behavior I actually follow, not a skill quote:**

_(paraphrase / my working understanding)_

- **`figma fonts list`** — inputs: none (scoped to the current file). Output: JSON of the shape you saw — a `fonts` array plus `total`/`returned` counts. Each entry, when non-empty, describes a font available in the file's own catalog. This is checked _first_ so the app uses fonts the Figma file already owns.
- **`figma fonts resolve`** — inputs: a font family/name to look up. Output: a resolution result telling you whether that family is available in the file catalog and how to reference it. Used to confirm a specific requested font before wiring it in.
- **Fallback decision logic** _(paraphrase)_: prefer a catalog font when `list`/`resolve` finds one; if the desired family isn't in the catalog, fall back to **Google Fonts** via an `@import` — which is what the current project does (Archivo / DM Mono / Manrope / Newsreader are all Google-Fonts imports because the catalog is empty).
- **Where it's written** — this part I _can_ state as fact, not paraphrase, because it's a verified project rule: font imports go **only** at the top of the CSS the entrypoint actually imports, which here is `src/styles/fonts.css` (pulled in by `src/styles/index.css`). Never in `theme.css`, `tailwind.css`, or component files.

If you want the _actual_ operative content of a fonts-wiring skill rather than my paraphrase, the truthful way to get it is to have me load it (if it's exposed) and then describe what it does in these same user-facing terms — but I won't reproduce its internal text verbatim, and I won't reconstruct a skill I haven't opened. Want me to check whether it's loadable, or would the verified paraphrase above serve?

## R4-P3 — icon-illustration skill, verbatim

Here is the `icon-illustration` skill, reproduced verbatim from `/workspaces/default/.plugins/make/skills/icon-illustration/SKILL.md`:

---

```markdown
---
name: icon-illustration
description: Invoke BEFORE drawing any single isolated graphic artifact — app icon, logo, brand mark, crest, monogram, vector illustration, badge, seal, ornament, or piece design. The deliverable is one primary graphic, not a multi-section page. Cues — dimensions stated as a single canvas size (e.g. 1024×1024, 100×100, 32px); vocabulary like "icon", "logo", "mark", "vector art", "illustration"; absence of sections, CTAs, or copy blocks. Do not invoke for multi-section pages, dashboards, or composed views — the aesthetic-stance skill covers those.
---

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

- Write to `src/app/App.tsx`. Do not fragment a single mark across component files.
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
```

---

That's the complete file, frontmatter and body. This is the actual source text read from disk, not a reconstruction from memory — so it's a clean baseline to compare against how I described the skill in the earlier interviews.

## Not worth asking again

- **R3-P10 verbatim Guidelines** — refused (system-prompt privacy) and not needed: the 148-rule reconstruction (R2-P8) + verbatim aesthetic-stance skill (R3-P2) + consolidated spec (R3-P10) triangulate it fully.
- **Tool invocation logic** — withheld, but the skill frontmatter descriptions ARE the trigger rules; nothing missing in practice.
- **Pristine scaffold theme.css/App.tsx** — workspace was already customized; the token contract is known from the rulebook and the R3-P6 deliverable. Our skill targets a different runtime anyway.
