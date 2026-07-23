> **One brief, two systems.** This and its sibling were produced from the *same*
> film-studio brief with different sampled ingredients. FRAME committed to quiet
> editorial on warm paper; MERIDIAN committed to brutalist-cinematic on near-black.
> Both are internally coherent and mutually exclusive — that divergence is the
> point of the workflow: ingredients + full commitment produce distinct systems,
> not variations on one template. Use the structure, not the palette.
>
> Where these transcripts' section shapes deviate from the required skeleton in `references/guidelines-authoring.md`, the skeleton governs new work.

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
