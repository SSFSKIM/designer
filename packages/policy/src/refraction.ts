// The refraction ladder, and the dual-cap rule that only means something against
// it (Decision Log #19). `index.ts` carries the account of why the ladder lives
// in a package of its own rather than in core; this file is the ladder.
//
// Every declaration's doc comment below is inlined verbatim into the published
// `vitrea` and `vitrea-web` type declarations, because tsup's `dts.resolve`
// bundles this package into both. That is the reason the prose here stays on
// what a consumer of `effectiveRefraction` needs and the workspace-internal
// layering argument stays in `index.ts`, where nothing inlines it: a file
// comment only detaches from the first declaration when imports sit between
// them, and this file has no imports to sit there.

/**
 * The refraction ladder, weakest rung first.
 *
 * Two independent things cap refraction: the accessibility policy's ceiling
 * (core's `ResolvedMaterialPolicy.refraction`, a regime — `nominal | reduced |
 * none`) and the group's resolved capability state (X2's `RefractionQuality` —
 * `true | approximate | none`, what the sampling backend can actually deliver).
 * **Renderers honour the lower of the two** (Decision Log #19), which is only a
 * meaningful sentence against an ordering — this one.
 *
 * Written out rather than derived from `RefractionQuality`, because that type's
 * own declaration order is not an ordering.
 */
export const REFRACTION_LADDER = ["none", "approximate", "true"] as const;

/**
 * X2's capability-derived refraction level (`core/src/state.ts` re-exports this
 * name). Derived from the ladder so the rungs and the type cannot drift apart.
 */
export type RefractionQuality = (typeof REFRACTION_LADDER)[number];

/**
 * The accessibility *ceiling* axis — core's `ResolvedMaterialPolicy.refraction`.
 * A different vocabulary from `RefractionQuality` on purpose: one says what the
 * backend can deliver, the other what the user's preferences permit.
 */
export type RefractionRegime = "nominal" | "reduced" | "none";

/**
 * The slice of a resolved material policy the ladder reads: one axis.
 *
 * Typed as the minimum rather than as a whole policy so both tiers' fuller types
 * satisfy it structurally with no adapter — core's `ResolvedMaterialPolicy` above
 * the seam, the renderer's `MaterialPolicyView` below it.
 */
export interface RefractionPolicyView {
  readonly refraction: RefractionRegime;
}

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
export function accessibilityRefractionCap(policy: RefractionPolicyView): RefractionQuality {
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

/** How much of a depth simulation each rung allows, keyed by the ladder. */
export type RefractionScale = Readonly<Record<RefractionQuality, number>>;

/**
 * The rung scales both tiers start from.
 *
 * `approximate` is not "half of true": it is the rim-lensing approximation, a
 * shallower bend confined nearer the edge, which is what a group sampling a CSS
 * proxy can honestly claim. Reduced transparency lands here too, which is the
 * point of the ladder having three rungs and not two.
 *
 * **Advisory and calibration-delegated (C7), like every other optical constant.**
 * This is the *default*, not the running value: `@vitrea/renderer-webgpu`'s
 * `MaterialProfile.refractionScale` is what the shaders read and what
 * `withMaterialOverrides` replaces, and the CSS tier's `sourceRefractionScale`
 * merges the same patch by the same rule. The literal lives here rather than in
 * either tier because it was previously authored three times over — once in the
 * profile and twice in `platform-web/src/optics.ts` — and three copies of one
 * measured number is three chances for a calibration round to move two of them.
 */
export const DEFAULT_REFRACTION_SCALE: RefractionScale = {
  none: 0,
  approximate: 0.45,
  true: 1,
};
