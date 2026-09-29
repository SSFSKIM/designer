/**
 * Frames on demand (#48).
 *
 * The root used to re-arm `requestAnimationFrame` on every frame, so a page whose
 * glass had not changed in minutes kept drawing it sixty times a second. The
 * contract now: a frame runs because something asked for one, the loop keeps
 * running while a frame leaves work behind, and it stops when nothing does. These
 * pin both halves — that an unchanged scene goes quiet, and that everything that
 * used to be picked up "because the loop was running anyway" still schedules the
 * frame that picks it up.
 *
 * Most cases step by hand (`autoStart: false`) and read `framePending`, the one
 * bit the loop acts on. The last block drives the real loop through a stubbed
 * `requestAnimationFrame`.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { releaseBackdropToneScratch } from "../src/backdrop-tone";
import { GLASS_CHANNEL_PROPERTIES } from "../src/channels";
import type { MediaMatcher } from "../src/media-policy";
import { createGlassRoot, type GlassRoot, type GlassRootOptions } from "../src/root";

class StubResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

const matcher: MediaMatcher = () => ({
  matches: false,
  media: "",
  addEventListener: () => {},
  removeEventListener: () => {},
});

let roots: GlassRoot[] = [];

function root(options: Partial<GlassRootOptions> = {}): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    windowActivation: "active",
    diagnosticSink: () => {},
    ...options,
  });
  roots.push(created);
  return created;
}

/** Steps frames until the root reports nothing pending; returns how many ran. */
function settle(instance: GlassRoot, from = 16, limit = 600): number {
  let frames = 0;
  let at = from;
  while (instance.framePending && frames < limit) {
    instance.runFrame(at);
    at += 16;
    frames += 1;
  }
  return frames;
}

function host(instance: GlassRoot, groupId = "g"): ReturnType<GlassRoot["registerHost"]> {
  if (instance.scene.glassGroup(groupId) === undefined) instance.registerGroup({ id: groupId });
  const element = document.createElement("div");
  instance.plane("base").hostLayer.append(element);
  return instance.registerHost({ host: element, groupId });
}

/** MutationObserver delivers on a microtask. */
const flushMicrotasks = (): Promise<void> => new Promise((resolve) => queueMicrotask(resolve));

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
});

afterEach(() => {
  for (const instance of roots) instance.destroy();
  roots = [];
  document.body.replaceChildren();
  // The scratch canvas is module-wide; a test's raster stub must not outlive it.
  releaseBackdropToneScratch();
  vi.restoreAllMocks();
  vi.useRealTimers();
});

describe("an unchanged scene", () => {
  it("goes quiet after the frames its setup asked for", () => {
    const instance = root();
    host(instance);
    expect(instance.framePending).toBe(true);

    const frames = settle(instance);
    expect(frames).toBeGreaterThan(0);
    expect(frames).toBeLessThan(10);
    expect(instance.framePending).toBe(false);

    // And stays quiet: a frame drawn anyway leaves nothing behind.
    instance.runFrame(10_000);
    expect(instance.framePending).toBe(false);
  });
});

describe("what schedules a frame", () => {
  it("a scene change outside a frame, including one made straight on `root.scene`", () => {
    const instance = root();
    host(instance);
    settle(instance);

    instance.scene.updateGlassGroup("g", { mergeDistance: 32 });
    expect(instance.framePending).toBe(true);
  });

  it("a host patch, a promotion and a geometry invalidation", () => {
    const instance = root();
    const handle = host(instance);
    settle(instance);

    handle.update({ thickness: 12 });
    expect(instance.framePending).toBe(true);
    settle(instance);

    handle.invalidateGeometry();
    expect(instance.framePending).toBe(true);
    settle(instance);

    handle.promoteTo("overlay");
    expect(instance.framePending).toBe(true);
  });

  it("a write to a host's inline channels, whoever made it", async () => {
    const instance = root();
    const handle = host(instance);
    settle(instance);
    await flushMicrotasks();
    expect(instance.framePending).toBe(false);

    // The documented styling surface: an app driving its own motion.
    handle.host.style.setProperty(GLASS_CHANNEL_PROPERTIES.glow, "0.5");
    await flushMicrotasks();
    expect(instance.framePending).toBe(true);
  });

  it("but not the root's own writes while it draws", async () => {
    const instance = root();
    const handle = host(instance);
    settle(instance);
    await flushMicrotasks();

    // A presence transit writes the materialization channel on every frame it runs.
    handle.update({ present: false });
    settle(instance);
    await flushMicrotasks();
    expect(instance.framePending).toBe(false);
  });

  it("the material, the scheme, the pose and the accessibility overrides", () => {
    const instance = root();
    host(instance);
    const changes: (() => void)[] = [
      () => instance.setMaterialProfile({}),
      () => instance.setColorScheme("dark"),
      () => instance.setWindowActivation("inactive"),
      () => instance.setAccessibilityOverrides({ reducedMotion: true }),
    ];
    for (const change of changes) {
      settle(instance);
      change();
      expect(instance.framePending).toBe(true);
    }
  });

  it("a new listener, and a backdrop source marked by its owner", () => {
    const instance = root();
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    host(instance);
    settle(instance);

    instance.subscribe(() => false);
    expect(instance.framePending).toBe(true);
    settle(instance);

    instance.markBackdropSourceDirty("src");
    expect(instance.framePending).toBe(true);
    settle(instance);

    // A source nobody declared is nothing to draw, and no reason to throw.
    instance.markBackdropSourceDirty("unknown");
    expect(instance.framePending).toBe(false);
  });

  it("an image supplied before it decoded, once it loads", () => {
    const instance = root();
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    host(instance);
    const image = document.createElement("img");
    instance.setBackdropTexture("src", { kind: "image", image });
    settle(instance);

    const before = instance.scene.backdropSource("src")?.dirtyEpoch ?? 0;
    image.dispatchEvent(new Event("load"));
    expect(instance.framePending).toBe(true);
    expect(instance.scene.backdropSource("src")?.dirtyEpoch).toBe(before + 1);

    // Withdrawn, it is not watched any more.
    instance.setBackdropTexture("src", undefined);
    settle(instance);
    image.dispatchEvent(new Event("load"));
    expect(instance.framePending).toBe(false);
  });
});

describe("what keeps frames coming", () => {
  it("a presence transit, for exactly as long as it travels", () => {
    const instance = root();
    const handle = host(instance);
    settle(instance);

    handle.update({ present: false });
    const frames = settle(instance);
    // The materialization driver's transit is hundreds of milliseconds at 16 ms a
    // frame: many frames, then none.
    expect(frames).toBeGreaterThan(5);
    expect(instance.framePending).toBe(false);
    expect(handle.host.style.getPropertyValue(GLASS_CHANNEL_PROPERTIES.materialization)).toBe("0");
  });

  it("a listener that does not return false — the behaviour listeners were written for", () => {
    const instance = root();
    host(instance);
    settle(instance);

    let ticks = 0;
    const stop = instance.subscribe(() => {
      ticks += 1;
    });
    for (let frame = 0; frame < 5; frame += 1) {
      expect(instance.framePending).toBe(true);
      instance.runFrame(1000 + frame * 16);
    }
    expect(ticks).toBe(5);
    expect(instance.framePending).toBe(true);

    stop();
    settle(instance, 2000);
    expect(instance.framePending).toBe(false);
  });

  it("stops for a listener that returns false", () => {
    const instance = root();
    host(instance);
    let ticks = 0;
    instance.subscribe(() => {
      ticks += 1;
      return false;
    });
    settle(instance);
    expect(instance.framePending).toBe(false);
    expect(ticks).toBeGreaterThan(0);
  });
});

describe("the backdrop tone on the CSS tier", () => {
  function sampled(texture: (canvas: HTMLCanvasElement) => Parameters<GlassRoot["setBackdropTexture"]>[1]) {
    let reads = 0;
    // jsdom has no raster; only that boundary is replaced.
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockImplementation(() => ({
      clearRect() {},
      drawImage() {},
      getImageData() {
        reads += 1;
        return { data: new Uint8ClampedArray(4 * 512 * 512).fill(128) };
      },
    }) as unknown as CanvasRenderingContext2D);
    const instance = root({ renderer: "css" });
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    instance.registerGroup({ id: "g", backdropSourceId: "src" });
    const canvas = document.createElement("canvas");
    canvas.width = 4;
    canvas.height = 4;
    instance.setBackdropTexture("src", texture(canvas));
    host(instance);
    return { instance, reads: () => reads };
  }

  it("reads a canvas supplied `live: false` only when it is marked", () => {
    vi.useFakeTimers();
    const { instance, reads } = sampled((canvas) => ({ kind: "canvas", canvas, live: false }));
    settle(instance);
    const first = reads();
    expect(first).toBeGreaterThan(0);

    vi.advanceTimersByTime(5000);
    expect(instance.framePending).toBe(false);
    instance.runFrame(9000);
    expect(reads()).toBe(first);

    instance.markBackdropSourceDirty("src");
    vi.advanceTimersByTime(300);
    settle(instance, 10_000);
    expect(reads()).toBeGreaterThan(first);
  });

  it("schedules the frame that reads a live canvas on the cadence, and only that", () => {
    vi.useFakeTimers();
    const { instance, reads } = sampled((canvas) => ({ kind: "canvas", canvas }));
    settle(instance);
    const first = reads();
    expect(first).toBeGreaterThan(0);
    expect(instance.framePending).toBe(false);

    // The cadence runs out on a timer, not on a frame nobody would draw — and
    // keeps running out: each reading owes the next one.
    let previous = first;
    for (let refresh = 0; refresh < 5; refresh += 1) {
      vi.advanceTimersByTime(300);
      expect(instance.framePending).toBe(true);
      settle(instance, 5000 + refresh * 1000);
      expect(reads()).toBeGreaterThan(previous);
      previous = reads();
    }
  });
});

describe("the loop", () => {
  let callbacks: Map<number, FrameRequestCallback>;
  let next = 1;
  const flushFrame = (timeMs: number): void => {
    const pending = [...callbacks.values()];
    callbacks.clear();
    for (const callback of pending) callback(timeMs);
  };

  beforeEach(() => {
    callbacks = new Map();
    vi.spyOn(window, "requestAnimationFrame").mockImplementation((callback) => {
      const handle = next++;
      callbacks.set(handle, callback);
      return handle;
    });
    vi.spyOn(window, "cancelAnimationFrame").mockImplementation((handle) => {
      callbacks.delete(handle);
    });
  });

  it("schedules one frame per demand and none when idle", () => {
    const instance = root({ autoStart: true });
    host(instance);
    expect(callbacks.size).toBe(1);

    let at = 0;
    for (let frame = 0; frame < 20 && callbacks.size > 0; frame += 1) flushFrame((at += 16));
    expect(callbacks.size).toBe(0);
    expect(instance.framePending).toBe(false);

    instance.requestFrame();
    instance.requestFrame();
    expect(callbacks.size).toBe(1);
  });

  it("hands a frame after idle one frame's interval, not the idle gap", () => {
    const instance = root({ autoStart: true });
    host(instance);
    const deltas: number[] = [];
    let at = 0;
    for (let frame = 0; frame < 20 && callbacks.size > 0; frame += 1) flushFrame((at += 16));

    instance.subscribe(({ deltaMs }) => {
      deltas.push(deltaMs);
      return false;
    });
    flushFrame(at + 60_000);
    expect(deltas).toEqual([16]);
  });

  it("arms itself after a frame stepped by hand on a started root leaves demand", () => {
    const instance = root({ autoStart: true });
    host(instance);
    let wantsMore = false;
    instance.subscribe(() => wantsMore);
    let at = 0;
    for (let frame = 0; frame < 20 && callbacks.size > 0; frame += 1) flushFrame((at += 16));
    expect(callbacks.size).toBe(0);

    // The demand arises inside a frame an app drives by hand, outside the loop.
    wantsMore = true;
    instance.runFrame(at + 16);
    expect(instance.framePending).toBe(true);
    expect(callbacks.size).toBe(1);
  });

  it("does not run while stopped, and picks the demand back up on start", () => {
    const instance = root({ autoStart: true });
    instance.stop();
    callbacks.clear();
    host(instance);
    expect(callbacks.size).toBe(0);
    instance.start();
    expect(callbacks.size).toBe(1);
  });
});
