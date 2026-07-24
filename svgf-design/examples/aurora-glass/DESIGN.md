# Aurora — Design Law

## 0. Stance commitment

**Precision industrial**, read as an engineered-audio-instrument register: exact,
sober, low-noise chrome (cool near-white workspace, steel-tinted panels,
almost no shadow) wrapped around one dark, content-rich stage — the room
itself. Aurora is not a mood board for "spatial audio"; it is a control
surface for it, closer to how a Sonos or Teenage Engineering interface reads
than to a music-streaming marketing page. The chrome stays quiet on purpose
so the room's live visual field is the only thing allowed to be loud.
**If a decision is ever ambiguous, choose the more restrained, more legible
option.**

**Rejected ingredients.** The sampler drew `warm`, `swiss`, `vernacular` for
stance (seed `4471`); `swiss` was chosen because it is the only one of the
three whose `materials-map.md` default family is `glass`, which the brief's
"immersive visual field" + "control playback" shape calls for directly.
`swiss` maps to the **Precision industrial** system "as-is" per
`stances.md`'s mapping table, so its own token block is ported unmodified —
the sampler's secondary picks (Blackletter/Didone typography traditions,
textured-paper/cream canvas) are declined outright: they belong to stances
mapped to "derive fresh," not to a stance whose values are ported intact
verbatim.

## Material law

- **Family.** `glass`. Register classifier: a person operates this surface
  to browse rooms, join one, and control playback — **product UI**, ceiling
  **Apple-neat**. Goo is banned outright, no exception.
- **The one signature surface.** The bottom-docked transport toolbar —
  play/pause, prev/next, scrub, spatial toggle, volume — carries the full
  engineered-glass chain (`feImage` → `feDisplacementMap` → `feGaussianBlur`
  → `feColorMatrix`, generated, never hand-written) over the room's live
  waveform field.
- **Dosage.** 1 signature + 1 supporting (headroom for one more unused). The
  supporting moment is the "Output" device chip floating over the hero —
  **frost tier only**, no `feDisplacementMap` chain, smaller, no interactive
  role beyond a single toggle. Nothing else in the build touches glass:
  rail rows, queue rows, listener chips, and browse cards are all plain
  Precision-industrial surfaces.
- **Ground plan.** `grounds.md`'s **Simulated product content** — the ground
  *is* the product: a generated stereo waveform field (muted ambient-bed
  layer + saturated active-track layer, ~200 bars at 8px pitch, envelope-
  shaped so the foreground reads as one real musical passage) plus three
  radial hue washes (indigo `#2f2b6b`, violet `#7a3fe0`, teal `#1fb8b0`) —
  clears the ≥3-hue-stop and structural-geometry bars both. The transport
  toolbar is fixed-position and persists under scroll (a standard docked-
  player convention, same as Spotify's or Apple Music's bottom bar); its
  *designed* ground is this hero field, and every section beneath it (queue
  rows, listener chips, browse cards) is real structured content, never a
  blank plane, so the toolbar never transiently rests over nothing.
- **Fallback-tier plan.** `@supports not (backdrop-filter: blur(1px))`:
  solid near-black fill, no transparency. Frost tier (`@supports
  (backdrop-filter: blur(1px))`): `blur(14px) saturate(160%)`. Both fallback
  tiers share the toolbar's exact geometry, radius, and specular rim with
  the refraction tier — a browser without Chromium's `backdrop-filter:
  url()` sees a lesser-supported version of the same design, not a
  downgrade.
- **Register ceiling.** Apple-neat. No showy/expressive refraction: one
  moderate `strength` value (55 desktop / 50 narrow), a plain CSS inset
  `box-shadow` specular rim (no `feSpecularLighting`), no ambient motion.

**Build note — two breakpoints, two generated maps.** The toolbar is sized
in px and regenerated per breakpoint per `SKILL.md`'s sizing law, rather
than stretched with CSS:

```
node svgf-design/scripts/make-glass-map.mjs --width 840 --height 96 --bezel 22 --strength 55 --shape pill
node svgf-design/scripts/make-glass-map.mjs --width 560 --height 84 --bezel 18 --strength 50 --shape pill
```

Both snippets are pasted with their values untouched. The narrow instance's
CSS **class names** only (`.svgf-glass*` → `.svgf-glass-narrow*`) are
namespaced so the two coexist in one page without one's sizing rule
clobbering the other's — filter `id`s stay exactly `svgf-glass-840-96` and
`svgf-glass-560-84` as generated, and every geometry/strength/blur value is
untouched.

## 1. Palette, with usage rules

`--accent` (`#D46B2C`) does exactly two jobs: the primary action (Join,
focus rings) and the "joined" state marker in the rail. It never decorates
an icon, a divider, or a card. Status colors (`--success/--warning/--danger/
--info`) are reserved for literal state, never decoration. **Named
exception:** the room hero's waveform gradients and track-art swatch
(`--room-indigo/--room-violet/--room-teal/--room-bg-*`) are generated art
for that room's mood, not chrome — they never appear outside the hero
panel and the toolbar's own tint/specular layers.

## 2. Typography, with placement rules

Three roles, held everywhere: `--font-display` (room name, track title,
section headings — Precision-industrial's Archivo weight/scale ported,
substituted with a system sans stack since the build ships with zero
webfonts), `--font-ui` (nav, body, buttons, copy), `--font-mono` (timestamps,
durations, listener counts, queue index numbers — tabular data only, never
prose). No blackletter, no Didone — declined per the stance-commitment note
above.

## 3. Canvas & texture

App chrome (rail, headers, queue, listeners, browse) sits on
`--background` (`#F4F6F7`), cool and near-white, zero grain. The room stage
is the one deliberate dark inset — not a second app-wide canvas, a
content-scoped exception named directly in the Material law's ground plan.
No grain/noise/paper texture anywhere; the dosage budget went entirely to
glass.

## 4. Layout system

Two-column shell ≥861px: 280px fixed rail + fluid stage. Hairlines
(`--border`, 1px) separate rail rows and queue rows; the browse grid is the
only card surface in the build (`--card`, 1px `--border`, no shadow at
rest, `--shadow-float` only on hover). Spacing holds the `--space-*` scale
throughout. **Responsive collapse, ≤860px:** the rail becomes a horizontal
top bar (logo + nav tabs only, live-room list dropped — still reachable via
the "More rooms to explore" grid), the stage goes single-column full width,
and the toolbar swaps to the narrower generated glass map with track-meta
text and the volume control dropped to icon-only controls.

## 5. Component canon

Rail room row (list item, accent left-bar + tint for the joined state) ·
queue row (index/title-artist/duration, mono duration) · avatar chip
(initial-letter circle, muted background) · browse room card (card surface,
Join = primary button) · primary/secondary/ghost buttons (Precision-
industrial component spec, `--radius-2`) · transport toolbar (glass,
canonical, exactly one instance rendered at a time) · output chip
(frost-only glass, canonical, exactly one instance).

## 6. Voice

Short, concrete, no exclamation points. Real proper nouns throughout — room
names, host names, track titles — never "User 1" or "Song Title." Counts
read as plain numerals with a lowercase unit ("214 listening," not "214
Listeners!").

## 7. Motion

Hover/focus transitions only, `--duration-fast`/`--duration-standard` per
Precision-industrial's own timing. The toolbar's refraction motion is free
via scrolling content beneath it — nothing is animated on top of that
baseline. No ambient loops anywhere. `prefers-reduced-motion` freezes every
transition and any `strength`-attribute change instantly; state still
changes, it just stops easing.

## 8. Hard don'ts

No second accent color. No glass on the rail, queue rows, listener chips,
or browse cards — glass never becomes a card default. No goo anywhere. No
grain/paper texture layered on top of glass. No more than one full-
refraction signature surface. No `filter`/`backdrop-filter` on `body` or on
the `.app`/`.transport-dock` wrappers — only on the toolbar and the output
chip themselves. No `filter: url` on any body-text container. No ambient
filter animation. No `@supports (backdrop-filter: url(` gate anywhere —
the refraction layer is capability-gated by the no-op overlay, never
feature-detected.
