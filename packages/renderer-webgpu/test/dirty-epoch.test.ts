/**
 * The §Core model invariant, driven by core's own scene and scheduler.
 *
 * > blur/analysis pyramids belong to `BackdropSource`, rebuilt **at most once per
 * > dirty source per frame** — never per group. Static backdrops rebuild nothing.
 *
 * C6's acceptance asks for this **instrumented**, which means measuring the
 * composition rather than asserting the guard. So this file stands up a real
 * `GlassScene` and a real `FrameScheduler`, registers a participant that claims
 * through the renderer's own `RebuildLedger`, and reads the ledger's counters.
 *
 * ## Why core is imported by relative path
 *
 * `@vitrea/core` reaches this package through a dynamic import (X7's lazy seam),
 * so a package-level dependency back on core would close a cycle that neither
 * `pnpm -r build` nor `tsc` can order. The two modules used here — `scene` and
 * `scheduler` — import only geometry and motion types, both of which *are*
 * dependencies of this package, so a direct module import resolves cleanly and
 * adds no edge to the package graph.
 */

import { describe, expect, it } from "vitest";

import { createGlassScene, type GlassScene } from "../../core/src/scene";
import { createFrameScheduler, type FrameContext } from "../../core/src/scheduler";
import { createRebuildLedger, type RebuildLedger } from "../src/rebuild-ledger";

const PLATFORM = {
  webgpu: "available",
  backdropFilter: true,
  backdropProxyConformance: "pass",
  deviceHealth: "ok",
} as const;

const CLEAN_PROBE = { taint: "clean", textureCompatibility: "compatible" } as const;

function sceneWithTextureSource(sourceIds: readonly string[], groupsPerSource = 1): GlassScene {
  const scene = createGlassScene({ platform: PLATFORM });
  for (const sourceId of sourceIds) {
    scene.registerBackdropSource({ id: sourceId, kind: "texture", probe: CLEAN_PROBE });
    for (let i = 0; i < groupsPerSource; i += 1) {
      scene.registerGlassGroup({ id: `${sourceId}:g${i}`, backdropSourceId: sourceId });
    }
  }
  return scene;
}

/**
 * A renderer stand-in: it does what `pyramid.ts` does at the frame boundary —
 * consume the dirty set in `write`, claim through the ledger — and nothing else.
 * Faking the GPU work would only obscure what is being measured.
 */
function participantOver(ledger: RebuildLedger, id = "renderer") {
  const builds: string[] = [];
  return {
    builds,
    participant: {
      id,
      write(context: FrameContext) {
        ledger.beginFrame(context.frame.id);
        for (const request of context.consumeDirtyBackdropSources()) {
          if (ledger.claim(request.sourceId)) builds.push(request.sourceId);
        }
      },
    },
  };
}

describe("the ledger on its own", () => {
  it("allows one claim per source per frame and refuses the rest", () => {
    const ledger = createRebuildLedger();
    ledger.beginFrame(1);

    expect(ledger.claim("bg")).toBe(true);
    expect(ledger.claim("bg")).toBe(false);
    expect(ledger.claim("bg")).toBe(false);
    expect(ledger.claim("other")).toBe(true);

    expect(ledger.countInFrame("bg")).toBe(1);
    expect(ledger.rebuilds).toBe(2);
    expect(ledger.refusedDuplicates).toBe(2);
    expect(ledger.peakPerSourcePerFrame).toBe(1);
  });

  it("resets the tally at a frame boundary but not the totals", () => {
    const ledger = createRebuildLedger();
    ledger.beginFrame(1);
    ledger.claim("bg");
    ledger.beginFrame(2);

    expect(ledger.countInFrame("bg")).toBe(0);
    expect(ledger.claim("bg")).toBe(true);
    expect(ledger.rebuilds).toBe(2);
    expect(ledger.peakPerSourcePerFrame).toBe(1);
  });
});

describe("one dirty source serving many groups", () => {
  it("rebuilds once, not once per group", () => {
    // The half of the invariant that says "never per group".
    const scene = sceneWithTextureSource(["bg"], 5);
    const scheduler = createFrameScheduler({ scene });
    const ledger = createRebuildLedger();
    const renderer = participantOver(ledger);
    scheduler.addParticipant(renderer.participant);

    scene.markBackdropSourceDirty("bg");
    const report = scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(report.rebuilds).toHaveLength(1);
    expect(report.rebuilds[0]?.groupIds).toHaveLength(5);
    expect(renderer.builds).toEqual(["bg"]);
    expect(ledger.peakPerSourcePerFrame).toBe(1);
  });
});

describe("two participants in one frame", () => {
  it("hands the rebuild to the first and nothing to the second", () => {
    // core's own guard: one pass over the dirty set per frame id. A second
    // renderer — or the same one asking twice — gets an empty list.
    const scene = sceneWithTextureSource(["bg"]);
    const scheduler = createFrameScheduler({ scene });
    const ledger = createRebuildLedger();

    const first = participantOver(ledger, "first");
    const second = participantOver(ledger, "second");
    scheduler.addParticipant(first.participant);
    scheduler.addParticipant(second.participant);

    scene.markBackdropSourceDirty("bg");
    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(first.builds).toEqual(["bg"]);
    expect(second.builds).toEqual([]);
    expect(ledger.peakPerSourcePerFrame).toBe(1);
  });

  it("still refuses a second build when a participant consumes twice", () => {
    // The half core CANNOT see: a renderer that also rebuilt on some other path.
    // core hands out nothing the second time, but the ledger is what makes a
    // renderer-side second build impossible rather than merely unlikely.
    const scene = sceneWithTextureSource(["bg"]);
    const scheduler = createFrameScheduler({ scene });
    const ledger = createRebuildLedger();
    const builds: string[] = [];

    scheduler.addParticipant({
      id: "greedy",
      write(context) {
        ledger.beginFrame(context.frame.id);
        for (const request of context.consumeDirtyBackdropSources()) {
          if (ledger.claim(request.sourceId)) builds.push(request.sourceId);
        }
        // A lazy rebuild on first draw would look exactly like this.
        if (ledger.claim("bg")) builds.push("bg");
      },
    });

    scene.markBackdropSourceDirty("bg");
    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(builds).toEqual(["bg"]);
    expect(ledger.refusedDuplicates).toBe(1);
    expect(ledger.peakPerSourcePerFrame).toBe(1);
  });
});

describe("across frames", () => {
  it("rebuilds nothing for a static backdrop", () => {
    // "Static backdrops rebuild nothing."
    const scene = sceneWithTextureSource(["bg"]);
    const scheduler = createFrameScheduler({ scene });
    const ledger = createRebuildLedger();
    const renderer = participantOver(ledger);
    scheduler.addParticipant(renderer.participant);

    scene.markBackdropSourceDirty("bg");
    scheduler.runFrame({ id: 1, timeMs: 0 });
    for (let frame = 2; frame <= 30; frame += 1) {
      scheduler.runFrame({ id: frame, timeMs: frame * 16.7 });
    }

    expect(renderer.builds).toEqual(["bg"]);
    expect(ledger.rebuilds).toBe(1);
  });

  it("rebuilds once per frame for a source dirtied every frame", () => {
    // A video: `importExternalTexture` expires at task end, so it is dirty on
    // every frame that samples it — and still rebuilds exactly once per frame.
    const scene = sceneWithTextureSource(["video"], 3);
    const scheduler = createFrameScheduler({ scene });
    const ledger = createRebuildLedger();
    const renderer = participantOver(ledger);
    scheduler.addParticipant(renderer.participant);

    for (let frame = 1; frame <= 60; frame += 1) {
      scene.markBackdropSourceDirty("video");
      scheduler.runFrame({ id: frame, timeMs: frame * 16.7 });
    }

    expect(renderer.builds).toHaveLength(60);
    expect(ledger.peakPerSourcePerFrame).toBe(1);
  });

  it("holds the invariant across several sources at once", () => {
    const scene = sceneWithTextureSource(["a", "b", "c"], 2);
    const scheduler = createFrameScheduler({ scene });
    const ledger = createRebuildLedger();
    const renderer = participantOver(ledger);
    scheduler.addParticipant(renderer.participant);

    for (let frame = 1; frame <= 10; frame += 1) {
      for (const id of ["a", "b", "c"]) scene.markBackdropSourceDirty(id);
      scheduler.runFrame({ id: frame, timeMs: frame * 16.7 });
      for (const id of ["a", "b", "c"]) expect(ledger.countInFrame(id)).toBe(1);
    }

    expect(ledger.rebuilds).toBe(30);
    expect(ledger.peakPerSourcePerFrame).toBe(1);
  });
});

describe("a source nobody samples", () => {
  it("stays dirty rather than being rebuilt for nothing", () => {
    const scene = createGlassScene({ platform: PLATFORM });
    scene.registerBackdropSource({ id: "orphan", kind: "texture", probe: CLEAN_PROBE });
    const scheduler = createFrameScheduler({ scene });
    const ledger = createRebuildLedger();
    const renderer = participantOver(ledger);
    scheduler.addParticipant(renderer.participant);

    scene.markBackdropSourceDirty("orphan");
    const report = scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(renderer.builds).toEqual([]);
    expect(report.pendingSources).toEqual(["orphan"]);

    // It is picked up the moment a group arrives — which is also how device-loss
    // recovery gets its work back.
    scene.registerGlassGroup({ id: "late", backdropSourceId: "orphan" });
    scheduler.runFrame({ id: 2, timeMs: 16.7 });
    expect(renderer.builds).toEqual(["orphan"]);
  });
});

describe("dom sources", () => {
  it("never rebuild, because the compositor does their blur", () => {
    // §Core model: "In dom-backdrop mode the browser compositor does the blur;
    // the GPU builds no pyramid at all."
    const scene = createGlassScene({ platform: PLATFORM });
    scene.registerBackdropSource({ id: "page", kind: "dom" });
    scene.registerGlassGroup({ id: "g", backdropSourceId: "page" });

    const scheduler = createFrameScheduler({ scene });
    const ledger = createRebuildLedger();
    const renderer = participantOver(ledger);
    scheduler.addParticipant(renderer.participant);

    scene.markBackdropSourceDirty("page");
    scheduler.runFrame({ id: 1, timeMs: 0 });

    expect(renderer.builds).toEqual([]);
    expect(ledger.rebuilds).toBe(0);
  });
});

describe("a renderer that sits out a frame", () => {
  it("leaves the rebuild pending rather than losing it", () => {
    // Device-loss recovery, as the scheduler sees it: with no participant to take
    // the work, the source stays dirty and the next healthy frame picks it up.
    const scene = sceneWithTextureSource(["bg"]);
    const scheduler = createFrameScheduler({ scene });

    scene.markBackdropSourceDirty("bg");
    const lost = scheduler.runFrame({ id: 1, timeMs: 0 });
    expect(lost.rebuilds).toEqual([]);
    expect(lost.pendingSources).toEqual(["bg"]);

    const ledger = createRebuildLedger();
    const renderer = participantOver(ledger);
    scheduler.addParticipant(renderer.participant);
    const recovered = scheduler.runFrame({ id: 2, timeMs: 16.7 });

    expect(recovered.rebuilds).toHaveLength(1);
    expect(renderer.builds).toEqual(["bg"]);
  });
});
