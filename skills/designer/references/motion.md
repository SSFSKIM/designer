# Motion

This file teaches the small, role-based motion system to draw from once a page's layout, tokens, and content are in place: the duration and easing scale to use, which CSS properties are cheap enough to animate by default and which cause layout damage, how the same motion vocabulary resolves from the stance's axes, and the reduced-motion contract every nonessential animation needs. Use it at the "craft pass" step, alongside `references/effects-policy.md` for material effects — motion and effects are both additions layered on top of a finished interface, added only where they communicate state change, spatial continuity, or feedback rather than decorating for its own sake — then check the result against `references/qa-protocol.md` before calling it done. Motion is derived, not sampled: it is a resolver over the stance's axes — energy supplies amplitude and character, density supplies speed pressure, criticality caps overshoot and ambiguity, and the material model supplies the spatial vocabulary (`references/material.md`). The duration tiers and easing curves below are the vocabulary that resolver draws from.

Motion serves three goals, in this order: preserve orientation (show where something came from, where it went, or what changed), confirm interaction (make hover, press, selection, loading, and completion states feel responsive), and protect reading and task flow (motion must not delay access, compete with data, or make dense UI feel unstable).

## Duration tiers

```css
:root {
  --motion-instant: 80ms;
  --motion-fast: 120ms;
  --motion-standard: 180ms;
  --motion-slow: 240ms;
  --motion-overlay: 320ms;
  --motion-emphasis: 420ms;
}
```

|Tier|Duration|Use it for|
|---|---|---|
|Instant|`80ms`|Press feedback, checkbox/radio state, very small icon feedback|
|Fast|`120ms`|Hover, focus, border-color, background-color, button-state changes, small tooltips|
|Standard|`180ms`|Tabs, selected-state changes, compact popovers, row expansion, small panel shifts|
|Slow|`240ms`|Small drawers, accordion content, context panels, larger reveal transitions|
|Overlay|`320ms`|Dialogs, mobile sheets, full-size menus, contextual side panels|
|Emphasis|`420ms`|One-time onboarding, celebration, hero reveal, nonessential brand motion|

### Application rules

```text
80ms   → press/tap compression, checkbox tick, icon nudge
120ms  → hover/focus states, color transitions, small control states
180ms  → tab content, popover/tooltip, selected content state
240ms  → accordion, inspector panel, non-blocking contextual expansion
320ms  → modal, sheet, command palette, mobile navigation
420ms  → one-off completion celebration or initial hero composition only
```

Do not make common actions slower than `180ms` unless the animation provides a meaningful spatial transition. For example:

- A button changing color at `320ms` feels laggy.
- A dialog appearing in `80ms` can feel abrupt.
- A data-table row should not drift into place over `400ms`.
- A toast should enter quickly enough to be noticed without pulling attention from the active task.

## Easing curves

```css
:root {
  /* General utility motion */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-enter: cubic-bezier(0, 0, 0, 1);
  --ease-exit: cubic-bezier(0.3, 0, 1, 1);

  /* Softer editorial motion */
  --ease-editorial: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-editorial-enter: cubic-bezier(0.16, 1, 0.3, 1);

  /* Expressive but controlled consumer motion */
  --ease-playful: cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-spring-soft: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* Decisive operational motion */
  --ease-operational: cubic-bezier(0.2, 0, 0, 1);
  --ease-operational-exit: cubic-bezier(0.4, 0, 1, 1);
}
```

### When to use each curve

|Curve|Use|
|---|---|
|`cubic-bezier(0.2, 0, 0, 1)`|Default UI motion: buttons, focus, tabs, menus, compact state changes|
|`cubic-bezier(0, 0, 0, 1)`|Entering elements that should arrive directly and clearly|
|`cubic-bezier(0.3, 0, 1, 1)`|Exits that should get out of the way quickly|
|`cubic-bezier(0.22, 1, 0.36, 1)`|Composed-energy reveals: image and caption, polished card motion, soft page transitions|
|`cubic-bezier(0.16, 1, 0.3, 1)`|Larger calm enters: drawers, menus, image overlays, restrained sheets|
|`cubic-bezier(0.2, 0.8, 0.2, 1)`|Lively-energy interaction feedback and approachable card hover|
|`cubic-bezier(0.34, 1.56, 0.64, 1)`|Small, celebratory overshoot only: a completion check, reward token, tiny icon — not entire panels or core navigation|

### Rules for spring-like easing

Use `--ease-spring-soft` only for small, positive feedback moments:

- a completed habit check,
- a reaction button,
- a tiny badge settling into place,
- a progress reward,
- an icon in a playful onboarding screen.

Do not use spring overshoot for:

- modals,
- tables,
- forms,
- navigation,
- charts,
- enterprise controls,
- destructive actions,
- warnings or errors.

## Properties

### Animate regularly

|Property|Typical use|Why|
|---|---|---|
|`opacity`|Enter/exit, selected content, skeletons, overlays|Low-cost and visually clear|
|`transform`|Hover lift, press scale, panel enter/exit, icon nudge|Usually compositor-friendly and does not reflow layout|
|`background-color`|Buttons, tabs, selected rows, status state|Confirms state without moving layout|
|`color`|Links, labels, icon state|Communicates state cleanly|
|`border-color`|Focus, hover, selected input, panel emphasis|Supports structure without visual drama|
|`outline-color` / `box-shadow`|Focus ring and limited elevation change|Useful when localized and short|
|`text-decoration-color`|Link underline reveal in reading-led copy|Good for text-led interactions|
|`clip-path`|Rarely, for isolated image/art direction|Only for nonessential rich media, not standard controls|
|`grid-template-rows`|Accordion expansion|Controlled exception for semantic content reveal|

### Avoid by default

|Property|Why|
|---|---|
|`width` / `height`|Causes layout work; usually creates unstable content movement|
|`top` / `right` / `bottom` / `left`|Prefer `transform`; positional animation often causes layout/repaint work|
|`margin` / `padding`|Reflows siblings and makes dense layouts jump|
|`font-size`|Causes layout shift and makes text feel unstable|
|`line-height`|Causes reflow and can disrupt reading|
|`letter-spacing`|Can cause jitter, reflow, and text readability issues|
|`border-width`|Moves content and changes component dimensions|
|`filter: blur()`|Expensive at large areas; can look mushy and harm contrast|
|`backdrop-filter`|Expensive and visually inconsistent during animation|
|`background-position` across a whole page|Commonly creates meaningless “drifting” visual noise|
|continuously changing gradient coordinates|Distracting unless the product is explicitly visual/media-led|
|continuous turbulence/displacement filters|GPU-heavy and usually decorative rather than informative|

### Exceptions

**Height or layout-like expansion.** For accordions, disclosures, and content reveals, a controlled layout property may be animated — not because it is free, but because the change is semantically meaningful. Prefer `grid-template-rows: 0fr → 1fr` over a hard-coded `height`, because it can accommodate unknown content length.

**`box-shadow`.** Animate shadows only on isolated objects: a hoverable card, a floating menu, a primary action button, a dialog. Do not animate shadows across every table row or list item in a dense dashboard.

## The motion resolver

Motion has no axis of its own. It resolves from four positions the stance already records: energy, density, criticality, and the material model. Read all four, then pick durations and curves from the tiers above.

### Energy — amplitude and character

|Energy|Resolution|
|---|---|
|quiet|No overshoot. At most one high-salience motion treatment per viewport. Standard and operational curves only.|
|composed|Standard curves, with the editorial curves for reveals.|
|lively|The playful curve for feedback; `--ease-spring-soft` on small positive feedback only.|
|exuberant|Overshoot permitted only if `DESIGN.md` records “overshoot: yes”. Motion may mark state changes as the product's primary expressive channel — that counts as one of the two simultaneous expressive channels the energy rule allows.|

### Density — speed pressure

|Density|Default duration|Overlay duration|
|---|---|---|
|dense|Instant and fast tiers, `80–180ms`|`180–240ms`|
|standard|`120–220ms`|`240–320ms`|
|spacious|`160–260ms`|up to `320ms`|

The emphasis tier (`420ms`) is available only at spacious, or for a genuine one-time moment at any density.

### Criticality — caps

|Criticality|Cap|
|---|---|
|consequential|No overshoot on error, confirmation, or destructive flows. Nothing that could read as a state the system is not in. Common actions never slower than `180ms`.|
|transactional|The same caps, applied on money and data-loss paths.|
|exploratory|No cap beyond the tiers above.|

### Material model — the spatial vocabulary

|Material model|What may move|
|---|---|
|printed|Cuts, fades, colour changes. No translate on hover — paper does not hover.|
|tonal|Fades and small shifts; lightness-step changes.|
|elevated|Lifts and depth transitions between the named tiers.|
|glass over planes|Morphs and plane changes, per `references/material.md`.|

### Three worked resolutions

|Dimension|spacious × composed (an editorial site)|dense × quiet (an operations dashboard)|standard × lively (a consumer app)|
|---|---|---|---|
|Default duration|`160–260ms`|`80–180ms`|`120–220ms`|
|Overlay duration|`320ms`|`180–240ms`|`240–320ms`|
|Main easing|`cubic-bezier(0.22, 1, 0.36, 1)`|`cubic-bezier(0.2, 0, 0, 1)`|`cubic-bezier(0.2, 0.8, 0.2, 1)`|
|Forbidden feeling|Overly productized SaaS animation|Playful bounce, delayed panels, floating cards|Cold abruptness, entirely static reward moments|

These are resolutions, not a separate scale: the same duration tiers and easing curves compress or stretch to the axis position. A spacious, composed surface runs its defaults slower and rides the editorial easing curve; a dense, quiet surface runs at the fast end of the tiers and stays on the standard/operational curve throughout; standard density at lively energy sits in the middle and is the only place `--ease-spring-soft` earns routine use.

Reduced motion overrides every resolution above — whatever the axes resolve to, the **Reduced motion** contract in the next section still governs.

## Reduced motion

Reduced motion is not “disable all feedback.” It is:

- remove nonessential movement,
- keep state changes immediate,
- retain contrast, focus, and selection feedback,
- preserve usability without spatial motion.

Every nonessential animation needs a reduced-motion alternative — this is a requirement, not an optional refinement to add if time allows.

### Global CSS baseline

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 1ms !important;
  }
}
```

For richer effects, add explicit reduced-motion overrides in project code rather than relying on the blanket rule alone:

```css
@media (prefers-reduced-motion: reduce) {
  .interactive-card,
  .playful-primary-button,
  .glass-panel,
  .skeleton::after {
    transition: none;
    animation: none;
  }

  .interactive-card:hover,
  .playful-primary-button:active {
    transform: none;
  }
}
```

### If a JS motion library is in play

Configure reduced-motion handling once, at a single top-level boundary that reads the user's `prefers-reduced-motion` preference and disables nonessential motion for every animated component beneath it — do not special-case the check inside each individual component. Keep the fallback state fully legible even with all transform and opacity motion removed.

### What remains with reduced motion

- Active tab changes immediately
- Focus ring appears immediately
- Toast still appears and can be dismissed
- Accordion still opens
- Selected controls still change fill/border/text
- Progress values still update
- Modal still becomes visible
- Loading states remain visible

Reduced motion removes decorative movement, not product feedback or navigation capability.

## CSS versus a JS motion library

CSS transitions and keyframes are the default implementation for nearly everything above: hover and focus states, button press feedback, color/border/opacity/transform transitions, accordion reveal, small static keyframe effects, skeleton shimmer, simple tab-content entry, and tooltip/menu transitions when the mount state is already retained in the DOM.

Reach for a JS motion library only when CSS cannot express the behavior cleanly:

- enter/exit transitions where the element actually unmounts,
- dialog, toast, drawer, and sheet presence animation that must coordinate mount and unmount,
- coordinated multi-step sequences,
- layout-aware list reordering,
- drag interactions,
- gesture-driven interactions,
- shared-layout transitions where the spatial continuity is genuinely valuable.

Do not reach for a motion library just because animation exists somewhere on the page. An ordinary dashboard should not import an animation framework to handle button hover states — CSS is smaller, more inspectable, and usually more robust for those interactions. Bring in a library for the specific unmount-coordination or gesture case that needs it, not as a default dependency for the whole surface.
