# Stances

A stance is a committed visual system: the brief's position on the axes below, the values derived for this product from that position, one signature element, and the road not taken. It is not a mood and it is not a name. "Clean and modern" is a mood — it names no radius scale, no type ramp, and no rule for when a shadow is allowed. `swiss` is a name — a starting position with character, never a source of values. The stance is the thing that answers those questions the same way on every screen, so a page reads as designed rather than assembled section by section from whatever felt right at the time. Use this file at three points in the workflow: parsing the brief, where density and criticality are read off it; deriving and committing to one stance, where the seven coordinates are chosen and the values derived from the product's own world; and building semantic tokens, where that derivation becomes a token set.

## The axes

Nine lines are recorded in `DESIGN.md` §0. Two are **constraints** the brief fixes and the design does not choose — category is allowed to speak here. Seven are **coordinates** the design chooses for this product; sampled ingredients and the named-stance library nudge them, and category may bias one but never picks a value. Every rung is named, no axis has an unlabelled default, and the record states each position with its reason.

| Axis | Kind | Rungs | What decides it | Token families it owns | Checkable rules |
|---|---|---|---|---|---|
| **Density** | constraint | spacious / standard / dense | The user's verb — read or browse pulls spacious; operate on rows, monitor, fix pulls dense — plus session length and viewport. Standard is a real product default, chosen by task and recorded as a choice. | Control and row height, spacing base and steps, gaps, label placement, containment method, type-scale ratio. **Not** body size by itself. | Dense: control height 28–32px, rows ≤ 36px, steps favour 4/8/12/16, labels inline, containment by hairline or tone, accent coverage ≤ 5%. Spacious: controls 40–48px, steps favour 8/16/24/32/48, labels above fields, scale ratio ≥ 1.25. Body size is a type decision made *within* the density; density never silently shrinks type. Touch targets never below the platform floor. One density per view hierarchy. |
| **Criticality** | constraint | exploratory / transactional / consequential | Whether actions are reversible, audited, safety- or money-relevant, or regulated. Trust is an outcome of this plus craft, not a position. | State redundancy, contrast floors, destructive-action treatment, transparency permission on task surfaces, motion caps, copy directness, confirmation and recovery. | Consequential: no state communicated by hue alone; the accent never doubles as warning, danger, or success; primary task surfaces opaque; no overshoot on error or confirmation motion; irreversible actions confirmed or recoverable; error copy literal and actionable. |
| **Energy** | coordinate | quiet / composed / lively / exuberant (no middle rung) | The stakes and the user's frame of mind, and what the brand can carry. Not "the brand is fun". | Accent chroma ceiling, heading-to-body contrast, size jumps, radius and shape language, illustration licence, motion amplitude and overshoot permission, copy enthusiasm ceiling. | Quiet: accent C ≤ 0.15, control radius ≤ 6px, no overshoot, at most one high-salience treatment per viewport. Lively and above: C up to 0.22, radius ≥ 10px or a declared shape language, and at most **two** loud channels at once — chroma and shape, not chroma plus huge type plus spring plus decorative shadow. Overshoot is a separate recorded yes/no. Energy sets a *ceiling*; it never raises chroma by itself. Ceilings per rung: `color-engineering.md` §"Accent-chroma ceilings by energy". |
| **Type** | coordinate | a class — neutral sans / characterful serif / characterful display / mono-as-display — plus the tradition (the 13 in `scripts/ingredients.json`) and the *criteria* | Energy, the product's world, and what must be legible at what size. | Display, UI, and mono selection; family count; weight range; numerals; tracking; case. | The stance records criteria — x-height, terminals, width, weight range, tabular numerals, whether a display face is licensed — and never a family name; families are chosen at build time under `typography.md`'s derive-first / swap-one-slot rule. Family count follows density: one plus a mono at dense, two at standard, three only where a real data role exists. The class sits inside the energy: at quiet, grotesque, humanist, geometric, slab, transitional; at lively and above, any. Script and display faces never carry body or UI text. |
| **Material model** | coordinate (categorical, governed by compatibility rules) | printed / tonal / elevated / glass over planes | Whether anything genuinely sits above content that changes underneath it, whether the product's world has physical layers, whether the honest metaphor is paper. | Border system, shadow tiers, surface stepping, radius tendency, texture, `backdrop-filter` and the glass runtime. | The rungs and their full consequences are in `material.md` §"The axis" — read it while placing the brief, not at the craft pass. In short: printed takes no shadow but a modal; tonal steps by lightness, three rungs at most, shadow on floating UI only; elevated names three or four tiers, each meaning a height, on floating UI only; glass is a floating control layer only, never nested, never in the content layer, with an opaque fallback. Not a slider — glass is not more elevation. |
| **Color commitment** | coordinate | restrained / committed / full palette / drenched | Whether color is the brand's carrier, and what the surface is for. | Accent coverage, number of color roles, whether the ground itself may be chromatic. | Restrained keeps chromatic surface at 10% or under; committed 30–60%; full palette means three or four roles each with a job it can be named by; drenched is for hero and campaign moments only. Coverage comes from here, the chroma ceiling from energy. Dense task surfaces forbid full palette and drenched — a dense screen has no surface left to spend; visual layering on a campaign page is not density. |
| **Accent job** | coordinate (a role decision, recorded on its own line) | none / status-only / directional / atmospheric | What the accent is *for*, decided before what color it is. | Which roles may carry the accent hue, the focus and selection treatment, and whether a non-color interaction language is needed instead. | Exactly one primary job. A directional accent never doubles as danger, warning, or success — once one hue means both "press this" and "this failed", the failure state is the one that loses. Status-only carries actions by neutrals, weight, and position; atmospheric puts the hue in fields and imagery and differentiates actions some other way. `none` is a monochrome interaction language — weight, spacing, hairlines, and a visible non-color focus treatment carry every state — and it is legitimate at the luxury and archival registers; the accessibility floor's focus-visibility requirement binds whatever the job is. Name one hue that was weighed for the job and rejected. `color-engineering.md` §"Choosing the accent". |
| **Ground lightness** | coordinate | light / dark | The physical-scene sentence: where the product is used, and what it is looked at against. Never derived from energy or criticality — dark reads heavy and dominant, not serious. | Background and foreground roles, the direction of surface layering, border alpha, shadow opacity, accent lightness floor. | Light: ground L ≥ 0.93, or a deliberately mid-tone brand body. Dark: elevation drawn by lighter surfaces, shadows demoted to overlays, accent L ≥ 0.62, contrast measured on the surface the text actually sits on. Both modes derive from one role set rather than one being an inversion of the other. |
| **Ground temperature** | coordinate | warm / neutral / cool / brand-tinted | The product's material world — what the thing is made of, where it is used, what it is next to. | Neutral ramp hue, border and shadow tint, the cream-band check. | All neutrals share one hue family within ±20°, at C ≤ 0.02 (≤ 0.04 when brand-tinted). Borders and shadows are the foreground hue at an alpha, not black. A cream-band ground (L 0.84–0.97, C < 0.06, h 40–100) needs a named justification — `taste-calibration.md` flags that band as a saturated default. Warmth at dark or at a mid-tone is first-class. |

**Derived by resolvers, not axes.** Several things that feel like decisions are outputs of the nine lines. Motion is derived — energy supplies amplitude and character, density supplies speed pressure, criticality caps overshoot and ambiguity, and the material model supplies the spatial story (`motion.md`). Voice is derived from energy crossed with criticality, formality rising with criticality (`voice-copy.md`). Radius is energy crossed with density; border weight is material crossed with density. The light and dark pairing is derived once, both modes from one role set (`color-engineering.md`). Each resolver is keyed by axis position rather than by stance name, so a stance nothing has ever named still finds its row.

**Not axes.** Trust and seriousness are outcomes of criticality, craft, and quiet energy; they belong to the QA floor, not to a slider. "Premium" and "professional" are underspecified brief words — decompose them into positions before honoring them. "Playful ↔ sober" is energy under another name, conflated with criticality and formality; use the four energy rungs instead. Motion is a resolver, not a position of its own — energy, density, criticality, and the material model derive it. Layout is a separate composition grammar (`composition.md`).

## Compatibility rules

Per-axis lookups are not additive: the joint position is what ships, and some pairs collide. These resolutions are what a naive per-axis reading gets wrong.

| Combination | Resolution |
|---|---|
| dense × glass over planes | Glass only on small persistent navigation or controls; primary data surfaces stay opaque. |
| consequential × lively or exuberant | Emphasis stays in type and color. No humorous copy, no bounce, no ambiguous state transitions. |
| dense × characterful display | The display face appears in one overview region; operational components keep instrumental text. |
| dense × full palette or drenched | On task surfaces, refused; on chrome and overview, confined there. No continuous tint behind tabular data. Density is information density — a poster or a zine page that is visually layered is not this rule's case. |
| dark × elevated | Resolves to tonal, with shadow demoted to overlays; elevation is drawn by lighter surfaces. |
| consequential × any | No glass on primary task surfaces, no overshoot on error or confirmation motion, no hue-only state. |
| restrained × exploratory | Neutral primary actions are allowed, but focus and selection stay unmistakable. |
| warm × light | Lands in or near the cream band. Needs a named justification, or the warmth moves into the accent and the imagery. |

## The derivation procedure

1. **Read the constraints off the brief.** Density and criticality, one line each with the reason. Category is allowed to speak here.
2. **Write two candidate coordinate vectors.** The modal one — what the category expects — and one non-modal alternative that still fits the product. Sampled ingredients and, optionally, a named stance from the library are the material for the second. Discard anything the compatibility rules forbid.
3. **Choose, with reasons, and record the rejected vector.** A vector that sits on the category's modal position at every coordinate is allowed, but it then has to carry its distinctness in the values and the signature.
4. **Derive the values from the product's own world.** Accent job first, then the accent hue from what the product means, with one candidate hue weighed and rejected. Ground from the scene sentence, with one alternative rejected. Type from the criteria under the derive-first rule. Radius, border, and shadow from the material model. Spacing and geometry from density. Motion, voice, and the light/dark pairing from the resolvers.
5. **Write the commitment as base plus tension** (below). The tension is the signature element.
6. **Run the clone check before writing code.** Would this `DESIGN.md` come out the same for a different product in the same category? The same constraints are expected. The same coordinates are plausible. The same values are the tell — re-derive.
7. **Record it** in `DESIGN.md` §0: the nine axis lines with reasons, the rejected vector, the two rejected values, and the signature.

**Framework defaults are overridden explicitly.** Tailwind and shadcn ship a radius scale, a gray ramp, and a shadow set, and those sit in the layer beneath the tokens. A derivation that never names them leaves them in place, and they show through — two builds that derived different stances still converge on the same corners and the same grays. Name the replacements.

**Ingredients are bounded mutations.** Each sampled ingredient has to map to a coordinate, a composition rule, or a component treatment. It may change one or two decisions; it never imports a whole visual system. It survives the same compatibility and fit tests as everything else, and the record says why this mutation helps this product. The sampler has one job — escaping the modal answer — and a draw that cannot be attached to a decision is discarded, not honored.

### Writing the commitment

A commitment is one sentence: a base and a tension. The base is the position stated in material terms; the tension is the one thing that interrupts it, and that interruption is the signature element.

- Operational: "Quiet operational typography on a planar cool ground, interrupted by one directional amber signal."
- Consumer: "Generous rounded surfaces on a lavender ground, with every loud moment saved for the instant a habit is checked off."

"Modern, clean, trustworthy" is the anti-example. It has no base and no tension, so nothing follows from it, nothing contradicts it, and nothing can be checked against it later.

## Five worked derivations

The five systems below are finished results of the procedure above. Each is shown with the product it was derived for, its position on the nine lines, and the reasoning that turned that position into these values. Read them for the shape of a whole system — color roles, radius scale, border system, shadow tiers, spacing scale, type ramp, motion — and for how a position becomes values.

The values are that product's instantiation. A value from a worked derivation may be reused only after re-derivation for the product at hand, with the reason recorded; byte-identical reuse across unrelated products is the clone tell `qa-protocol.md` looks for. Products that share a brief's constraints will share the position, not the values.

---

### 1. Precision industrial

**Derived for:** a freight-rail dispatch console — car locations, block assignments, crew hours, and exception alarms, worked on a desktop across a full shift.

**Axis position:**

- Density: dense — one screen holds a working set of trains and cars, and dispatchers scan rows rather than read pages.
- Criticality: consequential — a misread block assignment moves real equipment; actions are audited.
- Energy: quiet — the stakes are high and the session is long; nothing should ask for attention that has not earned it.
- Type: neutral sans — a compact grotesque for display, a neutral UI sans, a mono for data. Criteria: high x-height, tabular figures, unmistakable 0/O and 1/l.
- Material model: tonal — nothing in a dispatch board floats; panels are planes told apart by a lightness step.
- Color commitment: restrained — the chromatic surface belongs to status and charts.
- Accent job: directional — exceptions, high-priority actions, and keyboard focus.
- Ground lightness: light — a lit control room, screens read alongside paper and printed manifests.
- Ground temperature: cool — the product's world is steel, rail, and instrumentation.

**Why these values, for that product:** a dispatcher looks at this for eight hours in a lit room, so the ground is a near-white with a steel cast — cool enough that status colors and chart series read against it without the ground competing for chroma. Structure is carried by a lightness step and a hairline instead of a shadow, which is the tonal model doing its job at dense: an ordinary card that lifts is a lie about a board where nothing floats. The accent is oxide orange because it is the one hue absent from the status set this product already needs — green, amber, red, blue — so against steel it reads as "exception" rather than as decoration, and it can carry action and focus without ever also meaning failure. Display sizes stay compact: 48px is a page title here, not a hero, because a tool read all shift has no room for a hero. Products with the same constraints will share this position; they will not share this orange, this steel, or this family triple.

```css
/* PRECISION INDUSTRIAL
   Character: exact, durable, sober, low-noise.
   Surface model: cool near-white workspace + steel-tinted panels.
   Use shadows sparingly; structure comes from grid and rules.
*/

:root {
  /* Color tokens */
  --background: #F4F6F7;
  --foreground: #162024;

  --card: #FFFFFF;
  --card-foreground: #162024;

  --primary: #123B45;
  --primary-foreground: #F7FAFA;

  --secondary: #E3E9EA;
  --secondary-foreground: #243237;

  --muted: #EDF1F1;
  --muted-foreground: #607076;

  --accent: #D46B2C;
  --accent-foreground: #241006;

  --border: #C7D0D2;
  --ring: #D46B2C;

  /* Optional semantic status colors */
  --success: #2C725E;
  --warning: #B75D16;
  --danger: #B63B3B;
  --info: #276B8A;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 2px;
  --radius-2: 4px;
  --radius-3: 6px;
  --radius-4: 8px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-strong: 2px;
  --border-subtle: rgb(22 32 36 / 12%);
  --border-default: rgb(22 32 36 / 20%);
  --border-strong-color: rgb(22 32 36 / 38%);
  --border-active: #123B45;

  /* Shadows — use only for floating UI, never ordinary cards */
  --shadow-none: none;
  --shadow-float:
    0 1px 2px rgb(22 32 36 / 8%),
    0 8px 20px rgb(22 32 36 / 10%);
  --shadow-popover:
    0 2px 4px rgb(22 32 36 / 8%),
    0 18px 42px rgb(22 32 36 / 16%);
  --shadow-modal:
    0 8px 16px rgb(22 32 36 / 10%),
    0 28px 70px rgb(22 32 36 / 22%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;

  /* Typography */
  --font-display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --font-ui: "Inter", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Geist Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 48px;
  --type-display-line: 1.04;
  --type-display-weight: 650;
  --type-display-tracking: -0.025em;

  --type-h1-size: 36px;
  --type-h1-line: 1.12;
  --type-h1-weight: 650;
  --type-h1-tracking: -0.02em;

  --type-h2-size: 28px;
  --type-h2-line: 1.18;
  --type-h2-weight: 620;
  --type-h2-tracking: -0.014em;

  --type-h3-size: 20px;
  --type-h3-line: 1.25;
  --type-h3-weight: 620;
  --type-h3-tracking: -0.008em;

  --type-body-size: 15px;
  --type-body-line: 1.55;
  --type-body-weight: 430;
  --type-body-tracking: 0em;

  --type-body-sm-size: 13px;
  --type-body-sm-line: 1.5;
  --type-body-sm-weight: 430;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.4;
  --type-caption-weight: 500;
  --type-caption-tracking: 0.01em;

  --type-label-size: 11px;
  --type-label-line: 1.25;
  --type-label-weight: 650;
  --type-label-tracking: 0.08em;
  --type-label-transform: uppercase;

  --type-data-size: 12px;
  --type-data-line: 1.35;
  --type-data-weight: 500;
  --type-data-tracking: -0.01em;

  /* Motion */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter: cubic-bezier(0, 0, 0, 1);
  --ease-exit: cubic-bezier(0.3, 0, 1, 1);

  --duration-instant: 80ms;
  --duration-fast: 120ms;
  --duration-standard: 180ms;
  --duration-slow: 240ms;

  /* Use: hover/focus = 120ms; menus = 180ms; dialogs = 240ms. */
}
```

**Implementation rules:** use `--radius-2` for controls, `--radius-3` for panels, and `--radius-0` for data tables. Ordinary cards have a 1px border and **no shadow**. Use the orange accent for exceptions, high-priority actions, and keyboard focus — not decorative highlights.

---

### 2. Quiet editorial

**Derived for:** a film-production studio's operations tool — call sheets, shooting schedules, crew and location records, and the daily paperwork a production runs on.

**Axis position:**

- Density: standard — documents are read and edited, not monitored; a schedule is a page, not a feed.
- Criticality: transactional — a wrong call time costs a morning, and most changes are reversible with a reissue.
- Energy: composed — the studio's own materials are considered and typographic; the tool should not be louder than the work.
- Type: characterful serif — a display serif with a text companion, a humanist sans for UI, a mono for metadata. Criteria: moderate contrast, generous measure.
- Material model: printed — the artefacts are literally paper, and every shadow would be a lie about them.
- Color commitment: restrained — color marks state; the page is ink on paper otherwise.
- Accent job: directional — rare, and only for a selected state, an active link, or the primary action.
- Ground lightness: light — daytime office and set use, printed alongside its own output.
- Ground temperature: warm — paper, and specifically the studio's own call sheets.

**Why these values, for that product:** the studio's artefacts are printed and handed out, so the material model is printed and the ground is a paper cream with ink-dark text, with shadows almost nowhere. That ground sits in the cream band `taste-calibration.md` flags as a saturated default, and it is here on a justification rather than by reflex: the paper metaphor is the thing being designed, not an atmosphere borrowed for warmth. Another product that wants this cream justifies it again on its own terms or moves the warmth into the accent and the imagery. The display serif carries the studio's editorial voice at standard density without turning an operations tool into a magazine; the humanist sans keeps forms and controls plain underneath it. The vermilion accent is the grease-pencil mark on a call sheet, and it appears rarely — which is exactly what keeps a selected row or an active link legible as the one thing that changed. Products with the same constraints will share this position; the cream, the vermilion, and this family triple are this studio's.

```css
/* QUIET EDITORIAL
   Character: literary, composed, spacious, image-aware.
   Surface model: warm paper ground + ink text + restrained vermilion accent.
   Let typography and whitespace create hierarchy.
*/

:root {
  /* Color tokens */
  --background: #F5F0E8;
  --foreground: #24211E;

  --card: #FCF9F3;
  --card-foreground: #24211E;

  --primary: #2C302A;
  --primary-foreground: #FAF6EE;

  --secondary: #E8E0D4;
  --secondary-foreground: #4A443D;

  --muted: #EEE8DF;
  --muted-foreground: #756D64;

  --accent: #A9462D;
  --accent-foreground: #FFF8F0;

  --border: #D4CABE;
  --ring: #A9462D;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 2px;
  --radius-2: 4px;
  --radius-3: 8px;
  --radius-4: 12px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-emphasis: 1px;
  --border-subtle: rgb(36 33 30 / 12%);
  --border-default: rgb(36 33 30 / 18%);
  --border-emphasized: rgb(36 33 30 / 32%);
  --border-image: rgb(36 33 30 / 10%);

  /* Shadows — editorial interfaces should be nearly shadowless */
  --shadow-none: none;
  --shadow-image:
    0 1px 1px rgb(36 33 30 / 6%),
    0 6px 18px rgb(36 33 30 / 8%);
  --shadow-float:
    0 2px 6px rgb(36 33 30 / 8%),
    0 16px 36px rgb(36 33 30 / 12%);
  --shadow-modal:
    0 8px 22px rgb(36 33 30 / 10%),
    0 32px 80px rgb(36 33 30 / 18%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 40px;
  --space-8: 48px;
  --space-10: 64px;
  --space-12: 80px;
  --space-16: 112px;
  --space-20: 144px;

  /* Typography */
  --font-display: "Newsreader", Georgia, serif;
  --font-ui: "Public Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "DM Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 64px;
  --type-display-line: 0.98;
  --type-display-weight: 480;
  --type-display-tracking: -0.032em;

  --type-h1-size: 44px;
  --type-h1-line: 1.04;
  --type-h1-weight: 500;
  --type-h1-tracking: -0.024em;

  --type-h2-size: 32px;
  --type-h2-line: 1.12;
  --type-h2-weight: 510;
  --type-h2-tracking: -0.018em;

  --type-h3-size: 23px;
  --type-h3-line: 1.22;
  --type-h3-weight: 560;
  --type-h3-tracking: -0.01em;

  --type-body-size: 16px;
  --type-body-line: 1.62;
  --type-body-weight: 400;
  --type-body-tracking: -0.003em;

  --type-body-sm-size: 14px;
  --type-body-sm-line: 1.55;
  --type-body-sm-weight: 400;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.45;
  --type-caption-weight: 500;
  --type-caption-tracking: 0.01em;

  --type-label-size: 11px;
  --type-label-line: 1.3;
  --type-label-weight: 650;
  --type-label-tracking: 0.12em;
  --type-label-transform: uppercase;

  --type-data-size: 12px;
  --type-data-line: 1.45;
  --type-data-weight: 500;
  --type-data-tracking: 0em;

  /* Motion */
  --ease-standard: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-enter: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-exit: cubic-bezier(0.7, 0, 0.84, 0);

  --duration-instant: 100ms;
  --duration-fast: 160ms;
  --duration-standard: 260ms;
  --duration-slow: 420ms;

  /* Use: hover/focus = 160ms; image/caption reveals = 260ms; overlays = 420ms. */
}
```

**Implementation rules:** use full-bleed or editorially cropped images, with rules and whitespace doing most of the layout work. Use `--radius-0` or `--radius-1` for cards and image frames; reserve `--radius-3` for inputs and soft utility controls. The vermilion accent should appear rarely: selected state, active link, primary action, or a small editorial rule.

---

### 3. Contemporary craft commerce

**Derived for:** an alpine guesthouse booking site — rooms, seasons, rates, availability, and a booking flow that ends in a held reservation.

**Axis position:**

- Density: standard — a guest browses a handful of rooms and then fills one form.
- Criticality: transactional — money changes hands and a date is held, but a booking can be changed or cancelled.
- Energy: composed — the guesthouse sells calm; an insistent interface would contradict the product.
- Type: characterful serif — a soft serif with optical sizes, a humanist sans for UI, a mono for reference codes. Criteria: warm terminals, comfortable measure, a text cut that holds at 15px.
- Material model: elevated for product media only, tonal everywhere else — the rooms lift; the chrome does not.
- Color commitment: restrained — photography carries the color.
- Accent job: directional — clay, on the booking action and the selected date.
- Ground lightness: light — daylight browsing, mostly on a phone in the evening.
- Ground temperature: warm — stone, larch, and wool, at a mineral temperature rather than a paper one.

**Why these values, for that product:** the guesthouse's world is mineral and wooden, so the ground is warm but drier than paper — closer to plaster than to a printed page. It sits in the cream band on a named justification, the building's own materials, recorded in `DESIGN.md`; a different product wanting the same warmth justifies it again or moves it. Room photography is the product, so it is the one thing allowed to lift: `--shadow-product` on media, and everything else tonal with a border, which keeps the interface quietly premium instead of turning every text block into a floating card. The accent is clay — the local kiln color, not a generic terracotta — and it is directional, carrying the booking action and the selected date and nothing else, so a page full of imagery still has exactly one place the eye goes to act. The botanical green primary is the pine line above the village. Products with the same constraints will share this position; this clay and this green belong to this valley.

```css
/* CONTEMPORARY CRAFT COMMERCE
   Character: tactile, assured, warm, materially grounded.
   Surface model: mineral neutral + deep ink + botanical green + clay signal.
   Product imagery leads; UI elements remain quietly premium.
*/

:root {
  /* Color tokens */
  --background: #EDE7DC;
  --foreground: #302A24;

  --card: #F8F4EC;
  --card-foreground: #302A24;

  --primary: #334D3D;
  --primary-foreground: #F9F6EF;

  --secondary: #DDD4C6;
  --secondary-foreground: #463D34;

  --muted: #E6DED2;
  --muted-foreground: #766C60;

  --accent: #B65A3C;
  --accent-foreground: #FFF9F3;

  --border: #CDBFAF;
  --ring: #B65A3C;

  /* Optional semantic colors */
  --success: #426B4F;
  --warning: #A36B22;
  --danger: #A63F34;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 3px;
  --radius-2: 6px;
  --radius-3: 10px;
  --radius-4: 16px;
  --radius-5: 24px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-strong: 1px;
  --border-subtle: rgb(48 42 36 / 10%);
  --border-default: rgb(48 42 36 / 18%);
  --border-emphasized: rgb(48 42 36 / 30%);
  --border-inverse: rgb(249 246 239 / 32%);

  /* Shadows — soft, warm, used on product media and flyouts only */
  --shadow-none: none;
  --shadow-product:
    0 1px 2px rgb(48 42 36 / 5%),
    0 10px 24px rgb(48 42 36 / 10%);
  --shadow-float:
    0 4px 10px rgb(48 42 36 / 8%),
    0 18px 42px rgb(48 42 36 / 14%);
  --shadow-modal:
    0 12px 28px rgb(48 42 36 / 12%),
    0 36px 88px rgb(48 42 36 / 20%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 28px;
  --space-8: 36px;
  --space-10: 48px;
  --space-12: 60px;
  --space-16: 80px;
  --space-20: 112px;
  --space-24: 144px;

  /* Typography */
  --font-display: "Fraunces", Georgia, serif;
  --font-ui: "Albert Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Azeret Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 60px;
  --type-display-line: 0.98;
  --type-display-weight: 560;
  --type-display-tracking: -0.035em;

  --type-h1-size: 42px;
  --type-h1-line: 1.06;
  --type-h1-weight: 560;
  --type-h1-tracking: -0.025em;

  --type-h2-size: 30px;
  --type-h2-line: 1.15;
  --type-h2-weight: 580;
  --type-h2-tracking: -0.018em;

  --type-h3-size: 21px;
  --type-h3-line: 1.25;
  --type-h3-weight: 600;
  --type-h3-tracking: -0.008em;

  --type-body-size: 15px;
  --type-body-line: 1.58;
  --type-body-weight: 430;
  --type-body-tracking: 0em;

  --type-body-sm-size: 13px;
  --type-body-sm-line: 1.5;
  --type-body-sm-weight: 450;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.4;
  --type-caption-weight: 520;
  --type-caption-tracking: 0.01em;

  --type-label-size: 11px;
  --type-label-line: 1.25;
  --type-label-weight: 700;
  --type-label-tracking: 0.09em;
  --type-label-transform: uppercase;

  --type-price-size: 15px;
  --type-price-line: 1.2;
  --type-price-weight: 650;
  --type-price-tracking: -0.01em;

  /* Motion */
  --ease-standard: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-enter: cubic-bezier(0.12, 0.8, 0.2, 1);
  --ease-exit: cubic-bezier(0.6, 0, 0.8, 0.2);

  --duration-instant: 100ms;
  --duration-fast: 150ms;
  --duration-standard: 220ms;
  --duration-slow: 360ms;

  /* Use: product-image hover = 220ms; add-to-cart = 150ms; drawer = 360ms. */
}
```

**Implementation rules:** use `--radius-2` for buttons and inputs, `--radius-3` for product cards, and `--radius-4` for image-led promotional surfaces. Product imagery can use `--shadow-product`; standard text/content cards should normally remain flat with a border.

---

### 4. Institutional calm

**Derived for:** a city bus network's public status page — line status, disruptions, replacement services, read on a phone at a stop and on a desktop before leaving the house.

**Axis position:**

- Density: standard — a rider checks one or two lines; a dense board would be a timetable, not a status page.
- Criticality: consequential — public information read in a hurry, by everyone, with a missed replacement bus as the cost of a misread; the accessibility floor binds hard rather than aspirationally.
- Energy: quiet — the page is read by someone who is already late.
- Type: characterful serif for display with a humanist sans for UI. Criteria: legibility first, a large-x-height sans that holds at 14px on a phone in daylight, a serif with enough weight to head a page without shouting.
- Material model: tonal — a status page is a fixed arrangement of regions, all equally present.
- Color commitment: restrained — the chromatic surface belongs to line status.
- Accent job: directional — teal, and deliberately not any of the status hues.
- Ground lightness: light — outdoors, in daylight, on a bright screen.
- Ground temperature: neutral — a civic page borrows no material world; the neutrals must not argue with the status colors.

**Why these values, for that product:** criticality is consequential even though nothing is bought here, because the information is acted on immediately and by people with no alternative source — so no state is carried by hue alone, every status is also a word, and contrast is measured on the surface the text actually sits on rather than on the page background. Energy is quiet because the reader is anxious and the page's only job is to be read. The ground is a light, faintly parchment white that reads as civic rather than clinical, with the neutrals held near zero chroma so the status colors are the only hues on the page. The teal accent is directional and is not green, amber, red, or blue: it can mark a selected line and the primary action without ever being mistaken for "delayed" or "cancelled", which is the whole reason it was chosen over the navy that a transit brief pulls toward by default. The serif display and the large-x-height sans were chosen for legibility at a bus stop first and for character second. Products with the same constraints will share this position; this teal and this family pair are this network's.

```css
/* INSTITUTIONAL CALM
   Character: measured, trustworthy, clear, enduring.
   Surface model: parchment-light background + navy anchor + restrained blue-green.
   Emphasize information clarity, predictability, and accessible contrast.
*/

:root {
  /* Color tokens */
  --background: #F7F7F3;
  --foreground: #1D2A36;

  --card: #FFFFFF;
  --card-foreground: #1D2A36;

  --primary: #1E4263;
  --primary-foreground: #F8FBFC;

  --secondary: #E7ECEC;
  --secondary-foreground: #31434B;

  --muted: #EFF2F1;
  --muted-foreground: #64727A;

  --accent: #2B7B78;
  --accent-foreground: #F4FFFF;

  --border: #CAD3D4;
  --ring: #2B7B78;

  /* Optional semantic colors */
  --success: #31755F;
  --warning: #9A661B;
  --danger: #A34242;
  --info: #29658C;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 2px;
  --radius-2: 4px;
  --radius-3: 6px;
  --radius-4: 10px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-strong: 2px;
  --border-subtle: rgb(29 42 54 / 10%);
  --border-default: rgb(29 42 54 / 17%);
  --border-emphasized: rgb(29 42 54 / 28%);
  --border-focus: #2B7B78;

  /* Shadows — reserved for menus/dialogs, never navigation or primary content */
  --shadow-none: none;
  --shadow-dropdown:
    0 2px 4px rgb(29 42 54 / 7%),
    0 10px 24px rgb(29 42 54 / 11%);
  --shadow-popover:
    0 4px 10px rgb(29 42 54 / 9%),
    0 20px 48px rgb(29 42 54 / 14%);
  --shadow-modal:
    0 10px 24px rgb(29 42 54 / 12%),
    0 34px 76px rgb(29 42 54 / 20%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;

  /* Typography */
  --font-display: "Source Serif 4", Georgia, serif;
  --font-ui: "Source Sans 3", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Roboto Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 46px;
  --type-display-line: 1.08;
  --type-display-weight: 600;
  --type-display-tracking: -0.02em;

  --type-h1-size: 36px;
  --type-h1-line: 1.14;
  --type-h1-weight: 650;
  --type-h1-tracking: -0.016em;

  --type-h2-size: 28px;
  --type-h2-line: 1.2;
  --type-h2-weight: 650;
  --type-h2-tracking: -0.01em;

  --type-h3-size: 21px;
  --type-h3-line: 1.28;
  --type-h3-weight: 650;
  --type-h3-tracking: -0.005em;

  --type-body-size: 16px;
  --type-body-line: 1.55;
  --type-body-weight: 400;
  --type-body-tracking: 0em;

  --type-body-sm-size: 14px;
  --type-body-sm-line: 1.5;
  --type-body-sm-weight: 400;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.45;
  --type-caption-weight: 550;
  --type-caption-tracking: 0.005em;

  --type-label-size: 12px;
  --type-label-line: 1.3;
  --type-label-weight: 700;
  --type-label-tracking: 0.05em;
  --type-label-transform: none;

  --type-data-size: 13px;
  --type-data-line: 1.4;
  --type-data-weight: 500;
  --type-data-tracking: 0em;

  /* Motion */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter: cubic-bezier(0, 0, 0.2, 1);
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);

  --duration-instant: 90ms;
  --duration-fast: 140ms;
  --duration-standard: 200ms;
  --duration-slow: 300ms;

  /* Use: focus/hover = 140ms; menus = 200ms; dialogs = 300ms. */
}
```

**Implementation rules:** use `--radius-2` as the default across inputs, buttons, and cards. Information architecture should do more work than visual novelty: clear labels, ordered forms, durable tables, and obvious selected states. Never rely on color alone for validation, warnings, or progress.

---

### 5. Playful consumer

**Derived for:** a habit-tracking app — daily check-ins, streaks, categories, and progress read over weeks.

**Axis position:**

- Density: standard — a handful of habits on a phone screen; dense would make a chore of a ten-second visit.
- Criticality: exploratory — a check-in can be undone, and the worst outcome of a mistake is a wrong streak.
- Energy: lively — the product runs on encouragement, but not exuberant: a bouncing interface is charming on day one and in the way by week three.
- Type: characterful display — a display sans with real personality, a geometric or humanist UI sans, a mono for dates and counts. Criteria: a display face that holds at 30px stat sizes, a UI sans with an open aperture at 14px.
- Material model: elevated — a card being checked off should lift under the finger.
- Color commitment: committed — one primary interaction color plus a set of support colors that tell categories apart and carry celebration.
- Accent job: directional — the violet primary. The support colors are category roles, not accents.
- Ground lightness: light — a phone held in a lit room, opened in the morning and at night.
- Ground temperature: brand-tinted — lavender, carrying the primary down into the surface.

**Why these values, for that product:** nothing here is irreversible, so criticality is exploratory and the design can afford to spend on encouragement rather than on confirmation. Energy is lively rather than exuberant because the app is opened for ten seconds a day and the motion has to survive a thousand repetitions. Color commitment is committed rather than restrained because color is how six categories are told apart at a glance, but the roles are split and the split is what keeps it legible: violet is the one interaction color, and mint, peach, and sky are category identity and celebration, never actions. The ground is brand-tinted — a lavender white that carries the violet down into the surface, so a screen with no accent on it still belongs to this product rather than to any white consumer app. Elevated material follows from the primary gesture: the check-in is a physical act, and the card that responds to it is the one object on the screen. Products with the same constraints will share this position; this violet and this lavender are this app's.

```css
/* PLAYFUL CONSUMER
   Character: optimistic, lively, legible, emotionally direct.
   Surface model: soft lavender white + ink blue + citrus/lilac/peach signals.
   Playfulness comes from scale, rhythm, and interaction—not visual clutter.
*/

:root {
  /* Color tokens */
  --background: #F7F5FF;
  --foreground: #24203D;

  --card: #FFFFFF;
  --card-foreground: #24203D;

  --primary: #5A47D5;
  --primary-foreground: #FFFFFF;

  --secondary: #E9E4FF;
  --secondary-foreground: #342B76;

  --muted: #F0EDF8;
  --muted-foreground: #716B88;

  --accent: #FFB94D;
  --accent-foreground: #3B2500;

  --border: #DCD7EF;
  --ring: #5A47D5;

  /* Supporting expressive colors */
  --playful-mint: #82D7B2;
  --playful-mint-foreground: #123E2D;
  --playful-peach: #FFB6A2;
  --playful-peach-foreground: #542016;
  --playful-sky: #94D7FF;
  --playful-sky-foreground: #123854;
  --success: #2F9E6C;
  --warning: #C77B12;
  --danger: #D34858;

  /* Radius scale */
  --radius-0: 0px;
  --radius-1: 6px;
  --radius-2: 10px;
  --radius-3: 14px;
  --radius-4: 20px;
  --radius-5: 28px;
  --radius-full: 9999px;

  /* Border system */
  --border-hairline: 1px;
  --border-strong: 2px;
  --border-subtle: rgb(36 32 61 / 10%);
  --border-default: rgb(36 32 61 / 16%);
  --border-emphasized: rgb(36 32 61 / 26%);
  --border-primary: rgb(90 71 213 / 50%);

  /* Shadows — soft and slightly colored; one level for cards, one for active/floating */
  --shadow-none: none;
  --shadow-card:
    0 1px 2px rgb(36 32 61 / 5%),
    0 7px 16px rgb(90 71 213 / 8%);
  --shadow-active:
    0 2px 4px rgb(36 32 61 / 7%),
    0 10px 24px rgb(90 71 213 / 16%);
  --shadow-float:
    0 5px 12px rgb(36 32 61 / 10%),
    0 22px 46px rgb(90 71 213 / 20%);
  --shadow-modal:
    0 10px 24px rgb(36 32 61 / 14%),
    0 36px 82px rgb(36 32 61 / 24%);

  /* Spacing scale */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;

  /* Typography */
  --font-display: "Bricolage Grotesque", "Arial Rounded MT Bold", sans-serif;
  --font-ui: "DM Sans", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "Fira Mono", "SFMono-Regular", Consolas, monospace;

  --type-display-size: 52px;
  --type-display-line: 1;
  --type-display-weight: 700;
  --type-display-tracking: -0.035em;

  --type-h1-size: 36px;
  --type-h1-line: 1.08;
  --type-h1-weight: 700;
  --type-h1-tracking: -0.025em;

  --type-h2-size: 28px;
  --type-h2-line: 1.14;
  --type-h2-weight: 700;
  --type-h2-tracking: -0.018em;

  --type-h3-size: 20px;
  --type-h3-line: 1.25;
  --type-h3-weight: 700;
  --type-h3-tracking: -0.008em;

  --type-body-size: 16px;
  --type-body-line: 1.5;
  --type-body-weight: 500;
  --type-body-tracking: 0em;

  --type-body-sm-size: 14px;
  --type-body-sm-line: 1.45;
  --type-body-sm-weight: 500;
  --type-body-sm-tracking: 0em;

  --type-caption-size: 12px;
  --type-caption-line: 1.35;
  --type-caption-weight: 600;
  --type-caption-tracking: 0.01em;

  --type-label-size: 12px;
  --type-label-line: 1.25;
  --type-label-weight: 700;
  --type-label-tracking: 0.02em;
  --type-label-transform: none;

  --type-stat-size: 30px;
  --type-stat-line: 1;
  --type-stat-weight: 750;
  --type-stat-tracking: -0.035em;

  /* Motion */
  --ease-standard: cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-spring-soft: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-enter: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-exit: cubic-bezier(0.7, 0, 0.84, 0);

  --duration-instant: 90ms;
  --duration-fast: 140ms;
  --duration-standard: 220ms;
  --duration-emphasis: 320ms;
  --duration-slow: 420ms;

  /* Use:
     button press = 90ms standard;
     card hover = 140ms standard;
     completion/check-in feedback = 220ms soft spring;
     modal/sheet = 320ms enter;
     celebratory sequence max = 420ms.
  */
}
```

**Implementation rules:** use `--radius-3` for standard cards and controls, `--radius-4` for hero modules or bottom sheets, and `--radius-full` only for compact chips, avatars, or progress dots. Use the support colors for categories or celebration moments, but maintain a single primary interaction color: violet. Motion should feel encouraging, not distracting; animations should never block recording a habit or reading progress.

## The library

A named stance is a prior and a grammar with character, never a template: a position the derivation starts from, a signature that keeps it recognisable, a composition grammar, a list of forbidden moves, and reference exemplars worth looking at. It contains no hex and no family name. Read the archetype as the prior, the brief as the evidence, and the resolved stance as what the derivation returns for this product. `scripts/sample-ingredients.mjs` draws its stance names from this table; a drawn name biases coordinates and supplies a signature, and the seven steps above still run in full. The density column is the position these products usually sit at, not a fixed one — density and criticality come off the brief even when a name suggests otherwise.

| Stance | Exemplars | Usual density | Energy | Type | Material | Color commitment · accent job | Ground | Signature | Composition grammar | Forbidden moves |
|---|---|---|---|---|---|---|---|---|---|---|
| `archival` | MoMA catalogs, Rijksmuseum | spacious | quiet | characterful serif, old-style, plus a mono for object labels; tabular figures | printed | restrained · directional | light; warm (justify) or neutral | numbered sections and object labels | catalogue plates, generous margins, captions | shadows, gradients, rounded cards |
| `brutalist` | Bloomberg Businessweek online, brutalistwebsites.com | standard | composed — raw, not loud | mono-as-display, or condensed characterful display | printed | restrained plus one hot accent · directional | light or dark; neutral (true black and white) | exposed structure | hairline rules, a visible grid, oversized display | soft shadows, radius over 2px, gradients, decorative icons |
| `data-dense` | Bloomberg Terminal, FlightRadar | dense | quiet | neutral sans plus a mono for data; high x-height, tabular figures, distinguishable 0/O | tonal | restrained plus a functional status set · status-only or directional | light or dark; cool | density itself, and functional color coding | table-led, exception-first | cards for rows, shadows, padding as decoration |
| `editorial` | Monocle, The Gentlewoman, Kinfolk | spacious | composed | characterful serif display with a humanist sans; high-contrast display cut, generous measure | printed | restrained · directional, rare | light; warm (cream needs justification) or neutral | an asymmetric column grid carrying photography | editorial stack, pull quotes, image-led | card grids, gradients, an eyebrow on every section |
| `kinetic` | Pentagram motion reels, Apple product reveals | standard | exuberant, motion-led; overshoot yes | neutral sans, tight neo-grotesque | glass over planes, or tonal at dark | committed · directional, marking motion state | dark; any temperature | motion marks every state change | one stage, staged reveals | a static hero, motion with no state behind it |
| `maximalist` | zine aesthetic, scrap-and-tape | standard — visually layered, not information-dense | exuberant | two display traditions mixed — condensed against a serif or a slab; contrast in width and weight | printed (scrap) or elevated (stacked paper) | full palette with a hierarchy · atmospheric | light; warm, textured | controlled layering | overlapping elements, torn edges, stamps | a uniform grid, a single accent, restraint |
| `memphis` | Ettore Sottsass | standard | exuberant | characterful display, geometric sans | printed, flat geometry | full palette · atmospheric — the primary shapes do the structural work | light; pastel | primary geometric shapes as structure | asymmetric, shapes used as layout devices | gradients, soft shadows, corporate blue |
| `minimalist` | Apple, Aesop, Teenage Engineering product pages | spacious | quiet | neutral sans, geometric or neo-grotesque; one family, one weight doing most of the work | tonal | restrained · directional, one element per screen | light (warmer than an industrial cool) or dark; neutral | one hero element | product-object, centered, whitespace as the layout | multiple accents, cards, decorative rules |
| `swiss` | Vignelli, Jost Hochuli, Helvetica | standard | quiet | neutral sans, neo-grotesque; neutral terminals, a limited size inventory, flush-left | printed | restrained · directional or status-only | light; neutral to cool | the strict modular grid | asymmetric grid, strong alignment, type and image sharing grid lines | ornamental shadows, unrelated radius variation, atmospheric gradients, a decorative display face |
| `warm` | Aesop, Le Labo, boutique hospitality | standard | composed | characterful serif, humanist or old-style, with a humanist sans | elevated for product media only, tonal elsewhere | restrained · directional | light or dark; warm (cream needs justification) | tactile imagery | product-object, generous crops | cold grays, glossy chrome, hard shadows |
| `risograph` | riso zine printing, People of Print | standard | lively | characterful display, geometric or condensed, print-feel | printed, one grain at the root | committed, two inks · atmospheric — the spot inks are the page's air, and the action is told apart by weight and position | light; warm uncoated | overprint and misregistration | poster blocks, flat block illustration | gradients, gloss, blur |
| `terminal` | tmux dashboards, btop, Berkeley Graphics | dense | quiet | mono-as-display for every role | printed, box-drawing rules | restrained · status-only or directional, one phosphor | dark; cool (console black) | the console | panes and rules | rounded corners, shadows, proportional type |
| `bauhaus` | Bauhaus Dessau, Braun under Rams | standard | composed | neutral sans, geometric exclusively | printed | full palette — the primary triad, used structurally · atmospheric (the triad is surface color, not signal; actions are carried by weight and position) | light; neutral or cream (justify) | primary-color blocking | grid-locked geometry | any shadow, ornament, gradients |
| `y2k-web` | Frutiger Aero, early-2000s consumer web | standard | lively | neutral sans, rounded geometric | elevated with gloss — a period reference, flagged in `DESIGN.md` | committed · atmospheric, aqua chrome | light; cool (sky) | the aqua chrome hero | rounded chrome, a glossy hero, orbs | flat matte everything, brutal rules |
| `luxury-fashion` | Céline campaigns, The Row lookbooks | spacious | quiet | characterful serif, Didone display, with a neutral sans | printed | restrained, monochrome · none — weight, spacing, and hairlines carry interaction, with a visible non-color focus treatment | light or dark; neutral (pure white or pure black) | extreme whitespace and hairlines | lookbook, full-bleed monochrome photography | color accents, rounded corners, shadows |
| `deco` | Art Deco poster lithography, hotel signage | standard | composed | characterful serif, glyphic, or geometric with vertical emphasis | printed | committed — a metallic tone as an ornamental surface role, never a second accent · directional | light warm cream, or dark ink | stepped geometry and symmetry | symmetric, vertical emphasis, framed | asymmetry for its own sake, soft rounded forms |
| `vernacular` | hand-painted shop signs, county-fair flyers | standard — visually crowded, not information-dense | exuberant | characterful display, condensed and loud, mixed across weights | printed, rough | full palette · atmospheric | light; warm and rough | hand-painted clutter | sign-painter stacking, decorative borders | polish, uniform type, restraint |
| `topographic` | USGS quadrangles, Swiss hiking maps, NASA mission graphics | standard to dense | quiet | a mono for coordinates and annotations with a neutral sans | printed, contour lines | restrained, terrain palette · status-only markers | light or dark; cool terrain neutrals | the contour grid | map-led, annotation typography | pure white or pure black grounds, decorative gradients |

Three of these names — `swiss`, `editorial`, `warm` — used to resolve straight onto Precision industrial, Quiet editorial, and Contemporary craft commerce, values carried over whole. That mapping is deleted, and with it the reason four unrelated products shipped the same orange. A brief that lands on `swiss` derives its own grotesque, its own accent, and its own ground from the product in front of it; Precision industrial is what one such derivation looked like for one freight-rail console. Institutional calm is a position no name in this table proposes, which is the ordinary case rather than a gap: most briefs resolve to a stance the library has never named.

## Closing rule

One stance per interface, named or unnamed. A stance the library never names is a first-class outcome, not a fallback, provided the record carries the full derivation. Never blend two — a dense operational table beside a lively consumer hero reads as two projects stapled together, not one considered design. Before any UI code, record in `DESIGN.md` §0 the nine axis lines with a reason each, the rejected coordinate vector, the accent hue and the ground that were weighed and rejected, and the signature element. Override the framework's own defaults explicitly: its radii, grays, and shadows sit beneath the tokens and will show through anything that leaves them unnamed. A later revision that wants a different stance replaces that record; it does not layer a second stance on top of the first.
