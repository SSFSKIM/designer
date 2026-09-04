/**
 * The two ways a root exposes one group's resolved state, held to one answer.
 *
 * `capabilities(groupId)` and `renderInput().groups[*].state` are both
 * `GlassGroupState` — the honesty core, the record of what actually drew — and a
 * consumer that reads one and a test that reads the other have to see the same
 * value. They did not: the render input's copy was snapshotted at the top of the
 * group's iteration, before the CSS tier's shadow carrier was planned and before
 * its surfaces declared their tint form, so it named the body form alone on every
 * CSS frame. The first half of this file is that parity, asserted on a real root
 * over two frames.
 *
 * The second half is the group's tint verdict. The form is decided per surface,
 * at that surface's own composite level, so two members of a group can straddle
 * the boundary; the group has one field for them and it reports the weakest — the
 * same fold the shadow carrier takes — so a readout never claims a precision some
 * surface of the group did not draw.
 */

import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import {
  cssTierDeclarations,
  type CssTierEngineCapabilities,
  type CssTierInterior,
} from "../src/css-tier";
import type { MediaMatcher } from "../src/media-policy";
import { MATERIAL_OPTICS, weakestCssTintForm } from "../src/optics";
import { createGlassRoot, type GlassRoot } from "../src/root";

/** jsdom has no ResizeObserver, and `GeometrySync` builds one unconditionally. */
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

/**
 * A Chromium user agent, because the CSS tier's form fields are what this file is
 * about: the conformance row an unrecognised agent falls back to is the
 * conservative one, which carries no reference filter and would decide two of the
 * three fields for a reason unrelated to what is asserted here.
 */
const CHROME =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/152.0.7977.64 Safari/537.36";

describe("one group, one resolved state", () => {
  let roots: GlassRoot[] = [];
  let containers: HTMLElement[] = [];
  let restore: (() => void)[] = [];

  beforeEach(() => {
    (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
    const originalRect = Element.prototype.getBoundingClientRect;
    // jsdom cannot lay out, and a member with no measured box writes no
    // declarations at all — so the shadow plan and the tint form would both be
    // absent for a reason that has nothing to do with what is being asserted.
    Element.prototype.getBoundingClientRect = function rect(this: Element): DOMRect {
      return {
        x: 0, y: 0, top: 0, left: 0, right: 160, bottom: 96, width: 160, height: 96,
        toJSON: () => ({}),
      } as DOMRect;
    };
    Object.defineProperty(globalThis.navigator, "userAgent", {
      value: CHROME,
      configurable: true,
    });
    restore = [
      () => {
        Element.prototype.getBoundingClientRect = originalRect;
      },
      () => {
        delete (globalThis.navigator as unknown as Record<string, unknown>).userAgent;
      },
    ];
  });

  afterEach(() => {
    for (const instance of roots) instance.destroy();
    for (const container of containers) container.remove();
    for (const undo of restore) undo();
    roots = [];
    containers = [];
    restore = [];
  });

  const rootWithHosts = (hostCount: number): GlassRoot => {
    const container = document.createElement("div");
    document.body.append(container);
    containers.push(container);
    const instance = createGlassRoot({
      container,
      autoStart: false,
      matcher,
      diagnosticSink: () => {},
    });
    roots.push(instance);
    instance.registerGroup({ id: "g1" });
    for (let index = 0; index < hostCount; index += 1) {
      const host = document.createElement("button");
      instance.plane("base").hostLayer.append(host);
      instance.registerHost({ host, groupId: "g1", plane: "base" });
    }
    return instance;
  };

  it("publishes the state `capabilities` returns, forms and all, on the first frame", () => {
    const instance = rootWithHosts(1);
    instance.runFrame(0);

    const capability = instance.capabilities("g1");
    const published = instance.renderInput()?.groups[0];

    expect(published?.groupId).toBe("g1");
    expect(capability?.activeRenderer).toBe("css");
    // The three CSS-tier form fields are named rather than left to the deep
    // equality alone: an equality between two states that both lack them would
    // pass and say nothing, which is exactly the shape the defect had.
    expect(capability?.cssBody).toBeDefined();
    expect(capability?.cssTint).toBeDefined();
    expect(capability?.cssShadow).toBeDefined();
    expect(published?.state).toEqual(capability);
  });

  it("keeps the two in agreement on a second frame", () => {
    // The form maps are cleared and refilled every frame, so a fix that happened
    // to work on the first one — where they are empty until the frame fills them
    // — could still publish a stale or partial state afterwards.
    const instance = rootWithHosts(2);
    instance.runFrame(0);
    instance.runFrame(16);

    const capability = instance.capabilities("g1");
    expect(capability?.cssShadow).toBeDefined();
    expect(instance.renderInput()?.groups[0]?.state).toEqual(capability);
  });
});

describe("the group's tint form is its weakest member's", () => {
  const CHROMIUM: CssTierEngineCapabilities = {
    referenceFilterInBackdrop: true,
    maskOnBackdropFilter: "yes",
  };
  const base = {
    radii: [20, 20, 20, 20] as const,
    optics: MATERIAL_OPTICS.regular,
    policy: NOMINAL_ACCESSIBILITY_POLICY,
    spanPx: 96,
    extentsCssPx: [160, 96] as const,
    filterIdPrefix: "p",
    engine: CHROMIUM,
  };

  /*
   * Two surfaces of one group whose declared forms differ, driven through
   * `cssTierDeclarations` rather than through a two-host root: the quantity that
   * decides the form is the surface's own composite level, and the public route
   * to a chosen level runs through the size law and the backdrop tone — a lot of
   * machinery to arrange one boundary crossing that the tier's own entry point
   * states directly. What the runtime adds on top of these two declarations is
   * the fold, and the fold is asserted on the helper the runtime calls.
   */
  const light: CssTierInterior = { tintAlpha: 0.487, tint: [0.9, 0.9, 0.9], addedLight: 0.0046 };
  const dark: CssTierInterior = { tintAlpha: 0.95, tint: [0.04, 0.04, 0.04], addedLight: 0 };

  it("folds a group whose members straddle the boundary down to the encoded form", () => {
    const a = cssTierDeclarations({ ...base, interior: light, backdropLuminance: 0.5 });
    const b = cssTierDeclarations({ ...base, interior: dark, backdropLuminance: 0.02 });
    expect(a.body.tintForm).toBe("linear");
    expect(b.body.tintForm).toBe("encoded");

    // Whichever order the member loop reaches them in, the group reports the
    // weaker form: `encoded` keeps the whole tint in the page's own space, and a
    // group reporting `linear` would claim a filter-carried remainder that one of
    // its two surfaces never drew.
    expect(weakestCssTintForm(a.body.tintForm, "encoded")).toBe("encoded");
    expect(weakestCssTintForm(b.body.tintForm, "linear")).toBe("encoded");
  });

  it("reports the linear form only where every member drew it", () => {
    expect(weakestCssTintForm(undefined, "linear")).toBe("linear");
    expect(weakestCssTintForm("linear", "linear")).toBe("linear");
    expect(weakestCssTintForm(undefined, "encoded")).toBe("encoded");
    expect(weakestCssTintForm("encoded", "encoded")).toBe("encoded");
  });
});
