/**
 * `createGlassRoot` — the one object an app (or `@vitrea/react`) holds.
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
  DEFAULT_GROUP_SAMPLING,
  resolveMaterial,
  type AccessibilityOverrides,
  type BackdropSourceDescriptor,
  type FrameInfo,
  type FrameReport,
  type GlassGroupDescriptor,
  type GlassGroupState,
  type GlassPlane,
  type GlassScene,
  type PlatformProbe,
  type Rect,
  type RefractionQuality,
  type ResolvedAccessibilityPolicy,
  type ResolvedForegroundAdaptation,
  type ResolvedMaterial,
} from "@vitrea/core";

import { createBackdropProxyManager, type ProxyRequest } from "./backdrop-proxy";
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
import { createLayoutReadMeter, type LayoutReadMeter } from "./measure";
import {
  browserMediaMatcher,
  observeAccessibilityPreferences,
  type AccessibilityFeed,
  type MediaMatcher,
} from "./media-policy";
import { MATERIAL_OPTICS, opticsUnderPolicy, type MaterialOptics } from "./optics";
import { createGlassLayerManager, type GlassLayerManager, type PlaneLayers } from "./planes";
import {
  describeProbeFailure,
  probeGroup,
  probePlatform,
  type GroupProbeReport,
  type PlatformProbeReport,
} from "./probe";
import { accessibilityRefractionCap, effectiveRefraction } from "./refraction";
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
  readonly radii: readonly [number, number, number, number];
  readonly smoothing: number;
  readonly thickness: number;
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
  readonly samplingPadding: number;
  readonly mergeDistance: number;
  readonly blurRadius: number;
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
  readonly accessibility: ResolvedAccessibilityPolicy;
  readonly webgpu: WebGPUStatus | undefined;
  /** Resolves once the WebGPU lifecycle has settled; immediately on a CSS root. */
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
  radii: readonly [number, number, number, number];
  smoothing: number;
  thickness: number;
  ownedTransform: string | undefined;
  readonly onPlaneChange: ((plane: GlassPlane) => void) | undefined;
  /** Whether the CSS tier currently owns this host's appearance. */
  cssStyled: boolean;
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
    // A root that wires no GPU has no WebGPU in play, and says so rather than
    // claiming a capability nothing is going to use.
    webgpu: false,
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

  const webgpu: WebGPULifecycle | undefined = wantsWebGPU
    ? createWebGPULifecycle({
        ...(options.webgpu?.device === undefined ? {} : { device: options.webgpu.device }),
        ...(options.webgpu?.powerPreference === undefined
          ? {}
          : { powerPreference: options.webgpu.powerPreference }),
        onStatusChange: (status) => {
          setProbe({ webgpu: status.available, deviceHealth: status.deviceHealth });
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

  const readyPromise: Promise<void> =
    webgpu === undefined ? Promise.resolve() : webgpu.start().then(() => undefined);

  /**
   * Layer 2 for one group. Proxies only exist once a group has measured members,
   * so before the first read the group is presumed to pass: refusing to render
   * on the strength of an audit that could not run yet would demote every group
   * for one frame at startup.
   */
  const auditGroup = (groupId: string): GroupProbeReport => {
    const proxy = proxies.proxyFor(groupId);
    if (proxy === undefined) {
      return { groupId, verdict: "pass", breaks: [], reach: platformProbe.reach };
    }
    const report = probeGroup({ groupId, proxy }, platformProbe, meter);
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
  const styleObserver = new MutationObserver(() => {
    for (const groupId of probeReports.keys()) auditGroup(groupId);
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

    for (const resolved of resolution.groups) {
      const groupId = resolved.groupId;
      const groupRecord = scene.glassGroup(groupId);
      if (groupRecord === undefined) continue;

      const variant = groupRecord.descriptor.material?.variant ?? "regular";
      const baseOptics = MATERIAL_OPTICS[variant];
      const optics = opticsUnderPolicy(baseOptics, accessibility.material);
      const state = stateFor(groupId) ?? resolved.state;

      const members = [...hosts.values()].filter((record) => record.groupId === groupId);
      const measured = members
        .map((record) => ({ record, bounds: scene.glassNode(record.nodeId)?.bounds }))
        .filter(
          (entry): entry is { record: HostRecord; bounds: Rect } => entry.bounds !== undefined,
        );

      groupInputs.push({
        groupId,
        state,
        probe: probeReports.get(groupId) ?? {
          groupId,
          verdict: "pass",
          breaks: [],
          reach: platformProbe.reach,
        },
        samplingPadding: resolved.sampling.samplingPadding,
        mergeDistance: resolved.sampling.mergeDistance,
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
          radii: record.radii,
          smoothing: record.smoothing,
          thickness: record.thickness,
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

        // The CSS tier paints if and only if it is the active renderer.
        const declarations = cssTierDeclarations({
          radii: record.radii,
          optics: baseOptics,
          policy: accessibility,
        });
        if (state.activeRenderer === "css") {
          for (const [property, value] of Object.entries(declarations)) {
            record.host.style.setProperty(property, value);
          }
          record.cssStyled = true;
        } else if (record.cssStyled) {
          clearDeclarations(record.host, declarations);
          record.cssStyled = false;
        }
      }
    }

    proxies.sync(proxyRequests, {
      devicePixelRatio: viewport?.devicePixelRatio ?? 1,
      maxProxyAreaDevicePx: platformProbe.conformance.maxProxyAreaDevicePx,
    });

    // Auditing after the proxies exist is the only order that works: layer 2
    // walks the proxy's own ancestor chain, so there is nothing to walk until
    // the element is in the tree.
    for (const request of proxyRequests) auditGroup(request.groupId);

    renderInput = {
      frame,
      accessibility,
      planes: layers.planes.map((planeLayers) => ({
        plane: planeLayers.plane,
        layers: planeLayers,
        nodes: (nodesByPlane.get(planeLayers.plane) ?? []).sort((a, b) => a.order - b.order),
      })),
      groups: groupInputs,
      device: webgpu?.status.device,
    };
  };

  scheduler.addParticipant({
    id: "vitrea.platform-web",
    read: () => geometry.read(),
    write: (context) => {
      if (context.resolution !== undefined) write(context.frame, context.resolution);
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
        radii: shape.radii,
        smoothing: shape.smoothing,
        thickness: shape.thickness,
        ownedTransform: undefined,
        onPlaneChange: hostOptions.onPlaneChange,
        cssStyled: false,
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
          if (record.onPlaneChange === undefined) {
            layers.plane(destination).hostLayer.append(record.host);
          } else {
            record.onPlaneChange(destination);
          }
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
          if (record.cssStyled) {
            clearDeclarations(
              record.host,
              cssTierDeclarations({
                radii: record.radii,
                optics: MATERIAL_OPTICS.regular,
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
      for (const groupId of probeReports.keys()) auditGroup(groupId);
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
      webgpu?.destroy();
      layers.destroy();
      hosts.clear();
      probeReports.clear();
    },
  };

  if (options.autoStart ?? true) root.start();

  return root;
}

export const DEFAULT_SAMPLING = DEFAULT_GROUP_SAMPLING;
