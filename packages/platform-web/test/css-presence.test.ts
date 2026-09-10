/**
 * The CSS tier at a presence — `materialization` on the tier most visitors get
 * (W27d; wave §Presence, not alpha; contract X6).
 *
 * Four kinds of claim are asserted here and they are not interchangeable.
 *
 *  - **The endpoints.** At 1 the tier writes exactly the declarations it wrote
 *    before the channel existed, so the calibrated bed cannot move by a bit; at
 *    0 it writes no material at all — no filter, no tint, no rim, no glow and no
 *    shadow on any carrier — which is what `Glass.identity` means.
 *  - **X6 itself.** No `opacity` is ever written on the host, at any presence
 *    and under any regime. A sub-1 opacity there forms a Backdrop Root and takes
 *    the group's proxy sampling with it, which is the whole reason presence is
 *    a material scalar rather than a fade.
 *  - **The mechanism's cost.** The reference-filter definitions are named by
 *    their width and by the tint table they carry, so a presence that reached
 *    either would rebuild a `<filter>` and re-solve a table every frame of every
 *    transit. The specs a body asks for are pinned presence-invariant.
 *  - **The transit.** A driver writing the material every frame gets no
 *    transitions to chase, on the host or on any of the three layers.
 */

import { NOMINAL_ACCESSIBILITY_POLICY, resolveAccessibilityPolicy } from "@vitreajs/vitrea";
import { describe, expect, it, vi } from "vitest";

/*
 * The one thing a following width must not cost is the table solve, so the
 * solver is counted here. Everything else in this module is the real one: the
 * factory delegates, and the mock exists to make a call observable rather than
 * to change an answer.
 */
vi.mock("../src/optics", async (importOriginal) => {
  const actual = (await importOriginal()) as Record<string, unknown>;
  const solve = actual.cssTierTintTable as typeof cssTierTintTable;
  return { ...actual, cssTierTintTable: vi.fn(solve) };
});

import {
  cssTierDeclarations,
  cssTierFloorAlpha,
  foregroundInk,
  referenceFilterId,
  type CssTierEngineCapabilities,
  type CssTierInterior,
  type CssTierRender,
  type CssTierSurface,
  type StyleDeclarations,
} from "../src/css-tier";
import { createCssTierFilterDefs, referenceFilterSpecs } from "../src/css-tier-layers";
import { cssTierTintTable, MATERIAL_OPTICS } from "../src/optics";

const CHROMIUM: CssTierEngineCapabilities = {
  referenceFilterInBackdrop: true,
  maskOnBackdropFilter: "yes",
};

/** The plain surface of `css-tier.test.ts` — no span, no engine, no interior. */
const plain: CssTierSurface = {
  radii: [22, 22, 22, 22],
  optics: MATERIAL_OPTICS.regular,
  policy: NOMINAL_ACCESSIBILITY_POLICY,
};

/** A measured surface on the engine that draws the tier's fidelity form. */
const measured: CssTierSurface = {
  ...plain,
  radii: [20, 20, 20, 20],
  spanPx: 96,
  extentsCssPx: [160, 96],
  devicePixelRatio: 2,
  engine: CHROMIUM,
  filterIdPrefix: "p",
  backdropLuminance: 0.42,
};

/**
 * An interior composite bright enough that the linear chain carries it — the
 * form assertions below name it, so a change of form is a failure here rather
 * than a silently different test.
 */
const interior: CssTierInterior = { tintAlpha: 0.66, tint: [0.86, 0.86, 0.86], addedLight: 0.02 };

/** The same surface with the tint inside the sharp filter. */
const linear: CssTierSurface = { ...measured, interior };

const forcedColors: CssTierSurface = {
  ...plain,
  policy: resolveAccessibilityPolicy({
    reducedTransparency: false,
    reducedMotion: false,
    increasedContrast: false,
    forcedColors: true,
    reducedTransparencySupported: true,
  }),
};

const at = (surface: CssTierSurface, materialization: number): CssTierRender =>
  cssTierDeclarations({ ...surface, materialization });

const layersOf = (render: CssTierRender): Readonly<Record<string, StyleDeclarations>> => {
  const { layers } = render;
  if (layers === undefined) throw new Error("the tier created no layers for this surface");
  return layers;
};

/**
 * The render without L1's weight — the one declaration a declared presence adds
 * to what the tier wrote before the channel existed.
 */
const withoutSharpWeight = (render: CssTierRender): CssTierRender => {
  const { layers } = render;
  if (layers === undefined) return render;
  const { opacity, ...sharp } = layers.sharp;
  void opacity;
  return { ...render, layers: { ...layers, sharp } };
};

/** The alpha of an `rgba()` declaration — the channel every presence term lands in. */
const alphaOf = (declaration: string): number => {
  const match = /rgba\([^)]*?,\s*([\d.]+)\)/.exec(declaration);
  if (match === null) throw new Error(`no rgba alpha in ${declaration}`);
  return Number(match[1]);
};

const PRESENCES = [0, 0.2, 0.35, 0.5, 0.75, 0.9, 1] as const;

describe("presence at the endpoints", () => {
  it("writes exactly the resting declarations at full presence", () => {
    // The bed is calibrated at presence 1, and every term is a multiplication
    // whose identity is 1 — so this is a bit-for-bit claim rather than a
    // tolerance, on every form the tier draws. L1's weight is the one
    // declaration the channel adds, and at 1 it is inert.
    for (const surface of [plain, measured, linear, forcedColors]) {
      const full = cssTierDeclarations({ ...surface, materialization: 1 });
      expect(full.layers?.sharp.opacity).toBe(surface === forcedColors ? undefined : "1");
      expect(withoutSharpWeight(full)).toEqual(cssTierDeclarations(surface));
      expect(cssTierDeclarations({ ...surface, driven: false })).toEqual(
        cssTierDeclarations(surface),
      );
    }
  });

  it("writes no weight at all for a caller that declares no presence", () => {
    // The rule `spanPx` already follows: a caller that has never heard of the
    // channel keeps the declarations this tier wrote before it existed, which is
    // what lets W19's recorded pre-fold declarations still compare.
    for (const surface of [plain, measured, linear]) {
      expect(layersOf(cssTierDeclarations(surface)).sharp!.opacity).toBeUndefined();
    }
  });

  it("clamps a presence outside the range rather than refusing it", () => {
    // The channel is read from a custom property an app can write and driven by
    // a kernel that can overshoot; a surface that vanished because a driver
    // ended at 1.0000001 would be a failure this function can simply not have.
    expect(at(linear, 1.5)).toEqual(at(linear, 1));
    expect(at(linear, -0.5)).toEqual(at(linear, 0));
  });

  it("draws no glass at all at zero presence", () => {
    const render = at(linear, 0);
    const layers = layersOf(render);

    // The body: no filter and no heavy layer, rather than a body drawn at zero
    // weight — an invisible `blur()` still costs a render surface and a pass.
    expect(layers.sharp!["backdrop-filter"]).toBe("none");
    expect(layers.sharp!["-webkit-backdrop-filter"]).toBe("none");
    expect(layers.heavy!.display).toBe("none");
    expect(render.body.form).toBe("collapsed");
    expect(render.body.sharpSigmaCssPx).toBe(0);
    expect(render.body.heavySigmaCssPx).toBe(0);
    expect(render.body.flatShare).toBe(0);
    expect(render.body.projectedSigmaCssPx).toBe(0);
    expect(render.body.tintTransfer).toBeUndefined();
    expect(render.body.ramp).toBeUndefined();

    // L3: no tint, no press glow, no rim and no shadow.
    expect(alphaOf(layers.overlay!["background-color"]!)).toBe(0);
    expect(layers.overlay!["background-image"]).toBe("none");
    expect(layers.overlay!["box-shadow"]).toBe("none");

    // The host: its own shadow gone, its tokens reading the nothing it draws,
    // and the geometry — which is layout — exactly where it was.
    expect(render.host["box-shadow"]).toBe("none");
    expect(render.host["--vitrea-occlusion"]).toBe("0");
    expect(render.host["--vitrea-blur"]).toBe("0px");
    expect(alphaOf(render.host["--vitrea-tint"]!)).toBe(0);
    expect(render.host["border-width"]).toBe(cssTierDeclarations(linear).host["border-width"]);
    expect(render.host["border-radius"]).toBe(cssTierDeclarations(linear).host["border-radius"]);
  });

  it("returns no outer shadow to any carrier at zero presence", () => {
    // Carrier B paints a member's shadow from a different element, so the
    // resolved string is the only thing that can carry the presence there — a
    // group container drawing a full shadow for an absent member is the failure
    // this pins.
    for (const shadowCarrier of ["layer", "host", "group"] as const) {
      const render = at({ ...measured, shadowCarrier }, 0);
      expect(render.outerShadow, shadowCarrier).toBe("none");
      expect(render.host["box-shadow"], shadowCarrier).toBe("none");
      expect(layersOf(render).overlay!["box-shadow"], shadowCarrier).toBe("none");
    }
  });

  it("costs a root no filter definitions at zero presence", () => {
    expect(referenceFilterSpecs(at(linear, 0).body)).toEqual([]);
    expect(referenceFilterSpecs(cssTierDeclarations(linear).body).length).toBeGreaterThan(0);
  });
});

describe("presence never touches an element's opacity (contract X6)", () => {
  it("writes no opacity on the host at any presence or under any regime", () => {
    for (const surface of [plain, measured, linear, forcedColors]) {
      for (const presence of PRESENCES) {
        const render = at(surface, presence);
        expect(render.host.opacity).toBeUndefined();
        expect(render.host.filter).toBeUndefined();
        expect(render.host["mix-blend-mode"]).toBeUndefined();
      }
    }
  });

  it("carries the body's presence on the two filtered layers instead", () => {
    // The layers are the host's own children, so an opacity there is a backdrop
    // root for descendants they do not have — and it is already this tier's
    // carrier for a mix weight (L2's flat share).
    for (const presence of PRESENCES) {
      const layers = layersOf(at(measured, presence));
      expect(Number(layers.sharp!.opacity), `sharp at ${presence}`).toBeCloseTo(presence, 3);
      if (presence > 0) {
        // The mask carries the share on this engine, so the layer's own opacity
        // is the presence and the product is the mask's alpha times it.
        expect(Number(layers.heavy!.opacity), `heavy at ${presence}`).toBeCloseTo(presence, 3);
      }
    }
  });

  it("scales the flat share where the engine cannot compose a mask", () => {
    const flat: CssTierSurface = {
      ...measured,
      engine: { referenceFilterInBackdrop: true, maskOnBackdropFilter: "no" },
    };
    const full = Number(layersOf(cssTierDeclarations(flat)).heavy!.opacity);
    expect(full).toBeGreaterThan(0);
    expect(Number(layersOf(at(flat, 0.5)).heavy!.opacity)).toBeCloseTo(full * 0.5, 2);
  });
});

describe("what a presence scales", () => {
  it("moves every optical carrier monotonically and lands both endpoints", () => {
    const read = (presence: number) => {
      const render = at(measured, presence);
      const layers = layersOf(render);
      const shadow = render.outerShadow;
      return {
        body: Number(layers.sharp!.opacity),
        tint: alphaOf(layers.overlay!["background-color"]!),
        rim: layers.overlay!["box-shadow"] === "none" ? 0 : alphaOf(layers.overlay!["box-shadow"]!),
        shadow: shadow === "none" ? 0 : alphaOf(shadow),
        occlusion: Number(render.host["--vitrea-occlusion"]),
      };
    };
    const zero = read(0);
    expect(zero).toEqual({ body: 0, tint: 0, rim: 0, shadow: 0, occlusion: 0 });

    let previous = zero;
    for (const presence of PRESENCES.slice(1)) {
      const current = read(presence);
      for (const key of ["body", "tint", "rim", "shadow", "occlusion"] as const) {
        expect(current[key], `${key} at ${presence}`).toBeGreaterThanOrEqual(previous[key]);
      }
      previous = current;
    }
    const full = read(1);
    expect(full.tint).toBeGreaterThan(0);
    expect(full.rim).toBeGreaterThan(0);
    expect(full.shadow).toBeGreaterThan(0);
  });

  it("scales the press glow with the material it lights", () => {
    // The channel stays a `var()` so the declarations remain frame-invariant;
    // what the presence moves is the gain each stop multiplies it by.
    const glowAt = (presence: number): string =>
      layersOf(at(measured, presence)).overlay!["background-image"]!;
    const full = glowAt(1);
    const half = glowAt(0.5);
    expect(full).toContain("--vitrea-glow");
    expect(half).toContain("--vitrea-glow");
    const factor = (declaration: string): number =>
      Number(/--vitrea-glow, 0\) \* ([\d.]+)\)/.exec(declaration)?.[1] ?? Number.NaN);
    expect(factor(half)).toBeCloseTo(factor(full) * 0.5, 4);
    expect(glowAt(0)).toBe("none");
  });

  it("scales the author's tint strength and never its colour", () => {
    const authorLayer = { color: [255, 149, 0] as const, strength: 0.4 };
    const tinted = { ...linear, authorLayer };
    expect(cssTierDeclarations(tinted).body.tintForm).toBe("linear");
    const overlayAt = (presence: number): string =>
      layersOf(at(tinted, presence)).overlay!["background-color"]!;
    expect(overlayAt(1)).toBe("rgba(255, 149, 0, 0.4)");
    expect(overlayAt(0.5)).toBe("rgba(255, 149, 0, 0.2)");
    expect(alphaOf(overlayAt(0))).toBe(0);
  });

  it("decides the ink against the material the surface is actually drawing", () => {
    // At zero presence the reader is looking at the backdrop, so the ink has to
    // follow the backdrop rather than the material that is no longer there.
    const overDark = at({ ...plain, backdropLuminance: 0.02 }, 0);
    const overLight = at({ ...plain, backdropLuminance: 0.9 }, 0);
    expect(overDark.host["--vitrea-foreground"]).toBe(
      foregroundInk({ policy: NOMINAL_ACCESSIBILITY_POLICY, level: 0 }),
    );
    expect(overLight.host["--vitrea-foreground"]).toBe(
      foregroundInk({ policy: NOMINAL_ACCESSIBILITY_POLICY, level: 1 }),
    );
    expect(overDark.host["--vitrea-foreground"]).not.toBe(overLight.host["--vitrea-foreground"]);
  });
});

describe("the presence and the reference filter", () => {
  it("scales every width the body draws with, and the token that publishes one", () => {
    // The light bending is what a materializing surface has less of, and each of
    // these is derived from the profile's one σ through a function linear in it
    // — so one factor moves all four and no second law is written.
    const resting = cssTierDeclarations(measured).body;
    expect(resting.form).toBe("two-layer");
    for (const presence of [0.2, 0.5, 0.9]) {
      const body = at(measured, presence).body;
      expect(body.sharpSigmaCssPx, `sharp at ${presence}`).toBeCloseTo(
        resting.sharpSigmaCssPx * presence,
        6,
      );
      expect(body.heavySigmaCssPx, `heavy at ${presence}`).toBeCloseTo(
        resting.heavySigmaCssPx * presence,
        6,
      );
      expect(body.heavyStepSigmaCssPx, `step at ${presence}`).toBeCloseTo(
        resting.heavyStepSigmaCssPx * presence,
        6,
      );
      expect(body.projectedSigmaCssPx, `projection at ${presence}`).toBeCloseTo(
        resting.projectedSigmaCssPx * presence,
        6,
      );
      expect(at(measured, presence).host["--vitrea-blur"], `token at ${presence}`).toBe(
        `${String(Math.round(resting.projectedSigmaCssPx * presence * 100) / 100)}px`,
      );
    }
  });

  it("names a definition per width and never a definition per driver value", () => {
    // The cost of a following width is one `<filter>` per width per frame, which
    // the root's frame-scoped sweep removes again; what would NOT be bounded is
    // a table re-solved with each, so the ids differ in their width segment and
    // agree in the transfer segment they are cached on.
    const specs = (render: CssTierRender) => referenceFilterSpecs(render.body);
    const resting = specs(cssTierDeclarations(linear));
    expect(resting.length).toBe(2);
    const restingIds = resting.map((spec) => referenceFilterId("p", spec.sigmaCssPx, spec.transfer));
    const transferSegment = (id: string): string => id.slice(id.indexOf("-t"));
    for (const presence of [0.2, 0.5, 0.9]) {
      const ids = specs(at(linear, presence)).map((spec) =>
        referenceFilterId("p", spec.sigmaCssPx, spec.transfer),
      );
      expect(ids.length, `count at ${presence}`).toBe(2);
      expect(ids[0], `sharp id at ${presence}`).not.toBe(restingIds[0]);
      expect(transferSegment(ids[0]!), `transfer at ${presence}`).toBe(
        transferSegment(restingIds[0]!),
      );
    }
  });

  it("keeps the tint table at the resting material and puts the presence on the floor", () => {
    const resting = cssTierDeclarations(linear);
    const floor = cssTierFloorAlpha(MATERIAL_OPTICS.regular);
    expect(resting.body.tintForm).toBe("linear");
    expect(alphaOf(layersOf(resting).overlay!["background-color"]!)).toBeCloseTo(floor, 3);
    for (const presence of [0.2, 0.5, 0.9]) {
      const render = at(linear, presence);
      expect(render.body.tintTransfer, `transfer at ${presence}`).toEqual(resting.body.tintTransfer);
      expect(
        alphaOf(layersOf(render).overlay!["background-color"]!),
        `floor at ${presence}`,
      ).toBeCloseTo(floor * presence, 3);
    }
  });

  it("solves a tint table once per material, however many widths carry it", () => {
    // The transit's real cost, and the reason the transfer is presence-invariant
    // while the width is not: the table is a bisection to an interpolation bound
    // run per channel, and a driver that re-solved it every frame would be the
    // one unbounded thing about a materialization. Each ensure/sweep pair below
    // is a frame: a new width, a new `<filter>`, the previous one swept.
    const transfer = cssTierDeclarations(linear).body.tintTransfer;
    expect(transfer).toBeDefined();
    const defs = createCssTierFilterDefs(document, document.body, "q");
    const solves = () => vi.mocked(cssTierTintTable).mock.calls.length;
    const before = solves();
    const tables: string[] = [];
    for (const sigmaCssPx of [9.3, 8.4, 7.1, 5.5]) {
      defs.ensure({ sigmaCssPx, ...(transfer === undefined ? {} : { transfer }) });
      defs.sweep();
      const fn = document.querySelector("filter feComponentTransfer feFuncR");
      tables.push(fn?.getAttribute("tableValues") ?? "");
    }
    // Three channels, once, for four definitions.
    expect(solves() - before).toBe(3);
    // And every definition carries the same table — the resting material's.
    expect(new Set(tables).size).toBe(1);
    expect(tables[0]).not.toBe("");
    defs.dispose();
  });

  it("leaves the mask's own ramp alone, so the raster cache is presence-invariant", () => {
    // The mask is keyed on the geometry and the three ramp numbers; a presence
    // in the ramp would redraw a canvas per frame for a weight the layer's own
    // `opacity` already carries.
    for (const presence of [0.2, 0.5, 0.9]) {
      expect(at(measured, presence).body.ramp, `at ${presence}`).toEqual(
        cssTierDeclarations(measured).body.ramp,
      );
    }
  });
});

describe("a driven material declares no transitions", () => {
  /**
   * Every transition the render declares. The collapsed heavy layer declares
   * none — it is `display: none`, and a transition on a layer that paints
   * nothing would be a property written for no one — so the list is filtered
   * rather than padded, and asserted non-empty by its readers.
   */
  const transitionsOf = (render: CssTierRender): readonly string[] =>
    [render.host.transition, ...Object.values(render.layers ?? {}).map((layer) => layer.transition)]
      .filter((value): value is string => value !== undefined);

  it("suppresses every element's transition while a driver writes each frame", () => {
    for (const surface of [plain, measured, linear, forcedColors]) {
      const transitions = transitionsOf(cssTierDeclarations({ ...surface, driven: true }));
      expect(transitions.length).toBeGreaterThan(0);
      for (const transition of transitions) expect(transition).toBe("none");
    }
  });

  it("keeps the material's own transitions when no driver is running", () => {
    for (const transition of transitionsOf(cssTierDeclarations(measured))) {
      expect(transition).toContain("ms");
    }
    // A held presence is not a driver: a surface parked below 1 transitions
    // like any other, because presence is authored rather than animated here.
    for (const transition of transitionsOf(at(measured, 0.5))) {
      expect(transition).toContain("ms");
    }
  });

  it("is independent of the presence in both directions", () => {
    for (const transition of transitionsOf(
      cssTierDeclarations({ ...measured, driven: true, materialization: 1 }),
    )) {
      expect(transition).toBe("none");
    }
  });
});
