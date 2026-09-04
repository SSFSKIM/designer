# Color engineering

This file teaches the procedure for constructing a semantic color-token system from scratch, OKLCH-first. Use it at the "build semantic tokens" step once a stance is chosen. Every stance runs this file: the values are derived for the product at hand, from its ground, its meaning, and its energy. The worked derivations in `references/stances.md` are finished results of this procedure shown alongside the products they were derived for — evidence that the method produces a whole system, never a starting palette.

## Think in OKLCH

Think in **OKLCH first**, then validate in the actual rendering environment. Use hex only when a codebase, library, browser fallback, or asset pipeline needs it.

OKLCH is more useful for palette construction than HSL because its three axes map more closely to how designers reason about color:

```text
oklch(L C H)

L = perceived lightness, from 0 to 1
C = chroma / colorfulness
H = hue angle, from 0 to 360 degrees
```

That axis mapping is what makes moves like these tractable:

- “Make this surface lighter without changing its temperature.”
- “Keep the hue but reduce saturation for dark mode.”
- “Make the accent more forceful without making it visually lighter.”
- “Keep chart series at comparable perceived weight.”

HSL is convenient for quick experiments, but equal numeric changes in HSL do not create reliably equal visual changes. A palette with six HSL colors at the same saturation/lightness can still have one series that looks dramatically louder than the rest.

## The construction sequence

Build palettes in this order:

1. Choose the ground temperature
2. Build a neutral ramp
3. Choose the anchor/ink color
4. Choose an accent hue by product meaning
5. Build semantic states
6. Verify contrast in actual roles
7. Build dark mode as a new surface system
8. Build chart colors separately from UI semantic colors
9. Test the palette on real components and real data

Do **not** start with a random purple/blue brand color and derive everything else from it.

## Neutral ramps

The first palette decision is usually the relationship between the page ground and the “ink” color.

### Ground temperature warm × lightness light — warm-paper ground

Use warm-paper neutrals when the product should feel editorial, crafted, filmic, archival, cultural, hospitality-oriented, human, tactile, or narrative-led. The warm hue is usually a low-chroma yellow-orange range, around `H 65–95`. Keep the chroma very low — the goal is not beige UI, it is a neutral with a perceptible material temperature.

Warmth at high lightness lands inside the cream band `taste-calibration.md` flags — L 0.84–0.97, C below 0.06, hue 40–100 — so a ramp like the one below either carries a justification in `DESIGN.md` argued on this product's own grounds, or the warmth moves: to a mid-tone or dark ground, or out of the ground entirely and into the accent and the imagery. Warm at dark lightness is a first-class ground, not a consolation for having been refused the light one.

```css
:root {
  /* Warm-paper neutral ramp: H ≈ 78, low chroma */
  --paper-0: oklch(0.985 0.006 78); /* near-white highlight */
  --paper-1: oklch(0.965 0.009 78); /* elevated surface */
  --paper-2: oklch(0.942 0.012 78); /* main page ground */
  --paper-3: oklch(0.912 0.015 78); /* muted panel / hover */
  --paper-4: oklch(0.864 0.018 78); /* stronger secondary surface */
  --paper-5: oklch(0.784 0.020 78); /* subtle divider / disabled fill */
  --paper-6: oklch(0.677 0.022 78); /* muted text region */
  --paper-7: oklch(0.540 0.020 78); /* secondary text */
  --paper-8: oklch(0.365 0.018 78); /* soft ink */
  --paper-9: oklch(0.235 0.016 78); /* primary ink */
}
```

Map that ramp into implementation like this:

```css
--background: var(--paper-2);
--card: var(--paper-1);
--secondary: var(--paper-3);
--muted: var(--paper-3);
--border: color-mix(in oklch, var(--paper-9) 16%, transparent);
--foreground: var(--paper-9);
--muted-foreground: var(--paper-7);
```

The lightness steps are intentionally not uniform. The top end of a palette needs smaller jumps because people are more sensitive to small surface shifts in very light UI.

### Ground temperature cool × lightness light — cool-technical ground

Use cool-technical neutrals when the product should feel operational, infrastructural, analytical, precise, scientific, data-dense, contemporary industrial, or high-trust. The hue generally sits in a very low-chroma blue/cyan range, around `H 220–250`.

```css
:root {
  /* Cool-technical neutral ramp: H ≈ 235, low chroma */
  --slate-0: oklch(0.985 0.004 235); /* near-white highlight */
  --slate-1: oklch(0.964 0.007 235); /* elevated panel */
  --slate-2: oklch(0.944 0.010 235); /* workspace ground */
  --slate-3: oklch(0.912 0.013 235); /* muted surface */
  --slate-4: oklch(0.855 0.016 235); /* subdued fill */
  --slate-5: oklch(0.760 0.018 235); /* disabled / subtle control */
  --slate-6: oklch(0.650 0.019 235); /* muted content */
  --slate-7: oklch(0.515 0.020 235); /* secondary text */
  --slate-8: oklch(0.340 0.021 235); /* ink-adjacent */
  --slate-9: oklch(0.215 0.022 235); /* primary ink */
}
```

Do not make “cool technical” mean blue-gray everywhere. A technical palette does not need blue backgrounds everywhere — it needs controlled temperature, stable contrast, and enough low-chroma structure that charts, alerts, and selected states can do their jobs. A very chromatic blue-gray canvas becomes visually loud and competes with data. The background should support information, not become the strongest color on screen.

### Neutral and brand-tinted grounds

The other two temperature positions are quieter, and still derived rather than defaulted to. A **neutral** ground holds chroma at or near zero — `C ≤ 0.01` the whole way down the ramp — and is the right answer when the content supplies all the color the page has: a photo-led product, a chart-led one, anything where a tinted ground would compete with what it carries. A **brand-tinted** ground is the neutral ramp shifted toward the brand hue and capped at `C ≤ 0.04`, which is enough for the tint to register across a large surface and not enough for it to argue with the accent.

Whichever position the ground takes, every neutral in one ramp stays inside a single hue family, within ±20°. A ramp whose hue drifts as it darkens reads as two systems photographed together, and the seam usually shows up first where a border meets a panel.

## Choosing the accent

Choose the accent hue from the product’s meaning, not from a generic “brand color” reflex.

### The accent's job

Decide what the accent is *for* before deciding what color it is, and record the answer in `DESIGN.md`. An accent has one primary job:

- **Status-only** — the accent appears where the system reports state, and actions are carried by neutrals, weight, and position instead.
- **Directional** — the accent carries action, selection, and focus, and nothing else.
- **Atmospheric** — the accent is the product's air: large fields, imagery, illustration, with actions differentiated some other way.
- **None** — there is no accent hue: interaction is a monochrome language of weight, spacing, and hairlines, with a visible non-color focus treatment.

A directional accent never doubles as warning, danger, or success. Once the same hue means both "press this" and "this failed", both meanings weaken, and the failure state is the one that loses.

Name one hue that was weighed for the job and rejected, with the reason it lost. An accent with no rejected candidate is usually the category's reflex answer wearing the product's clothes — `taste-calibration.md` looks for exactly that tell.

### Product-to-accent heuristics

|Product meaning / stance|Accent families I consider|Why|
|---|---|---|
|Infrastructure, energy, industrial|deep teal, oxide orange, controlled amber|Signals monitoring, physical systems, energy, caution|
|Editorial, craft, food, film|vermilion, clay, moss, ink blue|Feels material and culturally grounded|
|Institutional, healthcare, civic|restrained teal, navy, dark blue-green|Trustworthy, stable, accessible|
|Youthful consumer, wellness|violet, coral, citrus, mint|Expressive and emotionally legible|
|Finance, legal, private-client|deep navy, forest, burgundy in moderation|Serious, durable, low-noise|
|Nature, ecology, climate|moss, lichen, water blue, soil/clay|Semantically connected without obvious “greenwashing”|
|Music, media, creative tools|electric-but-controlled violet, indigo, vermilion|Supports energy and signal without making all surfaces neon|

### Accent-chroma ceilings by energy

These are starting limits for UI — not rules for illustrations or campaign art.

| Energy | Light ground: C ceiling / typical L | Dark ground: C ceiling / typical L |
|---|---|---|
| quiet | ≤ 0.15 / 0.45–0.66 | ≤ 0.17 / 0.62–0.78 |
| composed | ≤ 0.17 / 0.45–0.65 | ≤ 0.19 / 0.62–0.78 |
| lively | ≤ 0.20 / 0.50–0.70 | ≤ 0.22 / 0.65–0.80 |
| exuberant | ≤ 0.22 / 0.55–0.72 | ≤ 0.25 / 0.68–0.82 |

The ceiling is a permission, not a target. An exuberant product can sit at `C 0.10` and take its character from shape, type, and motion instead — Apple's does. Energy never raises chroma by itself; it only says how far up the product is allowed to go.

Two things pull the ceiling back down. Criticality of `consequential` lowers whatever the energy allowed, for any hue that carries state: where actions are irreversible, audited, financial, or safety-relevant, an accent that reads as alarm is a usability defect rather than a stylistic one. And coverage is a separate question from intensity — **color commitment** decides how much of the surface is chromatic at all: restrained is roughly 10% or less, committed 30–60%, full palette means three or four color roles each with a job it can be named by, and drenched means the color *is* the surface. Dense density forbids the last two outright; a dense screen has no surface left to spend. In an operational dashboard, the same chroma can make the interface feel alarmed or toy-like.

## Validation

Validate a color in its **real semantic role**, not by checking whether the raw swatch looks attractive.

### A. Text contrast

For normal text, target at least:

```text
WCAG AA normal text: 4.5:1
WCAG AA large text: 3:1
```

For UI controls, target:

```text
UI boundary / meaningful visual state: at least 3:1
```

Check: foreground text on background; card text on card; primary button text on primary fill; secondary-action text on secondary fill; muted text on background; disabled text only where it remains meaningfully readable; focus ring against background and the component it surrounds; alert/status text and icon against alert background.

### B. Role contrast

Also check whether the accent has enough distinction from nearby system colors. A primary accent may pass contrast against white but still fail as an active state if it is too close to an information blue, a chart series, a success green, a selected table row fill, or a dark navigation state.

### C. Color-blind resilience

For functional status or data: do not encode meaning with hue alone; pair color with a label, icon, pattern, marker, line style, value, or position; avoid red/green-only comparisons; ensure adjacent chart colors differ in lightness and/or chroma as well as hue.

### D. Saturation check in context

View the accent at actual component size: 12px label, 14px button text, selected tab, 40px primary button, full-width alert, chart line, focused input. A color that looks refined as a 200px swatch can become abrasive when repeated in fifty controls.

## Dark mode: derive, do not invert

Dark mode is not:

```css
background: black;
foreground: white;
```

and it is not simply the light palette inverted. A good dark system is a new surface hierarchy with related temperature and reduced visual glare.

### Rule 1: retain the hue family, reduce chroma in large surfaces

Light backgrounds can carry slight warmth or coolness because they are high-lightness, low-demand surfaces. Dark backgrounds should usually be **less chromatic** than their light equivalents — a strongly chromatic dark background can feel neon, muddy, or tiring.

```text
Light workspace: L 0.94, C 0.01
Dark workspace:  L 0.19–0.23, C 0.01–0.02
```

### Rule 2: do not use pure black by default

Pure black makes bright text and colored accents feel harsh. Begin dark workspaces around `L 0.16–0.22` rather than `#000000`.

### Rule 3: surfaces step upward in lightness, not downward

In light mode, background → card is lighter. In dark mode, background → card is lighter too — the direction remains the same. Cards and overlays rise toward the foreground, but with restrained contrast.

### Rule 4: use borders more than shadows

In light mode, subtle shadows can help separate white panels from a light background. In dark mode, shadows often disappear into the background or create muddy halos. Use slightly lighter surface steps, low-opacity light borders, subtle inset highlights, and very restrained black shadows only for dialogs and popovers.

### Rule 5: reduce text brightness below pure white

Main text is usually around `L 0.92–0.96`, not pure white. Pure white is reserved for exceptional emphasis or small high-contrast details.

### Rule 6: re-tune accents independently

A light-mode primary accent is not automatically suitable for dark mode. Dark mode often requires higher lightness, slightly reduced chroma if it vibrates, a separate foreground text color, more muted secondary/accent fills, and distinct border/focus values.

### Rule 7: re-check charts separately

Series that are distinct on a light canvas may collapse or bloom on a dark canvas. Dark-mode chart colors usually need higher lightness and more controlled chroma.

## Chart series

Do not use the same colors for primary button, destructive action, success status, and chart series. Chart colors are a separate palette with different requirements.

### First, decide the chart purpose

**Sequential data** — use one hue with a lightness/chroma ramp. Examples: heatmaps, risk intensity, volume, probability, time accumulation.

**Diverging data** — use two semantic poles with a neutral midpoint. Examples: below/above target, loss/profit, temperature deviation, negative/positive variance.

**Categorical data** — use 6–8 distinguishable hues with controlled equal visual weight. Examples: projects, departments, crew groups, channels, locations, product categories.

### Rules for categorical series

1. Keep most series within a comparable lightness band.
2. Vary hue first, then use lightness/chroma to resolve conflicts.
3. Do not make every series equally saturated if one is intended as the focus.
4. Reserve the brand primary for the selected/focused series where possible.
5. Use direct labels, markers, patterns, tooltips, or line styles so color is not the only cue.
6. Do not use eight random rainbow colors.
7. Test the series on the intended chart background, with actual line widths and point sizes.

## Worked example

**Brief:** a desktop-first project dashboard for a small film-production studio tracking shoots, budgets, crew, and delivery deadlines — calm, editorial, operational, not generic enterprise SaaS. Stance: density standard; criticality transactional; energy composed; type characterful serif; material printed; color commitment restrained; accent job status-only; ground warm, light — in this product's own terms, quiet editorial operations (warm paper ground, deep ink text, cinematic green-black primary, clay/orange accent, hairline warm-gray structure, no bright-blue SaaS defaults, no shadows on ordinary panels).

Neutral ramp (warm paper, `H ≈ 78`):

```css
--film-paper-0: oklch(0.985 0.006 78);
--film-paper-1: oklch(0.968 0.008 78);
--film-paper-2: oklch(0.946 0.011 78); /* page workspace */
--film-paper-3: oklch(0.918 0.014 78);
--film-paper-4: oklch(0.862 0.017 78);
--film-paper-5: oklch(0.762 0.019 78);
--film-paper-6: oklch(0.642 0.020 78);
--film-paper-7: oklch(0.510 0.019 78); /* muted labels */
--film-paper-8: oklch(0.330 0.018 78);
--film-paper-9: oklch(0.220 0.016 78); /* primary ink */
```

Primary (studio green-black) and accent (oxide/clay orange), chosen by product meaning rather than a generic brand reflex:

```css
--film-primary: oklch(0.305 0.046 164); /* buttons, active nav, selected tabs, focus ring */
--film-accent: oklch(0.610 0.145 42);   /* deadline risk and time pressure only */
```

Final light-mode token assignment:

```css
:root {
  --background: oklch(0.946 0.011 78);
  --foreground: oklch(0.220 0.016 78);
  --card: oklch(0.968 0.008 78);
  --primary: oklch(0.305 0.046 164);
  --primary-foreground: oklch(0.975 0.006 78);
  --secondary: oklch(0.918 0.014 78);
  --muted: oklch(0.918 0.014 78);
  --muted-foreground: oklch(0.510 0.019 78);
  --accent: oklch(0.610 0.145 42);
  --accent-foreground: oklch(0.245 0.045 42);
  --border: oklch(0.762 0.019 78);
  --ring: oklch(0.305 0.046 164);
}
```

Dark mode re-derives rather than inverts (rules above): workspace drops to `oklch(0.170 0.012 78)`, main text rises to `oklch(0.880 0.010 78)` — not pure white — primary lightens to `oklch(0.720 0.100 164)`, and accent lightens to `oklch(0.735 0.115 42)` with reduced chroma per Rule 6.

Chart series (8 categorical, light mode): studio green, oxide orange, slate blue, warm amber, muted magenta, blue-teal, olive green, brick red — each lifted in lightness and chroma-controlled for the dark-mode variant, per the chart rules above.

The palette is validated last, against real components in both modes — page ground with body copy, card, primary/secondary buttons in every state, a dense table with selected/hover rows, and a chart with all series visible — not against swatches in isolation.
