/**
 * X8 rider 3's refusal, raised where the app can act on it.
 *
 * Per-corner radii are post-v1 and this suite does not change that. What it
 * pins is the *honesty* of the limit at the public boundary, because the shape
 * of the gap was easy to walk into: `CornerRadii` is a Vec4 in every type
 * along the path, the CSS tier renders four radii correctly through
 * `border-radius`, and the proxy's mask path draws four — so four different
 * radii look supported right up until the WebGPU tier resolves the shape
 * against `radii[0]`, or `@vitrea/geometry` throws from inside a frame with
 * nothing left pointing at the registration that caused it.
 *
 * The finding is a warning rather than a refusal on purpose: the surface draws
 * either way, and taking a page down over a corner is the wrong trade for a
 * limit that is scheduled to lift.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { createGlassRoot, type GlassRoot } from "../src/root";
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

function root(devMode = true): GlassRoot {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    devMode,
    matcher,
    diagnosticSink: (entry) => {
      if (entry.origin === "platform") diagnostics.push(entry.diagnostic);
    },
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

const reported = (): readonly PlatformDiagnostic[] =>
  diagnostics.filter((entry) => entry.code === "non-uniform-radii");

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

describe("four different corner radii", () => {
  it("is reported at registration, naming the surface and both tiers' answers", () => {
    const instance = root();
    instance.registerHost({
      host: host(instance),
      groupId: "g1",
      nodeId: "asymmetric",
      radii: [4, 20, 4, 20],
    });

    expect(reported()).toHaveLength(1);
    expect(reported()[0]?.subjects).toEqual(["asymmetric"]);
    // What the app asked for, what each tier will do with it, and what to do —
    // a finding that only said "unsupported" would leave an author guessing
    // which of the two renderings they were looking at.
    expect(reported()[0]?.message).toContain("[4, 20, 4, 20]");
    expect(reported()[0]?.message).toContain("border-radius");
    expect(reported()[0]?.message).toContain("mirror-symmetric");
  });

  it("says nothing about a uniform surface, or about the default", () => {
    const instance = root();
    instance.registerHost({ host: host(instance), groupId: "g1", radii: [12, 12, 12, 12] });
    instance.registerHost({ host: host(instance), groupId: "g1" });

    expect(reported()).toEqual([]);
  });

  /*
   * A capsule's radius is recomputed from its measured box on every resize, and
   * a morph writes radii on every frame it runs for. Both go through `update`,
   * so a check that only ran at registration would miss the ways a surface
   * actually becomes non-uniform.
   */
  it("is reported when a patch makes a uniform surface non-uniform", () => {
    const instance = root();
    const handle = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      nodeId: "patched",
      radii: [12, 12, 12, 12],
    });
    expect(reported()).toEqual([]);

    handle.update({ radii: [12, 12, 0, 12] });

    expect(reported()).toHaveLength(1);
    expect(reported()[0]?.subjects).toEqual(["patched"]);
  });

  /*
   * Deduped by code and subject, like every other finding. A morph patching
   * radii every frame would otherwise say this sixty times a second.
   */
  it("says it once per surface, however many frames patch it", () => {
    const instance = root();
    const handle = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      nodeId: "morphing",
      radii: [4, 20, 4, 20],
    });
    for (let frame = 0; frame < 10; frame += 1) handle.update({ radii: [4, 20, 4, 20] });

    expect(reported()).toHaveLength(1);
  });

  it("is a warning, not a refusal — the surface still registers and draws", () => {
    const instance = root();
    const handle = instance.registerHost({
      host: host(instance),
      groupId: "g1",
      nodeId: "still-here",
      radii: [4, 20, 4, 20],
    });

    expect(reported()[0]?.severity).toBe("warning");
    expect(instance.scene.glassNode(handle.nodeId)?.descriptor.shape.radii).toEqual([4, 20, 4, 20]);
  });

  it("is silent in production, like every other dev-mode check", () => {
    const instance = root(false);
    instance.registerHost({ host: host(instance), groupId: "g1", radii: [4, 20, 4, 20] });

    expect(reported()).toEqual([]);
  });
});
