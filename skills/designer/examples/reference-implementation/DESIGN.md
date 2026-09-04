# FRAME Studio — Design Guidelines

The working design system for the FRAME production-management app: the source of
truth between visual intent and code. When code and this document disagree, fix
the code. When this document and the token block in `index.html` disagree, the
token block wins for *value* — this doc governs *usage*.

## 0. Stance commitment

FRAME is a quiet-editorial operations tool for film production management:
precise, calm, and legible, in the voice of a well-made call sheet — not a
decorative SaaS dashboard with card-repetition filler, gradients, or glow. The
same brief was also read toward a brutalist-cinematic, near-black system; that
reading was rejected in favor of warm-paper quiet editorial, because the
audience is a producer under deadline pressure and calm legibility serves that
better than high-contrast drama. If a decision is ever ambiguous, choose the
more restrained option.

**Axis position** — two constraints the brief fixed, seven coordinates chosen:

- Density: **standard** — a producer reads and edits documents; a schedule is
  a page, not a monitored feed.
- Criticality: **transactional** — a wrong call time costs a morning, and a
  reissue undoes it.
- Energy: **composed** — the studio's own paperwork is considered and
  typographic; the tool must not be louder than the work it tracks.
- Type: **characterful serif** — criteria: moderate contrast and a text cut
  that heads a page without shouting (Newsreader), tabular figures for
  headings and metric values (Archivo), an open aperture at 14px for body and
  controls (Manrope), a mono for codes, dates, and budgets (DM Mono).
- Material model: **printed** — the artefacts are paper handed out on set, so
  panels part by a hairline and a lightness step, and the one shadow token is
  for floating menus and dialogs only.
- Color commitment: **restrained** — chromatic surface stays under a tenth of
  the page; the rest is ink on paper.
- Accent job: **status-only** — the oxide clay marks delivery risk and time
  pressure, the states a producer must see first; actions are carried by the
  studio-green `primary`, which is a role of its own, not the accent. The clay
  also draws the focus ring, recorded here as the one exception a status accent
  is allowed: focus is an interaction state, not a claim about the content.
- Ground lightness: **light** — daylight office and set use, read alongside
  its own printed output.
- Ground temperature: **warm** — `oklch(0.946 0.011 78)`, paper cream. It
  lands in the cream band `references/taste-calibration.md` flags as a
  saturated default, and it is here on a justification rather than a reflex:
  the call sheet is the artefact being designed, not warmth borrowed for
  atmosphere.

**Rejected coordinate vector.** Brutalist-cinematic — dark, neutral, printed,
mono-as-display, composed, restrained, directional. It fits the industry and
loses to the user: a producer scanning budgets on deadline reads faster off
paper, and the drama would be the tool's rather than the film's.

**Rejected values.** Vermilion was weighed for the accent and lost to the
oxide clay — at that chroma it reads as alarm beside the terracotta "At risk"
badge, and the accent has to sit next to the status set without joining it. A
cool neutral ground was weighed against the paper cream and lost: cool makes a
call sheet look like a database, the one reading this product must avoid.

**Signature element.** The call-sheet rule structure — hairline rules and mono
eyebrow labels ruling every panel, the way a printed call sheet is ruled. The
risk is spent there; nothing else lifts, glows, or gradients.

**Sampler draw.** None recorded — this example predates the sampler record.

## 1. Palette, with usage rules

- `background` / `foreground` — base canvas and primary ink. Nothing else is
  ever used for page ground.
- `card` — every raised surface (panels, tiles, the selected-project list).
  `card-foreground` for its text.
- `primary` (deep studio green) — the one action color: primary buttons,
  active nav, the active tab fill, the key chart stroke.
- `accent` (oxide orange) — reserved for exactly one meaning: delivery risk,
  time pressure, and focus rings. It never doubles as a second brand color or
  a decorative highlight elsewhere.
- `muted` / `muted-foreground` — secondary surfaces and de-emphasized text
  (eyebrows, captions, metadata).
- `border` — every hairline. The system is bordered, not shadowed.
- Status set (the one sanctioned literal-hex exception): On track (green
  family), At risk (terracotta family), Review (ochre family). Each must
  render with a word or icon, never color alone.
- Charts draw only from `--chart-1` … `--chart-8`. No invented chart hex.
- Forbidden: a second accent, hardcoded hex outside the status set,
  gradients used as decoration rather than the one documented chart fill.

## 2. Typography roles, with placement rules

| Role                      | Family     | Where |
|---------------------------|------------|-------|
| Page/hero titles          | Newsreader | `h1` only — route heroes, greetings |
| Section headings, metric values | Archivo | `h2`/`h3`, `Metric` tile values |
| Body & UI                 | Manrope    | paragraphs, buttons, nav — the default |
| Codes, dates, budgets, status | DM Mono | project codes, due dates, $ values, eyebrow labels |

Headings inherit their face from the token block; never restyle an `h1`–`h3`
with a one-off font-family. Mono is for tabular or metadata content only —
never prose.

## 3. Canvas & texture

Base ground is the warm-paper `background` token, applied once at the page
root. Cards sit one step apart (`card`) so panels read as separated surfaces
without a shadow. No grain, no noise, no decorative gradient anywhere except
the one token-driven chart area-fill. Texture is never animated and never
sits behind text.

## 4. Layout system

CSS Grid, max content width 1440px, centered. Sticky header + a fixed-width
sidebar rail. Sections separate by a hairline border or whitespace, never a
shadow. Spacing scale: 4/5/6/8 — one scale per view. Single responsive
breakpoint at 1000px: every multi-column band (metric rail, budget/selection
pair) collapses to one column below it.

## 5. Component canon

Build order for a new view: page header → exception/alert card → `Metric`
tiles → data panel (chart or list) → selection list. Canonical pieces, reused
rather than re-invented:
- `StatusBadge` — the only status chip (On track / At risk / Review).
- `Metric` — the only KPI tile (label, value, one-line detail, icon).
- `.panel` — the only card pattern: `card` background, 1px `border`, no
  shadow, small radius.
- Tabs — a bordered pill group with one active fill (`secondary`), never more
  than one active at a time.

## 6. Voice

Quiet-editorial with industrial precision: complete sentences, warm but
unfussy, no exclamation marks in chrome. Sentence case everywhere except DM
Mono eyebrows (styled caps; the string itself stays normal case). Numbers are
internally consistent and non-round — budgets, percentages, and dates are
causally ordered against today. Errors and empty states say what happened and
the next step, never just "Error."

## 7. Motion

Restrained: color/opacity transitions on hover and active states, a one-pixel
`translate-y` on primary-button press. No entrance animation on data, no
parallax. Respect `prefers-reduced-motion` by disabling transitions.

## 8. Hard don'ts

- No shadow on a standard panel — floating menus/dialogs only, and only the
  one documented restrained shadow token.
- No gradient except the one chart area-fill.
- No second accent color, no improvised hex outside the status set.
- No lorem ipsum or round placeholder numbers — budgets and percentages must
  be non-round and arithmetic.
- No restyling `h1`–`h3` font-family ad hoc.
- No chart color outside `--chart-1..8`.
- No animation beyond section 7.
