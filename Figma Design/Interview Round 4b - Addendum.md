# Interview Round 4b — Addendum (create_make_theme correction + second Guidelines.md)

Arrived 2026-07-22 after Round 4. Two artifacts.

## (1) Correction: where the Guidelines.md authoring procedure lives

Figma AI invoked `create_make_theme` live on the film-studio brief. The full tool response ends at:

> YOUR TASK: Combine any preferences the user expressed with these directions to make a great theme for them. Be opinionated and specific. Commit to one stance — the most memorable outputs come from full commitment to one direction rather than hedging.

**There are no `guidelines/Guidelines.md` writing instructions in the tool response.** The tool returns sampled aesthetic ingredients (stances, type traditions, canvas treatment) and a task directive — nothing more.

Its own conclusion: the aesthetic-stance skill's phrasing that the tool returns ingredients "plus the writing instructions for guidelines/Guidelines.md" is misleading about the source. The Guidelines.md authoring procedure lives in the **aesthetic-stance SKILL.md body** (loaded via the Skill tool), which tells the model how to turn ingredients into a written guidelines doc and theme.css tokens. **The tool supplies raw material; the skill supplies the authoring procedure.**

Open offer from Figma AI (not yet taken): load the aesthetic-stance skill in-session and quote its Guidelines.md-authoring section verbatim, to compare against the R3-P2 capture.

## (2) Second complete Guidelines.md — MERIDIAN PICTURES (brutalist stance)

Same film-studio brief, different sampled ingredients → a *different* committed system than FRAME Studio (Round 4). Committed stance: **brutalist–editorial, cinematic** — raw mono + stark monochrome + one hot accent, condensed expressive display over transitional serif body, near-black canvas.

Full document as delivered:

```markdown
# Guidelines.md — MERIDIAN PICTURES

## 0. Stance commitment

**Brutalist–editorial, cinematic.** One idea, fully committed: the site behaves
like a printed film program bound in black — raw monospaced labels, enormous
condensed titles, hairline rules, and exactly one hot accent used sparingly as a
"now playing" signal. No gradients, no soft shadows, no rounded cards. Structure
is exposed. Whitespace is the luxury. Motion is minimal and mechanical (cuts,
wipes), never bouncy.

If a decision is ever ambiguous, choose the more austere option.

## 1. Palette (tokens live in /src/styles/theme.css)

- `--ink`          #0A0A0A   near-black canvas (primary background)
- `--ink-raise`    #141414   raised surface (panels, stills backing)
- `--paper`        #F4F1EA   warm off-white (primary text on dark)
- `--paper-dim`    #A8A29A   muted text, captions, metadata
- `--hairline`     #2A2A28   rules, borders, dividers
- `--accent`       #FF3B1D   signal red — reserved for one thing per view
- `--accent-ink`   #0A0A0A   text on accent fills

Rules:
- Accent red is a scalpel, not a paint roller. One accent moment per viewport:
  a "NOW IN PRODUCTION" tag, an active nav item, a play trigger. Never two.
- No pure white (#FFF) and no pure-saturated anything except the accent.
- Stills and posters are the only source of color; the chrome stays monochrome.

## 2. Typography

- Display / titles: **PP Right Grotesk Compact** (fallback: "Anton", condensed
  sans). Set enormous, tight tracking, UPPERCASE for film titles.
- Body / editorial: **Charter** (transitional serif; fallback Georgia). Generous
  measure, comfortable reading size for synopses and director notes.
- Labels / metadata / nav: **monospace** (ui-monospace, "Berkeley Mono"),
  UPPERCASE, letter-spaced. Runtime, year, format, role — all mono.

Imports go ONLY in /src/styles/fonts.css, at the top.

Do not use Tailwind text-size / weight / leading utilities to override these;
the scale is defined in theme.css. Hierarchy comes from the type roles above,
not ad-hoc sizing.

## 3. Canvas & texture

- Base canvas is `--ink`. Optional very subtle film-grain overlay (a tiled noise
  PNG at ~4% opacity, `mix-blend-mode: overlay`) applied once at the app root —
  never per component.
- No cream paper here; the brief is filmic, so the "paper" is the light text,
  not the ground.

## 4. Layout system

- 12-column grid, hard left-aligned. Asymmetry is welcome; centering is not the
  default. Big empty gutters.
- Hairline rules (`1px solid var(--hairline)`) separate sections instead of
  cards/boxes. Think ledger, not dashboard.
- Section headers are mono kickers ("01 — SLATE") above condensed display titles.
- Max content width ~1400px; editorial text columns capped at ~68ch.

## 5. Components (build order per view)

1. **Global chrome** — fixed top bar: wordmark left (condensed), mono nav right,
   hairline bottom border. Accent marks the active route only.
2. **Hero** — full-bleed film still (`ImageWithFallback`, `object-cover`), title
   overlaid in giant uppercase condensed, mono metadata row beneath
   (YEAR · RUNTIME · DIRECTOR · FORMAT).
3. **Slate index** — list, not grid-of-cards. Each film = a full-width row:
   mono index number, condensed title, thin still thumbnail, hairline divider.
   Hover reveals accent underline + still enlarges slightly (scale, no shadow).
4. **Film detail** — still hero → serif synopsis in a narrow column → mono credit
   block → BTS gallery.
5. **Directors** — portrait + serif bio + mono filmography list.
6. **Footer** — mono contact block, big condensed wordmark, hairline top.

## 6. Imagery

- All stills/posters via `ImageWithFallback`, imported as ES modules, never bare
  path strings. `object-cover` for stills, `object-contain` for logos.
- Prefer real cinematic stills sourced through the image tools; do NOT fake film
  frames with gradients or divs. Duotone/monochrome treatment on hover is allowed
  via CSS filter, but keep at least one full-color still per view for warmth.
- 16:9 and 2.39:1 aspect ratios only for stills — respect cinematic framing.

## 7. Motion

- Cuts and wipes, not springs. Section reveals: quick opacity + 8px translate,
  ~200ms, ease-out. Still enlargements: scale 1.0→1.03, 300ms.
- One "projector" flourish max (e.g., a title that flickers in). Use `motion/react`.
- Respect `prefers-reduced-motion`: disable all transforms, keep opacity only.

## 8. Hard don'ts

- No rounded cards, drop shadows, glassmorphism, or gradients.
- No second accent color. No emoji as UI.
- No centered marketing-hero clichés. This is a program, not a SaaS page.
- Accent red never used for body text or large fills.
```

Figma AI's caveats: (a) hexes, fonts, and component order are its authored decisions derived from the ingredients — not tool output; (b) it would mirror this doc's tokens into `/src/styles/theme.css` as the enforceable source of truth, with Guidelines.md as the prose companion.

## Why this addendum matters

We now hold **two contrasting Guidelines.md artifacts from the same brief** (FRAME Studio: quiet-editorial warm paper; MERIDIAN: brutalist near-black). That pair is the clearest possible demonstration that the workflow is generative, not template-driven: identical brief + different sampled ingredients → two fully-committed, internally-coherent, mutually-exclusive systems. This pair should become a canonical example in the skill (illustrating stance commitment and "the ingredients are tiebreakers, the brief is authority").
