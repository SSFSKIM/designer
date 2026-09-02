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
  resolveGlassGroupState,
  resolveMaterial,
  type AccessibilityOverrides,
  type BackdropSourceDescriptor,
  type FrameInfo,
  type FrameReport,
  type ConcentricParent,
  type CornerReference,
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
import { foldProbeVerdict, groupCapabilityInputs, type ProbeVerdict } from "./group-state";
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
  adaptedSourceOptics,
  backdropToneAdaptation,
  backdropToneUnderPolicy,
  boundedForegroundLevel,
  CSS_TIER_MAPPING,
  cssOpticsFromSource,
  cssTierOptics,
  gpuTierForegroundBounds,
  gpuTierForegroundLevel,
  linearTint,
  occlusionAlphaUnderPolicy,
  opticsUnderPolicy,
  resolvedBackdropTone,
  resolvedBackdropToneResponse,
  resolvedPolicyFold,
  resolvedTintShade,
  sizeScatterSigmaAt,
  sizeThickness,
  sizeThicknessUnderPolicy,
  sourceOptics,
  sourceOuterShadow,
  sourceSize,
  tintedCssOptics,
  tintedSourceOptics,
  tintToneAdaptation,
  toneRespondedSourceOptics,
  type CssTierMapping,
  type LinearRgb,
  type MaterialOptics,
  type MaterialSourceOptics,
} from "./optics";
import {
  BACKDROP_TONE_CADENCE_MS,
  sampleBackdropTone,
  type BackdropToneSample,
} from "./backdrop-tone";
import { createGlassLayerManager, type GlassLayerManager, type PlaneLayers } from "./planes";
import { resolveSamplingGeometry } from "./proxy-geometry";
import { createTintParser, resolveTintDeclaration } from "./tint";
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
  /**
   * Which corner reference the shape is fit against, absent where the app did
   * not say and the renderer's `"apple-continuous"` default applies.
   *
   * Carried since Decision Log #23(c). Before that the renderer *had* the field
   * and nothing ever set it, so every surface took the default — including one
   * authored on the Figma smoothing axis, which is a different fit rather than a
   * different point on the same one.
   */
  readonly reference?: CornerReference;
  /** X8 rider 2's parent edge, absent for an ordinary surface. */
  readonly concentricOf?: ConcentricParent;
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
  /**
   * The backdrop's own average colour in linear light (W7) — X6's declared hint
   * where there is one, otherwise measured from the pixels the app supplied for
   * this group's backdrop source, and absent where neither exists.
   *
   * Resolved here, once per group, precisely so both tiers read the same number:
   * backdrop tone adaptation moves the material onto this colour, and two tiers
   * moving onto different colours is a coherence failure rather than a rounding
   * difference.
   */
  readonly backdropTone?: readonly [number, number, number];
  /**
   * The same backdrop's ENCODED-space tone level (W9): the mean taken in sRGB
   * space, decoded once — the reading the reference's tone response tracks,
   * feeding the collapse band's argument and the response curve, where
   * `backdropTone` itself is the LINEAR mean the collapse converges onto.
   * Absent exactly where `backdropTone` is.
   */
  readonly backdropToneLevel?: number;
  /**
   * The same backdrop's LINEAR-space mean luminance — the denominator of the
   * W9 correction ratio. A per-pixel consumer whose samples average linearly
   * (the GPU tier's blurred chain) multiplies its input by
   * `backdropToneLevel / backdropToneLinearLuminance` so the input's
   * spatial mean matches the encoded-space model exactly (claims §5.31).
   * Absent exactly where `backdropTone` is.
   */
  readonly backdropToneLinearLuminance?: number;
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
  /**
   * Join this root's frame loop. Returns the unsubscribe.
   *
   * The root already owns a cadence — five scene phases per frame, driven by rAF
   * when `autoStart` is on and by `runFrame` when it is not. Before this seam
   * existed, a binding that needed per-frame work of its own (advance a spring,
   * re-read a value the scene does not push) had no way to join it and ran a
   * *second* `requestAnimationFrame` loop beside the first. That is what
   * `vitrea-react`'s ticker did, and what every other adapter would have copied:
   * two loops, two wake-ups per frame, and an ordering between them that nothing
   * declares.
   *
   * Listeners run **after** the frame, in subscription order, so what they
   * observe is the frame's settled result rather than a half-run scene. `deltaMs`
   * is the gap since this root's previous frame and is `0` on the first one; a
   * caller that integrates motion should cap it rather than trust it, because a
   * backgrounded tab delivers an arbitrarily large first step on return.
   *
   * A listener that throws is reported as `frame-listener-failed` and
   * unsubscribed — one adapter's bad frame must not stop the material from
   * drawing, and a listener that throws once throws every frame.
   */
  subscribe(listener: GlassFrameListener): () => void;
  start(): void;
  stop(): void;
  destroy(): void;
}

/**
 * A per-frame callback registered through `GlassRoot.subscribe`.
 *
 * Deliberately *not* handed the `FrameReport`: the report is the scheduler's
 * account of its own phases, and a listener that read it would be coupled to
 * core's phase model rather than to the passage of time. Everything else a
 * listener needs is already reachable from the root it subscribed to.
 */
export type GlassFrameListener = (frame: GlassFrameTick) => void;

export interface GlassFrameTick {
  /** The frame's ordinal on this root, from 1. */
  readonly id: number;
  /** The timestamp this frame ran at, in the units the driver supplies. */
  readonly timeMs: number;
  /** Elapsed since this root's previous frame; `0` on the first. */
  readonly deltaMs: number;
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

/** A thrown value, said out loud. Anything can be thrown; only `Error` explains itself. */
const describeError = (error: unknown): string =>
  error instanceof Error ? `${error.name}: ${error.message}` : String(error);

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

  /**
   * A group's own proxy-audit verdict. `pass` until layer 2 has run for it, for
   * the same reason the first frame presumes it: refusing to render on an audit
   * that could not run would demote every group at startup.
   *
   * Declared here rather than beside `stateFor` because `setProbe` composes with
   * it, and `setProbe` runs from the WebGPU lifecycle's own callbacks.
   */
  /**
   * X8 rider 3, said out loud at the boundary that accepted it.
   *
   * `CornerRadii` is a Vec4 all the way down — the channel vector carries four,
   * the CSS tier writes four through `border-radius`, the proxy's mask path
   * draws four — and v1's *corner algebra* is mirror-symmetric by construction,
   * built on `|x|, |y|` with one corner reach and one coefficient set. So four
   * different radii are accepted by every layer and honoured by only some of
   * them: the CSS tier draws what the app asked for, and the GPU tier resolves
   * the shape against `radii[0]`.
   *
   * `@vitrea/geometry` refuses this already, and its refusal is deliberate and
   * well argued — but it fires per frame, from inside the renderer, on a
   * `ShapeChannels` that no longer knows which `registerHost` call produced it,
   * and only on the tier that happens to be drawing. Naming it here costs one
   * comparison per registration and puts the finding next to the declaration.
   *
   * A warning, not a throw. The surface draws either way, and taking a page down
   * over a corner would be the wrong trade for a limit the roadmap intends to
   * lift.
   */
  const reportNonUniformRadii = (
    nodeId: string,
    radii: readonly [number, number, number, number],
  ): void => {
    const spread = Math.max(...radii) - Math.min(...radii);
    if (spread <= 1e-9) return;

    platformDiagnostics.report({
      code: "non-uniform-radii",
      severity: "warning",
      subjects: [nodeId],
      message: `Host "${nodeId}" declared four different corner radii ([${radii.join(", ")}]), and v1 renders them differently on each tier: the CSS tier draws all four through border-radius, and the WebGPU tier resolves the shape against ${String(radii[0])} on every corner, because v1's corner algebra is mirror-symmetric by construction (X8 rider 3). Give the surface one radius until per-corner radii land, or accept that the two tiers will not agree on this surface.`,
    });
  };

  const verdictFor = (groupId: string): ProbeVerdict =>
    probeReports.get(groupId)?.verdict ?? "pass";

  /**
   * Publish one group's own probe into the scene: the scene-wide facts, narrowed
   * by that group's proxy-audit verdict (Decision Log #23(c)).
   *
   * Re-published rather than merged in core, because the group's probe is a
   * *derivative* of the scene-wide one: when a device is lost or WebGPU settles,
   * every group's override has to be rebuilt from the new scene-wide answer, or
   * a group that failed its audit once would keep answering with a stale
   * `webgpu` availability forever. That is what `setProbe` below does, and it is
   * why the override replaces rather than merges — one place composes, and it is
   * here.
   */
  const publishGroupProbe = (groupId: string): void => {
    if (scene.glassGroup(groupId) === undefined) return;
    scene.setPlatformProbe(foldProbeVerdict(probe, verdictFor(groupId)), groupId);
  };

  const setProbe = (next: Partial<PlatformProbe>): void => {
    probe = { ...probe, ...next };
    scene.setPlatformProbe(probe);
    // Every group's override is composed from the scene-wide probe, so a change
    // to it invalidates all of them.
    for (const groupId of probeReports.keys()) publishGroupProbe(groupId);
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
  /**
   * The author tint's shade law (W10), from the same profile — what turns a
   * seed into Apple's "range of tones mapped to content brightness underneath".
   * Rebuilt by `setMaterialProfile` alongside the rest, so a calibrated shade
   * lands as a data change and moves both tiers at once.
   */
  let tintShade = resolvedTintShade(options.materialProfile);
  /**
   * The profile's size law (W2), held for the same reason as `policyFold`: the
   * constants multiply a surface's span rather than being numbers either tier's
   * optics can carry, and both the CSS declarations and the group's sampling
   * floor need them from the *same* profile the renderer is drawing with.
   */
  let sizeConstants = sourceSize(options.materialProfile);
  /**
   * The outer shadow's constants (W8), from the same profile and held for the
   * same reason: both tiers cast the one shadow, so a calibrated one has to reach
   * this tier's `box-shadow` and the renderer's field rect from a single document.
   */
  let outerShadowConstants = sourceOuterShadow(options.materialProfile);
  /**
   * The backdrop tone adaptation's curve (W7), from the same profile. The GPU
   * tier evaluates it per pixel; this tier evaluates it once per surface against
   * whatever it knows of the backdrop — see `backdropTone` below.
   */
  let backdropToneConstants = resolvedBackdropTone(options.materialProfile);
  /**
   * The backdrop tone response's anchors (W9), from the same profile — the law
   * that owns the interior mean, where the collapse constants above own
   * texture. See the renderer's `MaterialProfile.backdropToneAnchorX`.
   */
  let backdropToneResponse = resolvedBackdropToneResponse(options.materialProfile);
  /**
   * What this tier knows about each backdrop source's own colour, in linear
   * light — the input the adaptation cannot get any other way here.
   *
   * Held on the root rather than in the bridge because a CSS-tier root has no
   * bridge and needs the answer just the same: `setBackdropTexture` is how an app
   * hands over its backdrop's pixels, and until now a root without a renderer
   * dropped them. Re-read whenever the app says the content changed, which is the
   * same ledger the GPU tier rebuilds its pyramid from.
   */
  const suppliedTextures = new Map<string, GlassBackdropTexture>();
  const backdropTones = new Map<
    string,
    { readonly epoch: number; readonly atMs: number; readonly sample: BackdropToneSample | undefined }
  >();
  /**
   * The source's tone, re-read when its content can have changed and no more
   * often than `BACKDROP_TONE_CADENCE_MS`.
   *
   * **"Can have changed" is a property of the source kind, not of the ledger**,
   * and that distinction is a defect this got wrong once. An `image` source is
   * one decode: it changes only when the app hands over a different texture,
   * which clears this cache directly, so the dirty epoch is a complete account of
   * it. A `canvas` or `video` source is *content the app is drawing*, and on a
   * CSS-tier root nothing marks its epoch at all — there is no pyramid to rebuild
   * — so an epoch-only rule read the tone once at first paint and froze it there
   * forever. Measured on the demo: three surfaces stuck on the tone of a section
   * the reader had already scrolled past.
   *
   * So a live source is re-read on the cadence regardless of its epoch, and that
   * cadence is what keeps it affordable: a per-frame `getImageData` of a
   * page-sized backdrop would be a real cost for a number that moves slowly, and
   * the GPU tier's own analysis readback makes the same judgement about the same
   * quantity.
   *
   * The first read is never delayed either way: a surface must not paint
   * unadapted and change its mind a quarter of a second later.
   */
  const backdropToneFor = (sourceId: string): BackdropToneSample | undefined => {
    const texture = suppliedTextures.get(sourceId);
    if (texture === undefined) return undefined;
    const epoch = scene.backdropSource(sourceId)?.dirtyEpoch ?? 0;
    const held = backdropTones.get(sourceId);
    const now = view.performance?.now() ?? 0;
    if (held !== undefined) {
      const stale = texture.kind === "image" ? held.epoch !== epoch : true;
      if (!stale || now - held.atMs < BACKDROP_TONE_CADENCE_MS) return held.sample;
    }
    const sample = sampleBackdropTone(texture);
    backdropTones.set(sourceId, { epoch, atMs: now, sample });
    return sample;
  };
  /** One CSS-colour parser per root, memoised by string. See `tint.ts`. */
  const parseTint = createTintParser(view.document);

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
    // Into the scene, so `resolve()` and `capabilities()` give one answer.
    publishGroupProbe(groupId);

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

    /*
     * The group's own probe, off the scene record where `auditGroup` published
     * it — not folded here a second time. Before core carried a per-group probe
     * this function did the fold itself, which meant the scene's `resolve()` and
     * this getter could disagree about the same group. They cannot now: one
     * value, composed in one place (`publishGroupProbe`).
     *
     * The fallback is the scene-wide probe, for a group that has been registered
     * but not yet audited.
     */
    const platform = record.platform ?? probe;

    return resolveGlassGroupState(
      groupCapabilityInputs(
        source.descriptor.kind === "texture"
          ? {
              configuredSource: "texture",
              platform,
              // Whether pixels were ever handed over is a platform-side fact —
              // core holds a declaration, the bridge holds the canvas — folded
              // into the per-source probe the same way this group's own proxy
              // verdict is folded into `backdropProxyConformance` (Decision Log
              // #21a). Only asked where there is a bridge to ask: on a CSS-tier
              // root nothing samples a texture at all, and "no pixels supplied"
              // would be naming a loss the tier never had.
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
            }
          : { configuredSource: "dom", platform, governor, hint },
      ),
    );
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
    if (!external) return;
    staleProbes = "all";
    /*
     * The geometry clip chain goes stale on exactly the same events (Decision
     * Log #41(k)): an app style change can add or remove an `overflow` on an
     * ancestor, and which ancestors clip is cached per host so that a scroll
     * costs rect reads rather than style reads. Nothing else observes it — a
     * `ResizeObserver` does not fire for an `overflow` change, and `MutationObserver`
     * is already here for the probe's identical problem.
     *
     * Only the *cache* is dropped. Nothing is marked dirty by this, so a page
     * whose app CSS churns does not start re-measuring every host; the chain is
     * re-walked the next time a host is measured for a reason of its own.
     */
    geometry.invalidateClipChains();
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

      /*
       * What this group's backdrop is, for backdrop tone adaptation (W7) —
       * resolved ONCE, here, and handed to both tiers.
       *
       * Once and per group is the point. The two tiers have to adapt onto the
       * same colour by the same amount or they draw different pictures wherever
       * the backdrop has structure, and the coherence bound is what that costs
       * (measured at an interior level ratio of 79 when the GPU tier read the
       * backdrop per pixel and this tier read one average).
       *
       * The order is the app's statements in the order they deserve: X6's declared
       * hint first, which is core's own rule for `resolveBackdropHint`; then the
       * pixels the app handed over for the backdrop source; then nothing, which
       * means neither tier adapts. Nothing is not a fallback level — a guessed
       * backdrop would dissolve an untinted surface into a page it never measured.
       *
       * A hint carries a level and not a colour, so the tone it stands for is
       * achromatic; only the sampled path can move the material's hue.
       */
      const declaredHint = resolved.hint.availability === "author-hint" ? resolved.hint.hint : undefined;
      const declaredLuminance =
        declaredHint === undefined
          ? undefined
          : (declaredHint.luminance ??
            (declaredHint.tone === "dark" || declaredHint.tone === "light"
              ? cssMapping.toneLuminance[declaredHint.tone]
              : undefined));
      const backdropTone: BackdropToneSample | undefined =
        declaredLuminance === undefined
          ? backdropToneFor(groupRecord.descriptor.backdropSourceId)
          : {
              rgb: [declaredLuminance, declaredLuminance, declaredLuminance],
              luminance: declaredLuminance,
              // A declared hint carries no structure to correct for: the tone
              // input IS the declaration, so the linear mean equals it and the
              // W9 correction ratio resolves to 1.
              linearLuminance: declaredLuminance,
            };

      /*
       * The group's sampling geometry, with the **default** derived from the
       * blur this group is actually drawing with rather than from a constant
       * (see `resolveSamplingGeometry`). core cannot do this: σ lives in the
       * material, which is this package's, and core's own 24 is 3σ at the
       * nominal σ of 8 — right until an accessibility preference moves σ. An
       * authored value is passed straight through, warning and all.
       *
       * Taken over the group's **largest** member since the size law (W2): σ is
       * now per surface, and a floor derived from the nominal would starve a
       * platter's proxy by exactly the scattering gain — the widest kernel any
       * member samples with is what S1's 3σ rule is about. A group with nothing
       * measured yet has no span to take, and falls back to the nominal σ.
       */
      const groupSpanPx = measured.reduce(
        (widest, entry) => Math.max(widest, Math.min(entry.bounds.width, entry.bounds.height)),
        0,
      );
      const sampling = resolveSamplingGeometry({
        samplingPadding: groupRecord.descriptor.samplingPadding,
        mergeDistance: groupRecord.descriptor.mergeDistance,
        blurRadius: sizeScatterSigmaAt(
          optics.blurRadius,
          sizeThicknessUnderPolicy(groupSpanPx, accessibility.material, sizeConstants),
          sizeConstants,
        ),
      });

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
        samplingPadding: sampling.samplingPadding,
        mergeDistance: sampling.mergeDistance,
        declaredMergeDistance: groupRecord.descriptor.mergeDistance,
        blurRadius: optics.blurRadius,
        ...(backdropTone === undefined
          ? {}
          : {
              backdropTone: backdropTone.rgb,
              backdropToneLevel: backdropTone.luminance,
              backdropToneLinearLuminance: backdropTone.linearLuminance,
            }),
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
            members: inPlane.map((entry) => {
              // The clip chain the read phase measured alongside the box
              // (Decision Log #41(k)). A proxy sits in the plane layer, not
              // inside whatever is cropping the host, so nothing narrows it for
              // us — the geometry has to carry the crop or the glass paints
              // outside the scroller that was supposed to contain it.
              const clip = scene.glassNode(entry.record.nodeId)?.clip;
              return {
                nodeId: entry.record.nodeId,
                bounds: entry.bounds,
                radii: [
                  entry.record.radii[0],
                  entry.record.radii[1],
                  entry.record.radii[2],
                  entry.record.radii[3],
                ] as const,
                ...(clip === undefined ? {} : { clip }),
              };
            }),
            samplingPadding: sampling.samplingPadding,
            mergeDistance: sampling.mergeDistance,
            blurRadius: optics.blurRadius,
            saturation: optics.saturation,
          });
        }
      }

      for (const { record, bounds } of measured) {
        const nodeRecord = scene.glassNode(record.nodeId);
        // `null` clears an inherited tint and `undefined` inherits, so the two
        // cannot be collapsed with `??` — the same distinction core's own
        // resolution makes.
        const declaredTint =
          nodeRecord?.descriptor.tint === undefined
            ? groupRecord.descriptor.material?.tint
            : nodeRecord.descriptor.tint;
        const material: ResolvedMaterial = resolveMaterial({
          variant: nodeRecord?.descriptor.variant ?? variant,
          ...(groupRecord.descriptor.material?.dimming === undefined
            ? {}
            : { dimming: groupRecord.descriptor.material.dimming }),
          ...(declaredTint === undefined || declaredTint === null ? {} : { tint: declaredTint }),
          nodeId: record.nodeId,
          diagnostics: coreDiagnostics,
        });
        const foreground = resolution.nodes.find((node) => node.nodeId === record.nodeId)?.foreground;

        // X6's hint reaches both tiers here: the node's resolved mode plus the
        // group's resolved hint tone, both already computed by core — this
        // consumes that resolution rather than repeating it. Resolved before the
        // material because a tinted surface's tone is read against the backdrop
        // the hint describes.
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

        /*
         * The author tint, folded into this surface's material.
         *
         * The GPU tier evaluates the tone per pixel against the backdrop it is
         * already sampling. Nothing on this side can: a CSS declaration is one
         * colour, so the tone is taken at one backdrop level — the hinted one
         * where the app declared it, the mapping's reference level otherwise.
         * That is the same single-level approximation `cssTintAlpha` already
         * makes for the untinted material, on the same reasoning, and it is why
         * the tier-coherence claim is worded around a declared backdrop rather
         * than a range.
         */
        const toneBackdrop =
          hintedBackdropLuminance(hint, cssMapping) ?? cssMapping.referenceBackdropLuminance;
        const toneAdaptation = tintToneAdaptation(accessibility.material.ambientTint, tintShade);
        const seed = material.tint === undefined ? undefined : linearTint(material.tint);

        /*
         * Backdrop tone adaptation (W7) — step two of the composition contract,
         * between the profile's neutral and the author's tint. The backdrop it
         * adapts onto was resolved once for the whole group, above, and the GPU
         * tier is handed the same value: one tone, one amount, two tiers.
         *
         * The size gate is per surface, from the host's own measured border box,
         * and it takes the UNFOLDED thickness — the gate is geometric, and the
         * policy has its own fold on the strength beside it.
         */
        const surfaceThickness = sizeThickness(
          Math.min(bounds.width, bounds.height),
          sizeConstants,
        );
        const backdropTonePolicyStrength = backdropToneUnderPolicy(
          accessibility.material,
          tintShade,
          sizeConstants.refractionScale,
        );
        const backdropAdaptation =
          backdropTone === undefined
            ? 0
            : backdropToneAdaptation(
                backdropTone.luminance,
                surfaceThickness,
                backdropToneConstants,
              ) * backdropTonePolicyStrength;

        /*
         * The response solve (W9) runs whenever a backdrop tone was measured —
         * it is not gated on the collapse being non-zero, because the law it
         * lands (the interior mean tracking the backdrop's encoded mean) is
         * exactly the behaviour the collapse's narrow band no longer carries.
         */
        const respondedSource =
          backdropTone === undefined
            ? gpuOptics[variant]
            : toneRespondedSourceOptics(
                gpuOptics[variant],
                backdropTone,
                surfaceThickness,
                backdropAdaptation,
                // The response law rides only the UN-DEGRADED regime — the
                // renderer's own gate, mirrored: its anchors are
                // standard-reference measurements, and a policy fold on the
                // tone axis means a reference this law was never measured on.
                (backdropTonePolicyStrength >= 0.999 ? 1 : 0) *
                  Math.min(1, Math.max(0, backdropToneConstants.max)),
                backdropToneResponse,
              );

        /*
         * The author tint (W10) composites LAST, over the converted material:
         * an opaque layer of the seed at its shade, at the author's opacity,
         * folded into this tier's one `rgba()` in the encoded space it actually
         * composites in. The shade reads the material's luminance at one level
         * per source — the measured backdrop where the host sampled one, the
         * hint or the mapping's reference otherwise — and its grip is the
         * regime's, the profile's provenance gate's, and `(1 − collapse)`: a
         * collapsed material is a dark body, and the reference paints the pure
         * seed on one.
         */
        const adaptedSource = adaptedSourceOptics(
          respondedSource,
          backdropTone?.rgb as LinearRgb | undefined,
          backdropAdaptation,
        );
        // The material the shade is read off is the one the tier draws: the
        // occlusion regime's lift is part of it (the increased-contrast
        // reference is at u ≈ 0.98 and shades to 0.99, measured), so the tint
        // composites AFTER the policy fold, on both tiers.
        const policySource: MaterialSourceOptics = {
          ...adaptedSource,
          tintAlpha: occlusionAlphaUnderPolicy(
            adaptedSource.tintAlpha,
            accessibility.material.occlusion,
            policyFold.increasedOcclusionLift,
          ),
        };
        const tintBackdrop = backdropTone?.linearLuminance ?? toneBackdrop;
        const tintGrip = toneAdaptation * tintShade.strength * (1 - backdropAdaptation);
        const nodeBaseOptics =
          backdropAdaptation <= 0 && backdropTone === undefined
            ? baseOptics
            : cssOpticsFromSource(baseOptics, adaptedSource, cssMapping);
        const nodeOptics =
          seed === undefined && backdropAdaptation <= 0 && backdropTone === undefined
            ? optics
            : tintedCssOptics(
                opticsUnderPolicy(nodeBaseOptics, accessibility.material, policyFold),
                policySource,
                seed,
                tintBackdrop,
                tintGrip,
                tintShade,
              );

        const input: GlassNodeRenderInput = {
          nodeId: record.nodeId,
          groupId,
          plane: record.plane,
          order: record.order,
          bounds,
          shapeFamily: record.shapeFamily,
          radii: record.radii,
          smoothing: record.smoothing,
          /*
           * Off the scene descriptor, not off the host record — these two are
           * scene-model fields now (Decision Log #23(c)) and mirroring them here
           * would be a second copy that could disagree with core's. Spread
           * conditionally so an absent field stays absent: the renderer's own
           * default for `reference` is `"apple-continuous"`, and writing an
           * explicit `undefined` would be a different thing from not saying.
           */
          ...(nodeRecord?.descriptor.reference === undefined
            ? {}
            : { reference: nodeRecord.descriptor.reference }),
          ...(nodeRecord?.descriptor.concentricOf === undefined
            ? {}
            : { concentricOf: nodeRecord.descriptor.concentricOf }),
          thickness: record.thickness,
          // An inline-style read: the same declaration block a binding wrote
          // into, never the cascade. It forces no style recalculation, so the
          // zero-read steady state survives it (see `channels.ts`).
          channels: readHostChannels(record.host, bounds),
          material,
          foreground: foreground ?? { adaptation: { mode: "fixed" } },
          optics: nodeOptics,
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

        // The CSS tier paints if and only if it is the active renderer.
        const declarations = cssTierDeclarations({
          radii: record.radii,
          optics: nodeBaseOptics,
          ...(material.tint === undefined ? {} : { tint: material.tint }),
          mapping: cssMapping,
          policyFold,
          policy: accessibility,
          foreground: hint,
          // The backdrop this surface is over, declared or measured — the ink is
          // decided against the material the surface actually draws, and this axis
          // can move that material a long way on a tone nobody declared (W7).
          ...(backdropTone === undefined ? {} : { backdropLuminance: backdropTone.luminance }),
          // The size law's input, from the host's own measured border box — the
          // same shorter-extent span the renderer resolves per surface (W2).
          spanPx: Math.min(bounds.width, bounds.height),
          size: sizeConstants,
          outerShadow: outerShadowConstants,
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
          /*
           * The backdrop the ink is decided against: a *measured* tone counts
           * here exactly as a declared one does (W7). Before this the ink asked
           * only `hintedBackdropLuminance`, which answers for an author hint and
           * nothing else — so a group whose backdrop vitrea had actually measured,
           * and whose material had just adapted onto it, still fell through to the
           * `light-dark()` default. That is the wrong direction to be wrong in:
           * the adaptation can take a surface from near-white to near-black while
           * the ink stays where the colour scheme put it, which is the K4/#32(b)
           * failure arriving through a third door.
           */
          const measuredBackdrop = backdropTone?.luminance;
          const hintedBackdrop = hintedBackdropLuminance(hint, cssMapping) ?? measuredBackdrop;
          /*
           * The material the renderer is drawing, adapted, tinted and folded: the
           * backdrop moves its neutral, the seed displaces that, and the occlusion
           * regime lifts its alpha — which is the pair the level behind the glyphs
           * is a function of. The ink therefore follows both an author tint and
           * the backdrop adaptation automatically, rather than being decided
           * against a material the tier stopped drawing.
           */
          const gpuMaterial = tintedSourceOptics(policySource, seed, tintBackdrop, tintGrip, tintShade);
          // Same rule as the CSS tier's: a declared tint can decide the ink with
          // no hint at all, wherever the level's whole range lands on one side of
          // the crossover. See `boundedForegroundLevel`.
          const level =
            hintedBackdrop !== undefined
              ? gpuTierForegroundLevel(gpuMaterial, hintedBackdrop)
              : seed === undefined
                ? undefined
                : boundedForegroundLevel(
                    gpuTierForegroundBounds(gpuMaterial),
                    cssMapping.foregroundCrossover,
                  );
          const ink = foregroundDeclarations({
            policy: accessibility,
            mapping: cssMapping,
            ...(level === undefined ? {} : { level }),
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

  const frameListeners = new Set<GlassFrameListener>();
  let lastFrameTimeMs: number | undefined;

  const runFrame = (timeMs?: number): FrameReport => {
    frameId += 1;
    const at = timeMs ?? 0;
    const report = scheduler.runFrame({ id: frameId, timeMs: at });

    // After the frame, so a listener observes a settled scene. Snapshotted
    // because a listener may unsubscribe itself or another one mid-notify.
    const deltaMs = lastFrameTimeMs === undefined ? 0 : at - lastFrameTimeMs;
    lastFrameTimeMs = at;
    const tick: GlassFrameTick = { id: frameId, timeMs: at, deltaMs };
    for (const listener of [...frameListeners]) {
      if (!frameListeners.has(listener)) continue;
      try {
        listener(tick);
      } catch (error) {
        /*
         * Drop it rather than let it stop the loop. A listener that throws on
         * one frame throws on every frame, so keeping it subscribed turns one
         * adapter's bug into an unbounded diagnostic storm and — where the
         * caller drives frames by hand rather than from rAF — into a thrown
         * `runFrame`, which stops the material drawing entirely.
         */
        frameListeners.delete(listener);
        platformDiagnostics.report({
          code: "frame-listener-failed",
          severity: "error",
          subjects: [`frame-${String(frameId)}`],
          message:
            `A frame listener threw and was unsubscribed: ${describeError(error)}. ` +
            "Frame listeners run after the scene has settled and must not throw — " +
            "catch inside the listener and report through your own channel.",
        });
      }
    }

    return report;
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
      /*
       * The other order (#41(k)). `setBackdropTexture` marks the source dirty so
       * the next frame imports it, but only where the scene already knows the
       * source — before this, a texture handed over first was held by the bridge
       * and then never marked at all, so the pixels sat unimported until
       * something *else* happened to dirty the source. On a one-shot image
       * source nothing else ever does.
       *
       * Every path in this repo declares first, which is exactly why this went
       * unnoticed; both READMEs promise the opposite ("the id joins the two
       * halves; the order does not matter"), and a cached `<img>` whose `onLoad`
       * fires before the group's effect runs is the ordinary way an app gets
       * there. Marked through the same call `setBackdropTexture` uses, so the
       * two orders converge on one epoch bump rather than on two mechanisms.
       */
      if (bridge?.hasBackdropTexture(descriptor.id) === true) {
        scene.markBackdropSourceDirty(descriptor.id);
      }
    },

    setBackdropTexture(sourceId, texture) {
      bridge?.setBackdropTexture(sourceId, texture);
      // Held on this side too (W7). The bridge is the GPU tier's, and a CSS-tier
      // root has none — but the backdrop's own tone is what the CSS tier's
      // adaptation is missing, and these are exactly the pixels that answer it.
      if (texture === undefined) {
        suppliedTextures.delete(sourceId);
        backdropTones.delete(sourceId);
      } else {
        suppliedTextures.set(sourceId, texture);
        backdropTones.delete(sourceId);
      }
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

      if (devMode) reportNonUniformRadii(nodeId, shape.radii);

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
        ...(hostOptions.reference === undefined ? {} : { reference: hostOptions.reference }),
        // Refused here on an unknown parent, a cross-group parent or a cycle —
        // core's own checks, on the call that can be blamed for it.
        ...(hostOptions.concentricOf === undefined
          ? {}
          : { concentricOf: hostOptions.concentricOf }),
        ...(hostOptions.variant === undefined ? {} : { variant: hostOptions.variant }),
        // Parsed here, once, rather than per frame: the value is a CSS colour
        // string and the browser is the parser, so the seam between "what the
        // author wrote" and "what core carries" is registration.
        ...(hostOptions.tint === undefined
          ? {}
          : {
              tint:
                resolveTintDeclaration(
                  hostOptions.tint,
                  parseTint,
                  nodeId,
                  platformDiagnostics,
                ) ?? null,
            }),
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
          // Checked on patch as well as on registration: a capsule's radius is
          // recomputed every time its box changes, and a morph writes radii on
          // every frame it runs for.
          if (devMode && patch.radii !== undefined) reportNonUniformRadii(nodeId, record.radii);
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
            // `in patch` rather than `!== undefined`, like the overrides below
            // it: a key present with `undefined` clears, an absent key keeps —
            // core's own patch rule, and the only way to say "back to the
            // default fit" or "no longer concentric".
            ...("reference" in patch ? { reference: patch.reference } : {}),
            ...("concentricOf" in patch ? { concentricOf: patch.concentricOf } : {}),
            ...("variant" in patch ? { variant: patch.variant } : {}),
            ...("tint" in patch
              ? {
                  tint: resolveTintDeclaration(
                    patch.tint,
                    parseTint,
                    nodeId,
                    platformDiagnostics,
                  ),
                }
              : {}),
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
      tintShade = resolvedTintShade(profile);
      sizeConstants = sourceSize(profile);
      outerShadowConstants = sourceOuterShadow(profile);
      backdropToneConstants = resolvedBackdropTone(profile);
      backdropToneResponse = resolvedBackdropToneResponse(profile);
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

    subscribe(listener) {
      frameListeners.add(listener);
      return () => {
        frameListeners.delete(listener);
      };
    },

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
      frameListeners.clear();
    },
  };

  if (options.autoStart ?? true) root.start();

  return root;
}
