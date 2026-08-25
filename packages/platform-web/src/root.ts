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
} from "vitrea";

import { createBackdropProxyManager, type ProxyRequest } from "./backdrop-proxy";
import { readHostChannels, type SurfaceChannelValues } from "./channels";
import { cssTierDeclarations, type StyleDeclarations } from "./css-tier";
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
  opticsUnderPolicy,
  type CssTierMapping,
  type MaterialOptics,
} from "./optics";
import { createGlassLayerManager, type GlassLayerManager, type PlaneLayers } from "./planes";
import {
  describeProbeFailure,
  probeGroup,
  probePlatform,
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
  readonly webgpu?: { readonly device?: GPUDevice; readonly powerPreference?: GPUPowerPreference };
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
  /** Vitrea-owned visual transform, composed on top of `bounds`. */
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
   * is where the canvas, image or video arrives, and it is the only wiring the
   * GPU tier needs beyond `renderer: "webgpu"`. Passing `undefined` withdraws it.
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

  const wantsWebGPU = (options.renderer ?? "css") === "webgpu";

  let probe: PlatformProbe = {
    // A root that wires no GPU never asked for one — "not-requested", not
    // "unavailable". core resolves that as a choice, not a fault (X2's K1
    // amendment, Decision Log #21c); `wantsWebGPU` roots start "unavailable"
    // until `webgpu.start()` resolves.
    webgpu: wantsWebGPU ? "unavailable" : "not-requested",
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
   * Set if the renderer chunk cannot be resolved at all.
   *
   * A device with no renderer behind it draws nothing, and a group resolved onto
   * the WebGPU tier there would be reporting a capability that is painting
   * nothing. `no-webgpu` is the honest name for it — there is no GPU tier in
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

  const bridge: GlassRendererBridge | undefined = wantsWebGPU
    ? createGlassRendererBridge({
        layers,
        diagnostics: platformDiagnostics,
        ...(options.materialProfile === undefined
          ? {}
          : { materialProfile: options.materialProfile }),
        onRendererUnavailable: () => {
          rendererUnavailable = true;
          setProbe({ webgpu: "unavailable" });
        },
      })
    : undefined;

  const webgpu: WebGPULifecycle | undefined = wantsWebGPU
    ? createWebGPULifecycle({
        ...(options.webgpu?.device === undefined ? {} : { device: options.webgpu.device }),
        ...(options.webgpu?.powerPreference === undefined
          ? {}
          : { powerPreference: options.webgpu.powerPreference }),
        onStatusChange: (status) => {
          bridge?.syncDevice(status);
          // This callback only exists on a `wantsWebGPU` root, so WebGPU was
          // requested here by construction — "available" or "unavailable" is
          // the whole range, never "not-requested".
          setProbe({
            webgpu: status.available && !rendererUnavailable ? "available" : "unavailable",
            deviceHealth: status.deviceHealth,
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
  const auditGroup = (groupId: string, plane: GlassPlane): GroupProbeReport => {
    // A group demoted by this very probe has no proxy — demotion removes it —
    // so auditing only groups that *have* one would make `probe-failed`
    // unrecoverable, and every demotion reason is required to name a recovery.
    // The plane's proxy layer stands in: the walk starts at `from`'s parent, so
    // both start at the plane root and audit exactly the same chain. The proxy
    // layer is vitrea's own element and carries no trigger by construction.
    const from = proxies.proxyFor(groupId) ?? layers.plane(plane).proxyLayer;
    const report = probeGroup({ groupId, proxy: from }, platformProbe, meter);
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
          source: source.descriptor.probe,
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
    /** Every group with something measured, and the plane its proxy belongs in. */
    const auditablePlanes = new Map<string, GlassPlane>();

    for (const resolved of resolution.groups) {
      const groupId = resolved.groupId;
      const groupRecord = scene.glassGroup(groupId);
      if (groupRecord === undefined) continue;

      const variant = groupRecord.descriptor.material?.variant ?? "regular";
      const baseOptics = cssOptics[variant];
      const optics = opticsUnderPolicy(baseOptics, accessibility.material);
      const state = stateFor(groupId) ?? resolved.state;

      const members = [...hosts.values()].filter((record) => record.groupId === groupId);
      const measured = members
        .map((record) => ({ record, bounds: scene.glassNode(record.nodeId)?.bounds }))
        .filter(
          (entry): entry is { record: HostRecord; bounds: Rect } => entry.bounds !== undefined,
        );

      const firstPlane = measured[0]?.record.plane;
      if (firstPlane !== undefined) auditablePlanes.set(groupId, firstPlane);

      groupInputs.push({
        groupId,
        state,
        probe: probeReports.get(groupId) ?? {
          groupId,
          verdict: "pass",
          breaks: [],
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
        for (const plane of new Set(measured.map((entry) => entry.record.plane))) {
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
        const declarations = cssTierDeclarations({
          radii: record.radii,
          optics: baseOptics,
          policy: accessibility,
          foreground: {
            mode: (foreground ?? { adaptation: { mode: "fixed" as const } }).adaptation.mode,
            ...(resolved.hint.hint?.tone === undefined ? {} : { tone: resolved.hint.hint.tone }),
          },
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
            flushStyle(meter, record.host);
            record.cssMaterialized = true;
          }

          const serialised = JSON.stringify(declarations);
          if (record.cssApplied !== serialised) {
            for (const [property, value] of Object.entries(declarations)) {
              record.host.style.setProperty(property, value);
            }
            record.cssApplied = serialised;
          }
        } else if (record.cssApplied !== undefined) {
          clearDeclarations(record.host, declarations);
          record.cssApplied = undefined;
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
    for (const [groupId, plane] of auditablePlanes) {
      if (staleProbes === "all" || staleProbes.has(groupId)) auditGroup(groupId, plane);
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
        bridge.write(renderInput, context.consumeDirtyBackdropSources());
      }
    },
    // Drawing belongs to `render`, with the graph frozen — the same split the
    // renderer's own frame participant uses.
    render: () => bridge?.render(),
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

      const hostLayer = layers.plane(plane).hostLayer;
      if (!hostLayer.contains(hostOptions.host) && devMode) {
        platformDiagnostics.report({
          code: "host-outside-plane",
          severity: "error",
          subjects: [nodeId],
          message: `Host "${nodeId}" is not inside the "${plane}" plane's host layer, so X1's sandwich cannot order it: its glass body would paint somewhere other than behind it. Render or portal the element into root.plane("${plane}").hostLayer.`,
        });
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
          geometry.markDirty(nodeId);
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
          record.ownedTransform = transform;
          if (transform === undefined) record.host.style.removeProperty("transform");
          else record.host.style.setProperty("transform", transform);
          // Deliberately no `markDirty`: a transform does not change a border-box
          // rect, so re-reading would measure the same numbers at a cost.
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
                policy: scene.accessibilityPolicy(),
              }),
            );
          }
        },
      };

      return handle;
    },

    capabilities: (groupId) => stateFor(groupId),
    probeReport: (groupId) => probeReports.get(groupId),

    revalidateProbe() {
      for (const groupId of probeReports.keys()) {
        const plane =
          [...hosts.values()].find((record) => record.groupId === groupId)?.plane ?? "base";
        auditGroup(groupId, plane);
      }
    },

    setMaterialProfile(profile) {
      // Both tiers, from one call. The CSS side re-derives rather than being
      // told: the mapping is what knows the crossing's cost, and a caller
      // handing the CSS tier its own alpha would be re-opening K5's gap by hand.
      cssOptics = cssTierOptics(profile, cssMapping);
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
      hosts.clear();
      probeReports.clear();
    },
  };

  if (options.autoStart ?? true) root.start();

  return root;
}
