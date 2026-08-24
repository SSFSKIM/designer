/**
 * The scene model (§Core model): the three registries and everything that
 * follows from their references.
 *
 * ```
 * BackdropSource            GlassGroup                GlassNode
 * ├─ kind: texture | dom    ├─ backdropSourceId       ├─ shape family params
 * ├─ raw texture/source     ├─ morph namespace        ├─ viewport bounds, clip
 * ├─ blur pyramid           ├─ material profile       ├─ z-slot (plane + order)
 * ├─ analysis maps          ├─ adaptation policy      ├─ variant
 * ├─ dirty epoch            ├─ mergeDistance          ├─ interaction state
 * └─ resolution policy      └─ samplingPadding        └─ foreground policy
 * ```
 *
 * Core owns the *bookkeeping* half of each row. The raw texture, the blur
 * pyramid and the analysis maps are GPU objects C6 owns; what lives here is the
 * fact that they belong to the **source** and not to the group, plus the
 * dirty-epoch accounting that makes the invariant enforceable: a dirty source
 * yields **at most one rebuild per frame**, serving every group that samples it.
 *
 * Two failure modes are kept deliberately distinct:
 *
 * - **Structural** mistakes throw `GlassSceneError` — a duplicate id, a dangling
 *   reference, removing something still in use. Continuing past one leaves a
 *   scene whose references lie, so there is nothing to report and recover from.
 * - **Policy** findings go to the diagnostics channel — overlap, variant mixing,
 *   an illegal foreground mode. Those are recoverable, often per-frame, and the
 *   host decides what to do about them.
 *
 * Nothing here measures, schedules, or draws. Viewport rects arrive as data from
 * platform-web's batched read; frames are driven from outside (see
 * `scheduler.ts`).
 */

import type { ShapeChannels, ShapeFamily } from "@vitrea/geometry";
import type { InteractionState } from "@vitrea/motion";

import {
  resolveAccessibilityPolicy,
  type AccessibilityOverrides,
  type ResolvedAccessibilityPolicy,
  type SystemAccessibilityPreferences,
} from "./accessibility";
import {
  resolveBackdropHint,
  type BackdropEstimatorProvider,
  type BackdropHint,
  type ResolvedBackdropHint,
} from "./backdrop-hint";
import {
  classifyStateChange,
  resolveGlassGroupState,
  type CapabilityInputs,
  type GovernorPressure,
  type HintAvailability,
  type PlatformProbe,
  type SourceProbe,
  type StateChange,
} from "./capability";
import { createDiagnosticsChannel, type DiagnosticsChannel } from "./diagnostics";
import type { FramePhase } from "./frame";
import {
  defaultForegroundAdaptation,
  resolveForegroundAdaptation,
  type ForegroundAdaptation,
  type ResolvedForegroundAdaptation,
} from "./foreground";
import {
  checkVariantMixing,
  resolveMaterial,
  type MaterialProfile,
  type MaterialVariant,
  type ResolvedMaterial,
} from "./material";
import { rectsOverlap, type GlassPlane, type Rect, type ZSlot } from "./planes";
import type { GlassGroupState } from "./state";

export type GlassSceneErrorCode = "duplicate-id" | "unknown-id" | "in-use" | "wrong-source-kind";

/** A structural violation. Distinct from a diagnostic: the scene refuses the change. */
export class GlassSceneError extends Error {
  readonly code: GlassSceneErrorCode;

  constructor(code: GlassSceneErrorCode, message: string) {
    super(message);
    this.name = "GlassSceneError";
    this.code = code;
  }
}

/**
 * How large the derived pyramids for a texture source are. Effect-texture
 * resolution is decoupled from DOM DPR on purpose (§Performance envelope).
 */
export interface BackdropResolutionPolicy {
  /** Effect-texture scale relative to CSS px. */
  readonly scale: number;
  /** Cap on a pyramid level's longest side, in texture px. */
  readonly maxDimension: number;
}

/** Advisory default; the governor and calibration both move it. */
export const DEFAULT_BACKDROP_RESOLUTION: BackdropResolutionPolicy = {
  scale: 1,
  maxDimension: 2048,
};

export interface TextureBackdropSource {
  readonly id: string;
  readonly kind: "texture";
  /**
   * Probed *before* registration. Reporting `analysis: "exact"` for a frame and
   * then withdrawing it would be exactly the pretence X2 exists to prevent.
   */
  readonly probe: SourceProbe;
  readonly resolution?: BackdropResolutionPolicy;
}

export interface DomBackdropSource {
  readonly id: string;
  readonly kind: "dom";
}

export type BackdropSourceDescriptor = TextureBackdropSource | DomBackdropSource;

export interface BackdropSourceRecord {
  readonly descriptor: BackdropSourceDescriptor;
  /** Bumped whenever the source's content changes. */
  readonly dirtyEpoch: number;
  /** The epoch a rebuild was last handed out for. Dirty means `dirtyEpoch > builtEpoch`. */
  readonly builtEpoch: number;
}

export interface GlassGroupDescriptor {
  readonly id: string;
  readonly backdropSourceId: string;
  /** Scope for matched-geometry ids, so two morph pairs cannot collide. */
  readonly morphNamespace?: string;
  readonly material?: MaterialProfile;
  /** Requested adaptation. Resolved against the group's state, never assumed legal. */
  readonly foreground?: ForegroundAdaptation;
  /** Proximity-union threshold within the group, in CSS px (§Geometry). */
  readonly mergeDistance?: number;
  /** Backdrop sampled beyond the member union, in CSS px. */
  readonly samplingPadding?: number;
  /** X6: the author's declared hint. */
  readonly backdrop?: BackdropHint;
  /** X6: the provider form of the same contract. */
  readonly estimator?: BackdropEstimatorProvider;
}

export interface GlassGroupRecord {
  readonly descriptor: GlassGroupDescriptor;
  /** Set once the group has been resolved at least once. */
  readonly state?: GlassGroupState;
  /** Per-group governor override; falls back to the scene-wide pressure. */
  readonly governor?: GovernorPressure;
}

export interface GlassNodeDescriptor {
  readonly id: string;
  readonly groupId: string;
  readonly shapeFamily: ShapeFamily;
  readonly shape: ShapeChannels;
  readonly zSlot: ZSlot;
  /** Inherits the group's material profile when absent. */
  readonly variant?: MaterialVariant;
  readonly interaction?: InteractionState;
  /** Overrides the group's adaptation for this surface. */
  readonly foreground?: ForegroundAdaptation;
}

export interface GlassNodeRecord {
  readonly descriptor: GlassNodeDescriptor;
  /** Measured by platform-web in the read phase; absent until then. */
  readonly bounds?: Rect;
  /** Ancestor clip chain, viewport space. */
  readonly clip?: readonly Rect[];
}

/** One pyramid rebuild. `groupIds` is why there is one request and not one per group. */
export interface BackdropRebuildRequest {
  readonly sourceId: string;
  /** The dirty epoch this rebuild satisfies. */
  readonly epoch: number;
  readonly resolution: BackdropResolutionPolicy;
  /** Every group the rebuild serves. */
  readonly groupIds: readonly string[];
}

export interface ResolvedGroup {
  readonly groupId: string;
  readonly state: GlassGroupState;
  readonly hint: ResolvedBackdropHint;
  readonly foreground: ResolvedForegroundAdaptation;
}

export interface ResolvedNode {
  readonly nodeId: string;
  readonly groupId: string;
  readonly material: ResolvedMaterial;
  readonly foreground: ResolvedForegroundAdaptation;
}

export interface GroupStateChange {
  readonly groupId: string;
  /** Absent on a group's first resolution. */
  readonly previous?: GlassGroupState;
  readonly next: GlassGroupState;
  readonly change: StateChange;
}

export interface SceneResolution {
  readonly groups: readonly ResolvedGroup[];
  readonly nodes: readonly ResolvedNode[];
  /** Only the groups whose state moved, plus every group's first resolution. */
  readonly changes: readonly GroupStateChange[];
  /**
   * One policy for the whole root, carried here so a renderer has everything a
   * frame decided in one object rather than two.
   */
  readonly accessibility: ResolvedAccessibilityPolicy;
}

/** One overlapping pair inside one plane (X1). */
export interface PlaneOverlap {
  readonly plane: GlassPlane;
  readonly nodeIds: readonly [string, string];
}

export interface GlassSceneOptions {
  readonly platform: PlatformProbe;
  readonly accessibility?: SystemAccessibilityPreferences;
  readonly accessibilityOverrides?: AccessibilityOverrides;
  readonly diagnostics?: DiagnosticsChannel;
  /**
   * Dev-only checks — same-plane overlap, variant mixing — run only here.
   * Default true: they are cheap at v1's surface counts, and what they catch is
   * invisible otherwise.
   */
  readonly devMode?: boolean;
}

export interface GlassScene {
  readonly diagnostics: DiagnosticsChannel;

  /**
   * The phase of the frame in flight, or `undefined` outside one. The scheduler
   * sets it; the scene uses it to gate phase-scoped operations. Outside a frame
   * the scene has no opinion — a host may register and measure whenever it likes.
   */
  readonly framePhase: FramePhase | undefined;
  setFramePhase(phase: FramePhase | undefined): void;

  registerBackdropSource(descriptor: BackdropSourceDescriptor): void;
  /** Only the resolution policy is patchable: `kind` is identity, the probe has its own setter. */
  updateBackdropSource(id: string, patch: { readonly resolution: BackdropResolutionPolicy }): void;
  removeBackdropSource(id: string): void;
  backdropSource(id: string): BackdropSourceRecord | undefined;

  registerGlassGroup(descriptor: GlassGroupDescriptor): void;
  updateGlassGroup(id: string, patch: Partial<Omit<GlassGroupDescriptor, "id">>): void;
  removeGlassGroup(id: string): void;
  glassGroup(id: string): GlassGroupRecord | undefined;
  groupsOfSource(sourceId: string): readonly GlassGroupRecord[];

  registerGlassNode(descriptor: GlassNodeDescriptor): void;
  updateGlassNode(id: string, patch: Partial<Omit<GlassNodeDescriptor, "id">>): void;
  removeGlassNode(id: string): void;
  glassNode(id: string): GlassNodeRecord | undefined;
  nodesOfGroup(groupId: string): readonly GlassNodeRecord[];

  /** Measured viewport geometry, from the read phase. */
  setNodeBounds(id: string, bounds: Rect, clip?: readonly Rect[]): void;

  setPlatformProbe(probe: PlatformProbe): void;
  setSourceProbe(sourceId: string, probe: SourceProbe): void;
  /** Scene-wide by default; per group when `groupId` is given. */
  setGovernorPressure(pressure: GovernorPressure, groupId?: string): void;
  setSystemAccessibility(preferences: SystemAccessibilityPreferences): void;
  setAccessibilityOverrides(overrides: AccessibilityOverrides): void;
  accessibilityPolicy(): ResolvedAccessibilityPolicy;

  markBackdropSourceDirty(id: string): void;
  /** Peek without consuming. */
  dirtyBackdropSources(): readonly BackdropSourceRecord[];
  /**
   * Hand out the frame's rebuilds. The frame id *is* the scope: a second call
   * with the same id returns nothing, which is the §Core model invariant.
   */
  consumeDirtyBackdropSources(frameId: number): readonly BackdropRebuildRequest[];

  resolve(): SceneResolution;
  checkSamePlaneOverlap(): readonly PlaneOverlap[];
}

const unknown = (kind: string, id: string): GlassSceneError =>
  new GlassSceneError("unknown-id", `Unknown ${kind} "${id}".`);

const duplicate = (kind: string, id: string): GlassSceneError =>
  new GlassSceneError("duplicate-id", `Duplicate ${kind} id "${id}" — ids must be unique.`);

/** A texture source with a pending pyramid rebuild. dom sources never qualify. */
type RebuildableSource = BackdropSourceRecord & { readonly descriptor: TextureBackdropSource };

export function createGlassScene(options: GlassSceneOptions): GlassScene {
  const diagnostics = options.diagnostics ?? createDiagnosticsChannel();
  const devMode = options.devMode ?? true;

  const sources = new Map<string, BackdropSourceRecord>();
  const groups = new Map<string, GlassGroupRecord>();
  const nodes = new Map<string, GlassNodeRecord>();

  let platform = options.platform;
  let governor: GovernorPressure = "none";
  /**
   * Until a host reports otherwise, nothing is detected and every query is
   * answerable — the nominal policy. `reducedTransparencySupported` defaults to
   * true on purpose: the undetectable-preference warning is about a platform
   * fact a host *reported*, not about a host that has not spoken yet. The field
   * is required on `SystemAccessibilityPreferences`, so platform-web cannot
   * report preferences without stating it.
   */
  let system: SystemAccessibilityPreferences = options.accessibility ?? {
    reducedTransparency: false,
    reducedMotion: false,
    increasedContrast: false,
    forcedColors: false,
    reducedTransparencySupported: true,
  };
  let overrides: AccessibilityOverrides = options.accessibilityOverrides ?? {};
  let consumedFrameId: number | undefined;
  let framePhase: FramePhase | undefined;

  /**
   * Restructuring the graph while the renderer is walking it desynchronises the
   * frame's resolution from what gets drawn. Before the write phase a host may
   * mutate freely: React commits land outside a frame, and collect/read/update
   * are exactly where a host is meant to reconcile.
   */
  const guardStructural = (subject: string): void => {
    if (framePhase !== "write" && framePhase !== "render") return;
    diagnostics.report({
      code: "frame-phase-violation",
      severity: "error",
      subjects: [subject],
      message: `The scene was restructured during the "${framePhase}" phase. Register and remove before the write phase — the renderer is already walking the graph this frame's resolution described.`,
    });
  };

  const requireSource = (id: string): BackdropSourceRecord => {
    const record = sources.get(id);
    if (record === undefined) throw unknown("backdrop source", id);
    return record;
  };

  const requireGroup = (id: string): GlassGroupRecord => {
    const record = groups.get(id);
    if (record === undefined) throw unknown("glass group", id);
    return record;
  };

  const requireNode = (id: string): GlassNodeRecord => {
    const record = nodes.get(id);
    if (record === undefined) throw unknown("glass node", id);
    return record;
  };

  const groupsOfSource = (sourceId: string): readonly GlassGroupRecord[] =>
    [...groups.values()].filter((group) => group.descriptor.backdropSourceId === sourceId);

  const nodesOfGroup = (groupId: string): readonly GlassNodeRecord[] =>
    [...nodes.values()].filter((node) => node.descriptor.groupId === groupId);

  /**
   * dom sources are never rebuildable: the browser compositor does their blur,
   * so the GPU builds no pyramid for them at all (§Core model invariant).
   */
  const isRebuildable = (record: BackdropSourceRecord): record is RebuildableSource =>
    record.descriptor.kind === "texture" && record.dirtyEpoch > record.builtEpoch;

  function capabilityInputs(
    group: GlassGroupRecord,
    hint: HintAvailability,
  ): CapabilityInputs {
    const source = requireSource(group.descriptor.backdropSourceId);
    const pressure = group.governor ?? governor;

    return source.descriptor.kind === "texture"
      ? {
          configuredSource: "texture",
          platform,
          source: source.descriptor.probe,
          governor: pressure,
          hint,
        }
      : { configuredSource: "dom", platform, governor: pressure, hint };
  }

  const hintOf = (group: GlassGroupRecord): ResolvedBackdropHint =>
    resolveBackdropHint({
      groupId: group.descriptor.id,
      ...(group.descriptor.backdrop === undefined ? {} : { backdrop: group.descriptor.backdrop }),
      ...(group.descriptor.estimator === undefined
        ? {}
        : { estimator: group.descriptor.estimator }),
      diagnostics,
    });

  return {
    diagnostics,

    get framePhase() {
      return framePhase;
    },

    setFramePhase(phase) {
      framePhase = phase;
    },

    registerBackdropSource(descriptor) {
      if (sources.has(descriptor.id)) throw duplicate("backdrop source", descriptor.id);
      guardStructural(descriptor.id);
      sources.set(descriptor.id, { descriptor, dirtyEpoch: 0, builtEpoch: 0 });
    },

    updateBackdropSource(id, patch) {
      const record = requireSource(id);
      if (record.descriptor.kind !== "texture") {
        throw new GlassSceneError(
          "wrong-source-kind",
          `Backdrop source "${id}" is a dom source: the compositor owns its blur, so it has no resolution policy.`,
        );
      }
      sources.set(id, {
        ...record,
        descriptor: { ...record.descriptor, resolution: patch.resolution },
      });
    },

    removeBackdropSource(id) {
      requireSource(id);
      guardStructural(id);
      const dependents = groupsOfSource(id);
      if (dependents.length > 0) {
        throw new GlassSceneError(
          "in-use",
          `Backdrop source "${id}" is in use by ${dependents.map((group) => `"${group.descriptor.id}"`).join(", ")}. Remove those groups first.`,
        );
      }
      sources.delete(id);
    },

    backdropSource(id) {
      return sources.get(id);
    },

    registerGlassGroup(descriptor) {
      if (groups.has(descriptor.id)) throw duplicate("glass group", descriptor.id);
      requireSource(descriptor.backdropSourceId);
      guardStructural(descriptor.id);
      groups.set(descriptor.id, { descriptor });
    },

    updateGlassGroup(id, patch) {
      const record = requireGroup(id);
      const descriptor = { ...record.descriptor, ...patch };
      requireSource(descriptor.backdropSourceId);
      groups.set(id, { ...record, descriptor });
    },

    removeGlassGroup(id) {
      requireGroup(id);
      guardStructural(id);
      const members = nodesOfGroup(id);
      if (members.length > 0) {
        throw new GlassSceneError(
          "in-use",
          `Glass group "${id}" still holds ${members.map((node) => `"${node.descriptor.id}"`).join(", ")}. Remove those nodes first.`,
        );
      }
      groups.delete(id);
    },

    glassGroup(id) {
      return groups.get(id);
    },

    groupsOfSource,

    registerGlassNode(descriptor) {
      if (nodes.has(descriptor.id)) throw duplicate("glass node", descriptor.id);
      requireGroup(descriptor.groupId);
      guardStructural(descriptor.id);
      nodes.set(descriptor.id, { descriptor });
    },

    updateGlassNode(id, patch) {
      const record = requireNode(id);
      const descriptor = { ...record.descriptor, ...patch };
      requireGroup(descriptor.groupId);
      nodes.set(id, { ...record, descriptor });
    },

    removeGlassNode(id) {
      requireNode(id);
      guardStructural(id);
      nodes.delete(id);
    },

    glassNode(id) {
      return nodes.get(id);
    },

    nodesOfGroup,

    setNodeBounds(id, bounds, clip) {
      const record = requireNode(id);
      // Measuring in any other phase is the interleaved read/write that costs a
      // forced synchronous layout — the bug the batched read phase exists to
      // prevent. The value is still accepted: refusing it would leave the frame
      // drawing stale geometry, which is worse than a warned-about one.
      if (framePhase !== undefined && framePhase !== "read") {
        diagnostics.report({
          code: "frame-phase-violation",
          severity: "warning",
          subjects: [id],
          message: `Bounds for "${id}" were set during the "${framePhase}" phase. Batch every layout read into the "read" phase so the steady state performs none.`,
        });
      }
      nodes.set(id, { ...record, bounds, ...(clip === undefined ? {} : { clip }) });
    },

    setPlatformProbe(probe) {
      platform = probe;
    },

    setSourceProbe(sourceId, probe) {
      const record = requireSource(sourceId);
      if (record.descriptor.kind !== "texture") {
        throw new GlassSceneError(
          "wrong-source-kind",
          `Backdrop source "${sourceId}" is a dom source; only texture sources carry a source probe.`,
        );
      }
      sources.set(sourceId, { ...record, descriptor: { ...record.descriptor, probe } });
    },

    setGovernorPressure(pressure, groupId) {
      if (groupId === undefined) {
        governor = pressure;
        return;
      }
      const record = requireGroup(groupId);
      groups.set(groupId, { ...record, governor: pressure });
    },

    setSystemAccessibility(preferences) {
      system = preferences;
    },

    setAccessibilityOverrides(next) {
      overrides = next;
    },

    accessibilityPolicy() {
      return resolveAccessibilityPolicy(system, overrides, diagnostics);
    },

    markBackdropSourceDirty(id) {
      const record = requireSource(id);
      sources.set(id, { ...record, dirtyEpoch: record.dirtyEpoch + 1 });
    },

    dirtyBackdropSources() {
      return [...sources.values()].filter(isRebuildable);
    },

    consumeDirtyBackdropSources(frameId) {
      // The whole invariant in one guard: a frame gets one pass over the dirty
      // set, so no source is rebuilt twice however often a renderer asks.
      if (consumedFrameId === frameId) return [];
      consumedFrameId = frameId;

      const requests: BackdropRebuildRequest[] = [];
      const built: RebuildableSource[] = [];

      for (const record of sources.values()) {
        if (!isRebuildable(record)) continue;

        const consumers = groupsOfSource(record.descriptor.id).map((group) => group.descriptor.id);
        // Nothing samples it, so nothing needs it rebuilt. It stays dirty for
        // whenever a group does arrive.
        if (consumers.length === 0) continue;

        requests.push({
          sourceId: record.descriptor.id,
          epoch: record.dirtyEpoch,
          resolution: record.descriptor.resolution ?? DEFAULT_BACKDROP_RESOLUTION,
          groupIds: consumers,
        });
        built.push(record);
      }

      for (const record of built) {
        sources.set(record.descriptor.id, { ...record, builtEpoch: record.dirtyEpoch });
      }
      return requests;
    },

    resolve() {
      const resolvedGroups: ResolvedGroup[] = [];
      const resolvedNodes: ResolvedNode[] = [];
      const changes: GroupStateChange[] = [];
      const settled: GlassGroupRecord[] = [];

      for (const group of groups.values()) {
        const groupId = group.descriptor.id;
        const hint = hintOf(group);
        const state = resolveGlassGroupState(capabilityInputs(group, hint.availability));

        const requested = group.descriptor.foreground ?? defaultForegroundAdaptation(state);
        const foreground = resolveForegroundAdaptation(requested, state, { groupId, diagnostics });

        const previous = group.state;
        const change = classifyStateChange(previous, state);
        if (change.kind !== "unchanged") {
          changes.push({
            groupId,
            ...(previous === undefined ? {} : { previous }),
            next: state,
            change,
          });
        }
        settled.push({ ...group, state });
        resolvedGroups.push({ groupId, state, hint, foreground });

        const profile: MaterialProfile = group.descriptor.material ?? { variant: "regular" };
        const members = nodesOfGroup(groupId);

        for (const node of members) {
          const nodeId = node.descriptor.id;
          const material = resolveMaterial({
            variant: node.descriptor.variant ?? profile.variant,
            ...(profile.dimming === undefined ? {} : { dimming: profile.dimming }),
            nodeId,
            diagnostics,
          });
          resolvedNodes.push({
            nodeId,
            groupId,
            material,
            foreground: resolveForegroundAdaptation(node.descriptor.foreground ?? requested, state, {
              groupId: nodeId,
              diagnostics,
            }),
          });
        }

        if (devMode) {
          checkVariantMixing({
            groupId,
            members: members.map((node) => ({
              nodeId: node.descriptor.id,
              variant: node.descriptor.variant ?? profile.variant,
            })),
            diagnostics,
          });
        }
      }

      for (const group of settled) groups.set(group.descriptor.id, group);

      return {
        groups: resolvedGroups,
        nodes: resolvedNodes,
        changes,
        accessibility: resolveAccessibilityPolicy(system, overrides, diagnostics),
      };
    },

    checkSamePlaneOverlap() {
      if (!devMode) return [];

      const measured = [...nodes.values()].filter(
        (node): node is GlassNodeRecord & { readonly bounds: Rect } => node.bounds !== undefined,
      );

      const overlaps: PlaneOverlap[] = [];
      // Pairwise: v1's benchmark scene is eight surfaces, so a sweep line would
      // buy nothing but code. Revisit if a scene ever holds dozens.
      for (let i = 0; i < measured.length; i += 1) {
        for (let j = i + 1; j < measured.length; j += 1) {
          const a = measured[i];
          const b = measured[j];
          if (a === undefined || b === undefined) continue;

          const plane = a.descriptor.zSlot.plane;
          if (plane !== b.descriptor.zSlot.plane) continue;
          if (!rectsOverlap(a.bounds, b.bounds)) continue;

          const nodeIds: readonly [string, string] = [a.descriptor.id, b.descriptor.id];
          overlaps.push({ plane, nodeIds });
          diagnostics.report({
            code: "same-plane-overlap",
            severity: "error",
            subjects: [...nodeIds],
            message: `Glass surfaces "${nodeIds[0]}" and "${nodeIds[1]}" overlap inside the "${plane}" plane (X1). The paint sandwich cannot put one surface's body above the other's DOM label — put the upper one on the overlay plane instead.`,
          });
        }
      }
      return overlaps;
    },
  };
}
