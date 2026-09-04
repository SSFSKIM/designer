/**
 * The tint across the tier boundary: the parse, the conversion, and the ink.
 *
 * The load-bearing claims here are three.
 *
 * 1. **The untinted material is untouched.** Every tinted path is entered on a
 *    tint being present, and the conversion is an identity without one — the
 *    calibration bed measures the material these tests leave alone.
 * 2. **The tint is an opaque shaded layer at the author's opacity (W10)**, and
 *    this tier folds it into its one `rgba()` exactly, in the encoded space both
 *    layers composite in — so the fold is convex and the gamut clip that §5.13
 *    attributed the tinted coherence miss to cannot occur. Since W16 G1 that one
 *    `rgba()` is the overlay layer's `background-color` rather than the host's:
 *    the tint sits above both filtered layers, because a tint beneath them is
 *    blurred by them. The arithmetic is unchanged and only the element moved.
 * 3. **A declared tint can decide the ink with no backdrop hint**, and only when
 *    the whole reachable range of levels agrees.
 */

import { describe, expect, it } from "vitest";

import type { ResolvedAccessibilityPolicy, ResolvedMaterialPolicy } from "@vitreajs/vitrea";
import { glassTint } from "@vitreajs/vitrea";

import {
  cssTierDeclarations,
  FOREGROUND_INK,
  type CssTierSurface,
  type StyleDeclarations,
} from "../src/css-tier";
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
  tintShade,
  tintShadeLayer,
  tintToneAdaptation,
  TINT_SHADE,
} from "../src/optics";
import { createTintParser, resolveTintDeclaration } from "../src/tint";
import { createPlatformDiagnosticsChannel } from "../src/diagnostics";

const base = cssTierOptics().regular;
const source = sourceOptics().regular;
/** A saturated orange, so a hue error would be visible rather than rounding. */
const orange = linearTint(glassTint([1, 0.584, 0]));

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

/**
 * The host's own declarations — the geometry, the outer shadow and the five
 * tokens, which is where the ink token has always lived and still does.
 *
 * Since W16 G1 the tier returns a `CssTierRender` rather than one flat record,
 * because its properties are written to four different elements. These two
 * readers name the element instead of flattening them back together.
 */
const hostOf = (surface: CssTierSurface): StyleDeclarations => cssTierDeclarations(surface).host;

/**
 * The overlay layer's declarations — the tint, the press glow and the rim, the
 * three terms this tier paints above both filtered layers.
 *
 * It throws where the tier created no layers rather than handing back an empty
 * record: the only surface without them is the forced-colours one, and a test
 * asking that regime for its tint is asking a question it has no answer to.
 */
const overlayOf = (surface: CssTierSurface): StyleDeclarations => {
  const { layers } = cssTierDeclarations(surface);
  if (layers === undefined) throw new Error("the tier created no layers for this surface");
  return layers.overlay;
};

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

describe("the shade law, mirrored", () => {
  it("agrees with the renderer's constants", () => {
    // The mirror's own values; `packages/calibration/test/tier-coherence.test.ts`
    // is what pins them against the renderer's profile in both directions.
    expect(TINT_SHADE.dark).toBeGreaterThan(0);
    expect(TINT_SHADE.dark).toBeLessThan(TINT_SHADE.light);
    expect(TINT_SHADE.strength).toBe(1);
  });

  it("follows the accessibility axis that already governs the material's response", () => {
    expect(tintToneAdaptation("nominal")).toBe(1);
    expect(tintToneAdaptation("reduced")).toBe(TINT_SHADE.reducedAdaptation);
    expect(tintToneAdaptation("none")).toBe(0);
  });

  it("is a shade of the seed — hue intact, darker over darker content, never brighter than the seed", () => {
    const dark = tintShadeLayer(orange.color, 0, 1);
    const light = tintShadeLayer(orange.color, 1, 1);
    expect(dark[0] / orange.color[0]).toBeCloseTo(dark[1] / orange.color[1], 10);
    expect(dark[0]).toBeLessThan(light[0]);
    expect(light).toEqual(orange.color);
    expect(tintShade(0, 1)).toBeCloseTo(TINT_SHADE.dark, 12);
  });

  it("leaves the colour alone when the regime stops the response", () => {
    expect(tintShadeLayer(orange.color, 0, 0)).toEqual(orange.color);
  });
});

describe("tintedSourceOptics", () => {
  it("moves the tint colour AND the alpha — the layer is opaque at the author's opacity", () => {
    const tinted = tintedSourceOptics(source, orange, 0.2, 1);
    expect(tinted.tintAlpha).toBe(1);
    expect(tinted.tint[0]).toBeGreaterThan(tinted.tint[2]);
    const half = tintedSourceOptics(source, { ...orange, strength: 0.5 }, 0.2, 1);
    expect(half.tintAlpha).toBeCloseTo(1 - 0.5 * (1 - source.tintAlpha), 12);
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

  it("declares the shaded seed itself, opaque, at full strength — no gamut clip", () => {
    // §5.13 recorded a fully saturated tint as unreachable through the alpha
    // solve, because the tier was asked to reproduce a linear-light WASH of the
    // seed. The measured tint is not a wash: at full strength the layer is
    // opaque and its colour is the shade of the seed in the gamut by
    // construction, so the declaration is exact to the 8-bit rounding.
    const backdrop = CSS_TIER_MAPPING.referenceBackdropLuminance;
    const optics = tintedCssOptics(base, source, orange, backdrop, 1);
    expect(optics.tintAlpha).toBe(1);
    const u = (1 - source.tintAlpha) * backdrop + source.tintAlpha * 1;
    const layer = tintShadeLayer(orange.color, u, 1);
    for (const index of [0, 1, 2] as const) {
      expect(Math.abs(optics.tint[index] - Math.round(srgbEncode(layer[index]) * 255))).toBeLessThanOrEqual(1);
    }
  });

  it("folds a partial strength as the encoded-space mix of the two layers, exactly", () => {
    // Two `rgba()` layers over the backdrop fold into one: what the page would
    // composite with the author's layer over the material's layer is what the
    // single declaration composites, channel for channel.
    const backdrop = CSS_TIER_MAPPING.referenceBackdropLuminance;
    const s = 0.5;
    const optics = tintedCssOptics(base, source, { ...orange, strength: s }, backdrop, 1);
    const u = (1 - source.tintAlpha) * backdrop + source.tintAlpha * 1;
    const layer = tintShadeLayer(orange.color, u, 1);
    for (const index of [0, 1, 2] as const) {
      const material = srgbEncode(backdrop) * (1 - base.tintAlpha) + (base.tint[index] / 255) * base.tintAlpha;
      const twoLayers = material * (1 - s) + srgbEncode(layer[index]) * s;
      const oneLayer = srgbEncode(backdrop) * (1 - optics.tintAlpha) + (optics.tint[index] / 255) * optics.tintAlpha;
      expect(Math.abs(twoLayers - oneLayer)).toBeLessThan(1.5 / 255);
    }
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
    const host = hostOf({
      radii: [12, 12, 12, 12],
      optics,
      tint,
      policy: policy(),
    });
    expect(host["--vitrea-foreground"]).toBe(FOREGROUND_INK.dark);
  });

  it("takes the light token on a dark tint once the tint shows enough of itself to decide", () => {
    // At a partial strength a near-black layer over the white material still
    // leaves a bright surface whatever is behind it — or a mid one, depending
    // on the backdrop — and the bracket correctly declines to decide. At full
    // strength the layer is opaque (W10): the surface IS the dark tint, and the
    // ink is decided with no hint at all.
    const seed = [0.02, 0.02, 0.04] as const;
    const partial = tintedCssOptics(base, source, linearTint(glassTint(seed, 0.3)), 0.05, 1);
    expect(
      hostOf({
        radii: [12, 12, 12, 12],
        optics: partial,
        tint: glassTint(seed, 0.3),
        policy: policy(),
      })["--vitrea-foreground"],
    ).toContain("light-dark(");
    const full = tintedCssOptics(base, source, linearTint(glassTint(seed)), 0.05, 1);
    expect(
      hostOf({
        radii: [12, 12, 12, 12],
        optics: full,
        tint: glassTint(seed),
        policy: policy(),
      })["--vitrea-foreground"],
    ).toBe(FOREGROUND_INK.light);
  });

  it("leaves an untinted hintless surface on the scheme's own answer", () => {
    const host = hostOf({
      radii: [12, 12, 12, 12],
      optics: base,
      policy: policy(),
    });
    expect(host["--vitrea-foreground"]).toContain("light-dark(");
  });
});

describe("accessibility still wins", () => {
  const tint = glassTint([1, 0.584, 0]);
  const tinted = tintedCssOptics(base, source, orange, 0.2, 1);

  it("keeps the tint's colour while increased contrast lifts its occlusion", () => {
    // At full strength the layer is already opaque (W10), so the lift is read
    // at half strength, where the material still has headroom to lose.
    const tint = glassTint([1, 0.584, 0], 0.5);
    const tinted = tintedCssOptics(base, source, linearTint(tint), 0.2, 1);
    const nominal = {
      radii: [12, 12, 12, 12],
      optics: tinted,
      tint,
      policy: policy(),
    } as const satisfies CssTierSurface;
    const lifted = { ...nominal, policy: policy({ occlusion: "increased" }) };
    expect(Number(hostOf(lifted)["--vitrea-occlusion"])).toBeGreaterThan(
      Number(hostOf(nominal)["--vitrea-occlusion"]),
    );
    // The colour is the author's either way; only how much of it there is moved.
    // The tint itself is the overlay layer's `background-color` since W16 G1,
    // and the token beside it on the host is the same alpha published.
    expect(overlayOf(lifted)["background-color"]?.split(",").slice(0, 3)).toEqual(
      overlayOf(nominal)["background-color"]?.split(",").slice(0, 3),
    );
  });

  it("never overrides near-monochrome ink with a tint-derived level", () => {
    const host = hostOf({
      radii: [12, 12, 12, 12],
      optics: tinted,
      tint,
      policy: policy({ foreground: "near-monochrome" }),
    });
    expect(host["--vitrea-foreground"]).toBe("light-dark(#000, #fff)");
  });

  it("erases the tint entirely under forced colours, where there is no material", () => {
    // The one regime that keeps the whole material on the host: forced colours
    // tears the three created layers down rather than emptying them, so there is
    // no overlay to read a tint from and `Canvas` is the host's own background.
    const forced = {
      radii: [12, 12, 12, 12],
      optics: tinted,
      tint,
      policy: policy({ glass: "none" }),
    } as const satisfies CssTierSurface;
    const render = cssTierDeclarations(forced);
    expect(render.layers).toBeUndefined();
    expect(render.host["--vitrea-tint"]).toBe("Canvas");
    expect(render.host["background-color"]).toBe("Canvas");
    expect(render.host["--vitrea-foreground"]).toBe("CanvasText");
  });

  it("collapses the shade range, not the colour, when the ambient regime narrows", () => {
    // Over dark content the nominal regime shades the seed; with no regime grip
    // the layer is the author's colour flat. The hue never moves either way.
    const wide = tintedSourceOptics(source, orange, 0.0, tintToneAdaptation("nominal"));
    const narrow = tintedSourceOptics(source, orange, 0.0, tintToneAdaptation("none"));
    for (const index of [0, 1, 2] as const) {
      expect(narrow.tint[index]).toBeCloseTo(orange.color[index], 12);
    }
    expect(wide.tint[0]).toBeLessThan(narrow.tint[0]);
    expect(wide.tint[0] / orange.color[0]).toBeCloseTo(wide.tint[1] / orange.color[1], 10);
  });
});
