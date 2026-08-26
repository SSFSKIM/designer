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
 * 0. **WebGPU not requested is not a fault, and neither is WebGPU not ready
 *    yet.** A root configured for the CSS tier never had WebGPU in play;
 *    `platform.webgpu: "not-requested"` forces `activeRenderer: "css"` the same
 *    way a renderer fault would, but names no fault, so a group with nothing
 *    else wrong resolves `health: "ok"` — labeling intent as a fault would
 *    invert the honesty doctrine (X2's K1 amendment, Decision Log #21c).
 *    `"pending"` resolves identically, for the same reason read forwards: a root
 *    that asked for WebGPU and is still bringing it up has not failed at
 *    anything, and answering `no-webgpu` — whose recovery is honestly `"none"` —
 *    would be a terminal answer to a request still in flight.
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
 * 6. **A texture source with no pixels behind it is a sampling fault.** The app
 *    declared a texture and the runtime has nothing to read, so the group draws
 *    tint, rim and glow over an unsampled backdrop and says so
 *    (`no-texture-supplied`). Reporting `gpu-texture` / `true` / `exact` for a
 *    source nobody supplied is the loudest possible version of the pretence this
 *    file exists to prevent.
 */

import type { ConfiguredSource, DemotionReason, GlassGroupState } from "./state";

/**
 * Whether WebGPU is in play for this root at all, distinct from whether it
 * *works* — a root configured for the CSS tier never asks, and that is a
 * choice, not a fault (X2's K1 amendment, Decision Log #21c).
 *
 * The question is three-state on the way up, not two: between "asked for" and
 * "answered" there is a startup window in which the answer is not known yet, and
 * a host that has to publish *something* during it has only honest options if
 * the union has a name for it. `"pending"` is that name.
 */
export const WEBGPU_AVAILABILITIES = [
  "not-requested",
  "pending",
  "unavailable",
  "available",
] as const;

export type WebGPUAvailability = (typeof WEBGPU_AVAILABILITIES)[number];

/** Platform-wide probe results. platform-web produces these; core only reads them. */
export interface PlatformProbe {
  /**
   * `"available"` — a WebGPU adapter and device were obtained *and* whatever
   * draws with them is ready to paint. `"unavailable"` — WebGPU was requested
   * but no adapter, device or renderer could be had. `"pending"` — requested,
   * and the answer has not arrived yet; resolves exactly as `"not-requested"`
   * does, so a group is on the CSS tier without being demoted while the GPU tier
   * starts. `"not-requested"` — this root never asked for WebGPU at all (its
   * renderer is CSS by choice), which resolves honestly rather than as a fault.
   *
   * The two CSS-without-a-fault values resolve alike and stay tellable apart on
   * purpose: a host reads them back to distinguish "CSS by choice" from "CSS
   * while WebGPU starts", which is the difference between a final answer and a
   * provisional one.
   */
  readonly webgpu: WebGPUAvailability;
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
  /**
   * Whether pixels have actually been handed over for this source.
   *
   * `TextureBackdropSource` declares that a source *is* a texture and carries no
   * pixels — core may not know what an `HTMLCanvasElement` is (X4) — so the
   * declaration and the supply are two separate events, and a group can sit
   * between them for as long as the app takes. Only the platform layer knows
   * which side of that gap a source is on, so it folds the fact in here, exactly
   * as it folds a per-group proxy verdict into `backdropProxyConformance`
   * (Decision Log #21a).
   *
   * Optional, defaulting to `"supplied"`: core cannot see the pixels either way,
   * and a resolver that assumed absence would demote every source registered
   * through a host that does not report this at all.
   */
  readonly supply?: "supplied" | "absent";
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
  "no-texture-supplied",
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
  "no-texture-supplied": {
    trigger: "source-replaced",
    explanation:
      "The source is declared as a texture and no pixels have been handed over for it yet, so there is nothing to sample. Supply the canvas, image or video behind it — the group keeps drawing tint, rim and glow until then.",
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

  if (platform.webgpu === "unavailable") faults.add("no-webgpu");
  // A device can only be lost if there was one to lose.
  if (platform.webgpu === "available" && platform.deviceHealth === "lost") {
    faults.add("device-lost");
  }

  if (configuredSource === "texture") {
    if (inputs.source.supply === "absent") {
      // Taint and compatibility are claims *about supplied pixels*. With none
      // handed over there is nothing for them to be true or false of, so raising
      // them here would name a fault about a thing that does not exist.
      faults.add("no-texture-supplied");
    } else {
      if (inputs.source.taint === "tainted") faults.add("tainted-source");
      if (inputs.source.textureCompatibility === "incompatible") faults.add("incompatible-texture");
    }
  } else {
    if (!platform.backdropFilter) {
      faults.add("no-backdrop-filter");
    } else if (platform.backdropProxyConformance === "fail") {
      // Only meaningful where there is a filter to apply. Raising both would
      // put the group on the CSS tier (probe-failed demotes the renderer) with
      // no CSS blur to draw with — the worst of both, and the opposite of what
      // `no-backdrop-filter` is supposed to preserve.
      faults.add("probe-failed");
    }
  }

  if (governor === "demote-tier") faults.add("governor");

  return REASON_PRECEDENCE.filter((reason) => faults.has(reason));
}

/**
 * Faults that drop the renderer to the CSS tier.
 *
 * `probe-failed` is here because the spec says so outright: when the proxy
 * topology proves non-equivalent, the group demotes *to the CSS tier*
 * (§rendering contract, and S1's "its dom groups demote to the CSS tier"). That
 * is also the sensible fallback — the CSS tier applies `backdrop-filter` in
 * place and uses no proxies at all, so the very thing that failed is not on its
 * path.
 */
const RENDERER_FAULTS: readonly DemotionReason[] = [
  "no-webgpu",
  "device-lost",
  "probe-failed",
  "governor",
];

/**
 * Faults that cost the group its backdrop while the renderer keeps drawing.
 *
 * `no-backdrop-filter` is deliberately *not* a renderer fault, unlike
 * `probe-failed`: if the engine has no CSS blur at all, the CSS tier cannot draw
 * glass either, so keeping WebGPU — which can still render tint, rim and glow
 * geometrically over an unsampled backdrop — is both the higher fidelity and the
 * honest answer.
 */
const SAMPLING_FAULTS: readonly DemotionReason[] = [
  "tainted-source",
  "incompatible-texture",
  "no-texture-supplied",
  "no-backdrop-filter",
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

  // A root that never requested WebGPU — or that is still bringing it up —
  // forces the same renderer a fault would, without being one: neither names
  // anything in `faults`, so a group with no other fault reports `health: "ok"`
  // (rule 0 above).
  const cssWithoutFault =
    inputs.platform.webgpu === "not-requested" || inputs.platform.webgpu === "pending";
  const activeRenderer = cssWithoutFault || rendererDemoted ? "css" : "webgpu";

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
