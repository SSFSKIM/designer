/**
 * The dual-cap rule (Decision Log #19, ratified with C4's landing).
 *
 * Two independent things cap refraction: the accessibility policy's ceiling
 * (core's `ResolvedMaterialPolicy.refraction`, a regime — `nominal | reduced |
 * none`) and the group's resolved capability state (X2's `RefractionQuality` —
 * `true | approximate | none`, what the sampling backend can actually deliver).
 * **Renderers honour the lower of the two.** That sentence is only meaningful
 * against an ordering, so the ordering lives here, once, and both C5's CSS tier
 * and C6's shaders read it from the same place.
 */

import type { RefractionQuality, ResolvedMaterialPolicy } from "@vitreajs/vitrea";

/** Weakest first. `RefractionQuality`'s own declaration order is not an ordering. */
export const REFRACTION_LADDER = ["none", "approximate", "true"] as const satisfies readonly RefractionQuality[];

export function refractionRank(quality: RefractionQuality): number {
  return REFRACTION_LADDER.indexOf(quality);
}

/**
 * The accessibility regime as a rung on the same ladder.
 *
 * `reduced` maps to `approximate` rather than to something between: the ladder
 * has three rungs and "less refraction than true lensing" is exactly the
 * rim-lensing approximation. `nominal` maps to the top rung, which is a cap of
 * "uncapped" — it can never raise a state, only fail to lower it.
 */
export function accessibilityRefractionCap(policy: ResolvedMaterialPolicy): RefractionQuality {
  switch (policy.refraction) {
    case "nominal":
      return "true";
    case "reduced":
      return "approximate";
    case "none":
      return "none";
  }
}

/** The lower of the two caps. Symmetric — neither argument is privileged. */
export function effectiveRefraction(
  a: RefractionQuality,
  b: RefractionQuality,
): RefractionQuality {
  return refractionRank(a) <= refractionRank(b) ? a : b;
}
