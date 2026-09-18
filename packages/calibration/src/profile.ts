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
 * A native capture profile key, e.g. `apple-macos-26.5-2x-light-standard` or
 * `apple-macos-27.0-2x-light-standard-glass0.5`.
 * Every axis that can move a pixel is in the key, so a claim always names the
 * cell it was measured in.
 *
 * The trailing `-glass<amount>` token is the appearance slider macOS 27
 * introduced, and it is optional because it does not exist before 27: the key
 * `NSGlassTintAmount` is absent from every 26.x preference store, so a 26.5 key
 * with no slider token is not a key that omitted an axis, it is a key captured
 * on a system that had none (W29 G0 (d); claims §5.149 §4). On 27 the axis is
 * measured to move every cell of every arm, in both poses and at both scales,
 * far beyond the cell's own run-to-run spread — the value reaches the glass
 * filter unrounded as `inputBlurFillNormalOpacity` — so W29's contract X6, "the
 * key names every axis that moved a pixel", makes the token mandatory for a 27
 * fixture. W29 Decision Log 3 (a) rules the bed's position at the system
 * default 0.5 and puts it in the key; the charter's Design puts it **last**.
 *
 * Last, rather than beside the OS token, for two reasons that are not
 * aesthetic. The granted reference bundle must accept the key without a
 * rebuild (contract X4), and the one thing it reads out of a key is the
 * substring `-<scale>x-` (`main.swift`'s scale gate; the scheme and a11y
 * axes it takes from the profile's own declared fields) — which survives
 * either placement, so placement is decided by the readers that do parse
 * positionally. Those are this pattern and the scene matrix's own assertions,
 * and a token appended after the a11y mode leaves every earlier axis at the
 * offset a 26.5 key has it at.
 *
 * The amount is parsed as a number, so `-glass0.50` and `-glass0.5` name the
 * same position; nothing canonicalises the spelling, because a key is a literal
 * written once in `scenes.json` and reviewed there.
 */
export const PROFILE_KEY_PATTERN =
  /^apple-(?<platform>macos|ios|ipados)-(?<osVersion>\d+\.\d+)-(?<scale>\d+)x-(?<colorScheme>light|dark)-(?<a11yMode>standard|reduced-transparency|increased-contrast)(?:-glass(?<glass>\d+(?:\.\d+)?))?$/;

export interface NativeProfile {
  readonly platform: "macos" | "ios" | "ipados";
  readonly osVersion: string;
  readonly scale: number;
  readonly colorScheme: "light" | "dark";
  readonly a11yMode: "standard" | "reduced-transparency" | "increased-contrast";
  /**
   * The appearance slider's position, `NSGlassTintAmount`, when the key states
   * one. Absent on every pre-27 key, and absent rather than defaulted to the
   * system centre: a bed captured before the axis existed made no statement
   * about it, and a 0.5 invented here would read as one.
   */
  readonly glass?: number;
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
    ...(groups.glass === undefined ? {} : { glass: Number(groups.glass) }),
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
 *
 * `probe` is the fifth role and the inverse of `recorded`: a fixture the fits
 * and the claims **do** read, and that the *gate* does not. It is captured by
 * the ordinary harness run like any other cell, but no adopted bound, no
 * regression floor, no conditioning exclusion and no cross-tier coherence row
 * is ever stated over one — so a probe cell can be added, re-captured or
 * re-scoped without moving a number the frozen bed is judged by. It exists
 * because a measurement bed and a judgement bed are not the same thing: W25
 * needed the two probe grids and a coarse-pitch ladder as fitting ground for a
 * kernel width the frozen bed cannot identify at all, and folding them into the
 * gated sets would have re-partitioned the holdout to buy it (claims §5.113;
 * W25 Decision Log 3 (e)).
 */
export const FIXTURE_SETS = [
  "calibration",
  "validation",
  "holdout",
  "recorded",
  "probe",
] as const;

export type FixtureSet = (typeof FIXTURE_SETS)[number];
