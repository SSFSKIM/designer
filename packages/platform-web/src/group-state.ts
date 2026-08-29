/**
 * A group's resolved state, with its own probe verdict folded in.
 *
 * ## What this was, and what it is now
 *
 * S1 established that the backdrop-root audit must be **per group**, "not per
 * document, because different groups can sit under different ancestors". core's
 * `PlatformProbe` was scene-wide: one probe for the whole scene, handed to every
 * group by `capabilityInputs`, so a per-group `backdropProxyConformance` could
 * not be expressed through the scene at all.
 *
 * Rather than mutate core (not C5's to change) or lie by demoting every group
 * when one failed, this module used to call core's **pure** resolver directly
 * with the group's own verdict folded in, and the gap was recorded for the
 * parent rather than worked around silently: core wanted a per-group probe input
 * in the shape it already had for the governor.
 *
 * It has one now — `setPlatformProbe(probe, groupId?)`, Decision Log #23(c). So
 * the verdict lives in the scene, `scene.resolve()`'s answer and this layer's
 * answer are the same answer again, and what remains here is the *fold* itself:
 * one definition of how a verdict narrows a probe, used both when publishing the
 * group's probe into the scene and when resolving a group on demand.
 *
 * `effectiveGroupState` stays, deprecated, because it is exported and a consumer
 * may hold it. Nothing in this package calls it any more.
 */

import {
  resolveGlassGroupState,
  type CapabilityInputs,
  type GlassGroupState,
  type GovernorPressure,
  type HintAvailability,
  type PlatformProbe,
  type SourceProbe,
} from "@vitreajs/vitrea";

export type ProbeVerdict = "pass" | "fail";

/**
 * core's capability inputs for one group, over a probe that has already had the
 * group's verdict folded into it.
 *
 * Written as an intersection over a union rather than one flat shape so the
 * `configuredSource` discriminant still narrows `source` — TypeScript
 * distributes the intersection, and a flat optional `source` would let a texture
 * group be built without one.
 */
export type GroupCapabilityInputs = (
  | {
      readonly configuredSource: "texture";
      readonly source: SourceProbe;
    }
  | {
      readonly configuredSource: "dom";
      readonly source?: undefined;
    }
) & {
  readonly platform: PlatformProbe;
  readonly governor: GovernorPressure;
  readonly hint: HintAvailability;
};

/** The same, plus the verdict of *this group's* proxy audit, still unfolded. */
export type GroupStateInputs = GroupCapabilityInputs & {
  readonly probe: ProbeVerdict;
};

/**
 * One group's verdict, narrowed onto the probe it will be resolved against.
 *
 * The verdict is folded into `backdropProxyConformance` rather than applied to
 * the resolved state afterwards, so core's precedence still decides which reason
 * gets reported: a missing GPU explains a larger loss than a failed proxy audit
 * and outranks it, which is core's `REASON_PRECEDENCE` and not something to
 * re-litigate here.
 *
 * A verdict can only ever narrow. `pass` leaves the scene-wide answer alone
 * rather than raising it — a group whose own chain is intact says nothing about
 * a page-level audit that failed, and letting it overwrite one would turn a
 * per-group refinement into a per-group override.
 */
export function foldProbeVerdict(platform: PlatformProbe, verdict: ProbeVerdict): PlatformProbe {
  return {
    ...platform,
    backdropProxyConformance:
      verdict === "fail" ? "fail" : platform.backdropProxyConformance,
  };
}

/**
 * This layer's inputs as core's — the one place the `source?: undefined` arm is
 * dropped, so no caller has to restate the discriminant to satisfy core's type.
 */
export function groupCapabilityInputs(inputs: GroupCapabilityInputs): CapabilityInputs {
  return inputs.configuredSource === "texture"
    ? {
        configuredSource: "texture",
        platform: inputs.platform,
        source: inputs.source,
        governor: inputs.governor,
        hint: inputs.hint,
      }
    : {
        configuredSource: "dom",
        platform: inputs.platform,
        governor: inputs.governor,
        hint: inputs.hint,
      };
}

/**
 * Resolve one group, honouring its own probe verdict.
 *
 * @deprecated core carries the per-group probe itself now
 * (`GlassScene.setPlatformProbe(probe, groupId)`, Decision Log #23(c)). Publish
 * the group's probe into the scene and read `scene.resolve()`, or — where a
 * caller needs an answer outside a frame — fold with `foldProbeVerdict` and pass
 * `groupCapabilityInputs` to core's `resolveGlassGroupState`. This function is
 * exactly those two steps and is kept only because it is exported.
 */
export function effectiveGroupState(inputs: GroupStateInputs): GlassGroupState {
  const platform = foldProbeVerdict(inputs.platform, inputs.probe);
  const { governor, hint } = inputs;

  return resolveGlassGroupState(
    groupCapabilityInputs(
      inputs.configuredSource === "texture"
        ? { configuredSource: "texture", platform, source: inputs.source, governor, hint }
        : { configuredSource: "dom", platform, governor, hint },
    ),
  );
}
