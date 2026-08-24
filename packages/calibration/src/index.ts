/**
 * @vitrea/calibration — skeleton (C1).
 *
 * X9 authority lives in the parent spec; this package owns the content. C1
 * fixes the profile-key grammar and the metric axes so C7's fixtures and C9's
 * fidelity claims cite the same thing.
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
