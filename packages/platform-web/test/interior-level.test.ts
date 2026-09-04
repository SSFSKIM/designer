/**
 * The interior level's derivation, pinned against the numbers the renderer's own
 * captures produced (W17 G1; charter Decision Log 2 (b)–(c), claims §5.74).
 *
 * Three things are asserted here and they are three different kinds of claim.
 *
 *  - **The alpha chain is the shader's.** The size law's occlusion enters the
 *    alpha before the W9 response solve, the inner shadow enters the pair after
 *    it, and the numbers those two produce are the ones W17 G0 recorded on the
 *    three W16 probe cells by rendering them. This is a pin against a
 *    measurement, so the constants are written out.
 *  - **The band's light is a derivation.** `X` comes from the profile's rim
 *    width, ambient alpha, specular exponent and gain and the surface's own box,
 *    through a co-area integral — never from a table of measured excesses, which
 *    the charter's K5 clause forbids. The pin is the derivation reproducing G0's
 *    own evaluation of it, and the residual against the RENDER is recorded in
 *    `interiorBandLight`'s doc comment rather than asserted here.
 *  - **The transfer is exact and representable.** Slope and intercept are the
 *    lerp's own coefficients, the intercept cannot go negative, and the composite
 *    they produce is the renderer's composite at every backdrop level rather than
 *    at one declared one.
 */

import { NOMINAL_ACCESSIBILITY_POLICY, glassTint } from "@vitreajs/vitrea";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import {
  cssTierDeclarations,
  cssTierFloorAlpha,
  cssTierTintTransfer,
  referenceFilterId,
  type CssTierEngineCapabilities,
  type CssTierInterior,
} from "../src/css-tier";
import type { MediaMatcher } from "../src/media-policy";
import { DEFAULT_HOST_SHAPE } from "../src/host";
import { createGlassRoot } from "../src/root";
import {
  MATERIAL_OPTICS,
  MATERIAL_SOURCE_INTERIOR_LIGHT,
  MATERIAL_SOURCE_OPTICS,
  MATERIAL_SOURCE_SIZE,
  adaptedSourceOptics,
  authorTintLayer,
  backdropToneAdaptation,
  cssTierTintTable,
  cssTintAlpha,
  cssTintFormAt,
  linearChainQuantumCodes,
  LINEAR_CHAIN_CODE_TOLERANCE,
  linearTint,
  occlusionAlphaUnderPolicy,
  innerShadowedSourceOptics,
  interiorBandLight,
  interiorShadowKeep,
  resolvedBackdropTone,
  resolvedBackdropToneResponse,
  sizeOcclusionAlphaAt,
  sizeThickness,
  sourceInteriorLight,
  toneRespondedSourceOptics,
  type InteriorSurfaceGeometry,
  type MaterialSourceOptics,
} from "../src/optics";

/** The sRGB encode, restated for the tests that read the page's own space. */
const encode = (l: number): number =>
  l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;

/** Rec. 709 luminance, the space every number below is in. */
const luma = (rgb: readonly [number, number, number]): number =>
  0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];

/**
 * The three W16 probe cells, at the boxes W17 G0 evaluated its model over — the
 * component's DECLARED box in CSS px rather than the host's measured border box,
 * which is two CSS px larger on each extent because the host carries a one-pixel
 * border for layout. The declared box is what the recorded numbers below were
 * produced from, so it is what a pin against them has to use; the runtime reads
 * the measured one, and the difference moves the size law's thickness on none of
 * these three spans.
 *
 * The checkerboard's own tone is one sample for all three — its linear mean is
 * exactly 0.5 by construction and its encoded mean decodes to 0.2140, which is
 * the response curve's input.
 */
const CHECKERBOARD_TONE = {
  rgb: [0.5, 0.5, 0.5] as [number, number, number],
  luminance: 0.21404114048223255,
  linearLuminance: 0.5,
};

const PROBES = [
  {
    cell: "checkerboard__rrect-md__rest",
    geometry: { widthCssPx: 160, heightCssPx: 96, radiusCssPx: 20, thicknessCssPx: 8 },
    // G0's `parts/analytic.json` and `parts/solve.json`, 1x light standard.
    shaderOrderAlpha: 0.48700000000000004,
    shaderOrderTintLuma: 0.8991049060110656,
    innerShadowKeep: 0.9964045039906037,
    bandLight: 0.004619103946700296,
  },
  {
    cell: "checkerboard__capsule-button__rest",
    geometry: { widthCssPx: 120, heightCssPx: 44, radiusCssPx: 22, thicknessCssPx: 8 },
    shaderOrderAlpha: 0.46249169921875,
    shaderOrderTintLuma: 0.877090561648483,
    innerShadowKeep: 0.996963419321641,
    bandLight: 0.009300152791914134,
  },
  {
    cell: "checkerboard__rrect-ml__rest",
    geometry: { widthCssPx: 240, heightCssPx: 128, radiusCssPx: 27, thicknessCssPx: 8 },
    shaderOrderAlpha: 0.48700000000000004,
    shaderOrderTintLuma: 0.8991049060110656,
    innerShadowKeep: 0.997296244989193,
    bandLight: 0.0033885124629982654,
  },
] as const;

/**
 * The chain `root.ts` runs, in the shader's order — the occlusion into the alpha
 * first, then the solve, then the collapse.
 *
 * Restated here rather than reached through `createGlassRoot` because the claim
 * is about the arithmetic and not about the DOM: the ordering test in
 * `root-lifecycle.test.ts` is the one that says the runtime runs this chain.
 */
function shaderOrderSource(
  geometry: InteriorSurfaceGeometry,
  spanPx: number,
): { source: MaterialSourceOptics; thickness: number } {
  const base = MATERIAL_SOURCE_OPTICS.regular;
  const thickness = sizeThickness(spanPx, MATERIAL_SOURCE_SIZE);
  const sized: MaterialSourceOptics = {
    ...base,
    tintAlpha: sizeOcclusionAlphaAt(base.tintAlpha, thickness, MATERIAL_SOURCE_SIZE),
  };
  const toneConstants = resolvedBackdropTone();
  const adaptation = backdropToneAdaptation(
    CHECKERBOARD_TONE.luminance,
    thickness,
    toneConstants,
  );
  const responded = toneRespondedSourceOptics(
    sized,
    CHECKERBOARD_TONE,
    thickness,
    adaptation,
    Math.min(1, Math.max(0, toneConstants.max)),
    resolvedBackdropToneResponse(),
  );
  void geometry;
  return {
    source: adaptedSourceOptics(responded, CHECKERBOARD_TONE.rgb, adaptation),
    thickness,
  };
}

describe("the interior level's alpha chain (W17 G1)", () => {
  it("reproduces the shader-order alpha and tint G0 recorded on the probe cells", () => {
    for (const probe of PROBES) {
      const span = Math.min(probe.geometry.widthCssPx, probe.geometry.heightCssPx);
      const { source } = shaderOrderSource(probe.geometry, span);
      expect(source.tintAlpha, probe.cell).toBeCloseTo(probe.shaderOrderAlpha, 12);
      expect(luma(source.tint), probe.cell).toBeCloseTo(probe.shaderOrderTintLuma, 12);
    }
  });

  it("puts the occlusion before the solve, and the two orders are not one number", () => {
    // The defect this pin exists for: solving at the unsized alpha and raising it
    // afterwards lands the composite's mean above the response the solve exists
    // to hit. `rrect-md` is the cell it was largest on among the probes, at
    // +0.0147 of the interior level (claims §5.74 §3).
    const probe = PROBES[0]!;
    const base = MATERIAL_SOURCE_OPTICS.regular;
    const thickness = sizeThickness(96, MATERIAL_SOURCE_SIZE);
    const toneConstants = resolvedBackdropTone();
    const adaptation = backdropToneAdaptation(
      CHECKERBOARD_TONE.luminance,
      thickness,
      toneConstants,
    );
    const solve = (source: MaterialSourceOptics): MaterialSourceOptics =>
      adaptedSourceOptics(
        toneRespondedSourceOptics(
          source,
          CHECKERBOARD_TONE,
          thickness,
          adaptation,
          Math.min(1, Math.max(0, toneConstants.max)),
          resolvedBackdropToneResponse(),
        ),
        CHECKERBOARD_TONE.rgb,
        adaptation,
      );
    const shaderOrder = solve({
      ...base,
      tintAlpha: sizeOcclusionAlphaAt(base.tintAlpha, thickness, MATERIAL_SOURCE_SIZE),
    });
    const tierOrder = solve(base);
    const composite = (source: MaterialSourceOptics, alpha: number): number =>
      (1 - alpha) * CHECKERBOARD_TONE.linearLuminance + alpha * luma(source.tint);

    expect(composite(shaderOrder, shaderOrder.tintAlpha), probe.cell).toBeCloseTo(0.6944, 4);
    // The tier's old order: solve at 0.46, then raise to 0.487.
    expect(
      composite(
        tierOrder,
        sizeOcclusionAlphaAt(tierOrder.tintAlpha, thickness, MATERIAL_SOURCE_SIZE),
      ),
    ).toBeCloseTo(0.7058, 4);
  });

  it("keeps the inner shadow as a pair rather than as a subtraction", () => {
    for (const probe of PROBES) {
      const span = Math.min(probe.geometry.widthCssPx, probe.geometry.heightCssPx);
      const { source, thickness } = shaderOrderSource(probe.geometry, span);
      const keep = interiorShadowKeep(
        MATERIAL_SOURCE_OPTICS.regular,
        probe.geometry,
        thickness,
        1,
      );
      /*
       * Within 5.5e−5 of G0's own evaluation, which is 4e−5 of the interior
       * level, and the difference is a reading rather than a correction. On the
       * capsule the two agree to 1e−15. On `rrect-md` they agree to 2e−10, the
       * co-area integral's second branch: past the corner's radius the inward
       * offset of a rounded rectangle is a plain rectangle whose perimeter falls
       * at a different rate, and the shadow's 20.8 CSS px depth reaches past that
       * cell's 20 px radius where G0's single-branch form did not. On `rrect-ml`
       * they differ by 5.5e−5, and the arithmetic says G0's evaluation ran on a
       * corner radius near 12 rather than the 27 the surface declares — the
       * spike's script read the LAST surface of the capture's report. The
       * geometry the runtime uses is the host's own, so the derivation stands and
       * the older number is recorded beside it rather than reproduced.
       */
      expect(Math.abs(keep - probe.innerShadowKeep), probe.cell).toBeLessThan(6e-5);

      // The identity the pair is built on: the shadowed composite is exactly the
      // keep factor times the unshadowed one, at every backdrop level.
      const shadowed = innerShadowedSourceOptics(source, keep);
      for (const backdrop of [0.05, 0.2, 0.5, 0.8]) {
        const plain = (1 - source.tintAlpha) * backdrop + source.tintAlpha * luma(source.tint);
        const withShadow =
          (1 - shadowed.tintAlpha) * backdrop + shadowed.tintAlpha * luma(shadowed.tint);
        expect(withShadow, `${probe.cell} at ${backdrop}`).toBeCloseTo(keep * plain, 12);
      }
    }
  });
});

describe("the band's derived light (W17 G1)", () => {
  it("derives X from the profile and the box, reproducing G0's evaluation", () => {
    for (const probe of PROBES) {
      const derived = interiorBandLight(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, 1);
      // Within 2.2e-5 of G0's, which used the same co-area weight without the
      // corner arcs' own shrinkage in the specular term.
      expect(derived, probe.cell).toBeCloseTo(probe.bandLight, 4);
      expect(derived, probe.cell).toBeGreaterThan(0);
    }
  });

  it("is largest where the band is the largest fraction of the interior", () => {
    // The band-fraction signature the attribution measured: the capsule's 44 px
    // span carries twice the thick spans' term, and `rrect-ml` the least of the
    // three. A derivation that did not reproduce the ORDER would be arithmetic
    // that happened to land on three numbers.
    const [md, capsule, ml] = PROBES;
    const at = (probe: (typeof PROBES)[number]): number =>
      interiorBandLight(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, 1);
    expect(at(capsule!)).toBeGreaterThan(at(md!));
    expect(at(md!)).toBeGreaterThan(at(ml!));
  });

  it("fades with the collapse, exactly as the renderer's own band does", () => {
    // A material that has taken its backdrop's tone has no lit edge to show, and
    // the reference agrees on a calibration cell rather than by inference. So
    // `present` scales the whole term and zeroes it outright.
    const probe = PROBES[0]!;
    const full = interiorBandLight(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, 1);
    expect(interiorBandLight(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, 0.5)).toBeCloseTo(
      full / 2,
      12,
    );
    expect(interiorBandLight(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, 0)).toBe(0);
  });

  it("reads the profile's own constants, patch included", () => {
    // A mirror that did not follow the document would put this tier on a band the
    // renderer is not drawing — K5's gap, reappearing through the patch.
    const probe = PROBES[0]!;
    const patched = { ...MATERIAL_SOURCE_OPTICS.regular, rimAlpha: 0.36, specularGain: 1.1 };
    expect(interiorBandLight(patched, probe.geometry, 1)).toBeCloseTo(
      2 * interiorBandLight(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, 1),
      12,
    );
    expect(sourceInteriorLight({ lensSizeGainMax: 4 }).shadowDepthGainMax).toBe(4);
    expect(sourceInteriorLight().lightDirection).toEqual(
      MATERIAL_SOURCE_INTERIOR_LIGHT.lightDirection,
    );
  });
});

describe("the tint's transfer (W17 G1, re-formed at Decision Log 4 (a))", () => {
  const interiorOf = (probe: (typeof PROBES)[number]): CssTierInterior => {
    const span = Math.min(probe.geometry.widthCssPx, probe.geometry.heightCssPx);
    const { source, thickness } = shaderOrderSource(probe.geometry, span);
    const shadowed = innerShadowedSourceOptics(
      source,
      interiorShadowKeep(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, thickness, 1),
    );
    return {
      tintAlpha: shadowed.tintAlpha,
      tint: [shadowed.tint[0], shadowed.tint[1], shadowed.tint[2]],
      addedLight: interiorBandLight(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, 1),
    };
  };
  const FLOOR = cssTierFloorAlpha(MATERIAL_OPTICS.regular);
  const FLOOR_ENCODED = [
    MATERIAL_OPTICS.regular.tint[0] / 255,
    MATERIAL_OPTICS.regular.tint[1] / 255,
    MATERIAL_OPTICS.regular.tint[2] / 255,
  ] as const;
  const transferOf = (probe: (typeof PROBES)[number]) =>
    cssTierTintTransfer(interiorOf(probe), FLOOR, FLOOR_ENCODED);

  it("names the floor rather than deriving one", () => {
    // Decision Log 4 (a): the floor is the tier's own existing constant — the
    // LEAST tint it draws on the shipped profile, which is the clear variant's
    // converted alpha, on the variant whose whole point is to be persistently
    // more transparent. "The surface always paints a real tint" is a statement
    // about the least it paints.
    expect(FLOOR).toBe(MATERIAL_OPTICS.clear.tintAlpha);
    expect(cssTierFloorAlpha(MATERIAL_OPTICS.clear)).toBe(MATERIAL_OPTICS.clear.tintAlpha);
    // One floor for both variants: it is the tier's minimum and not a per-variant
    // conversion, and everything the filter carries is amplified by 1/(1 − a3),
    // so the smallest alpha that satisfies the doctrine is the right one.
    expect(cssTierFloorAlpha(MATERIAL_OPTICS.regular)).toBe(FLOOR);
    // And it is never above the folded alpha, which is the ruling's
    // non-negativity condition: every fold between the profile and the composite
    // raises the source alpha, and the conversion is monotone in it.
    for (const probe of PROBES) {
      const folded = cssTintAlpha({
        ...MATERIAL_SOURCE_OPTICS.regular,
        tintAlpha: interiorOf(probe).tintAlpha,
      });
      expect(folded, probe.cell).toBeGreaterThanOrEqual(FLOOR);
    }
  });

  it("composites to the renderer's own level at every backdrop level, not one", () => {
    // The point the two-equation solve could not make and the affine could not
    // keep under an overlay: the page draws `E(F(b))·(1 − a3) + E(T)·a3`, and
    // that has to equal `E(M(b) + X)` at every `b` rather than at the group's own.
    for (const probe of PROBES) {
      const interior = interiorOf(probe);
      const transfer = transferOf(probe);
      const table = cssTierTintTable({
        tintAlpha: transfer.tintAlpha,
        tint: transfer.tint[1]!,
        addedLight: transfer.addedLight,
        floorAlpha: transfer.floorAlpha,
        floorEncoded: transfer.floorEncoded[1]!,
      });
      for (const backdrop of [0, 0.05, 0.2, 0.5, 0.8, 1]) {
        const rendered =
          (1 - interior.tintAlpha) * backdrop +
          interior.tintAlpha * interior.tint[1] +
          interior.addedLight;
        // The table as the engine reads it: piecewise linear over its points.
        const t = backdrop * (table.length - 1);
        const index = Math.min(table.length - 2, Math.floor(t));
        const drawn = table[index]! + (t - index) * (table[index + 1]! - table[index]!);
        const composited = encode(drawn) * (1 - FLOOR) + FLOOR_ENCODED[1] * FLOOR;
        expect(composited, `${probe.cell} at ${backdrop}`).toBeCloseTo(encode(rendered), 3);
      }
    }
  });

  it("samples enough points for the interpolation bound, and no more", () => {
    for (const probe of PROBES) {
      const transfer = transferOf(probe);
      const options = {
        tintAlpha: transfer.tintAlpha,
        tint: transfer.tint[1]!,
        addedLight: transfer.addedLight,
        floorAlpha: transfer.floorAlpha,
        floorEncoded: transfer.floorEncoded[1]!,
      };
      const table = cssTierTintTable(options);
      // The count comes from the bound and not from a chosen number: a looser
      // bound takes fewer points and a tighter one takes more.
      expect(cssTierTintTable(options, 1e-2).length, probe.cell).toBeLessThan(table.length);
      expect(cssTierTintTable(options, 1e-6).length, probe.cell).toBeGreaterThan(table.length);
      expect(table.length, probe.cell).toBeLessThanOrEqual(257);
    }
  });

  it("is monotone and non-negative, which is what a primitive may emit", () => {
    for (const probe of PROBES) {
      const transfer = transferOf(probe);
      for (const channel of [0, 1, 2] as const) {
        const table = cssTierTintTable({
          tintAlpha: transfer.tintAlpha,
          tint: transfer.tint[channel]!,
          addedLight: transfer.addedLight,
          floorAlpha: transfer.floorAlpha,
          floorEncoded: transfer.floorEncoded[channel]!,
        });
        expect(Math.min(...table), `${probe.cell} channel ${channel}`).toBeGreaterThanOrEqual(0);
        expect(Math.max(...table), `${probe.cell} channel ${channel}`).toBeLessThanOrEqual(1);
        for (let i = 1; i < table.length; i += 1) {
          expect(table[i]!, `${probe.cell} channel ${channel} at ${i}`).toBeGreaterThanOrEqual(
            table[i - 1]!,
          );
        }
      }
    }
  });

  it("names one definition per group, and the id carries no minus sign", () => {
    const ids = PROBES.map((probe) => referenceFilterId("p", 1.25, transferOf(probe)));
    // `rrect-md` and `rrect-ml` share an alpha and a tint and differ only in the
    // band's light, which is exactly the case an id keyed on the width alone
    // would have collapsed.
    expect(new Set(ids).size).toBe(3);
    for (const id of ids) expect(id).not.toContain("-t-");
  });
});

describe("the boundary the darks take (W17 G1, Decision Log 4 (c))", () => {
  it("derives the boundary from the chain's quantum against the page's", () => {
    // The linear-light chain holds eight bits IN LINEAR LIGHT, so its step is
    // 1/255 there and `E(L + 1/255) − E(L)` wide in the buffer the page keeps.
    expect(linearChainQuantumCodes(0)).toBeCloseTo(12.7, 1);
    expect(linearChainQuantumCodes(0.05)).toBeCloseTo(2.47, 2);
    expect(linearChainQuantumCodes(0.5)).toBeCloseTo(0.657, 3);
    // The tolerance is the page's own quantum, so the boundary is where the two
    // are equal — 0.2443 on the shipped transfer function.
    expect(LINEAR_CHAIN_CODE_TOLERANCE).toBe(1);
    expect(linearChainQuantumCodes(0.2443)).toBeCloseTo(1, 2);
    expect(cssTintFormAt(0.24)).toBe("encoded");
    expect(cssTintFormAt(0.25)).toBe("linear");
  });

  it("puts every light composite on the exact form and the dark scheme on E's", () => {
    // The bed's own levels: the light cells' composites sit at 0.62 to 0.98 and
    // the dark scheme's at 0.05 to 0.09, where the chain steps by two codes.
    for (const level of [0.62, 0.69, 0.7, 0.93, 0.98]) expect(cssTintFormAt(level)).toBe("linear");
    for (const level of [0.0037, 0.05, 0.09, 0.2]) expect(cssTintFormAt(level)).toBe("encoded");
  });
});

describe("what the tier declares with an interior composite (W17 G1)", () => {
  const CHROMIUM: CssTierEngineCapabilities = {
    referenceFilterInBackdrop: true,
    maskOnBackdropFilter: "yes",
  };
  const OTHER: CssTierEngineCapabilities = {
    referenceFilterInBackdrop: false,
    maskOnBackdropFilter: "no",
  };
  const probe = PROBES[0]!;
  const interior = ((): CssTierInterior => {
    const { source, thickness } = shaderOrderSource(probe.geometry, 96);
    const shadowed = innerShadowedSourceOptics(
      source,
      interiorShadowKeep(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, thickness, 1),
    );
    return {
      tintAlpha: shadowed.tintAlpha,
      tint: [shadowed.tint[0], shadowed.tint[1], shadowed.tint[2]],
      addedLight: interiorBandLight(MATERIAL_SOURCE_OPTICS.regular, probe.geometry, 1),
    };
  })();
  const base = {
    radii: [20, 20, 20, 20] as const,
    optics: MATERIAL_OPTICS.regular,
    policy: NOMINAL_ACCESSIBILITY_POLICY,
    spanPx: 96,
    extentsCssPx: [160, 96] as const,
    filterIdPrefix: "p",
  };

  it("keeps the floor on L3 and puts the remainder in the sharp filter", () => {
    const render = cssTierDeclarations({ ...base, engine: CHROMIUM, interior });
    expect(render.body.filter).toBe("reference-filter");
    expect(render.body.tintForm).toBe("linear");
    expect(render.layers?.sharp["backdrop-filter"]).toContain(
      referenceFilterId("p", render.body.sharpSigmaCssPx, render.body.tintTransfer),
    );
    /*
     * The contrast floor stays an ELEMENT paint (Decision Log 4 (a)): L3 keeps
     * the encoded overlay at the tier's own floor alpha, so a filter that does
     * not render leaves a surface rather than nothing — which is the doctrine
     * S1's undetectable failure class is written for, and which W17's first form
     * broke.
     */
    expect(render.layers?.overlay["background-color"]).toBe(
      `rgba(${MATERIAL_OPTICS.regular.tint.join(", ")}, ${String(
        Math.round(cssTierFloorAlpha(MATERIAL_OPTICS.regular) * 1000) / 1000,
      )})`,
    );
    // And L3 keeps the two things that are not the tint.
    expect(render.layers?.overlay["box-shadow"]).toContain("inset");
    expect(render.layers?.overlay["background-image"]).not.toBe("none");
    // The heavy step never carries the table: applying it at both layers would
    // apply it twice.
    expect(render.layers?.heavy["backdrop-filter"]).toBe(
      `url(#${referenceFilterId("p", render.body.heavyStepSigmaCssPx)})`,
    );
  });

  it("draws the encoded form where the chain's quantum is coarser than the page's", () => {
    // Decision Log 4 (c). A group whose composite is near black gets W16's
    // overlay, because a filter chain that cannot hold 12/255 is drawing a
    // different material rather than a more precise one.
    const dark: CssTierInterior = { tintAlpha: 0.95, tint: [0.04, 0.04, 0.04], addedLight: 0 };
    const render = cssTierDeclarations({
      ...base,
      engine: CHROMIUM,
      interior: dark,
      backdropLuminance: 0.02,
    });
    expect(render.body.tintForm).toBe("encoded");
    expect(render.body.tintTransfer).toBeUndefined();
    expect(render.layers?.overlay["background-color"]).toMatch(/^rgba\(/);
  });

  it("keeps the rgba overlay on an engine with no reference filter", () => {
    const render = cssTierDeclarations({ ...base, engine: OTHER, interior });
    expect(render.body.filter).toBe("blur");
    expect(render.body.tintTransfer).toBeUndefined();
    expect(render.layers?.overlay["background-color"]).toMatch(/^rgba\(/);
    // Byte-identical to the same surface with no interior declared at all: the
    // conformance row decides the form, and a composite the engine cannot carry
    // changes nothing about what it draws (contract X9).
    expect(render).toEqual(cssTierDeclarations({ ...base, engine: OTHER }));
  });

  it("draws the author's own layer over the tinted filter rather than the fold", () => {
    const tint = glassTint([1, 0.584, 0], 0.5);
    const authorLayer = authorTintLayer(
      MATERIAL_SOURCE_OPTICS.regular,
      linearTint(tint),
      0.5,
      1,
    )!;
    const render = cssTierDeclarations({
      ...base,
      engine: CHROMIUM,
      interior,
      tint,
      authorLayer,
    });
    // The author's opacity, not the fold's alpha: the material's half of the W10
    // fold is inside the filter, so what is left on L3 is the layer itself.
    expect(render.layers?.overlay["background-color"]).toBe(
      `rgba(${authorLayer.color.join(", ")}, ${String(authorLayer.strength)})`,
    );
  });

  it("carries the folded alpha under a preference, on the same transfer", () => {
    // The folds are not a second mechanism: reduced transparency and increased
    // contrast raise the SOURCE alpha, the transfer is the same expression of it,
    // and the intercept stays representable.
    for (const occlusion of ["increased", "opaque"] as const) {
      const lifted = {
        ...interior,
        tintAlpha: occlusionAlphaUnderPolicy(interior.tintAlpha, occlusion),
      };
      const floor = cssTierFloorAlpha(MATERIAL_OPTICS.regular);
      const encoded = [1, 1, 1] as const;
      const transfer = cssTierTintTransfer(lifted, floor, encoded);
      expect(transfer.tintAlpha, occlusion).toBeGreaterThan(interior.tintAlpha);
      const table = cssTierTintTable({
        tintAlpha: transfer.tintAlpha,
        tint: transfer.tint[1]!,
        addedLight: transfer.addedLight,
        floorAlpha: transfer.floorAlpha,
        floorEncoded: transfer.floorEncoded[1]!,
      });
      expect(Math.min(...table), occlusion).toBeGreaterThanOrEqual(0);
    }
  });
});

describe("the runtime runs the chain in the shader's order (W17 G1)", () => {
  class StubResizeObserver {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  }
  const matcher: MediaMatcher = () => ({
    matches: false,
    media: "(prefers-reduced-motion: reduce)",
    addEventListener: () => {},
    removeEventListener: () => {},
  });

  let restoreRect: (() => void) | undefined;
  beforeEach(() => {
    (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
    // jsdom cannot lay out, and the size law reads the host's measured border
    // box — so a box is stubbed rather than the law being asserted at span zero,
    // where the ordering this test exists for is inert by construction.
    const original = Element.prototype.getBoundingClientRect;
    Element.prototype.getBoundingClientRect = function rect(this: Element): DOMRect {
      return {
        x: 0, y: 0, top: 0, left: 0, right: 160, bottom: 96, width: 160, height: 96,
        toJSON: () => ({}),
      } as DOMRect;
    };
    restoreRect = () => {
      Element.prototype.getBoundingClientRect = original;
    };
  });
  afterEach(() => {
    restoreRect?.();
    restoreRect = undefined;
  });

  it("converts the sized alpha rather than sizing the converted one", () => {
    const container = document.createElement("div");
    document.body.append(container);
    const instance = createGlassRoot({
      container,
      autoStart: false,
      matcher,
      diagnosticSink: () => {},
    });
    const host = document.createElement("button");
    instance.plane("base").hostLayer.append(host);
    instance.registerGroup({ id: "g1" });
    instance.registerHost({ host, groupId: "g1", plane: "base" });
    instance.runFrame(0);

    const published = Number(host.style.getPropertyValue("--vitrea-occlusion"));
    const source = MATERIAL_SOURCE_OPTICS.regular;
    const thickness = sizeThickness(96, MATERIAL_SOURCE_SIZE);
    const sized = sizeOcclusionAlphaAt(source.tintAlpha, thickness, MATERIAL_SOURCE_SIZE);
    // The inner shadow is in the published pair too, on the host's own declared
    // shape: 12 CSS px radii and an 8 px thickness, which is what a host that
    // declared nothing registers with.
    const geometry: InteriorSurfaceGeometry = {
      widthCssPx: 160,
      heightCssPx: 96,
      radiusCssPx: DEFAULT_HOST_SHAPE.radii[0],
      thicknessCssPx: DEFAULT_HOST_SHAPE.thickness,
    };
    const shadowed = innerShadowedSourceOptics(
      { ...source, tintAlpha: sized },
      interiorShadowKeep(source, geometry, thickness, 1),
    );
    const emitted = (alpha: number): number => Math.round(alpha * 1000) / 1000;

    expect(published).toBe(emitted(cssTintAlpha(shadowed)));
    // And not the order the tier took until W17 G1, which is a different number
    // rather than a different route to the same one.
    expect(published).not.toBe(
      emitted(sizeOcclusionAlphaAt(cssTintAlpha(source), thickness, MATERIAL_SOURCE_SIZE)),
    );

    instance.destroy();
    container.remove();
  });
});
