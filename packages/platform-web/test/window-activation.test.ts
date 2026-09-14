import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createGlassRoot, type GlassRoot } from "../src/root";
import * as activation from "../src/index";

class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

let root: GlassRoot | undefined;
let focused = true;
let time = 0;
const frame = (): void => { root!.runFrame(time += 16); };
const pose = (value: boolean): void => {
  focused = value;
  window.dispatchEvent(new Event(value ? "focus" : "blur"));
};

beforeEach(() => {
  vi.stubGlobal("ResizeObserver", ResizeObserverStub);
  vi.spyOn(document, "hasFocus").mockImplementation(() => focused);
  focused = true;
  time = 0;
});
afterEach(() => {
  root?.destroy();
  root = undefined;
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function create(windowActivation?: activation.GlassWindowActivation): GlassRoot {
  root = createGlassRoot({
    autoStart: false,
    diagnosticSink: () => {},
    matcher: (media) => ({ media, matches: false, addEventListener() {}, removeEventListener() {} }),
    ...(windowActivation === undefined ? {} : { windowActivation }),
  });
  return root;
}

describe("window activation is a root pose", () => {
  it("defaults to the supplied document and batches focus changes at the read phase", () => {
    create();
    frame();
    expect(root!.windowActivation).toBe("active");
    pose(false);
    expect(root!.windowActivation).toBe("active");
    frame();
    expect(root!.windowActivation).toBe("inactive");
    pose(true);
    frame();
    expect(root!.windowActivation).toBe("active");
  });

  it("pins either endpoint despite the observer and auto re-reads the document", () => {
    create("inactive");
    frame();
    expect(root!.windowActivation).toBe("inactive");
    pose(true);
    frame();
    expect(root!.windowActivation).toBe("inactive");
    activation.setWindowActivation(root!, "active");
    pose(false);
    frame();
    expect(root!.windowActivation).toBe("active");
    root!.setWindowActivation("auto");
    frame();
    expect(root!.windowActivation).toBe("inactive");
    pose(true);
    frame();
    expect(root!.windowActivation).toBe("active");
  });

  it("does not mistake visibility or a synthetic blur for a different hasFocus answer", () => {
    create();
    frame();
    window.dispatchEvent(new Event("blur"));
    document.dispatchEvent(new Event("visibilitychange"));
    frame();
    expect(root!.windowActivation).toBe("active");
  });

  it("recedes the material and restores the active endpoint", () => {
    create("active");
    const host = document.createElement("button");
    root!.plane("base").hostLayer.append(host);
    root!.registerGroup({ id: "g" });
    root!.registerHost({ host, groupId: "g", plane: "base" });
    frame();
    const node = () => root!.renderInput()!.planes.flatMap((plane) => plane.nodes)[0]!;
    const active = node().optics.borderAlpha;
    root!.setWindowActivation("inactive");
    frame();
    expect(node().optics.borderAlpha).toBe(0);
    expect(active).toBeGreaterThan(0);
    expect(host.style.opacity).not.toBe("0");
    root!.setWindowActivation("active");
    frame();
    expect(node().optics.borderAlpha).toBe(active);
  });

  it("keeps an author patch intact while the inactive difference wins over it", () => {
    create("active");
    root!.setMaterialProfile({ optics: { regular: { rimAlpha: 0.5, tintAlpha: 0.6 } } });
    const host = document.createElement("button");
    root!.plane("base").hostLayer.append(host);
    root!.registerGroup({ id: "g" });
    root!.registerHost({ host, groupId: "g", plane: "base" });
    frame();
    const node = () => root!.renderInput()!.planes.flatMap((plane) => plane.nodes)[0]!;
    const active = node();
    root!.setWindowActivation("inactive");
    frame();
    expect(node().optics.borderAlpha).toBe(0);
    expect(node().channels).toEqual(active.channels);
    expect(node().material).toEqual(active.material);
    root!.setWindowActivation("active");
    frame();
    expect(node().optics).toEqual(active.optics);
  });

  it("unregisters the supplied window listeners at destruction", () => {
    const add = vi.spyOn(window, "addEventListener");
    const remove = vi.spyOn(window, "removeEventListener");
    create();
    root!.destroy();
    root = undefined;
    for (const type of ["focus", "blur"]) {
      const listener = add.mock.calls.find(([name]) => name === type)![1];
      expect(remove).toHaveBeenCalledWith(type, listener);
    }
  });
});
