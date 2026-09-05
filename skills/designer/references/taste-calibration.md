# Taste Calibration

This file is calibration, not another workflow step to run through in order. Sampling for variety alone does not stop convergence: a stance can be freshly rolled and still land on a trained-in default, because those defaults are what the underlying models reach for absent a reason not to. Nothing named below is forbidden outright: when a brief is actually calling for one of these treatments, deliver it, and deliver it well. The failure mode this file exists to catch is different, one of these appearing because it's the reflex answer, not because the brief called for it, or surviving into a shipped page after the brief was silent on the question. Grafted with attribution from two outside sources: Anthropic's `frontend-design` skill (terms in its own LICENSE.txt) and `impeccable` v3.5 (Apache 2.0).

## The three saturated default looks

Generated interfaces cluster hard around three visual answers right now, largely independent of what the brief is actually about:

1. **Warm-cream editorial.** A body near `#F4F1EA`, a high-contrast serif display face, and a terracotta accent carrying emphasis.
2. **Near-black plus one hot accent.** A near-black canvas built around exactly one saturated color (acid-green in some briefs, vermilion in others) doing all the signaling by itself.
3. **Broadsheet dense-column.** Hairline rules, zero border-radius anywhere, and tight newspaper-style columns standing in for editorial seriousness.

None of the three is off-limits; each is a real, defensible answer for some brief. What makes them worth naming is that they show up whether or not the subject calls for them: the tell is reaching for one by reflex, not choosing one on purpose. Follow the brief's own words exactly whenever it names a direction, including when that direction happens to be one of these three; a brief that explicitly asks for broadsheet gets broadsheet. Where the brief leaves an axis open, that openness isn't license to default here: spend it on something the subject in front of you actually earns.

*Adapted from Anthropic's `frontend-design` skill's calibration guidance.*

## The cream band, specified

The warm-cream default above isn't one hex value, it's a whole region of color space, and the region is what needs catching rather than just that one shade. In OKLCH terms: L 0.84–0.97, C < 0.06, hue 40–100. Anything in that band still registers as cream, sand, paper, or parchment to a viewer no matter which of those words ends up naming it in the token file, and no matter whether the brief's own language was "warm," "traditional," or "editorial-restraint."

Token names are a tell on their own, ahead of even checking the underlying values: `--paper`, `--cream`, `--sand`, `--bone`, `--flour`, `--linen`, `--parchment`, `--wheat`, `--biscuit`, `--ivory`. Reaching for any of these as a body-background name is itself the reflex worth catching, separate from whatever OKLCH numbers end up behind it.

Three routes carry real warmth without landing in the band:

1. Build the body itself from a saturated brand color, picking from the same family as terracotta, oxblood, deep ochre, or near-black, instead of reaching for a near-white stand-in.
2. A neutral that's genuinely off-white, chroma sitting at zero, or shifted only in the direction of the brand's own color family rather than nudged warm out of habit.
3. A darker, brand-tinted mid-tone body that's recognizably built from the brand's own color rather than a generic warm neutral.

Let the accent, the typography, and the imagery carry "warmth" instead of the body background. That's where the intent actually lands without tripping the default.

*Adapted from `impeccable` v3.5's new-project color guidance.*

## The sage accent, flagged

The accent-side twin of the cream band: a desaturated green — sage, forest, ink-green — in roughly OKLCH hue 130–165 at low-to-mid chroma, carrying the primary action on an otherwise neutral page. Like cream it's a region, not one hex, and unlike cream it always has a justification within reach: green reads as affirmative (checkmarks, power lights, "in the black"), so any product whose key action is affirmative can rationalize it after the fact. The tell is therefore not green's presence but green winning without a named competitor. When the accent lands in this band, the design record should name one alternative hue that was weighed on the product's own grounds and lost; a green with no rejected candidate is the reflex answer wearing the product's clothes.

*Added in-house (2026-07) after eval builds converged on this band through individually defensible reasoning; not from the grafted sources.*

## The leftover accent, flagged

A third band, found the same way as the sage accent: two operations consoles for unrelated products, built blind to each other under the derivation rules, both landed their accent in violet (OKLCH hue roughly 300–335), each with a defensible reason. The mechanism is elimination. A console with a full status set has already spent green, amber, red, and blue; the derivation rule says the accent must never double as a status hue; the brief's own world offers steel, paper, or nothing in particular; and violet is what is left. An accent chosen because it is the only hue not yet taken is not derived from the product — it is derived from the status set, and every product with that status set will land on it.

The tell is the reasoning, not the hue: "the one hue absent from the status set" is a valid constraint and an invalid source. When the accent lands in this band, the design record names what the product's own world offered instead — a material, a convention, a signage color, a brand — and says why that lost to the leftover. Where the world offers nothing, a `none` accent job (a monochrome interaction language with a visible non-color focus) is the honest answer, not the last free hue.

*Added in-house (2026-09) after the stance-derivation acceptance pair converged on this band through independently defensible reasoning; not from the grafted sources.*

## The landing scaffold, and two more layout bands

The same convergence happens on the layout side, and it was found the same way — by measuring what independently reasonable builds actually produced. **The landing scaffold** is the largest of the three: sixteen of twenty landing builds open with one construction, a full-width band carrying a left-ranged headline with no image and an empty right half, and then run a three-up, a pricing trio and an FAQ under it in that order; twenty-two of thirty-two builds across the corpus carry a card grid of exactly three in three columns. None of those four parts is forbidden and each is the right answer to some brief. What makes the run worth naming is that it arrives whole, in that order, whatever the page is about. Each part is earned on its own or it is absent: a three-up by three homogeneous peers the brief itself counts — three features, three benefits or three plans nobody counted are a sales device, not a count; an FAQ by objections a real reader would raise, named in the record; the headline band by an argument that is genuinely verbal, with no artifact to show. Where there is an artifact and no asset to show it with, draw it — an SVG, a painted canvas, a real diagram — as content. The empty right half is the shape a missing image takes, not a composition.

**The almost-equal split** is the second: two tracks at 1.1–1.35 : 1, which is what the word "asymmetric" produces when nothing decided how unequal the two regions should be. It reads as centered that forgot to center — too near equal to feel deliberate, too far from it to feel symmetric. A region that genuinely dominates takes at least 1.5 : 1; regions that are peers take equal tracks; a ratio landing in the band between them is the tell that it was typed rather than derived. Geometry adopted from a supplied reference or an existing design system is excepted and recorded as adopted.

**The sidebar by category** is the third: a persistent left navigation on a console because it is a console. A sidebar is earned by six or more peer destinations, or by a drill model that needs a way back, stated in the record — "operational surface" is a category, not a reason. The same test retires a stat row above a queue that nobody monitors by the numbers, and a main-plus-rail grid on a page with nothing to put in the rail.

*Added in-house (2026-09) from the layout survey; not from the grafted sources.*

## Absolute bans

Match-and-refuse: catching any of these mid-build means stopping and restructuring that piece from scratch, not softening it in place.

- **Side-stripe borders.** A colored `border-left` or `border-right` heavier than a hairline on cards, list rows, callouts, or alerts. Rebuild with a full border, a background tint, a leading icon or number, or nothing at all.
- **Gradient text.** `background-clip: text` filled with a gradient. Rebuild as one solid color and carry emphasis through weight or size instead.
- **Glassmorphism as the default surface.** Blur-and-glass treatment reached for because it looks premium, not because something is genuinely floating over changing content beneath it. Rebuild flat unless the actual conditions for glass are met.
- **The hero-metric template.** A big number, a small label beneath it, a row of supporting stats, a gradient sitting behind the whole thing. Rebuild the hero around the subject's own thesis instead of a generic stat block.
- **Identical card grids.** Same-size cards, each one an icon plus a heading plus a paragraph, repeated down the page without variation. Rebuild with asymmetry, varied card weight, or a structure other than a card at all.
- **An eyebrow above every section.** A small tracked all-caps label sitting above every heading on the page. One deliberate kicker used as a genuine brand device is a real choice; repeating it above each section by reflex is scaffolding wearing a costume.
- **Numbered markers as reflex scaffolding.** `01 / 02 / 03` placed above sections that aren't actually an ordered sequence. Reserve numbers for content that's a genuine process, flow, or timeline, the kind where losing track of the order would actually cost the reader something.
- **Heading overflow at breakpoints.** A long display word, an aggressive clamp scale, and a narrow grid combining to spill past the container on tablet or mobile. Test the actual copy at every breakpoint and lower the clamp ceiling, or rewrite the copy, until it fits.

*Adapted from `impeccable` v3.5's absolute-bans list.*

## The category-reflex check

Run this check across two levels of depth; the deeper one only matters once the shallower one is already handled.

First, the thing this check does not catch. Category legitimately predicts the two *constraints*: a dispatch tool is dense and consequential, a gallery site is spacious and exploratory, and that is the brief being read correctly rather than a reflex firing. It may also bias a *coordinate* — quiet for the dispatch tool, composed for the gallery — and that is still not the reflex. Forcing a playful register onto an operations console to avoid looking derivative is its own failure, not a fix for this one. What category may never predict is a *value* — which orange, which grotesque, which cream. Both checks below test values, never positions.

**First-order.** If the palette and theme are predictable from nothing but the product's category (a wellness app landing on sage and cream, a fintech product landing on navy and gold), that's the first training-data reflex firing. Rework the color strategy and the physical-scene sentence below until the category by itself no longer predicts the answer.

**Second-order.** A second reflex sits one level past the first. Even after dodging the obvious category default, the aesthetic family itself can still be predictable once you also know what was being dodged: an AI workflow tool avoiding SaaS-cream lands on editorial-typographic anyway, a fintech product avoiding navy-and-gold lands on terminal-dark anyway. Clearing the first reflex doesn't clear this one; it just pushes the reflex down a level. Rework again until the combination of category and anti-reference no longer gives the aesthetic family away.

*Adapted from `impeccable` v3.5's AI-slop test.*

## Commitment devices

Work in two passes before any UI code gets written.

**Pass one: plan.** Draft a compact token plan: named colors as four to six hex values, the type roles in play (a display face used with restraint, a body face, an optional utility or mono face), and a layout concept sketched in a sentence or two plus a rough wireframe. Name the signature element in this same pass: the one thing this build will be remembered by.

**Pass two: self-review, then build.** Hold the plan against the brief and ask whether this exact plan would come out the same for any similar brief. Same constraints are expected and same coordinates are fine; same values is the failure. Where any piece looks like the answer this category always gets rather than a choice earned by this specific brief, revise it, and note what changed and why. Only once the plan survives that question should the actual UI code get written, following the revised plan rather than drifting from it partway through the build.

**The signature element.** Spend the one real risk in exactly one place (the memorable thing the design is built around), and hold everything surrounding it quiet and disciplined. A page that takes ten risks reads as noisy; a page that takes none reads as safe. One risk, spent well, earns the attention the rest of the page doesn't ask for.

**Dark vs. light, decided by scene, not by default.** Neither is the safe choice. Before picking, write one sentence describing the actual physical scene: who is looking at this, in what place, under what light, in what frame of mind. If that sentence still leaves the choice open, it hasn't earned its keep yet: keep sharpening the scene, with more specific people and places and light, until the answer becomes the obvious one.

**Color-strategy axis** — the `color commitment` axis in `references/stances.md`. Pick a commitment level before picking any colors:

- **Restrained**: tinted neutrals with a single accent that stays modest, roughly a tenth of the surface or less. Where most quiet product UI belongs by default.
- **Committed**: one saturated color owns a real share of the surface, somewhere between 30 and 60 percent. What a page built around a strong identity reaches for.
- **Full palette**: three or four distinct color roles, each doing its own job on purpose. Suits a marketing campaign or a data-heavy visualization.
- **Drenched**: color isn't applied to the surface, it is the surface. Kept for brand hero moments and campaign pages that want to make an entrance.

*Adapted from Anthropic's `frontend-design` skill's two-pass process and `impeccable` v3.5's color-strategy axis.*

## Copy tells

**No em dashes as punctuation.** Reach for a comma, colon, semicolon, period, or parentheses instead, and treat the typed double-hyphen the same way, not as a permitted workaround.

**No aphoristic-cadence voice as the page's default rhythm.** Watch for a serious statement followed by a short, punchy negation, repeated section after section until it turns into the page's go-to rhythm. Once that same short-rebuttal shape shows up in three or more copy blocks on one page, rewrite toward language specific to what's actually being said there.

**No buzzword family.** Streamline, empower, supercharge, leverage, unleash, transform, seamless, world-class, enterprise-grade, next-generation, cutting-edge, game-changer, mission-critical. Swap each for one specific noun plus a verb spelling out, in plain terms, what the product actually does.

*Adapted from `impeccable` v3.5's copy guidance.*
