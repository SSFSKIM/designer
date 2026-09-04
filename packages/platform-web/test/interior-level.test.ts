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
  cssTintAlpha,
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

describe("the tint's transfer (W17 G1)", () => {
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

  it("is the lerp's own coefficients and nothing solved", () => {
    for (const probe of PROBES) {
      const interior = interiorOf(probe);
      const transfer = cssTierTintTransfer(interior);
      expect(transfer.slope, probe.cell).toBeCloseTo(1 - interior.tintAlpha, 12);
      for (const channel of [0, 1, 2] as const) {
        expect(transfer.intercept[channel], `${probe.cell} channel ${channel}`).toBeCloseTo(
          interior.tintAlpha * interior.tint[channel] + interior.addedLight,
          12,
        );
      }
    }
  });

  it("reproduces the renderer's composite at every backdrop level, not one", () => {
    // The point the two-equation solve could not make: matching value and slope
    // at the group's own level does not match a mean over a cell whose filtered
    // backdrop has a standard deviation of 0.39 to 0.42 (claims §5.74 §5). An
    // affine has no such residual — it is the same function.
    for (const probe of PROBES) {
      const interior = interiorOf(probe);
      const transfer = cssTierTintTransfer(interior);
      for (const backdrop of [0, 0.05, 0.2, 0.5, 0.8, 1]) {
        const rendered =
          (1 - interior.tintAlpha) * backdrop +
          interior.tintAlpha * interior.tint[1] +
          interior.addedLight;
        expect(
          transfer.slope * backdrop + transfer.intercept[1],
          `${probe.cell} at ${backdrop}`,
        ).toBeCloseTo(rendered, 12);
      }
    }
  });

  it("cannot emit a negative intercept, which is what makes it representable", () => {
    // Filter Effects clamps a primitive's result to the allowed range, so a
    // `type="linear"` transfer cannot carry a negative intercept however negative
    // it is written: the chartered two-equation solve's was −0.19 and clipped
    // 29 % of a checkerboard's filtered backdrop at dpr 1 (claims §5.74 §5). The
    // lerp's intercept is a sum of non-negative quantities, and the extremes say
    // so rather than the argument.
    for (const interior of [
      { tintAlpha: 0, tint: [0, 0, 0] as const, addedLight: 0 },
      { tintAlpha: 1, tint: [1, 1, 1] as const, addedLight: 0.1 },
      { tintAlpha: 0.5, tint: [-1, -1, -1] as const, addedLight: -1 },
    ]) {
      const transfer = cssTierTintTransfer(interior);
      expect(transfer.slope).toBeGreaterThanOrEqual(0);
      for (const channel of transfer.intercept) expect(channel).toBeGreaterThanOrEqual(0);
    }
  });

  it("names one definition per group, and the id carries no minus sign", () => {
    const ids = PROBES.map((probe) =>
      referenceFilterId("p", 1.25, cssTierTintTransfer(interiorOf(probe))),
    );
    // `rrect-md` and `rrect-ml` share an alpha and a tint and differ only in the
    // band's light, which is exactly the case an id keyed on σ alone would have
    // collapsed.
    expect(new Set(ids).size).toBe(3);
    for (const id of ids) expect(id).not.toContain("-t-");
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

  it("moves the tint into the sharp filter and leaves L3 without one", () => {
    const render = cssTierDeclarations({ ...base, engine: CHROMIUM, interior });
    expect(render.body.filter).toBe("reference-filter");
    expect(render.body.tintTransfer).toEqual(cssTierTintTransfer(interior));
    expect(render.layers?.sharp["backdrop-filter"]).toContain(
      referenceFilterId("p", render.body.sharpSigmaCssPx, render.body.tintTransfer),
    );
    // The tint is drawn once, in linear light, inside the filter — so the layer
    // that used to carry it carries nothing of the material's colour.
    expect(render.layers?.overlay["background-color"]).toBe("transparent");
    // And L3 keeps the two things that are not the tint.
    expect(render.layers?.overlay["box-shadow"]).toContain("inset");
    expect(render.layers?.overlay["background-image"]).not.toBe("none");
    // The heavy step never carries the affine: applying it at both layers would
    // apply it twice.
    expect(render.layers?.heavy["backdrop-filter"]).toBe(
      `url(#${referenceFilterId("p", render.body.heavyStepSigmaCssPx)})`,
    );
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
      const transfer = cssTierTintTransfer(lifted);
      expect(transfer.slope, occlusion).toBeLessThan(cssTierTintTransfer(interior).slope);
      for (const channel of transfer.intercept) {
        expect(channel, occlusion).toBeGreaterThanOrEqual(0);
      }
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
