/**
 * The frame-phase contract and its reference implementation.
 *
 * Core is passive: `runFrame` happens because a host called it. There is no
 * timer, no rAF, and no clock read anywhere below — the frame's time arrives as
 * a number, like every other measurement.
 */

import { describe, expect, it, vi } from "vitest";

import {
  FRAME_PHASES,
  createDiagnosticsChannel,
  createFrameScheduler,
  createGlassScene,
  type BackdropRebuildRequest,
  type FrameContext,
  type FramePhase,
  type FrameParticipant,
  type GlassScene,
  type PlatformProbe,
  type ShapeChannels,
} from "../src/index";

const workingPlatform: PlatformProbe = {
  webgpu: "available",
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

function seeded(diagnostics = createDiagnosticsChannel()): GlassScene {
  const scene = createGlassScene({ platform: workingPlatform, diagnostics });
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

/** Records the phase each hook saw, in order. */
function recorder(id: string, log: string[]): FrameParticipant {
  const hook = (phase: FramePhase) => (context: FrameContext) => {
    log.push(`${id}:${context.phase}`);
    expect(context.phase).toBe(phase);
  };
  return {
    id,
    collect: hook("collect"),
    read: hook("read"),
    update: hook("update"),
    write: hook("write"),
    render: hook("render"),
  };
}

describe("the phase contract", () => {
  it("names the five phases in pipeline order", () => {
    expect([...FRAME_PHASES]).toEqual(["collect", "read", "update", "write", "render"]);
  });

  it("walks every phase once, in order", () => {
    const log: string[] = [];
    const scheduler = createFrameScheduler({ scene: seeded() });
    scheduler.addParticipant(recorder("a", log));

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(log).toEqual(["a:collect", "a:read", "a:update", "a:write", "a:render"]);
  });

  it("runs every participant of a phase before moving to the next", () => {
    const log: string[] = [];
    const scheduler = createFrameScheduler({ scene: seeded() });
    scheduler.addParticipant(recorder("a", log));
    scheduler.addParticipant(recorder("b", log));

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(log).toEqual([
      "a:collect",
      "b:collect",
      "a:read",
      "b:read",
      "a:update",
      "b:update",
      "a:write",
      "b:write",
      "a:render",
      "b:render",
    ]);
  });

  it("skips a participant that declines a phase", () => {
    const seen: FramePhase[] = [];
    const scheduler = createFrameScheduler({ scene: seeded() });
    scheduler.addParticipant({
      id: "renderer-only",
      render: (context) => seen.push(context.phase),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(seen).toEqual(["render"]);
  });

  it("drops a removed participant, and replaces one registered under the same id", () => {
    const log: string[] = [];
    const scheduler = createFrameScheduler({ scene: seeded() });
    scheduler.addParticipant(recorder("a", log));
    scheduler.addParticipant(recorder("b", log));

    scheduler.removeParticipant("a");
    scheduler.runFrame({ id: 1, timeMs: 0 });
    expect(log.filter((entry) => entry.startsWith("a:"))).toEqual([]);

    log.length = 0;
    scheduler.addParticipant(recorder("b", log));
    scheduler.runFrame({ id: 2, timeMs: 16 });
    expect(log.filter((entry) => entry === "b:collect")).toHaveLength(1);
  });

  it("does nothing at all until a host calls runFrame — core is passive", () => {
    const collect = vi.fn();
    const scheduler = createFrameScheduler({ scene: seeded() });
    scheduler.addParticipant({ id: "a", collect });

    expect(collect).not.toHaveBeenCalled();

    scheduler.runFrame({ id: 1, timeMs: 0 });
    expect(collect).toHaveBeenCalledTimes(1);

    // No timer was armed, so no further calls can arrive on their own.
    expect(collect).toHaveBeenCalledTimes(1);
  });

  it("hands every hook the frame it was called for", () => {
    const frames: number[] = [];
    const scheduler = createFrameScheduler({ scene: seeded() });
    scheduler.addParticipant({
      id: "a",
      read: (context) => frames.push(context.frame.id),
      render: (context) => frames.push(context.frame.timeMs),
    });

    scheduler.runFrame({ id: 7, timeMs: 116.5 });

    expect(frames).toEqual([7, 116.5]);
  });
});

describe("the update phase resolves the scene", () => {
  it("resolves before any participant's update hook, so hooks see the result", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    let seen: string | undefined;
    scheduler.addParticipant({
      id: "a",
      update: (context) => {
        seen = context.resolution?.groups[0]?.state.analysis;
      },
    });

    const report = scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(seen).toBe("exact");
    expect(report.resolution.groups).toHaveLength(1);
  });

  it("has no resolution before the update phase", () => {
    const scheduler = createFrameScheduler({ scene: seeded() });
    const before: (boolean | undefined)[] = [];
    scheduler.addParticipant({
      id: "a",
      collect: (context) => before.push(context.resolution === undefined),
      read: (context) => before.push(context.resolution === undefined),
      update: (context) => before.push(context.resolution === undefined),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(before).toEqual([true, true, false]);
  });

  it("runs the dev-mode overlap check as part of the frame", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    scene.registerGlassNode({
      id: "second",
      groupId: "grp",
      shapeFamily: "capsule",
      shape,
      zSlot: { plane: "base", order: 1 },
    });
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "measurer",
      read: () => {
        scene.setNodeBounds("node", { x: 0, y: 0, width: 40, height: 40 });
        scene.setNodeBounds("second", { x: 10, y: 10, width: 40, height: 40 });
      },
    });

    const report = scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(report.overlaps).toEqual([{ plane: "base", nodeIds: ["node", "second"] }]);
    expect(diagnostics.reported.map((finding) => finding.code)).toContain("same-plane-overlap");
  });

  it("runs the cross-group proxy check in the same phase, on the same fresh bounds", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    scene.registerGlassGroup({ id: "neighbour", backdropSourceId: "src", samplingPadding: 60 });
    scene.registerGlassNode({
      id: "neighbour-node",
      groupId: "neighbour",
      shapeFamily: "capsule",
      shape,
      zSlot: { plane: "base", order: 1 },
    });
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "measurer",
      read: () => {
        scene.setNodeBounds("node", { x: 0, y: 0, width: 40, height: 40 });
        scene.setNodeBounds("neighbour-node", { x: 48, y: 0, width: 40, height: 40 });
      },
    });

    const report = scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(report.proxyOverlaps).toEqual([{ plane: "base", groupIds: ["grp", "neighbour"] }]);
    expect(diagnostics.reported.map((finding) => finding.code)).toContain("group-proxy-overlap");
  });
});

describe("dirty consumption is scoped to the write phase", () => {
  it("hands the frame's rebuilds to whoever asks during write", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    let requests = 0;
    scheduler.addParticipant({
      id: "collector",
      collect: () => scene.markBackdropSourceDirty("src"),
      write: (context) => {
        requests = context.consumeDirtyBackdropSources().length;
      },
    });

    const report = scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(requests).toBe(1);
    expect(report.rebuilds).toHaveLength(1);
    expect(report.rebuilds[0]?.sourceId).toBe("src");
    expect(report.pendingSources).toEqual([]);
  });

  it("gives the second asker in one frame nothing — one rebuild per dirty source", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    const counts: number[] = [];
    scheduler.addParticipant({
      id: "a",
      collect: () => scene.markBackdropSourceDirty("src"),
      write: (context) => counts.push(context.consumeDirtyBackdropSources().length),
    });
    scheduler.addParticipant({
      id: "b",
      write: (context) => counts.push(context.consumeDirtyBackdropSources().length),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(counts).toEqual([1, 0]);
  });

  it("leaves a rebuild no participant claimed pending and still dirty", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({ id: "a", collect: () => scene.markBackdropSourceDirty("src") });

    const unclaimed = scheduler.runFrame({ id: 1, timeMs: 0 });

    // The scheduler consumed nothing on the frame's behalf, so the source is
    // exactly as dirty as it was — the work is deferred, not silently built.
    expect(unclaimed.rebuilds).toEqual([]);
    expect(unclaimed.pendingSources).toEqual(["src"]);
    expect(scene.dirtyBackdropSources().map((source) => source.descriptor.id)).toEqual(["src"]);

    let claimed = 0;
    scheduler.addParticipant({
      id: "renderer",
      write: (context) => {
        claimed = context.consumeDirtyBackdropSources().length;
      },
    });
    const next = scheduler.runFrame({ id: 2, timeMs: 16 });

    expect(claimed).toBe(1);
    expect(next.rebuilds).toHaveLength(1);
    expect(next.pendingSources).toEqual([]);
  });

  it("refuses consumption outside the write phase, and says which phase asked", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    let outOfPhase: number | undefined;
    scheduler.addParticipant({
      id: "a",
      collect: () => scene.markBackdropSourceDirty("src"),
      render: (context) => {
        outOfPhase = context.consumeDirtyBackdropSources().length;
      },
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(outOfPhase).toBe(0);
    const violation = diagnostics.reported.find(
      (finding) => finding.code === "frame-phase-violation",
    );
    expect(violation?.severity).toBe("error");
    expect(violation?.message).toContain("render");
    expect(violation?.message).toContain("write");
  });

  it("carries an unclaimed rebuild through every frame that leaves it unclaimed", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({ id: "a" });

    scene.markBackdropSourceDirty("src");

    for (const id of [1, 2, 3]) {
      const report = scheduler.runFrame({ id, timeMs: id * 16 });
      expect(report.rebuilds).toEqual([]);
      expect(report.pendingSources).toEqual(["src"]);
    }

    // Nothing advanced `builtEpoch`, which is the mechanism: the source is dirty
    // for as long as no one has actually built it.
    expect(scene.backdropSource("src")?.builtEpoch).toBe(0);
  });

  it("hands a rebuild the device-loss frames could not do to the renderer that returns", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    let handed: readonly BackdropRebuildRequest[] = [];

    // The device is lost: the renderer participant is gone, and the backdrop
    // content keeps changing while it recovers.
    scene.markBackdropSourceDirty("src");
    expect(scheduler.runFrame({ id: 1, timeMs: 0 }).pendingSources).toEqual(["src"]);
    scene.markBackdropSourceDirty("src");
    expect(scheduler.runFrame({ id: 2, timeMs: 16 }).pendingSources).toEqual(["src"]);

    scheduler.addParticipant({
      id: "renderer",
      write: (context) => {
        handed = context.consumeDirtyBackdropSources();
      },
    });
    const recovered = scheduler.runFrame({ id: 3, timeMs: 32 });

    // One rebuild, at the latest epoch: the outage cost frames, not work.
    expect(handed).toHaveLength(1);
    expect(handed[0]?.epoch).toBe(2);
    expect(recovered.rebuilds).toEqual(handed);
    expect(recovered.pendingSources).toEqual([]);
  });
});

describe("a hook that throws", () => {
  it("propagates, and still leaves the scene outside a frame", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    const lost = new Error("device lost mid-render");
    scheduler.addParticipant({
      id: "renderer",
      render: () => {
        throw lost;
      },
    });

    expect(() => scheduler.runFrame({ id: 1, timeMs: 0 })).toThrow(lost);

    // A phase left stuck at "render" would turn the host's own recovery into a
    // stream of violations it never committed.
    expect(scene.framePhase).toBeUndefined();
    scene.setNodeBounds("node", { x: 0, y: 0, width: 10, height: 10 });
    expect(diagnostics.reported).toEqual([]);
  });

  it("gives back the rebuilds the failed frame claimed, so a one-shot dirty mark survives", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    let handed = 0;
    scheduler.addParticipant({
      id: "renderer",
      write: (context) => {
        handed = context.consumeDirtyBackdropSources().length;
      },
      render: () => {
        throw new Error("device lost mid-render");
      },
    });

    // The one dirty mark this source will ever get — a static raster imported
    // once, or a device-loss recovery. Nothing re-marks it.
    scene.markBackdropSourceDirty("src");
    expect(() => scheduler.runFrame({ id: 1, timeMs: 0 })).toThrow(/device lost/);

    expect(handed).toBe(1);
    // Consuming committed `builtEpoch` at hand-out, and the frame died before
    // anything was built. Left committed, the source would sit clean at an epoch
    // whose pixels were never imported, forever.
    expect(scene.backdropSource("src")?.builtEpoch).toBe(0);
    expect(scene.dirtyBackdropSources().map((source) => source.descriptor.id)).toEqual(["src"]);
  });

  it("lets the next frame actually build what the failed one gave back", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    let fail = true;
    const epochs: number[] = [];
    scheduler.addParticipant({
      id: "renderer",
      write: (context) => {
        for (const request of context.consumeDirtyBackdropSources()) epochs.push(request.epoch);
      },
      render: () => {
        if (fail) throw new Error("first frame dies");
      },
    });

    scene.markBackdropSourceDirty("src");
    expect(() => scheduler.runFrame({ id: 1, timeMs: 0 })).toThrow();
    fail = false;
    const recovered = scheduler.runFrame({ id: 2, timeMs: 16 });

    expect(epochs).toEqual([1, 1]);
    expect(recovered.pendingSources).toEqual([]);
    expect(scene.backdropSource("src")?.builtEpoch).toBe(1);
  });

  it("leaves a dirty mark that arrived after the hand-out alone", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "renderer",
      write: (context) => void context.consumeDirtyBackdropSources(),
      render: () => {
        // A live source keeps changing while the frame is failing; the rollback
        // restores the older `builtEpoch` and must not touch `dirtyEpoch`.
        scene.markBackdropSourceDirty("src");
        throw new Error("boom");
      },
    });

    scene.markBackdropSourceDirty("src");
    expect(() => scheduler.runFrame({ id: 1, timeMs: 0 })).toThrow();

    expect(scene.backdropSource("src")?.dirtyEpoch).toBe(2);
    expect(scene.backdropSource("src")?.builtEpoch).toBe(0);
  });

  it("rolls back only the frame that consumed, and only once", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "renderer",
      write: (context) => void context.consumeDirtyBackdropSources(),
    });

    scene.markBackdropSourceDirty("src");
    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(scene.rollbackDirtyBackdropSources(2)).toEqual([]);
    expect(scene.backdropSource("src")?.builtEpoch).toBe(1);
    expect(scene.rollbackDirtyBackdropSources(1)).toEqual(["src"]);
    expect(scene.backdropSource("src")?.builtEpoch).toBe(0);
    expect(scene.rollbackDirtyBackdropSources(1)).toEqual([]);
  });
});

describe("measurement is scoped to the read phase", () => {
  it("says nothing when bounds are set during read", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "a",
      read: () => scene.setNodeBounds("node", { x: 0, y: 0, width: 10, height: 10 }),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(diagnostics.reported).toEqual([]);
  });

  it("warns when bounds are set in another phase — that is the layout-thrash bug", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "a",
      render: () => scene.setNodeBounds("node", { x: 0, y: 0, width: 10, height: 10 }),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    const violation = diagnostics.reported.find(
      (finding) => finding.code === "frame-phase-violation",
    );
    expect(violation?.message).toContain("read");
    expect(scene.glassNode("node")?.bounds).toBeDefined();
  });

  it("says nothing about bounds set outside a frame — core cannot know what a host is doing", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);

    scene.setNodeBounds("node", { x: 0, y: 0, width: 10, height: 10 });

    expect(diagnostics.reported).toEqual([]);
  });
});

describe("structural change during a frame", () => {
  it("errors when the graph is restructured in write, once the frame has resolved", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "a",
      write: () => scene.removeGlassNode("node"),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    const violation = diagnostics.reported.find(
      (finding) => finding.code === "frame-phase-violation",
    );
    expect(violation?.severity).toBe("error");
    expect(violation?.subjects).toEqual(["node"]);
  });

  it("allows registration in collect and read, before the scene has resolved", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "a",
      collect: () =>
        scene.registerGlassNode({
          id: "collected",
          groupId: "grp",
          shapeFamily: "capsule",
          shape,
          zSlot: { plane: "base", order: 9 },
        }),
      read: () =>
        scene.registerGlassNode({
          id: "measured",
          groupId: "grp",
          shapeFamily: "capsule",
          shape,
          zSlot: { plane: "overlay", order: 0 },
        }),
    });

    const report = scheduler.runFrame({ id: 1, timeMs: 0 });

    // Both landed before `update` resolved, so the frame's resolution describes
    // them — which is exactly why these two phases stay open.
    expect(diagnostics.reported).toEqual([]);
    expect(report.resolution.nodes.map((node) => node.nodeId)).toEqual([
      "node",
      "collected",
      "measured",
    ]);
  });

  it("errors when the graph is restructured in update, after the frame has resolved", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "a",
      update: () =>
        scene.registerGlassNode({
          id: "late",
          groupId: "grp",
          shapeFamily: "capsule",
          shape,
          zSlot: { plane: "base", order: 9 },
        }),
    });

    const report = scheduler.runFrame({ id: 1, timeMs: 0 });

    const violation = diagnostics.reported.find(
      (finding) => finding.code === "frame-phase-violation",
    );
    expect(violation?.severity).toBe("error");
    expect(violation?.subjects).toEqual(["late"]);
    expect(violation?.message).toContain("update");
    // The reason it is an error: the node exists, and this frame's resolution
    // has already been written without it.
    expect(scene.glassNode("late")).toBeDefined();
    expect(report.resolution.nodes.map((node) => node.nodeId)).toEqual(["node"]);
  });

  it("errors on a descriptor patch in update too — the whole scene is frozen, not just its shape", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "a",
      update: () => scene.updateGlassNode("node", { variant: "clear" }),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    // A patch moves no entry in or out of the graph, but a node's variant feeds
    // its resolved material and its foreground its resolved adaptation — so a
    // patch after the resolve is just as stale as a registration would be.
    expect(diagnostics.reported[0]).toMatchObject({
      code: "frame-phase-violation",
      severity: "error",
      subjects: ["node"],
    });
    // Still applied: refusing it would leave the scene disagreeing with the host.
    expect(scene.glassNode("node")?.descriptor.variant).toBe("clear");
  });

  it("accepts the same patch in collect, before the frame resolves", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "a",
      collect: () => scene.updateGlassNode("node", { interaction: "hover" }),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(diagnostics.reported).toEqual([]);
    expect(scene.glassNode("node")?.descriptor.interaction).toBe("hover");
  });

  it("says nothing about registration outside a frame — the normal path", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);

    scene.registerGlassGroup({ id: "later", backdropSourceId: "src" });

    expect(diagnostics.reported).toEqual([]);
  });
});
