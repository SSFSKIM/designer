/**
 * `GlassGroup` — one sampling group, declared.
 *
 * A group is what shares a backdrop source, one masked sampling proxy, and one
 * material profile (§Core model). It is also the unit X1's proxy constraints are
 * written in, which is why `mergeDistance` and `samplingPadding` are props here
 * and nowhere else: core checks `mergeDistance >= samplingPadding` from these
 * numbers, and platform-web checks the 3σ floor against the material's blur.
 *
 * This component renders no DOM at all. Registering a group is a scene-model
 * change, and the spec's thinness law says the binding maps lifecycle onto
 * platform-web registration rather than growing structure of its own.
 *
 * ## The backdrop, and X6's one hint contract
 *
 * `backdrop={{ kind: "texture", ... }}` registers a GPU-ownable source and moves
 * the group onto the texture path; the default `"dom"` uses the root's shared dom
 * source. `hint` and `estimator` are X6's *single* mechanism in its two forms —
 * an author-declared `{ tone, luminance?, complexity? }`, or a provider. Neither
 * is pixel analysis and core's reporting never says it is.
 */

import type {
  BackdropEstimatorProvider,
  BackdropHint,
  BackdropResolutionPolicy,
  DimmingPolicy,
  ForegroundAdaptation,
  MaterialProfile,
  MaterialVariant,
  SourceProbe,
} from "vitrea";
import type { GlassRoot as PlatformGlassRoot } from "@vitrea/platform-web";
import { useCallback, useId, useLayoutEffect, useMemo, useRef, type ReactNode } from "react";

import { GlassGroupContext, useGlassRoot, type GlassGroupHandle } from "./context";

/** A GPU-ownable backdrop: an image, video, canvas, or procedural texture. */
export interface GlassTextureBackdrop {
  readonly kind: "texture";
  /** Stable id; the same texture registered by two groups is registered once. */
  readonly id: string;
  /**
   * Probed *before* registration (core's requirement): reporting `analysis:
   * "exact"` for a frame and then withdrawing it is the pretence X2 exists to
   * prevent. Defaults to a clean, compatible source.
   */
  readonly probe?: SourceProbe;
  readonly resolution?: BackdropResolutionPolicy;
}

/** The arbitrary-DOM path. Uses the root's shared dom source unless given an id. */
export interface GlassDomBackdrop {
  readonly kind: "dom";
  readonly id?: string;
}

export type GlassBackdrop = GlassTextureBackdrop | GlassDomBackdrop;

const DEFAULT_SOURCE_PROBE: SourceProbe = { taint: "clean", textureCompatibility: "compatible" };

/**
 * How many groups are currently using each texture source, per root.
 *
 * Sources are root-scoped and groups are not, so the count cannot live on a
 * group: two groups sampling one video is the case the source registry exists to
 * serve (the blur pyramid belongs to the source, rebuilt once per dirty source
 * per frame — never once per group). Whichever group unmounts last is the one
 * that removes the source, which is also what core requires: it refuses to
 * remove a source any group still references.
 */
const sourceLeases = new WeakMap<PlatformGlassRoot, Map<string, number>>();

function retainTextureSource(root: PlatformGlassRoot, backdrop: GlassTextureBackdrop): () => void {
  const counts = sourceLeases.get(root) ?? new Map<string, number>();
  sourceLeases.set(root, counts);

  const held = counts.get(backdrop.id) ?? 0;
  if (held === 0 && root.scene.backdropSource(backdrop.id) === undefined) {
    root.registerBackdropSource({
      id: backdrop.id,
      kind: "texture",
      probe: backdrop.probe ?? DEFAULT_SOURCE_PROBE,
      ...(backdrop.resolution === undefined ? {} : { resolution: backdrop.resolution }),
    });
  }
  counts.set(backdrop.id, held + 1);

  return () => {
    const remaining = (counts.get(backdrop.id) ?? 1) - 1;
    if (remaining > 0) {
      counts.set(backdrop.id, remaining);
      return;
    }
    counts.delete(backdrop.id);
    if (root.scene.backdropSource(backdrop.id) !== undefined) {
      root.scene.removeBackdropSource(backdrop.id);
    }
  };
}

export interface GlassGroupProps {
  readonly children?: ReactNode | undefined;
  /** Generated from `useId` when absent, so a group is never accidentally shared. */
  readonly id?: string | undefined;
  readonly backdrop?: GlassBackdrop | undefined;
  /** X6: the author's declared hint about what is behind this group. */
  readonly hint?: BackdropHint | undefined;
  /** X6: the provider form of the same contract. */
  readonly estimator?: BackdropEstimatorProvider | undefined;
  /** Group-wide material. A surface may override `variant`; `dimming` lives here. */
  readonly variant?: MaterialVariant | undefined;
  /** Required for any `clear` surface in this group — core refuses to invent one. */
  readonly dimming?: DimmingPolicy | undefined;
  readonly foreground?: ForegroundAdaptation | undefined;
  /** Scope for matched-geometry ids, so two morph pairs cannot collide. */
  readonly morphNamespace?: string | undefined;
  readonly mergeDistance?: number | undefined;
  readonly samplingPadding?: number | undefined;
}

/** The patchable half of a group's descriptor: everything that is not identity. */
interface GroupPolicy {
  readonly material: MaterialProfile | undefined;
  readonly backdrop: BackdropHint | undefined;
  readonly foreground: ForegroundAdaptation | undefined;
  readonly morphNamespace: string | undefined;
  readonly mergeDistance: number | undefined;
  readonly samplingPadding: number | undefined;
}

export function GlassGroup(props: GlassGroupProps): ReactNode {
  const {
    children,
    id,
    backdrop,
    hint,
    estimator,
    variant,
    dimming,
    foreground,
    morphNamespace,
    mergeDistance,
    samplingPadding,
  } = props;

  const root = useGlassRoot();
  const generatedId = useId();
  const groupId = id ?? `vitrea-group${generatedId}`;

  const leases = useRef(0);
  const disposed = useRef(false);
  const registered = useRef(false);
  /** Runs with the group's removal, never before it: core refuses an in-use source. */
  const releaseSource = useRef<(() => void) | undefined>(undefined);

  const removeGroup = useCallback(() => {
    if (!registered.current || root === null) return;
    registered.current = false;
    root.removeGroup(groupId);
    releaseSource.current?.();
    releaseSource.current = undefined;
  }, [groupId, root]);

  /**
   * The policy half of the descriptor, as a value.
   *
   * Compared by content rather than by identity, because `<GlassGroup hint={{
   * tone: "dark" }}>` is the way anyone writes this and an inline literal is a
   * fresh object on every render. Keying on identity would re-run the effect on
   * every parent render — and re-registering an existing id is a structural
   * throw in core, not a warning.
   */
  const policy: GroupPolicy = useMemo(
    () => ({
      material:
        variant === undefined && dimming === undefined
          ? undefined
          : { variant: variant ?? "regular", ...(dimming === undefined ? {} : { dimming }) },
      backdrop: hint,
      foreground,
      morphNamespace,
      mergeDistance,
      samplingPadding,
    }),
    [dimming, foreground, hint, mergeDistance, morphNamespace, samplingPadding, variant],
  );
  // `JSON.stringify` drops undefined values, so an absent prop and an explicitly
  // undefined one produce the same key — which is what they mean here.
  const policyKey = JSON.stringify(policy);

  /** Identity, not policy: only these can require a different group. */
  const sourceId = backdrop?.id;
  const sourceKind = backdrop?.kind;

  // Held in refs so registration reads the current policy without listing it as
  // a dependency — a group's identity is its id and its source, nothing else.
  const policyRef = useRef(policy);
  policyRef.current = policy;
  const backdropRef = useRef(backdrop);
  backdropRef.current = backdrop;

  useLayoutEffect(() => {
    if (root === null) return;

    const texture = backdropRef.current;
    releaseSource.current =
      texture?.kind === "texture" ? retainTextureSource(root, texture) : undefined;

    const current = policyRef.current;
    root.registerGroup({
      id: groupId,
      ...(sourceId === undefined ? {} : { backdropSourceId: sourceId }),
      ...(current.material === undefined ? {} : { material: current.material }),
      ...(current.backdrop === undefined ? {} : { backdrop: current.backdrop }),
      ...(current.foreground === undefined ? {} : { foreground: current.foreground }),
      ...(current.morphNamespace === undefined ? {} : { morphNamespace: current.morphNamespace }),
      ...(current.mergeDistance === undefined ? {} : { mergeDistance: current.mergeDistance }),
      ...(current.samplingPadding === undefined ? {} : { samplingPadding: current.samplingPadding }),
      ...(estimatorRef.current === undefined ? {} : { estimator: estimatorRef.current }),
    });
    registered.current = true;
    disposed.current = false;

    return () => {
      disposed.current = true;
      if (leases.current === 0) removeGroup();
    };
  }, [groupId, removeGroup, root, sourceId, sourceKind]);

  const estimatorRef = useRef(estimator);
  estimatorRef.current = estimator;

  /**
   * Policy changes patch the descriptor. core's `DescriptorPatch` is built for
   * exactly this: a key present with `undefined` clears an override, an absent
   * key keeps it — which is what `<GlassGroup hint={undefined}>` should mean.
   */
  useLayoutEffect(() => {
    if (root === null || !registered.current) return;
    root.scene.updateGlassGroup(groupId, {
      material: policy.material,
      backdrop: policy.backdrop,
      estimator,
      foreground: policy.foreground,
      morphNamespace: policy.morphNamespace,
      mergeDistance: policy.mergeDistance,
      samplingPadding: policy.samplingPadding,
    });
    // `policy` is keyed by content; `estimator` carries a method, so identity is
    // the only comparison available for it.
  }, [estimator, groupId, policyKey, root]);

  const handle: GlassGroupHandle = useMemo(
    () => ({
      groupId,
      retain() {
        leases.current += 1;
        return () => {
          leases.current -= 1;
          if (leases.current === 0 && disposed.current) removeGroup();
        };
      },
    }),
    [groupId, removeGroup],
  );

  return <GlassGroupContext.Provider value={handle}>{children}</GlassGroupContext.Provider>;
}
