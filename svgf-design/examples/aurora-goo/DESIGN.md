# Aurora — Campaign Design Law

*(Landing-page face of Aurora, the spatial-audio listening-room app. Same
product as `examples/aurora-glass`, different surface: that build is the
listening room itself — product UI, browsed and operated. This build is the
page that sells the room before anyone's opened it — no login, no room
list, no scrub bar. Read `examples/aurora-glass/DESIGN.md` first; this file
is written as the deliberate contrast to it.)*

## 0. Stance commitment

**Memphis** — Ettore Sottsass: geometric primary shapes on a pastel ground,
asymmetric composition, playful without reading childish. Aurora's landing
page gets to be the loud room the product's own control surface can never
be — this stance is the one in the sampler's whole library whose default
material family (per `materials-map.md`'s stance table) *is* goo, which is
exactly the mechanism this build needs to sell "the room takes shape when
you walk in" as a literal, huggable visual idea rather than a metaphor
described in copy.
**If a decision is ever ambiguous, choose the bolder, more legible-as-play
option — this is the Awwwards-ceiling arm, not the Apple-neat one.**

**Sampler + rejected ingredients.** `node scripts/sample-ingredients.mjs
--seed 404` (run from repo root) drew stances `memphis`, `vernacular`,
`data-dense`; typography traditions Condensed/expressive-display and
Humanist serif; canvas treatment textured-paper/cream. `memphis` was chosen
over the other two sampled stances because it is the only one of the three
whose `materials-map.md` default family is `goo` — matching this build's
committed brief directly, the same test `aurora-glass`'s DESIGN.md applied
when it picked `swiss` for `glass`. Per `stances.md`'s mapping table,
`memphis` maps to **Playful consumer (variant)**, not a from-scratch
derivation and not a straight port either — the row's own instruction is
followed exactly: "keep the one-primary-interaction-color rule and the
soft-spring motion curve, but shift the ground toward a pastel rather than
lavender-white, and let the support colors (mint/peach/sky) run more
saturated and more geometric." The typography-tradition and canvas-treatment
sampler picks are declined outright, same reasoning `aurora-glass` used for
its own decline: a stance mapped to a named system variant doesn't take
"derive fresh" ingredients, and "textured paper/cream" specifically would
also collide with the Material law below (memphis's own `materials-map.md`
row lists `grain-print` under "Families explicitly OFF" with no named
exception for this stance — unlike `y2k-web`, `deco`, or `topographic`,
which each get one named cross-family allowance). This build stays goo-only
by construction, not by omission.

## Material law

- **Family.** `goo`. **Register classifier** (`materials-map.md`'s
  classifier, run against *this surface*, not the app as a whole): does a
  person operate this page to accomplish a transactional task — enter data,
  work a flow, complete a purchase? No. Every control on this page is
  navigational or persuasive (nav links, "Start listening free," "See how a
  room comes alive," footer links) — none completes a transaction on this
  page itself; "Open Aurora" hands off to the product surface
  `aurora-glass` builds, it doesn't reproduce it here. That makes this
  page's entire job "communicate, announce, sell" — the classifier's second
  test, **campaign/brand**, ceiling **Awwwards-expressive**. This is the
  exact fork `aurora-glass`'s own classifier note names: that build answered
  "yes" to the operate-a-surface test (browse rooms, join one, control
  playback) and got **product UI → Apple-neat**, with goo "banned outright,
  no exception." Same product, same designer, two different surfaces, two
  different verdicts — the contrast is the point of this pair, not an
  inconsistency between the two DESIGN.md files.
- **The one signature surface.** A single named hero identity, built from
  two goo instances that read as one moment: (a) a **static four-blob
  organic cluster** — the page's hero mark, standing in for "a room's shape"
  — and (b) **one interaction merge** directly beneath it, demonstrating in
  real time what the copy claims: two separate presences (you, a friend)
  fusing into one shared room the instant the second one joins. Both use the
  same `feGaussianBlur` → `feColorMatrix` → `feComposite` chain and the same
  tuned alpha row (`values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 18 -7"` —
  N=18, K=-7, cutoff `|K|/N ≈ 0.389`), differing only in `stdDeviation`,
  scaled to each instance's own size. One alpha law, three instances (the
  third is the supporting motif below) — never re-derived per element.
- **Dosage.** 1 signature (the hero identity, both halves above) + 1
  supporting: a small **static** two-blob accent (`#svgf-goo-accent`,
  `stdDeviation="9"`) next to the "312 rooms merged this week" stat in the
  proof strip — visibly quieter than the signature (roughly a third the
  linear size, static with no interaction path, two circles instead of
  four-or-two-in-motion, `role="img"` rather than `role="status"`). 1 slot
  of headroom unused. Nothing else on the page touches goo — the nav, the
  six room cards, the testimonial, and the footer are all plain
  Memphis-variant surfaces with flat geometric accents (a Sottsass
  circle/triangle motif drawn as ordinary fill shapes, no filter). No other
  material family appears anywhere in this build — `glass`, `grain-print`,
  and `lighting` are declined per the stance-commitment note above, not
  merely unused.
- **Ground plan.** `grounds.md`'s **Authored SVG/gradient grounds**, sitting
  under the hero and its blob cluster: three radial hue washes at full
  saturation (`--support-sky`, `--support-peach`, `--support-mint` — the
  same three hues the goo blobs themselves are drawn in, so the cluster
  reads as condensed from its own backdrop) plus a `repeating-linear-gradient`
  diagonal band pair in two close pastel-cream values, clearing both the
  ≥3-hue-stop and the structural-geometry bar this file's recipe names.
  Chosen over real photography or simulated product content per
  `grounds.md`'s own register guidance: "Campaign/brand surfaces prefer
  authored art or photography — a hero, a launch page... has no 'real data'
  to be truthful to." A landing page inventing a fake "live waveform" the
  way `aurora-glass`'s product surface legitimately does would be dishonest
  content, not atmosphere; abstract authored gradient is the truthful choice
  here, the mirror image of why the other build chose simulated content.
- **Fallback-tier plan.** The hero's static cluster is unconditional — it
  renders identically regardless of JS or hover support, so the page's
  headline claim is never dependent on the interactive half firing at all.
  For the interaction merge specifically: hover works with zero JS on any
  pointer-capable browser; a `<button>` (`.merge-trigger`, a real control
  outside the goo group) sets `data-active` for touch/keyboard users via a
  few inline lines of vanilla JS. If JS is disabled and the input has no
  hover (a touch device with scripting off — the only context where neither
  path fires), the pair simply stays in its resting, unmerged state with its
  caption text already naming what merging does ("Micah hasn't joined yet.")
  — never a broken or empty-looking state, since the fully-merged form is
  already on screen in the static hero above it.
- **Register ceiling.** Awwwards-expressive — the north star this file's
  own reference chapter (`goo.md`) names for campaign/brand work. Bold
  cluster geometry, full saturation on the support hues, a real interaction
  payoff on hover/press. Still bounded by the family's own bans regardless
  of ceiling: goo never on the nav, the CTA buttons, the room cards, or any
  paragraph of body copy; no ambient looping; the filter itself never
  re-parametrized per frame; every bit of state the merge shows also exists
  as `role="status"` text.

**Build note — one alpha law, three `stdDeviation` instances, region math
recomputed per instance (not copied from `goo.md`'s worked examples, whose
geometry is smaller and centered differently):**

| Instance | Shapes (cx, cy, r) | `stdDeviation` | Bbox (x, y, w, h) | Reach margin used (≥3×σ) | Filter region (`userSpaceOnUse`) |
|---|---|---|---|---|---|
| Hero cluster (`#svgf-goo-hero`) | (110,150,42) mint · (210,110,58) sky · (320,150,66) peach · (400,190,40) mint | 16 (reach 48px) | 68, 52, 372, 178 | 50px | `x="18" y="2" width="472" height="278"` |
| Interaction merge, resting (`#svgf-goo-merge`) | (90,90,34) mint · (230,90,34) peach | 12 (reach 36px) | 56, 56, 208, 68 | 40px | `x="16" y="16" width="288" height="148"` |
| Supporting accent (`#svgf-goo-accent`) | (40,45,20) mint · (92,45,24) peach | 9 (reach 27px) | 20, 21, 96, 48 | 30px | `x="-10" y="-9" width="156" height="108"` |

Every region's margin exceeds its own instance's `3×stdDeviation` reach
figure, and every region's bounds sit fully inside that instance's own
`viewBox` (hero: `0 0 520 300`; merge: `0 0 320 180`; accent:
`-10 -9 156 108`) — nothing is clipped by the SVG viewport before the
filter even gets a chance to bleed.

Edge-to-edge gaps, checked against each instance's reach
(`2·stdDeviation·(1−|K|/N)`, all three instances share `|K|/N ≈ 0.389`, so
reach ≈ `1.222·stdDeviation`):

- Hero cluster: mint↔sky gap ≈7.7px (reach ≈19.6px at σ=16 → bridges); sky↔
  peach and peach↔mint already overlap directly (negative gap) before any
  blur — the cluster reads as one continuous silhouette from a mix of direct
  overlap and goo-bridged near-touches, not four separate circles trying to
  fuse from a distance.
- Interaction merge: resting gap 72px (reach ≈14.7px at σ=12 → nowhere close,
  reads as two clearly separate presences); merged gap (each blob translated
  33px inward) 6px (well inside reach → fuses).
- Supporting accent: gap 8px (reach ≈11.0px at σ=9 → bridges), a permanently
  merged, static pair — it never has a "resting apart" state to contrast
  against, which is what keeps it a plain static accent rather than a second
  interactive moment competing with the signature.

## 1. Palette, with usage rules

Playful consumer's structural roles ported, ground and support hues
re-derived per the stance-commitment note:

```
--background: #FCEEDD   (warm pastel cream — Memphis's "pastel, not
                          lavender-white" instruction; also reads as the
                          product's own dawn palette, seen from underneath)
--foreground: #241C33
--card: #FFFFFF
--card-foreground: #241C33
--primary: #5A47D5      (kept intact — Playful consumer's one interaction
                          violet; CTA buttons, focus rings, links only)
--primary-foreground: #FFFFFF
--secondary: #F1E1C6
--secondary-foreground: #3D2E16
--muted: #F5EDE0
--muted-foreground: #7A6F5E
--accent: #FFB94D       (kept intact — badges/labels only, never a second
                          interaction color)
--accent-foreground: #3B2500
--border: #E4D2B8
--ring: #5A47D5
--support-sky: #1FA9E8   (goo blob hue + hero-ground wash — saturated per
--support-peach: #FF6F47  the Memphis-variant instruction, "more saturated
--support-mint: #22BE86   and more geometric" than Playful consumer's own
                           pastel mint/peach/sky)
--support-sky-foreground: #062A3D
--support-peach-foreground: #3A1206
--support-mint-foreground: #063223
--success: #1F9E67
--warning: #C77B12
--danger: #D34858
```

`--primary` does exactly two jobs — the primary CTA ("Start listening
free," "Open Aurora") and focus rings — never a card, a divider, or an icon.
`--support-sky/peach/mint` are a **named exception**, the direct analogue of
`aurora-glass`'s room-hue exception: they exist only inside the hero ground
and the three goo instances (hero, merge, accent); they never decorate a
room card, a nav item, or body copy. `--accent` (amber) is reserved for the
"Live" status badge and testimonial attribution labels — literal marker
roles, never decoration.

## 2. Typography, with placement rules

Three roles, held everywhere: `--font-display` (headline, section titles,
room names — a geometric/expressive system-sans stack standing in for
Bricolage Grotesque, zero webfonts), `--font-ui` (nav, body, buttons,
captions), `--font-mono` (listener counts, stats, timestamps — tabular data
only, matching `aurora-glass`'s own mono convention for the same kind of
content). Condensed/expressive-display and Humanist serif were sampled and
declined per the stance-commitment note; Memphis's own "variant of Playful
consumer" mapping ports that system's type ramp and roles rather than
introducing a fourth tradition.

## 3. Canvas & texture

The entire page sits on the pastel `--background`; the hero section alone
carries the authored gradient ground (radial hue washes + diagonal band
pair) named in the Material law. No grain, no paper texture, no photography
anywhere — declined outright, not merely unused (memphis's `materials-map.md`
row has no cross-family exception the way `y2k-web`, `deco`, or
`topographic` do). The dosage budget goes entirely to goo.

## 4. Layout system

Single-column narrative page, generously asymmetric (Memphis's own
composition instinct): hero splits roughly 55/45 headline-copy vs.
blob-cluster rather than a centered symmetric hero. Six room cards sit in an
intentionally uneven grid (not a uniform 3×2 card wall) — three across on
wide viewports, reflowing to two then one under the collapse below.
Sections separated by generous `--space-20`/`--space-24` rhythm, no
dividers doing the structural work borders would do in a denser product UI.
**Responsive collapse, ≤880px:** nav collapses to logo + a single "Open
Aurora" CTA (secondary links move below the fold to the footer); the hero
goes single-column, blob cluster moves below the headline/CTA stack instead
of beside it; the room-card row goes to a single column; the interaction
merge demo's two SVGs stack the trigger button beneath the graphic instead
of beside it.

## 5. Component canon

Primary/secondary/ghost buttons (Playful-consumer-variant spec, `--radius-2`
not the system's own `--radius-4/5` — Memphis's "primary-shape energy over
rounded-pill softness" instruction caps everyday chrome at a modest round
and reserves `--radius-full` for the handful of true circles: avatar
initials, the "Live" status dot, stat-strip accent dots) · room card (flat
`--card` surface, hairline border, host name + genre + listening count, no
shadow at rest, `--shadow-card` on hover only) · stat block (mono figure +
label, one paired with the supporting goo accent) · goo hero identity
(canonical, exactly one instance) · goo interaction merge (canonical,
exactly one instance, gated behind a real `<button>`) · testimonial card
(quote + attributed real proper noun, reusing `aurora-glass`'s own room-host
cast) · footer (plain, same voice as `aurora-glass`'s).

## 6. Voice

Confident, warm, concrete — sells a feeling with specifics, never
exclamation points doing the enthusiasm's job. Real proper nouns throughout:
the six rooms and their hosts are `aurora-glass`'s own cast (Nocturne/Mara
Voss, Low Tide/Theo Anders, Analog Drift/Priya Nair, Half Light/Sam Okafor,
Static Bloom/Jun Watanabe, Quiet Static/Ilse Berg), never "User 1" or "Host
Name." The interaction-merge demo's second presence, Micah, is a new name
for this build's own scenario — a prospective listener joining, not one of
the six hosts. Counts read as plain numerals with a lowercase unit ("214
listening," "312 rooms merged this week"), matching the product surface's
own convention exactly.

## 7. Motion

Hover/focus transitions on nav and buttons per `--duration-fast`/
`--ease-standard`. The goo interaction merge animates only on hover or the
`.merge-trigger` button's `data-active` toggle, `420ms` with
`--ease-spring-soft` (Playful consumer's own curve, kept per the
stance-commitment note) — nothing else on the page moves on its own. No
ambient loops anywhere; the static hero cluster and the supporting accent
are permanently still. `prefers-reduced-motion: reduce` removes the merge's
transition only — the `data-active`/`:hover` state still changes and the
blobs still land in their merged position, they just arrive instantly
instead of easing; the `role="status"` text swap is unaffected either way.

## 8. Hard don'ts

No second interaction color beside `--primary`. No goo on the nav, the CTA
buttons, any room card, the testimonial, or the footer — goo never becomes
a section-divider default or a card treatment. No more than one goo
signature surface (the hero identity is one moment in two parts, not two).
No glass, grain-print, or lighting anywhere in this build — declined per the
stance-commitment note, not merely unused; adding a "quiet supporting frost"
later would require re-opening every glass rule (both tiers,
`prefers-reduced-transparency`) this file deliberately avoided taking on.
No perpetual ambient filter animation. Never re-parametrize a goo filter's
`stdDeviation` or alpha-matrix `values` per frame — only the circles'
`transform` animates, under a static filter, exactly as `goo.md` prescribes.
No `filter: url(` on `body` or any full-viewport wrapper. No `filter: url(`
on any body-text container. State the merge communicates always exists as
`role="status"` text, never only as the visual fuse.
