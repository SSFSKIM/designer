/**
 * `GlassRoot.subscribe` — the seam that lets an adapter join the root's frame
 * loop instead of running a second one beside it.
 *
 * This is the framework-agnostic half of Decision Log #30(c). Before it, the
 * only thing an adapter could do with the root's cadence was ignore it: the
 * scheduler is private to `createGlassRoot`, so `vitrea-react` ran its own
 * `requestAnimationFrame` and every future Vue or Svelte binding would have
 * copied that. The properties below are what an adapter is entitled to rely on,
 * so they are pinned rather than left to whatever the implementation happens to
 * do.
 *
 * Frames are stepped by hand (`autoStart: false`), because the contract is about
 * ordering and delivery, not about rAF.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { createGlassRoot, type GlassFrameTick, type GlassRoot } from "../src/root";
import type { MediaMatcher } from "../src/media-policy";
import type { PlatformDiagnostic } from "../src/diagnostics";

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

let roots: GlassRoot[] = [];
let containers: HTMLElement[] = [];
let diagnostics: PlatformDiagnostic[] = [];

function root(): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: (entry) => {
      if (entry.origin === "platform") diagnostics.push(entry.diagnostic);
    },
  });
  roots.push(created);
  return created;
}

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
});

afterEach(() => {
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
  diagnostics = [];
});

describe("joining the root's frame loop", () => {
  it("delivers one tick per frame, numbered from one", () => {
    const instance = root();
    const seen: GlassFrameTick[] = [];
    instance.subscribe((tick) => seen.push(tick));

    instance.runFrame(16);
    instance.runFrame(32);

    expect(seen.map((tick) => tick.id)).toEqual([1, 2]);
    expect(seen.map((tick) => tick.timeMs)).toEqual([16, 32]);
  });

  /*
   * Zero on the first frame, not "the time since the epoch". A driver that
   * integrated the first delta would resolve a spring's whole trajectory in one
   * step on the frame it mounted — which is exactly the bug the react ticker
   * carries its own `previousMs === undefined` guard for.
   */
  it("reports no delta on the first frame, and the real gap after it", () => {
    const instance = root();
    const deltas: number[] = [];
    instance.subscribe(({ deltaMs }) => deltas.push(deltaMs));

    instance.runFrame(1000);
    instance.runFrame(1016);
    instance.runFrame(1049);

    expect(deltas).toEqual([0, 16, 33]);
  });

  /*
   * The scene's phase is `undefined` outside a frame, and that is the assertion:
   * a listener runs past the frame's end, not inside one of its five phases. It
   * matters because the scene is frozen from `update` onward and reports a
   * `frame-phase-violation` for a descriptor mutation there — so a listener that
   * ran mid-frame could not register, patch or measure, which is most of what an
   * adapter's per-frame work consists of.
   */
  it("runs listeners past the end of the frame, not inside one of its phases", () => {
    const instance = root();
    let phaseAtNotify: string | undefined = "never ran";
    instance.subscribe(() => {
      phaseAtNotify = instance.scene.framePhase;
    });

    instance.runFrame(16);

    expect(phaseAtNotify).toBeUndefined();
  });

  it("lets a listener patch the scene without tripping the phase guard", () => {
    const instance = root();
    instance.registerGroup({ id: "g1" });
    instance.subscribe(() => {
      instance.scene.updateGlassGroup("g1", { mergeDistance: 64 });
    });

    instance.runFrame(16);

    expect(diagnostics.filter((entry) => entry.code === "frame-listener-failed")).toEqual([]);
    expect(instance.scene.glassGroup("g1")?.descriptor.mergeDistance).toBe(64);
  });

  it("stops delivering once unsubscribed", () => {
    const instance = root();
    let count = 0;
    const unsubscribe = instance.subscribe(() => (count += 1));

    instance.runFrame(16);
    unsubscribe();
    instance.runFrame(32);

    expect(count).toBe(1);
  });

  /*
   * A surface unmounting on a click unsubscribes from inside the notify loop.
   * Iterating the live set would then skip whichever listener came after it —
   * a defect that reads as "the morph stopped animating", not as a bug.
   */
  it("keeps notifying the rest when a listener unsubscribes itself mid-frame", () => {
    const instance = root();
    const seen: string[] = [];
    const unsubscribeFirst = instance.subscribe(() => {
      seen.push("first");
      unsubscribeFirst();
    });
    instance.subscribe(() => seen.push("second"));

    instance.runFrame(16);

    expect(seen).toEqual(["first", "second"]);
  });

  it("does not deliver to a listener another listener removed in the same frame", () => {
    const instance = root();
    const seen: string[] = [];
    instance.subscribe(() => {
      seen.push("first");
      unsubscribeSecond();
    });
    const unsubscribeSecond = instance.subscribe(() => seen.push("second"));

    instance.runFrame(16);

    expect(seen).toEqual(["first"]);
  });

  it("stops delivering after destroy", () => {
    const instance = root();
    let count = 0;
    instance.subscribe(() => (count += 1));

    instance.runFrame(16);
    instance.destroy();
    instance.runFrame(32);

    expect(count).toBe(1);
  });
});

describe("a listener that throws", () => {
  /*
   * Dropped, not tolerated. A listener that throws on one frame throws on every
   * frame, so keeping it subscribed turns one adapter's bug into an unbounded
   * diagnostic storm — and on a hand-driven root, into a `runFrame` that throws
   * and therefore into a material that stops drawing.
   */
  it("is unsubscribed and reported, and the frame still completes", () => {
    const instance = root();
    const after: string[] = [];
    instance.subscribe(() => {
      throw new Error("adapter bug");
    });
    instance.subscribe(() => after.push("ran"));

    expect(() => instance.runFrame(16)).not.toThrow();
    expect(after).toEqual(["ran"]);

    const reported = diagnostics.filter((entry) => entry.code === "frame-listener-failed");
    expect(reported).toHaveLength(1);
    expect(reported[0]?.severity).toBe("error");
    expect(reported[0]?.message).toContain("adapter bug");

    // Dropped: a second frame neither re-runs it nor re-reports it.
    instance.runFrame(32);
    expect(after).toEqual(["ran", "ran"]);
    expect(diagnostics.filter((entry) => entry.code === "frame-listener-failed")).toHaveLength(1);
  });

  it("names the throw even when what was thrown is not an Error", () => {
    const instance = root();
    instance.subscribe(() => {
      throw "a bare string";
    });

    instance.runFrame(16);

    expect(diagnostics[0]?.message).toContain("a bare string");
  });
});
