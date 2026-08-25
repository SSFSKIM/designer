/**
 * The e2e harness: a small imperative façade over `createGlassRoot`, exposed on
 * `window.h` so a Playwright spec can build a scene, step frames and read back
 * what happened.
 *
 * It is a *consumer* of the package, not a back door into it. Every call below
 * goes through the public API a React binding would use, and the one place it
 * reaches for something unusual — `appDevice` — uses the documented app-owned
 * device path of §GPU device ownership, because Playwright's bundled engines
 * expose no `navigator.gpu` on this machine and the WebGPU tier would otherwise
 * be unreachable in any automated test.
 */

import type { BackdropHint } from "vitrea";

import {
  createBackdropProxyManager,
  createGlassLayerManager,
  createGlassRoot,
  MATERIAL_OPTICS,
  type BackdropProxyManager,
  type GlassHostHandle,
  type GlassLayerManager,
  type GlassPlane,
  type GlassRoot,
  type ProxyRequest,
  type VitreaDiagnostic,
} from "../../src/index";

/** What `canvasPixels` reports about one region of a plane's own canvas. */
export interface CanvasReading {
  /** Fraction of sampled pixels with any alpha at all. */
  readonly painted: number;
  readonly maxAlpha: number;
  /** The most opaque pixel found, as `[r, g, b, a]`. */
  readonly peak: readonly [number, number, number, number];
}

export interface AdapterReport {
  readonly ok: boolean;
  readonly why?: string;
  readonly vendor?: string;
  readonly architecture?: string;
  /** `true` software, `false` measured hardware, `undefined` unmeasurable. */
  readonly isFallback?: boolean | undefined;
}

export interface SurfaceSpec {
  readonly nodeId?: string;
  readonly groupId: string;
  readonly plane?: GlassPlane;
  readonly left: number;
  readonly top: number;
  readonly width: number;
  readonly height: number;
  readonly radius?: number;
  readonly label?: string;
  readonly order?: number;
  /**
   * What element the app authored. A text input is worth having alongside the
   * button because engines differ on whether Tab visits buttons at all — Safari
   * ships with "press Tab to highlight each item" off — while every engine
   * includes text fields in the sequential focus order.
   */
  readonly as?: "button" | "input";
}

export interface RootSpec {
  readonly renderer?: "css" | "webgpu";
  /**
   * Hand the root a stand-in app-owned `GPUDevice`. The lifecycle touches only
   * `lost` and `destroy()` on an app-owned device, so this exercises the real
   * ownership path — including loss — without a GPU.
   */
  readonly appDevice?: boolean;
  readonly devMode?: boolean;
  readonly samplingPadding?: number;
  readonly mergeDistance?: number;
  /** X6: the author's declared backdrop hint, forwarded straight to `registerGroup`. */
  readonly backdrop?: BackdropHint;
}

export interface TextureGroupSpec {
  readonly groupId: string;
  readonly sourceId: string;
  /** Canvas backing-store size, in texture px. */
  readonly width?: number;
  readonly height?: number;
}

export interface DiagnosticRecord {
  readonly origin: "core" | "platform";
  readonly code: string;
  readonly severity: string;
  readonly subjects: readonly string[];
  readonly message: string;
}

export interface BoxReading {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

interface StubDevice {
  lost: Promise<{ reason: string }>;
  destroy(): void;
  resolveLost(reason: string): void;
}

const makeStubDevice = (): StubDevice => {
  let settle: (info: { reason: string }) => void = () => undefined;
  const lost = new Promise<{ reason: string }>((resolve) => {
    settle = resolve;
  });
  return { lost, destroy: () => undefined, resolveLost: (reason) => settle({ reason }) };
};

const px = (value: string): number => Number.parseFloat(value.replace("px", "")) || 0;

/**
 * Is this adapter a CPU rasteriser? `undefined` means *nobody could tell*.
 *
 * `isFallbackAdapter` lives on `GPUAdapterInfo`; read off the `GPUAdapter` — as
 * this used to — it is `undefined` on current Chromium, so the gate in
 * `../support.ts` reported "hardware" for SwiftShader and never fired. The
 * distinction between `false` and `undefined` is the whole point of the return
 * type: a verdict nobody computed must not read as a clean bill of health.
 */
const softwareAdapter = (info: GPUAdapterInfo): boolean | undefined => {
  const flagged = (info as { isFallbackAdapter?: boolean }).isFallbackAdapter;
  if (typeof flagged === "boolean") return flagged;
  // The flag is the authority; this is only for a build that stops exposing it,
  // where Chromium's own software adapter still names itself.
  if (info.vendor === "google" && info.architecture === "swiftshader") return true;
  return undefined;
};

let root: GlassRoot | undefined;
let device: StubDevice | undefined;
let standaloneLayers: GlassLayerManager | undefined;
let standaloneProxies: BackdropProxyManager | undefined;
const handles = new Map<string, GlassHostHandle>();
const textureCanvases = new Map<string, HTMLCanvasElement>();
const diagnostics: DiagnosticRecord[] = [];

const api = {
  async createRoot(spec: RootSpec = {}): Promise<void> {
    device = spec.appDevice === true ? makeStubDevice() : undefined;
    root = createGlassRoot({
      renderer: spec.renderer ?? "css",
      devMode: spec.devMode ?? true,
      autoStart: false,
      ...(device === undefined
        ? {}
        : { webgpu: { device: device as unknown as GPUDevice } }),
      diagnosticSink: (diagnostic: VitreaDiagnostic) => {
        diagnostics.push({
          origin: diagnostic.origin,
          code: diagnostic.diagnostic.code,
          severity: diagnostic.diagnostic.severity,
          subjects: [...diagnostic.diagnostic.subjects],
          message: diagnostic.diagnostic.message,
        });
      },
    });
    await root.ready();
  },

  requireRoot(): GlassRoot {
    if (root === undefined) throw new Error("no glass root — call createRoot first");
    return root;
  },

  addGroup(groupId: string, spec: RootSpec = {}): void {
    api.requireRoot().registerGroup({
      id: groupId,
      ...(spec.samplingPadding === undefined ? {} : { samplingPadding: spec.samplingPadding }),
      ...(spec.mergeDistance === undefined ? {} : { mergeDistance: spec.mergeDistance }),
      ...(spec.backdrop === undefined ? {} : { backdrop: spec.backdrop }),
    });
  },

  addSurface(spec: SurfaceSpec): string {
    const glassRoot = api.requireRoot();
    const plane = spec.plane ?? "base";
    const host = document.createElement(spec.as ?? "button");
    if (host instanceof HTMLButtonElement) {
      host.type = "button";
      host.textContent = spec.label ?? "glass";
    }
    host.className = "glass-host";
    host.style.left = `${spec.left}px`;
    host.style.top = `${spec.top}px`;
    host.style.width = `${spec.width}px`;
    host.style.height = `${spec.height}px`;

    // The app owns placement: it renders (or portals) into the plane's host
    // layer, and vitrea never moves the element. This is the asChild contract.
    glassRoot.plane(plane).hostLayer.append(host);

    const radius = spec.radius ?? 22;
    const handle = glassRoot.registerHost({
      host,
      groupId: spec.groupId,
      plane,
      radii: [radius, radius, radius, radius],
      ...(spec.nodeId === undefined ? {} : { nodeId: spec.nodeId }),
      ...(spec.order === undefined ? {} : { order: spec.order }),
    });
    handles.set(handle.nodeId, handle);
    return handle.nodeId;
  },

  frame(count = 1): void {
    const glassRoot = api.requireRoot();
    for (let index = 0; index < count; index += 1) glassRoot.runFrame(index * 16);
  },

  meter(): { rects: number; styles: number; viewport: number; total: number } {
    const { counts, total } = api.requireRoot().readMeter;
    return { ...counts, total };
  },

  resetMeter(): void {
    api.requireRoot().readMeter.reset();
  },

  capabilities(groupId: string): Record<string, unknown> | undefined {
    const state = api.requireRoot().capabilities(groupId);
    return state === undefined ? undefined : { ...state };
  },

  probeVerdict(groupId: string): string | undefined {
    return api.requireRoot().probeReport(groupId)?.verdict;
  },

  probeBreaks(groupId: string): readonly string[] {
    return (api.requireRoot().probeReport(groupId)?.breaks ?? []).map((broken) => broken.describe);
  },

  platformProbe(): Record<string, unknown> {
    const report = api.requireRoot().platformProbe;
    return {
      supported: report.support.supported,
      properties: [...report.support.properties],
      reach: report.reach,
      engine: report.engine.family,
      version: report.engine.version,
      rasterises: report.conformance.rasterisesBackdropFilter,
      referenceFilter: report.conformance.referenceFilterInBackdrop,
      maxProxyArea: report.conformance.maxProxyAreaDevicePx,
    };
  },

  diagnostics(): readonly DiagnosticRecord[] {
    return diagnostics;
  },

  diagnosticCodes(): readonly string[] {
    return diagnostics.map((record) => record.code);
  },

  clearDiagnostics(): void {
    diagnostics.length = 0;
  },

  /** The plane whose host layer currently contains this node's element. */
  hostPlane(nodeId: string): string | undefined {
    const host = document.querySelector(`[data-vitrea-node="${nodeId}"]`);
    const layer = host?.closest("[data-vitrea-layer='semantic-host']");
    return layer?.getAttribute("data-vitrea-plane") ?? undefined;
  },

  /**
   * Reach a genuine steady state.
   *
   * Two things legitimately dirty geometry after the first frames and would
   * otherwise land inside a measurement window: font loading completes and marks
   * every host dirty, and a `MutationObserver` delivers application-CSS changes
   * on a microtask. Waiting for both is what makes "steady state" mean steady
   * state rather than "a moment later".
   */
  async settle(): Promise<void> {
    await document.fonts.ready;
    await new Promise((resolve) => requestAnimationFrame(() => resolve(undefined)));
    await new Promise((resolve) => setTimeout(resolve, 0));
  },

  nodePlane(nodeId: string): string | undefined {
    return api.requireRoot().scene.glassNode(nodeId)?.descriptor.zSlot.plane;
  },

  promote(nodeId: string, plane: GlassPlane): void {
    handles.get(nodeId)?.promoteTo(plane);
  },

  release(nodeId: string): void {
    handles.get(nodeId)?.release();
    handles.get(nodeId)?.host.remove();
    handles.delete(nodeId);
  },

  setOwnedTransform(nodeId: string, transform: string | undefined): void {
    handles.get(nodeId)?.setOwnedTransform(transform);
  },

  invalidate(nodeId: string): void {
    handles.get(nodeId)?.invalidateGeometry();
  },

  resizeSurface(nodeId: string, width: number, height: number): void {
    const host = handles.get(nodeId)?.host;
    if (host === undefined) return;
    host.style.width = `${width}px`;
    host.style.height = `${height}px`;
  },

  /** Where a group's proxy element sits, read back off its own inline style. */
  proxyBox(groupId: string): BoxReading | undefined {
    const proxy = document.querySelector<HTMLElement>(`[data-vitrea-proxy="${groupId}"]`);
    if (proxy === null) return undefined;
    return {
      x: px(proxy.style.left),
      y: px(proxy.style.top),
      width: px(proxy.style.width),
      height: px(proxy.style.height),
    };
  },

  proxyStyle(groupId: string): Record<string, string> | undefined {
    const proxy = document.querySelector<HTMLElement>(`[data-vitrea-proxy="${groupId}"]`);
    if (proxy === null) return undefined;
    const computed = getComputedStyle(proxy);
    return {
      clipPath: computed.clipPath || computed.getPropertyValue("-webkit-clip-path"),
      pointerEvents: computed.pointerEvents,
      backdropFilter:
        computed.backdropFilter || computed.getPropertyValue("-webkit-backdrop-filter"),
      parentLayer:
        proxy.parentElement?.getAttribute("data-vitrea-layer") ?? "(not in a proxy layer)",
      parentPlane: proxy.parentElement?.getAttribute("data-vitrea-plane") ?? "(none)",
    };
  },

  proxyOrder(plane: GlassPlane): readonly string[] {
    const layer = document.querySelector(
      `[data-vitrea-layer='backdrop-proxy'][data-vitrea-plane='${plane}']`,
    );
    return [...(layer?.children ?? [])].map(
      (child) => child.getAttribute("data-vitrea-proxy") ?? "?",
    );
  },

  loseDevice(): void {
    device?.resolveLost("unknown");
  },

  webgpu(): Record<string, unknown> | undefined {
    const status = api.requireRoot().webgpu;
    return status === undefined
      ? undefined
      : {
          available: status.available,
          deviceHealth: status.deviceHealth,
          ownership: status.ownership,
          hasDevice: status.device !== undefined,
        };
  },

  refractionFor(nodeId: string): Record<string, string> | undefined {
    const input = api.requireRoot().renderInput();
    for (const plane of input?.planes ?? []) {
      for (const node of plane.nodes) {
        if (node.nodeId === nodeId) return { ...node.refraction };
      }
    }
    return undefined;
  },

  hostStyle(nodeId: string): Record<string, string> | undefined {
    const host = handles.get(nodeId)?.host;
    if (host === undefined) return undefined;
    const computed = getComputedStyle(host);
    return {
      backdropFilter:
        computed.backdropFilter || computed.getPropertyValue("-webkit-backdrop-filter"),
      backgroundColor: computed.backgroundColor,
      borderTopWidth: computed.borderTopWidth,
      borderTopColor: computed.borderTopColor,
      borderRadius: computed.borderTopLeftRadius,
      pointerEvents: computed.pointerEvents,
      transition: computed.transitionProperty,
      /** The resolved ink — what the label is actually drawn in, whatever chose it. */
      color: computed.color,
      tint: computed.getPropertyValue("--vitrea-tint").trim(),
      occlusion: computed.getPropertyValue("--vitrea-occlusion").trim(),
      // The raw custom-property string, unresolved by the browser — unlike
      // `color`, which `light-dark()` collapses to an `rgb()` either way, this
      // token tells the two cases apart (X6, corrective K4).
      foreground: computed.getPropertyValue("--vitrea-foreground").trim(),
    };
  },

  /** Hit-test at a point, reporting what the browser says is on top. */
  hitTest(x: number, y: number): { top: string; stack: readonly string[] } {
    const describe = (element: Element): string => {
      const node = element.getAttribute("data-vitrea-node");
      if (node !== null) return `host:${node}`;
      const layer = element.getAttribute("data-vitrea-layer");
      if (layer !== null) return `layer:${layer}`;
      const proxy = element.getAttribute("data-vitrea-proxy");
      if (proxy !== null) return `proxy:${proxy}`;
      return element.id === "" ? element.tagName.toLowerCase() : `#${element.id}`;
    };
    const top = document.elementFromPoint(x, y);
    return {
      top: top === null ? "(nothing)" : describe(top),
      stack: document.elementsFromPoint(x, y).map(describe),
    };
  },

  activeElement(): string {
    const active = document.activeElement;
    if (active === null) return "(none)";
    const node = active.getAttribute("data-vitrea-node");
    return node !== null ? `host:${node}` : active.id === "" ? active.tagName.toLowerCase() : `#${active.id}`;
  },

  focus(nodeId: string): void {
    handles.get(nodeId)?.host.focus();
  },

  scrollTo(y: number): void {
    document.getElementById("scroller")?.scrollTo(0, y);
  },

  scrollTop(): number {
    return document.getElementById("scroller")?.scrollTop ?? 0;
  },

  /** Put a candidate backdrop-root-forming style on the glass root's parent. */
  breakBackdropRoot(property: string, value: string): void {
    document.body.style.setProperty(property, value);
  },

  clearBackdropRoot(property: string): void {
    document.body.style.removeProperty(property);
  },

  /** Hide the proxy layer, to compare a filtered scene against an unfiltered one. */
  setProxiesVisible(visible: boolean): void {
    for (const layer of document.querySelectorAll<HTMLElement>(
      "[data-vitrea-layer='backdrop-proxy']",
    )) {
      layer.style.display = visible ? "" : "none";
    }
  },

  /**
   * A standalone plane + proxy pair, with no scene behind it.
   *
   * The proxy construction is what S1 made normative, and it is worth pixel
   * assertions in its own right — independently of whether a group happened to
   * resolve to the tier that asks for one.
   */
  mountProxies(requests: readonly Omit<ProxyRequest, "blurRadius" | "saturation">[]): void {
    standaloneLayers ??= createGlassLayerManager({ zIndex: 1200 });
    standaloneProxies ??= createBackdropProxyManager({
      plane: (plane) => {
        if (standaloneLayers === undefined) throw new Error("no layers");
        return standaloneLayers.plane(plane);
      },
      diagnostics: {
        report: (diagnostic) =>
          diagnostics.push({
            origin: "platform",
            code: diagnostic.code,
            severity: diagnostic.severity,
            subjects: [...diagnostic.subjects],
            message: diagnostic.message,
          }),
        reported: [],
        clear: () => undefined,
      },
    });
    standaloneProxies.sync(
      requests.map((request) => ({
        ...request,
        blurRadius: MATERIAL_OPTICS.regular.blurRadius,
        saturation: MATERIAL_OPTICS.regular.saturation,
      })),
      { devicePixelRatio: window.devicePixelRatio, maxProxyAreaDevicePx: 1_750_000 },
    );
  },

  /**
   * Is there a real adapter here?
   *
   * C5 measured that the answer is machine-specific and counter-intuitive — on
   * this localhost secure context Playwright's WebKit returns a device while
   * stock Chromium returns none — so every GPU assertion consumes this rather
   * than assuming an environment. Requesting an adapter here does not disturb
   * the root's own request: adapters are not exclusive, devices are.
   */
  async adapter(): Promise<AdapterReport> {
    if (navigator.gpu === undefined) return { ok: false, why: "no navigator.gpu" };
    try {
      const found = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
      if (found === null) return { ok: false, why: "requestAdapter() returned null" };
      const info = found.info ?? ({} as GPUAdapterInfo);
      return {
        ok: true,
        vendor: info.vendor,
        architecture: info.architecture,
        isFallback: softwareAdapter(info),
      };
    } catch (error) {
      return { ok: false, why: error instanceof Error ? error.message : String(error) };
    }
  },

  /**
   * Register a texture-backed group and hand the bridge a canvas painting into
   * it — the two halves of acceptance #2, which are deliberately separate calls
   * because core holds the declaration and cannot hold the pixels (X4).
   */
  addTextureGroup(spec: TextureGroupSpec): void {
    const glassRoot = api.requireRoot();
    const canvas = document.createElement("canvas");
    canvas.width = spec.width ?? 512;
    canvas.height = spec.height ?? 512;

    // A backdrop worth refracting: hard edges, so lensing has something to bend.
    const context = canvas.getContext("2d");
    if (context !== null) {
      const band = canvas.height / 8;
      for (let i = 0; i < 8; i += 1) {
        context.fillStyle = i % 2 === 0 ? "#ff3b30" : "#0a84ff";
        context.fillRect(0, i * band, canvas.width, band);
      }
    }

    glassRoot.registerBackdropSource({
      id: spec.sourceId,
      kind: "texture",
      probe: { taint: "clean", textureCompatibility: "compatible" },
    });
    glassRoot.registerGroup({ id: spec.groupId, backdropSourceId: spec.sourceId });
    glassRoot.setBackdropTexture(spec.sourceId, { kind: "canvas", canvas });
    glassRoot.scene.markBackdropSourceDirty(spec.sourceId);
    textureCanvases.set(spec.sourceId, canvas);
  },

  markTextureDirty(sourceId: string): void {
    api.requireRoot().scene.markBackdropSourceDirty(sourceId);
  },

  /**
   * Read a region of one plane's own canvas back.
   *
   * The renderer's canvas, not the page: acceptance #2's mechanism. Reading the
   * canvas gives the alpha channel that a page screenshot flattens away, and
   * alpha is the whole question — glass that painted nothing and glass that
   * painted transparent black are the same pixel once composited.
   *
   * **Synchronous, and it must stay synchronous.** A WebGPU canvas can only be
   * snapshotted while the texture it drew into is still current; once the frame
   * is presented, `drawImage` and `createImageBitmap` both hand back a fully
   * transparent image over a canvas the page is plainly still showing. So the
   * read has to happen in the same task as the draw, which means callers step
   * frames and read inside one `page.evaluate`, and nothing here may await.
   */
  canvasPixels(
    layer: "optics-canvas" | "highlight-canvas",
    plane: GlassPlane,
    region: BoxReading,
  ): CanvasReading {
    const layers = api.requireRoot().plane(plane);
    const canvas = layer === "optics-canvas" ? layers.opticsCanvas : layers.highlightCanvas;

    // `drawImage` rather than `createImageBitmap`: the latter returns a fully
    // transparent bitmap off a WebGPU canvas in this build, over a canvas
    // `toDataURL` and the page's own compositing both show as painted.
    const scale = canvas.width / window.innerWidth;
    const x = Math.round(region.x * scale);
    const y = Math.round(region.y * scale);
    const width = Math.max(1, Math.round(region.width * scale));
    const height = Math.max(1, Math.round(region.height * scale));

    const scratch = document.createElement("canvas");
    scratch.width = width;
    scratch.height = height;
    const context = scratch.getContext("2d", { willReadFrequently: true });
    if (context === null) throw new Error("no 2d context for readback");
    context.clearRect(0, 0, width, height);
    context.drawImage(canvas, x, y, width, height, 0, 0, width, height);

    const data = context.getImageData(0, 0, width, height).data;
    let painted = 0;
    let maxAlpha = 0;
    let peak: readonly [number, number, number, number] = [0, 0, 0, 0];
    for (let i = 0; i < data.length; i += 4) {
      const alpha = data[i + 3] ?? 0;
      if (alpha > 0) painted += 1;
      if (alpha > maxAlpha) {
        maxAlpha = alpha;
        peak = [data[i] ?? 0, data[i + 1] ?? 0, data[i + 2] ?? 0, alpha];
      }
    }

    return { painted: painted / (width * height), maxAlpha, peak };
  },

  /** Whether the bridge is attached with a live device and configured canvases. */
  rendererActive(): boolean {
    return api.requireRoot().rendererBridge?.active ?? false;
  },

  /**
   * Destroy the live device out from under the runtime.
   *
   * `destroy()` is the only loss a page can provoke. The lifecycle deliberately
   * does not re-request after one — `reason === "destroyed"` is our own teardown,
   * not a fault — so the tier swap this provokes is permanent within the root,
   * and recovery is shown on a second root instead.
   */
  async loseRealDevice(): Promise<void> {
    const live = api.requireRoot().webgpu?.device;
    if (live === undefined) throw new Error("no live device to lose");
    live.destroy();
    await live.lost;
    // One task, so the lifecycle's own `lost` handler has published the loss and
    // the bridge's device sync has run.
    await new Promise((resolve) => setTimeout(resolve, 50));
  },

  reset(): void {
    for (const handle of handles.values()) {
      handle.release();
      handle.host.remove();
    }
    handles.clear();
    diagnostics.length = 0;
    root?.destroy();
    root = undefined;
    standaloneProxies?.destroy();
    standaloneProxies = undefined;
    standaloneLayers?.destroy();
    standaloneLayers = undefined;
    device = undefined;
    textureCanvases.clear();
    document.body.removeAttribute("style");
    document.getElementById("scroller")?.scrollTo(0, 0);
  },
};

declare global {
  interface Window {
    h: typeof api;
  }
}

window.h = api;
document.documentElement.setAttribute("data-harness-ready", "1");
