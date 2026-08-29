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
 * That hand-out is provisional for as long as the frame is — a frame that throws
 * gives its claims back (`rollbackDirtyBackdropSources`), because a spent claim
 * with nothing built behind it would leave the source clean forever.
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
import {
  inflateRect,
  rectsOverlap,
  unionRect,
  type GlassPlane,
  type Rect,
  type ZSlot,
} from "./planes";
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

/** How far a group samples beyond its member union, and how near members merge. */
export interface GroupSamplingGeometry {
  /** Padding on the proxy's border box, in CSS px. */
  readonly samplingPadding: number;
  /** Proximity-union threshold within the group, in CSS px. */
  readonly mergeDistance: number;
}

/**
 * Advisory defaults, chosen so X1's constraints hold out of the box rather than
 * being numbers worth trusting.
 *
 * S1 measured that `samplingPadding` must be at least 3σ of the group's blur:
 * Filter Effects 2 clips a filter's input to the filtered element's own border
 * box, so an unpadded box starves its own blur at the edges. 24 is 3σ at
 * σ = 8 CSS px, a plausible regular-material blur — calibration (C7) replaces
 * it, and the *actual* 3σ check cannot live here because core carries no blur
 * radius (see the note on `GlassGroupDescriptor.samplingPadding`).
 *
 * `mergeDistance` defaults to the same number because X1 requires
 * `mergeDistance ≥ samplingPadding`: any two members close enough for their
 * padded proxies to overlap must already have merged into one, or the filter
 * applies twice — measured at 1.5625× for `brightness(1.25)`, paint-order
 * dependent, drifting up to 17/255 even in legal 8px-gap geometry.
 */
export const DEFAULT_GROUP_SAMPLING: GroupSamplingGeometry = {
  samplingPadding: 24,
  mergeDistance: 24,
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
  /**
   * Proximity-union threshold within the group, in CSS px (§Geometry). X1
   * requires it to be at least `samplingPadding`; core checks that, since both
   * numbers live here.
   */
  readonly mergeDistance?: number;
  /**
   * Padding on the group proxy's border box, in CSS px. X1 also requires it to
   * be at least 3σ of the group's blur — core cannot check *that* one, because
   * it carries no blur radius; platform-web owns it, where the material's blur
   * is known.
   */
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
  /** Defaults filled in, so a consumer reads one pair of numbers and not two optionals. */
  readonly sampling: GroupSamplingGeometry;
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

/** One overlapping pair of surfaces inside one plane (X1). */
export interface PlaneOverlap {
  readonly plane: GlassPlane;
  readonly nodeIds: readonly [string, string];
}

/**
 * Two groups close enough in one plane that one group's padded proxy would
 * sample the pixels the other one paints (X1).
 */
export interface ProxyOverlap {
  readonly plane: GlassPlane;
  readonly groupIds: readonly [string, string];
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
  /** A key present with `undefined` clears that override; an absent key keeps it. */
  updateGlassGroup(id: string, patch: DescriptorPatch<Omit<GlassGroupDescriptor, "id">>): void;
  removeGlassGroup(id: string): void;
  glassGroup(id: string): GlassGroupRecord | undefined;
  groupsOfSource(sourceId: string): readonly GlassGroupRecord[];

  registerGlassNode(descriptor: GlassNodeDescriptor): void;
  /** A key present with `undefined` clears that override; an absent key keeps it. */
  updateGlassNode(id: string, patch: DescriptorPatch<Omit<GlassNodeDescriptor, "id">>): void;
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
  /**
   * Give back what `frameId` took, because the frame did not finish.
   *
   * Consuming commits `builtEpoch` at hand-out rather than at completion — core
   * has no view of the wire and cannot wait for one. That is right while the
   * frame runs to its end, and a lie the moment it does not: a claim spent on a
   * frame that threw leaves the source sitting clean at an epoch whose pixels
   * were never imported, and nothing ever marks it dirty again. Restoring the
   * pre-consume epochs makes the commit provisional for exactly as long as the
   * frame is.
   *
   * Returns the source ids restored. Idempotent, and a no-op for any frame id
   * other than the one that consumed.
   */
  rollbackDirtyBackdropSources(frameId: number): readonly string[];

  resolve(): SceneResolution;
  checkSamePlaneOverlap(): readonly PlaneOverlap[];
  /**
   * The cross-group half of X1's proxy geometry. `mergeDistance` only unions
   * members *within* a group, so a neighbouring group's proxy can still sample
   * the pixels this one paints — which S1 measured double-filtering.
   */
  checkGroupProxyOverlap(): readonly ProxyOverlap[];
}

/**
 * A descriptor patch. Unlike `Partial`, a key present with `undefined` is
 * meaningful: it *clears* the override and restores the inherited default.
 * Without that, a declarative binding could never take a prop back — React
 * re-rendering `<GlassGroup backdrop={undefined}>` would have no way to say
 * "this group no longer declares a hint" short of tearing the entry down.
 */
export type DescriptorPatch<D> = { readonly [K in keyof D]?: D[K] | undefined };

/**
 * Apply a patch, deleting the keys it explicitly cleared. `id` is identity and
 * therefore not patchable, which is why the patch is typed over `Omit<D, "id">`
 * while the result is a whole descriptor.
 */
function applyPatch<D extends object>(base: D, patch: DescriptorPatch<Omit<D, "id">>): D {
  const next = { ...base } as Record<string, unknown>;
  for (const [key, value] of Object.entries(patch)) {
    if (value === undefined) delete next[key];
    else next[key] = value;
  }
  return next as D;
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
  /**
   * What `consumedFrameId`'s hand-out committed, and what it committed *over* —
   * the ledger `rollbackDirtyBackdropSources` unwinds. One frame's worth, because
   * a rollback only ever concerns the frame that is failing right now.
   */
  let consumedEpochs: readonly { readonly id: string; readonly builtEpoch: number }[] = [];
  let framePhase: FramePhase | undefined;

  /**
   * Descriptors are frozen from the `update` phase onward.
   *
   * `update` is where reads become resolved state — the scheduler resolves the
   * whole scene at the top of it — so any descriptor change after that leaves
   * the frame's resolution describing a scene that no longer exists, and write
   * and render act on the difference. That covers patches, not only
   * registration: a node's `variant` feeds its resolved material and its
   * `foreground` its resolved adaptation, so "only the graph's shape is frozen"
   * would be a line with nothing behind it. Reconcile in `collect`, which is
   * what that phase is for; outside a frame a host may mutate freely, and that
   * is where a React commit lands.
   */
  const FROZEN_PHASES: readonly FramePhase[] = ["update", "write", "render"];

  const guardFrozenScene = (subject: string): void => {
    if (framePhase === undefined || !FROZEN_PHASES.includes(framePhase)) return;
    diagnostics.report({
      code: "frame-phase-violation",
      severity: "error",
      subjects: [subject],
      message: `The scene was changed during the "${framePhase}" phase, after this frame resolved. Register, remove and patch in the "collect" phase or outside a frame — from "update" onward the resolution and the scene must agree.`,
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

  /**
   * Fill in the group's sampling geometry and check X1's relationship between
   * the two numbers. Authored values are never coerced — a silently widened
   * merge distance would change which members fuse, which is a visual decision
   * that belongs to the author.
   */
  const paddingOf = (group: GlassGroupRecord): number =>
    group.descriptor.samplingPadding ?? DEFAULT_GROUP_SAMPLING.samplingPadding;

  function samplingOf(group: GlassGroupRecord): GroupSamplingGeometry {
    const samplingPadding = paddingOf(group);
    const mergeDistance = group.descriptor.mergeDistance ?? samplingPadding;

    if (devMode && mergeDistance < samplingPadding) {
      diagnostics.report({
        code: "merge-distance-below-padding",
        severity: "warning",
        subjects: [group.descriptor.id],
        message: `Group "${group.descriptor.id}" has mergeDistance ${mergeDistance} below samplingPadding ${samplingPadding}, which X1 forbids: two members can then sit close enough for their padded proxies to overlap without having merged, and the backdrop filter applies twice over the overlap — paint-order dependent, and measured drifting up to 17/255. Raise mergeDistance to at least the padding.`,
      });
    }

    return { samplingPadding, mergeDistance };
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
      guardFrozenScene(descriptor.id);
      sources.set(descriptor.id, { descriptor, dirtyEpoch: 0, builtEpoch: 0 });
    },

    updateBackdropSource(id, patch) {
      const record = requireSource(id);
      guardFrozenScene(id);
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
      guardFrozenScene(id);
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
      guardFrozenScene(descriptor.id);
      groups.set(descriptor.id, { descriptor });
    },

    updateGlassGroup(id, patch) {
      const record = requireGroup(id);
      const descriptor = applyPatch(record.descriptor, patch);
      requireSource(descriptor.backdropSourceId);
      guardFrozenScene(id);
      groups.set(id, { ...record, descriptor });
    },

    removeGlassGroup(id) {
      requireGroup(id);
      guardFrozenScene(id);
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
      guardFrozenScene(descriptor.id);
      nodes.set(descriptor.id, { descriptor });
    },

    updateGlassNode(id, patch) {
      const record = requireNode(id);
      const descriptor = applyPatch(record.descriptor, patch);
      requireGroup(descriptor.groupId);
      guardFrozenScene(id);
      nodes.set(id, { ...record, descriptor });
    },

    removeGlassNode(id) {
      requireNode(id);
      guardFrozenScene(id);
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

      consumedEpochs = built.map((record) => ({
        id: record.descriptor.id,
        builtEpoch: record.builtEpoch,
      }));
      for (const record of built) {
        sources.set(record.descriptor.id, { ...record, builtEpoch: record.dirtyEpoch });
      }
      return requests;
    },

    rollbackDirtyBackdropSources(frameId) {
      if (consumedFrameId !== frameId) return [];
      const restored: string[] = [];
      for (const { id, builtEpoch } of consumedEpochs) {
        const record = sources.get(id);
        // Gone since the hand-out. Nothing to restore, and nothing to say about
        // it: a removed source has no pyramid anyone is waiting for.
        if (record === undefined) continue;
        // `dirtyEpoch` is left exactly as it stands. Anything that marked the
        // source dirty after the hand-out is a real change this frame's failed
        // claim has no business erasing, and restoring the older `builtEpoch`
        // under it re-opens the gap either way.
        sources.set(id, { ...record, builtEpoch });
        restored.push(id);
      }
      consumedEpochs = [];
      return restored;
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
        const foreground = resolveForegroundAdaptation(requested, state, { subject: groupId, diagnostics });

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
        resolvedGroups.push({ groupId, state, hint, foreground, sampling: samplingOf(group) });

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
              subject: nodeId,
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

    checkGroupProxyOverlap() {
      if (!devMode) return [];

      // Two rects per (group, plane), because the check turns on the difference
      // between them: the padded box is everything that group's proxy *samples*,
      // and the unpadded union is everything it *paints* — a proxy is masked to
      // its members' shapes, so nothing of it lands outside that union. A group
      // with nothing measured yet contributes neither.
      const boxes: {
        readonly groupId: string;
        readonly plane: GlassPlane;
        readonly box: Rect;
        readonly clipUnion: Rect;
      }[] = [];

      for (const group of groups.values()) {
        const groupId = group.descriptor.id;
        const padding = paddingOf(group);
        const byPlane = new Map<GlassPlane, Rect>();

        for (const node of nodesOfGroup(groupId)) {
          const { bounds } = node;
          if (bounds === undefined) continue;
          const plane = node.descriptor.zSlot.plane;
          const grown = byPlane.get(plane);
          byPlane.set(plane, grown === undefined ? bounds : unionRect(grown, bounds));
        }

        for (const [plane, union] of byPlane) {
          boxes.push({ groupId, plane, box: inflateRect(union, padding), clipUnion: union });
        }
      }

      // The predicate is one group's padded box against the *other group's
      // painted region*, not against its padded box.
      //
      // Double filtering needs one proxy's sampled region to contain another
      // proxy's already filtered output. The second proxy paints only inside its
      // own clip union and its box reaches one padding beyond that, so a
      // box-against-box test fires out to the *sum* of the two paddings — and
      // over the outer part of that range the boxes meet only where neither
      // group has drawn anything, which is a region no filter can pick up. The
      // measurement is `spikes/s1-proxy-topology/overlap-experiment/`: 81
      // byte-deterministic cells over three blur radii and four backdrop
      // classes, with zero cross-group leak at every separation at or past one
      // padding, converging on the geometric bound from below.
      //
      // Symmetric on purpose. Only the later-painted group is ever contaminated,
      // so an order-aware form would halve this again — but paint order is the
      // platform's to decide and a finding that comes and goes with it is worse
      // diagnostics than a statement about the layout.
      const overlaps: ProxyOverlap[] = [];
      for (let i = 0; i < boxes.length; i += 1) {
        for (let j = i + 1; j < boxes.length; j += 1) {
          const a = boxes[i];
          const b = boxes[j];
          if (a === undefined || b === undefined) continue;
          if (a.plane !== b.plane || a.groupId === b.groupId) continue;
          if (!rectsOverlap(a.box, b.clipUnion) && !rectsOverlap(b.box, a.clipUnion)) continue;

          const groupIds: readonly [string, string] = [a.groupId, b.groupId];
          overlaps.push({ plane: a.plane, groupIds });
          diagnostics.report({
            code: "group-proxy-overlap",
            severity: "warning",
            subjects: [...groupIds],
            message: `Groups "${groupIds[0]}" and "${groupIds[1]}" sit close enough in the "${a.plane}" plane that one group's padded backdrop proxy samples the pixels the other group paints, and X1 says the filter then applies twice over them — paint-order dependent, and steeply distance-dependent: measured at most 3/255 at a 1.5σ gap, mean 0.43 / max 4 at 1σ, mean 2.56 / max 15 at 0.25σ, and byte-identical zero once the gap reaches the padding. mergeDistance cannot help: it only unions members inside one group. Either put these surfaces in one group so they share a proxy, or separate them by at least the larger group's samplingPadding.`,
          });
        }
      }
      return overlaps;
    },
  };
}
