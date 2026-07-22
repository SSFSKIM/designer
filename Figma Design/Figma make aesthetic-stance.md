It gives me a disciplined path from a loose product brief to a coherent visual system, then into an implemented React interface.

## What it is really for

I use `make:aesthetic-stance` when the deliverable has **multiple coordinated parts**, for example:

- Marketing sites and landing pages
- Product pages
- Dashboards
- Admin tools
- Portals
- App shells with navigation, tables, settings, or charts
- Multi-section editorial or commerce experiences

I do **not** use it for an isolated icon, logo, badge, or a single small component. Those need a different design process.

Its central rule is:

> Choose a strong, appropriate visual stance quickly and apply it consistently across the entire interface.

That stance governs typography, color, image treatment, layout density, border language, component shape, and motion. It is a way of making all those decisions feel like one design rather than separate stylistic decisions.

---

# The full workflow

## Phase 1 — Read the brief as a design problem, not just a build request

Before choosing colors or components, I extract the design inputs.

### I identify:

|Input|Questions I answer|
|---|---|
|**Product / domain**|What is this? Finance, travel, culture, health, AI, commerce, internal operations?|
|**Audience**|Expert operators, consumers, creators, executives, patients, developers?|
|**Primary action**|What should a person understand or do first?|
|**Content type**|Narrative copy, dense data, imagery, products, settings, results, documentation?|
|**Emotional tone**|Credible, warm, provocative, calm, premium, technical, playful, institutional?|
|**Constraints**|Existing brand, supplied copy/images, required sections, responsive requirements, accessibility needs?|
|**Interaction model**|Read, browse, compare, configure, monitor, purchase, submit, analyze?|

This stops me from treating every brief as “make a modern website.”

For example, a climate-monitoring dashboard, a small-batch ceramics storefront, and a private-equity reporting portal may all need cards and buttons—but their visual behavior should be completely different.

---

## Phase 2 — Generate a visual foundation with `create_make_theme`

For a full-page brief, I call:

`mcp__plugin_make_figma_make_mcp__create_make_theme`

with a short, focused summary of the request.

### What I take from the theme output

It gives me a starting framework for:

- A potential **aesthetic stance**
- Typography direction
- Color and canvas suggestions
- Spacing rhythm
- Component patterns
- Layout ingredients
- Practical guidance for implementation

I treat this as an **art-direction proposal**, not a locked template. The user’s explicit taste, brand constraints, and product context always win.

### Example

If the brief is:

> “Design a dashboard for a boutique architecture practice to track projects, clients, and site visits.”

The result should probably not look like a blue enterprise SaaS dashboard.

I might translate it into:

- **Stance:** restrained architectural studio system
- **Ground:** mineral white or charcoal field, not neutral gray app chrome
- **Typography:** measured grotesk for UI + a distinctive but controlled display face
- **Structure:** precise grid, thin rules, generous white space, plan-like density
- **Accent:** a single clay, oxidized red, or deep green signal color
- **Data treatment:** labeled, calm, and spatial rather than badge-heavy

The theme tool helps establish that direction; I then make it specific to the experience.

---

## Phase 3 — Choose one aesthetic stance and commit

This is the most important stage.

I choose a single visual language that fits the brief, such as:

- **Technical precision** — dark, calibrated, data-forward, compact
- **Editorial clarity** — typography-led, generous, image-aware, intentional pacing
- **Contemporary heritage** — refined materials, measured typography, archival details
- **Playful utility** — bold hierarchy, expressive color, direct interactions
- **Institutional confidence** — durable, restrained, legible, sober
- **Experimental cultural** — poster-like, asymmetric, art-directed, expressive

Then I ensure every section supports it.

### What “commit” means in practice

If the stance is technical precision:

- Typography becomes structured and functional.
- Cards are probably flatter and more systematic.
- Borders and grids do more of the organizational work.
- Colors are restrained and semantic.
- Motion is concise and purposeful.
- Imagery, if present, is controlled rather than decorative.

If the stance is editorial hospitality:

- Composition can breathe and be more image-led.
- Type scale can create pacing and atmosphere.
- The surface may feel tactile or warm.
- Asymmetry may feel natural.
- Dividers can feel like publication rules instead of software chrome.

I avoid blending these without a real reason. A “technical dashboard with luxurious editorial serif headings, glassmorphism cards, purple gradients, and playful sticker badges” usually signals indecision, not sophistication.

---

## Phase 4 — Build the design system before detailing the UI

Once the stance is chosen, I turn it into a small, usable system.

## 4.1 Color tokens

I define semantic tokens rather than styling elements individually:

- `--background`
- `--foreground`
- `--card` / `--card-foreground`
- `--primary` / `--primary-foreground`
- `--secondary`
- `--muted` / `--muted-foreground`
- `--accent`
- `--border`
- `--ring`
- `--radius`

This means the design has rules for:

- What the page surface is
- Where contrast is strongest
- What counts as interactive priority
- How subdued text behaves
- What separates sections
- How focus is indicated

The palette is always selected for the product’s meaning and usability—not just visual novelty.

### Color philosophy

- The **ground** is deliberate: light, dark, tinted, split, image-led, or saturated.
- Accent color is used sparingly for **action, focus, status, and priority**.
- Borders organize; they should not overpower.
- Text hierarchy comes from contrast and type, not merely from making everything gray.
- Accessibility is part of the token decisions from the start.

---

## 4.2 Typography system

I typically establish a hierarchy from two or three families:

1. **Display face**  
    Used for primary headings or editorial emphasis. It sets personality.
    
2. **Body/UI face**  
    Used for readable copy, interface controls, navigation, tables, and descriptions.
    
3. **Mono face, only when justified**  
    Used for data, timestamps, IDs, code, or technical labels—not as generic decoration.
    

Then I define:

- Display scale
- Heading scale
- Body and caption scale
- Weight hierarchy
- Line-height behavior
- Deliberate letter spacing
- Uppercase label treatment, when appropriate

The aim is not “use cool fonts.” It is to make content scan correctly and give the product a recognizable voice.

I also actively avoid repetitive defaults when they do not fit: the same trendy mono/sans pair, overly tight display headings, or a default editorial serif used simply to make a design look premium.

---

## 4.3 Layout, spacing, and hierarchy

I build the macro structure with **CSS Grid** and component internals with **Flexbox**.

### For each page, I establish:

- Content max-widths
- Section rhythm
- Grid column logic
- Card or panel behavior
- Alignment rules
- Desktop-to-mobile collapse rules
- Density model: expansive, compact, or mixed
- Visual anchor(s): hero, key metric, primary action, selected object, image, etc.

The page should have an intentional eye path:

1. What is the user meant to notice first?
2. What explains or supports it?
3. What action can they take?
4. What information is secondary but still reachable?

I do not automatically use three equal cards or a symmetric two-column hero. Those are valid compositions only when the content calls for them.

### Whitespace is functional

Whitespace is not blank decoration. It:

- Makes hierarchy legible
- Gives primary content authority
- Separates conceptual groups
- Reduces cognitive overload
- Helps an interface feel calm even when it contains dense information

---

## Phase 5 — Decide imagery and visual material

If the interface needs visuals, I choose imagery that supports the stance.

That can involve:

- Context-specific photography
- Cropped visual narratives
- Tonal image treatments
- Controlled overlays
- Product shots
- Maps, diagrams, or charts
- No imagery at all, if the product benefits from typographic or data-led clarity

When using photos, I use them as part of the composition—not as arbitrary rectangles inserted to fill space. The crop, overlay, background treatment, and adjacent typography should make them feel native to the interface.

I also ensure descriptive `alt` text and reserve a suitable background color so the layout remains stable while an image loads.

---

## Phase 6 — Translate the stance into components and interactions

Only after the page’s visual logic is clear do I detail UI components:

- Navigation
- Buttons
- Inputs
- Filters
- Tables
- Cards
- Tabs
- Charts
- Accordions
- Status indicators
- Empty states
- Loading and selection states

The component design follows the stance.

For example:

|Design stance|Component expression|
|---|---|
|Technical / analytical|Clear grid, modest radii, high legibility, structured labels|
|Editorial / cultural|Strong typography, softer pacing, image and text interplay|
|Operational / enterprise|Dense, predictable, data-first, durable interaction states|
|Playful consumer|Expressive hierarchy, stronger color signals, direct feedback|
|Premium retail|Material cues, restrained controls, product-focused composition|

If the brief implies interactivity, I implement it. Tabs switch, filters filter, menus open, accordions expand, and charts use actual data structure. The goal is a working interface, not a static illustration of one.

---

## Phase 7 — Add craft without ornament drift

This is where a design becomes polished, but it is also where over-design can happen.

I add small refinements that serve use:

- Hover state changes
- Focus rings
- Selected states
- Subtle transitions
- Clear cursor and affordance behavior
- Meaningful loading or empty states
- Hairline dividers
- Muted labels
- Responsive spacing changes

I avoid additions that are only “visual interest”:

- Random gradients
- Decorative sparkles
- Excessive glowing effects
- Arbitrary blobs
- Extra badges
- Unnecessary icons
- Repeated floating cards
- Decorative images unrelated to the brief

A practical question I ask is:

> Can I justify this element through the product, content, or user task—or only by saying it adds visual interest?

If it is the latter, it probably should not exist.

---

## Phase 8 — Make it accessible and responsive

Accessibility and responsive behavior are not final-stage patches.

### Accessibility baseline

- Body text meets at least **4.5:1** contrast where required.
- Large text meets at least **3:1**.
- Interactive elements have at least **3:1** visible contrast.
- States are shown with more than color alone.
- Focus states remain apparent.
- Semantic HTML is preferred.
- Images have meaningful alternative text.

### Responsive baseline

I include a meaningful breakpoint—often near laptop/tablet scale—where:

- Multi-column layouts collapse
- Navigation adapts
- Padding and gaps adjust
- Data areas become horizontally manageable or reorganize
- Headline scale becomes more compact
- The visual composition remains intentional instead of merely stacked

The mobile version should be designed as a version of the same system, not a desktop page compressed into a narrow column.

---

## Phase 9 — Review against the stance, not just appearance

Before considering a UI complete, I review it through a short set of questions:

### Strategy

- Does it make the product and primary action immediately clear?
- Does the visual direction fit the audience and domain?

### Coherence

- Does every section feel like it belongs to the same system?
- Are typography, color, spacing, borders, and image treatments consistent?

### Hierarchy

- Is the most important thing visually dominant?
- Can a user scan the page without reading every word?

### Usability

- Do interactions work?
- Are controls visibly interactive and stateful?
- Is content realistic enough to judge density and hierarchy?

### Craft

- Are details refined, but restrained?
- Are dividers, hover states, focus states, and responsive transitions intentional?

### Default-resistance

- Did the design become generic because I used a familiar pattern automatically?
- Or is the visual decision actually justified by the brief?

---

# The philosophy in one sentence

`make:aesthetic-stance` is a workflow for turning a product brief into a **deliberate, coherent, accessible, responsive visual system**—then implementing that system faithfully instead of producing generic UI by default.

So yes: for most full UI designs, it is the core **creative-direction layer** of how I work. The remaining layers are implementation discipline, interaction behavior, technical constraints, and iteration based on your feedback.

how about create_make_theme? explain me the full design workflow in the greatest depth and detail possible so that I can understand how you design

`create_make_theme` is the **theme-definition stage** of my full-page UI workflow. It converts a short product/design brief into an actionable visual-system proposal: art direction, typography, colors, layout behavior, component character, and implementation guidelines.

Where `make:aesthetic-stance` tells me **how to think and make design decisions**, `create_make_theme` gives me a **project-specific starting system** to design from.

A useful distinction:

|Layer|Role|
|---|---|
|**Brief**|What is being made, for whom, and why|
|**`make:aesthetic-stance`**|The design method: choose a stance, commit to it, avoid defaults, make a coherent system|
|**`create_make_theme`**|The project-specific visual-system proposal generated from that brief|
|**Implementation**|Translate the chosen system into tokens, layouts, components, interactions, and responsive code|
|**Review / iteration**|Improve the result against the brief, usability, craft, and feedback|

I use the theme tool for a **full interface**, not for a logo, isolated card, single icon, or one small component.

---

