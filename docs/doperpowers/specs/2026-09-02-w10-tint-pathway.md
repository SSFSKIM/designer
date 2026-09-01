# W10 — The tint pathway

**Opened 2026-09-02.** Child of the post-v1 wave
(`docs/doperpowers/specs/2026-08-28-post-v1-wave.md`), chartered by W9's
Deferred entry "The tint pathway" (`2026-09-02-w9-backdrop-tone-sampling.md`,
Decision Log 4: "the next opener is picked from Deferred on its own decision
round" — picked by the user 2026-09-02 as the largest remaining floor class).
Grounded in claims §5.36 (the tint law, measured before this spec was
written), §5.27 (the six floors this spec exists to remove), §5.13 (the
gamut-clip account, now measured to be aimed at the wrong tier), §5.10 (the
tint's capture history) and the wave's Decision Log 12 (W3's composition
contract, which this round overturns in one clause with evidence).

## Purpose

Six enforced rows on the two light-standard profiles are regression floors
instead of met claims — the cross-tier interior level ratio on tinted
capsules over `checkerboard` (orange, calibration; blue, validation) and
`hc-text` (orange, holdout), 1.27–1.64 against a gated band of 0.80…1.25 —
and W9 measured them identical to four decimals through every change to the
tone axis. They are the tint pathway's own. §5.36 read the reference per
pixel and found the mechanism: Apple's tinted material is an **opaque,
hue-preserving shade of the seed** whose brightness is linear in the
untinted material's own local luminance, composited over the material at
the author's opacity in encoded space. vitrea's tint on both tiers is a
translucent wash of the seed at the material's alpha. W10 replaces the
wash with the measured law on both tiers and discharges the floors by fix.

## What counts as done (binding)

- The six `interiorLevelRatioGpuOverCss` floors in §5.27 **removed rather
  than re-pinned**, each with the 0.80…1.25 band restored as a met claim.
- Every other tinted row on every profile stays inside its adopted bound
  after the change (the tinted cells gate under the general tables, §5.13;
  no tint-specific table is introduced now either).
- Both tiers. The GPU tier is the tier that misses (§5.36); the CSS tier is
  near the reference by accident and must land there by construction.
- The W3 tone-map constants (`tintTone{Floor,CeilMix,Low,High}`), fitted to
  identity in §5.13 because a wash has no tone to fit, are **replaced**, not
  kept beside the new law — one mechanism for the tint's tone, on both tiers,
  in one profile document.
- **Out of scope**: the dark scheme's tint surface (the dark profiles gate
  the shade off, §5.36 finding 4 — its own charter in Deferred); the WebGL2
  tier; the mid-collapse regime's tinted behaviour (declared as the linear
  fold, unmeasured).

## Grounding (read from the code at open, 2026-09-02)

1. **GPU tier** — `packages/renderer-webgpu/src/wgsl/optics.ts`: after the
   W9 solve and the W7 collapse produce `adapted` (colour) and
   `adaptedAlpha`, the author tint runs `tintColour = mix(adapted, tone,
   strength)` where `tone` is the seed through the identity tone map, and
   the body composites as `mix(backdrop, tintColour, adaptedAlpha)`. The
   comment above it states the contract this round overturns: "The tint
   layer's ALPHA is untouched by the author's colour." The uniform `tone`
   (vec4: floor, ceilMix, low, high) and `seed.w` (the regime grip) carry
   the tone map; `aux.w` is the per-pixel strength unioned in the field
   pass.
2. **CSS tier** — `packages/platform-web/src/optics.ts`: `tintedSourceOptics`
   displaces the source's tint colour by the seed (through the mirrored
   `tintTone`), and `cssOpticsFromSource` then solves ONE `rgba()` layer's
   alpha on luminance (`cssTintAlpha`) and its colour per channel
   (`cssTintColor`, clamping at the gamut). `root.ts` calls
   `tintedSourceOptics` at two sites: the CSS node's base optics and the
   GPU tier's foreground decision (the ink is chosen against the tinted
   level).
3. **The strength axis** is already the right shape on both tiers: the
   author's colour alpha is the strength, per pixel on the GPU tier
   (`aux.w`) and per source on the CSS tier, and the half-strength cell
   measures as an encoded-space layer opacity (§5.36 finding 3), which is
   what a CSS `rgba()` overlay does natively and what the GPU shader can
   do with the `srgb_encode` helper W9 added plus its inverse.
4. **The measurement is already in hand.** §5.36 was read from the frozen
   bed and the W9 probe fixtures; no native capture is needed this round.
   The fit is native-against-native (the shade law relates the reference's
   tinted pixel to the reference's untinted pixel), so vitrea never enters
   it and the whole canonical bed is the referee.

## Inherited constraints (binding)

- **X1, the fresh-split rule.** The six floored rows are spent holdout and
  are never fitted against. The two shade constants are fitted on the five
  probe tinted cells alone; every canonical tinted row is the referee, read
  once from a from-scratch matrix rebuild. Protocol declared in §5.36.
- **Provenance:** `resolvedMaterialSha256` on every capture; the profile
  documents re-record their fingerprints with the change.
- **The wave's composition order** (colour scheme → backdrop adaptation →
  author tint) stands. What changes is what the tint step *is*: not a colour
  displacement at the material's alpha, but an opaque layer at the author's
  opacity whose colour is a shade of the seed read off the adapted material.

## The law (from §5.36; binding as the implementation target)

```
u        = luminance of the untinted, adapted material at this pixel (linear)
shade    = mix(tintShadeDark, tintShadeLight, u) · strength + (1 − strength)
           where strength = tintShadeStrength · (1 − k)      (k: W7 collapse)
layer    = seed · shade                                       (linear, hue intact)
tinted   = decode( mix( encode(material), encode(layer), s ) )  (s: author strength)
```

- `tintShadeDark ≈ 0.53`, `tintShadeLight ≈ 1.0` — the "range of tones":
  the shade at black content and at white content. Fitted this round.
- `tintShadeStrength` is 1 on the light profiles and 0 on the dark
  profiles (§5.36 finding 4). Where it is 0 the layer is the pure seed.
- The accessibility regimes need no constant of their own: their folds
  enter through `u` (the increased-contrast material is at u ≈ 0.98 and
  shades to 0.99, as measured).
- The CSS tier reads `u` per source (its documented granularity): the shade
  is flat across the surface where the GPU tier's tracks the checker. The
  mean lands; the structure cost is the tier's known one.
- The CSS tier stays ONE `rgba()` layer: the author layer over the material
  layer folds exactly in encoded space —
  `α′ = 1 − (1 − s)(1 − α)`, `C′ = ((1 − s)·α·E(N) + s·E(layer)) / α′`.
  Convex, so it never leaves the gamut; §5.13's clip vanishes structurally.

## Phase plan

1. **Charter + decision round 1** — this document, §5.36, and the user's
   ruling on the contract overturn and the protocol.
2. **Implement** on both tiers with the constants at their §5.36 pooled
   values, replacing the tone map; tests re-pinned to the law; profile
   documents carry the new keys; the capture allowlist admits them.
3. **Fit** the two constants on the probe cells under the declared
   objective; land them; record the fit in §5.36.
4. **Referee** — the canonical rebuild (twelve per-profile runs, both
   tiers), the six floors and every tinted row read once, the regression
   scan over the whole bed. Then the enforcement test, §5.27, this spec's
   close, the wave's tracking row and its `[parent-impact]` on Decision
   Log 12.

## Decision Log

1. *(open — see the round's question)* **The contract overturn and the
   protocol.** (a) Wave Decision Log 12's clause "the tint occupies the
   colour axis only, its strength carried by the colour's own alpha" is
   overturned in its first half by §5.36: a full-strength author tint is an
   opaque layer, and the material's alpha is not what the tinted surface
   shows. The strength-as-alpha half stands and is measured to be an
   encoded-space layer opacity. This is a `[parent-impact]` on the wave
   spec, recorded there at close. (b) The fit protocol as declared in
   §5.36.

## Deferred

- **The dark tint surface.** The dark scheme renders the pure seed over
  checkerboard and photo (§5.36 finding 4). Whether that is "no shading in
  the dark scheme" or "shade relative to the material's own body level"
  needs a dark-scheme tinted cell over a light backdrop. Until then the
  dark profiles gate the shade off.
- **The mid-collapse regime.** No tinted cell sits on W7's slope
  (mid-dark-solid); the `(1 − k)` fold is declared, not measured.
- **The second hue's residual.** Blue fits with c₀ ≈ 0.03 above orange
  (§5.36). If the blue validation/holdout cells miss their ΔE bounds under
  the orange-fitted constants, a hue term is a declared round; the referee
  decides.

## Revision Notes

*(none yet)*
