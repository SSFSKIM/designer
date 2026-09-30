# U5 — the CSS tier's body-law filter: its algebra, its clamping analysis, and where it is exact (2026-10-01)

Beside `implementation-design.md` §5, as revised by §11's R5. The code is
`packages/platform-web/src/optics.ts` (`cssTierBodyLaw`, the derivation), `css-tier.ts`
(`cssTierBodyLawFilter`, the primitives; `cssTierBodyLawStacked`, the stacked route) and
`css-tier-layers.ts` (the DOM). The proof is `packages/calibration/test/w42-css-filter-algebra.test.ts`,
which runs the program through an emulator of SVG's primitive semantics
(`w42-svg-filter-emulator.ts`) against the renderer's CPU references (`bodyLawComposite`,
`bodyToneTableCodesAt`, `bodyLawE3Codes`, `landedToneLinear`). Nothing here is a browser reading;
every engine-side question is still charter Decision Log 4's, and the engine row
`bodyLawFilterInBackdrop` is `"unverified"` on every row, so no page draws this.

Notation: C, W the narrow and wide blurs (opaque after §1), h the hinge (+1 lighten, −1 darken),
λ ∈ [−0.5, 1.6], w ∈ [0, 1], b = (1 − w)·λ, P = (1 − w)·C + w·W, D₊ = max(0, W − C),
D₋ = max(0, C − W), per channel. L is Rec. 709 luma in the knee's space.

## 1. The three constraints that shape every primitive

1. **`feComposite` arithmetic is premultiplied, alpha included, and clamps each channel.** Its
   alpha is k1·a1·a2 + k2·a1 + k3·a2 + k4. On opaque inputs that is k1 + k2 + k3 + k4, so every
   arithmetic in the program keeps that sum at or above 1 (exactly 1 for a convex pair, whose two
   coefficients are rounded to sum to 1). A signed difference x − y is therefore never one
   arithmetic — its alpha would be 0 — and is taken as the positive part
   max(0, x − y) = x + (1 − y) − 1 on the complement 1 − y, whose clamp at 0 IS the hinge.
2. **Every input is made opaque first (R5).** Each blur is followed by an `feComponentTransfer`
   setting alpha to 1 on un-premultiplied values. Where `edgeMode="none"` left the blur's alpha at
   its kernel weight (the receded normalised edge), that divides the colour by the weight —
   `forward.py`'s num/den; where `duplicate` left alpha at 1 it is the identity. `feBlend` is not
   used: on opaque inputs lighten is max, which the positive part already is, and on partial
   alpha it composites source-over (R5's point).
3. **A clamp inside the chain clips the law.** So each weighted sum is ordered so the only clamp
   is the last: a positive term is added to a value in [0, 1]; a negative one is added to the
   value's complement and complemented back (exact: 255 − x at eight bits); and the terms of one
   sum are positive parts of one difference with opposite signs, so at most one is non-zero per
   channel and no intermediate carries a partial sum that a later term would bring back.

## 2. The composite, per knee form (`kneeForms`), with its clamping analysis

The CPU reference is `bodyLawComposite`; M is its argument. "Exact" below means the filter's
argument equals clamp(M) channel by channel to float precision, for every λ in [−0.5, 1.6], every
w in [0, 1], both hinges and both averaging spaces (D2 = 1 runs every knee primitive in sRGB,
D2 = 0 in linearRGB, as the renderer's rejected F2 does). The test reads it on 5,000+ samples per
case, including the cube's corners, greys and near-isoluminant pairs: worst 1e-9.

| knee | program | where the true M leaves [0, 1] | verdict |
| --- | --- | --- | --- |
| 0, per channel (the carried form) | M = P + h·b·D_h (D_h = D₊ light, D₋ dark): h·b ≥ 0 adds to P; h·b < 0 adds \|b\|·D_h to 1 − P and complements. 8 primitives to M (10 when h·b < 0) | light, W > C: M = C + β(W − C) with β = (1 − w)λ + w, so M ∈ [C, W] iff β ∈ [0, 1] iff λ ∈ [−w/(1 − w), 1]. **Never for λ ∈ [0, 1]** (asserted); λ > 1 overshoots above W (to 1.3 at C = 0, W = 1, λ = 1.6, w = 0.5); λ < 0 undershoots below 0 only if λ < −w/(1 − w), which at w = 0.5 is −1, outside the range, and inside it only for w < 1/3. W ≤ C gives the convex P. Dark mirrors. | **exact up to the final clamp**; exact outright for λ ∈ [0, 1] |
| 1, on luma, whole colour | on = STEP(max(0, h·(L(W) − L(C)))) with a one-code step (`linear` slope 255); M = P + b·on·D₊ − b·on·D₋, the gated parts by k1 products. 19 primitives to M | as knee 0 with the whole colour: M = C + β(W − C) where on, so in range iff β ∈ [0, 1], again never for λ ∈ [0, 1] | **exact up to the final clamp, off R1's flip set**: where 0 < h·ΔL < 1/255 the step is a ramp (float) or the eight-bit lumas decide (engine). The decision is discontinuous by declaration (R1); no deadband is added |
| 2, on luma with W's chroma | Δ± = max(0, ±(L(W) − L(C))) on luma greys; M = W + p·Δ₊ + q·Δ₋ with (p, q) = (1 − w)·(λ − 1, 1) light and (1 − w)·(−1, 1 − λ) dark. 14 primitives to M | an achromatic shift of W: a saturated W leaves [0, 1] in a channel for **any** λ, including the dump's 0.9 | **exact up to the final clamp** |

Where M leaves [0, 1], the filter carries clamp(M) and the renderer's tones read the unclamped
M (T2's and E3's level and chroma; the landed tone's silhouette abscissa — the landed tone clamps
each channel itself, so there only the abscissa differs). That difference is the one irreducible
approximation of the composite on this tier, and it lives only where λ > 1, where λ < −w/(1 − w),
or under knee 2 on saturated colours.

## 3. T for T2 and E3: exact in form

T is `y = clamp(F(L(A)) + G(ℓ)·(A − L(A)))` per channel, the renderer's clipping order (F
clipped, chroma added, channels clipped). The program: L(A) and 1 − L(A) by `feColorMatrix`; F
by a 256-entry table per channel on L(A); Ĝ = G/G_max by a table on ℓ (L(A) for T2; **L(W) for
E3 under the law**, Fork 5); the chroma's two positive parts χ₊ = max(0, A − L), χ₋ = max(0, L −
A); the products Ĝ·χ± by k1; y = F + G_max·Ĝχ₊ − G_max·Ĝχ₋ by the §1 ordering, with
G_max = max(1, max G) so the products' alpha stays 1. χ₊ and χ₋ are complementary per channel, so
no partial sum is clipped early. §5's "two arithmetic composites with a 0.5 offset" is exact only
for a gain constant in the level; E3's and T2's gains move with the level, so the split replaces
the offset.

- F and g have their knots at integer codes (E3 at 40…150 and the extension's 160…255; g at 63,
  93, 118; T2's family-A levels), so the tables' linear interpolation between codes reproduces
  them. A document whose T2 levels are not integer codes would carry an interpolation error of at
  most the slope change at that knot times half a code.
- The span is one number per surface on this tier, so candidate 2's interpolation between rows
  (`native-t-addendum.md`) is folded into the table once, exactly.
- A fractional T2 strength mixes over the tone below it in linear light (§2.7), one convex
  arithmetic in `linearRGB`. **A fractional E3 strength under the law is mixed over the landed
  solve the same way — an assumption this unit made, which U4 must share.**
- Held: 600 samples per tone, including span 112 between rows and span 40 below the first, under
  5e-3 code — the table's written millionth times the gain. End to end (blurs to T2's codes) the
  same, wherever M is in range.

## 4. The landed solve (candidate 1): an approximation, and a better route found

Built as §5 proposed: F per channel is the solve on the grey at each encoded level, and G is the
least-squares chroma gain of the solve's encoded response along the three luma-preserving chroma
directions, by central differences of four codes. Exact on the greys AT THE TABLE'S KNOTS (1e-3
code; see "Between the knots" below for what it is not). On the 6³ grid
of encoded colours at span 96, dpr 2, worst code error (and worst over the grid's colours with
encoded chroma spread ≤ 0.2):

| endpoint | abscissa | worst | chroma ≤ 0.2 |
| --- | --- | --- | --- |
| macOS 27 active light | source | 86.07 at (0.8, 1, 0) | 17.66 |
| macOS 27 active dark | source | 47.00 at (0, 0, 0.4) | 44.58 |
| macOS 27 receded light (landed at E3 = 0) | silhouette | 70.70 at (0.6, 0, 1) | 21.61 |
| macOS 27 receded dark | silhouette | 27.77 at (1, 1, 0) | 4.62 |

The test pins each within 1.5 codes below and 1 above, so a tone that moves re-opens this record.
Two reasons it is this large, both structural: the renderer's source abscissa is the LINEAR
luminance of dec(A), which on a saturated colour is far from the encoded luma the tables are
indexed by (pure blue: 0.072 encoded against 0.30); and W31's retention restores chromaticity,
a ratio, and its gamut map is per-pixel nonlinear.

**The better route, measured and not built.** For the source abscissa, every quantity of the
solve is a function of ℓ = L_lin(dec A) alone, and the composite is linear in c = dec(A), so the
landed tone is exactly `T_lin(c) = P(ℓ)·c + Q(ℓ)` — an affine in linear light with coefficients
over the linear luminance — everywhere the retention's gamut map does not act (retention keeps
the luma exactly, so its renormalisation is the identity). A probe of that form on the same grid
(not committed; it re-derives in a few lines from `landedToneLinear`) reads **0.000 code wherever
the retention stays in gamut** on both active endpoints; active dark never leaves it, and active
light's worst, 28.4 codes, is entirely on the 123 of its 214 chromatic grid colours where the
retention's toward-colour leaves the gamut and the map scales its chroma. A filter
can carry it: ℓ by an `feColorMatrix` in linearRGB, P and Q as tables read in the encoded space
for resolution in the darks, P·c + Q by two arithmetics in linearRGB. Its one hazard is that
P = a + r·L(b)/ℓ diverges as ℓ → 0 under retention, so its table needs a cap or a split of the
toward-term, and the eight-bit chain may not hold it. The silhouette abscissa (the receded
documents) reads two scalars, L_enc(A) for the solve and L_lin for the composite, and has no
one-dimensional exact form. Recommended as the landed route Decision Log 4 measures beside this
one; not built here because it changes the design's §5 route.

**Between the knots, near black: a Decision Log 4 approximation** (the U3/U4 review's fix wave,
item 2). Every tone table has one entry per code, and `feComponentTransfer` reads the chord between
two entries. A blurred argument lands between codes. Wherever the response is smooth the chord is
close. Above 4 codes it is within 0.065 code at worst on all four endpoints (quarter, half and
three-quarter codes, span 96, dpr 2).

Across W36's black join it is not. The join rejoins the old solve before encoded 0.003 (0.77
code), and the landed solve per pixel is sharply non-monotone inside the first code:
- active light rises from 132.0 at code 0 to 177.0 at code 0.60 and falls back to 135.2 at code 1;
- receded dark rises from 20.0 to 215.9 at code 0.60, falls to 12.4 at code 1 and to 0.2 at code
  1.05.

The chord from code 0 to code 1 misses the peak, by these amounts:

| endpoint | worst miss below 4 codes |
| --- | --- |
| active light | 43.20 codes |
| active dark | 16.03 codes |
| receded light, landed at E3 = 0 | 53.08 codes |
| receded dark | 200.61 codes |

Every worst is between code 0 and code 1. The 43.2 is the review's reading at encoded 0.59/255.
`test/w42-css-filter-algebra.test.ts` pins each one code above its reading, and bounds the region
above 4 codes at 0.1.

A refinement would take a second transfer stage per tone table: one to stretch the first codes,
one to read a denser table in the stretched variable. That is only meaningful where the engine's
intermediates carry sub-code levels, and an eight-bit chain (§6) quantises the argument to the
knots, where the table is exact. It is not built. What an engine does between the knots is
Decision Log 4's reading.

The spike itself is not the filter's. It is the declared candidate 1's landed solve on a uniform
backdrop between codes 0 and 1, which the rehearsal's `landed_T` reproduces (U1's landed fixture
pins it to 1e-12 at encoded 0.0005 to 0.003). The WebGPU tier draws it at f32 too
(`implementation-design.md` §14).

## 5. What the CSS route does not carry (named gaps; each is Decision Log 4's or U6's)

- **Support.** A `backdrop-filter` reads the element's box, so the law's footprint is the box, not
  R_fp: the active margin (0.35 s, 16 pt minimum) is not carried and the receded one device px is
  lost. The filter region is set to the box so that `edgeMode` states the law's edge there; the
  outset-and-mask that would carry R_fp is not built. Whether `edgeMode` is honoured inside
  `backdrop-filter` at all is unmeasured.
- **The graded narrow width.** One `feGaussianBlur` has one width. The active pose blurs at the
  band-weighted mean of σn over the body (smoothstep(0, 20 pt, depth) over the circular-corner
  field); the least and greatest are reported beside it (`narrowSigmaGradedCssPx`). On a 200 × 96
  surface at dpr 2 in points: 2.04 CSS px, between 1.33 and 4.82.
- **The active band.** The WebGPU tier eases the law in over the outer 20 pt from the shipped body
  (Decision Log 5e, R4). A `backdrop-filter` stack has no layer that reads both bodies from the
  page, so the CSS law runs to the contour.
- **A fractional `bodyLawStrength`** draws at full weight, for the same reason; documents carry 0
  or 1.
- **Presence** rides L1's `opacity`, a mix toward the raw backdrop in the page's space: exact at 0
  and 1, as the shipped tier's table is. The filter is the resting material's.
- **The cost collapse** stands the law down: the collapse is a degradation to a known body, and
  the law's chain (21 to 43 primitives; §2's counts plus T's) costs more than the one it replaces,
  unmeasured until G3's bench.
- **The host's tokens, the ink and the author tint's shade** are still read off the shipped
  material, not the law's body. L3 keeps the author's own layer at its own strength over no plate
  (T contains the plate), so the contrast floor W17 Decision Log 4 (a) keeps is absent under the
  law — which only draws on an engine measured to render it.
- **The landed tone's inputs**: the neutral is the profile's tint (the renderer mixes toward the
  observed adaptive tint; the macOS 27 poles equal their tints, so every shipped endpoint agrees),
  and the solve is at presence 1.
- **The stacked route with D2 = 0**: `blur()` averages in the encoded space only.

## 6. Eight bits, as one model of an engine's intermediates

Rounding every stored channel to 1/255 (and the two blurs' inputs), 400 random pairs, knee 0,
λ 0.9: worst **2.91 codes** (T2), **3.06** (E3), **3.81** (landed, active light) from the float
chain. A model, not a measurement: whether an engine stores these intermediates in eight bits,
in which space, and how its `feComponentTransfer` tables are sampled is Decision Log 4's reading.
The test bounds the model at 5 codes.

## 7. The stacked approximation (engines with no reference filter)

Four `backdrop-filter` layers, each over the one below (`cssTierBodyLawStacked`):

1. `blur(σn)` → C, encoded averaging: D2 = 1 exactly, D2 = 0 not at all.
2. `blur(√(σw² − σn²))` at `mix-blend-mode: lighten` (dark `darken`), opacity λ →
   (1 − λ)·C + λ·max(C, W) = N: **exact for knee 0 with λ ∈ [0, 1]** (asserted); `opacity`
   clamps λ outside it; knees 1 and 2 are not per-channel blends. Where σn > σw the step is 0.
3. `blur(√(σw² − σn²))` at opacity w → (1 − w)·N + w·G*N = M + **w·h·λ·G*D_h** exactly (asserted
   on a 1-D signal): the Normal fill cannot read W again, and over-fills by the blurred hinge term.
4. W41's affine for T at the surface's encoded level L̄ (`78c4b854`, re-derived on the law's tone
   with no plate): slope G(L̄), intercept F̄(L̄) − G(L̄)·L̄, written `contrast(c) brightness(b)`
   for an intercept ≥ 0 and `brightness(b) contrast(c)` below it, each with no premature clamp
   (asserted). Exact at colours whose luma is L̄; elsewhere its luma slope is G where T's is F′. A
   fractional tone mixes the two affines in the encoded space.

It is derived and not attached: the tier creates three layers, this needs four and a measured
`mix-blend-mode` on a filtered layer, and no engine row enables it. Whether it is carried at all
is Decision Log 4's.

## 8. Tests

- `packages/calibration/test/w42-css-filter-algebra.test.ts` (27): §2's exactness for every knee,
  hinge and space over the λ and w grids, with R1's flip set counted and excluded for knee 1;
  the normalised edge from partial-alpha blurs; §3's tones, end to end and mixed; §4's landed
  bounds; §6's model; §7's three algebraic claims.
- `packages/calibration/test/tier-coherence.test.ts`: every W42 leaf and E3's three have a
  `CSS_COUNTERPART` line citing `CSS_BODY_LAW_IDENTITY`, compared by value; six new cases pin the
  declared constants, t, o, the texel, the unit, the fold under every policy and variant, the
  patch refusals, E3's and T2's decomposition into curve and gain, and the landed solve to
  `landedToneLinear` on the four macOS 27 endpoints and the default (to 1e-12).
- `packages/platform-web/test/w42-css-body-law.test.ts` (14, jsdom): identity documents and
  engines draw byte-identical declarations; the law stays off unless the row says `"yes"` with a
  reference filter; the conformance table says `"unverified"` everywhere with evidence; L1/L2/L3
  under the law; the fold's stand-downs; the derivation's widths in all three units, the graded
  mean against an independent integral, the tone precedence; the filter's DOM attribute for
  attribute, the opaque-alpha invariant, sharing and sweeping; the stacked layers.
- `packages/platform-web/test/w30-css-declaration-identity.test.ts`: untouched and green.
