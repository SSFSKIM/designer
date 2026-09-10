/**
 * What a group standing on an absent surface is handed (W27d; W22 G3's stack,
 * contract X6).
 *
 * `materialization` 0 is `Glass.identity`: the surface draws no filter, no tint,
 * no rim and no shadow, on either tier. The stack's third statement — "the glass
 * this group is standing on" — has to agree with that, or a group above a
 * surface that is not there adapts its own material to a composite nothing on
 * the screen is drawing. The endpoint is the claim: a surface at 0 must be worth
 * exactly what an unregistered one is worth, which is nothing.
 *
 * The harness is `backdrop-stack.test.ts`'s, kept here rather than shared
 * because these are the presence cases and that file is the mechanism's own; and
 * it is a vitest root rather than a browser spec, because what is asserted is
 * what the root RESOLVES, which jsdom can answer and a screenshot cannot.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import type { Rect } from "@vitreajs/vitrea";

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

const BASE_BOX: Rect = { x: 50, y: 35, width: 220, height: 130 };
const OVERLAY_BOX: Rect = { x: 100, y: 64, width: 120, height: 56 };

interface StackOptions {
  /** `registerHost`'s presence for the BASE host. Absent registers no base at all. */
  readonly basePresent?: boolean;
  /** The author tint on the base group, as `registerHost` parses it. */
  readonly baseTint?: string;
  /** Register the base and then release it — the other way a surface stops drawing. */
  readonly releaseBase?: boolean;
}

/**
 * A base surface over a DECLARED backdrop with a DOM-sampling overlay inside it:
 * the geometry of `glass-over-glass`, so the overlay is wholly contained and the
 * stack really does resolve. The declared hint is what puts the base into the
 * painted set at all — a surface over a page nobody measured has no output tone
 * to publish, presence or no presence.
 */
function stackedRoot(options: StackOptions = {}): GlassRoot {
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

  instance.registerGroup({ id: "base", backdrop: { tone: "light", luminance: 0.5 } });
  instance.registerGroup({ id: "over" });

  if (options.basePresent !== undefined || options.releaseBase === true) {
    const baseHost = boxed(document.createElement("div"), BASE_BOX);
    instance.plane("base").hostLayer.append(baseHost);
    const handle = instance.registerHost({
      host: baseHost,
      groupId: "base",
      plane: "base",
      nodeId: "base",
      ...(options.basePresent === undefined ? {} : { present: options.basePresent }),
      ...(options.baseTint === undefined ? {} : { tint: options.baseTint }),
    });
    if (options.releaseBase === true) handle.release();
  }

  const overHost = boxed(document.createElement("div"), OVERLAY_BOX);
  instance.plane("overlay").hostLayer.append(overHost);
  instance.registerHost({ host: overHost, groupId: "over", plane: "overlay", nodeId: "over" });

  return instance;
}

const toneOf = (instance: GlassRoot, groupId: string): number | undefined =>
  instance.renderInput()?.groups.find((entry) => entry.groupId === groupId)?.backdropToneLevel;

const frame = async (options: StackOptions): Promise<GlassRoot> => {
  const instance = stackedRoot(options);
  await instance.ready();
  instance.runFrame(16);
  return instance;
};

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

describe("a surface at zero presence is not a backdrop (W27d)", () => {
  it("hands the overlay the base's output while the base is there", async () => {
    // The control, and the reading the two cases below are measured against: the
    // shipped light material over a declared 0.5 renders well above it, and that
    // lift is the glass the overlay is standing on.
    const instance = await frame({ basePresent: true });
    const over = instance.renderInput()?.groups.find((entry) => entry.groupId === "over");
    expect(over?.state.samplingBackend).toBe("css-backdrop");
    const tone = toneOf(instance, "over");
    expect(tone).toBeDefined();
    expect(tone).toBeGreaterThan(0.5);
  });

  it("hands it nothing when the base is registered but not present", async () => {
    // The defect this closes: the base was pushed into the painted set with its
    // full composite tone at every presence, so an overlay over a surface drawing
    // nothing adapted to a material that was not on the screen.
    expect(toneOf(await frame({ basePresent: false }), "over")).toBeUndefined();
  });

  it("gives the same answer as no base at all, and as a released one", async () => {
    // The identity the endpoint is: `Glass.identity` and an absent surface are
    // the same backdrop, so the three readings have to agree exactly rather than
    // approximately.
    const absent = toneOf(await frame({}), "over");
    const released = toneOf(await frame({ releaseBase: true }), "over");
    const identity = toneOf(await frame({ basePresent: false }), "over");
    expect(absent).toBeUndefined();
    expect(released).toBeUndefined();
    expect(identity).toBe(absent);
  });

  it("keeps an author tint out of it too", async () => {
    // The tint is the last step of the composition contract and the one that can
    // move a group above the furthest — a full-strength red platter hands red
    // upward. At zero presence it draws nothing, so it hands nothing upward.
    expect(
      toneOf(await frame({ basePresent: false, baseTint: "#ff0000" }), "over"),
    ).toBeUndefined();
  });
});
