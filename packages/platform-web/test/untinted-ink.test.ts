/**
 * W27a — the untinted material's ink is decided by the material, on both tiers.
 *
 * Closes the tech-debt entry "The untinted material's ink is still decided by
 * the colour scheme". `boundedForegroundLevel` brackets the level behind the
 * glyphs over every backdrop the surface can sit on, and where the whole bracket
 * lands on one side of the crossover the ink is decided outright. W3 wired that
 * in for author-tinted surfaces only, so a surface with no tint and no hint kept
 * `light-dark()` and the *colour scheme* chose its ink — over a body whose own
 * white tint dominates the level at the material's measured alpha. In a dark
 * scheme that is the light ink on a near-white surface: K5's failure class,
 * reached through the no-hint path rather than through a hint.
 *
 * Asserted at the root rather than on the declaration functions, because the
 * guards this closes were two — one per tier — and only a root exercises both
 * writing paths (`cssTierDeclarations` for one, `foregroundDeclarations` written
 * straight onto the host for the other).
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { FOREGROUND_INK } from "../src/css-tier";
import type { MediaMatcher } from "../src/media-policy";
import { createGlassRoot, type GlassRoot, type GlassRootOptions } from "../src/root";

import { createFakeGpu } from "../../renderer-webgpu/test/harness/fake-gpu";
// The WebGPU flag namespaces the renderer reads at pass creation; absent in jsdom.
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

let roots: GlassRoot[] = [];
let containers: HTMLElement[] = [];
let restoreCanvasContexts: (() => void) | undefined;

function root(options: GlassRootOptions = {}): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: () => {},
    ...options,
  });
  roots.push(created);
  return created;
}

/** One untinted surface in one group with no backdrop hint at all. */
function withHost(instance: GlassRoot): HTMLElement {
  const host = document.createElement("button");
  instance.plane("base").hostLayer.append(host);
  instance.registerGroup({ id: "g1" });
  instance.registerHost({ host, groupId: "g1", plane: "base", nodeId: "n1" });
  return host;
}

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

const idleDevice = (): GPUDevice => createFakeGpu().device;

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
  (globalThis as { ImageBitmap?: unknown }).ImageBitmap ??= class ImageBitmap {};
});

afterEach(() => {
  restoreCanvasContexts?.();
  restoreCanvasContexts = undefined;
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
});

describe("the untinted material's ink, with no hint at all", () => {
  it("is the material's own answer on the CSS tier, not the colour scheme's", () => {
    const instance = root();
    const host = withHost(instance);
    instance.runFrame(16);

    expect(instance.capabilities("g1")?.activeRenderer).toBe("css");
    expect(host.style.getPropertyValue("--vitrea-foreground")).toBe(FOREGROUND_INK.dark);
    expect(host.style.getPropertyValue("--vitrea-foreground")).not.toContain("light-dark(");
  });

  it("is the same answer on the WebGPU tier, over the material the renderer draws", async () => {
    stubCanvasContexts();
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    const host = withHost(instance);
    await instance.ready();
    instance.runFrame(16);

    // The tier under test, not the fallback: the CSS tier's half of this is the
    // assertion above, and the two guards were separate code.
    expect(instance.capabilities("g1")?.activeRenderer).toBe("webgpu");
    expect(host.style.getPropertyValue("--vitrea-foreground")).toBe(FOREGROUND_INK.dark);
    expect(host.style.getPropertyValue("--vitrea-foreground")).not.toContain("light-dark(");
  });
});
