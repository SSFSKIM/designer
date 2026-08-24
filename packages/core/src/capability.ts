/**
 * X2 — the capability state machine (§Backdrop & analysis contracts, the
 * honesty core).
 *
 * Capability is not a free tuple. The app *configures* a source; the runtime
 * *resolves* one of an enumerated set of states from probe results that arrive
 * as plain data. Nothing here touches a GPU, a browser or a clock: platform-web
 * probes, C6 renders, this file only decides.
 *
 * ## Resolution rules
 *
 * 1. **Renderer faults** — no WebGPU, a lost device, or a governor tier switch —
 *    drop `activeRenderer` to `"css"`. Nothing else can.
 * 2. **Sampling faults** demote the backdrop path without touching the
 *    renderer. A tainted or incompatible texture leaves WebGPU drawing tint,
 *    rim and glow with nothing to sample (`samplingBackend: "none"`); it does
 *    *not* silently re-point the group at the DOM behind it, because the app
 *    asked for a texture and swapping backdrops underneath it would be exactly
 *    the pretence this model exists to prevent.
 * 3. **Refraction follows what is actually sampled.** `"true"` needs GPU-texture
 *    sampling; `"approximate"` is the shader's rim-lensing over a CSS proxy;
 *    the CSS tier gets `"none"` because `backdrop-filter` blurs, it does not
 *    bend.
 * 4. **`exact` analysis needs a GPU texture.** Otherwise a declared hint or an
 *    estimator provider yields `"hint"` (X6), and nothing yields `"none"`.
 * 5. **One reason is reported, by precedence** — see `REASON_PRECEDENCE`.
 */

import type { ConfiguredSource, DemotionReason, GlassGroupState } from "./state";

/** Platform-wide probe results. platform-web produces these; core only reads them. */
export interface PlatformProbe {
  /** A WebGPU adapter and device were obtained. */
  readonly webgpu: boolean;
  /** `backdrop-filter` is supported and actually filters. */
  readonly backdropFilter: boolean;
  /**
   * S1's startup conformance probe: does a portaled masked proxy sample the
   * same pixels as an in-place `backdrop-filter`? Filter Effects 2's Backdrop
   * Root lacks WG consensus, so this is probed, never assumed.
   */
  readonly backdropProxyConformance: "pass" | "fail";
  readonly deviceHealth: "ok" | "lost";
}

/** Per-source facts. Meaningful for `texture` sources only. */
export interface SourceProbe {
  /** CORS taint. A tainted source cannot be read into a GPU texture at all. */
  readonly taint: "clean" | "tainted";
  /** Whether an app-supplied view satisfies the declared usage/format/dimension requirements. */
  readonly textureCompatibility: "compatible" | "incompatible";
}

/**
 * Quality-governor pressure (§Performance envelope). The governor degrades
 * *within* a tier before it switches tiers, so only `"demote-tier"` is a
 * demotion; `"degrade-in-tier"` changes render quality knobs C6 owns and leaves
 * the resolved state untouched.
 */
export const GOVERNOR_PRESSURES = ["none", "degrade-in-tier", "demote-tier"] as const;

export type GovernorPressure = (typeof GOVERNOR_PRESSURES)[number];

/**
 * X6 — which of the one hint mechanism is in play. Both an author-declared
 * `backdrop` prop and an estimator provider produce `analysis: "hint"`; the
 * distinction is kept for developer-facing reporting, never smuggled into the
 * state, whose shape is frozen.
 */
export const HINT_AVAILABILITIES = ["none", "author-hint", "estimator"] as const;

export type HintAvailability = (typeof HINT_AVAILABILITIES)[number];

/** Everything the resolver needs. A texture group must declare its source probe. */
export type CapabilityInputs =
  | {
      readonly configuredSource: "texture";
      readonly platform: PlatformProbe;
      readonly source: SourceProbe;
      readonly governor: GovernorPressure;
      readonly hint: HintAvailability;
    }
  | {
      readonly configuredSource: "dom";
      readonly platform: PlatformProbe;
      readonly source?: undefined;
      readonly governor: GovernorPressure;
      readonly hint: HintAvailability;
    };

/**
 * Which reason is reported when several faults hold. Platform facts come first
 * because they explain the largest loss; the governor comes last so transient
 * pressure never masks a standing fault the app could fix.
 */
const REASON_PRECEDENCE: readonly DemotionReason[] = [
  "no-webgpu",
  "device-lost",
  "tainted-source",
  "incompatible-texture",
  "no-backdrop-filter",
  "probe-failed",
  "governor",
];

/** What clears a demotion. `"none"` is the honest answer for a platform fact. */
export type RecoveryTrigger =
  | "device-restored"
  | "source-replaced"
  | "probe-repassed"
  | "pressure-released"
  | "none";

export interface RecoveryContract {
  readonly trigger: RecoveryTrigger;
  readonly explanation: string;
}

/**
 * Every demotion names its recovery transition (§honesty core). This table is
 * the contract; the resolver is stateless, so recovery *is* re-resolution once
 * the named input changes.
 */
export const DEMOTION_RECOVERY: Readonly<Record<DemotionReason, RecoveryContract>> = {
  "no-webgpu": {
    trigger: "none",
    explanation:
      "WebGPU is unavailable in this browser session. Nothing the app can do recovers it; a user enabling support means a new session.",
  },
  "no-backdrop-filter": {
    trigger: "probe-repassed",
    explanation:
      "The backdrop-filter probe failed. Re-running it after the page's filter context changes can pass.",
  },
  "tainted-source": {
    trigger: "source-replaced",
    explanation:
      "A CORS-tainted source cannot be read into a GPU texture. Register a same-origin or CORS-permitted source.",
  },
  "incompatible-texture": {
    trigger: "source-replaced",
    explanation:
      "The supplied texture view does not satisfy the declared usage, format or dimension requirements. Register a conforming source.",
  },
  "device-lost": {
    trigger: "device-restored",
    explanation:
      "The GPUDevice was lost. vitrea-owned devices re-request automatically; an app-owned device needs the replacement-device callback and the resource re-registration handshake.",
  },
  "probe-failed": {
    trigger: "probe-repassed",
    explanation:
      "The backdrop-proxy conformance probe found this engine's proxy sampling non-equivalent. It clears if the probe passes on a later run.",
  },
  governor: {
    trigger: "pressure-released",
    explanation:
      "The quality governor switched tiers under sustained pressure. It restores after its hysteresis and cooldown elapse.",
  },
};

/** Faults that hold for these inputs, independent of what was resolved from them. */
function applicableFaults(inputs: CapabilityInputs): readonly DemotionReason[] {
  const { platform, governor, configuredSource } = inputs;
  const faults = new Set<DemotionReason>();

  if (!platform.webgpu) faults.add("no-webgpu");
  // A device can only be lost if there was one to lose.
  if (platform.webgpu && platform.deviceHealth === "lost") faults.add("device-lost");

  if (configuredSource === "texture") {
    if (inputs.source.taint === "tainted") faults.add("tainted-source");
    if (inputs.source.textureCompatibility === "incompatible") faults.add("incompatible-texture");
  } else {
    if (!platform.backdropFilter) faults.add("no-backdrop-filter");
    if (platform.backdropProxyConformance === "fail") faults.add("probe-failed");
  }

  if (governor === "demote-tier") faults.add("governor");

  return REASON_PRECEDENCE.filter((reason) => faults.has(reason));
}

const RENDERER_FAULTS: readonly DemotionReason[] = ["no-webgpu", "device-lost", "governor"];

const SAMPLING_FAULTS: readonly DemotionReason[] = [
  "tainted-source",
  "incompatible-texture",
  "no-backdrop-filter",
  "probe-failed",
];

/**
 * Resolve one group's state. Pure, total, and deterministic: the same inputs
 * always produce the same state, and `configuredSource` is copied through
 * untouched by every path.
 */
export function resolveGlassGroupState(inputs: CapabilityInputs): GlassGroupState {
  const faults = applicableFaults(inputs);
  const configuredSource: ConfiguredSource = inputs.configuredSource;

  const rendererDemoted = faults.some((fault) => RENDERER_FAULTS.includes(fault));
  const samplingDemoted = faults.some((fault) => SAMPLING_FAULTS.includes(fault));

  const activeRenderer = rendererDemoted ? "css" : "webgpu";

  const sampling = ((): Pick<GlassGroupState, "samplingBackend" | "refraction"> => {
    if (activeRenderer === "css") {
      // No shader runs, so nothing bends; backdrop-filter still frosts if present.
      return {
        samplingBackend: inputs.platform.backdropFilter ? "css-backdrop" : "none",
        refraction: "none",
      };
    }
    if (samplingDemoted) {
      return { samplingBackend: "none", refraction: "none" };
    }
    return configuredSource === "texture"
      ? { samplingBackend: "gpu-texture", refraction: "true" }
      : { samplingBackend: "css-backdrop", refraction: "approximate" };
  })();

  const analysis =
    sampling.samplingBackend === "gpu-texture" ? "exact" : inputs.hint === "none" ? "none" : "hint";

  const reason = faults[0];

  return {
    configuredSource,
    activeRenderer,
    ...sampling,
    analysis,
    health: reason === undefined ? "ok" : "demoted",
    ...(reason === undefined ? {} : { demotionReason: reason }),
  };
}

/** How one group's state moved between two resolutions. */
export type StateChange =
  | { readonly kind: "unchanged" }
  /** The group's first resolution — there was no previous state to move from. */
  | { readonly kind: "initial"; readonly reason?: DemotionReason }
  | { readonly kind: "demoted"; readonly reason: DemotionReason }
  | { readonly kind: "recovered"; readonly from: DemotionReason }
  | { readonly kind: "changed"; readonly reason?: DemotionReason };

const STATE_KEYS = [
  "configuredSource",
  "activeRenderer",
  "samplingBackend",
  "refraction",
  "analysis",
  "health",
  "demotionReason",
] as const;

const sameState = (a: GlassGroupState, b: GlassGroupState): boolean =>
  STATE_KEYS.every((key) => a[key] === b[key]);

/**
 * Name a transition, so a host can log "recovered from device-lost" rather than
 * diff two records. Used by the scene when it re-resolves during a frame. A
 * missing `previous` is a group's first resolution, not a change.
 */
export function classifyStateChange(
  previous: GlassGroupState | undefined,
  next: GlassGroupState,
): StateChange {
  if (previous === undefined) {
    return {
      kind: "initial",
      ...(next.demotionReason === undefined ? {} : { reason: next.demotionReason }),
    };
  }
  if (sameState(previous, next)) return { kind: "unchanged" };

  if (previous.health === "ok" && next.demotionReason !== undefined) {
    return { kind: "demoted", reason: next.demotionReason };
  }
  if (previous.demotionReason !== undefined && next.health === "ok") {
    return { kind: "recovered", from: previous.demotionReason };
  }
  return {
    kind: "changed",
    ...(next.demotionReason === undefined ? {} : { reason: next.demotionReason }),
  };
}
