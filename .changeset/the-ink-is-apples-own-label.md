---
"@vitreajs/vitrea-web": minor
---

The ink is Apple's own label colour now, through Apple's own vibrancy operator.

`--vitrea-foreground` was `#1c1c1e` and `#f5f5f7`, opaque, chosen to be legible.
It is now what Apple actually renders inside a `glassEffect`: **pure black at
α 0.847059** over a bright surface and **pure white at α 0.804706** over a dark
one, published as `rgb(0 0 0 / 0.847059)` and `rgb(255 255 255 / 0.804706)`. The
operator that produces them saturates the colour away — nothing of the input
colour survives it and only the alpha does — and its lightening pole scales that
alpha by 0.95, which is where 0.804706 comes from: 0.847059 × 0.95.

**The three named levels below it are macOS's ladder, not iOS's.** They were
iOS's flat 0.6 / 0.3 / 0.18. Through the operator they are now, and the two poles
are *not* symmetric:

| Level | Dark ink, over a bright surface | Light ink, over a dark surface |
| --- | --- | --- |
| secondary | 0.498039 | 0.521569 |
| tertiary | 0.258824 | 0.234706 |
| quaternary | 0.098039 | 0.093137 |

The right-hand column is macOS's dark-appearance ladder (0.549020, 0.247059,
0.098039) times the operator's 0.95. Apple publishes no component values for
these and says not to hard-code them, so the four alphas are documentation-
sourced and published as such: third-party measurements agreeing exactly, and
unchanged from macOS 11 through macOS 26.5.

**The secondary floor's rule is unchanged; its ceiling moved.** Secondary is
still raised to whatever holds WCAG 4.5 against the composite this surface is
actually drawing, and still collapses onto the primary where even the strongest
ink misses. What "the strongest ink" means is now the *primary's own* alpha —
0.847059 or 0.804706 — rather than opaque. The promise is the same sentence it
was: secondary is never worse than the primary, and holds 4.5 wherever the
primary can. In practice Apple's own secondary alpha survives unraised only over
dark surfaces below an encoded level of about 0.19; over a bright surface the
black ink at 0.498039 never reaches 4.5, so it is always raised there.

**What the translucent primary costs, stated rather than hidden.** The band of
surface levels over which *neither* ink pole carries body text is wider than it
was: an encoded [0.4425, 0.5145] before, [0.3935, 0.4900] now. A surface landing
in that band gets a primary that does not reach 4.5 and a secondary collapsed
onto it. Three ways out: hint the group's backdrop, so the ink is decided against
the level the surface really has; pick a thicker or a less clear variant; or
author the colour yourself — an application rule that names the host still wins.

**`foreground` takes two new string values.** Alongside the adaptation object
(`{ mode: "fixed" | "author-hint" | "sampled-async" }`), which is the cadence,
`"vibrant"` and `"token"` say who owns the label. `"vibrant"` changes no colour —
the published token already is the operator's output — but raises the runtime's
`color` declaration from `:where([data-vitrea-node])` (0,0,0) to
`[data-vitrea-vibrant]` (0,1,0), so it survives a reset sheet's
`button { color: … }`. `GlassButton`, `GlassIconButton` and
`GlassSegmentedControl` default to `"vibrant"`; a bare `GlassSurface asChild`
does not, and `"token"` opts a control back out. On both paths an application
rule that *names* the element still wins, which is Apple's behaviour: it installs
the operator on the automatic colour and leaves an authored one alone. One
limitation: the two axes share one prop, so a surface cannot ask for
`sampled-async` and `"vibrant"` at once.

**The ink crossfades instead of snapping.** When a surface's own level crosses
the point where the two poles trade places, the published ink transits over
180 ms through a 0.08-wide dead band, so a drifting backdrop cannot pump the text
colour. Mid-transit the value is a premultiplied mix of the two poles — exactly
what `color-mix(in srgb, …)` produces.
