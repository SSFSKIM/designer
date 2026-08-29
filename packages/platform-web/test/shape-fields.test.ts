/**
 * The corner reference and the concentric parent link, end to end through the
 * browser layer (Decision Log #23(c)).
 *
 * The point of making these scene-model fields was that the shipping pipeline
 * could then carry them. The pipeline is `registerHost` → core's descriptor →
 * `GlassNodeRenderInput` → `toSurfaceInput` → the renderer, and a break at any
 * link leaves the fields exactly as inert as they were in v1 — present on the
 * type, set by nobody. So each link is asserted, not only the first.
 *
 * Absence is asserted as carefully as presence: the renderer defaults an unset
 * reference to `"apple-continuous"`, and a browser layer that wrote an explicit
 * value for a surface that never asked would be deciding geometry on the app's
 * behalf.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { createGlassRoot, type GlassRoot } from "../src/root";
import type { MediaMatcher } from "../src/media-policy";

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

function root(): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    matcher,
    diagnosticSink: () => {},
  });
  roots.push(created);
  created.registerGroup({ id: "g1" });
  return created;
}

function host(instance: GlassRoot): HTMLElement {
  const element = document.createElement("button");
  instance.plane("base").hostLayer.append(element);
  return element;
}

beforeEach(() => {
  (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
});

afterEach(() => {
  for (const instance of roots) instance.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
});

describe("registerHost carries the shape fields into the scene", () => {
  it("records the corner reference the app declared", () => {
    const instance = root();
    const handle = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      reference: "figma-smoothing",
    });

    expect(instance.scene.glassNode(handle.nodeId)?.descriptor.reference).toBe("figma-smoothing");
  });

  it("leaves it absent when the app said nothing", () => {
    const instance = root();
    const handle = instance.registerHost({ host: host(instance), groupId: "g1" });

    expect(instance.scene.glassNode(handle.nodeId)?.descriptor.reference).toBeUndefined();
  });

  it("patches it, and clears it on a present-but-undefined key", () => {
    const instance = root();
    const handle = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      reference: "figma-smoothing",
    });

    handle.update({ reference: "apple-continuous" });
    expect(instance.scene.glassNode(handle.nodeId)?.descriptor.reference).toBe("apple-continuous");

    handle.update({ reference: undefined });
    expect(instance.scene.glassNode(handle.nodeId)?.descriptor.reference).toBeUndefined();
  });

  it("records a concentric parent, and refuses an unknown one at the call", () => {
    const instance = root();
    const parent = instance.registerHost({ host: host(instance), groupId: "g1", nodeId: "track" });
    const child = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      concentricOf: { nodeId: parent.nodeId, inset: 4 },
    });

    expect(instance.scene.glassNode(child.nodeId)?.descriptor.concentricOf).toEqual({
      nodeId: "track",
      inset: 4,
    });

    expect(() =>
      instance.registerHost({
        host: host(instance),
        groupId: "g1",
        concentricOf: { nodeId: "never-registered", inset: 4 },
      }),
    ).toThrow();
  });
});

describe("the render input carries them to the renderer", () => {
  /** One frame, so `renderInput()` has something in it. */
  function framed(instance: GlassRoot): void {
    instance.runFrame(16);
  }

  it("forwards the reference, and omits it where the scene omits it", () => {
    const instance = root();
    const declared = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      nodeId: "declared",
      reference: "figma-smoothing",
    });
    const silent = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      nodeId: "silent",
    });
    framed(instance);

    const nodes = instance.renderInput()?.planes.flatMap((plane) => plane.nodes) ?? [];
    const byId = new Map(nodes.map((entry) => [entry.nodeId, entry]));

    expect(byId.get(declared.nodeId)?.reference).toBe("figma-smoothing");
    expect(byId.get(silent.nodeId)).toBeDefined();
    expect(byId.get(silent.nodeId)?.reference).toBeUndefined();
    // Omitted, not present-and-undefined: the renderer's `?? "apple-continuous"`
    // reads the same either way, but `"reference" in node` does not, and the
    // structural view is what a devtool inspects.
    expect(Object.hasOwn(byId.get(silent.nodeId) ?? {}, "reference")).toBe(false);
  });

  it("forwards the concentric link", () => {
    const instance = root();
    instance.registerHost({ host: host(instance), groupId: "g1", nodeId: "track" });
    const child = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      nodeId: "indicator",
      concentricOf: { nodeId: "track", inset: 6 },
    });
    framed(instance);

    const nodes = instance.renderInput()?.planes.flatMap((plane) => plane.nodes) ?? [];
    const entry = nodes.find((node) => node.nodeId === child.nodeId);

    expect(entry?.concentricOf).toEqual({ nodeId: "track", inset: 6 });
  });
});
