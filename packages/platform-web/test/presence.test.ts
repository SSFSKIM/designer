import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { GlassPlane, Rect } from "@vitreajs/vitrea";
import { createGlassRoot, type GlassRoot } from "../src/root";
import type { GlassHostHandle } from "../src/host";
import { readHostChannels } from "../src/channels";
import { CSS_TIER_SHADOW_CASTER_ATTRIBUTE } from "../src/css-tier-layers";

let root: GlassRoot;
beforeEach(() => {
  vi.stubGlobal("ResizeObserver", class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  });
});
afterEach(() => {
  root?.destroy();
  vi.unstubAllGlobals();
});

function setup(present = true, reducedMotion = false) {
  root = createGlassRoot({
    autoStart: false,
    diagnosticSink: () => {},
    accessibilityOverrides: { reducedMotion },
    matcher: () => ({ matches: false, media: "", addEventListener() {}, removeEventListener() {} }),
  });
  root.registerGroup({ id: "presence" });
  const host = document.createElement("button");
  root.plane("base").hostLayer.append(host);
  const handle = root.registerHost({ host, groupId: "presence", present });
  const value = () => Number(host.style.getPropertyValue("--vitrea-materialization"));
  root.runFrame(0);
  return { host, handle, value };
}

describe("authored material presence", () => {
  it("dematerializes monotonically to identity, without replacing or fading its host", () => {
    const { host, handle, value } = setup();
    expect(value()).toBe(1);
    const id = host.getAttribute("data-vitrea-node");
    handle.update({ present: false });
    let previous = 1;
    for (let time = 10; time <= 220; time += 10) {
      root.runFrame(time);
      expect(value()).toBeLessThanOrEqual(previous);
      expect(value()).toBeGreaterThanOrEqual(0);
      expect(host.getAttribute("data-vitrea-node")).toBe(id);
      expect(host.style.opacity).toBe("");
      previous = value();
    }
    expect(value()).toBe(0);
    expect(readHostChannels(host, { x: 0, y: 0, width: 40, height: 40 }).materialization).toBe(0);
    handle.update({ present: true });
    root.runFrame(230);
    expect(value()).toBeGreaterThan(0);
    expect(value()).toBeLessThan(1);
    for (let time = 240; time <= 440; time += 10) root.runFrame(time);
    expect(value()).toBe(1);
  });

  it("starts absent in place and redirects from the current optical value", () => {
    const { handle, value } = setup(false);
    expect(value()).toBe(0);
    handle.update({ present: true });
    root.runFrame(20);
    const rising = value();
    expect(rising).toBeGreaterThan(0);
    expect(rising).toBeLessThan(1);
    handle.update({ present: false });
    expect(value()).toBe(rising);
    root.runFrame(40);
    expect(value()).toBeLessThan(rising);
  });

  it("steps presence under reduced motion, including a preference change mid-flight", () => {
    const { handle, value } = setup(true, true);
    handle.update({ present: false });
    root.runFrame(16);
    expect(value()).toBe(0);
    root.setAccessibilityOverrides({ reducedMotion: false });
    handle.update({ present: true });
    root.runFrame(32);
    expect(value()).toBeGreaterThan(0);
    expect(value()).toBeLessThan(1);
    root.setAccessibilityOverrides({ reducedMotion: true });
    root.runFrame(48);
    expect(value()).toBe(1);
  });
});

/**
 * A parked surface and the decisions the root takes for the WHOLE frame.
 *
 * `present={false}` is a steady state a surface sits in, not only a transit —
 * so every per-frame decision the root takes over its measured hosts has to
 * agree with what identity draws, which is nothing. The two below are the ones
 * that reach other surfaces: the CSS tier's cost budget, which is the root's
 * total and collapses every surface on it at once (W16 G1), and the group's
 * outer-shadow carrier, whose clip subtracts each member's box from every
 * member's shadow (W18 G1). Both are asserted against `capabilities()`, which is
 * the resolved state a capture cell and a readout go through.
 */

/** jsdom lays nothing out, so a host's box is whatever the test says it is. */
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

interface BedMember {
  readonly groupId: string;
  readonly nodeId: string;
  readonly rect: Rect;
  /** Left out registers the surface at its default full presence. */
  readonly present?: boolean;
  readonly plane?: GlassPlane;
}

/**
 * A CSS-tier root — no device, so nothing is promoted — carrying hosts of
 * declared size, and the handles to retarget their presence with.
 */
function bed(members: readonly BedMember[]): Map<string, GlassHostHandle> {
  root = createGlassRoot({
    autoStart: false,
    diagnosticSink: () => {},
    matcher: () => ({ matches: false, media: "", addEventListener() {}, removeEventListener() {} }),
  });
  for (const groupId of new Set(members.map((member) => member.groupId))) {
    root.registerGroup({ id: groupId });
  }
  const handles = new Map<string, GlassHostHandle>();
  for (const member of members) {
    const host = boxed(document.createElement("div"), member.rect);
    const plane = member.plane ?? "base";
    root.plane(plane).hostLayer.append(host);
    handles.set(
      member.nodeId,
      root.registerHost({
        host,
        groupId: member.groupId,
        nodeId: member.nodeId,
        plane,
        ...(member.present === undefined ? {} : { present: member.present }),
      }),
    );
  }
  root.runFrame(0);
  return handles;
}

describe("a parked surface and the root's CSS-tier cost budget (W27d; W16 G1)", () => {
  /*
   * 420,000 device px at ratio 1 — past the root's 400,000 budget on its own, so
   * whether this one host is charged decides the body form of every CSS surface
   * on the root. The live neighbour beside it is disjoint, since X1 forbids two
   * overlapping surfaces in one plane.
   */
  const WIDE: Rect = { x: 0, y: 0, width: 700, height: 600 };
  const LIVE: Rect = { x: 720, y: 0, width: 120, height: 80 };

  it("collapses the root while the wide surface is drawing its filters", () => {
    // The control, and the resting bed the fix must not move: a surface that is
    // there spends the budget, and the collapse is the measured degradation W16
    // declared rather than something presence introduced.
    bed([
      { groupId: "wide", nodeId: "wide", rect: WIDE },
      { groupId: "live", nodeId: "live", rect: LIVE },
    ]);
    expect(root.capabilities("live")?.cssBody).toBe("collapsed");
    expect(root.capabilities("wide")?.cssBody).toBe("collapsed");
  });

  it("charges nothing for one parked at identity, so its neighbours keep both layers", () => {
    // At presence 0 the tier writes `backdrop-filter: none` and does not display
    // the heavy layer, so the compositor produces no filtered pixel for this
    // host at all. Charging it took the two-layer body away from every other
    // surface on the root for an area nothing sampled.
    bed([
      { groupId: "wide", nodeId: "wide", rect: WIDE, present: false },
      { groupId: "live", nodeId: "live", rect: LIVE },
    ]);
    expect(root.capabilities("live")?.cssBody).toBe("two-layer");
    expect(root.capabilities("wide")?.cssBody).toBe("two-layer");
  });

  it("charges a surface in transit in full, which really does allocate both layers", () => {
    // Only exactly 0 is free. A thinned filter is still a filter — the layers
    // are up and the readback happens at the host's full size — so anything
    // positive pays the whole area, and the budget stays a statement about the
    // pixels the compositor has to produce.
    const handles = bed([
      { groupId: "wide", nodeId: "wide", rect: WIDE, present: false },
      { groupId: "live", nodeId: "live", rect: LIVE },
    ]);
    handles.get("wide")?.update({ present: true });
    root.runFrame(16);
    const value = Number(
      document.querySelector<HTMLElement>('[data-vitrea-node="wide"]')
        ?.style.getPropertyValue("--vitrea-materialization"),
    );
    expect(value).toBeGreaterThan(0);
    expect(value).toBeLessThan(1);
    expect(root.capabilities("live")?.cssBody).toBe("collapsed");
  });
});

describe("a parked surface and the CSS tier's group shadow (W27d; W18 G1)", () => {
  const A: Rect = { x: 0, y: 0, width: 120, height: 80 };
  const B: Rect = { x: 160, y: 0, width: 120, height: 80 };
  const C: Rect = { x: 320, y: 0, width: 120, height: 80 };

  const castersOf = (): readonly string[] =>
    [...document.querySelectorAll(`[${CSS_TIER_SHADOW_CASTER_ATTRIBUTE}]`)].map(
      (element) => element.getAttribute(CSS_TIER_SHADOW_CASTER_ATTRIBUTE) ?? "",
    );

  it("carries a whole group's shadows on the group's last host", () => {
    // The control: two drawing members need carrier B, because only the
    // last-painted host can hold a shadow every member's filters are behind.
    bed([
      { groupId: "g", nodeId: "a", rect: A },
      { groupId: "g", nodeId: "b", rect: B },
    ]);
    expect(root.capabilities("g")?.cssShadow).toBe("group");
    expect(castersOf()).toEqual(["a", "b"]);
  });

  it("leaves a group of one drawing member on its own layer", () => {
    // A parked member is not a sibling whose filters could sample anything, so
    // a group holding one drawing surface is a group of one: carrier A is exact
    // for its own shadow and costs it no container.
    bed([
      { groupId: "g", nodeId: "a", rect: A },
      { groupId: "g", nodeId: "b", rect: B, present: false },
    ]);
    expect(root.capabilities("g")?.cssShadow).toBe("layer");
    expect(castersOf()).toEqual([]);
  });

  it("cuts no hole in a sibling's shadow for a member that is not there", () => {
    // Carrier B's even-odd clip removes each cast's rounded box from every
    // member's shadow, which is the renderer's own `lift · (1 − coverage)`. An
    // absent member covers nothing, so a hole for it is a notch cut out of a
    // live sibling's shadow by a surface nobody can see.
    bed([
      { groupId: "g", nodeId: "a", rect: A },
      { groupId: "g", nodeId: "b", rect: B, present: false },
      { groupId: "g", nodeId: "c", rect: C },
    ]);
    expect(root.capabilities("g")?.cssShadow).toBe("group");
    expect(castersOf()).toEqual(["a", "c"]);
    const container = document.querySelector<HTMLElement>("[data-vitrea-css-group-shadow]");
    const clip = container?.style.getPropertyValue("clip-path") ?? "";
    // One outer rectangle plus one hole per drawing member, and no more.
    expect(clip.match(/M /gu)?.length).toBe(3);
  });
});
