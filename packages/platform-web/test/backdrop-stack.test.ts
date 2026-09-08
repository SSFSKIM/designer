/**
 * W22 G3 — the backdrop a group is handed when it is standing on other glass.
 *
 * Two claims, at the two levels the mechanism has. The arithmetic is `pure`: the
 * surface's output tone is its own composite applied to its own backdrop's tone,
 * exact at both ends of the transmission range. The wiring is a root: a group
 * that samples the DOM over another group's surface is handed that surface's
 * output, and one that is not over anything is handed nothing at all — which is
 * the rule `backdrop-tone.ts` states and this must not weaken.
 *
 * jsdom paints nothing, so nothing here is a pixel. The claim is about what the
 * root resolves and hands the bridge.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import type { Rect } from "@vitreajs/vitrea";

import { compositeToneOver, toneBeneath, type PaintedSurface } from "../src/backdrop-stack";
import type { BackdropToneSample } from "../src/backdrop-tone";
import type { MediaMatcher } from "../src/media-policy";
import { createGlassRoot, type GlassRoot } from "../src/root";

import { createFakeGpu } from "../../renderer-webgpu/test/harness/fake-gpu";
import "../../renderer-webgpu/test/setup/webgpu-flags";

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

/** jsdom lays nothing out, so a box is whatever the test says it is. */
function boxed<T extends Element>(element: T, rect: Rect): T {
  element.getBoundingClientRect = () =>
    ({
      ...rect,
      top: rect.y,
      left: rect.x,
      right: rect.x + rect.width,
      bottom: rect.y + rect.height,
      toJSON: () => rect,
    }) as DOMRect;
  return element;
}

const checkerboard: BackdropToneSample = {
  rgb: [0.5, 0.5, 0.5],
  // The canonical checkerboard's two readings: an equal-linear mean of 0.5 whose
  // encoded-space mean decodes to 0.214 (W9, claims §5.31).
  luminance: 0.214,
  linearLuminance: 0.5,
};

let roots: GlassRoot[] = [];
let containers: HTMLElement[] = [];
let restoreCanvasContexts: (() => void) | undefined;

/** jsdom has no canvas contexts; the bridge configures two per plane. */
const stubCanvasContexts = (): void => {
  const original = HTMLCanvasElement.prototype.getContext;
  (HTMLCanvasElement.prototype as { getContext: unknown }).getContext = () => ({
    configure: () => undefined,
    unconfigure: () => undefined,
    getCurrentTexture: () => ({ createView: () => ({}) }),
  });
  restoreCanvasContexts = () => {
    (HTMLCanvasElement.prototype as { getContext: unknown }).getContext = original;
  };
};

/**
 * A root drawing the calibration bed's stacked scene: a base surface over a
 * declared backdrop, and a DOM-sampling overlay sitting inside it on the overlay
 * plane. The geometry is `glass-over-glass`'s own — base 220 × 130 at (50, 35),
 * overlay 120 × 56 at (100, 64).
 */
function stackedRoot(overlayBox: Rect): GlassRoot {
  stubCanvasContexts();
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const instance = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: () => {},
    renderer: "webgpu",
    webgpu: { device: createFakeGpu().device },
  });
  roots.push(instance);

  // The base's backdrop is DECLARED rather than sampled, so the test needs no
  // pixels: X6's hint is the first of the three statements the root reads, and
  // what this exercises is the third.
  instance.registerGroup({ id: "base", backdrop: { tone: "light", luminance: 0.5 } });
  instance.registerGroup({ id: "over" });

  const baseHost = boxed(document.createElement("div"), { x: 50, y: 35, width: 220, height: 130 });
  instance.plane("base").hostLayer.append(baseHost);
  instance.registerHost({ host: baseHost, groupId: "base", plane: "base", nodeId: "base" });

  const overHost = boxed(document.createElement("div"), overlayBox);
  instance.plane("overlay").hostLayer.append(overHost);
  instance.registerHost({ host: overHost, groupId: "over", plane: "overlay", nodeId: "over" });

  return instance;
}

const toneOf = (instance: GlassRoot, groupId: string): number | undefined =>
  instance.renderInput()?.groups.find((entry) => entry.groupId === groupId)?.backdropToneLevel;

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
});

afterEach(() => {
  restoreCanvasContexts?.();
  restoreCanvasContexts = undefined;
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
});

describe("the tone a surface renders at (W22 G3)", () => {
  it("passes its backdrop's light through where it occludes nothing", () => {
    const output = compositeToneOver(
      { tintAlpha: 0, tint: [1, 1, 1], addedLight: 0 },
      checkerboard,
    );
    expect(output.linearLuminance).toBeCloseTo(0.5, 12);
    // The LEVEL is the linear mean even here, and that is the module's one
    // documented residual: a surface transparent enough to pass its backdrop's
    // structure through still reports a flat output. Measured at 0.005 on the
    // stacked cell, against 0.07 for the form that transported the gap.
    expect(output.luminance).toBeCloseTo(0.5, 12);
  });

  it("collapses onto its own tint where it occludes everything", () => {
    const output = compositeToneOver(
      { tintAlpha: 1, tint: [0.05, 0.05, 0.05], addedLight: 0.002 },
      checkerboard,
    );
    for (const channel of output.rgb) expect(channel).toBeCloseTo(0.052, 12);
    expect(output.linearLuminance).toBeCloseTo(0.052, 12);
    // One colour has one mean in both spaces, and the backdrop's own 2.3× split
    // does not survive.
    expect(output.luminance).toBeCloseTo(output.linearLuminance, 12);
  });

  it("does not carry the backdrop's encoded/linear split into its own output", () => {
    const output = compositeToneOver(
      { tintAlpha: 0.92, tint: [0.05, 0.05, 0.05], addedLight: 0 },
      checkerboard,
    );
    expect(output.linearLuminance).toBeCloseTo(0.08 * 0.5 + 0.92 * 0.05, 12);
    // The backdrop's two statistics stand 0.286 apart and the output's stand
    // together, which is what the capture reads: the base pane's own body is
    // 0.002 to 0.005 apart in both schemes because the material flattened it.
    expect(output.luminance).toBe(output.linearLuminance);
  });
});

describe("which surface is underneath (W22 G3)", () => {
  const base: PaintedSurface = {
    plane: "base",
    order: 0,
    bounds: { x: 50, y: 35, width: 220, height: 130 },
    tone: checkerboard,
  };

  it("finds a lower plane's surface that carries the whole footprint", () => {
    expect(toneBeneath({ x: 100, y: 64, width: 120, height: 56 }, "overlay", [base])).toBe(
      checkerboard,
    );
  });

  it("refuses a footprint that hangs over the edge", () => {
    // Half on the glass and half on a page nobody measured: there is no single
    // backdrop to hand it, so it is handed none.
    expect(
      toneBeneath({ x: 200, y: 64, width: 120, height: 56 }, "overlay", [base]),
    ).toBeUndefined();
  });

  it("refuses a surface in the same plane, however its order reads", () => {
    // X1 forbids two overlapping nodes in one plane, so a same-plane neighbour is
    // never underneath — reading `order` as depth would invent a stack.
    expect(
      toneBeneath({ x: 100, y: 64, width: 120, height: 56 }, "base", [{ ...base, order: -5 }]),
    ).toBeUndefined();
  });

  it("takes the nearest of two candidates", () => {
    const nearer: PaintedSurface = {
      ...base,
      order: 4,
      tone: { rgb: [0.1, 0.1, 0.1], luminance: 0.1, linearLuminance: 0.1 },
    };
    expect(
      toneBeneath({ x: 100, y: 64, width: 120, height: 56 }, "overlay", [base, nearer])?.luminance,
    ).toBe(0.1);
  });

  it("is not fooled by a surface with no extent", () => {
    // An unmeasured host reports an empty box, which contains nothing.
    expect(
      toneBeneath({ x: 0, y: 0, width: 0, height: 0 }, "overlay", [
        { ...base, bounds: { x: 0, y: 0, width: 0, height: 0 } },
      ]),
    ).toBeUndefined();
  });
});

describe("the root hands a stacked group the glass beneath it (W22 G3)", () => {
  it("gives a DOM-sampling overlay the base surface's rendered output", async () => {
    const instance = stackedRoot({ x: 100, y: 64, width: 120, height: 56 });
    await instance.ready();
    instance.runFrame(16);

    const over = instance.renderInput()?.groups.find((entry) => entry.groupId === "over");
    expect(over?.state.samplingBackend).toBe("css-backdrop");

    const baseTone = toneOf(instance, "base");
    const overTone = toneOf(instance, "over");
    expect(baseTone).toBeCloseTo(0.5, 12);
    expect(overTone).toBeDefined();
    if (overTone === undefined) return;
    // The base's own material stands between the two, so the overlay's backdrop
    // is neither absent nor the 0.5 the base declared: the shipped light
    // material over a mid grey renders well above it, and that lift is exactly
    // the glass the overlay is standing on.
    expect(overTone).not.toBeCloseTo(0.5, 3);
    expect(overTone).toBeGreaterThan(0.5);
    expect(overTone).toBeLessThan(1);
  });

  it("leaves an overlay that is not over the base unadapted", async () => {
    // Clear of the base entirely — the case the runtime has always been right
    // about, and the one this mechanism must not start guessing at.
    const instance = stackedRoot({ x: 400, y: 400, width: 120, height: 56 });
    await instance.ready();
    instance.runFrame(16);

    expect(toneOf(instance, "over")).toBeUndefined();
  });

  it("leaves an overlay that overhangs the base unadapted", async () => {
    const instance = stackedRoot({ x: 240, y: 64, width: 120, height: 56 });
    await instance.ready();
    instance.runFrame(16);

    expect(toneOf(instance, "over")).toBeUndefined();
  });
});
