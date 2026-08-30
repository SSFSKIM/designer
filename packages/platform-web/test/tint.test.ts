/**
 * The tint across the tier boundary: the parse, the conversion, and the ink.
 *
 * The load-bearing claims here are three.
 *
 * 1. **The untinted material is untouched.** Every tinted path is entered on a
 *    tint being present, and the conversion is an identity without one — the
 *    calibration bed measures the material these tests leave alone.
 * 2. **The conversion is the existing mapping, extended rather than replaced.**
 *    `cssTintColor` returns exactly what `encodeRgb` did for an achromatic tint,
 *    because it solves the same equation `cssTintAlpha` already satisfied.
 * 3. **A declared tint can decide the ink with no backdrop hint**, and only when
 *    the whole reachable range of levels agrees.
 */

import { describe, expect, it } from "vitest";

import type { ResolvedAccessibilityPolicy, ResolvedMaterialPolicy } from "@vitreajs/vitrea";
import { glassTint } from "@vitreajs/vitrea";

import { cssTierDeclarations, FOREGROUND_INK } from "../src/css-tier";
import {
  boundedForegroundLevel,
  cssTierForegroundBounds,
  cssTierOptics,
  CSS_TIER_MAPPING,
  cssTintAlpha,
  cssTintColor,
  gpuTierForegroundBounds,
  linearTint,
  sourceOptics,
  tintedCssOptics,
  tintedSourceOptics,
  tintTone,
  tintToneAdaptation,
  TINT_TONE,
  type TintToneConstants,
} from "../src/optics";
import { createTintParser, resolveTintDeclaration } from "../src/tint";
import { createPlatformDiagnosticsChannel } from "../src/diagnostics";

const base = cssTierOptics().regular;
const source = sourceOptics().regular;
/** A saturated orange, so a hue error would be visible rather than rounding. */
const orange = linearTint(glassTint([1, 0.584, 0]));

/**
 * A tone curve with an excursion to test. The recalibration cascade fitted the
 * shipped curve to the identity (2026-08-31) because the active-pose reference's
 * tinted material IS the seed, so the mechanism's shape properties are exercised
 * here on W3 phase 1's provisional constants rather than on constants that make
 * the mechanism inert.
 */
const EXCURSION: TintToneConstants = { ...TINT_TONE, floor: 0.45, ceilMix: 0.45, low: 0.02, high: 0.65 };

const materialPolicy = (patch: Partial<ResolvedMaterialPolicy> = {}): ResolvedMaterialPolicy => ({
  glass: "material",
  colorSource: "material",
  frost: "nominal",
  refraction: "nominal",
  occlusion: "nominal",
  border: "nominal",
  ambientTint: "nominal",
  foreground: "adaptive",
  ...patch,
});

const policy = (patch: Partial<ResolvedMaterialPolicy> = {}): ResolvedAccessibilityPolicy => ({
  reducedTransparency: false,
  reducedMotion: false,
  increasedContrast: false,
  forcedColors: false,
  material: materialPolicy(patch),
  motion: {
    overshoot: "elastic",
    deformation: "nominal",
    shimmer: "travel",
    morph: "elastic",
    crossfade: "never",
    positionalContinuity: true,
  },
});

const srgbEncode = (linear: number): number => {
  const c = Math.min(1, Math.max(0, linear));
  return c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
};

describe("parsing an author's colour", () => {
  const parse = createTintParser(document);

  it("reads the numeric syntaxes, with the alpha as the tint's strength", () => {
    expect(parse("#ff9500")).toEqual({ color: [1, 149 / 255, 0], strength: 1 });
    expect(parse("rgb(255, 149, 0)")?.strength).toBe(1);
    expect(parse("rgba(255, 149, 0, 0.5)")?.strength).toBeCloseTo(0.5, 6);
    expect(parse("rgb(255 149 0 / 50%)")?.strength).toBeCloseTo(0.5, 6);
  });

  it("reads short hex and hex with alpha", () => {
    expect(parse("#f90")).toEqual({ color: [1, 153 / 255, 0], strength: 1 });
    expect(parse("#ff950080")?.strength).toBeCloseTo(0.5, 1);
  });

  it("memoises, so a colour is parsed once however many frames declare it", () => {
    expect(parse("#123456")).toBe(parse("#123456"));
  });

  it("refuses what it cannot resolve, and says which value it refused", () => {
    const diagnostics = createPlatformDiagnosticsChannel();
    expect(resolveTintDeclaration("not-a-colour", parse, "node", diagnostics)).toBeNull();
    expect(diagnostics.reported[0]?.code).toBe("tint-unparseable");
    expect(diagnostics.reported[0]?.message).toContain("not-a-colour");
  });

  it("keeps the three declaration states apart", () => {
    expect(resolveTintDeclaration(undefined, parse, "node")).toBeUndefined();
    expect(resolveTintDeclaration(null, parse, "node")).toBeNull();
    expect(resolveTintDeclaration("#ff0000", parse, "node")).toEqual({
      color: [1, 0, 0],
      strength: 1,
    });
  });
});

describe("the tone map, mirrored", () => {
  it("agrees with the renderer's constants", () => {
    // The mirror's own values; `packages/calibration/test/tier-coherence.test.ts`
    // is what pins them against the renderer's profile in both directions.
    expect(TINT_TONE.low).toBeLessThan(TINT_TONE.high);
    expect(TINT_TONE.floor).toBeGreaterThan(0);
    expect(TINT_TONE.ceilMix).toBeGreaterThanOrEqual(0);
  });

  it("follows the accessibility axis that already governs the material's response", () => {
    expect(tintToneAdaptation("nominal")).toBe(1);
    expect(tintToneAdaptation("reduced")).toBe(TINT_TONE.reducedAdaptation);
    expect(tintToneAdaptation("none")).toBe(0);
  });

  it("leaves the colour alone when the regime stops the response", () => {
    expect(tintTone(orange.color, 0.9, 0)).toEqual(orange.color);
  });
});

describe("tintedSourceOptics", () => {
  it("moves the tint colour and never the alpha", () => {
    const tinted = tintedSourceOptics(source, orange, 0.2, 1);
    expect(tinted.tintAlpha).toBe(source.tintAlpha);
    expect(tinted.tint).not.toEqual(source.tint);
    expect(tinted.tint[0]).toBeGreaterThan(tinted.tint[2]);
  });

  it("is the identity with no tint and at zero strength", () => {
    expect(tintedSourceOptics(source, undefined, 0.2, 1)).toBe(source);
    expect(tintedSourceOptics(source, { ...orange, strength: 0 }, 0.2, 1)).toBe(source);
  });
});

describe("the CSS-tier conversion", () => {
  it("returns the base optics identically for an untinted surface", () => {
    expect(tintedCssOptics(base, source, undefined, 0.02, 1)).toBe(base);
    expect(tintedCssOptics(base, source, { ...orange, strength: 0 }, 0.02, 1)).toBe(base);
  });

  it("reproduces the untinted encode for an achromatic tint — one mapping, extended", () => {
    // The claim `cssTintColor` rests on: for a white tint the colour solve is the
    // same equation the alpha solve already satisfied, so it returns 255s.
    expect(cssTintColor(source, cssTintAlpha(source))).toEqual([255, 255, 255]);
  });

  it("lands the tinted composite on the renderer's, channel for channel, at the reference backdrop", () => {
    // Read on a tone that stays inside the gamut. `EXCURSION`'s floor of 0.45
    // shades the seed, so the colour the CSS tier has to declare is reachable and
    // the conversion is exact to within its own rounding. The full-saturation
    // case is the test below, and it is a different result rather than a looser
    // version of this one.
    const tinted = tintedSourceOptics(
      source,
      orange,
      CSS_TIER_MAPPING.referenceBackdropLuminance,
      1,
      EXCURSION,
    );
    const alpha = cssTintAlpha(tinted, CSS_TIER_MAPPING);
    const colour = cssTintColor(tinted, alpha, CSS_TIER_MAPPING);
    const backdrop = CSS_TIER_MAPPING.referenceBackdropLuminance;

    for (const index of [0, 1, 2] as const) {
      const gpu = srgbEncode(
        backdrop * (1 - tinted.tintAlpha) + tinted.tint[index] * tinted.tintAlpha,
      );
      const css = srgbEncode(backdrop) * (1 - alpha) + (colour[index] / 255) * alpha;
      // One 8-bit code of rounding is the whole budget; the conversion is exact
      // in the reals and quantised on the way out.
      expect(Math.abs(gpu - css)).toBeLessThan(1.5 / 255);
    }
  });

  it("cannot reach a FULLY SATURATED tint, and the shortfall is the sRGB gamut", () => {
    /*
     * A measured limit of the crossing, recorded rather than absorbed into the
     * bound above. The cascade fitted the tone curve to the identity, so a
     * full-strength author tint now hands this tier the bare seed — linear
     * (1, 0.3, 0) for `systemOrange`. The GPU tier composites toward that in
     * linear light; to reproduce the same result the CSS tier would have to
     * declare an `rgba()` colour brighter than sRGB can express, so
     * `cssTintColor` clips at 255 and the composite falls short.
     *
     * Isolated to the curve rather than to the alpha: at the same tint alpha the
     * shaded tone above lands within 0.07 of one code, and the bare seed misses
     * by 5.59. At C9a's old alpha of 0.62 the bare seed still missed, by 3.82 —
     * so this is the saturation, not the opacity.
     *
     * Fixing it means solving the alpha and the colour JOINTLY under the gamut
     * constraint instead of solving the alpha on luminance and deriving the
     * colour, which is a CSS-tier mechanism change and is named as the next
     * parent-impact item on this axis in claims §5.13. What the coherence gate
     * measures on real cells is in the same section.
     */
    const tinted = tintedSourceOptics(source, orange, CSS_TIER_MAPPING.referenceBackdropLuminance, 1);
    const alpha = cssTintAlpha(tinted, CSS_TIER_MAPPING);
    const colour = cssTintColor(tinted, alpha, CSS_TIER_MAPPING);
    const backdrop = CSS_TIER_MAPPING.referenceBackdropLuminance;

    // The channel that clips is the one the seed saturates, and it clips at 255.
    expect(tinted.tint[0]).toBeCloseTo(orange.color[0], 12);
    expect(colour[0]).toBe(255);

    const worst = Math.max(
      ...([0, 1, 2] as const).map((index) => {
        const gpu = srgbEncode(
          backdrop * (1 - tinted.tintAlpha) + tinted.tint[index] * tinted.tintAlpha,
        );
        const css = srgbEncode(backdrop) * (1 - alpha) + (colour[index] / 255) * alpha;
        return Math.abs(gpu - css);
      }),
    );
    // Bounded and on the record: under six 8-bit codes, and never zero.
    expect(worst).toBeGreaterThan(1.5 / 255);
    expect(worst).toBeLessThan(6 / 255);
  });

  it("carries the seed's hue into the declared colour", () => {
    const optics = tintedCssOptics(base, source, orange, 0.2, 1);
    expect(optics.tint[0]).toBeGreaterThan(optics.tint[2]);
    expect(optics.tintAlpha).toBeGreaterThan(0);
  });
});

describe("the ink, against a tinted surface", () => {
  it("returns nothing where the backdrop still decides", () => {
    // The untinted white material spans nearly the whole range at its alpha.
    const clear = { ...base, tintAlpha: 0.1, tint: [128, 128, 128] as const };
    expect(boundedForegroundLevel(cssTierForegroundBounds(clear), 0.475)).toBeUndefined();
  });

  it("decides dark ink for a bright tint whatever is behind it", () => {
    const bright = tintedCssOptics(base, source, linearTint(glassTint([1, 0.95, 0.6])), 0.5, 1);
    const bounds = cssTierForegroundBounds(bright);
    expect(bounds[0]).toBeGreaterThanOrEqual(CSS_TIER_MAPPING.foregroundCrossover);
    expect(boundedForegroundLevel(bounds, CSS_TIER_MAPPING.foregroundCrossover)).toBe(bounds[0]);
  });

  it("brackets the same way on the renderer's composite", () => {
    const dark = tintedSourceOptics(source, linearTint(glassTint([0.02, 0.02, 0.04])), 0.05, 1);
    const bounds = gpuTierForegroundBounds({ ...dark, tintAlpha: 0.9 });
    expect(boundedForegroundLevel(bounds, CSS_TIER_MAPPING.foregroundCrossover)).toBe(bounds[1]);
  });

  it("takes the dark token on a bright tint, with no hint at all", () => {
    const tint = glassTint([1, 0.95, 0.6]);
    const optics = tintedCssOptics(base, source, linearTint(tint), 0.5, 1);
    const declarations = cssTierDeclarations({
      radii: [12, 12, 12, 12],
      optics,
      tint,
      policy: policy(),
    });
    expect(declarations["--vitrea-foreground"]).toBe(FOREGROUND_INK.dark);
  });

  it("takes the light token on a dark tint once the material occludes enough to decide", () => {
    // At the nominal alpha a near-black tint still lets a white backdrop through
    // far enough to straddle the crossover, and the bracket correctly declines to
    // decide. Reduced transparency closes that headroom, and then it can.
    const tint = glassTint([0.02, 0.02, 0.04]);
    const optics = tintedCssOptics(base, source, linearTint(tint), 0.05, 1);
    expect(
      cssTierDeclarations({ radii: [12, 12, 12, 12], optics, tint, policy: policy() })[
        "--vitrea-foreground"
      ],
    ).toContain("light-dark(");
    expect(
      cssTierDeclarations({
        radii: [12, 12, 12, 12],
        optics,
        tint,
        policy: policy({ occlusion: "increased" }),
      })["--vitrea-foreground"],
    ).toBe(FOREGROUND_INK.light);
  });

  it("leaves an untinted hintless surface on the scheme's own answer", () => {
    const declarations = cssTierDeclarations({
      radii: [12, 12, 12, 12],
      optics: base,
      policy: policy(),
    });
    expect(declarations["--vitrea-foreground"]).toContain("light-dark(");
  });
});

describe("accessibility still wins", () => {
  const tint = glassTint([1, 0.584, 0]);
  const tinted = tintedCssOptics(base, source, orange, 0.2, 1);

  it("keeps the tint's colour while increased contrast lifts its occlusion", () => {
    const nominal = cssTierDeclarations({
      radii: [12, 12, 12, 12],
      optics: tinted,
      tint,
      policy: policy(),
    });
    const lifted = cssTierDeclarations({
      radii: [12, 12, 12, 12],
      optics: tinted,
      tint,
      policy: policy({ occlusion: "increased" }),
    });
    expect(Number(lifted["--vitrea-occlusion"])).toBeGreaterThan(
      Number(nominal["--vitrea-occlusion"]),
    );
    // The colour is the author's either way; only how much of it there is moved.
    expect(lifted["background-color"]?.split(",").slice(0, 3)).toEqual(
      nominal["background-color"]?.split(",").slice(0, 3),
    );
  });

  it("never overrides near-monochrome ink with a tint-derived level", () => {
    const declarations = cssTierDeclarations({
      radii: [12, 12, 12, 12],
      optics: tinted,
      tint,
      policy: policy({ foreground: "near-monochrome" }),
    });
    expect(declarations["--vitrea-foreground"]).toBe("light-dark(#000, #fff)");
  });

  it("erases the tint entirely under forced colours, where there is no material", () => {
    const declarations = cssTierDeclarations({
      radii: [12, 12, 12, 12],
      optics: tinted,
      tint,
      policy: policy({ glass: "none" }),
    });
    expect(declarations["--vitrea-tint"]).toBe("Canvas");
    expect(declarations["background-color"]).toBe("Canvas");
    expect(declarations["--vitrea-foreground"]).toBe("CanvasText");
  });

  it("collapses the tone range, not the colour, when the ambient regime narrows", () => {
    /*
     * Read on a curve that HAS a range. The cascade fitted the shipped curve to
     * the identity (floor 1, ceilMix 0 — the reference's tinted material is the
     * seed), so at the default constants there is no excursion for a regime to
     * narrow and this property would pass vacuously. `EXCURSION` carries W3 phase
     * 1's provisional constants for exactly that reason: the fold is a mechanism
     * and has to be proven of the mechanism.
     */
    const wide = tintedSourceOptics(source, orange, 0.9, tintToneAdaptation("nominal"), EXCURSION);
    const narrow = tintedSourceOptics(source, orange, 0.9, tintToneAdaptation("none"), EXCURSION);
    for (const index of [0, 1, 2] as const) {
      expect(narrow.tint[index]).toBeCloseTo(orange.color[index], 12);
    }
    expect(wide.tint[2]).toBeGreaterThan(narrow.tint[2]);
  });

  it("at the shipped constants the regime has no range left to narrow", () => {
    // The same statement from the other side, so the identity is asserted rather
    // than inferred from the test above having to reach for another profile.
    const wide = tintedSourceOptics(source, orange, 0.9, tintToneAdaptation("nominal"));
    const narrow = tintedSourceOptics(source, orange, 0.9, tintToneAdaptation("none"));
    expect(wide.tint).toEqual(narrow.tint);
    for (const index of [0, 1, 2] as const) {
      expect(wide.tint[index]).toBeCloseTo(orange.color[index], 12);
    }
  });
});
