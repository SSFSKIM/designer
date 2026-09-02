/**
 * W11a — the layer pair a GPU-tier group carries when it samples nothing.
 *
 * jsdom cannot paint, so nothing here is a pixel: the claim is about what the
 * root hands the bridge. A dom-mode group on a live GPU tier draws its material
 * as a layer the browser composites over its proxy, and that layer's alpha is
 * the CSS tier's (`unsampledMaterials`) — one number for both tiers. A group
 * sampling a texture composites in the shader and must carry no pair; a
 * CSS-tier root paints in place and must carry none either.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import type { MediaMatcher } from "../src/media-policy";
import { unsampledMaterials } from "../src/optics";
import { toRendererGroups } from "../src/renderer-bridge";
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

function withHost(instance: GlassRoot, sourceId?: string): void {
  const host = document.createElement("button");
  instance.plane("base").hostLayer.append(host);
  instance.registerGroup({ id: "g1", ...(sourceId === undefined ? {} : { backdropSourceId: sourceId }) });
  instance.registerHost({ host, groupId: "g1", plane: "base" });
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

/** The renderer's own fake device: enough of WebGPU for a frame to draw. */
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

describe("the unsampled layer pair (W11a)", () => {
  it("rides a dom-mode group on a live GPU tier, and the bridge forwards it", async () => {
    stubCanvasContexts();
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    withHost(instance);
    await instance.ready();
    instance.runFrame(16);

    const group = instance.renderInput()?.groups.find((entry) => entry.groupId === "g1");
    expect(group?.state.activeRenderer).toBe("webgpu");
    expect(group?.state.samplingBackend).toBe("css-backdrop");
    expect(group?.unsampledMaterial).toEqual(unsampledMaterials().regular);

    const input = instance.renderInput();
    expect(input).toBeDefined();
    if (input === undefined) return;
    const forwarded = toRendererGroups(input, () => false)[0]?.groups.find((entry) => entry.groupId === "g1");
    expect(forwarded?.backdropSourceId).toBeUndefined();
    expect(forwarded?.unsampledMaterial).toEqual(unsampledMaterials().regular);
  });

  it("follows the profile the root was given, not the module constant", async () => {
    stubCanvasContexts();
    const instance = root({
      renderer: "webgpu",
      webgpu: { device: idleDevice() },
      materialProfile: { optics: { regular: { tintAlpha: 0.3 } } },
    });
    withHost(instance);
    await instance.ready();
    instance.runFrame(16);

    const group = instance.renderInput()?.groups.find((entry) => entry.groupId === "g1");
    expect(group?.unsampledMaterial).toEqual(
      unsampledMaterials({ optics: { regular: { tintAlpha: 0.3 } } }).regular,
    );
    expect(group?.unsampledMaterial?.tintAlpha).not.toBe(unsampledMaterials().regular.tintAlpha);
  });

  it("is absent on a CSS-tier root, which paints in place", () => {
    const instance = root();
    withHost(instance);
    instance.runFrame(16);

    const group = instance.renderInput()?.groups.find((entry) => entry.groupId === "g1");
    expect(group?.state.activeRenderer).toBe("css");
    expect(group?.unsampledMaterial).toBeUndefined();
  });

  it("is absent on a group sampling a supplied texture, which composites in the shader", async () => {
    stubCanvasContexts();
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    instance.registerBackdropSource({
      id: "src",
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    withHost(instance, "src");
    await instance.ready();
    instance.setBackdropTexture("src", { kind: "canvas", canvas: document.createElement("canvas") });
    instance.runFrame(16);

    const group = instance.renderInput()?.groups.find((entry) => entry.groupId === "g1");
    expect(group?.state.samplingBackend).toBe("gpu-texture");
    expect(group?.unsampledMaterial).toBeUndefined();
  });
});
