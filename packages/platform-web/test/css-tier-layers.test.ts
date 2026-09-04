/**
 * The CSS tier's element model, its ramp mask and its cost collapse (W16 G1;
 * charter Decision Log 2 (a)–(c), claims §5.71).
 *
 * Split from `css-tier.test.ts` because the subject is different: that file holds
 * what the tier *says*, which is pure and needs no document, and this one holds
 * the DOM it says it into — three created children, a raster mask drawn from the
 * renderer's own k(u), and the reference filters the linear-light body blurs
 * through. What the two share is that neither is allowed to hold an optical
 * number of its own.
 */

import { describe, expect, it } from "vitest";

import {
  CSS_TIER_LAYER_ATTRIBUTE,
  createCssTierLayers,
  destroyCssTierLayers,
  filteredAreaDevicePx,
  maskShareAt,
  referenceFilterSigmas,
  roundedRectDepth,
} from "../src/css-tier-layers";
import {
  CSS_TIER_LAYER_ORDER,
  CSS_TIER_TWO_LAYER_AREA_BUDGET_DEVICE_PX,
  cssTierDeclarations,
  referenceFilterId,
  type CssTierEngineCapabilities,
  type CssTierSurface,
} from "../src/css-tier";
import {
  cssTierHeavyShareAt,
  scatterHeavyEffectiveRatioAtScale,
  MATERIAL_OPTICS,
  MATERIAL_SOURCE_SIZE,
} from "../src/optics";

import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";

const CHROMIUM: CssTierEngineCapabilities = {
  referenceFilterInBackdrop: true,
  maskOnBackdropFilter: "yes",
};

/**
 * One surface, with the size law's two inputs on by default because every W16
 * question is about a surface that has a span. `spanless()` is the other case and
 * builds the record without those keys at all rather than with `undefined` ones:
 * `exactOptionalPropertyTypes` treats "absent" and "declared undefined" as
 * different things, and so does this tier — an absent span is a caller that has
 * not measured the host, which is the honest default the size law stands down for.
 */
const surface = (overrides: Partial<CssTierSurface> = {}): CssTierSurface => ({
  radii: [12, 12, 12, 12],
  optics: MATERIAL_OPTICS.regular,
  policy: NOMINAL_ACCESSIBILITY_POLICY,
  spanPx: 96,
  extentsCssPx: [96, 96],
  engine: CHROMIUM,
  ...overrides,
});

const spanless = (): CssTierSurface => ({
  radii: [12, 12, 12, 12],
  optics: MATERIAL_OPTICS.regular,
  policy: NOMINAL_ACCESSIBILITY_POLICY,
  engine: CHROMIUM,
});

describe("the element model", () => {
  it("creates exactly three inert children, in paint order, and takes them all back", () => {
    const host = document.createElement("div");
    const layers = createCssTierLayers(host);

    const created = [...host.children] as HTMLElement[];
    expect(created).toHaveLength(3);
    // DOM order is paint order among children of the same negative `z-index`
    // band, and the declarations give each one a distinct one anyway — so the
    // order is stated twice and cannot drift.
    expect(created.map((child) => child.getAttribute(CSS_TIER_LAYER_ATTRIBUTE))).toEqual([
      ...CSS_TIER_LAYER_ORDER,
    ]);

    for (const child of created) {
      // Inert on every axis a user can reach. `focus.spec` and `hit-testing.spec`
      // hold the same rule end to end; this is the declaration that makes them
      // pass without either of them naming this tier.
      expect(child.getAttribute("aria-hidden")).toBe("true");
      expect(child.tagName).toBe("DIV");
      expect(child.hasAttribute("tabindex")).toBe(false);
      expect(child.hasAttribute("id")).toBe(false);
    }

    destroyCssTierLayers(host, layers);
    expect(host.children).toHaveLength(0);
  });

  it("declares each layer over the host's BORDER box, under its content, in order", () => {
    const render = cssTierDeclarations(surface());
    const layers = render.layers;
    expect(layers).toBeDefined();
    if (layers === undefined) return;

    const width = MATERIAL_OPTICS.regular.borderWidth;
    for (const name of CSS_TIER_LAYER_ORDER) {
      const declarations = layers[name];
      expect(declarations.position, name).toBe("absolute");
      // An absolutely positioned child's containing block is the host's PADDING
      // box, so a layer at `inset: 0` would leave the border area — where the rim
      // is drawn — uncovered.
      expect(declarations.inset, name).toBe(`-${String(width)}px`);
      expect(declarations["border-radius"], name).toBe("inherit");
      expect(declarations["pointer-events"], name).toBe("none");
      expect(Number(declarations["z-index"]), name).toBeLessThan(0);
    }

    // The order the material composes in: the sharp filter, the heavy one over
    // its output, then the tint and the rim over both.
    expect(Number(layers.sharp["z-index"])).toBeLessThan(Number(layers.heavy["z-index"]));
    expect(Number(layers.heavy["z-index"])).toBeLessThan(Number(layers.overlay["z-index"]));
  });

  it("takes the material off the host and leaves its geometry and its shadow there", () => {
    const render = cssTierDeclarations(surface());

    // Nothing of the body is on the host any more, and both filter spellings are
    // written at their inert value rather than dropped — a material that stops
    // writing one of its own declarations leaves whatever was last there.
    expect(render.host["backdrop-filter"]).toBe("none");
    expect(render.host["-webkit-backdrop-filter"]).toBe("none");
    expect(render.host["background-color"]).toBe("transparent");
    expect(render.host["background-image"]).toBe("none");
    // The stacking context the negative-`z-index` children need, and the only
    // root-forming property that is safe: `isolation: isolate` is not in Filter
    // Effects 2's backdrop-root trigger set, so the children's own filters stay
    // live.
    expect(render.host.isolation).toBe("isolate");
    // Layout stays. The border's WIDTH is the author's content box; only its
    // colour moves, because the host's border paints below the children.
    expect(render.host["border-style"]).toBe("solid");
    expect(render.host["border-width"]).toBe(`${String(MATERIAL_OPTICS.regular.borderWidth)}px`);
    expect(render.host["border-color"]).toBe("transparent");
    // And the outer shadow paints outside the border box and below the
    // background, where no clipped child can cover it.
    expect(render.host["box-shadow"]).toBeDefined();
  });

  it("paints the tint, the glow and the rim on the overlay, above both filters", () => {
    const render = cssTierDeclarations(
      surface({ tint: { color: [0.2, 0.47, 0.96], strength: 0.4 } }),
    );
    const overlay = render.layers?.overlay;
    expect(overlay?.["background-color"]).toMatch(/^rgba\(/);
    expect(overlay?.["background-image"]).toContain("radial-gradient");
    expect(overlay?.["box-shadow"]).toContain("inset");
  });

  it("draws no layer at all under forced colors, and keeps the host's own branch", () => {
    const render = cssTierDeclarations(
      surface({
        policy: {
          ...NOMINAL_ACCESSIBILITY_POLICY,
          material: { ...NOMINAL_ACCESSIBILITY_POLICY.material, glass: "none" },
        },
      }),
    );
    expect(render.layers).toBeUndefined();
    expect(render.host["background-color"]).toBe("Canvas");
    expect(render.host["border-color"]).toBe("CanvasText");
    expect(render.host["backdrop-filter"]).toBe("none");
    expect(render.body.form).toBe("collapsed");
  });
});

describe("the body's two widths", () => {
  it("composes the sharp layer's output to the heavy width in quadrature", () => {
    for (const dpr of [1, 1.5, 2, 3]) {
      const body = cssTierDeclarations(surface({ devicePixelRatio: dpr })).body;
      expect(body.form).toBe("two-layer");
      expect(
        Math.hypot(body.sharpSigmaCssPx, body.heavyStepSigmaCssPx),
        `dpr ${dpr}`,
      ).toBeCloseTo(body.heavySigmaCssPx, 12);
    }
  });

  it("reads both widths as device-pixel quantities through the live ratio", () => {
    const at1 = cssTierDeclarations(surface({ devicePixelRatio: 1 })).body;
    const at2 = cssTierDeclarations(surface({ devicePixelRatio: 2 })).body;
    /*
     * The sharp component is the profile's own σ in device px, so its CSS width
     * would halve at dpr 2 exactly but for the effective conversion, which is
     * itself per scale — 1.380 against 1.485 — so what is left after the halving
     * is the ratio of the two conversions. W13 Decision Log 5 refused the
     * halving for the single blur, on a measurement about projecting a MIX onto
     * one Gaussian; the component itself was never that number.
     */
    expect(at2.sharpSigmaCssPx).toBeCloseTo(
      (at1.sharpSigmaCssPx / 2)
        * (scatterHeavyEffectiveRatioAtScale(2) / scatterHeavyEffectiveRatioAtScale(1)),
      12,
    );
    expect(at2.sharpSigmaCssPx).toBeGreaterThan(at1.sharpSigmaCssPx / 2);
    // And the heavy component follows the renderer's own 2x gain rather than the
    // ratio alone, so it is NOT simply halved — which is the whole content of
    // the second scale.
    expect(at2.heavySigmaCssPx).not.toBeCloseTo(at1.heavySigmaCssPx / 2, 6);
  });

  it("publishes the single-σ projection as the token, and never a layer's width", () => {
    const render = cssTierDeclarations(surface({ devicePixelRatio: 2 }));
    // An app matching the material with its own `blur()` has to keep getting one
    // number, and the projection is what it always got: the 1x law's, unchanged
    // by the ratio, exactly as this tier drew before W16.
    expect(render.host["--vitrea-blur"]).toBe(
      `${String(Math.round(render.body.projectedSigmaCssPx * 100) / 100)}px`,
    );
    expect(render.body.projectedSigmaCssPx).toBe(
      cssTierDeclarations(surface({ devicePixelRatio: 1 })).body.projectedSigmaCssPx,
    );
  });
});

describe("the engine gates", () => {
  it("blurs through the linear-light reference filter only where the row says so", () => {
    const chromium = cssTierDeclarations(surface()).layers;
    expect(chromium?.sharp["backdrop-filter"]).toContain("url(#");
    expect(chromium?.sharp["backdrop-filter"]).toContain("saturate(");
    expect(chromium?.heavy["backdrop-filter"]).toContain("url(#");

    const unverified = cssTierDeclarations(
      surface({ engine: { referenceFilterInBackdrop: false, maskOnBackdropFilter: "no" } }),
    );
    // `blur()` operates on the page's ENCODED values where the reference's body
    // is linear in luminance, so this path carries the measured 2.4–2.8× residual
    // on the thick spans (claims §5.71 §2). It is a fidelity loss and not a broken
    // surface, which is why the fallback is this and not the single blur.
    expect(unverified.layers?.sharp["backdrop-filter"]).toContain("blur(");
    expect(unverified.body.filter).toBe("blur");
    expect(unverified.body.form).toBe("two-layer");
  });

  it("carries the ramp as a raster mask where one composes, and as one alpha where not", () => {
    const masked = cssTierDeclarations(surface());
    expect(masked.body.share).toBe("raster-mask");
    expect(masked.body.ramp).toBeDefined();
    // The mask carries the whole weight, so the layer's own alpha goes back to 1.
    expect(masked.layers?.heavy.opacity).toBe("1");
    expect(masked.layers?.heavy["mask-mode"]).toBe("alpha");

    for (const gate of ["no", "unverified"] as const) {
      const flat = cssTierDeclarations(
        surface({ engine: { referenceFilterInBackdrop: true, maskOnBackdropFilter: gate } }),
      );
      // The two components survive an unverified engine — sibling `opacity` on
      // `backdrop-filter` is ordinary CSS everywhere. The BAND is the only thing
      // the labeled pass unlocks.
      expect(flat.body.form, gate).toBe("two-layer");
      expect(flat.body.share, gate).toBe("flat");
      expect(flat.body.ramp, gate).toBeUndefined();
      expect(flat.layers?.heavy["mask-mode"], gate).toBeUndefined();
      expect(Number(flat.layers?.heavy.opacity), gate).toBeCloseTo(
        Math.round(flat.body.flatShare * 1000) / 1000,
        9,
      );
    }
  });

  it("names one filter id per width, and the same width twice names it once", () => {
    const body = cssTierDeclarations(surface()).body;
    const sigmas = referenceFilterSigmas(body);
    expect(sigmas).toEqual([body.sharpSigmaCssPx, body.heavyStepSigmaCssPx]);
    expect(referenceFilterId("p", 1.25)).toBe(referenceFilterId("p", 1.25));
    expect(referenceFilterId("p", 1.25)).not.toBe(referenceFilterId("p", 9.92));
    // Quantised the same way the declaration is, so the two cannot name
    // different numbers for the same layer.
    expect(referenceFilterId("p", 1.2501)).toBe(referenceFilterId("p", 1.25));
  });
});

describe("the cost collapse", () => {
  it("draws the two layers under the budget and today's single mixed σ above it", () => {
    const under = cssTierDeclarations(surface({ collapsed: false }));
    const over = cssTierDeclarations(surface({ collapsed: true }));

    expect(under.body.form).toBe("two-layer");
    expect(over.body.form).toBe("collapsed");
    // The degradation is a known form and not a third material: the single layer
    // draws exactly the projection this tier drew before W16.
    expect(over.body.sharpSigmaCssPx).toBe(over.body.projectedSigmaCssPx);
    expect(over.body.projectedSigmaCssPx).toBe(under.body.projectedSigmaCssPx);
    expect(over.body.heavyStepSigmaCssPx).toBe(0);
    expect(over.body.ramp).toBeUndefined();
    // And the second render surface really goes away — a layer at `opacity: 0`
    // would still cost the readback and the two-pass Gaussian the collapse exists
    // to buy back.
    expect(over.layers?.heavy.display).toBe("none");
    expect(over.layers?.heavy["backdrop-filter"]).toBeUndefined();
    expect(under.layers?.heavy.display).toBe("block");
  });

  it("counts one surface's filtered area at the budget's own boundary", () => {
    // The budget is the user's constant and the unit is filtered device px per
    // frame, counted once per surface — the same index G0's cost table is
    // written against.
    expect(filteredAreaDevicePx(160, 96, 1)).toBe(160 * 96);
    expect(filteredAreaDevicePx(160, 96, 2)).toBe(160 * 96 * 4);

    const budget = CSS_TIER_TWO_LAYER_AREA_BUDGET_DEVICE_PX;
    // 800 x 500 at dpr 1 is the budget exactly, and exactly at it is INSIDE it:
    // the rule is "while the root's total is under the budget", so the boundary
    // is a decision rather than a rounding.
    expect(filteredAreaDevicePx(800, 500, 1)).toBe(budget);
    expect(filteredAreaDevicePx(800, 500, 1) > budget).toBe(false);
    expect(filteredAreaDevicePx(801, 500, 1) > budget).toBe(true);
    // And the ratio is squared into it, which is what makes the same page break
    // the budget at 2x that clears it at 1x.
    expect(filteredAreaDevicePx(400, 250, 2)).toBe(budget);
  });

  it("collapses a surface with no span, and one whose frost is off, without being told to", () => {
    expect(cssTierDeclarations(spanless()).body.form).toBe("collapsed");

    const noFrost = cssTierDeclarations(
      surface({
        policy: {
          ...NOMINAL_ACCESSIBILITY_POLICY,
          material: { ...NOMINAL_ACCESSIBILITY_POLICY.material, frost: "none" },
        },
      }),
    );
    // A zero base σ makes the heavy step zero too, and a second render surface
    // that draws nothing is a cost with no material behind it.
    expect(noFrost.body.form).toBe("collapsed");
    expect(noFrost.body.sharpSigmaCssPx).toBe(0);
  });
});

describe("the ramp mask", () => {
  it("reconstructs the renderer's k(u) from the three numbers the body carries", () => {
    for (const dpr of [1, 2]) {
      for (const span of [44, 96, 160]) {
        const body = cssTierDeclarations(surface({ devicePixelRatio: dpr, spanPx: span })).body;
        const ramp = body.ramp;
        expect(ramp, `span ${span} at dpr ${dpr}`).toBeDefined();
        if (ramp === undefined) continue;
        for (const u of [0, 1, 4, 12, 40, 99, 200]) {
          expect(maskShareAt(u, ramp), `u ${u}, span ${span}, dpr ${dpr}`).toBeCloseTo(
            cssTierHeavyShareAt(u, dpr, 1, MATERIAL_SOURCE_SIZE, span),
            12,
          );
        }
      }
    }
  });

  it("measures depth from the contour, corners included", () => {
    // A 200 × 120 box with a radius of 24, in the same units the raster is drawn
    // in. The centre of a side is its half-extent deep; the corner's own centre
    // of curvature is the radius deep; and the contour itself is zero everywhere,
    // which is the property four gradients cannot have.
    const halfWidth = 100;
    const halfHeight = 60;
    const radius = 24;
    expect(roundedRectDepth(0, 0, halfWidth, halfHeight, radius)).toBeCloseTo(60, 9);
    expect(roundedRectDepth(halfWidth - 10, 0, halfWidth, halfHeight, radius)).toBeCloseTo(10, 9);
    expect(roundedRectDepth(0, halfHeight, halfWidth, halfHeight, radius)).toBeCloseTo(0, 9);
    // On the corner arc: the point at the centre of curvature is `radius` deep,
    // and the arc itself is on the contour.
    const cx = halfWidth - radius;
    const cy = halfHeight - radius;
    expect(roundedRectDepth(cx, cy, halfWidth, halfHeight, radius)).toBeCloseTo(radius, 9);
    const diagonal = radius / Math.SQRT2;
    expect(
      roundedRectDepth(cx + diagonal, cy + diagonal, halfWidth, halfHeight, radius),
    ).toBeCloseTo(0, 9);
    // Outside the silhouette the field is negative, which the mask clamps and the
    // layer's own `border-radius` clips.
    expect(roundedRectDepth(halfWidth + 5, 0, halfWidth, halfHeight, radius)).toBeLessThan(0);
  });

  it("holds the share at the deep value beyond the reach and at the contour value below it", () => {
    const body = cssTierDeclarations(surface({ spanPx: 160, extentsCssPx: [160, 160] })).body;
    const ramp = body.ramp;
    expect(ramp).toBeDefined();
    if (ramp === undefined) return;
    expect(maskShareAt(0, ramp)).toBeCloseTo(ramp.contourShare, 12);
    expect(maskShareAt(-50, ramp)).toBeCloseTo(ramp.contourShare, 12);
    expect(maskShareAt(ramp.reachDevicePx, ramp)).toBeCloseTo(ramp.deepShare, 12);
    expect(maskShareAt(ramp.reachDevicePx * 4, ramp)).toBeCloseTo(ramp.deepShare, 12);
  });
});
