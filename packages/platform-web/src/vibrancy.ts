/**
 * Apple's automatic label operator, as a function (W27e G2; claims §5.140).
 *
 * "The label automatically becomes vibrant, based on its textColor" is the
 * mechanism by which anything on Apple's glass stays legible, and until this
 * module vitrea's answer was a threshold between two hexes. What Apple actually
 * installs, read out of the committed layer dumps rather than off a pixel, is a
 * `vibrantColorMatrix` on the label's own `CGDrawingLayer` inside the
 * `glassEffect` — one matrix per pole, twenty float32 coefficients, zero
 * residual on 26 of 26 labelled dumps (claims §5.136 §4, §5.137).
 *
 * ## The semantics, in one line
 *
 * Both matrices offset every colour channel by a **whole unit** against
 * `inputClamp: 1`, so the operator **saturates**: nothing of the input colour
 * survives it and the only thing the input contributes is its alpha. The
 * destination blend is source-over and nothing else — `inputBackdropAware` binds
 * a snapshot of what is beneath as an extra *input* to the filter, and macOS
 * 26.5's QuartzCore carries no backdrop-aware variant that is not `_sover`
 * (claims §5.137 §2, which states the surviving argument for the alternative
 * reading at full strength and records why this is the reading vitrea takes).
 *
 *     darkening  →  black at the glyph's own coverage
 *     lightening →  white at 0.95 × that coverage
 *
 * ## Why this can live on the CPU
 *
 * The operator carries **no backdrop term**. The material's composite enters only
 * as the *selector*, and the selector is per-surface on both tiers, so folding
 * the operator into the published ink is not an approximation of the per-pixel
 * path — it *is* the per-pixel path, measured 0.00 and 0.04 code values apart on
 * the only two cells whose material varies beneath a patch the ink does not cover
 * (claims §5.137 §3–§4). That is what lets `css-tier.ts` publish a colour instead
 * of installing a `filter`, which on this tier is a measured hazard: a `filter`,
 * a `mask`, an `opacity` or a blend mode inside a host cuts the created layers
 * off from the page behind them, and §5.133 §5 measured a `mix-blend-mode` inside
 * a host collapsing a DOM-proxied group's `backdrop-filter` sampling. A per-pixel
 * path would also *diverge* from Apple where the two differ: Apple installs the
 * operator on the automatic colour and declines to rewrite an authored one
 * (§5.136 §4), and a filter over a subtree saturates the author's colour too.
 *
 * ## What is Apple's here and what is vitrea's
 *
 * Apple's, read with zero residual: the two matrices. Apple's, documentation-
 * sourced and published as such: the four label alphas (§5.137 §5 — Apple
 * publishes no component values and says not to hard-code them; these are four
 * independent third-party measurements agreeing exactly and unchanged from
 * macOS 11 to 26.5). vitrea's own, and *converged on* rather than authorised by
 * Apple's configuration: the selector. Apple selects per surface off that
 * surface's own adapted state, which is the same *shape* as
 * `foregroundCrossover`'s role and not its arithmetic — 258 of 258 occurrences
 * across three corpora, and the label following the same single bit on 72 of 72
 * (claims §5.138 §6; W27 Decision Log 16).
 */

import type { Rgb255 } from "./optics";

/**
 * Which pole applies. Named for what the operator *does* rather than for the
 * colour scheme it was read under, because the scheme is not what vitrea decides
 * on: a vitrea surface's own level does not have to follow the document's.
 */
export type LabelOperator = "darkening" | "lightening";

/**
 * The two matrices, at the float32 values
 * `results/2026-09-11-w27e-probe/table.json` holds. The dark alpha coefficient is
 * 0.95 in float32 and is written as that float32 value rather than as 0.95,
 * because `@vitrea/calibration`'s corpus test compares it to the dump byte for
 * byte. Four rows of five columns — `out_i = m_i1·R + m_i2·G + m_i3·B + m_i4·A +
 * m_i5` — not five rows of four.
 */
export const LABEL_MATRICES: Readonly<Record<LabelOperator, readonly number[]>> = {
  darkening: [1, 0, 0, 0, -1, 0, 1, 0, 0, -1, 0, 0, 1, 0, -1, 0, 0, 0, 1, 0],
  lightening: [1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0.949999988079071, 0],
};

/** An ink in encoded sRGB, channels and alpha in [0, 1], non-premultiplied. */
export interface LabelInk {
  readonly rgb: readonly [number, number, number];
  readonly alpha: number;
}

const clamp01 = (value: number): number => (value < 0 ? 0 : value > 1 ? 1 : value);

/**
 * A `CAColorMatrix` applied the way `inputClamp: 1` applies it: four rows of five
 * columns over non-premultiplied encoded channels, then a plain [0, 1] clamp —
 * per channel, because `inputClampPreserveHue` is unset and that key is what
 * would have made it a hue-preserving rescale. `feColorMatrix` at
 * `color-interpolation-filters: sRGB` is the same arithmetic, confirmed to the
 * code value on all four matrices the corpus carries (§5.133 §5, §5.137 §4).
 */
export function applyColorMatrix(ink: LabelInk, matrix: readonly number[]): LabelInk {
  if (matrix.length !== 20) {
    throw new Error(`A CAColorMatrix is twenty floats, not ${String(matrix.length)}`);
  }
  const input = [ink.rgb[0], ink.rgb[1], ink.rgb[2], ink.alpha];
  const out: number[] = [];
  for (let row = 0; row < 4; row += 1) {
    let sum = matrix[row * 5 + 4] as number;
    for (let column = 0; column < 4; column += 1) {
      sum += (matrix[row * 5 + column] as number) * (input[column] as number);
    }
    out.push(clamp01(sum));
  }
  return { rgb: [out[0] as number, out[1] as number, out[2] as number], alpha: out[3] as number };
}

/**
 * The pole the material's own composite level selects.
 *
 * `crossover` has no default: the number that belongs here is
 * `CSS_TIER_MAPPING.foregroundCrossover`, and a second copy of it would go on
 * agreeing with a constant that had moved. Above the crossover the surface is
 * bright and the ink darkens; below it the surface is dark and the ink lightens.
 */
export function labelOperatorFor(compositeLevel: number, crossover: number): LabelOperator {
  return compositeLevel >= crossover ? "darkening" : "lightening";
}

/** Apple's own two appearances, and the pole each one carries (§5.136 §4). */
export const LABEL_OPERATOR_BY_APPEARANCE: Readonly<Record<"light" | "dark", LabelOperator>> = {
  light: "darkening",
  dark: "lightening",
};

/**
 * The rendered ink: the operator evaluated on an automatic label colour.
 *
 * Takes no backdrop argument, and that absence is the claim: see the module note.
 */
export function vibrantInk(operator: LabelOperator, ink: LabelInk): LabelInk {
  return applyColorMatrix(ink, LABEL_MATRICES[operator]);
}

/**
 * The named levels, in the order they are published.
 *
 * `primary` is Apple's `labelColor` — SwiftUI's `Color.primary` resolves to it,
 * alpha included — and the three below it are `secondaryLabel`, `tertiaryLabel`
 * and `quaternaryLabel`.
 */
export const LABEL_LEVELS = ["primary", "secondary", "tertiary", "quaternary"] as const;

export type LabelLevel = (typeof LABEL_LEVELS)[number];

/**
 * **macOS's** label ladder, before the operator, per Apple appearance
 * (claims §5.137 §5; W27 Decision Log 15 (b)).
 *
 * Not the iOS one. vitrea published iOS's 1 / 0.6 / 0.3 / 0.18 on a cool
 * `#3C3C43` until this gate, which is a different platform's scale on a different
 * platform's ink; a web runtime replicating macOS publishes macOS's. The choice
 * was a decision rather than a lookup and Decision Log 15 (b) took it, with
 * Decision Log 9's WCAG floor kept as a minimum on secondary — Apple's alpha
 * wherever Apple's own would pass 4.5 against the actual composite, the solved
 * alpha where it would not.
 *
 * The alphas are Apple's own and documentation-sourced (§5.137 §5). The colour
 * they are carried on is *not* Apple's `labelColor` hex, because the operator
 * saturates it away: only the alpha survives into the glass.
 */
const APPEARANCE_LADDER: Readonly<Record<"light" | "dark", Readonly<Record<LabelLevel, number>>>> = {
  light: { primary: 0.847059, secondary: 0.498039, tertiary: 0.258824, quaternary: 0.098039 },
  dark: { primary: 0.847059, secondary: 0.54902, tertiary: 0.247059, quaternary: 0.098039 },
};

/**
 * Quantised to 1e-6, to nearest.
 *
 * A documented constant is published as documented — 1e-6 is fine enough that
 * the light pole's 0.847059 and the dark pole's 0.847059 × 0.95 = 0.804706 come
 * out exactly as the ledger records them, and coarse enough that a float32
 * product does not publish sixteen digits. A *solved* alpha is rounded the other
 * way; see `css-tier.ts`'s `alphaFor`.
 */
export const quantiseAlpha = (alpha: number): number => Math.round(alpha * 1e6) / 1e6;

/**
 * The four levels **through the operator**, per pole — what vitrea publishes.
 *
 * `darkening` carries Apple's light-appearance ladder unchanged, because that
 * matrix's alpha row is the identity. `lightening` carries the dark-appearance
 * ladder scaled by the matrix's 0.949999988079071, which is the one coefficient
 * of the pair that does anything to the alpha and the reason the primary ink
 * reads 0.804706 rather than 0.847059 in the dark.
 */
export const VIBRANT_LEVEL_ALPHA: Readonly<Record<LabelOperator, Readonly<Record<LabelLevel, number>>>> =
  Object.freeze({
    darkening: Object.freeze(
      Object.fromEntries(
        LABEL_LEVELS.map((level) => [
          level,
          quantiseAlpha(
            vibrantInk("darkening", { rgb: [0, 0, 0], alpha: APPEARANCE_LADDER.light[level] }).alpha,
          ),
        ]),
      ) as Record<LabelLevel, number>,
    ),
    lightening: Object.freeze(
      Object.fromEntries(
        LABEL_LEVELS.map((level) => [
          level,
          quantiseAlpha(
            vibrantInk("lightening", { rgb: [1, 1, 1], alpha: APPEARANCE_LADDER.dark[level] }).alpha,
          ),
        ]),
      ) as Record<LabelLevel, number>,
    ),
  });

/**
 * The colour each pole saturates to. Read out of the matrices rather than
 * written down, so a coefficient that moved could not leave a stale hex behind.
 */
export const VIBRANT_INK_CHANNELS: Readonly<Record<LabelOperator, Rgb255>> = Object.freeze({
  darkening: Object.freeze(
    vibrantInk("darkening", { rgb: [1, 1, 1], alpha: 1 }).rgb.map((c) => Math.round(c * 255)),
  ) as unknown as Rgb255,
  lightening: Object.freeze(
    vibrantInk("lightening", { rgb: [0, 0, 0], alpha: 1 }).rgb.map((c) => Math.round(c * 255)),
  ) as unknown as Rgb255,
});

/**
 * The two poles crossfaded at `tone`, the `darkening` pole's weight in [0, 1] —
 * the `foregroundTone` channel, consumed (W27e G2).
 *
 * `foregroundTone` has declared a `threshold-crossfade` driver since the motion
 * table was written and nothing had consumed it: the ink snapped at the
 * crossover, with neither the channel's dead band nor its 180 ms transit. This
 * is what the driver's output means.
 *
 * **A colour crossfade, in premultiplied space** — `α = t·α_d + (1−t)·α_l` and
 * the colour weighted by each pole's contribution to it. Three properties, and
 * the third is why this form and not the other:
 *
 *  - endpoint-exact: at 0 and 1 the fold is inert and the published ink is
 *    exactly one pole, which is the steady state on every frame outside a
 *    transit;
 *  - identical to `color-mix(in srgb, …)`, which is what a CSS transition on a
 *    colour does, so the value vitrea publishes is the value the platform would
 *    have interpolated had a custom property been registered as a `<color>`;
 *  - **order-free**, and therefore continuous under reversal. The alternative —
 *    the source-over composite of two drawn label layers, which is what a
 *    crossfade *is* on Apple's side — depends on which layer is on top, and the
 *    `threshold-crossfade` driver reverses from wherever it is. A fold whose
 *    layer order followed the driver's direction would pop by tens of code
 *    values the moment a backdrop drifted back across the band, which is the one
 *    thing this channel's hysteresis exists to prevent.
 *
 * The two folds differ mid-transit and agree at both ends; §5.140 records the
 * magnitude. Apple's layer order is not in evidence and no reading of the dumps
 * could carry it.
 */
export function crossfadeInk(darkening: LabelInk, lightening: LabelInk, tone: number): LabelInk {
  const t = clamp01(tone);
  if (t >= 1) return darkening;
  if (t <= 0) return lightening;
  const alpha = t * darkening.alpha + (1 - t) * lightening.alpha;
  if (alpha <= 0) return { rgb: darkening.rgb, alpha: 0 };
  const channel = (index: 0 | 1 | 2): number =>
    (t * darkening.alpha * darkening.rgb[index] +
      (1 - t) * lightening.alpha * lightening.rgb[index]) /
    alpha;
  return { rgb: [channel(0), channel(1), channel(2)], alpha };
}
