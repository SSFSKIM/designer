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

/** Fixtures split three ways so tuning cannot quietly become overfitting. */
export const FIXTURE_SETS = ["calibration", "validation", "holdout"] as const;

export type FixtureSet = (typeof FIXTURE_SETS)[number];
