/**
 * Apple's label operator in the runtime (W27e G2; claims §5.140).
 *
 * What is pinned here is the arithmetic and the two published tables. What is
 * *not* pinned here is that the coefficients are Apple's: that is
 * `@vitrea/calibration`'s `test/vibrancy.test.ts`, which reads the committed
 * layer dumps and compares them to these very constants — the runtime is the one
 * copy and the corpus test is what holds it to the dumps.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_MOTION_PROFILE,
  MOTION_DRIVER_BY_CHANNEL,
  ThresholdCrossfadeDriver,
  type DriverConfig,
} from "@vitrea/motion";

/**
 * The same narrowing `root.ts` performs, and the first case below is what makes
 * it checked: `MotionProfile` types every channel's config as the union while
 * the binding table pins this one to `threshold-crossfade`.
 */
const TONE = DEFAULT_MOTION_PROFILE.channels.foregroundTone as Extract<
  DriverConfig,
  { kind: "threshold-crossfade" }
>;

import {
  applyColorMatrix,
  crossfadeInk,
  labelOperatorFor,
  quantiseAlpha,
  vibrantInk,
  LABEL_LEVELS,
  VIBRANT_INK_CHANNELS,
  VIBRANT_LEVEL_ALPHA,
  type LabelInk,
} from "../src/vibrancy";
import { FOREGROUND_INK } from "../src/css-tier";
import { CSS_TIER_MAPPING } from "../src/optics";
import { INK_RULE, VIBRANT_INK_RULE } from "../src/ink-stylesheet";
import { HOST_ATTRIBUTES } from "../src/host";

describe("the label operator", () => {
  it("saturates: the output colour is a pole and only the alpha comes from the input", () => {
    // A sweep of the gamut through both matrices. Nothing of the input colour
    // survives, which is what a whole-unit offset against `inputClamp` 1 does and
    // what makes the operator's CSS fold exact (claims §5.137 §2).
    for (const r of [0, 0.25, 0.5, 0.75, 1]) {
      for (const g of [0, 0.5, 1]) {
        for (const b of [0, 0.5, 1]) {
          const ink: LabelInk = { rgb: [r, g, b], alpha: 0.5 };
          expect(vibrantInk("darkening", ink).rgb).toEqual([0, 0, 0]);
          expect(vibrantInk("lightening", ink).rgb).toEqual([1, 1, 1]);
        }
      }
    }
  });

  it("keeps the alpha under darkening and scales it by the dark matrix's 0.95", () => {
    for (const alpha of [0, 0.25, 0.847059, 1]) {
      const ink: LabelInk = { rgb: [0.3, 0.6, 0.9], alpha };
      expect(vibrantInk("darkening", ink).alpha).toBe(alpha);
      expect(vibrantInk("lightening", ink).alpha).toBeCloseTo(alpha * 0.949999988079071, 12);
    }
  });

  it("is idempotent on one pole and not on the other, which is why nothing applies it twice", () => {
    // The reason the runtime folds the operator into the published ink once and
    // installs no per-pixel filter over content that already carries it: a second
    // pass is inert in the light appearance and loses another 5 % in the dark.
    const black: LabelInk = { rgb: [0, 0, 0], alpha: 0.847059 };
    expect(vibrantInk("darkening", black)).toEqual(black);
    const white = vibrantInk("lightening", { rgb: [1, 1, 1], alpha: 0.847059 });
    expect(vibrantInk("lightening", white).alpha).toBeLessThan(white.alpha);
  });

  it("refuses a matrix that is not four rows of five", () => {
    expect(() => applyColorMatrix({ rgb: [0, 0, 0], alpha: 1 }, [1, 0, 0])).toThrow();
  });

  it("selects the pole off the material's own level against the crossover", () => {
    const crossover = CSS_TIER_MAPPING.foregroundCrossover;
    expect(labelOperatorFor(crossover, crossover)).toBe("darkening");
    expect(labelOperatorFor(crossover - 1e-9, crossover)).toBe("lightening");
    expect(labelOperatorFor(1, crossover)).toBe("darkening");
    expect(labelOperatorFor(0, crossover)).toBe("lightening");
  });
});

describe("the published ladder", () => {
  it("is macOS's, through the operator, to the last digit the ledger records", () => {
    // Documentation-sourced, and published as such (claims §5.137 §5): Apple
    // publishes no component values. The dark pole's numbers are the dark
    // appearance's times the lightening matrix's 0.95.
    expect(VIBRANT_LEVEL_ALPHA.darkening).toEqual({
      primary: 0.847059,
      secondary: 0.498039,
      tertiary: 0.258824,
      quaternary: 0.098039,
    });
    expect(VIBRANT_LEVEL_ALPHA.lightening).toEqual({
      primary: 0.804706,
      secondary: 0.521569,
      tertiary: 0.234706,
      quaternary: 0.093137,
    });
    // And it is a ladder: strictly descending on both poles.
    for (const pole of ["darkening", "lightening"] as const) {
      const alphas = LABEL_LEVELS.map((level) => VIBRANT_LEVEL_ALPHA[pole][level]);
      for (let i = 1; i < alphas.length; i += 1) {
        expect(alphas[i] as number).toBeLessThan(alphas[i - 1] as number);
      }
    }
  });

  it("is not the iOS ladder vitrea published before this gate", () => {
    // 1 / 0.6 / 0.3 / 0.18 on a cool `#3C3C43` is a different platform's scale on
    // a different platform's ink (W27 Decision Log 15 (b)).
    for (const pole of ["darkening", "lightening"] as const) {
      expect(VIBRANT_LEVEL_ALPHA[pole].primary).not.toBe(1);
      expect(VIBRANT_LEVEL_ALPHA[pole].secondary).not.toBe(0.6);
      expect(VIBRANT_LEVEL_ALPHA[pole].tertiary).not.toBe(0.3);
      expect(VIBRANT_LEVEL_ALPHA[pole].quaternary).not.toBe(0.18);
    }
  });

  it("saturates the ink to pure black and pure white, and nothing near them", () => {
    expect(VIBRANT_INK_CHANNELS.darkening).toEqual([0, 0, 0]);
    expect(VIBRANT_INK_CHANNELS.lightening).toEqual([255, 255, 255]);
    expect(FOREGROUND_INK.dark).toBe("rgb(0 0 0 / 0.847059)");
    expect(FOREGROUND_INK.light).toBe("rgb(255 255 255 / 0.804706)");
  });

  it("derives the channels from the matrices rather than transcribing them", () => {
    // A coefficient that moved must not leave a stale hex behind, so the two
    // channel triples are read back out of the operator.
    for (const pole of ["darkening", "lightening"] as const) {
      const out = vibrantInk(pole, { rgb: [0.5, 0.5, 0.5], alpha: 1 }).rgb;
      expect(out.map((channel) => Math.round(channel * 255))).toEqual([
        ...VIBRANT_INK_CHANNELS[pole],
      ]);
    }
  });

  it("quantises to 1e-6 rather than to the 1e-3 the ink used to be written at", () => {
    // At 1e-3 the two poles would publish 0.848 and 0.805, and "at Apple's alpha"
    // would be false by a hair on both.
    expect(quantiseAlpha(0.8470594)).toBe(0.847059);
    expect(quantiseAlpha(0.847059 * 0.949999988079071)).toBe(0.804706);
  });
});

describe("the crossfade", () => {
  const dark: LabelInk = { rgb: [0, 0, 0], alpha: VIBRANT_LEVEL_ALPHA.darkening.primary };
  const light: LabelInk = { rgb: [1, 1, 1], alpha: VIBRANT_LEVEL_ALPHA.lightening.primary };

  it("is exact at both ends", () => {
    expect(crossfadeInk(dark, light, 1)).toEqual(dark);
    expect(crossfadeInk(dark, light, 0)).toEqual(light);
    // And clamped, so a driver that overshot could not publish an out-of-gamut ink.
    expect(crossfadeInk(dark, light, 2)).toEqual(dark);
    expect(crossfadeInk(dark, light, -1)).toEqual(light);
  });

  it("is the premultiplied mix `color-mix(in srgb, …)` performs", () => {
    for (const t of [0.1, 0.25, 0.5, 0.75, 0.9]) {
      const mixed = crossfadeInk(dark, light, t);
      const alpha = t * dark.alpha + (1 - t) * light.alpha;
      expect(mixed.alpha).toBeCloseTo(alpha, 12);
      expect(mixed.rgb[0]).toBeCloseTo(((1 - t) * light.alpha) / alpha, 12);
    }
  });

  it("is order-free, which is what makes it continuous under a reversal", () => {
    // The `threshold-crossfade` driver reverses from wherever it is. A fold whose
    // layer order followed the direction would jump by tens of code values at the
    // turn; this one is a function of the weight alone.
    for (const t of [0.2, 0.5, 0.8]) {
      expect(crossfadeInk(dark, light, t)).toEqual(crossfadeInk(dark, light, t));
      const swapped = crossfadeInk(light, dark, 1 - t);
      expect(swapped.alpha).toBeCloseTo(crossfadeInk(dark, light, t).alpha, 12);
    }
  });

  /**
   * The number the ledger quotes for the departure from `declaration.md` §2 (d)
   * (claims §5.140 §7), pinned so it cannot drift out of the record.
   *
   * The declared fold was the source-over composite of two drawn label layers
   * with the *arriving* pole on top, which is what a crossfade is on Apple's
   * side. It is order-dependent, and the driver reverses from wherever it is —
   * so an order that followed the transit's direction would flip mid-transit,
   * and at the midpoint the two orders are 66 code values apart at the same
   * alpha. That discontinuity, on exactly the event this channel's hysteresis
   * exists to damp, is why the shipped fold is order-free instead.
   */
  it("pins what the declared source-over fold would have cost at a reversal", () => {
    const over = (bottom: LabelInk, top: LabelInk): LabelInk => {
      const alpha = top.alpha + bottom.alpha * (1 - top.alpha);
      const channel = (index: 0 | 1 | 2): number =>
        (top.rgb[index] * top.alpha + bottom.rgb[index] * bottom.alpha * (1 - top.alpha)) / alpha;
      return { rgb: [channel(0), channel(1), channel(2)], alpha };
    };
    const scaled = (ink: LabelInk, weight: number): LabelInk => ({
      rgb: ink.rgb,
      alpha: ink.alpha * weight,
    });

    const darkOnTop = over(scaled(light, 0.5), scaled(dark, 0.5));
    const lightOnTop = over(scaled(dark, 0.5), scaled(light, 0.5));
    expect(darkOnTop.alpha).toBeCloseTo(lightOnTop.alpha, 12);
    expect(Math.abs(darkOnTop.rgb[0] - lightOnTop.rgb[0]) * 255).toBeCloseTo(66.29, 2);

    // And what the shipped fold is worth against the declared one, which is the
    // other number §5.140 §7 quotes: 22.8 code values over an encoded 0.475
    // material, at the midpoint, agreeing exactly at both ends.
    const shipped = crossfadeInk(dark, light, 0.5);
    const overMaterial = (ink: LabelInk): number => ink.alpha * ink.rgb[0] + (1 - ink.alpha) * 0.475;
    expect(Math.abs(overMaterial(shipped) - overMaterial(darkOnTop)) * 255).toBeCloseTo(22.8, 1);
    expect(crossfadeInk(dark, light, 1)).toEqual(dark);
    expect(crossfadeInk(dark, light, 0)).toEqual(light);
  });

  it("moves monotonically between the poles", () => {
    let previous = crossfadeInk(dark, light, 0).rgb[0];
    for (let t = 0.05; t <= 1.0001; t += 0.05) {
      const next = crossfadeInk(dark, light, Math.min(1, t)).rgb[0];
      expect(next).toBeLessThanOrEqual(previous + 1e-12);
      previous = next;
    }
  });
});

describe("the `foregroundTone` channel, as the runtime consumes it", () => {
  it("is the family the binding table gives it, which `root.ts` narrows to", () => {
    // `root.ts` reads `DEFAULT_MOTION_PROFILE.channels.foregroundTone` as a
    // `threshold-crossfade` config rather than branching on the union. This is
    // what makes that read checked rather than asserted.
    expect(MOTION_DRIVER_BY_CHANNEL.foregroundTone).toBe("threshold-crossfade");
    expect(DEFAULT_MOTION_PROFILE.channels.foregroundTone.kind).toBe("threshold-crossfade");
  });

  it("crosses at the optics constant, not at the tunable's placeholder 0.5", () => {
    expect(TONE).toMatchObject({ threshold: 0.5, hysteresis: 0.08, crossfadeMs: 180 });
    expect(CSS_TIER_MAPPING.foregroundCrossover).not.toBe(0.5);

    const driver = new ThresholdCrossfadeDriver(
      { ...TONE, threshold: CSS_TIER_MAPPING.foregroundCrossover },
      0,
    );
    const half = 0.08 / 2;
    // Inside the dead band nothing commits; above it the dark pole does.
    driver.retarget(CSS_TIER_MAPPING.foregroundCrossover + half);
    expect(driver.target).toBe(0);
    driver.retarget(CSS_TIER_MAPPING.foregroundCrossover + half + 1e-6);
    expect(driver.target).toBe(1);
    // And it does not come back until the band's other edge.
    driver.retarget(CSS_TIER_MAPPING.foregroundCrossover - half);
    expect(driver.target).toBe(1);
    driver.retarget(CSS_TIER_MAPPING.foregroundCrossover - half - 1e-6);
    expect(driver.target).toBe(0);
  });

  it("takes 180 ms to cross, which is the whole of the transit the ink shows", () => {
    const driver = new ThresholdCrossfadeDriver(
      { ...TONE, threshold: CSS_TIER_MAPPING.foregroundCrossover },
      0,
    );
    driver.retarget(1);
    driver.advance(90);
    expect(driver.value).toBeCloseTo(0.5, 6);
    driver.advance(90);
    expect(driver.value).toBe(1);
    expect(driver.settled).toBe(true);
  });
});

describe("the ink stylesheet's two rules", () => {
  it("publishes the token path at (0,0,0) and the owned path at (0,1,0)", () => {
    expect(INK_RULE).toContain(`:where([${HOST_ATTRIBUTES.node}])`);
    expect(VIBRANT_INK_RULE).toContain(`[${HOST_ATTRIBUTES.vibrant}]`);
    expect(VIBRANT_INK_RULE).not.toContain(":where(");
    // Both resolve the same token: the operator path is a precedence and not a
    // second colour (W27 §Design; Decision Log 15 (a)).
    expect(INK_RULE).toContain("var(--vitrea-foreground)");
    expect(VIBRANT_INK_RULE).toContain("var(--vitrea-foreground)");
  });

  it("keeps the owned rule beatable by an application rule that names the element", () => {
    // Apple installs the operator on the automatic colour and declines to rewrite
    // a label that names its own colour (claims §5.136 §4), and root Decision Log
    // #34(c) says the same for vitrea. An attribute selector is 0,1,0: it beats a
    // bare tag and a universal reset, and loses to a class, an id or an
    // `!important`. Pinned as the shape of the selector rather than by parsing it.
    expect(VIBRANT_INK_RULE).not.toContain("!important");
    expect(VIBRANT_INK_RULE.startsWith("[")).toBe(true);
  });
});
