/**
 * `createGlassRoot` — the one object an app (or `vitrea-react`) holds.
 *
 * Everything else in this package is a piece; this is the wiring. It owns the
 * scene and the scheduler from core, the plane DOM, the read protocol, the
 * proxies, the probe, the media feed and the WebGPU lifecycle, and it drives the
 * five phases. core is passive by contract: it never schedules and never reads a
 * clock, so the `requestAnimationFrame` loop lives here and the frame's time
 * arrives as a number.
 *
 * ## The renderer option, and why the default is the CSS tier
 *
 * `renderer: "css"` (the default) wires no GPU at all: no adapter request, no
 * device, and every group resolves to the CSS tier. That is not a placeholder
 * for a missing C6 — it is the honest configuration of a root with no WebGPU in
 * play, and it is the configuration in which the fallback has to look
 * *intentional* rather than broken. `renderer: "webgpu"` asks for a device and
 * hands it to whatever renderer attaches; groups then resolve to the WebGPU tier
 * and the CSS tier steps aside for them, because painting both would be the
 * "silently pretending" this codebase refuses.
 *
 * ## What C6 reads
 *
 * `root.renderInput()` — per plane, the nodes with their measured rects, their
 * resolved material, their optics after the accessibility fold, and **both**
 * refraction caps plus the resolved lower of the two (Decision Log #19's dual-cap
 * rule). It is assembled in the `write` phase from the frame's resolution, so a
 * renderer never walks the scene itself and never measures anything.
 */

import {
  createDiagnosticsChannel,
  createFrameScheduler,
  createGlassScene,
  resolveMaterial,
  type AccessibilityOverrides,
  type BackdropSourceDescriptor,
  type FrameInfo,
  type FrameReport,
  type GlassGroupDescriptor,
  type GlassGroupState,
  type GlassPlane,
  type GlassScene,
  type MaterialVariant,
  type PlatformProbe,
  type Rect,
  type RefractionQuality,
  type ResolvedAccessibilityPolicy,
  type ResolvedForegroundAdaptation,
  type ResolvedMaterial,
  type ShapeFamily,
  type WebGPURendererModule,
} from "@vitreajs/vitrea";

import { createBackdropProxyManager, type ProxyRequest } from "./backdrop-proxy";
import { readHostChannels, type SurfaceChannelValues } from "./channels";
import {
  cssTierDeclarations,
  foregroundDeclarations,
  hintedBackdropLuminance,
  type StyleDeclarations,
} from "./css-tier";
import {
  consoleDiagnosticSink,
  createPlatformDiagnosticsChannel,
  type PlatformDiagnosticsChannel,
  type VitreaDiagnosticSink,
} from "./diagnostics";
import { createGeometrySync, type GeometrySync } from "./geometry-sync";
import { effectiveGroupState, type ProbeVerdict } from "./group-state";
import {
  DEFAULT_HOST_SHAPE,
  HOST_ATTRIBUTES,
  nextNodeId,
  type GlassHostHandle,
  type GlassHostOptions,
  type GlassHostPatch,
} from "./host";
import { installInkStylesheet, type InkStylesheetHandle } from "./ink-stylesheet";
import { checkLayerModel } from "./layer-model";
import { createLayoutReadMeter, flushStyle, type LayoutReadMeter, type ViewportReading } from "./measure";
import {
  browserMediaMatcher,
  observeAccessibilityPreferences,
  type AccessibilityFeed,
  type MediaMatcher,
} from "./media-policy";
import {
  CSS_TIER_MAPPING,
  cssTierOptics,
  gpuTierForegroundLevel,
  occlusionAlphaUnderPolicy,
  opticsUnderPolicy,
  resolvedPolicyFold,
  sourceOptics,
  type CssTierMapping,
  type MaterialOptics,
} from "./optics";
import { createGlassLayerManager, type GlassLayerManager, type PlaneLayers } from "./planes";
import {
  describeEngineDefect,
  describeProbeFailure,
  probeGroup,
  probePlatform,
  type BackdropRootBreak,
  type EngineDefectHazard,
  type GroupProbeReport,
  type PlatformProbeReport,
} from "./probe";
import { accessibilityRefractionCap, effectiveRefraction } from "./refraction";
import {
  createGlassRendererBridge,
  type GlassBackdropTexture,
  type GlassRendererBridge,
  type RendererMaterialProfile,
} from "./renderer-bridge";
import { createWebGPULifecycle, type WebGPULifecycle, type WebGPUStatus } from "./webgpu";

/** Every glass group needs a backdrop source; a dom root gets this one for free. */
export const DEFAULT_DOM_SOURCE_ID = "vitrea.dom";

export interface GlassRootOptions {
  readonly container?: HTMLElement;
  readonly zIndex?: number;
  /** Dev-mode checks — overlap, variant mixing, the probe's messages. Default true. */
  readonly devMode?: boolean;
  readonly accessibilityOverrides?: AccessibilityOverrides;
  /** Where findings from both code spaces go. Defaults to the console in dev mode. */
  readonly diagnosticSink?: VitreaDiagnosticSink;
  /** Which renderer this root wires. Default `"css"`; see the module comment. */
  readonly renderer?: "css" | "webgpu";
  readonly webgpu?: {
    readonly device?: GPUDevice;
    readonly powerPreference?: GPUPowerPreference;
    /**
     * An app-owned device was lost and only the app can replace it.
     *
     * The app owns the resources that would have to be re-registered, so vitrea
     * reports the loss and waits rather than inventing a device it was not given
     * (§GPU device ownership). Answer it by building a new device and handing it
     * to `root.replaceDevice`; without both halves wired, app-owned device loss
     * is terminal.
     */
    readonly onReplacementNeeded?: () => void;
    /**
     * Resolve the renderer module yourself, instead of through X7's dynamic
     * import.
     *
     * The seam already exists one layer down, on the bridge; this forwards it.
     * Two callers want it: a build that cannot code-split and would rather hand
     * the renderer over directly than have a dynamic import it must inline
     * anyway, and a test that needs the GPU tier's *bookkeeping* — tier
     * resolution, proxies, plane structure — on a machine with no adapter. The
     * default is the lazy import, and a CSS-tier bundle still carries no WGSL.
     */
    readonly load?: () => Promise<WebGPURendererModule>;
  };
  /**
   * Optical tunables for the material, honoured by **both** tiers.
   *
   * A patch over the renderer's own `DEFAULT_MATERIAL_PROFILE`, which is where
   * every optical number lives (C7 calibrates them there). The GPU tier receives
   * it unchanged; the CSS tier derives its declarations from the same patch
   * through `cssTierOptics`, because the two composite differently and a shared
   * number is not a shared material (corrective K5 — before it, a CSS-tier root
   * ignored this entirely and drew at more than twice the GPU tier's
   * transparency).
   */
  readonly materialProfile?: RendererMaterialProfile;
  /**
   * The CSS tier's side of that crossing: what a renderer quantity costs to
   * express as `backdrop-filter` plus an sRGB overlay.
   *
   * Calibration's seam, not an application knob — the shipped mapping is tuned
   * against the dom-tier cells and an app that replaces it is choosing a
   * different material for its CSS-tier visitors. `@vitrea/react` deliberately
   * does not surface it.
   */
  readonly cssTierMapping?: Partial<CssTierMapping>;
  /** Drive frames from `requestAnimationFrame`. Default true; tests step manually. */
  readonly autoStart?: boolean;
  readonly matcher?: MediaMatcher;
  readonly window?: Window;
}

/** One surface, as a renderer wants it: measured, resolved, capped. */
export interface GlassNodeRenderInput {
  readonly nodeId: string;
  readonly groupId: string;
  readonly plane: GlassPlane;
  readonly order: number;
  /** Viewport CSS px, from the read phase. A renderer never measures. */
  readonly bounds: Rect;
  readonly shapeFamily: ShapeFamily;
  readonly radii: readonly [number, number, number, number];
  readonly smoothing: number;
  readonly thickness: number;
  /**
   * The motion drivers' outputs for this surface, read off the host's own inline
   * custom properties (see `channels.ts`). Every value, never a time — §Motion
   * puts the drivers on the CPU and a renderer consumes what they produced.
   */
  readonly channels: SurfaceChannelValues;
  readonly material: ResolvedMaterial;
  readonly foreground: ResolvedForegroundAdaptation;
  readonly optics: MaterialOptics;
  /**
   * The dual-cap rule, shown rather than pre-collapsed: both inputs travel
   * alongside the resolved lower of the two, so a renderer honouring
   * `effective` can still report *why* it was capped.
   */
  readonly refraction: {
    readonly state: RefractionQuality;
    readonly accessibilityCap: RefractionQuality;
    readonly effective: RefractionQuality;
  };
  /**
   * The vitrea-owned visual transform currently on the host, for reporting only.
   *
   * A renderer must not compose it on top of `bounds`. Press compression, lensing
   * deformation and morph interpolation reach the GPU tier through `channels` —
   * the motion drivers' outputs, which is the one channel §Motion puts them on —
   * and folding this string in as well would apply the same deformation twice.
   * It travels because a devtool inspecting a frame wants to see what vitrea
   * wrote to the element, and nothing else reads it.
   */
  readonly ownedTransform: string | undefined;
}

export interface GlassGroupRenderInput {
  readonly groupId: string;
  readonly state: GlassGroupState;
  readonly probe: GroupProbeReport;
  /** Which source this group samples. A renderer binds it only where X2 allows. */
  readonly backdropSourceId: string;
  readonly variant: MaterialVariant;
  readonly samplingPadding: number;
  readonly mergeDistance: number;
  readonly blurRadius: number;
  /**
   * The scene's own declared `mergeDistance`, `undefined` when the app never
   * set one. Distinct from `mergeDistance` above: that field is core's
   * *resolved* proxy-geometry number (always present, defaulting to
   * `samplingPadding` — X1's proxy math needs a number regardless). This one
   * is what the GPU-tier union mapping (`groupUnionFromMergeDistance`) reads,
   * so an app that never declared a distance keeps `DEFAULT_GROUP_UNION`
   * exactly rather than inheriting the proxy default.
   */
  readonly declaredMergeDistance: number | undefined;
}

export interface GlassPlaneRenderInput {
  readonly plane: GlassPlane;
  readonly layers: PlaneLayers;
  readonly nodes: readonly GlassNodeRenderInput[];
}

export interface GlassFrameRenderInput {
  readonly frame: FrameInfo;
  readonly accessibility: ResolvedAccessibilityPolicy;
  readonly planes: readonly GlassPlaneRenderInput[];
  readonly groups: readonly GlassGroupRenderInput[];
  /**
   * The viewport as the read phase last measured it. A renderer sizes its
   * targets from this and bumps a size epoch when it changes — never from
   * `window`, which it has no business reading.
   */
  readonly viewport: ViewportReading | undefined;
  readonly device: GPUDevice | undefined;
}

export interface GlassRoot {
  readonly scene: GlassScene;
  readonly layers: GlassLayerManager;
  readonly platformProbe: PlatformProbeReport;
  readonly readMeter: LayoutReadMeter;
  readonly diagnostics: PlatformDiagnosticsChannel;

  plane(plane: GlassPlane): PlaneLayers;
  registerBackdropSource(descriptor: BackdropSourceDescriptor): void;
  /**
   * Supply the pixels behind a texture-configured backdrop source.
   *
   * core's `TextureBackdropSource` declares that a source *is* a texture and
   * carries no pixels — it may not know what an `HTMLCanvasElement` is (X4). This
   * is where the canvas, image or video arrives. Passing `undefined` withdraws
   * it.
   *
   * Supplying pixels marks the source dirty, so the next frame imports them: the
   * pyramid is rebuilt from the dirty-epoch ledger and nothing else, and a supply
   * that did not raise the epoch would sit unimported until something else
   * happened to. That covers the one-shot case — a decoded image handed over
   * once. A **video or canvas** source changes every frame by kind, and the frame
   * loop re-marks those itself, so an app does not re-mark them per frame either.
   *
   * A no-op on a CSS-tier root, so an app can call it unconditionally.
   */
  setBackdropTexture(sourceId: string, texture: GlassBackdropTexture | undefined): void;
  registerGroup(descriptor: Omit<GlassGroupDescriptor, "backdropSourceId"> & {
    readonly backdropSourceId?: string;
  }): void;
  removeGroup(groupId: string): void;
  registerHost(options: GlassHostOptions): GlassHostHandle;

  /** The resolved state of one group, with its own probe verdict folded in (X2). */
  capabilities(groupId: string): GlassGroupState | undefined;
  probeReport(groupId: string): GroupProbeReport | undefined;
  /** Re-run layer 2 for every group. Called on style mutations; also callable by hand. */
  revalidateProbe(): void;

  setAccessibilityOverrides(overrides: AccessibilityOverrides): void;
  /**
   * Replace the material's optical tunables, on whichever tier is drawing. The
   * patch replaces rather than accumulates, which is the renderer's rule; the
   * CSS tier re-derives its declarations from the same patch.
   */
  setMaterialProfile(profile: RendererMaterialProfile): void;
  readonly accessibility: ResolvedAccessibilityPolicy;
  readonly webgpu: WebGPUStatus | undefined;
  /**
   * Hand in a replacement for a lost app-owned device.
   *
   * The other half of `webgpu.onReplacementNeeded`: WebGPU has no cross-device
   * resource sharing, so every group stays demoted with `device-lost` until a
   * device arrives here and the renderer's re-registration handshake completes.
   * A no-op on a CSS-tier root.
   */
  replaceDevice(device: GPUDevice): void;
  /** The renderer bridge, on a `renderer: "webgpu"` root. Diagnostic surface. */
  readonly rendererBridge: GlassRendererBridge | undefined;
  /**
   * Resolves once the WebGPU lifecycle *and* the renderer load have settled;
   * immediately on a CSS root. Settled includes "failed": a caller waits to
   * learn the answer, not to be told it was yes.
   */
  ready(): Promise<void>;

  /** Run one frame by hand. `start()` runs them from rAF instead. */
  runFrame(timeMs?: number): FrameReport;
  renderInput(): GlassFrameRenderInput | undefined;
  start(): void;
  stop(): void;
  destroy(): void;
}

interface HostRecord {
  readonly nodeId: string;
  readonly groupId: string;
  readonly host: HTMLElement;
  plane: GlassPlane;
  order: number;
  readonly shapeFamily: ShapeFamily;
  radii: readonly [number, number, number, number];
  smoothing: number;
  thickness: number;
  ownedTransform: string | undefined;
  readonly onPlaneChange: ((plane: GlassPlane) => void) | undefined;
  /**
   * Whether this host has had the CSS tier's declarations applied even once.
   *
   * The first application is written with `transition: none`. Without that, the
   * tier's own transition animates *from the element's initial values* — a glass
   * surface fades in from fully transparent with no blur on its first frame,
   * which is an accident of the initial value rather than a designed
   * materialization (§Motion gives materialization its own monotonic driver).
   */
  cssMaterialized: boolean;
  /**
   * The CSS-tier declarations currently on this host, serialised.
   *
   * Kept so an unchanged frame writes nothing. Not an optimisation: every
   * `style.setProperty` is an attribute mutation, the probe re-audits on
   * attribute mutations, and an audit reads computed styles — so re-writing
   * identical declarations every frame would turn the steady state into a
   * read storm and make the zero-read guarantee false.
   */
  cssApplied: string | undefined;
  /**
   * The foreground pair currently on this host while the **GPU** tier is drawing,
   * serialised. A separate cache from `cssApplied` because the two write disjoint
   * property sets and either can be the live one on any frame.
   */
  gpuForegroundApplied: string | undefined;
}

/** Attributes the CSS tier writes, so stepping aside can remove exactly them. */
const clearDeclarations = (host: HTMLElement, declarations: StyleDeclarations): void => {
  for (const property of Object.keys(declarations)) host.style.removeProperty(property);
};

export function createGlassRoot(options: GlassRootOptions = {}): GlassRoot {
  const view = options.window ?? window;
  const devMode = options.devMode ?? true;
  const sink = options.diagnosticSink ?? (devMode ? consoleDiagnosticSink() : undefined);

  const meter = createLayoutReadMeter();
  const platformDiagnostics = createPlatformDiagnosticsChannel(
    sink === undefined ? undefined : (diagnostic) => sink({ origin: "platform", diagnostic }),
  );
  const coreDiagnostics = createDiagnosticsChannel(
    sink === undefined ? {} : { sink: (diagnostic) => sink({ origin: "core", diagnostic }) },
  );

  const platformProbe = probePlatform({ meter });
  if (!platformProbe.support.supported) {
    platformDiagnostics.report({
      code: "backdrop-filter-unsupported",
      severity: "warning",
      subjects: [],
      message:
        "Neither backdrop-filter nor -webkit-backdrop-filter is supported here, so no tier can blur the backdrop. Glass surfaces still render their tint, border and shadow — that is the honest maximum in this engine.",
    });
  }
  if (platformProbe.engine.family === "unknown") {
    platformDiagnostics.report({
      code: "engine-unrecognised",
      severity: "warning",
      subjects: [],
      message: `This engine is not in vitrea's conformance table, so the conservative row applies: proxy area is capped at ${platformProbe.conformance.maxProxyAreaDevicePx} device px and no engine behaviour is assumed. The probe fails closed by design.`,
    });
  }

  const layers = createGlassLayerManager({
    ...(options.container === undefined ? {} : { container: options.container }),
    ...(options.zIndex === undefined ? {} : { zIndex: options.zIndex }),
    document: view.document,
  });

  /*
   * The runtime's ink, at a precedence an application can beat (Decision Log
   * #34(c)). The host carries the `--vitrea-foreground` token and nothing else;
   * the `color` that resolves it lives in one static `:where()` rule installed
   * here. See `ink-stylesheet.ts` for why that, and why it is prepended rather
   * than adopted.
   */
  const inkStylesheet: InkStylesheetHandle = installInkStylesheet(view.document);

  const wantsWebGPU = (options.renderer ?? "css") === "webgpu";

  let probe: PlatformProbe = {
    // A root that wires no GPU never asked for one — "not-requested", not
    // "unavailable". core resolves that as a choice, not a fault (X2's K1
    // amendment, Decision Log #21c).
    //
    // A `wantsWebGPU` root starts "pending", which is the same amendment read
    // forwards. It did ask, and the answer has not arrived: "unavailable" would
    // resolve to `no-webgpu`, whose recovery is honestly `"none"` — a terminal
    // answer to a request still in flight, and the same inversion #21c fixed for
    // CSS-by-choice. "pending" resolves to the CSS tier with no fault named, so
    // the surfaces paint while the GPU tier comes up and nothing claims a loss
    // that has not happened.
    webgpu: wantsWebGPU ? "pending" : "not-requested",
    backdropFilter: platformProbe.support.supported,
    backdropProxyConformance: "pass",
    deviceHealth: "ok",
  };

  const scene = createGlassScene({ platform: probe, diagnostics: coreDiagnostics, devMode });
  scene.registerBackdropSource({ id: DEFAULT_DOM_SOURCE_ID, kind: "dom" });

  const scheduler = createFrameScheduler({ scene });
  const proxies = createBackdropProxyManager({
    plane: (plane) => layers.plane(plane),
    diagnostics: platformDiagnostics,
    document: view.document,
  });

  const hosts = new Map<string, HostRecord>();
  const probeReports = new Map<string, GroupProbeReport>();
  /**
   * Which groups need layer 2 re-run. `"all"` after an application CSS change,
   * because a theme switch or an animation start state can re-root any chain.
   *
   * The probe's inputs are application CSS, which mutates at runtime, so a
   * startup-only audit under-detects (S1 impact item 7) — but a per-frame audit
   * reads computed styles forever. A stale set is what makes it re-enterable
   * without being continuous.
   */
  let staleProbes: Set<string> | "all" = "all";
  let renderInput: GlassFrameRenderInput | undefined;
  let frameId = 0;
  let rafHandle: number | undefined;

  const geometry: GeometrySync = createGeometrySync({ scene, meter, window: view });

  const accessibilityFeed: AccessibilityFeed = observeAccessibilityPreferences({
    matcher: options.matcher ?? browserMediaMatcher(),
    onChange: (preferences) => scene.setSystemAccessibility(preferences),
  });
  scene.setSystemAccessibility(accessibilityFeed.preferences);
  if (options.accessibilityOverrides !== undefined) {
    scene.setAccessibilityOverrides(options.accessibilityOverrides);
  }

  const setProbe = (next: Partial<PlatformProbe>): void => {
    probe = { ...probe, ...next };
    scene.setPlatformProbe(probe);
  };

  /**
   * Set if this session has no GPU tier at all — the renderer chunk could not be
   * resolved, or a plane's canvas refused a `"webgpu"` context.
   *
   * A device with nothing painting behind it draws nothing, and a group resolved
   * onto the WebGPU tier there would be reporting a capability that is painting
   * nothing. `no-webgpu` is the honest name for both — there is no GPU tier in
   * this session, and its recovery is truthfully `"none"`. Note what this is
   * *not* set by: a lost device. core only raises `device-lost` where `webgpu`
   * is `"available"`, so clearing availability on loss would collapse a fault
   * that recovers into one that does not.
   */
  let rendererUnavailable = false;

  /**
   * This tier's numbers, derived from the one profile the root carries. Held in
   * a binding rather than read from the module constant so `setMaterialProfile`
   * moves both tiers — the next frame's declarations are rebuilt from it, and
   * the per-host serialised diff writes only what actually changed.
   */
  const cssMapping: CssTierMapping = { ...CSS_TIER_MAPPING, ...options.cssTierMapping };
  let cssOptics = cssTierOptics(options.materialProfile, cssMapping);
  /**
   * The same profile *before* the tier conversion — the material the renderer is
   * drawing. The foreground decision needs it whenever the GPU tier is the one
   * painting, because the level behind the glyphs is that material's composite
   * and not the CSS tier's reproduction of it (Decision Log #32(b)).
   */
  let gpuOptics = sourceOptics(options.materialProfile);
  /**
   * The profile's policy constants, held alongside the two tiers' optics because
   * they are the part of the profile neither tier's optics can carry: they
   * multiply whatever numbers the regime is given rather than being those
   * numbers. Both are patchable and the renderer already draws with the patched
   * values, so the foreground decision and this tier's own fold have to use them
   * or they would model a material nothing draws.
   */
  let policyFold = resolvedPolicyFold(options.materialProfile);

  const bridge: GlassRendererBridge | undefined = wantsWebGPU
    ? createGlassRendererBridge({
        layers,
        diagnostics: platformDiagnostics,
        ...(options.materialProfile === undefined
          ? {}
          : { materialProfile: options.materialProfile }),
        ...(options.webgpu?.load === undefined ? {} : { load: options.webgpu.load }),
        onRendererUnavailable: () => {
          rendererUnavailable = true;
          setProbe({ webgpu: "unavailable" });
        },
      })
    : undefined;

  /**
   * Whether the bridge has finished settling for the *current* device.
   *
   * The bridge's work is serialised and asynchronous — resolve the renderer
   * chunk, attach the device, configure two canvases per plane — so there is a
   * window after the device arrives in which nothing can paint yet. Publishing
   * `"available"` inside that window is what made every GPU page load blank: core
   * resolved the groups onto the WebGPU tier, `root`'s write phase stripped their
   * CSS declarations, and the bridge was not drawing yet.
   */
  let bridgeSettled = false;
  /** Guards a late settle from answering for a device that has since been replaced. */
  let deviceEpoch = 0;

  /**
   * What `PlatformProbe.webgpu` should say right now, for a root that asked.
   *
   * Availability is the *paintability* question, not the device question: the
   * whole point of the value is to tell core which tier is drawing, and a device
   * with nothing behind it draws nothing. The one exception is a lost device,
   * which stays `"available"` on purpose — core raises `device-lost` only where
   * WebGPU is available, so withdrawing it there would collapse a fault whose
   * recovery is `"device-restored"` into one whose recovery is `"none"`.
   */
  const availabilityFor = (status: WebGPUStatus): PlatformProbe["webgpu"] => {
    if (!status.available || rendererUnavailable) return "unavailable";
    if (status.deviceHealth === "lost") return "available";
    if (!bridgeSettled) return "pending";
    return bridge?.active === true ? "available" : "unavailable";
  };

  const webgpu: WebGPULifecycle | undefined = wantsWebGPU
    ? createWebGPULifecycle({
        ...(options.webgpu?.device === undefined ? {} : { device: options.webgpu.device }),
        ...(options.webgpu?.powerPreference === undefined
          ? {}
          : { powerPreference: options.webgpu.powerPreference }),
        ...(options.webgpu?.onReplacementNeeded === undefined
          ? {}
          : { onReplacementNeeded: options.webgpu.onReplacementNeeded }),
        onStatusChange: (status) => {
          const epoch = (deviceEpoch += 1);
          bridgeSettled = false;
          bridge?.syncDevice(status);
          // This callback only exists on a `wantsWebGPU` root, so WebGPU was
          // requested here by construction — "not-requested" is out of range.
          setProbe({ webgpu: availabilityFor(status), deviceHealth: status.deviceHealth });
          // `syncDevice` was queued synchronously above, so the bridge's own
          // settle promise already covers it. Re-publishing afterwards is what
          // turns "pending" into the real answer — and it is an answer either
          // way: a bridge that settles inactive is a session with no GPU tier
          // painting, which is `"unavailable"` however healthy the device is.
          void (bridge?.ready() ?? Promise.resolve()).then(() => {
            if (epoch !== deviceEpoch) return;
            bridgeSettled = true;
            setProbe({ webgpu: availabilityFor(status), deviceHealth: status.deviceHealth });
          });
          if (status.deviceHealth === "lost") {
            platformDiagnostics.report({
              code: "webgpu-device-lost",
              severity: "warning",
              subjects: [],
              message:
                status.ownership === "vitrea"
                  ? "The GPUDevice was lost. Affected groups carry demotionReason \"device-lost\" while vitrea re-requests a device automatically."
                  : "The app-owned GPUDevice was lost. Groups stay demoted until a replacement device is supplied and C6's resource re-registration handshake completes.",
            });
          } else if (!status.available) {
            platformDiagnostics.report({
              code: "webgpu-unavailable",
              severity: "warning",
              subjects: [],
              message: `No WebGPU device (${status.unavailableReason ?? "unknown"}). This session renders on the CSS tier; core reports demotionReason "no-webgpu", whose recovery is honestly "none" — enabling support means a new session.`,
            });
          }
        },
      })
    : undefined;

  /**
   * Settled means "the answer is known", not "the answer was yes": the device
   * handshake *and* the renderer load, so a caller that awaits this and then
   * steps a frame is looking at the tier this session actually resolved to.
   */
  const readyPromise: Promise<void> =
    webgpu === undefined
      ? Promise.resolve()
      : webgpu.start().then(() => bridge?.ready() ?? undefined);

  /**
   * Layer 2 for one group. Proxies only exist once a group has measured members,
   * so before the first read the group is presumed to pass: refusing to render
   * on the strength of an audit that could not run yet would demote every group
   * for one frame at startup.
   */
  const auditPlane = (groupId: string, plane: GlassPlane): GroupProbeReport => {
    // A group demoted by this very probe has no proxy — demotion removes it —
    // so auditing only groups that *have* one would make `probe-failed`
    // unrecoverable, and every demotion reason is required to name a recovery.
    // The plane's proxy layer stands in: the walk starts at `from`'s parent, so
    // both start at the plane root and audit exactly the same chain. The proxy
    // layer is vitrea's own element and carries no trigger by construction.
    const from = proxies.proxyFor(groupId, plane) ?? layers.plane(plane).proxyLayer;
    return probeGroup({ groupId, proxy: from, window: view }, platformProbe, meter);
  };

  /**
   * Layer 2 for one group, over every plane it has surfaces on.
   *
   * A split group has one proxy per plane, sitting under different ancestors —
   * two chains, either of which can be re-rooted on its own. The group's report
   * is therefore the union: it passes only where every plane passes, because a
   * group whose second plane samples nothing is not a group in good health, and
   * auditing only the first plane made the second one's re-rooting invisible.
   */
  const auditGroup = (groupId: string, planes: Iterable<GlassPlane>): GroupProbeReport => {
    const breaks: BackdropRootBreak[] = [];
    // Collected across every plane, like `breaks`: a split group's second plane
    // can sit under a rounded, clipping ancestor the first one does not.
    const engineDefects: EngineDefectHazard[] = [];
    let verdict: GroupProbeReport["verdict"] = "pass";
    let reach = platformProbe.reach;
    let audited = false;

    for (const plane of planes) {
      const perPlane = auditPlane(groupId, plane);
      audited = true;
      reach = perPlane.reach;
      engineDefects.push(...perPlane.engineDefects);
      if (perPlane.verdict === "fail") {
        verdict = "fail";
        breaks.push(...perPlane.breaks);
      }
    }

    const report: GroupProbeReport = audited
      ? { groupId, verdict, breaks, engineDefects, reach }
      : // Nothing measured yet, so nothing to walk. Presumed passing, for the
        // same reason the first frame presumes it: refusing to render on an
        // audit that could not run would demote every group at startup.
        { groupId, verdict: "pass", breaks: [], engineDefects: [], reach };

    const previous = probeReports.get(groupId);
    probeReports.set(groupId, report);

    if (report.verdict === "fail" && previous?.verdict !== "fail" && devMode) {
      platformDiagnostics.report({
        code: "backdrop-root-broken",
        severity: "error",
        subjects: [groupId],
        message: describeProbeFailure(report),
      });
    }

    /*
     * Layer 3's per-group advisory (Decision Log #39). A warning rather than an
     * error, and never a demotion: the engine drops the filter without saying
     * so and no readback path in the page can see it, so the honest act is to
     * name the defect, its repro and its workarounds and let the author decide.
     * The channel dedupes on code plus subjects, so a group that stays in the
     * hazardous shape says this once per session rather than once per audit.
     */
    if (devMode) {
      for (const hazard of report.engineDefects) {
        platformDiagnostics.report({
          code: "engine-known-defect",
          severity: "warning",
          subjects: [groupId, hazard.defect.id],
          message: describeEngineDefect(groupId, hazard.defect, hazard.ancestor),
        });
      }
    }
    return report;
  };

  const verdictFor = (groupId: string): ProbeVerdict =>
    probeReports.get(groupId)?.verdict ?? "pass";

  const stateFor = (groupId: string): GlassGroupState | undefined => {
    const record = scene.glassGroup(groupId);
    if (record === undefined) return undefined;
    const source = scene.backdropSource(record.descriptor.backdropSourceId);
    if (source === undefined) return undefined;

    const hint = record.descriptor.backdrop !== undefined
      ? "author-hint"
      : record.descriptor.estimator !== undefined
        ? "estimator"
        : "none";
    const governor = record.governor ?? "none";

    return source.descriptor.kind === "texture"
      ? effectiveGroupState({
          configuredSource: "texture",
          platform: probe,
          // Whether pixels were ever handed over is a platform-side fact — core
          // holds a declaration, the bridge holds the canvas — folded into the
          // per-source probe the same way this group's own proxy verdict is
          // folded into `backdropProxyConformance` (Decision Log #21a). Only
          // asked where there is a bridge to ask: on a CSS-tier root nothing
          // samples a texture at all, and "no pixels supplied" would be naming a
          // loss the tier never had.
          source:
            bridge === undefined
              ? source.descriptor.probe
              : {
                  ...source.descriptor.probe,
                  supply: bridge.hasBackdropTexture(source.descriptor.id)
                    ? "supplied"
                    : "absent",
                },
          governor,
          hint,
          probe: verdictFor(groupId),
        })
      : effectiveGroupState({
          configuredSource: "dom",
          platform: probe,
          governor,
          hint,
          probe: verdictFor(groupId),
        });
  };

  /**
   * Re-audit when the audited chain's computed styles could have changed. The
   * probe's inputs are application CSS, which mutates at runtime — hover states,
   * animations, theme switches — so a startup-only probe under-detects (S1
   * impact item 7). Attribute mutations are the observable proxy for that;
   * watching them costs nothing until one happens.
   */
  const styleObserver = new MutationObserver((records) => {
    // vitrea's own writes are not application CSS. Ignoring them is precise
    // rather than convenient: the audited chain runs from a proxy *upwards*, so
    // a re-rooting style inside the glass root would be this package's bug, and
    // treating our own per-frame writes as app changes would re-audit forever.
    const external = records.some(
      (record) => record.target instanceof Node && !layers.root.contains(record.target),
    );
    if (external) staleProbes = "all";
  });
  styleObserver.observe(view.document.documentElement, {
    attributes: true,
    attributeFilter: ["style", "class"],
    subtree: true,
  });

  const write = (frame: FrameInfo, resolution: FrameReport["resolution"]): void => {
    const viewport = geometry.viewport;
    if (viewport !== undefined) {
      layers.resizeCanvases(viewport.width, viewport.height, viewport.devicePixelRatio);
    }

    const accessibility = resolution.accessibility;
    const cap = accessibilityRefractionCap(accessibility.material);

    const groupInputs: GlassGroupRenderInput[] = [];
    const proxyRequests: ProxyRequest[] = [];
    const nodesByPlane = new Map<GlassPlane, GlassNodeRenderInput[]>();
    /**
     * Every group with something measured, and *every* plane its proxies belong
     * in. Recording only the first measured member's plane audited a split
     * group's chain on one plane and left the other unchecked for the session.
     */
    const auditablePlanes = new Map<string, Set<GlassPlane>>();

    for (const resolved of resolution.groups) {
      const groupId = resolved.groupId;
      const groupRecord = scene.glassGroup(groupId);
      if (groupRecord === undefined) continue;

      const variant = groupRecord.descriptor.material?.variant ?? "regular";
      const baseOptics = cssOptics[variant];
      const optics = opticsUnderPolicy(baseOptics, accessibility.material, policyFold);
      const state = stateFor(groupId) ?? resolved.state;

      const members = [...hosts.values()].filter((record) => record.groupId === groupId);
      const measured = members
        .map((record) => ({ record, bounds: scene.glassNode(record.nodeId)?.bounds }))
        .filter(
          (entry): entry is { record: HostRecord; bounds: Rect } => entry.bounds !== undefined,
        );

      const planesMeasured = new Set(measured.map((entry) => entry.record.plane));
      if (planesMeasured.size > 0) auditablePlanes.set(groupId, planesMeasured);

      groupInputs.push({
        groupId,
        state,
        probe: probeReports.get(groupId) ?? {
          groupId,
          verdict: "pass",
          breaks: [],
          engineDefects: [],
          reach: platformProbe.reach,
        },
        backdropSourceId: groupRecord.descriptor.backdropSourceId,
        variant,
        samplingPadding: resolved.sampling.samplingPadding,
        mergeDistance: resolved.sampling.mergeDistance,
        declaredMergeDistance: groupRecord.descriptor.mergeDistance,
        blurRadius: optics.blurRadius,
      });

      // The proxy path belongs to the WebGPU tier's dom sampling. The CSS tier
      // filters in place on the host, so a group there gets no proxy at all —
      // which is exactly why probe-failed demotes to it.
      if (state.activeRenderer === "webgpu" && state.samplingBackend === "css-backdrop") {
        for (const plane of planesMeasured) {
          const inPlane = measured.filter((entry) => entry.record.plane === plane);
          proxyRequests.push({
            groupId,
            plane,
            order: Math.min(...inPlane.map((entry) => entry.record.order)),
            members: inPlane.map((entry) => ({
              nodeId: entry.record.nodeId,
              bounds: entry.bounds,
              radii: [
                entry.record.radii[0],
                entry.record.radii[1],
                entry.record.radii[2],
                entry.record.radii[3],
              ],
            })),
            samplingPadding: resolved.sampling.samplingPadding,
            mergeDistance: resolved.sampling.mergeDistance,
            blurRadius: optics.blurRadius,
            saturation: optics.saturation,
          });
        }
      }

      for (const { record, bounds } of measured) {
        const nodeRecord = scene.glassNode(record.nodeId);
        const material: ResolvedMaterial = resolveMaterial({
          variant: nodeRecord?.descriptor.variant ?? variant,
          ...(groupRecord.descriptor.material?.dimming === undefined
            ? {}
            : { dimming: groupRecord.descriptor.material.dimming }),
          nodeId: record.nodeId,
          diagnostics: coreDiagnostics,
        });
        const foreground = resolution.nodes.find((node) => node.nodeId === record.nodeId)?.foreground;

        const input: GlassNodeRenderInput = {
          nodeId: record.nodeId,
          groupId,
          plane: record.plane,
          order: record.order,
          bounds,
          shapeFamily: record.shapeFamily,
          radii: record.radii,
          smoothing: record.smoothing,
          thickness: record.thickness,
          // An inline-style read: the same declaration block a binding wrote
          // into, never the cascade. It forces no style recalculation, so the
          // zero-read steady state survives it (see `channels.ts`).
          channels: readHostChannels(record.host, bounds),
          material,
          foreground: foreground ?? { adaptation: { mode: "fixed" } },
          optics,
          refraction: {
            state: state.refraction,
            accessibilityCap: cap,
            effective: effectiveRefraction(state.refraction, cap),
          },
          ownedTransform: record.ownedTransform,
        };

        const list = nodesByPlane.get(record.plane) ?? [];
        list.push(input);
        nodesByPlane.set(record.plane, list);

        // The CSS tier paints if and only if it is the active renderer. X6's
        // hint reaches it here: the node's resolved mode plus the group's
        // resolved hint tone, both already computed by core — this call
        // consumes that resolution rather than repeating it.
        const hint = {
          mode: (foreground ?? { adaptation: { mode: "fixed" as const } }).adaptation.mode,
          ...(resolved.hint.hint?.tone === undefined ? {} : { tone: resolved.hint.hint.tone }),
          // X6's optional luminance, forwarded rather than re-derived. Both tiers
          // need it because the foreground depends on how much of the backdrop
          // the material lets through, not only on its tone.
          ...(resolved.hint.hint?.luminance === undefined
            ? {}
            : { luminance: resolved.hint.hint.luminance }),
        };
        const declarations = cssTierDeclarations({
          radii: record.radii,
          optics: baseOptics,
          mapping: cssMapping,
          policyFold,
          policy: accessibility,
          foreground: hint,
        });
        if (state.activeRenderer === "css") {
          if (!record.cssMaterialized) {
            // Materialize with the transition off, then flush, then let the
            // normal write below arm it. Without the flush the browser batches
            // both writes into one change and transitions *from* the element's
            // initial values, so every surface fades in from transparent and
            // unblurred — an accident of the initial value, not a designed
            // materialization (§Motion gives that its own monotonic driver).
            record.host.style.setProperty("transition", "none");
            for (const [property, value] of Object.entries(declarations)) {
              if (property !== "transition") record.host.style.setProperty(property, value);
            }
            flushStyle(meter, record.host, view);
            record.cssMaterialized = true;
          }

          const serialised = JSON.stringify(declarations);
          if (record.cssApplied !== serialised) {
            for (const [property, value] of Object.entries(declarations)) {
              record.host.style.setProperty(property, value);
            }
            record.cssApplied = serialised;
          }
          // The CSS declarations carry the same foreground pair, so the GPU-tier
          // cache is stale rather than merely unused: dropping it makes a switch
          // back re-assert the ink instead of trusting a value another tier wrote.
          record.gpuForegroundApplied = undefined;
        } else {
          if (record.cssApplied !== undefined) {
            clearDeclarations(record.host, declarations);
            record.cssApplied = undefined;
          }

          /*
           * The GPU tier's foreground (Decision Log #32(b)).
           *
           * The material is the renderer's, so the level behind the glyphs is its
           * linear-light composite rather than the CSS tier's reproduction of one —
           * but the *decision* is the same decision, so it comes from the same
           * function. Before this the GPU tier published nothing, and an app
           * following the documented `var(--vitrea-foreground, …)` pattern fell
           * back to its own ink: measured on a dark-hinted surface at WCAG 1.57
           * against a 4.5 floor.
           *
           * Only this pair is written here. The tint, blur and border belong to
           * whichever tier is painting the body, and that is the canvas.
           */
          const hintedBackdrop = hintedBackdropLuminance(hint, cssMapping);
          const ink = foregroundDeclarations({
            policy: accessibility,
            mapping: cssMapping,
            ...(hintedBackdrop === undefined
              ? {}
              : {
                  level: gpuTierForegroundLevel(
                    {
                      ...gpuOptics[variant],
                      tintAlpha: occlusionAlphaUnderPolicy(
                        gpuOptics[variant].tintAlpha,
                        accessibility.material.occlusion,
                        policyFold.increasedOcclusionLift,
                      ),
                    },
                    hintedBackdrop,
                  ),
                }),
          });
          const serialisedInk = JSON.stringify(ink);
          if (record.gpuForegroundApplied !== serialisedInk) {
            for (const [property, value] of Object.entries(ink)) {
              record.host.style.setProperty(property, value);
            }
            record.gpuForegroundApplied = serialisedInk;
          }
        }
      }
    }

    const freshProxies = proxies.sync(proxyRequests, {
      devicePixelRatio: viewport?.devicePixelRatio ?? 1,
      maxProxyAreaDevicePx: platformProbe.conformance.maxProxyAreaDevicePx,
    });
    if (staleProbes !== "all") for (const groupId of freshProxies) staleProbes.add(groupId);

    // Auditing after the proxy sync is the only order that works: layer 2 walks
    // the proxy's own ancestor chain, so a freshly created proxy has to be in
    // the tree first. Only *stale* groups are audited, and the walk happens
    // inside the frame where its reads are counted — a per-frame audit would
    // perform a computed-style read per ancestor per group forever, and the
    // steady state is supposed to read nothing at all.
    for (const [groupId, planes] of auditablePlanes) {
      // `!probeReports.has(groupId)` is the third condition and it is not
      // redundant: the stale set starts at `"all"` and is emptied after the first
      // frame, so without it a group whose first measured frame comes later is
      // never audited at all — it inherits the presumed pass forever, and a late
      // group can claim a healthy GPU proxy path over a re-rooted chain
      // indefinitely.
      if (staleProbes === "all" || staleProbes.has(groupId) || !probeReports.has(groupId)) {
        auditGroup(groupId, planes);
      }
    }
    staleProbes = new Set();

    renderInput = {
      frame,
      accessibility,
      planes: layers.planes.map((planeLayers) => ({
        plane: planeLayers.plane,
        layers: planeLayers,
        nodes: (nodesByPlane.get(planeLayers.plane) ?? []).sort((a, b) => a.order - b.order),
      })),
      groups: groupInputs,
      viewport,
      device: webgpu?.status.device,
    };
  };

  scheduler.addParticipant({
    id: "vitrea.platform-web",
    read: () => geometry.read(),
    write: (context) => {
      if (context.resolution !== undefined) write(context.frame, context.resolution);
      // The dirty backdrop set is handed out in `write` and only there
      // (§Core model's invariant). Consuming it on a CSS root would be pointless
      // work, so only a wired bridge asks.
      if (bridge !== undefined && renderInput !== undefined) {
        // A video's imported external texture expires at task end and a live
        // canvas is repainted by its owner, so both are stale by the time the
        // next frame samples them. Nothing else marks them: the app is not
        // required to re-mark a source per frame, and before this a video froze
        // on its first imported frame forever.
        for (const sourceId of bridge.perFrameBackdropSources()) {
          if (scene.backdropSource(sourceId) !== undefined) {
            scene.markBackdropSourceDirty(sourceId);
          }
        }
        // The thunk, not the set: consuming commits `builtEpoch`, so the decision
        // belongs behind the bridge's own active/renderer guard rather than in
        // front of it. Consumed here and dropped there, a one-shot dirty mark —
        // a static raster imported once at startup, a device-loss recovery —
        // would be spent on a frame that built nothing and never come back.
        bridge.write(renderInput, () => context.consumeDirtyBackdropSources());
      }
    },
    // Drawing belongs to `render`, with the graph frozen — the same split the
    // renderer's own frame participant uses.
    render: () => {
      // What the renderer was handed and could not build. core committed
      // `builtEpoch` when it handed the request out, so an unbuilt source is
      // sitting clean at an epoch nobody imported; re-marking it costs one frame
      // of latency and needs no new core surface.
      for (const sourceId of bridge?.render() ?? []) {
        if (scene.backdropSource(sourceId) !== undefined) {
          scene.markBackdropSourceDirty(sourceId);
        }
      }
    },
  });

  const runFrame = (timeMs?: number): FrameReport => {
    frameId += 1;
    return scheduler.runFrame({ id: frameId, timeMs: timeMs ?? 0 });
  };

  const loop = (timeMs: number): void => {
    rafHandle = view.requestAnimationFrame(loop);
    runFrame(timeMs);
  };

  const root: GlassRoot = {
    scene,
    layers,
    platformProbe,
    readMeter: meter,
    diagnostics: platformDiagnostics,

    plane: (plane) => layers.plane(plane),

    registerBackdropSource(descriptor) {
      scene.registerBackdropSource(descriptor);
    },

    setBackdropTexture(sourceId, texture) {
      bridge?.setBackdropTexture(sourceId, texture);
      // Supplying pixels is a content change, and a content change that does not
      // raise the dirty epoch is invisible: the pyramid is rebuilt from that
      // ledger and nothing else. Before this, every caller in the repo reached
      // through `root.scene.markBackdropSourceDirty` by hand — including this
      // package's own e2e harness — while the doc above claimed this was the only
      // wiring the GPU tier needed.
      if (texture !== undefined && scene.backdropSource(sourceId) !== undefined) {
        scene.markBackdropSourceDirty(sourceId);
      }
    },

    registerGroup(descriptor) {
      scene.registerGlassGroup({
        ...descriptor,
        backdropSourceId: descriptor.backdropSourceId ?? DEFAULT_DOM_SOURCE_ID,
      });
    },

    removeGroup(groupId) {
      proxies.remove(groupId);
      probeReports.delete(groupId);
      scene.removeGlassGroup(groupId);
    },

    registerHost(hostOptions) {
      const nodeId = hostOptions.nodeId ?? nextNodeId();
      const plane = hostOptions.plane ?? "base";
      const order = hostOptions.order ?? hosts.size;
      const shape = {
        shapeFamily: hostOptions.shapeFamily ?? DEFAULT_HOST_SHAPE.shapeFamily,
        radii: hostOptions.radii ?? DEFAULT_HOST_SHAPE.radii,
        smoothing: hostOptions.smoothing ?? DEFAULT_HOST_SHAPE.smoothing,
        thickness: hostOptions.thickness ?? DEFAULT_HOST_SHAPE.thickness,
      };

      // An inline-style read, not a computed one: the app's own declaration
      // block, which forces no recalculation and costs the read meter nothing.
      // vitrea writes `transform` on a registered host and removes it on release,
      // so an app value sitting there is not composed with — it is destroyed, on
      // the first press or morph, with nothing to say why.
      if (devMode && hostOptions.host.style.transform !== "") {
        platformDiagnostics.report({
          code: "host-inline-transform",
          severity: "warning",
          subjects: [nodeId],
          message: `Host "${nodeId}" was registered carrying an inline transform (${hostOptions.host.style.transform}). vitrea owns the transform property on a registered host — press compression, lensing and morph all write it — so this value will be overwritten and then removed. Move it to an ancestor or a descendant element, or express it as a vitrea shape declaration.`,
        });
      }

      const hostLayer = layers.plane(plane).hostLayer;
      if (!hostLayer.contains(hostOptions.host) && devMode) {
        platformDiagnostics.report({
          code: "host-outside-plane",
          severity: "error",
          subjects: [nodeId],
          message: `Host "${nodeId}" is not inside the "${plane}" plane's host layer, so X1's sandwich cannot order it: its glass body would paint somewhere other than behind it. Render or portal the element into root.plane("${plane}").hostLayer.`,
        });
      }

      // The layer model, checked where it is decidable: registration is the
      // moment the app declares this element is glass, and the compositions the
      // rule forbids are structural, so nothing here belongs in a frame. Run
      // before `hosts.set` — `Node.contains` is true for self, and the candidate
      // must not be able to match itself. Production never reaches this call.
      if (devMode) {
        checkLayerModel(
          { nodeId, host: hostOptions.host },
          hosts.values(),
          (diagnostic) => platformDiagnostics.report(diagnostic),
        );
      }

      const record: HostRecord = {
        nodeId,
        groupId: hostOptions.groupId,
        host: hostOptions.host,
        plane,
        order,
        shapeFamily: shape.shapeFamily,
        radii: shape.radii,
        smoothing: shape.smoothing,
        thickness: shape.thickness,
        ownedTransform: undefined,
        onPlaneChange: hostOptions.onPlaneChange,
        cssMaterialized: false,
        cssApplied: undefined,
        gpuForegroundApplied: undefined,
      };
      hosts.set(nodeId, record);

      hostOptions.host.setAttribute(HOST_ATTRIBUTES.node, nodeId);
      hostOptions.host.setAttribute(HOST_ATTRIBUTES.group, hostOptions.groupId);
      hostOptions.host.setAttribute(HOST_ATTRIBUTES.plane, plane);
      // The host layer passes pointers through; a registered host opts back in,
      // so gaps between surfaces never swallow clicks on the page beneath.
      hostOptions.host.style.setProperty("pointer-events", "auto");

      scene.registerGlassNode({
        id: nodeId,
        groupId: hostOptions.groupId,
        shapeFamily: shape.shapeFamily,
        shape: {
          center: [0, 0],
          size: [0, 0],
          radii: shape.radii,
          smoothing: shape.smoothing,
          thickness: shape.thickness,
        },
        zSlot: { plane, order },
        ...(hostOptions.variant === undefined ? {} : { variant: hostOptions.variant }),
        ...(hostOptions.interaction === undefined ? {} : { interaction: hostOptions.interaction }),
        ...(hostOptions.foreground === undefined ? {} : { foreground: hostOptions.foreground }),
      });
      geometry.track({ nodeId, element: hostOptions.host });

      const handle: GlassHostHandle = {
        nodeId,
        groupId: hostOptions.groupId,
        host: hostOptions.host,
        get plane() {
          return record.plane;
        },

        update(patch: GlassHostPatch) {
          if (patch.radii !== undefined) record.radii = patch.radii;
          if (patch.smoothing !== undefined) record.smoothing = patch.smoothing;
          if (patch.thickness !== undefined) record.thickness = patch.thickness;
          if (patch.order !== undefined) record.order = patch.order;

          scene.updateGlassNode(nodeId, {
            shape: {
              center: [0, 0],
              size: [0, 0],
              radii: record.radii,
              smoothing: record.smoothing,
              thickness: record.thickness,
            },
            zSlot: { plane: record.plane, order: record.order },
            ...("variant" in patch ? { variant: patch.variant } : {}),
            ...("interaction" in patch ? { interaction: patch.interaction } : {}),
            ...("foreground" in patch ? { foreground: patch.foreground } : {}),
          });
          // Deliberately no `markDirty`. No field of `GlassHostPatch` can move
          // the host's border box — radii, smoothing, thickness, order, variant,
          // interaction and foreground are all material or sequencing — so a
          // re-measure here would read the same numbers at a cost. It was also
          // actively harmful: `getBoundingClientRect` reports the *transformed*
          // box, so an update landing while a vitrea-owned transform was live
          // (the press spring, mid-release) wrote the compressed rect into the
          // scene, and `setOwnedTransform` deliberately does not re-dirty, so it
          // stayed there.
        },

        invalidateGeometry() {
          geometry.markDirty(nodeId);
        },

        promoteTo(destination) {
          if (destination === record.plane) {
            platformDiagnostics.report({
              code: "redundant-promotion",
              severity: "warning",
              subjects: [nodeId],
              message: `Host "${nodeId}" was promoted to the "${destination}" plane it is already on.`,
            });
            return;
          }

          record.plane = destination;
          record.host.setAttribute(HOST_ATTRIBUTES.plane, destination);
          scene.updateGlassNode(nodeId, {
            zSlot: { plane: destination, order: record.order },
          });

          // The unit moves together: the body and highlight follow because they
          // are drawn from this node's plane in the render input, the proxy
          // because the next sync places it in the destination plane's layer,
          // and the semantic host because it is moved here — or by the consumer
          // that took placement over.
          //
          // Reparenting is a remove followed by an insert, and removing a focused
          // element from the document resets focus to the body. A morph that
          // silently dropped keyboard focus would be a real accessibility
          // regression, and it is invisible unless something restores it — so
          // this does.
          const wasFocused = view.document.activeElement === record.host;
          if (record.onPlaneChange === undefined) {
            layers.plane(destination).hostLayer.append(record.host);
          } else {
            record.onPlaneChange(destination);
          }
          if (wasFocused && view.document.activeElement !== record.host) record.host.focus();
          geometry.markDirty(nodeId);
        },

        setOwnedTransform(transform) {
          const had = record.ownedTransform !== undefined;
          record.ownedTransform = transform;
          if (transform === undefined) record.host.style.removeProperty("transform");
          else record.host.style.setProperty("transform", transform);
          // Setting or changing one marks nothing: `ResizeObserver` does not fire
          // for a transform, and the frames a press or a morph runs for are
          // exactly the frames that must stay at zero reads.
          //
          // *Clearing* one is different, and the difference is the bug this line
          // fixes. `getBoundingClientRect` reports the transformed box, so any
          // measurement taken while the transform was live is a measurement of
          // the compressed surface — around twelve times the geometry error
          // budget for a release-time press. Marking on the defined → undefined
          // edge is what re-reads the true border box once, and only once.
          if (had && transform === undefined) geometry.markDirty(nodeId);
        },

        release() {
          geometry.untrack(nodeId);
          hosts.delete(nodeId);
          scene.removeGlassNode(nodeId);
          for (const attribute of Object.values(HOST_ATTRIBUTES)) {
            record.host.removeAttribute(attribute);
          }
          record.host.style.removeProperty("pointer-events");
          record.host.style.removeProperty("transform");
          if (record.cssApplied !== undefined) {
            clearDeclarations(
              record.host,
              cssTierDeclarations({
                radii: record.radii,
                optics: cssOptics.regular,
                mapping: cssMapping,
                policy: scene.accessibilityPolicy(),
              }),
            );
          }
          if (record.gpuForegroundApplied !== undefined) {
            clearDeclarations(
              record.host,
              foregroundDeclarations({ policy: scene.accessibilityPolicy(), mapping: cssMapping }),
            );
          }
        },
      };

      return handle;
    },

    capabilities: (groupId) => stateFor(groupId),
    probeReport: (groupId) => probeReports.get(groupId),

    revalidateProbe() {
      for (const groupId of [...probeReports.keys()]) {
        const planes = new Set(
          [...hosts.values()]
            .filter((record) => record.groupId === groupId)
            .map((record) => record.plane),
        );
        // A group with no hosts left still gets its chain re-walked, at the base
        // plane's proxy layer, so a hand-called revalidation never silently skips
        // a group it holds a report for.
        auditGroup(groupId, planes.size === 0 ? ["base"] : planes);
      }
    },

    setMaterialProfile(profile) {
      // Both tiers, from one call. The CSS side re-derives rather than being
      // told: the mapping is what knows the crossing's cost, and a caller
      // handing the CSS tier its own alpha would be re-opening K5's gap by hand.
      cssOptics = cssTierOptics(profile, cssMapping);
      gpuOptics = sourceOptics(profile);
      policyFold = resolvedPolicyFold(profile);
      bridge?.setMaterialProfile(profile);
    },

    setAccessibilityOverrides(overrides) {
      scene.setAccessibilityOverrides(overrides);
    },

    get accessibility() {
      return scene.accessibilityPolicy();
    },

    get webgpu() {
      return webgpu?.status;
    },

    replaceDevice(device) {
      webgpu?.replaceDevice(device);
    },

    rendererBridge: bridge,

    ready: () => readyPromise,

    runFrame,
    renderInput: () => renderInput,

    start() {
      if (rafHandle === undefined) rafHandle = view.requestAnimationFrame(loop);
    },

    stop() {
      if (rafHandle !== undefined) {
        view.cancelAnimationFrame(rafHandle);
        rafHandle = undefined;
      }
    },

    destroy() {
      root.stop();
      styleObserver.disconnect();
      accessibilityFeed.stop();
      geometry.destroy();
      proxies.destroy();
      // The bridge first: it owns GPU resources built on the device the
      // lifecycle is about to destroy.
      bridge?.destroy();
      webgpu?.destroy();
      layers.destroy();
      inkStylesheet.dispose();
      hosts.clear();
      probeReports.clear();
    },
  };

  if (options.autoStart ?? true) root.start();

  return root;
}
