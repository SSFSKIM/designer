/**
 * The calibration scene page — C7's web side of the fidelity ground truth.
 *
 * A small imperative façade over `createGlassRoot`, deliberately the same shape
 * as `packages/platform-web/e2e/fixtures/harness.ts`: a *consumer* of the public
 * API, never a back door into it. Nothing here reaches past what an application
 * would call, because a calibration number produced through a private path would
 * be a number about a renderer nobody ships.
 *
 * What the page is arranged around:
 *
 * 1. **The background is the committed raster, composited — never redrawn.** The
 *    `<img>` the page shows is `apps/reference-apple/fixtures/backgrounds/…`
 *    itself, served in place, and the *same element* is handed to the renderer as
 *    the GPU tier's backdrop texture. Both tiers therefore sample the exact
 *    pixels the native harness composited. The spec's rule is that rasterisation
 *    differences must never reach the diff; one decode of one file is the
 *    strongest available form of that.
 *
 * 2. **Geometry is read, not restated.** `scenes.ts` derives every rect from
 *    `scenes.json`, the file the SwiftUI harness reads too.
 *
 * 3. **No text inside the glass**, for the reason `apps/reference-apple/README.md`
 *    gives: a glyph inside the measured region puts two font rasterisers inside
 *    the material axis, which is the one axis the raster-background rule exists
 *    to keep clean.
 *
 * 4. **Readiness is a signal, never a sleep.** `data-scene-ready` appears once
 *    the raster has decoded, the tier has resolved, and the frames have been
 *    presented. A capture driver that slept would be sampling whatever had
 *    happened by then.
 *
 * 5. **The resolved state is published verbatim** on `window.__vitreaCalibration`.
 *    X2's honesty core is what makes a cell descriptor truthful rather than
 *    aspirational: the page reports what actually drew, including a demotion and
 *    its reason, and the driver copies that into the cell rather than repeating
 *    what the URL asked for.
 *
 * Note on pixel readback: nothing here reads canvas pixels. K2 measured that a
 * WebGPU canvas is only readable while its frame texture is current — after
 * present, every readback path returns a transparent image over a canvas the
 * page is visibly still showing — so a readback split across two evaluates
 * yields a confident, wrong zero. The capture is a compositor screenshot, which
 * sees the presented frame, and that is why it is the driver's job and not the
 * page's.
 */

import { DEFAULT_MOTION_PROFILE } from "@vitrea/motion";
import {
  GLASS_CHANNEL_PROPERTIES,
  createGlassRoot,
  type GlassHostHandle,
  type GlassRoot,
  type RendererMaterialProfile,
  type VitreaDiagnostic,
} from "@vitrea/platform-web";
import type { GlassGroupState } from "@vitrea/core";

import { CANVAS, SCENE_IDS, resolveScene, type PlacedScene } from "./scenes";

const REFERENCE_MOUNT = "/reference-fixtures";

/** How many frames to settle over before the capture. */
const DEFAULT_FRAMES = 8;

/** Frame pacing for the manual steps — a nominal 60Hz, so the value is a value. */
const FRAME_MS = 1000 / 60;

export interface AdapterReport {
  readonly ok: boolean;
  readonly why?: string;
  readonly vendor?: string;
  readonly architecture?: string;
  readonly device?: string;
  readonly description?: string;
  readonly isFallback?: boolean;
}

export interface GroupReport {
  readonly id: string;
  readonly configuredSource: "texture" | "dom";
  readonly mergeDistance?: number;
  readonly declaredSpacing?: number;
  readonly state: GlassGroupState | undefined;
  readonly probeVerdict: string | undefined;
}

export interface SurfaceReport {
  readonly nodeId: string;
  readonly groupId: string;
  readonly plane: string;
  readonly family: string;
  readonly radius: number;
  /** Where the surface actually landed, read back off the measured render input. */
  readonly bounds: { x: number; y: number; width: number; height: number } | undefined;
  readonly refraction: Record<string, string> | undefined;
}

export interface SceneReport {
  readonly sceneId: string;
  readonly requestedRenderer: "css" | "webgpu";
  readonly requestedScale: number;
  readonly devicePixelRatio: number;
  readonly frames: number;
  readonly canvas: { width: number; height: number };
  /** What a capture of the stage must come out as, in device px. */
  readonly pixelSize: readonly [number, number];
  readonly background: {
    readonly id: string;
    readonly url: string;
    readonly naturalWidth: number;
    readonly naturalHeight: number;
  };
  readonly pressed: boolean;
  /**
   * The optical tunables this capture ran on, or `null` for the renderer's own
   * defaults. A fidelity number is only interpretable against the numbers that
   * produced it, so the patch travels with the report rather than living in the
   * command line that happened to inject it.
   */
  readonly materialProfile: RendererMaterialProfile | null;
  readonly groups: readonly GroupReport[];
  readonly surfaces: readonly SurfaceReport[];
  readonly webgpu: Record<string, unknown> | undefined;
  readonly rendererActive: boolean;
  readonly adapter: AdapterReport;
  /**
   * X5's lock, as observed rather than as intended. `getConfiguration()` is the
   * only way to read a canvas context's colour space back, and it is not in
   * every build — where it is absent this says so instead of asserting the
   * default.
   */
  readonly canvasColorSpace: string;
  readonly diagnostics: readonly { code: string; severity: string; message: string }[];
  /**
   * Anything that would make this capture a misleading data point. Non-empty
   * means the driver must record the capture as unusable, not merely noisy.
   */
  readonly problems: readonly string[];
}

declare global {
  interface Window {
    __vitreaCalibration: {
      readonly ready: Promise<SceneReport>;
      report?: SceneReport;
    };
    /**
     * Optical tunables to run this capture on, injected by the driver before this
     * script executes (`page.addInitScript`). Absent means the renderer's own
     * defaults, which is what an uncalibrated capture must be.
     */
    __vitreaMaterialProfile?: RendererMaterialProfile;
  }
}

const query = new URLSearchParams(window.location.search);

/**
 * Is there a real adapter here?
 *
 * Requesting one alongside the root's own request is safe — adapters are not
 * exclusive, devices are — and the answer is machine-specific enough
 * (C5 measured the naive expectation inverted on this hardware) that every cell
 * must record the observed answer rather than assume an environment.
 */
async function probeAdapter(): Promise<AdapterReport> {
  if (navigator.gpu === undefined) return { ok: false, why: "no navigator.gpu" };
  try {
    const found = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
    if (found === null) return { ok: false, why: "requestAdapter() returned null" };
    const info = found.info ?? ({} as GPUAdapterInfo);
    return {
      ok: true,
      vendor: info.vendor,
      architecture: info.architecture,
      device: info.device,
      description: info.description,
      isFallback: (found as { isFallbackAdapter?: boolean }).isFallbackAdapter === true,
    };
  } catch (error) {
    return { ok: false, why: error instanceof Error ? error.message : String(error) };
  }
}

/** The native harness's own background index — the filename convention's one home. */
async function backgroundUrl(id: string): Promise<string> {
  const response = await fetch(`${REFERENCE_MOUNT}/backgrounds/index.json`);
  if (!response.ok) {
    throw new Error(
      `The reference background index is not being served (${response.status}). ` +
        "Run apps/reference-apple/capture.sh backgrounds first.",
    );
  }
  const index = (await response.json()) as Record<string, string>;
  const relative = index[id];
  if (relative === undefined) {
    throw new Error(
      `The reference index carries no background "${id}"; it has: ${Object.keys(index).join(", ")}.`,
    );
  }
  return `${REFERENCE_MOUNT}/${relative}`;
}

/**
 * Load the raster and hold it until it has genuinely decoded.
 *
 * `decode()` rather than the `load` event: `load` fires when the bytes are in,
 * and a first paint can still land on an undecoded image. This is half of the
 * readiness signal.
 */
async function loadBackground(url: string): Promise<HTMLImageElement> {
  const image = new Image();
  image.src = url;
  image.alt = "";
  image.decoding = "sync";
  // The raster is already at capture scale, so any resampling here would blur
  // the very step edges the checkerboard and impulse scenes exist to measure.
  // This mirrors the native side's `.interpolation(.none).antialiased(false)`.
  image.style.imageRendering = "pixelated";
  await image.decode();
  return image;
}

/**
 * The settled pressed pose, taken from the motion profile's own state target.
 *
 * C9 owns motion; this is the *pose*, not a transient — the value the drivers
 * converge on while a press is held, which is what the `pressed` scenes measure.
 * Read from `DEFAULT_MOTION_PROFILE` rather than written out, so a re-tuned
 * profile moves the fixture instead of silently disagreeing with it.
 */
function applyPressedPose(host: HTMLElement, handle: GlassHostHandle): void {
  const target = DEFAULT_MOTION_PROFILE.stateTargets.pressed;
  const press = target.pressCompression ?? 1;
  host.style.setProperty(GLASS_CHANNEL_PROPERTIES.press, `${press}`);
  host.style.setProperty(GLASS_CHANNEL_PROPERTIES.glow, `${target.glow ?? 0}`);
  host.style.setProperty(GLASS_CHANNEL_PROPERTIES.lensStrength, `${target.lensStrength ?? 1}`);
  host.style.setProperty(GLASS_CHANNEL_PROPERTIES.state, "pressed");

  // The compression a binding would emit for that pose. Composed on top of the
  // measured rect by vitrea, which is why it goes through the handle rather than
  // onto the element's own transform.
  const scale = 1 - press * DEFAULT_MOTION_PROFILE.pressCompressionScale;
  handle.setOwnedTransform(`scale(${scale})`);
}

/**
 * X5's sRGB lock, as observed rather than as intended.
 *
 * On the GPU tier the answer is a property of the configured canvas context, and
 * `getConfiguration()` is the only way to read it back — where the build has no
 * such method this says so instead of asserting the default it believes applies.
 *
 * On the CSS tier there is no canvas colour space to read: the glass is CSS
 * declarations composited by the page, so the colour space is the document's and
 * the honest answer names that rather than reaching for a context the tier never
 * configured. Calling `getContext("webgpu")` there would *create* one and then
 * report a default nothing drew through.
 */
function readCanvasColorSpace(root: GlassRoot): string {
  if (root.rendererBridge?.active !== true) {
    return "srgb (CSS tier: page compositing; no canvas colour space is configured)";
  }
  const context = root.plane("base").opticsCanvas.getContext("webgpu") as
    | (GPUCanvasContext & { getConfiguration?: () => { colorSpace?: string } | null })
    | null;
  const configured = context?.getConfiguration?.()?.colorSpace;
  if (configured !== undefined) return configured;
  return "srgb (WebGPU default; getConfiguration() unavailable in this build)";
}

async function build(): Promise<SceneReport> {
  const sceneId = query.get("scene");
  if (sceneId === null) {
    throw new Error(`?scene= is required. The matrix declares: ${SCENE_IDS.join(", ")}.`);
  }
  const requestedRenderer: "css" | "webgpu" = query.get("renderer") === "css" ? "css" : "webgpu";
  const requestedScale = Number.parseFloat(query.get("scale") ?? "1");
  const frames = Number.parseInt(query.get("frames") ?? `${DEFAULT_FRAMES}`, 10);

  const placed: PlacedScene = resolveScene(sceneId);
  const problems: string[] = [];

  /*
   * The viewport must be exactly the canvas.
   *
   * X1 puts glass in viewport-fixed planes, and the renderer cover-fits a
   * backdrop texture to the *viewport* — so a viewport of a different aspect
   * ratio would map the raster onto the screen differently from the `<img>` the
   * page composites, and the glass would refract pixels that are not the ones
   * behind it. That is not a cosmetic mismatch; it silently invalidates the
   * material measurement, so it is checked rather than assumed.
   */
  if (window.innerWidth !== CANVAS.width || window.innerHeight !== CANVAS.height) {
    problems.push(
      `The viewport is ${window.innerWidth}×${window.innerHeight} CSS px but the scene canvas is ` +
        `${CANVAS.width}×${CANVAS.height}. The renderer cover-fits the backdrop texture to the ` +
        "viewport, so the glass would sample a differently-framed raster than the page shows.",
    );
  }
  if (window.devicePixelRatio !== requestedScale) {
    problems.push(
      `?scale=${requestedScale} was asked for but devicePixelRatio is ${window.devicePixelRatio}. ` +
        "The capture's pixel size would not match the native fixture's.",
    );
  }

  const url = await backgroundUrl(placed.backgroundId);
  const image = await loadBackground(url);
  if (image.naturalWidth !== CANVAS.width * requestedScale) {
    problems.push(
      `The committed raster is ${image.naturalWidth}×${image.naturalHeight} px, which is not ` +
        `${CANVAS.width}×${CANVAS.height} at scale ${requestedScale}. Both sides must composite ` +
        "the same raster at 1:1 or the step edges are resampled before they are measured.",
    );
  }

  const stage = document.getElementById("stage");
  if (stage === null) throw new Error("the page has no #stage");
  stage.style.width = `${CANVAS.width}px`;
  stage.style.height = `${CANVAS.height}px`;
  stage.append(image);

  const adapter = await probeAdapter();

  const diagnostics: { code: string; severity: string; message: string }[] = [];
  // Forwarded, never interpreted: the page has no opinion about an optical
  // number, and reading one here to "check" it would put a second copy of the
  // material's constants in the harness.
  const materialProfile = window.__vitreaMaterialProfile;
  const root = createGlassRoot({
    renderer: requestedRenderer,
    ...(materialProfile === undefined ? {} : { materialProfile }),
    // Dev mode on: the overlap and padding checks are exactly the findings that
    // would invalidate a capture, and they are cheaper to read here than to
    // rediscover in a diff.
    devMode: true,
    // Frames are stepped by hand. A calibration still has to be a *chosen*
    // frame: the GPU tier's backdrop adaptation converges over frames, so "the
    // frame rAF happened to deliver" would make the capture depend on timing.
    autoStart: false,
    diagnosticSink: (diagnostic: VitreaDiagnostic) =>
      diagnostics.push({
        code: diagnostic.diagnostic.code,
        severity: diagnostic.diagnostic.severity,
        message: diagnostic.diagnostic.message,
      }),
  });

  for (const group of placed.groups) {
    if (group.source === "texture") {
      const sourceId = `${group.id}.raster`;
      root.registerBackdropSource({
        id: sourceId,
        kind: "texture",
        // The raster is a same-origin PNG served by this dev server and it is a
        // plain 2-D image, so both probe answers are facts about the file rather
        // than optimism. Reporting `analysis: "exact"` for a frame and then
        // withdrawing it is precisely what X2 exists to prevent.
        probe: { taint: "clean", textureCompatibility: "compatible" },
      });
      root.registerGroup({
        id: group.id,
        backdropSourceId: sourceId,
        ...(group.mergeDistance === undefined ? {} : { mergeDistance: group.mergeDistance }),
      });
      // core's texture source deliberately carries no pixels (X4), so the pixels
      // arrive here — and they are the *same element* the page composites, not a
      // re-decode of the same file.
      root.setBackdropTexture(sourceId, { kind: "image", image });
      root.scene.markBackdropSourceDirty(sourceId);
    } else {
      root.registerGroup({
        id: group.id,
        ...(group.mergeDistance === undefined ? {} : { mergeDistance: group.mergeDistance }),
      });
    }
  }

  const handles = new Map<string, GlassHostHandle>();
  for (const surface of placed.surfaces) {
    const host = document.createElement("div");
    // Decoration, and nothing else: the scenes carry no text and no semantics,
    // so the host stays out of the accessibility tree and out of hit-testing.
    host.setAttribute("aria-hidden", "true");
    host.className = "glass-host";
    host.style.left = `${surface.left}px`;
    host.style.top = `${surface.top}px`;
    host.style.width = `${surface.width}px`;
    host.style.height = `${surface.height}px`;

    // The app owns placement; vitrea never moves the element. The asChild contract.
    root.plane(surface.plane).hostLayer.append(host);

    const handle = root.registerHost({
      host,
      nodeId: surface.nodeId,
      groupId: surface.groupId,
      plane: surface.plane,
      shapeFamily: surface.family,
      // Uniform, per X8's v1 restriction. The renderer resolves these on the
      // `apple-continuous` corner reference by default, which is the same curve
      // the native side asks for with `RoundedRectangle(style: .continuous)`.
      radii: [surface.radius, surface.radius, surface.radius, surface.radius],
      variant: "regular",
      ...(placed.pressed ? { interaction: "pressed" as const } : {}),
    });
    handles.set(surface.nodeId, handle);
    if (placed.pressed) applyPressedPose(host, handle);
  }

  // Settled includes "failed": waiting here is waiting to learn the answer.
  await root.ready();

  /*
   * Frames are stepped with a yield between them, and that yield is load-bearing.
   *
   * The GPU tier's adaptive tint is driven by an analysis reduction read back off
   * the device: the bridge fires `collectAdaptation()` once per frame and never
   * blocks on it, so the observation lands on a later microtask. Stepped in a
   * tight synchronous loop, none of those promises can resolve until after the
   * final draw — so every capture rendered the material's *un-adapted* tint, and
   * the count of frames made no difference at all (measured: byte-identical at 8
   * and at 240). An app driving vitrea from a real rAF loop always renders the
   * adapted tint, so calibrating against the un-adapted one would fit every
   * material constant to a state no application ever shows.
   *
   * Yielding to the macrotask queue between frames is what lets each frame's
   * readback reach the next frame's draw. The first observation jumps rather than
   * filters (the renderer resets rather than low-passes from zero, so a page does
   * not fade in from black), so convergence on a static backdrop takes a couple
   * of frames rather than the filter's 500 ms — but the default count is left
   * well above that, and `frames` remains a URL parameter so the settled state
   * can be re-verified rather than assumed.
   */
  for (let index = 0; index < frames; index += 1) {
    root.runFrame(index * FRAME_MS);
    await new Promise((resolve) => requestAnimationFrame(() => resolve(undefined)));
  }

  // Two frame callbacks after the last draw, so what the compositor is showing
  // is the frame that was just drawn rather than the one before it. This is the
  // last third of the readiness signal, and it is a presentation *event* rather
  // than an interval.
  await new Promise((resolve) => requestAnimationFrame(() => resolve(undefined)));
  await new Promise((resolve) => requestAnimationFrame(() => resolve(undefined)));

  const renderInput = root.renderInput();
  const boundsOf = (nodeId: string): SurfaceReport["bounds"] => {
    for (const plane of renderInput?.planes ?? []) {
      for (const node of plane.nodes) {
        if (node.nodeId === nodeId) {
          const { x, y, width, height } = node.bounds;
          return { x, y, width, height };
        }
      }
    }
    return undefined;
  };
  const refractionOf = (nodeId: string): Record<string, string> | undefined => {
    for (const plane of renderInput?.planes ?? []) {
      for (const node of plane.nodes) {
        if (node.nodeId === nodeId) return { ...node.refraction };
      }
    }
    return undefined;
  };

  const groups: GroupReport[] = placed.groups.map((group) => ({
    id: group.id,
    configuredSource: group.source,
    ...(group.mergeDistance === undefined ? {} : { mergeDistance: group.mergeDistance }),
    ...(group.declaredSpacing === undefined ? {} : { declaredSpacing: group.declaredSpacing }),
    state: root.capabilities(group.id),
    probeVerdict: root.probeReport(group.id)?.verdict,
  }));

  // The one thing a capture may not do: claim a renderer it did not get. The
  // driver reads this and labels the cell with what drew, but a *requested* GPU
  // tier that silently produced CSS glass is worth naming here too, so the
  // fallback is on the record at the point it happened.
  for (const group of groups) {
    if (requestedRenderer === "webgpu" && group.state?.activeRenderer !== "webgpu") {
      problems.push(
        `Group "${group.id}" was asked for the webgpu tier and resolved to ` +
          `"${group.state?.activeRenderer ?? "nothing"}"` +
          (group.state?.demotionReason === undefined
            ? ""
            : ` (${group.state.demotionReason})`) +
          ". The capture is CSS-tier data and must be labelled as such.",
      );
    }
  }

  return {
    sceneId,
    requestedRenderer,
    requestedScale,
    devicePixelRatio: window.devicePixelRatio,
    frames,
    canvas: CANVAS,
    pixelSize: [
      Math.round(CANVAS.width * window.devicePixelRatio),
      Math.round(CANVAS.height * window.devicePixelRatio),
    ],
    background: {
      id: placed.backgroundId,
      url,
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
    },
    pressed: placed.pressed,
    materialProfile: materialProfile ?? null,
    groups,
    surfaces: placed.surfaces.map((surface) => ({
      nodeId: surface.nodeId,
      groupId: surface.groupId,
      plane: surface.plane,
      family: surface.family,
      radius: surface.radius,
      bounds: boundsOf(surface.nodeId),
      refraction: refractionOf(surface.nodeId),
    })),
    webgpu:
      root.webgpu === undefined
        ? undefined
        : {
            available: root.webgpu.available,
            deviceHealth: root.webgpu.deviceHealth,
            ownership: root.webgpu.ownership,
          },
    rendererActive: root.rendererBridge?.active ?? false,
    adapter,
    canvasColorSpace: readCanvasColorSpace(root),
    diagnostics,
    problems,
  };
}

const ready = build();
window.__vitreaCalibration = { ready };

ready.then(
  (report) => {
    window.__vitreaCalibration.report = report;
    document.documentElement.setAttribute("data-scene-ready", "1");
  },
  (error: unknown) => {
    const message = error instanceof Error ? error.message : String(error);
    document.documentElement.setAttribute("data-scene-error", message);
    // Visible, so a human opening the URL by hand sees the reason rather than a
    // blank 320×200 rectangle.
    const stage = document.getElementById("stage");
    if (stage !== null) stage.textContent = message;
  },
);
