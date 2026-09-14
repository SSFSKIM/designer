import { afterEach, describe, expect, it, vi } from "vitest";
import { createGlassRoot, type GlassRoot } from "../src/root";
import { releaseBackdropToneScratch } from "../src/backdrop-tone";

let root: GlassRoot | undefined;
afterEach(() => {
  root?.destroy();
  root = undefined;
  document.body.replaceChildren();
  releaseBackdropToneScratch();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function setup(silhouette = true, hint?: number) {
  vi.stubGlobal("ResizeObserver", class {
    observe() {} unobserve() {} disconnect() {}
  });
  vi.stubGlobal("ImageBitmap", class {});
  let reads = 0;
  // jsdom supplies no raster API. Only that boundary is replaced; the root,
  // cadence, geometry and tone reduction run unchanged against these pixels.
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockImplementation(() => ({
    clearRect() {}, drawImage() {},
    getImageData() {
      reads += 1;
      return { data: new Uint8ClampedArray([0, 0, 0, 255, 255, 255, 255, 255]) };
    },
  }) as unknown as CanvasRenderingContext2D);
  const container = document.createElement("div");
  document.body.append(container);
  root = createGlassRoot({
    windowActivation: "active",
    container, renderer: "css", autoStart: false, diagnosticSink() {},
    matcher: () => ({ matches: false, media: "", addEventListener() {}, removeEventListener() {} }),
    ...(silhouette ? { materialProfile: { backdropToneAbscissa: { kind: "silhouette" } } } : {}),
  });
  root.registerBackdropSource({ id: "src", kind: "texture",
    probe: { taint: "clean", textureCompatibility: "compatible" } });
  root.registerGroup({ id: "g", backdropSourceId: "src",
    ...(hint === undefined ? {} : { backdrop: { tone: "light" as const, luminance: hint } }),
  });
  const canvas = document.createElement("canvas");
  canvas.width = 2;
  canvas.height = 1;
  root.setBackdropTexture("src", { kind: "canvas", canvas,
    placement: { kind: "rect", rect: { x: 0, y: 0, width: 200, height: 100 } } });
  const handles: ReturnType<GlassRoot["registerHost"]>[] = [];
  const addHost = (x: number) => {
    const host = document.createElement("div");
    host.getBoundingClientRect = () => ({ x, y: 0, width: 10, height: 10,
      left: x, right: x + 10, top: 0, bottom: 10, toJSON() {} });
    root!.plane("base").hostLayer.append(host);
    handles.push(root!.registerHost({ host, groupId: "g" }));
    return host;
  };
  const left = addHost(0);
  const right = addHost(190);
  return { instance: root, container, canvas, left, right, handles, reads: () => reads };
}

describe("CSS silhouette profile routing", () => {
  it("feeds and reports each host's local input without extra steady-state reads", () => {
    const { instance, left, right, reads } = setup();
    instance.runFrame(16);
    const inputs = instance.capabilities("g")?.backdropToneAbscissae;
    expect(inputs?.map((input) => input.encodedLuminance)).toEqual([0, 1]);
    expect(left.style.cssText).not.toEqual(right.style.cssText);
    expect(reads()).toBe(1);
    const first = reads();
    instance.runFrame(32);
    expect(reads()).toBe(first);
  });

  it("reuses source pixels when geometry changes before the live cadence", () => {
    const { instance, left, handles, reads } = setup();
    instance.runFrame(16);
    left.getBoundingClientRect = () => ({ x: 190, y: 0, width: 10, height: 10,
      left: 190, right: 200, top: 0, bottom: 10, toJSON() {} });
    handles[0]!.invalidateGeometry();
    instance.runFrame(32);
    expect(instance.capabilities("g")?.backdropToneAbscissae?.map((i) => i.encodedLuminance))
      .toEqual([1, 1]);
    expect(reads()).toBe(1);
  });

  it.each([null, false, "silhouette", {}, { kind: "source" },
    { kind: "silhouette", radius: 2 }])("refuses malformed abscissae %j without replacing the profile", (value) => {
    const { instance, container } = setup();
    const profile = { backdropToneAbscissa: value } as unknown as
      Parameters<GlassRoot["setMaterialProfile"]>[0];
    const children = container.innerHTML;
    expect(() => createGlassRoot({
      windowActivation: "active", container, renderer: "css", materialProfile: profile,
    }))
      .toThrow(/backdropToneAbscissa/);
    expect(container.innerHTML).toBe(children);
    expect(() => instance.setMaterialProfile(profile)).toThrow(/backdropToneAbscissa/);
    instance.setColorScheme("dark");
    instance.runFrame(16);
    expect(instance.capabilities("g")?.backdropToneAbscissae?.map((i) => i.kind))
      .toEqual(["silhouette", "silhouette"]);
  });

  it("refreshes replacement, placement, dimensions and profile switches immediately", () => {
    const { instance, canvas, reads } = setup();
    instance.runFrame(16);
    instance.setBackdropTexture("src", { kind: "canvas", canvas,
      placement: { kind: "rect", rect: { x: 190, y: 0, width: 200, height: 100 } } });
    instance.runFrame(32);
    expect(instance.capabilities("g")?.backdropToneAbscissae?.map((i) => i.encodedLuminance))
      .toEqual([0, 0]);
    expect(reads()).toBe(2);
    canvas.width = 1;
    instance.runFrame(48);
    expect(instance.capabilities("g")?.backdropToneAbscissae?.map((i) => i.sourceWidth))
      .toEqual([1, 1]);
    expect(reads()).toBe(3);
    instance.setMaterialProfile({ backdropToneAbscissa: "source" });
    instance.setMaterialProfile({ backdropToneAbscissa: { kind: "silhouette" } });
    instance.runFrame(64);
    expect(reads()).toBe(4);
  });

  it("reports author hints without reading pixels, even with silhouette enabled", () => {
    const { instance, reads } = setup(true, 0.25);
    instance.runFrame(16);
    const inputs = instance.capabilities("g")?.backdropToneAbscissae;
    expect(inputs?.map((input) => input.kind)).toEqual(["hint", "hint"]);
    expect(inputs?.map((input) => input.luminance)).toEqual([0.25, 0.25]);
    expect(reads()).toBe(0);
    expect(instance.renderInput()?.groups[0]?.backdropToneHint).toBe(true);
  });

  it("refreshes live sources on cadence and removes readouts when the profile switches", () => {
    let now = 0;
    vi.spyOn(window.performance, "now").mockImplementation(() => now);
    const { instance, reads } = setup();
    instance.runFrame(16);
    const first = reads();
    now = 249;
    instance.runFrame(32);
    expect(reads()).toBe(first);
    now = 250;
    instance.runFrame(48);
    expect(reads()).toBe(first * 2);
    instance.setMaterialProfile({ backdropToneAbscissa: "source" });
    instance.runFrame(64);
    expect(instance.capabilities("g")?.backdropToneAbscissae).toBeUndefined();
  });

  it("leaves the default profile on the legacy source path", () => {
    const { instance, reads } = setup(false);
    instance.runFrame(16);
    expect(instance.capabilities("g")?.backdropToneAbscissae).toBeUndefined();
    expect(reads()).toBe(1);
  });
});
