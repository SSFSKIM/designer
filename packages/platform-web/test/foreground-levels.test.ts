/**
 * W27a — the named ink levels reach the host, and Apple's floor on the fourth
 * one is named where it is reachable.
 *
 * The arithmetic behind the alphas is pinned in `css-tier.test.ts`. What is
 * asserted here is the wiring: that both tiers write the three tokens onto the
 * host beside `--vitrea-foreground`, that releasing a host takes them back off,
 * and that the quaternary diagnostic fires on the pair it is about — a surface
 * below the material's thin/thick knee on a page whose own CSS names the token —
 * and stays silent otherwise.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { FOREGROUND_LEVELS, FOREGROUND_LEVEL_TOKENS } from "../src/css-tier";
import type { PlatformDiagnostic } from "../src/diagnostics";
import { documentStylesNameToken } from "../src/ink-stylesheet";
import type { MediaMatcher } from "../src/media-policy";
import { MATERIAL_SOURCE_SIZE } from "../src/optics";
import { createGlassRoot, type GlassRoot, type GlassRootOptions } from "../src/root";

import { createFakeGpu } from "../../renderer-webgpu/test/harness/fake-gpu";
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
let sheets: HTMLStyleElement[] = [];
let restoreCanvasContexts: (() => void) | undefined;
let reported: PlatformDiagnostic[] = [];

function root(options: GlassRootOptions = {}): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: (entry) => {
      if (entry.origin === "platform") reported.push(entry.diagnostic);
    },
    ...options,
  });
  roots.push(created);
  return created;
}

function withHost(instance: GlassRoot, nodeId = "n1"): HTMLElement {
  const host = document.createElement("button");
  instance.plane("base").hostLayer.append(host);
  instance.registerGroup({ id: "g1" });
  instance.registerHost({ host, groupId: "g1", plane: "base", nodeId });
  return host;
}

/** An application stylesheet that reads one of the published levels. */
function appSheetNaming(token: string): HTMLStyleElement {
  const sheet = document.createElement("style");
  sheet.textContent = `.caption { color: var(${token}); }`;
  document.head.append(sheet);
  sheets.push(sheet);
  return sheet;
}

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
  reported = [];
});

afterEach(() => {
  restoreCanvasContexts?.();
  restoreCanvasContexts = undefined;
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  for (const sheet of sheets) sheet.remove();
  roots = [];
  containers = [];
  sheets = [];
});

describe("the named ink levels on the host", () => {
  it("are written by the CSS tier beside the primary", () => {
    const instance = root();
    const host = withHost(instance);
    instance.runFrame(16);

    expect(host.style.getPropertyValue("--vitrea-foreground")).not.toBe("");
    for (const level of FOREGROUND_LEVELS) {
      expect(host.style.getPropertyValue(FOREGROUND_LEVEL_TOKENS[level])).not.toBe("");
    }
  });

  it("are written by the WebGPU tier too, so an app need not know which drew", async () => {
    stubCanvasContexts();
    const instance = root({ renderer: "webgpu", webgpu: { device: idleDevice() } });
    const host = withHost(instance);
    await instance.ready();
    instance.runFrame(16);

    expect(instance.capabilities("g1")?.activeRenderer).toBe("webgpu");
    for (const level of FOREGROUND_LEVELS) {
      expect(host.style.getPropertyValue(FOREGROUND_LEVEL_TOKENS[level])).not.toBe("");
    }
  });

  it("come back off when the host is released, like every other token", () => {
    const instance = root();
    const host = document.createElement("button");
    instance.plane("base").hostLayer.append(host);
    instance.registerGroup({ id: "g1" });
    const handle = instance.registerHost({ host, groupId: "g1", plane: "base", nodeId: "n1" });
    instance.runFrame(16);
    handle.release();

    for (const level of FOREGROUND_LEVELS) {
      expect(host.style.getPropertyValue(FOREGROUND_LEVEL_TOKENS[level])).toBe("");
    }
  });
});

describe("Apple's floor on the quaternary level", () => {
  /*
   * jsdom reports a zero-sized border box, so every surface here resolves below
   * the material's thin/thick knee — which is the population the finding is
   * about. Pinned rather than relied on silently: if jsdom ever grew layout, a
   * span of 0 would still be below the knee and this would still read true.
   */
  const knee = (MATERIAL_SOURCE_SIZE.sizeSpanMin + MATERIAL_SOURCE_SIZE.sizeSpanMax) / 2;

  it("warns when a thin surface meets a document that styles with the token", () => {
    expect(knee).toBeGreaterThan(0);
    appSheetNaming(FOREGROUND_LEVEL_TOKENS.quaternary);

    const instance = root({ devMode: true });
    withHost(instance);
    instance.runFrame(16);

    const finding = reported.find((entry) => entry.code === "quaternary-ink-on-thin-material");
    expect(finding).toBeDefined();
    expect(finding?.subjects).toEqual(["n1"]);
    expect(finding?.message).toContain(FOREGROUND_LEVEL_TOKENS.tertiary);
  });

  it("stays silent on a page that never names the token", () => {
    const instance = root({ devMode: true });
    withHost(instance);
    instance.runFrame(16);

    expect(reported.map((entry) => entry.code)).not.toContain("quaternary-ink-on-thin-material");
  });

  it("stays silent outside dev mode, where no finding is reported at all", () => {
    appSheetNaming(FOREGROUND_LEVEL_TOKENS.quaternary);

    const instance = root({ devMode: false });
    withHost(instance);
    instance.runFrame(16);

    expect(reported.map((entry) => entry.code)).not.toContain("quaternary-ink-on-thin-material");
  });

  it("reads the document's own rules, and only for the token asked about", () => {
    appSheetNaming(FOREGROUND_LEVEL_TOKENS.quaternary);

    expect(documentStylesNameToken(document, FOREGROUND_LEVEL_TOKENS.quaternary)).toBe(true);
    // `--vitrea-foreground` is a prefix of all three level tokens, so a scan that
    // matched loosely would answer yes to everything vitrea publishes.
    expect(documentStylesNameToken(document, FOREGROUND_LEVEL_TOKENS.secondary)).toBe(false);
  });
});
