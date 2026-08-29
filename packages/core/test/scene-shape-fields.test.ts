/**
 * The corner reference and the concentric parent link, as scene-model fields
 * (Decision Log #23(c)).
 *
 * Both existed in v1 — on `SurfaceInput`, the renderer's per-frame structural
 * view — and neither was ever populated by the shipping pipeline, because core's
 * node descriptor had nowhere to carry them and the browser layer builds that
 * view from core. So the corner reference silently defaulted for every surface,
 * and the parent link was reachable only from test fixtures.
 *
 * The parent link is the scene model's **first node→node reference**, which is
 * why most of what follows is refusals. Every other cross-reference in the scene
 * (`node.groupId`, `group.backdropSourceId`) is checked where it is written; a
 * parent edge additionally has to rule out a cycle, and has to survive the
 * parent being removed out from under it.
 */

import { describe, expect, it } from "vitest";

import type { PlatformProbe } from "../src/capability";
import type { ShapeChannels } from "@vitrea/geometry";
import { createGlassScene, GlassSceneError } from "../src/scene";

const PROBE: PlatformProbe = {
  webgpu: "not-requested",
  backdropFilter: true,
  backdropProxyConformance: "pass",
  deviceHealth: "ok",
};

const SHAPE: ShapeChannels = {
  center: [0, 0],
  size: [160, 44],
  radii: [12, 12, 12, 12],
  smoothing: 0.6,
  thickness: 8,
};

function scene() {
  const instance = createGlassScene({ devMode: false, platform: PROBE });
  instance.registerBackdropSource({ id: "dom", kind: "dom" });
  instance.registerGlassGroup({ id: "g1", backdropSourceId: "dom" });
  instance.registerGlassGroup({ id: "g2", backdropSourceId: "dom" });
  return instance;
}

const node = (id: string, extra: Record<string, unknown> = {}) => ({
  id,
  groupId: "g1",
  shapeFamily: "fixed-rounded-rect" as const,
  shape: SHAPE,
  zSlot: { plane: "base" as const, order: 0 },
  ...extra,
});

describe("the corner reference", () => {
  it("is carried on the descriptor, and absent when the author did not say", () => {
    const instance = scene();
    instance.registerGlassNode(node("figma", { reference: "figma-smoothing" }));
    instance.registerGlassNode(node("unsaid"));

    expect(instance.glassNode("figma")?.descriptor.reference).toBe("figma-smoothing");
    // Absent, not defaulted here: the renderer owns `"apple-continuous"` as the
    // default, and a core that filled it in would be deciding geometry.
    expect(instance.glassNode("unsaid")?.descriptor.reference).toBeUndefined();
  });

  it("is patchable, and a present-but-undefined key clears it", () => {
    const instance = scene();
    instance.registerGlassNode(node("n", { reference: "figma-smoothing" }));

    instance.updateGlassNode("n", { reference: "apple-continuous" });
    expect(instance.glassNode("n")?.descriptor.reference).toBe("apple-continuous");

    instance.updateGlassNode("n", { reference: undefined });
    expect(instance.glassNode("n")?.descriptor.reference).toBeUndefined();
  });
});

describe("the concentric parent link", () => {
  it("is carried on the descriptor", () => {
    const instance = scene();
    instance.registerGlassNode(node("track"));
    instance.registerGlassNode(node("indicator", { concentricOf: { nodeId: "track", inset: 4 } }));

    expect(instance.glassNode("indicator")?.descriptor.concentricOf).toEqual({
      nodeId: "track",
      inset: 4,
    });
  });

  it("refuses a parent that is not registered", () => {
    const instance = scene();

    expect(() =>
      instance.registerGlassNode(node("indicator", { concentricOf: { nodeId: "ghost", inset: 4 } })),
    ).toThrow(GlassSceneError);
    // And leaves nothing behind: a refused registration is not a half-registration.
    expect(instance.glassNode("indicator")).toBeUndefined();
  });

  /*
   * Same group, because the renderer resolves a concentric child against its
   * parent's *instance*, and instances are packed per group — a cross-group
   * parent is not in the buffer the child's draw reads at all. The renderer
   * throws `pass-input` for it today, one frame at a time, with no way back to
   * the call that caused it.
   */
  it("refuses a parent in another group", () => {
    const instance = scene();
    instance.registerGlassNode(node("track", { groupId: "g2" }));

    expect(() =>
      instance.registerGlassNode(node("indicator", { concentricOf: { nodeId: "track", inset: 4 } })),
    ).toThrow(/group "g2"/);
  });

  it("refuses a node that is its own parent", () => {
    const instance = scene();

    expect(() =>
      instance.registerGlassNode(node("self", { concentricOf: { nodeId: "self", inset: 4 } })),
    ).toThrow(/its own concentric parent/);
  });

  it("refuses a cycle closed by an update", () => {
    const instance = scene();
    instance.registerGlassNode(node("a"));
    instance.registerGlassNode(node("b", { concentricOf: { nodeId: "a", inset: 4 } }));
    instance.registerGlassNode(node("c", { concentricOf: { nodeId: "b", inset: 4 } }));

    expect(() =>
      instance.updateGlassNode("a", { concentricOf: { nodeId: "c", inset: 4 } }),
    ).toThrow(/cycle/);
    // The chain that was legal before the refused update is still legal.
    expect(instance.glassNode("c")?.descriptor.concentricOf?.nodeId).toBe("b");
  });

  it("accepts a chain that bottoms out", () => {
    const instance = scene();
    instance.registerGlassNode(node("a"));
    instance.registerGlassNode(node("b", { concentricOf: { nodeId: "a", inset: 4 } }));
    instance.registerGlassNode(node("c", { concentricOf: { nodeId: "b", inset: 2 } }));

    expect(instance.glassNode("c")?.descriptor.concentricOf?.nodeId).toBe("b");
  });

  /*
   * The same rule `removeGlassGroup` and `removeBackdropSource` already follow:
   * a still-referenced thing is not removable. A child left behind would be a
   * level set of a field that no longer exists — the renderer's own
   * parent-not-found throw, once per frame, forever.
   */
  it("refuses to remove a parent that still has a child", () => {
    const instance = scene();
    instance.registerGlassNode(node("track"));
    instance.registerGlassNode(node("indicator", { concentricOf: { nodeId: "track", inset: 4 } }));

    expect(() => instance.removeGlassNode("track")).toThrow(/concentric parent/);

    instance.updateGlassNode("indicator", { concentricOf: undefined });
    expect(() => instance.removeGlassNode("track")).not.toThrow();
  });

  it("removes a childless parent, and a child, in any order", () => {
    const instance = scene();
    instance.registerGlassNode(node("track"));
    instance.registerGlassNode(node("indicator", { concentricOf: { nodeId: "track", inset: 4 } }));

    instance.removeGlassNode("indicator");
    instance.removeGlassNode("track");

    expect(instance.nodesOfGroup("g1")).toEqual([]);
  });
});
