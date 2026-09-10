import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createGlassRoot, type GlassRoot } from "../src/root";
import { readHostChannels } from "../src/channels";

let root: GlassRoot;
beforeEach(() => {
  vi.stubGlobal("ResizeObserver", class {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  });
});
afterEach(() => {
  root?.destroy();
  vi.unstubAllGlobals();
});

function setup(present = true, reducedMotion = false) {
  root = createGlassRoot({
    autoStart: false,
    diagnosticSink: () => {},
    accessibilityOverrides: { reducedMotion },
    matcher: () => ({ matches: false, media: "", addEventListener() {}, removeEventListener() {} }),
  });
  root.registerGroup({ id: "presence" });
  const host = document.createElement("button");
  root.plane("base").hostLayer.append(host);
  const handle = root.registerHost({ host, groupId: "presence", present });
  const value = () => Number(host.style.getPropertyValue("--vitrea-materialization"));
  root.runFrame(0);
  return { host, handle, value };
}

describe("authored material presence", () => {
  it("dematerializes monotonically to identity, without replacing or fading its host", () => {
    const { host, handle, value } = setup();
    expect(value()).toBe(1);
    const id = host.getAttribute("data-vitrea-node");
    handle.update({ present: false });
    let previous = 1;
    for (let time = 10; time <= 220; time += 10) {
      root.runFrame(time);
      expect(value()).toBeLessThanOrEqual(previous);
      expect(value()).toBeGreaterThanOrEqual(0);
      expect(host.getAttribute("data-vitrea-node")).toBe(id);
      expect(host.style.opacity).toBe("");
      previous = value();
    }
    expect(value()).toBe(0);
    expect(readHostChannels(host, { x: 0, y: 0, width: 40, height: 40 }).materialization).toBe(0);
    handle.update({ present: true });
    root.runFrame(230);
    expect(value()).toBeGreaterThan(0);
    expect(value()).toBeLessThan(1);
    for (let time = 240; time <= 440; time += 10) root.runFrame(time);
    expect(value()).toBe(1);
  });

  it("starts absent in place and redirects from the current optical value", () => {
    const { handle, value } = setup(false);
    expect(value()).toBe(0);
    handle.update({ present: true });
    root.runFrame(20);
    const rising = value();
    expect(rising).toBeGreaterThan(0);
    expect(rising).toBeLessThan(1);
    handle.update({ present: false });
    expect(value()).toBe(rising);
    root.runFrame(40);
    expect(value()).toBeLessThan(rising);
  });

  it("steps presence under reduced motion, including a preference change mid-flight", () => {
    const { handle, value } = setup(true, true);
    handle.update({ present: false });
    root.runFrame(16);
    expect(value()).toBe(0);
    root.setAccessibilityOverrides({ reducedMotion: false });
    handle.update({ present: true });
    root.runFrame(32);
    expect(value()).toBeGreaterThan(0);
    expect(value()).toBeLessThan(1);
    root.setAccessibilityOverrides({ reducedMotion: true });
    root.runFrame(48);
    expect(value()).toBe(1);
  });
});
