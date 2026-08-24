/**
 * The three registries (§Core model): BackdropSource, GlassGroup, GlassNode —
 * their references, the dirty-epoch bookkeeping that enforces "at most once per
 * dirty source per frame", and the same-plane overlap check.
 */

import { describe, expect, it } from "vitest";

import {
  DEFAULT_BACKDROP_RESOLUTION,
  DEFAULT_GROUP_SAMPLING,
  GlassSceneError,
  createDiagnosticsChannel,
  createGlassScene,
  type GlassScene,
  type PlatformProbe,
  type Rect,
  type ShapeChannels,
} from "../src/index";

const workingPlatform: PlatformProbe = {
  webgpu: true,
  backdropFilter: true,
  backdropProxyConformance: "pass",
  deviceHealth: "ok",
};

const shape: ShapeChannels = {
  center: [0, 0],
  size: [100, 44],
  radii: [22, 22, 22, 22],
  smoothing: 0.6,
  thickness: 8,
};

const rect = (x: number, y: number, width = 40, height = 40): Rect => ({ x, y, width, height });

/** A scene with one texture source, one group on it, and one node in the group. */
function seeded(): GlassScene {
  const scene = createGlassScene({ platform: workingPlatform });
  scene.registerBackdropSource({
    id: "src",
    kind: "texture",
    probe: { taint: "clean", textureCompatibility: "compatible" },
  });
  scene.registerGlassGroup({ id: "grp", backdropSourceId: "src" });
  scene.registerGlassNode({
    id: "node",
    groupId: "grp",
    shapeFamily: "capsule",
    shape,
    zSlot: { plane: "base", order: 0 },
  });
  return scene;
}

describe("registration and references", () => {
  it("registers all three kinds and reads them back", () => {
    const scene = seeded();

    expect(scene.backdropSource("src")?.descriptor.kind).toBe("texture");
    expect(scene.glassGroup("grp")?.descriptor.backdropSourceId).toBe("src");
    expect(scene.glassNode("node")?.descriptor.groupId).toBe("grp");
  });

  it("answers group-to-source and node-to-group membership in both directions", () => {
    const scene = seeded();
    scene.registerGlassGroup({ id: "grp2", backdropSourceId: "src" });

    expect(scene.groupsOfSource("src").map((group) => group.descriptor.id)).toEqual(["grp", "grp2"]);
    expect(scene.nodesOfGroup("grp").map((node) => node.descriptor.id)).toEqual(["node"]);
    expect(scene.nodesOfGroup("grp2")).toEqual([]);
  });

  it("refuses a duplicate id", () => {
    const scene = seeded();

    expect(() => scene.registerGlassGroup({ id: "grp", backdropSourceId: "src" })).toThrow(
      GlassSceneError,
    );
    expect(() =>
      scene.registerGlassNode({
        id: "node",
        groupId: "grp",
        shapeFamily: "capsule",
        shape,
        zSlot: { plane: "base", order: 1 },
      }),
    ).toThrow(/duplicate/i);
  });

  it("refuses a dangling reference rather than building half a scene", () => {
    const scene = seeded();

    expect(() => scene.registerGlassGroup({ id: "orphan", backdropSourceId: "missing" })).toThrow(
      GlassSceneError,
    );
    expect(() =>
      scene.registerGlassNode({
        id: "orphan",
        groupId: "missing",
        shapeFamily: "capsule",
        shape,
        zSlot: { plane: "base", order: 0 },
      }),
    ).toThrow(/unknown/i);
  });

  it("carries a structured code on every structural error", () => {
    const scene = seeded();

    try {
      scene.registerGlassGroup({ id: "grp", backdropSourceId: "src" });
      expect.unreachable("expected a duplicate-id error");
    } catch (error) {
      expect(error).toBeInstanceOf(GlassSceneError);
      expect((error as GlassSceneError).code).toBe("duplicate-id");
    }
  });

  it("patches a descriptor without disturbing the rest of it", () => {
    const scene = seeded();
    scene.updateGlassGroup("grp", { samplingPadding: 40 });

    expect(scene.glassGroup("grp")?.descriptor.samplingPadding).toBe(40);
    expect(scene.glassGroup("grp")?.descriptor.backdropSourceId).toBe("src");
  });

  it("clears an override when a patch names the key with undefined", () => {
    const scene = createGlassScene({ platform: workingPlatform });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({
      id: "g",
      backdropSourceId: "page",
      backdrop: { tone: "dark" },
      samplingPadding: 60,
    });

    // A declarative binding must be able to take a prop back. Omitting the key
    // keeps it; naming it with undefined removes it.
    scene.updateGlassGroup("g", { samplingPadding: 80 });
    expect(scene.glassGroup("g")?.descriptor.backdrop).toEqual({ tone: "dark" });

    scene.updateGlassGroup("g", { backdrop: undefined });
    expect(scene.glassGroup("g")?.descriptor.backdrop).toBeUndefined();
    expect(scene.glassGroup("g")?.descriptor.samplingPadding).toBe(80);
    expect(scene.resolve().groups[0]?.state.analysis).toBe("none");
  });

  it("clears a node override the same way, restoring what it inherits", () => {
    const scene = createGlassScene({ platform: workingPlatform });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({
      id: "g",
      backdropSourceId: "page",
      material: { variant: "regular", dimming: { scrim: 0.3, direction: "darken" } },
    });
    scene.registerGlassNode({
      id: "n",
      groupId: "g",
      shapeFamily: "capsule",
      shape,
      zSlot: { plane: "base", order: 0 },
      variant: "clear",
    });

    expect(scene.resolve().nodes[0]?.material.variant).toBe("clear");

    scene.updateGlassNode("n", { variant: undefined });
    expect(scene.resolve().nodes[0]?.material.variant).toBe("regular");
  });

  it("re-parents a node only onto a group that exists", () => {
    const scene = seeded();
    scene.registerGlassGroup({ id: "grp2", backdropSourceId: "src" });

    scene.updateGlassNode("node", { groupId: "grp2" });
    expect(scene.nodesOfGroup("grp2").map((node) => node.descriptor.id)).toEqual(["node"]);
    expect(scene.nodesOfGroup("grp")).toEqual([]);

    expect(() => scene.updateGlassNode("node", { groupId: "missing" })).toThrow(/unknown/i);
  });

  it("refuses to update or remove something that was never registered", () => {
    const scene = seeded();

    expect(() => scene.updateGlassNode("ghost", {})).toThrow(/unknown/i);
    expect(() => scene.removeGlassGroup("ghost")).toThrow(/unknown/i);
  });
});

describe("removal keeps references intact", () => {
  it("refuses to remove a source that groups still sample", () => {
    const scene = seeded();

    expect(() => scene.removeBackdropSource("src")).toThrow(/in use/i);
    expect(scene.backdropSource("src")).toBeDefined();
  });

  it("refuses to remove a group that still has nodes", () => {
    const scene = seeded();

    expect(() => scene.removeGlassGroup("grp")).toThrow(
      expect.objectContaining({ code: "in-use" }) as unknown as Error,
    );
    expect(scene.glassGroup("grp")).toBeDefined();
  });

  it("tears down cleanly from the leaves inward", () => {
    const scene = seeded();

    scene.removeGlassNode("node");
    scene.removeGlassGroup("grp");
    scene.removeBackdropSource("src");

    expect(scene.glassNode("node")).toBeUndefined();
    expect(scene.glassGroup("grp")).toBeUndefined();
    expect(scene.backdropSource("src")).toBeUndefined();
  });
});

describe("dirty-epoch bookkeeping (§Core model invariant)", () => {
  it("registers a source clean — nothing to rebuild before anything changed", () => {
    const scene = seeded();

    expect(scene.dirtyBackdropSources()).toEqual([]);
  });

  it("marks a source dirty and offers exactly one rebuild for it", () => {
    const scene = seeded();
    scene.markBackdropSourceDirty("src");

    expect(scene.dirtyBackdropSources().map((source) => source.descriptor.id)).toEqual(["src"]);

    const requests = scene.consumeDirtyBackdropSources(1);

    expect(requests).toHaveLength(1);
    expect(requests[0]?.sourceId).toBe("src");
    expect(requests[0]?.groupIds).toEqual(["grp"]);
  });

  it("collapses several dirty marks in one frame into one rebuild", () => {
    const scene = seeded();
    scene.markBackdropSourceDirty("src");
    scene.markBackdropSourceDirty("src");
    scene.markBackdropSourceDirty("src");

    expect(scene.consumeDirtyBackdropSources(1)).toHaveLength(1);
  });

  it("hands a source out at most once per frame, however often the renderer asks", () => {
    const scene = seeded();
    scene.markBackdropSourceDirty("src");

    expect(scene.consumeDirtyBackdropSources(1)).toHaveLength(1);
    expect(scene.consumeDirtyBackdropSources(1)).toEqual([]);
    expect(scene.consumeDirtyBackdropSources(1)).toEqual([]);
  });

  it("rebuilds nothing on the next frame if nothing changed again", () => {
    const scene = seeded();
    scene.markBackdropSourceDirty("src");

    scene.consumeDirtyBackdropSources(1);

    expect(scene.consumeDirtyBackdropSources(2)).toEqual([]);
  });

  it("defers a mark that arrives after this frame consumed to the next frame", () => {
    const scene = seeded();
    scene.markBackdropSourceDirty("src");

    scene.consumeDirtyBackdropSources(1);
    scene.markBackdropSourceDirty("src");
    expect(scene.consumeDirtyBackdropSources(1)).toEqual([]);

    expect(scene.consumeDirtyBackdropSources(2)).toHaveLength(1);
  });

  it("serves every group from one source rebuild — never one per group", () => {
    const scene = seeded();
    scene.registerGlassGroup({ id: "grp2", backdropSourceId: "src" });
    scene.registerGlassGroup({ id: "grp3", backdropSourceId: "src" });
    scene.markBackdropSourceDirty("src");

    const requests = scene.consumeDirtyBackdropSources(1);

    expect(requests).toHaveLength(1);
    expect(requests[0]?.groupIds).toEqual(["grp", "grp2", "grp3"]);
  });

  it("never rebuilds a source nothing samples", () => {
    const scene = seeded();
    scene.registerBackdropSource({
      id: "unused",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    scene.markBackdropSourceDirty("unused");

    expect(scene.consumeDirtyBackdropSources(1)).toEqual([]);
  });

  it("never offers a dom source — the compositor owns its blur, so there is no pyramid", () => {
    const scene = createGlassScene({ platform: workingPlatform });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "g", backdropSourceId: "page" });
    scene.markBackdropSourceDirty("page");

    expect(scene.dirtyBackdropSources()).toEqual([]);
    expect(scene.consumeDirtyBackdropSources(1)).toEqual([]);
  });

  it("carries the source's resolution policy on the request", () => {
    const scene = createGlassScene({ platform: workingPlatform });
    scene.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
      resolution: { scale: 0.5, maxDimension: 1024 },
    });
    scene.registerGlassGroup({ id: "g", backdropSourceId: "src" });
    scene.markBackdropSourceDirty("src");

    expect(scene.consumeDirtyBackdropSources(1)[0]?.resolution).toEqual({
      scale: 0.5,
      maxDimension: 1024,
    });
  });

  it("refuses to mark an unknown source dirty", () => {
    const scene = seeded();

    expect(() => scene.markBackdropSourceDirty("ghost")).toThrow(/unknown/i);
  });

  it("patches a texture source's resolution policy", () => {
    const scene = seeded();
    scene.updateBackdropSource("src", { resolution: { scale: 0.5, maxDimension: 512 } });
    scene.markBackdropSourceDirty("src");

    expect(scene.consumeDirtyBackdropSources(1)[0]?.resolution).toEqual({
      scale: 0.5,
      maxDimension: 512,
    });
  });

  it("refuses a resolution policy or a source probe on a dom source", () => {
    const scene = createGlassScene({ platform: workingPlatform });
    scene.registerBackdropSource({ id: "page", kind: "dom" });

    const wrongKind = expect.objectContaining({
      code: "wrong-source-kind",
    }) as unknown as Error;

    expect(() =>
      scene.updateBackdropSource("page", { resolution: DEFAULT_BACKDROP_RESOLUTION }),
    ).toThrow(wrongKind);
    expect(() =>
      scene.setSourceProbe("page", { taint: "clean", textureCompatibility: "compatible" }),
    ).toThrow(wrongKind);
  });
});

describe("same-plane overlap (X1, dev mode)", () => {
  function twoNodes(a: Rect, b: Rect, planes: readonly ["base" | "overlay", "base" | "overlay"]) {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "g", backdropSourceId: "page" });
    scene.registerGlassNode({
      id: "a",
      groupId: "g",
      shapeFamily: "capsule",
      shape,
      zSlot: { plane: planes[0], order: 0 },
    });
    scene.registerGlassNode({
      id: "b",
      groupId: "g",
      shapeFamily: "capsule",
      shape,
      zSlot: { plane: planes[1], order: 1 },
    });
    scene.setNodeBounds("a", a);
    scene.setNodeBounds("b", b);
    return { scene, diagnostics };
  }

  it("errors when two surfaces overlap inside one plane", () => {
    const { scene, diagnostics } = twoNodes(rect(0, 0), rect(20, 20), ["base", "base"]);

    expect(scene.checkSamePlaneOverlap()).toEqual([{ plane: "base", nodeIds: ["a", "b"] }]);
    expect(diagnostics.reported[0]).toMatchObject({
      code: "same-plane-overlap",
      severity: "error",
      subjects: ["a", "b"],
    });
  });

  it("says nothing about the same overlap in a different plane — that is the cross-plane case", () => {
    const { scene, diagnostics } = twoNodes(rect(0, 0), rect(20, 20), ["base", "overlay"]);

    expect(scene.checkSamePlaneOverlap()).toEqual([]);
    expect(diagnostics.reported).toEqual([]);
  });

  it("allows adjacent surfaces — a toolbar is the common case", () => {
    const { scene, diagnostics } = twoNodes(rect(0, 0), rect(40, 0), ["base", "base"]);

    expect(scene.checkSamePlaneOverlap()).toEqual([]);
    expect(diagnostics.reported).toEqual([]);
  });

  it("skips nodes whose bounds were never measured", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "g", backdropSourceId: "page" });
    for (const id of ["a", "b"]) {
      scene.registerGlassNode({
        id,
        groupId: "g",
        shapeFamily: "capsule",
        shape,
        zSlot: { plane: "base", order: 0 },
      });
    }

    expect(scene.checkSamePlaneOverlap()).toEqual([]);
  });

  it("reports one overlapping pair once, however many frames it survives", () => {
    const { scene, diagnostics } = twoNodes(rect(0, 0), rect(20, 20), ["base", "base"]);

    for (let frame = 0; frame < 4; frame += 1) scene.checkSamePlaneOverlap();

    expect(diagnostics.reported).toHaveLength(1);
  });

  it("skips the whole check outside dev mode", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics, devMode: false });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "g", backdropSourceId: "page" });
    for (const [id, bounds] of [
      ["a", rect(0, 0)],
      ["b", rect(20, 20)],
    ] as const) {
      scene.registerGlassNode({
        id,
        groupId: "g",
        shapeFamily: "capsule",
        shape,
        zSlot: { plane: "base", order: 0 },
      });
      scene.setNodeBounds(id, bounds);
    }

    expect(scene.checkSamePlaneOverlap()).toEqual([]);
    expect(diagnostics.reported).toEqual([]);
  });

  it("finds every overlapping pair, not just the first", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "g", backdropSourceId: "page" });
    for (const [id, bounds] of [
      ["a", rect(0, 0)],
      ["b", rect(10, 10)],
      ["c", rect(20, 20)],
    ] as const) {
      scene.registerGlassNode({
        id,
        groupId: "g",
        shapeFamily: "capsule",
        shape,
        zSlot: { plane: "base", order: 0 },
      });
      scene.setNodeBounds(id, bounds);
    }

    expect(scene.checkSamePlaneOverlap()).toEqual([
      { plane: "base", nodeIds: ["a", "b"] },
      { plane: "base", nodeIds: ["a", "c"] },
      { plane: "base", nodeIds: ["b", "c"] },
    ]);
  });
});

describe("cross-group proxy overlap (X1, dev mode)", () => {
  /** Two one-node groups on the same source, `gap` px apart, each padded by `padding`. */
  function neighbours(gap: number, padding: number, plane: "base" | "overlay" = "base") {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });

    for (const [id, x] of [
      ["left", 0],
      ["right", 40 + gap],
    ] as const) {
      scene.registerGlassGroup({
        id,
        backdropSourceId: "page",
        samplingPadding: padding,
        mergeDistance: padding,
      });
      scene.registerGlassNode({
        id: `${id}-node`,
        groupId: id,
        shapeFamily: "capsule",
        shape,
        zSlot: { plane, order: 0 },
      });
      scene.setNodeBounds(`${id}-node`, rect(x, 0));
    }
    return { scene, diagnostics };
  }

  it("catches the 8px-gap case S1 measured, which mergeDistance cannot", () => {
    const { scene, diagnostics } = neighbours(8, 60);

    expect(scene.checkGroupProxyOverlap()).toEqual([
      { plane: "base", groupIds: ["left", "right"] },
    ]);
    expect(diagnostics.reported[0]).toMatchObject({
      code: "group-proxy-overlap",
      severity: "warning",
      subjects: ["left", "right"],
    });
    expect(diagnostics.reported[0]?.message).toContain("mergeDistance cannot help");
    // The per-group constraint is satisfied, which is exactly why this second
    // check has to exist.
    expect(diagnostics.reported.map((finding) => finding.code)).not.toContain(
      "merge-distance-below-padding",
    );
  });

  it("says nothing when the gap exceeds the sum of the paddings", () => {
    const { scene, diagnostics } = neighbours(200, 60);

    expect(scene.checkGroupProxyOverlap()).toEqual([]);
    expect(diagnostics.reported).toEqual([]);
  });

  it("says nothing about surfaces that share one group — one group, one proxy", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "toolbar", backdropSourceId: "page", samplingPadding: 60 });
    for (const [id, x] of [
      ["a", 0],
      ["b", 48],
    ] as const) {
      scene.registerGlassNode({
        id,
        groupId: "toolbar",
        shapeFamily: "capsule",
        shape,
        zSlot: { plane: "base", order: 0 },
      });
      scene.setNodeBounds(id, rect(x, 0));
    }

    expect(scene.checkGroupProxyOverlap()).toEqual([]);
  });

  it("says nothing across planes — each plane has its own proxy layer", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    for (const [id, plane] of [
      ["base-group", "base"],
      ["overlay-group", "overlay"],
    ] as const) {
      scene.registerGlassGroup({ id, backdropSourceId: "page", samplingPadding: 60 });
      scene.registerGlassNode({
        id: `${id}-node`,
        groupId: id,
        shapeFamily: "capsule",
        shape,
        zSlot: { plane, order: 0 },
      });
      scene.setNodeBounds(`${id}-node`, rect(0, 0));
    }

    expect(scene.checkGroupProxyOverlap()).toEqual([]);
  });

  it("ignores groups with nothing measured yet", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    for (const id of ["a", "b"]) {
      scene.registerGlassGroup({ id, backdropSourceId: "page", samplingPadding: 60 });
      scene.registerGlassNode({
        id: `${id}-node`,
        groupId: id,
        shapeFamily: "capsule",
        shape,
        zSlot: { plane: "base", order: 0 },
      });
    }

    expect(scene.checkGroupProxyOverlap()).toEqual([]);
  });

  it("reports one pair once, however many frames it survives", () => {
    const { scene, diagnostics } = neighbours(8, 60);

    for (let frame = 0; frame < 4; frame += 1) scene.checkGroupProxyOverlap();

    expect(diagnostics.reported).toHaveLength(1);
  });

  it("skips the check outside dev mode", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics, devMode: false });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    for (const [id, x] of [
      ["a", 0],
      ["b", 48],
    ] as const) {
      scene.registerGlassGroup({ id, backdropSourceId: "page", samplingPadding: 60 });
      scene.registerGlassNode({
        id: `${id}-node`,
        groupId: id,
        shapeFamily: "capsule",
        shape,
        zSlot: { plane: "base", order: 0 },
      });
      scene.setNodeBounds(`${id}-node`, rect(x, 0));
    }

    expect(scene.checkGroupProxyOverlap()).toEqual([]);
    expect(diagnostics.reported).toEqual([]);
  });
});

describe("resolution", () => {
  it("resolves every group's state from the scene's probe inputs", () => {
    const scene = seeded();
    const resolution = scene.resolve();

    expect(resolution.groups).toHaveLength(1);
    expect(resolution.groups[0]?.state).toMatchObject({
      configuredSource: "texture",
      activeRenderer: "webgpu",
      analysis: "exact",
      health: "ok",
    });
  });

  it("threads a group's hint into its resolved analysis (X6)", () => {
    const scene = createGlassScene({ platform: workingPlatform });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "g", backdropSourceId: "page", backdrop: { tone: "dark" } });

    const group = scene.resolve().groups[0];
    expect(group?.state.analysis).toBe("hint");
    expect(group?.hint).toEqual({ availability: "author-hint", hint: { tone: "dark" } });
  });

  it("gives each group a foreground mode its own state can support", () => {
    const scene = createGlassScene({ platform: workingPlatform });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({
      id: "g",
      backdropSourceId: "page",
      foreground: { mode: "sampled-async", rateHz: 4, hysteresis: 0.06 },
    });

    const group = scene.resolve().groups[0];
    expect(group?.foreground.adaptation).toEqual({ mode: "fixed" });
    expect(group?.foreground.downgraded).toEqual({ from: "sampled-async", to: "fixed" });
  });

  it("resolves each node's material, inheriting the group's variant and dimming", () => {
    const scene = createGlassScene({ platform: workingPlatform });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({
      id: "g",
      backdropSourceId: "page",
      material: { variant: "clear", dimming: { scrim: 0.3, direction: "darken" } },
    });
    scene.registerGlassNode({
      id: "n",
      groupId: "g",
      shapeFamily: "capsule",
      shape,
      zSlot: { plane: "base", order: 0 },
    });

    expect(scene.resolve().nodes[0]?.material).toEqual({
      variant: "clear",
      adaptation: "constrained",
      dimming: { scrim: 0.3, direction: "darken" },
    });
  });

  it("warns when a group's nodes disagree on a variant", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({
      id: "g",
      backdropSourceId: "page",
      material: { variant: "regular", dimming: { scrim: 0.3, direction: "darken" } },
    });
    scene.registerGlassNode({
      id: "a",
      groupId: "g",
      shapeFamily: "capsule",
      shape,
      zSlot: { plane: "base", order: 0 },
    });
    scene.registerGlassNode({
      id: "b",
      groupId: "g",
      shapeFamily: "capsule",
      shape,
      zSlot: { plane: "base", order: 1 },
      variant: "clear",
    });

    scene.resolve();

    expect(diagnostics.reported.map((finding) => finding.code)).toContain("variant-mixing");
  });

  it("reports only the groups whose state actually moved", () => {
    const scene = seeded();
    expect(scene.resolve().changes).toHaveLength(1); // first resolution: undefined -> resolved
    expect(scene.resolve().changes).toEqual([]);

    scene.setPlatformProbe({ ...workingPlatform, deviceHealth: "lost" });
    const changes = scene.resolve().changes;

    expect(changes).toHaveLength(1);
    expect(changes[0]?.groupId).toBe("grp");
    expect(changes[0]?.change).toEqual({ kind: "demoted", reason: "device-lost" });
  });

  it("names the recovery when the device comes back", () => {
    const scene = seeded();
    scene.resolve();
    scene.setPlatformProbe({ ...workingPlatform, deviceHealth: "lost" });
    scene.resolve();

    scene.setPlatformProbe(workingPlatform);
    expect(scene.resolve().changes[0]?.change).toEqual({
      kind: "recovered",
      from: "device-lost",
    });
  });

  it("re-resolves after a source is re-probed — the source-replaced recovery", () => {
    const scene = seeded();
    scene.setSourceProbe("src", { taint: "tainted", textureCompatibility: "compatible" });

    expect(scene.resolve().groups[0]?.state.demotionReason).toBe("tainted-source");

    scene.setSourceProbe("src", { taint: "clean", textureCompatibility: "compatible" });
    expect(scene.resolve().groups[0]?.state.health).toBe("ok");
  });

  it("applies governor pressure globally, and per group when asked", () => {
    const scene = seeded();
    scene.registerGlassGroup({ id: "grp2", backdropSourceId: "src" });

    scene.setGovernorPressure("demote-tier");
    for (const group of scene.resolve().groups) {
      expect(group.state.demotionReason).toBe("governor");
    }

    scene.setGovernorPressure("none");
    scene.setGovernorPressure("demote-tier", "grp2");
    const byId = new Map(scene.resolve().groups.map((group) => [group.groupId, group.state]));

    expect(byId.get("grp")?.health).toBe("ok");
    expect(byId.get("grp2")?.demotionReason).toBe("governor");
  });

  it("fills in a group's sampling geometry, defaulting merge distance to the padding (X1)", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "defaults", backdropSourceId: "page" });
    scene.registerGlassGroup({ id: "padded", backdropSourceId: "page", samplingPadding: 60 });

    const byId = new Map(scene.resolve().groups.map((group) => [group.groupId, group.sampling]));

    expect(byId.get("defaults")).toEqual(DEFAULT_GROUP_SAMPLING);
    expect(byId.get("padded")).toEqual({ samplingPadding: 60, mergeDistance: 60 });
    expect(diagnostics.reported).toEqual([]);
  });

  it("warns when merge distance falls below sampling padding — the double-filter case", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({
      id: "tight",
      backdropSourceId: "page",
      samplingPadding: 60,
      mergeDistance: 8,
    });

    const sampling = scene.resolve().groups[0]?.sampling;

    // Reported, never coerced: widening the merge distance would change which
    // members fuse, and that is the author's decision to make.
    expect(sampling).toEqual({ samplingPadding: 60, mergeDistance: 8 });
    expect(diagnostics.reported[0]).toMatchObject({
      code: "merge-distance-below-padding",
      severity: "warning",
      subjects: ["tight"],
    });
  });

  it("accepts a merge distance equal to the padding — the constraint is inclusive", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({
      id: "exact",
      backdropSourceId: "page",
      samplingPadding: 32,
      mergeDistance: 32,
    });

    scene.resolve();

    expect(diagnostics.reported).toEqual([]);
  });

  it("skips the sampling-geometry check outside dev mode", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics, devMode: false });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({
      id: "tight",
      backdropSourceId: "page",
      samplingPadding: 60,
      mergeDistance: 8,
    });

    scene.resolve();

    expect(diagnostics.reported).toEqual([]);
  });

  it("keeps the default geometry satisfying X1's own constraint", () => {
    expect(DEFAULT_GROUP_SAMPLING.mergeDistance).toBeGreaterThanOrEqual(
      DEFAULT_GROUP_SAMPLING.samplingPadding,
    );
    expect(DEFAULT_GROUP_SAMPLING.samplingPadding).toBeGreaterThan(0);
  });

  it("starts on the nominal policy and stays quiet until a host reports otherwise", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = createGlassScene({ platform: workingPlatform, diagnostics });

    const policy = scene.accessibilityPolicy();
    expect(policy.reducedTransparency).toBe(false);
    expect(policy.material.frost).toBe("nominal");
    expect(diagnostics.reported).toEqual([]);

    // The undetectable-preference warning is about a platform fact a host
    // reported — not about a host that has not spoken yet.
    scene.setSystemAccessibility({
      reducedTransparency: false,
      reducedMotion: false,
      increasedContrast: false,
      forcedColors: false,
      reducedTransparencySupported: false,
    });
    scene.accessibilityPolicy();

    expect(diagnostics.reported.map((finding) => finding.code)).toEqual([
      "reduced-transparency-undetectable",
    ]);
  });

  it("carries the root's accessibility policy on the resolution itself", () => {
    const scene = createGlassScene({
      platform: workingPlatform,
      accessibility: {
        reducedTransparency: true,
        reducedMotion: false,
        increasedContrast: false,
        forcedColors: false,
        reducedTransparencySupported: true,
      },
    });

    expect(scene.resolve().accessibility.material.frost).toBe("increased");
  });

  it("resolves the accessibility policy once for the whole root", () => {
    const scene = createGlassScene({
      platform: workingPlatform,
      accessibility: {
        reducedTransparency: false,
        reducedMotion: true,
        increasedContrast: false,
        forcedColors: false,
        reducedTransparencySupported: true,
      },
    });

    expect(scene.accessibilityPolicy().motion.overshoot).toBe("none");

    scene.setAccessibilityOverrides({ reducedMotion: false });
    expect(scene.accessibilityPolicy().motion.overshoot).toBe("elastic");
  });
});
