# QA and iteration protocol

This file teaches the pre-delivery check every piece of UI work runs through before it's called done, the states a coherent product needs beyond its happy path, and the discipline that holds a design system together across many turns of a session and many rounds of feedback. Use it at the "craft pass, then QA" step — step 8 of the workflow spine in `SKILL.md` — after `references/motion.md` and `references/effects-policy.md` have added restrained motion and material; run everything below before calling any surface finished. The same discipline applies to later turns too: a request to add a screen, fix a state, or respond to "make it pop" gets checked against this file, not just the first delivery.

## Pre-delivery checks, in order

Most UI work ships without a live render of the result — there's no guarantee a screenshot tool is reachable in the working environment, so the default assumption is blind delivery. Run these ten checks, in this order, before calling anything done. The order is not arbitrary: it runs cheapest and most catastrophic first, because a blank screen is worse than any aesthetic flaw, and the earliest checks are the ones a blind pass can least afford to skip.

1. **Compiles and renders.** Every import resolves, every dependency actually used is declared, no missing entry-point export, no reference to a file that was never created.
2. **Structural completeness.** No "rest stays the same" elisions, no placeholder stubs, every screen or handler referenced actually exists, list items carry stable keys.
3. **Composition, computed rather than seen.** Re-derive the grid math by hand: do column ratios sum, does anything overflow its track, is there a real focal point or did everything flatten to equal weight, is the spacing scale held consistently. Then run the composition QA against what `DESIGN.md` §4 declared. (1) The surface's canonical shape — for a workspace the stat row, the main-plus-rail grid, the sidebar; for a narrative page the headline band with an empty right half, the three-up, the pricing trio, the FAQ — is absent unless §4 names the composition line that earned each part. (2) The declared first-read region is first in DOM order, top-left in geometry, and dominates the first viewport: a share of at least 0.4 for a workspace, one band for a narrative page. (3) No grid-track ratio falls in the 1.1–1.35 : 1 band (adopted or reference geometry excepted, recorded as adopted), and none is byte-identical to a snippet in a reference file. (4) Every repeated group of three or more equal siblings is earned by the volume-and-homogeneity line, and a three-up is three peers the brief itself counts. (5) On a compare task, the compared units share one axis in one region rather than sitting in separate cards. (6) A recorded one-candidate case is exempt from this clause. Where the candidates have been rendered as wireframe HTML, or two builds of a paired brief are being compared, an instrument — `docs/research/scripts/layout-topology.mjs` in this repository — puts them at a first-viewport partition of at least 0.20; candidates that exist only as ASCII are compared by eye instead, for a difference in grouping, co-visibility, or progression. Where a ledger of prior builds exists, the nearest existing build with a different relation model or activity sits at a partition of at least 0.15. Every one of these measures has a blind spot: a fail on one is a reason to look, not a verdict, and the human grid is the referee.
4. **Contrast, checked blind.** Reason about token pairings instead of trusting the eye: every text color is paired with a background known to clear roughly 4.5:1 for body text and 3:1 for large text and interactive controls. Distrust text set over an image (a scrim is mandatory) and any accent-on-accent pairing. When the token system is OKLCH, its lightness channel is a usable proxy without rendering anything: treat a lightness gap of at least 0.4 between a foreground/background text pair as the blind-contrast heuristic floor — a pair under that gap gets flagged for a real check rather than shipped on the assumption it's fine.
5. **Responsive collapse.** Mentally run each breakpoint: does a sidebar or rail become a drawer, does a wide table scroll instead of mushing together, do sticky elements survive, is there a fixed width that will overflow a narrow phone screen.
6. **State coverage.** Empty, loading, error, one-item, and many-items are all accounted for — does a rail or list overflow at twenty rows.
7. **Content pass.** No lorem ipsum, numbers are internally consistent, sibling copy is the same length, sentence case is held.
8. **Interactivity.** Buttons do something, even a stub handler; focus-visible rings are present; icon-only controls carry an accessible name.
9. **Token discipline.** Scan the diff for raw hex values, arbitrary one-off sizes, or ad hoc weights that should be tokens or theme defaults instead, and for values lifted from a worked derivation without a recorded re-derivation.
10. **Scope.** Confirm only what the request needed was touched, and that protected files and unrelated code were left alone.

If a real render is reachable in the working environment, don't stop at these ten — see "Seeing your work" below. Blind checks are the fallback for an environment with no rendering path, not the preferred method once one exists.

## Verify the build against its own law

The checks above catch generic craft failures. This one catches a subtler and more damaging failure: the finished page quietly contradicting the `DESIGN.md` it committed to. A stance is only worth writing down if the build actually holds to it, and the most common way a committed page still reads as AI-generated is that it declared a rule and then broke it — because the QA pass attested compliance in prose instead of checking the rendered markup. Do not attest; verify. Read the `DESIGN.md` law, then check the built output against each rule it states, mechanically wherever the rule is mechanical:

- **Repeated structural labels.** If the law says an eyebrow or kicker — a small uppercase, letter-spaced label above a heading — is used sparingly or once, grep the markup and count how many section headings actually carry it. The same kicker stacked above three or more sections is the exact "eyebrow on every section" tell the taste layer bans (`references/taste-calibration.md`), and it is one of the strongest reasons a committed page still feels generated: a device that marks every section marks nothing. Remove the repeats until the label earns its place.
- **Color literals outside the token block.** If the law says every color is a token, grep for hex, `rgb(`, `hsl(`, and `oklch(` occurrences outside the `:root`/token definition — including inside inline SVG attributes and `<style>` rules, the two places drift hides. Any color literal loose in the markup is a future inconsistency; move it to a named token. A status hex or an illustration's internal colors are exceptions only if `DESIGN.md` actually names them as exceptions.
- **Ground against its own claim.** If the law claims the page stays out of the cream band — or commits to any specific ground — re-derive the primary background token's OKLCH and confirm it. A background at lightness 0.84–0.97, chroma under 0.06, hue 40–100 is in the cream band no matter what the prose says. Reconcile the build to the claim or the claim to the build, but never ship the two disagreeing.
- **Layout against its lines.** Check the dominant region, reading order, columns, and repetition that `DESIGN.md` §4 declared against the page that was actually built, mechanically wherever the rule is mechanical: read the DOM order and the resolved grid tracks rather than trusting the wireframe that was drawn. A page that declared peer panes and shipped a rail of unrelated cards, or declared a compare task and shipped one card per supplier, broke its own law as surely as one that declared a single accent and used three.
- **Clone check.** Would this `DESIGN.md` and this token block come out the same for a different product in the same category? The same constraints are expected — two all-shift operations consoles both land at dense and consequential, and that is the brief read correctly. The same coordinates are plausible: both may land at quiet as well, and neither has copied the other. Identical values are the tell. Mechanically: the accent hex, the display family and the type ramp must not be byte-identical to any of the worked derivations in `references/stances.md` (`#D46B2C`, `#A9462D`, `#B65A3C`, `#2B7B78`, `#FFB94D` and their font triples) unless `DESIGN.md` re-derives them for this product with a product-specific reason. And if a sibling build for a related product exists in the workspace, diff the two token blocks — monoculture is visible across two builds long before it is visible in either one alone. This check does not apply to an adopted design system — there the values are expected to match the system — and for a persona build the persona's own QA lens governs the hue and value questions.
- **Material against its model.** Check the built surfaces against the material model `DESIGN.md` declared, using `references/material.md`'s checkable consequences. Printed: `box-shadow` appears nowhere except a modal. Tonal: no shadow on a card at rest. Elevated: every shadow in the stylesheet is one of the named tiers, and each tier means a height. Glass over planes: no glass host and no `backdrop-filter` outside the declared plane surfaces, and none at all on rows, lists, tables, or prose. When glass is in play, run that file's "QA additions for glass" alongside this list.

The principle generalizes past these six: any rule the `DESIGN.md` states in checkable terms — one accent doing real work, borders thin and low-opacity, a mono face only on tabular data — is a rule this pass verifies against the actual output, not against a memory of having intended to follow it. This is also the cheapest lever against the "still feels AI" complaint: the page already committed to being specific; this check makes sure it stayed specific.

## Top defects by frequency

Ranked by how often each one turns up in delivered work, most common first:

1. **Hardcoded values that should be tokens** — raw hex, an arbitrary one-off size, a color that will drift from the token system the moment it's touched again. The most common defect by a wide margin.
2. **Contrast risk on secondary or muted text and text-over-image** — the exact thing a blind pass can't verify by eye.
3. **Flattened hierarchy** — everything ends up the same visual weight, with no earned focal point.
4. **Responsive overflow** — a fixed width or a wide table that breaks a narrow layout.
5. **Missing non-happy states** — empty, error, or loading skipped entirely.
6. **Inconsistent spacing** — mixed scales with no governing system.
7. **Sibling copy-length mismatch** that wrecks a grid's rhythm.
8. **Icon-only controls with no accessible name.**
9. **Over-touching** — refactoring or restyling things the request never asked for.
10. **Placeholder or stub leakage** — a stray TODO or a half-wired handler that survived to delivery.

This ranking reflects what blind delivery makes likely more than it reflects a universal defect rate — the top three are direct consequences of not seeing pixels before delivering, so they get over-indexed on accordingly. That weighting shifts once a live render is available; see below.

## Seeing your work

Everything above exists to compensate for a structural limitation: without a rendered preview, delivery is blind, and both the checklist and the defect ranking are shaped by that constraint.

That constraint isn't universal, and it shouldn't be treated as the default once it no longer applies. When a browser automation tool is available in the working environment — a headless-browser or screenshot capability such as the `playwright-cli` skill — use it before delivering, every time a surface's layout or visual treatment changed:

- **Screenshot at a minimum of two viewport widths** — one desktop-scale width and one narrow, phone-scale width — so the responsive collapse gets checked against an actual render instead of a mental model of one.
- **Look at both screenshots and re-review composition and contrast with eyes**, not just computation: is there a real focal point, does the hierarchy read the way the math predicted, does the text-over-background pairing actually look legible rather than merely calculate as legible.
- **Do this before delivering**, not after — a screenshot taken to confirm a suspicion once the user has already complained is QA that already failed.

Blind checks are the fallback for an environment with no rendering path reachable, not the preferred method. A browser tool sitting unused while work ships on blind reasoning alone is a gap in the QA pass, not a valid shortcut.

## Unglamorous states

A coherent happy path with inconsistent empty, loading, error, or permission states is not a coherent product — these are where a design system actually gets tested. All six states below reuse the same surfaces, tokens, and type roles the happy path already established; none of them invent a separate visual language for the occasion.

### Empty

Answer, in the copy and the layout: what's absent, why it might be absent, and what the user can do next. Distinguish "no data yet" from "no results match the current filters" — they're different states with different fixes.

**Recipe:** a small role-appropriate icon, an eyebrow label naming the context, a heading stating the specific absence (not "No results" alone), one line of supporting copy, and exactly one action — "Create the first X" for a genuine first-run empty, "Clear filters" for a filtered-to-empty state. Keep it inside the normal page container using the card/surface token already in use elsewhere, not a bespoke full-bleed illustration panel.

**Rules:** don't imply an error when there's simply no content yet. Don't offer five possible actions when one covers it. Skip a large decorative illustration unless the product is genuinely consumer- or image-led.

### Loading / skeleton

A skeleton exists to preserve the final layout's dimensions and information hierarchy while data resolves, not to fill time with motion.

**Recipe:** shape each skeleton block to the dimension of the real content it's standing in for — a heading-width block above a body-width block, a row grid matching the eventual table's column proportions — so the page doesn't jump when real content arrives. Mark the container `aria-busy="true"` with an accessible label, and use a single quiet shimmer treatment rather than several animations running at different speeds — reduced motion should turn it off entirely, the way `references/motion.md` already treats a skeleton's shimmer as nonessential motion.

**Rules:** don't show a skeleton for a load shorter than roughly 300–500ms — it flashes more than it helps. Don't center a spinner over a data table whose structure is already predictable; skeleton the structure instead. Don't use high-contrast shimmer.

### Error

An error state preserves context, explains impact, and offers a way forward — it does not replace the whole page over one failed section.

**Recipe:** keep the failed section in its original position in the layout. Pair a status icon with a short label naming what's unavailable, a heading, one line of plain-language explanation, and a retry action when retry is actually possible. Use `role="alert"` for a blocking or destructive error and a quieter, less interruptive status pattern for a passive one.

**Rules:** never expose a stack trace or technical error code in ordinary product UI. Don't use the error color as a full-section or full-page background — reserve it for the accent details (icon, border, label) that mark the state as an error. Don't collapse an entire page because one chart or table failed to load.

### Zero-data chart

A chart with no data yet is not an error, and it must never render a flat baseline that could be mistaken for a real measured value of zero.

**Recipe:** keep the chart's container, heading, and axis framing exactly as they'll appear once data exists, so the page doesn't reflow when it does. In the plotting area, replace the series with a centered icon, a heading naming the specific absence ("No budget activity to chart yet," not "No data"), one line explaining the condition (no date range selected, nothing connected yet, no reporting permission), and an action only if the user can actually create or connect the missing data.

**Rules:** never draw a zero baseline as if it were an observed value. Don't hide the chart region entirely — an empty, correctly framed chart tells the user where the data will eventually live.

### Long-content overflow

Overflow needs a deliberate strategy at the screen level; truncating arbitrarily to make content fit is not a strategy.

**Recipe:** for tabular data, let the table scroll horizontally inside its own container at its real minimum width rather than compressing every column into a narrow layout; on the narrowest breakpoints, prioritize the columns that matter or provide a detail view for the rest. For long prose, constrain the reading measure (`max-width: 68ch` or similar) rather than letting a line run the full container width. Truncate a cell or line only when the full content is reachable another way — a detail view, a tooltip, a dialog, an expandable row, or an accessible title attribute.

**Rules:** never truncate a critical error message, permission explanation, legal copy, or a primary task label. Test every layout with the longest realistic name, date, or value the domain actually produces, not a short placeholder that happens to fit.

### Permission denied

A permission state makes three things clear: what's unavailable, why (if it's safe to say), and what the user can do next.

**Recipe:** the same card/surface treatment as an empty state — icon, eyebrow, heading naming what's restricted, one line explaining the boundary of the current role, and a "request access" action only if the product can actually fulfill that request; otherwise, point to who can grant it. Keep global navigation and the screen's title or breadcrumb visible so the user still knows where they are.

**Rules:** never make a permission denial look like a broken page. Never leak, in the denied-state copy itself, information the user isn't authorized to see. Never show a request-access action the product has no path to fulfill.

## Multi-turn coherence

A session that runs many turns has the same underlying problem as blind delivery: no live feedback loop forcing a check against the original decision. The defense is the same in both cases — reload the source of truth, match what already exists, and change only what the request actually earns.

**Extend, don't redesign, by default.** A later turn — "now add a settings screen," "add a chart to the overview" — is not license to re-theme. Reuse the existing shell, navigation, and page pattern; pull the same tokens and the same components the earlier screens already established. Only redesign a piece of the system if the user explicitly asks for it, or if a genuinely new kind of surface can't fit the existing system at all — and even then, say so explicitly rather than drifting silently into a second visual language.

**Refactor triggers are concrete, not aesthetic.** Pull a piece of UI out into its own reusable unit when:

- it's reused in more than one place — extract immediately, don't wait for a third use,
- the file holding it has grown long enough that a single change now requires scrolling past unrelated code,
- a section has its own meaningful state (a form, a multi-step flow), or
- a third variant of something inline is about to get added.

Don't pre-emptively split things apart on the first turn before any of these triggers exist — premature componentization creates its own mess. Extract when reuse or size actually earns it.

**Token-drift defense: the established system is constraint, not suggestion.** The token file is the single source of truth, and later turns never redefine what it already provides. Reach for the semantic token or role already in use — the card surface, the muted-foreground role, the established border token — rather than a raw value, so a turn-five change inherits a turn-one decision automatically instead of reinventing it. Any new color has to become a named token, not a one-off value dropped into a component. Before adding new UI, scan for the pattern the system already established — a badge treatment, a card's padding, a heading's scale — and copy it rather than improvise a new one. Drift happens exactly when a later turn improvises locally instead of reaching back to what's already defined; the fix is always to reach back.

**What to re-read before each new change:**

- **The token file** — nearly always, to reload the exact token names and values in play rather than guessing a color that doesn't exist or duplicating one that does.
- **`DESIGN.md`**, if the project has one — before building any new UI, every turn; the check-the-design-law-first rule doesn't expire after the first screen.
- **The specific screen or component being touched** — read it before editing, even if its state is already tracked, so the change matches the surrounding idiom: comment density, naming, spacing conventions.
- **The project's dependency manifest** — before using any library, to confirm it's actually installed and at what version.
- **The type/font file**, only when the change is adding a new type role.
- **Any supplied reference or imported design the current turn points at**, if the turn references one.

## Translating vague feedback

Vague feedback is a real signal, not an implementation instruction — it means something is mismatched in hierarchy, identity, density, contrast, materiality, or product fit. Don't translate it literally ("make it pop" does not mean "add a gradient and a bigger shadow"). Diagnose first, apply levers in order, and protect the parts of the system the feedback isn't actually about.

### "Make it pop"

**Diagnose, in order:** is the primary message or action visually clear; is everything the same visual weight; is the section too symmetrical or too evenly spaced; is the color system too low-contrast for the priority it needs to carry; is there a missing focal object (a key metric, an exception, a chart, a CTA); does "pop" actually mean more brand personality rather than more hierarchy.

**Levers, in order:** hierarchy first (relative scale, section proportion, a key object made larger or more immediate, supporting information demoted); then composition (break an equal-card layout, create an asymmetric primary/secondary relationship, introduce a clear visual anchor); then contrast (strengthen foreground/background contrast on the primary element, a controlled accent only in the primary area, better surface separation); then typography (a stronger display or metric treatment, selective scale increase, better label/value contrast); then semantic visual material (a chart, progress state, meaningful icon, or image, only if it clarifies the task); only then micro-interaction (a restrained hover or active state, and only after the static hierarchy already works).

**Refuse to change:** don't add a gradient, glow, blob, animation, or decorative image without a role. Don't make every card colorful — that destroys the ability to prioritize at all. Don't increase every type size. Don't replace a coherent palette with neon accents to fake intensity. Don't add a shadow to every surface. Don't turn an operational, scanning-and-action interface into a marketing page.

### "Feels bland"

**Diagnose, in order:** does the interface have a recognizable stance; does the system feel specific to this product or generic to software in general; are type, color, spacing, and shape all neutral in the same way; is there any visual rhythm or pacing across the page; is the content itself generic or placeholder-like; is there a distinctive material, editorial, technical, or cultural point of view at all. "Bland" is rarely solved with more decoration — it usually means no decision in the system was actually committed to.

**Levers, in order:** stance first (name what the product should feel like and remove decisions that belong to a different stance); then typography (a stronger type pairing, a real role for display type, better labels and metadata); then ground and surface (revisit the page's temperature, reduce generic gray-card repetition); then composition (stronger proportion and pacing, some sections expansive and others compact, more deliberate whitespace); then content specificity (replace generic labels and filler with product-specific language and data); only then a selective signature detail (one distinctive data treatment, crop, or border rhythm — not several).

**Refuse to change:** don't add clutter to compensate for weak art direction. Don't introduce five fonts, several gradients, or multiple illustration styles at once. Don't add decoration that can't repeat coherently across the rest of the product. Don't sacrifice clarity for personality. Don't abandon an existing design system unless the feedback is explicitly about redesigning it.

### "More premium"

**Diagnose, in order:** does "premium" mean more exclusive, more crafted, more calm, more expensive-looking, or more trustworthy; is the current design visually noisy, crowded, or overly promotional; are typography, imagery, spacing, and surfaces sufficiently controlled; are there too many colors, badges, shadows, rounded shapes, or competing calls to action; is the content quality itself undermining the intended perception; does the audience actually benefit from restraint, or do they need operational directness instead. "Premium" rarely means gold, blur, glass, and a serif face — it usually means better judgment, more restraint, and clearer hierarchy.

**Levers, in order:** reduction first (remove redundant controls, reduce competing visual states, simplify card structure, limit accents); then typography (better display/body contrast, more whitespace around important type, fewer weights, refined letter-spacing and line-height); then surface and material (better neutral temperature, fewer shadows, quiet texture only where it fits, finer borders); then image direction (better crop and tonal treatment, fewer and better images); then interaction (smoother, quieter hover/focus/selected states, less exaggerated motion); then content (replace generic sales language with concrete proof, provenance, or expertise).

**Refuse to change:** don't use gold as shorthand for luxury. Don't add a gradient merely to signal expense. Don't make every corner pill-shaped. Don't hide usable information just to make a dashboard look sparse. Don't drop to low-contrast type that harms accessibility. Don't use "premium" styling to mask weak content or a confusing flow.

### "Too corporate"

**Diagnose, in order:** which part actually feels corporate — type, copy, layout, color, density, imagery, language, or interaction; is the product genuinely institutional or high-trust, in which case "less corporate" means less generic, not less reliable; are generic enterprise patterns dominating (an anonymous blue CTA, a gray dashboard shell, dense navigation, badge overload, equal cards, jargon-heavy copy); does the design lack warmth, specificity, or human language; is the ask actually for more editorial, more playful, more tactile, or more direct.

**Levers, in order:** content voice first (replace abstract business language with direct, product-specific language, reduce jargon, use human-readable labels); then typography (move away from default enterprise type where appropriate, reduce excessive uppercase label density); then composition (break rigid equal-grid structure, use more content-led rhythm, reduce over-boxing); then color and material (move from anonymous blue-gray to a context-specific palette, use accent color with semantic restraint); then imagery (real people, projects, and work, not generic stock); then interaction language (make controls direct — "Edit project settings," not "Manage workspace configuration," if that's what it does).

**Refuse to change:** don't remove clarity, accessibility, or predictable navigation just to feel less corporate. Don't turn a serious medical, financial, legal, or operational product into a whimsical brand campaign. Don't replace a useful table with decorative cards. Don't scatter personality into every component without a controlled role. Don't strip status semantics, audit context, or error clarity from a high-stakes product.

### "I don't like it"

This is the broadest feedback, and the first job is locating the actual objection.

**Diagnose, in order:** visual taste (colors, fonts, shapes, or imagery feel wrong), product fit (doesn't feel like the audience, category, or brand), hierarchy (unclear what matters or where to look), usability (too dense, too empty, confusing, or hard to act on), reference mismatch (an unspoken reference the result is far from), or scope mismatch (a marketing experience delivered where an operational tool was needed, or the reverse).

**Levers, in order:** request concrete comparison points first (one thing that feels wrong, one thing that feels right; ask whether the issue is visual direction, density, navigation, content, or functionality; ask for a reference only if it will materially change the next attempt); then re-state the chosen stance and check whether it's actually the wrong one — if so, change the stance before polishing components; then audit the largest visual decisions (ground color, type pairing, layout composition, primary hierarchy, image strategy); then change the system, not isolated symptoms (a wrong button radius won't fix "too corporate," a font swap alone won't fix bad hierarchy); then protect what's objectively working (accessibility, real interaction, semantic structure, responsive behavior, useful information architecture) unless those are actually part of the complaint.

**Refuse to change:** don't make random cosmetic changes just to show activity. Don't destroy a working information architecture because the palette needs revision. Don't remove accessibility or responsive behavior to match a static reference image. Don't keep polishing a stance the user fundamentally dislikes. Don't claim to understand a vague dislike without first identifying which dimension is actually failing.
