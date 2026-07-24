# Goo (organic merge)

The expressive family. Read `filter-mechanics.md` first for the sRGB rule
and the filter-region rule — this file assumes both and tunes them for
metaballs specifically. Where `glass.md` is the home register (refined-tech,
neutral briefs default here), goo is unlocked only when a brief or stance
earns it: playful, organic, or creative work, and campaign/brand surfaces at
the Awwwards ceiling. `effects-policy.md` already stakes out the conservative
read of goo ("very rarely," "usually too loud... for product UI") — this
file is the deep chapter for the moments where it IS earned, not a
contradiction of that caution.

## The mechanism

Goo is three primitives: blur two or more shapes until their alpha fields
overlap, re-harden the alpha with a contrast matrix so only the merged
silhouette survives, then composite the crisp originals back on top so
interior detail (icons, text-free color) stays sharp.

```svg
<filter id="goo-mechanism" color-interpolation-filters="sRGB">
  <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
  <feColorMatrix in="blur" type="matrix"
    values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9" result="goo" />
  <feComposite in="SourceGraphic" in2="goo" operator="atop" />
</filter>
```

`color-interpolation-filters="sRGB"` is mandatory here for the same reason
filter-mechanics.md's sRGB rule states generally: the alpha matrix below is
authored assuming sRGB math, and WebKit's linearRGB divergence would shift
where the threshold actually falls.

**Tuning the alpha row** — the last row, `0 0 0 N K`, is the only part you
tune. It computes `a' = N·a + K` on every pixel's alpha:

- **N (contrast multiplier)** steepens the alpha ramp. Higher N = a harder,
  more sudden edge between "merged" and "not merged." N≈10 reads soft and
  jelly-like; N≈18–22 is a normal crisp goo edge; N≥30 turns razor-sharp and
  starts aliasing.
- **K (threshold shift)**, always negative, sets *where* on the blurred
  alpha ramp that edge falls. The cutoff alpha is approximately `|K| / N` —
  at `22, -9` that's ≈0.41, meaning pixels blurred to less than ~41% opacity
  get discarded and the rest snap to solid. Raise `|K|` (or lower N) to
  require more overlap before shapes bridge; lower `|K|` to make them bridge
  sooner and from further apart.
- **Reach** (how close two shapes must get before they visually merge)
  scales with `stdDeviation`: shapes bridge once their blurred fields
  overlap above the cutoff, roughly `2 · stdDeviation · (1 − |K|/N)` px of
  edge-to-edge gap. At `stdDeviation="10"`, `22, -9` that's ≈12px — the
  interaction recipe below is built around that number.

Swap `feComposite operator="atop"` for `feBlend in="SourceGraphic"
in2="goo"` only when you want the melted silhouette itself, with no crisp
interior detail — a rarer, more abstract look.

**Filter region.** Blur eats the default 10% bbox padding described in
filter-mechanics.md's filter-region rule — a `stdDeviation="10"` blur
reaches roughly `3 × stdDeviation ≈ 30px` past each shape's edge before it's
negligible, and 10% of a typical goo cluster's bbox is far less than that.
Both recipes below pin the region explicitly with `filterUnits="userSpaceOnUse"`
and concrete pixel values sized to give ≥30px of bleed on every side — copy
those values, don't rely on the default.

## Registers

Goo is unlocked for **playful, organic, or creative stances**, and on
**campaign/brand surfaces** it may reach the Awwwards-expressive ceiling
this skill names as its north star for the family. It stays locked out of
product UI's interactive layer regardless of stance: **goo never appears on
interactive controls or body text (locked decision 4)** — a button, link,
input, or paragraph never sits inside a goo filter's `<g>`. This is the same
boundary `effects-policy.md`'s "very rarely" verdict already drew for
product UI; that verdict is correct for controls, this file exists for
everything a control isn't — hero identity marks, loaders, delight moments,
campaign illustration.

## Dosage

Goo is a **delight-moment material**, not a structural treatment. Budget it
as one of: one merge animation, one loading motif, or one hero identity —
never more than one goo moment per surface unless goo itself is the
product's signature. It counts against the same 1-signature + ≤2-supporting
budget every other material in this skill answers to; it does not get its
own separate allowance.

## Motion

Goo animates on **interaction only** — hover, press, or a real state change
such as a completed step. **No perpetual ambient loops (locked decision
5):** nothing drifts, pulses, or breathes on its own the way it might in a
looping Codrops demo.

The mechanism that makes this cheap: the **filter itself never
re-parametrizes per frame.** `stdDeviation` and the alpha-matrix `values`
stay fixed for the filter's lifetime. What moves is the shapes underneath
it, animated with CSS `transform` (compositor-only, no layout, no repaint
of the filter graph) — the browser re-rasterizes the same static filter
chain against new shape positions every frame, which is orders of magnitude
cheaper than rebuilding a displacement map or re-running `feGaussianBlur` at
a different `stdDeviation`.

`prefers-reduced-motion: reduce` removes the transition, not the
interaction: the class/attribute toggle still fires and the shapes still
land in their merged positions, they just jump there instantly instead of
animating over the resting duration — the user sees the merged end state,
never a frozen mid-morph.

Because goo is a purely visual effect, **any state it communicates must also
exist as text or ARIA** (atlas §4.3) — a merge that means "step complete" is
not information until it also exists as a label a screen reader can read.

## Recipe: static organic cluster (hero identity)

A fixed, non-animated three-blob mark — a brand identity moment, not an
interaction. Complete and paste-ready:

```html
<svg viewBox="0 0 320 140" width="320" height="140"
     xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Brand mark: three merged organic forms">
  <defs>
    <filter id="goo-hero" color-interpolation-filters="sRGB"
            filterUnits="userSpaceOnUse" x="20" y="0" width="280" height="140">
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
      <feColorMatrix in="blur" type="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9" result="goo" />
      <feComposite in="SourceGraphic" in2="goo" operator="atop" />
    </filter>
  </defs>

  <g filter="url(#goo-hero)">
    <circle cx="96" cy="70" r="36" fill="#7E6BEA" />
    <circle cx="156" cy="70" r="36" fill="#FFB94D" />
    <circle cx="216" cy="70" r="36" fill="#82D7B2" />
  </g>
</svg>
```

The region — `x="20" y="0" width="280" height="140"`, `userSpaceOnUse` —
gives the r=36 circle cluster (bbox roughly x:60–252, y:34–106) at least 34px
of bleed on every side, comfortably past the ~30px the `stdDeviation="10"`
blur needs. `role="img"` + `aria-label` carry the identity meaning; nothing
here toggles state, so no further ARIA is needed.

## Recipe: interaction merge

Two blobs that bridge into one on hover or on a real `[data-active]` state
change (e.g. a two-step flow completing). The filter stays static; only the
circles' `transform` animates.

```html
<div class="goo-pair" data-active="false">
  <svg viewBox="-15 0 230 120" width="230" height="120"
       xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
      <filter id="goo-merge" color-interpolation-filters="sRGB"
              filterUnits="userSpaceOnUse" x="-15" y="0" width="230" height="120">
        <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
        <feColorMatrix in="blur" type="matrix"
          values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9" result="goo" />
        <feComposite in="SourceGraphic" in2="goo" operator="atop" />
      </filter>
    </defs>

    <g filter="url(#goo-merge)">
      <circle class="goo-blob goo-blob-a" cx="45" cy="60" r="30" fill="#7E6BEA" />
      <circle class="goo-blob goo-blob-b" cx="155" cy="60" r="30" fill="#FFB94D" />
    </g>
  </svg>

  <p class="goo-status" role="status">
    Step 1<span class="goo-status-merged"> and Step 2 merged — both complete</span>
  </p>
</div>
```

```css
.goo-blob {
  transform-box: fill-box;
  transform-origin: center;
  transition: transform 420ms cubic-bezier(0.22, 1, 0.36, 1);
}

/* resting gap: 50px edge-to-edge — well outside the ~12px reach of
   stdDeviation 10 with the 22/-9 alpha row, so the blobs read as separate */
.goo-pair:hover .goo-blob-a,
.goo-pair[data-active="true"] .goo-blob-a {
  transform: translateX(20px); /* closes gap to ~10px: inside reach, merges */
}
.goo-pair:hover .goo-blob-b,
.goo-pair[data-active="true"] .goo-blob-b {
  transform: translateX(-20px);
}

.goo-status-merged {
  display: none;
}
.goo-pair[data-active="true"] .goo-status-merged {
  display: inline;
}

@media (prefers-reduced-motion: reduce) {
  .goo-blob {
    transition: none;
  }
}
```

A separate real control (a button elsewhere in the flow, never the goo
group itself — locked decision 4) sets `data-active="true"` when step 2
actually completes; that same attribute drives both the visual merge and
the `role="status"` text swap, so the merge is never the only way the state
is communicated. The `:hover` rule is left in as a cheap decorative preview
of the motion — it carries no unique information, so it needs no ARIA
counterpart of its own.

## Bans

- **Goo never appears on interactive controls or body text.** No button,
  link, input, or paragraph sits inside a goo filter's `<g>` — locked
  decision 4, no exceptions by register.
- **No goo as a section-divider default.** A wavy/gooey divider between page
  sections is decoration wearing a material's clothes; it needs the same
  earned justification as any other goo moment, not a reflexive swap for a
  straight edge.
- **No perpetual ambient loops.** A goo motif that idles, pulses, or
  breathes without an interaction driving it violates locked decision 5.
- **Never re-parametrize the filter itself per animation frame.** Animate
  the shapes with CSS `transform` under a static filter; animating
  `stdDeviation` or the alpha-matrix `values` on every frame rebuilds the
  filter graph and defeats the entire cost model this file's Motion section
  relies on.
- **State shown by a goo merge must also exist as text or ARIA.** A merge
  that means something (steps complete, items combined, selection made)
  is not accessible information until it exists outside the filter too.
