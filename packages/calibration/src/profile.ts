/**
 * X9's native side: the profile-key grammar, the metric axes, the fixture
 * split, and the tier vocabulary.
 *
 * Fixed by C1 and unchanged by C7 — the whole point of pinning it early was
 * that fixtures, metrics and fidelity claims would end up citing the same
 * thing. C7 only moved these declarations out of the package barrel so that
 * `report.ts` can depend on them without the barrel depending back.
 */

/** Metric axes are reported separately — a shape win must never mask a material loss. */
export const METRIC_AXES = ["shape", "material", "motion", "perceptual"] as const;

export type MetricAxis = (typeof METRIC_AXES)[number];

/** Claims are stated per tier: vitrea's own shader math versus the engine's blur. */
export type FidelityTier = "texture" | "dom";

/**
 * A native capture profile key, e.g. `apple-macos-26.5-2x-light-standard`.
 * Every axis that can move a pixel is in the key, so a claim always names the
 * cell it was measured in.
 */
export const PROFILE_KEY_PATTERN =
  /^apple-(?<platform>macos|ios|ipados)-(?<osVersion>\d+\.\d+)-(?<scale>\d+)x-(?<colorScheme>light|dark)-(?<a11yMode>standard|reduced-transparency|increased-contrast)$/;

export interface NativeProfile {
  readonly platform: "macos" | "ios" | "ipados";
  readonly osVersion: string;
  readonly scale: number;
  readonly colorScheme: "light" | "dark";
  readonly a11yMode: "standard" | "reduced-transparency" | "increased-contrast";
}

/** Parse a profile key, or return null — an unparseable key is never guessed at. */
export function parseProfileKey(key: string): NativeProfile | null {
  const groups = PROFILE_KEY_PATTERN.exec(key)?.groups;
  if (!groups) return null;

  return {
    platform: groups.platform as NativeProfile["platform"],
    osVersion: groups.osVersion as string,
    scale: Number(groups.scale),
    colorScheme: groups.colorScheme as NativeProfile["colorScheme"],
    a11yMode: groups.a11yMode as NativeProfile["a11yMode"],
  };
}

/**
 * Fixture roles, so tuning cannot quietly become overfitting.
 *
 * The first three are the anti-overfitting split: fit on `calibration`, check
 * yourself on `validation`, read `holdout` once at the end.
 *
 * `recorded` is a fourth role and not a fourth set. It names a fixture that is
 * captured, committed and measurable, and that **no fit, self-check, bound or
 * claim may read** — a cell kept for the evidence it carries rather than for the
 * question it answers. It exists because a role of "in the bed, in no set" was
 * previously unsayable, so a cell that should have carried none of the three was
 * given one of them by default (claims §5.18: four `__pressed` fixtures that are
 * byte-copies of their `__rest` twins, two of them sitting in `validation` as
 * copies of `calibration` cells).
 */
export const FIXTURE_SETS = ["calibration", "validation", "holdout", "recorded"] as const;

export type FixtureSet = (typeof FIXTURE_SETS)[number];
