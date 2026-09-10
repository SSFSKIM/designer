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

/** A `materialize` source parked beside the card, on the plane it started on. */
const SOURCE_BOX: Rect = { x: 340, y: 40, width: 96, height: 40 };

/**
 * A settled `materialize` pair, as W27d leaves one: two endpoints registered on
 * their own boxes and planes inside ONE group, the source parked at identity on
 * the base plane and the destination fully present on the overlay plane, with
 * the card of the first describe underneath as the glass the destination is
 * standing on.
 *
 * The source is disjoint from the card because X1 forbids two overlapping
 * surfaces in one plane; what makes the case is its PLANE, not its position.
 *
 * `pairFirst` registers the pair — its group and both its endpoints — ahead of
 * the card, which is the page where a `materialize` pair's markup comes before
 * the surface it lands on. Registration order is what the frame's plane sort
 * tie-breaks on, so it is the second half of this case and not a variation of it.
 */
interface PairOptions {
  readonly sourcePresent: boolean | "unregistered";
  readonly destinationPresent?: boolean;
  readonly pairFirst?: boolean;
}

function pairedRoot(options: PairOptions): GlassRoot {
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

  const registerCard = (): void => {
    instance.registerGroup({ id: "base", backdrop: { tone: "light", luminance: 0.5 } });
    const card = boxed(document.createElement("div"), BASE_BOX);
    instance.plane("base").hostLayer.append(card);
    instance.registerHost({ host: card, groupId: "base", plane: "base", nodeId: "card" });
  };

  const registerPair = (): void => {
    instance.registerGroup({ id: "pair" });
    if (options.sourcePresent !== "unregistered") {
      const source = boxed(document.createElement("div"), SOURCE_BOX);
      instance.plane("base").hostLayer.append(source);
      instance.registerHost({
        host: source,
        groupId: "pair",
        plane: "base",
        nodeId: "pair-source",
        present: options.sourcePresent,
      });
    }
    const destination = boxed(document.createElement("div"), OVERLAY_BOX);
    instance.plane("overlay").hostLayer.append(destination);
    instance.registerHost({
      host: destination,
      groupId: "pair",
      plane: "overlay",
      nodeId: "pair-destination",
      present: options.destinationPresent ?? true,
    });
  };

  if (options.pairFirst === true) {
    registerPair();
    registerCard();
  } else {
    registerCard();
    registerPair();
  }

  return instance;
}

const pairedFrame = async (
  sourcePresent: boolean | "unregistered",
  destinationPresent?: boolean,
): Promise<GlassRoot> => {
  const instance = pairedRoot({
    sourcePresent,
    ...(destinationPresent === undefined ? {} : { destinationPresent }),
  });
  await instance.ready();
  instance.runFrame(16);
  return instance;
};

/** The pair registered first, which is what the frame's plane sort tie-breaks on. */
const pairFirstFrame = async (
  sourcePresent: boolean | "unregistered",
  destinationPresent?: boolean,
): Promise<GlassRoot> => {
  const instance = pairedRoot({
    sourcePresent,
    ...(destinationPresent === undefined ? {} : { destinationPresent }),
    pairFirst: true,
  });
  await instance.ready();
  instance.runFrame(16);
  return instance;
};

/** The order the frame resolved its groups in, which is the order it renders them in. */
const resolutionOrder = (instance: GlassRoot): readonly string[] =>
  (instance.renderInput()?.groups ?? []).map((entry) => entry.groupId);

/**
 * The other half of the same endpoint: what the group's own absent member does
 * to the group's search for what IT is standing on (W27d; claims §5.132 §6).
 *
 * The stacked predictor reduces the group to a footprint and a back plane. Both
 * were taken over every measured member, so a member drawing nothing widened the
 * footprint past what any one surface underneath could carry and pushed the back
 * plane down to a plane there is nothing beneath — and the surface that really
 * was there stopped seeing the glass it was sitting on.
 */
describe("a group's own absent member is not part of what it stands on (W27d)", () => {
  it("hands the destination the card it is over once the source has parked", async () => {
    const instance = await pairedFrame(false);
    const pair = instance.renderInput()?.groups.find((entry) => entry.groupId === "pair");
    expect(pair?.state.samplingBackend).toBe("css-backdrop");
    const tone = toneOf(instance, "pair");
    expect(tone).toBeDefined();
    expect(tone).toBeGreaterThan(0.5);
  });

  it("agrees exactly with the same pair carrying only its destination", async () => {
    // The identity the endpoint is: inside the group as much as above it, a
    // parked member is worth exactly what an unregistered one is worth, so the
    // two readings have to agree exactly rather than approximately.
    const parked = toneOf(await pairedFrame(false), "pair");
    const alone = toneOf(await pairedFrame("unregistered"), "pair");
    expect(alone).toBeDefined();
    expect(parked).toBe(alone);
  });

  it("stands on nothing while the source is still there", async () => {
    // The resting bed, unmoved: a source drawing on the base plane really is
    // part of this group's footprint, and a group straddling the card's edge on
    // the card's own plane has no single surface beneath it to adapt to.
    expect(toneOf(await pairedFrame(true), "pair")).toBeUndefined();
  });

  it("predicts no stacked tone for a group whose members have all parked", async () => {
    // Nothing of the group is drawing, so there is no footprint to stand on —
    // and the search must not fall back to any member's box.
    expect(toneOf(await pairedFrame(false, false), "pair")).toBeUndefined();
  });
});

/**
 * The same endpoint one level up, in the frame's own resolution ORDER (W27d;
 * claims §5.132 §6).
 *
 * W22 G3 resolves groups back to front so that whatever a group is standing on
 * has already been resolved when the group's backdrop is decided, and it reads
 * the plane off every measured member. A parked `materialize` source therefore
 * held the whole pair on the base plane, and where the pair was registered
 * before the card, the tie-break on registration order put the pair first: the
 * card was not yet in the painted set when the destination — drawing on the
 * overlay, plainly over the card — asked what it was standing on, and the
 * predictor the case above fixed was handed an empty set instead.
 *
 * The plane a group sorts by has to be the plane it is painting on, and a member
 * at identity paints on none.
 */
describe("a parked member does not hold its group's sort plane (W27d)", () => {
  it("hands the destination the card even when the pair is registered first", async () => {
    const instance = await pairFirstFrame(false);
    expect(resolutionOrder(instance)).toEqual(["base", "pair"]);
    const tone = toneOf(instance, "pair");
    expect(tone).toBeDefined();
    expect(tone).toBeGreaterThan(0.5);
  });

  it("reads the same as the card-first page, which is the point", async () => {
    // Sorting by what is drawn makes the two registration orders one case: the
    // pair is an overlay-plane group either way, so the two readings agree
    // exactly rather than approximately.
    const pairFirst = toneOf(await pairFirstFrame(false), "pair");
    expect(pairFirst).toBe(toneOf(await pairedFrame(false), "pair"));
  });

  it("keeps a drawing source's group on the base plane, in registration order", async () => {
    // The control on the sort itself, and the resting bed it must not move: a
    // source that is genuinely there really is painting on the base plane, so
    // its group is a base-plane group and the tie-break on registration order
    // decides it, exactly as it did before this filter existed.
    expect(resolutionOrder(await pairFirstFrame(true))).toEqual(["pair", "base"]);
    expect(resolutionOrder(await pairedFrame(true))).toEqual(["base", "pair"]);
  });
});
