/**
 * W42 G2 step 3, U5 — the CSS tier's derivation of the body law, its gates, and its filter's DOM
 * (G2's implementation-design.md §4, §5 as revised by §11's R5; test 7).
 *
 * What the filter COMPUTES is proven against the renderer's CPU references in
 * `packages/calibration/test/w42-css-filter-algebra.test.ts`, the one package that depends on
 * both tiers; the mirrors it derives from are pinned in `tier-coherence.test.ts`. This file holds
 * the rest: that nothing a page draws moves while any gate is shut, that the law replaces the
 * body exactly where every gate is open, what the derivation hands the filter, and the DOM the
 * filter becomes.
 */

import { describe, expect, it } from "vitest";

import {
  NOMINAL_ACCESSIBILITY_POLICY,
  resolveAccessibilityPolicy,
  type ResolvedAccessibilityPolicy,
} from "@vitreajs/vitrea";

import {
  cssTierDeclarations,
  cssTierBodyLawFilter,
  cssTierBodyLawStacked,
  bodyLawFilterId,
  type CssTierEngineCapabilities,
  type CssTierSurface,
} from "../src/css-tier";
import {
  createCssTierFilterDefs,
  cssTierFilterSpecs,
  referenceFilterSpecs,
} from "../src/css-tier-layers";
import { macos26MaterialProfileDocument, macos27MaterialProfileDocument } from "../src/material-document";
import {
  CSS_BODY_LAW_IDENTITY,
  MATERIAL_OPTICS,
  cssLandedToneInputs,
  cssTierBodyLaw,
  resolvedBackdropToneResponse,
  resolvedBodyLaw,
  type CssBodyLawLeaves,
} from "../src/optics";
import { CONFORMANCE_TABLE, CONSERVATIVE_ROW } from "../src/probe/conformance-table";
import type { RendererMaterialProfile } from "../src/renderer-bridge";

/** An engine that renders reference filters, with the law's row at each of its values. */
const REFERENCE: CssTierEngineCapabilities = {
  referenceFilterInBackdrop: true,
  maskOnBackdropFilter: "yes",
};
const MEASURED_YES: CssTierEngineCapabilities = { ...REFERENCE, bodyLawFilterInBackdrop: "yes" };

const ACTIVE_LIGHT = macos27MaterialProfileDocument.active.light.patch as RendererMaterialProfile;
const LAW_ON = {
  ...ACTIVE_LIGHT,
  bodyLawStrength: 1,
  bodyLawWidthUnit: 1,
  bodyLawEncodedAveraging: 1,
} as RendererMaterialProfile;

function surface(
  patch: RendererMaterialProfile | undefined,
  overrides: Partial<CssTierSurface> = {},
): CssTierSurface {
  return {
    radii: [22, 22, 22, 22],
    optics: MATERIAL_OPTICS.regular,
    policy: NOMINAL_ACCESSIBILITY_POLICY,
    spanPx: 96,
    extentsCssPx: [200, 96],
    devicePixelRatio: 2,
    materialization: 1,
    filterIdPrefix: "t",
    engine: MEASURED_YES,
    bodyLaw: {
      leaves: resolvedBodyLaw(patch),
      variant: "regular",
      ...(patch === undefined ? {} : { profile: patch }),
    },
    ...overrides,
  };
}

/** The same surface with no law input at all: what the tier drew before U5. */
function shipped(overrides: Partial<CssTierSurface> = {}): CssTierSurface {
  const { bodyLaw: _unused, ...rest } = surface(undefined, overrides);
  void _unused;
  return rest;
}

const policyWith = (flags: {
  readonly reducedTransparency?: boolean;
  readonly increasedContrast?: boolean;
  readonly forcedColors?: boolean;
}): ResolvedAccessibilityPolicy =>
  resolveAccessibilityPolicy({
    reducedTransparency: flags.reducedTransparency ?? false,
    reducedMotion: false,
    increasedContrast: flags.increasedContrast ?? false,
    forcedColors: flags.forcedColors ?? false,
    reducedTransparencySupported: true,
  });

describe("nothing a page draws moves while any gate is shut", () => {
  it("resolves every shipped document's every endpoint at the identity", () => {
    for (const document of [macos27MaterialProfileDocument, macos26MaterialProfileDocument]) {
      for (const scheme of ["light", "dark"] as const) {
        for (const endpoint of [document.active[scheme], document.receded?.[scheme]]) {
          expect(resolvedBodyLaw(endpoint?.patch)).toStrictEqual(CSS_BODY_LAW_IDENTITY);
        }
      }
    }
  });

  it("at the identity, declares byte for byte what the tier declared with no law input", () => {
    for (const engine of [REFERENCE, MEASURED_YES, { ...REFERENCE, referenceFilterInBackdrop: false }]) {
      for (const dpr of [1, 2]) {
        const overrides = { engine, devicePixelRatio: dpr };
        expect(cssTierDeclarations(surface(ACTIVE_LIGHT, overrides)))
          .toStrictEqual(cssTierDeclarations(shipped(overrides)));
      }
    }
  });

  it("keeps the law off on every engine whose row is not \"yes\", whatever the document says", () => {
    const engines: CssTierEngineCapabilities[] = [
      REFERENCE,
      { ...REFERENCE, bodyLawFilterInBackdrop: "unverified" },
      { ...REFERENCE, bodyLawFilterInBackdrop: "no" },
      // "yes" with nothing to carry the filter: the primary route needs a reference filter, and
      // the stacked route is derived but attached to no layer (u5_css_algebra.md §5).
      { ...REFERENCE, referenceFilterInBackdrop: false, bodyLawFilterInBackdrop: "yes" },
    ];
    for (const engine of engines) {
      const render = cssTierDeclarations(surface(LAW_ON, { engine }));
      expect(render.body.law).toBeUndefined();
      expect(render).toStrictEqual(cssTierDeclarations(shipped({ engine })));
    }
    const { engine: _unused, ...defaulted } = surface(LAW_ON);
    void _unused;
    expect(cssTierDeclarations(defaulted).body.law).toBeUndefined();
  });

  it("records the row as unverified on every engine the conformance table knows", () => {
    for (const row of [...CONFORMANCE_TABLE, CONSERVATIVE_ROW]) {
      expect(row.bodyLawFilterInBackdrop, `${row.family} ${String(row.minVersion)}`).toBe("unverified");
      expect(row.evidence.some((line) => line.includes("bodyLawFilterInBackdrop"))).toBe(true);
    }
  });
});

describe("where every gate is open, L1 carries the law's filter and nothing else (§5)", () => {
  it("names the filter on L1, hides L2 and paints no plate on L3", () => {
    const render = cssTierDeclarations(surface(LAW_ON));
    const law = render.body.law;
    expect(law).toBeDefined();
    if (law === undefined || render.layers === undefined) return;
    const id = bodyLawFilterId("t", law);
    expect(render.layers.sharp["backdrop-filter"]).toBe(`url(#${id})`);
    expect(render.layers.sharp["-webkit-backdrop-filter"]).toBe(`url(#${id})`);
    expect(render.layers.sharp["backdrop-filter"]).not.toContain("saturate");
    expect(render.layers.sharp.opacity).toBe("1");
    expect(render.layers.heavy.display).toBe("none");
    expect(render.layers.overlay["background-color"]).toBe("transparent");
    // The rim, the glow and the shadow stay where the shipped tier puts them.
    const plain = cssTierDeclarations(shipped());
    expect(render.layers.overlay["box-shadow"]).toBe(plain.layers?.overlay["box-shadow"]);
    expect(render.layers.overlay["background-image"]).toBe(plain.layers?.overlay["background-image"]);
    expect(render.host).toStrictEqual(plain.host);
    // The root builds the law's definition and none of the shipped body's.
    expect(cssTierFilterSpecs(render.body)).toStrictEqual([{ kind: "body-law", law }]);
    expect(referenceFilterSpecs(render.body)).toStrictEqual([]);
  });

  it("keeps the author's own layer on L3, at its own strength and presence", () => {
    const render = cssTierDeclarations(
      surface(LAW_ON, { authorLayer: { color: [200, 40, 10], strength: 0.5 }, materialization: 0.5 }),
    );
    expect(render.layers?.overlay["background-color"]).toBe("rgba(200, 40, 10, 0.25)");
    expect(render.layers?.sharp.opacity).toBe("0.5");
  });

  it("stands down under the accessibility fold, the variant, presence, the collapse and no span", () => {
    const off = [
      ["Reduce Transparency", { policy: policyWith({ reducedTransparency: true }) }],
      ["no presence", { materialization: 0 }],
      ["the cost collapse", { collapsed: true }],
    ] as const;
    for (const [name, overrides] of off) {
      expect(cssTierDeclarations(surface(LAW_ON, overrides)).body.law, name).toBeUndefined();
    }
    const clear = surface(LAW_ON);
    expect(cssTierDeclarations({ ...clear, bodyLaw: { ...clear.bodyLaw!, variant: "clear" } }).body.law)
      .toBeUndefined();
    const { spanPx: _span, ...spanless } = surface(LAW_ON);
    void _span;
    expect(cssTierDeclarations(spanless).body.law).toBeUndefined();
    // Forced colours is a different surface altogether, with no layers to carry anything.
    const forced = cssTierDeclarations(surface(LAW_ON, { policy: policyWith({ forcedColors: true }) }));
    expect(forced.layers).toBeUndefined();
    expect(forced.body.law).toBeUndefined();
    // Increase Contrast alone moves no occlusion and keeps the law (declaration `accessibility`).
    expect(cssTierDeclarations(surface(LAW_ON, { policy: policyWith({ increasedContrast: true }) }))
      .body.law).toBeDefined();
  });
});

/** The derivation for a patch on one geometry, at nominal policy. */
function derive(
  patch: RendererMaterialProfile,
  extents: readonly [number, number],
  dpr: number,
  leaves: CssBodyLawLeaves = resolvedBodyLaw(patch),
) {
  const span = Math.min(extents[0], extents[1]);
  return cssTierBodyLaw({
    leaves,
    strength: leaves.bodyLawStrength,
    widthCssPx: extents[0],
    heightCssPx: extents[1],
    radiusCssPx: Math.min(22, span / 2),
    devicePixelRatio: dpr,
    landed: cssLandedToneInputs(patch, "regular", span, NOMINAL_ACCESSIBILITY_POLICY.material, dpr),
    response: resolvedBackdropToneResponse(patch),
  });
}

describe("the derivation hands the filter the law's widths, knee and tone (§5)", () => {
  it("folds memo C's floor into both widths, in every width unit (D1)", () => {
    const receded = { ...LAW_ON, bodyLawPose: 1 } as RendererMaterialProfile;
    // s = 44, t = 0, a two-device-px texel: σ_F = 0.8 device px, 0.4 CSS px at 2x.
    const points = derive(receded, [160, 44], 2);
    expect(points.pose).toBe("receded");
    expect(points.edge).toBe("normalised");
    expect(points.floorSigmaCssPx).toBeCloseTo(0.4, 12);
    expect(points.narrowSigmaGradedCssPx).toStrictEqual([4, 4, 4]);
    expect(points.narrowSigmaCssPx).toBeCloseTo(Math.hypot(4, 0.4), 12);
    expect(points.wideSigmaCssPx).toBeCloseTo(Math.hypot(16, 0.4), 12);
    // Device px: half as wide in CSS px at 2x.
    const device = derive({ ...receded, bodyLawWidthUnit: 0 } as RendererMaterialProfile, [160, 44], 2);
    expect(device.narrowSigmaCssPx).toBeCloseTo(Math.hypot(2, 0.4), 12);
    expect(device.wideSigmaCssPx).toBeCloseTo(Math.hypot(8, 0.4), 12);
    // Texels on a large shape: f = 4 device px, t = 1, o = 0.8.
    const texels = derive({ ...receded, bodyLawWidthUnit: 2 } as RendererMaterialProfile, [320, 200], 2);
    expect(texels.texelDevicePx).toBe(4);
    expect(texels.floorSigmaCssPx).toBeCloseTo(0.8, 12);
    expect(texels.narrowSigmaCssPx).toBeCloseTo(Math.hypot(16, 0.8), 12);
    expect(texels.wideSigmaCssPx).toBeCloseTo(Math.hypot(32, 0.8), 12);
    // The edge swap trades the two modes.
    const swapped = derive({ ...receded, bodyLawEdgeSwap: 1 } as RendererMaterialProfile, [160, 44], 2);
    expect(swapped.edge).toBe("clamp");
    expect(derive(LAW_ON, [160, 96], 2).edge).toBe("clamp");
  });

  it("stands one width for the active graded term: the band-weighted mean over the body", () => {
    const law = derive(LAW_ON, [300, 160], 2);
    const [mean, least, greatest] = law.narrowSigmaGradedCssPx;
    // t = 1: o runs from 0.8 at the centre to 0.4 a point inside and 0.5 at the contour, so
    // σn = 2·5·o in points lies in [4, 8].
    expect(least).toBeGreaterThanOrEqual(4 - 1e-9);
    expect(greatest).toBeLessThanOrEqual(8 + 1e-9);
    expect(mean).toBeGreaterThan(least);
    expect(mean).toBeLessThan(greatest);
    // An independent, finer integral of the same weight over the same field.
    let sum = 0;
    let weights = 0;
    const cells = 600;
    for (let j = 0; j < cells; j++) {
      for (let i = 0; i < cells; i++) {
        const x = -150 + ((i + 0.5) / cells) * 300;
        const y = -80 + ((j + 0.5) / cells) * 160;
        const qx = Math.abs(x) - (150 - 22);
        const qy = Math.abs(y) - (80 - 22);
        const depth = 22 - (Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0));
        if (!(depth > 0)) continue;
        const u = Math.min(1, depth / 20);
        const weight = u * u * (3 - 2 * u);
        const o = depth >= 80 ? 0.8 : depth >= 1 ? 0.8 + (0.4 - 0.8) * ((80 - depth) / 79)
          : 0.4 + (0.5 - 0.4) * (1 - depth);
        sum += weight * 10 * o;
        weights += weight;
      }
    }
    expect(mean).toBeCloseTo(sum / weights, 1);
    expect(law.narrowSigmaCssPx).toBeCloseTo(Math.hypot(mean, law.floorSigmaCssPx), 12);
  });

  it("reads the tone by precedence, mixing a fractional strength over the tone below", () => {
    const tone = (extra: Record<string, unknown>) =>
      derive({ ...LAW_ON, ...extra } as RendererMaterialProfile, [200, 96], 2).tone;
    expect(tone({}).kind).toBe("landed");
    expect(tone({}).exactForm).toBe(false);
    expect(tone({ bodyE3Strength: 1 }).kind).toBe("e3");
    expect(tone({ bodyE3Strength: 1 }).gainArgument).toBe("wide");
    expect(tone({ bodyE3Strength: 1 }).below).toBeUndefined();
    expect(tone({ bodyE3Strength: 0.5 }).below?.tone.kind).toBe("landed");
    expect(tone({ bodyE3Strength: 1, bodyToneTableStrength: 1 }).kind).toBe("table");
    const mixed = tone({ bodyE3Strength: 1, bodyToneTableStrength: 0.25 });
    expect(mixed.kind).toBe("table");
    expect(mixed.below?.weight).toBe(0.25);
    expect(mixed.below?.tone.kind).toBe("e3");
    for (const t of [tone({}), tone({ bodyE3Strength: 1 }), tone({ bodyToneTableStrength: 1 })]) {
      for (const channel of t.neutral) expect(channel).toHaveLength(256);
      expect(t.gain).toHaveLength(256);
    }
    // At the identity table the tone is the identity map on the greys.
    const identity = tone({ bodyToneTableStrength: 1 });
    expect(identity.neutral[0][128]).toBeCloseTo(128 / 255, 6);
    expect(identity.gain.every((gain) => gain === 1)).toBe(true);
  });
});

describe("the filter's DOM (jsdom)", () => {
  const programs = [0, 1, 2].flatMap((knee) =>
    [1, -1].map((hinge) => cssTierBodyLawFilter(derive(
      { ...LAW_ON, bodyLawKnee: knee, bodyLawHinge: hinge, bodyE3Strength: 1,
        bodyToneTableStrength: 0.5 } as RendererMaterialProfile, [200, 96], 2))),
  );

  it("writes every primitive of the program, attribute for attribute", () => {
    for (const law of programs) {
      const parent = document.createElement("div");
      const defs = createCssTierFilterDefs(document, parent, "p");
      defs.ensure({ kind: "body-law", law });
      const filters = parent.querySelectorAll("filter");
      expect(filters).toHaveLength(1);
      const filter = filters[0]!;
      expect(filter.getAttribute("id")).toBe(bodyLawFilterId("p", law));
      expect([filter.getAttribute("x"), filter.getAttribute("y"), filter.getAttribute("width"),
        filter.getAttribute("height")]).toEqual(["0%", "0%", "100%", "100%"]);
      const children = [...filter.children];
      expect(children).toHaveLength(law.primitives.length);
      children.forEach((element, i) => {
        const primitive = law.primitives[i]!;
        expect(element.tagName).toBe(primitive.primitive);
        expect(element.getAttribute("result")).toBe(primitive.result);
        expect(element.getAttribute("in")).toBe(primitive.in);
        expect(element.getAttribute("color-interpolation-filters")).toBe(primitive.space);
        switch (primitive.primitive) {
          case "feGaussianBlur":
            expect(element.getAttribute("in")).toBe("SourceGraphic");
            expect(Number(element.getAttribute("stdDeviation"))).toBeCloseTo(primitive.stdDeviation, 6);
            expect(element.getAttribute("edgeMode")).toBe(primitive.edgeMode);
            break;
          case "feComposite":
            expect(element.getAttribute("operator")).toBe("arithmetic");
            expect(element.getAttribute("in2")).toBe(primitive.in2);
            expect(["k1", "k2", "k3", "k4"].map((k) => Number(element.getAttribute(k))))
              .toEqual([primitive.k1, primitive.k2, primitive.k3, primitive.k4]);
            break;
          case "feColorMatrix":
            expect(element.getAttribute("type")).toBe("matrix");
            expect(element.getAttribute("values")?.split(" ").map(Number)).toEqual([...primitive.values]);
            break;
          case "feComponentTransfer": {
            const functions = [...element.children].map((child) => child.tagName);
            const expected = (["r", "g", "b", "a"] as const)
              .filter((channel) => primitive[channel] !== undefined)
              .map((channel) => ({ r: "feFuncR", g: "feFuncG", b: "feFuncB", a: "feFuncA" })[channel]);
            expect(functions).toEqual(expected);
            for (const child of element.children) {
              const type = child.getAttribute("type");
              if (type === "table") {
                expect(child.getAttribute("tableValues")?.split(" ")).toHaveLength(256);
              } else {
                expect(type).toBe("linear");
                expect(child.hasAttribute("slope") && child.hasAttribute("intercept")).toBe(true);
              }
            }
            break;
          }
        }
      });
      // Every `in` names SourceGraphic or an earlier result, and the last result is the output.
      const seen = new Set<string>(["SourceGraphic"]);
      for (const primitive of law.primitives) {
        expect(seen.has(primitive.in), primitive.result).toBe(true);
        if (primitive.primitive === "feComposite") expect(seen.has(primitive.in2)).toBe(true);
        seen.add(primitive.result);
      }
      expect(law.primitives.at(-1)?.result).toBe(law.results.output);
      defs.dispose();
    }
  });

  it("makes every arithmetic write an opaque result, so no step composites on partial alpha", () => {
    for (const law of programs) {
      for (const primitive of law.primitives) {
        if (primitive.primitive !== "feComposite") continue;
        expect(primitive.k1 + primitive.k2 + primitive.k3 + primitive.k4, primitive.result)
          .toBeGreaterThanOrEqual(1 - 1e-9);
      }
      // No feBlend: on partial alpha it composites source-over (R5).
      const blends = law.primitives.filter((p) => p.primitive === ("feBlend" as never));
      expect(blends).toHaveLength(0);
    }
  });

  it("shares one definition between surfaces with one program, and sweeps it when unnamed", () => {
    const parent = document.createElement("div");
    const defs = createCssTierFilterDefs(document, parent, "p");
    const [a, b] = programs;
    defs.ensure({ kind: "body-law", law: a! });
    defs.ensure({ kind: "body-law", law: cssTierBodyLawFilter(a!.parameters) });
    expect(parent.querySelectorAll("filter")).toHaveLength(1);
    defs.sweep();
    defs.ensure({ kind: "body-law", law: b! });
    defs.sweep();
    const ids = [...parent.querySelectorAll("filter")].map((filter) => filter.getAttribute("id"));
    expect(ids).toEqual([bodyLawFilterId("p", b!)]);
    defs.dispose();
  });
});

describe("the stacked approximation's layers (§5)", () => {
  it("declares C, the hinge at opacity λ, the Normal fill at w and the tone's affine", () => {
    const law = derive({ ...LAW_ON, bodyLawLambda: 1.3, bodyLawHinge: -1 } as RendererMaterialProfile,
      [200, 96], 2);
    const layers = cssTierBodyLawStacked(law, 0.5);
    expect(layers.map((layer) => layer.role)).toEqual(["narrow", "hinge", "normal", "tone"]);
    const [narrow, hinge, normal, tone] = layers.map((layer) => layer.declarations);
    const step = Math.sqrt(law.wideSigmaCssPx ** 2 - law.narrowSigmaCssPx ** 2);
    const px = (value: number): string => `${String(Math.round(value * 100) / 100)}px`;
    expect(narrow!["backdrop-filter"]).toBe(`blur(${px(law.narrowSigmaCssPx)})`);
    expect(hinge!["backdrop-filter"]).toBe(`blur(${px(step)})`);
    expect(hinge!["mix-blend-mode"]).toBe("darken");
    // λ above 1 is clamped by `opacity`, one of the route's named approximations.
    expect(hinge!.opacity).toBe("1");
    expect(normal!["mix-blend-mode"]).toBe("normal");
    expect(normal!.opacity).toBe("0.5");
    expect(tone!["backdrop-filter"]).toMatch(/^(contrast|brightness)\(/);
  });
});
