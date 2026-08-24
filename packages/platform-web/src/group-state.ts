/**
 * A group's resolved state, with its own probe verdict folded in.
 *
 * ## Why this exists rather than being core's job
 *
 * S1 established that the backdrop-root audit must be **per group**, "not per
 * document, because different groups can sit under different ancestors". core's
 * `PlatformProbe` is scene-wide: `GlassScene.setPlatformProbe` takes one probe
 * for the whole scene and `capabilityInputs` hands it to every group, so a
 * per-group `backdropProxyConformance` cannot be expressed through the scene.
 *
 * Rather than mutate core (not this child's to change) or lie by demoting every
 * group when one fails, this module calls core's **pure** resolver directly with
 * the group's own probe verdict. Same function, same transition table, same
 * enumerated states — only the input is narrowed to the group it is about. The
 * scene still carries the scene-wide facts (WebGPU presence, device health,
 * `backdrop-filter` support, and the page-level audit that every group shares),
 * so its own resolution is right in the common case; this layer is what makes
 * the uncommon case honest instead of approximately honest.
 *
 * Recorded for the parent as a contract gap, not worked around silently: core
 * wants a per-group probe input in the shape it already has for the governor
 * (`setGovernorPressure(pressure, groupId?)`).
 */

import {
  resolveGlassGroupState,
  type CapabilityInputs,
  type GlassGroupState,
  type GovernorPressure,
  type HintAvailability,
  type PlatformProbe,
  type SourceProbe,
} from "@vitrea/core";

export type ProbeVerdict = "pass" | "fail";

/** core's capability inputs, plus the verdict of *this group's* proxy audit. */
export type GroupStateInputs = (
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
  readonly probe: ProbeVerdict;
};

/**
 * Resolve one group, honouring its own probe verdict.
 *
 * The verdict is folded into `backdropProxyConformance` rather than applied
 * afterwards, so core's precedence still decides which reason gets reported: a
 * missing GPU explains a larger loss than a failed proxy audit and outranks it,
 * which is core's `REASON_PRECEDENCE` and not something to re-litigate here.
 */
export function effectiveGroupState(inputs: GroupStateInputs): GlassGroupState {
  const platform: PlatformProbe = {
    ...inputs.platform,
    backdropProxyConformance:
      inputs.probe === "fail" ? "fail" : inputs.platform.backdropProxyConformance,
  };

  const capability: CapabilityInputs =
    inputs.configuredSource === "texture"
      ? {
          configuredSource: "texture",
          platform,
          source: inputs.source,
          governor: inputs.governor,
          hint: inputs.hint,
        }
      : {
          configuredSource: "dom",
          platform,
          governor: inputs.governor,
          hint: inputs.hint,
        };

  return resolveGlassGroupState(capability);
}
