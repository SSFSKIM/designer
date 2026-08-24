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
  type FrameContext,
  type FramePhase,
  type FrameParticipant,
  type GlassScene,
  type PlatformProbe,
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

  it("reports the frame's rebuilds even when no participant consumed them", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({ id: "a", collect: () => scene.markBackdropSourceDirty("src") });

    expect(scheduler.runFrame({ id: 1, timeMs: 0 }).rebuilds).toHaveLength(1);
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

  it("carries an unconsumed rebuild into the next frame", () => {
    const scene = seeded();
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({ id: "a" });

    scene.markBackdropSourceDirty("src");
    expect(scheduler.runFrame({ id: 1, timeMs: 0 }).rebuilds).toHaveLength(1);
    expect(scheduler.runFrame({ id: 2, timeMs: 16 }).rebuilds).toHaveLength(0);
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
  it("errors when the graph is restructured while the renderer is walking it", () => {
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

  it("allows registration in collect and update, where a host legitimately mutates", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);
    const scheduler = createFrameScheduler({ scene });
    scheduler.addParticipant({
      id: "a",
      collect: () =>
        scene.registerGlassNode({
          id: "late",
          groupId: "grp",
          shapeFamily: "capsule",
          shape,
          zSlot: { plane: "base", order: 9 },
        }),
      update: () => scene.updateGlassNode("late", { interaction: "hover" }),
    });

    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(diagnostics.reported).toEqual([]);
    expect(scene.glassNode("late")?.descriptor.interaction).toBe("hover");
  });

  it("says nothing about registration outside a frame — the normal path", () => {
    const diagnostics = createDiagnosticsChannel();
    const scene = seeded(diagnostics);

    scene.registerGlassGroup({ id: "later", backdropSourceId: "src" });

    expect(diagnostics.reported).toEqual([]);
  });
});
