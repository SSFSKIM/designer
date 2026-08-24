/**
 * The governor's knobs.
 *
 * §Performance envelope: "The governor degrades **within** a tier first
 * (refraction resolution, adaptation cadence, edge analysis) and switches tiers
 * only with long hysteresis and cooldown." Decision Log #19 adds that intra-tier
 * degradation is **not a state change** — a group under `degrade-in-tier`
 * pressure keeps `activeRenderer: "webgpu"` and its whole resolved state.
 *
 * So the split is: **the policy lives in core, the knobs live here.** This module
 * exposes what can be turned and publishes a suggested ladder as *data*; it never
 * decides to turn anything, never reads a clock, and never applies hysteresis.
 * A governor that lived in the renderer would be a governor that could not see
 * the scene it is governing.
 *
 * ## The three knobs, weakest cost first
 *
 * 1. **`fieldFamily`** — `rsupn` → `rsup`. S2 priced this at 29% of the field's
 *    cost for a bound that degrades from 0.170 px / 2.91° to 0.574 px / 4.26°.
 *    It is the *first* step because it is one uniform and one pipeline: no
 *    resolution change, so nothing resamples and nothing shimmers as it engages.
 *    **Conditional on the f32 cross-check** (Decision Log #20) — `fieldFamily`
 *    refuses to move to `rsup` unless the check has been recorded as passing, so
 *    an unverified family cannot ship by omission.
 * 2. **`refractionResolutionScale`** — the group field and optics render at a
 *    fraction of device resolution and upsample. Quadratic saving on the two
 *    heaviest passes, and the most visible step, so it comes second.
 * 3. **`adaptationCadenceHz`** — how often analysis is reduced and read back.
 *    Cheapest of the three in visual terms because the values it feeds are
 *    already low-passed over hundreds of milliseconds; dropping the cadence
 *    mostly changes how quickly a scroll's new backdrop is noticed.
 */

export type FieldFamily = "rsupn" | "rsup";

export interface GovernorKnobs {
  /** Which pseudo-SDF family the field pass compiles. */
  readonly fieldFamily: FieldFamily;
  /** Device-resolution fraction for the field and optics passes, 0 < s <= 1. */
  readonly refractionResolutionScale: number;
  /** Analysis reduction + readback rate. 0 disables adaptation entirely. */
  readonly adaptationCadenceHz: number;
}

/**
 * Full fidelity. `adaptationCadenceHz` is core's advisory 15 Hz readback ceiling
 * (Decision Log #19) — the analysis pass has no reason to run faster than the
 * values it produces can be consumed.
 */
export const NOMINAL_GOVERNOR: GovernorKnobs = {
  fieldFamily: "rsupn",
  refractionResolutionScale: 1,
  adaptationCadenceHz: 15,
};

/**
 * The suggested intra-tier ladder, as data for core's policy to walk. Each step
 * is cumulative on the one before it, weakest visual cost first.
 */
export const GOVERNOR_LADDER: readonly GovernorKnobs[] = [
  NOMINAL_GOVERNOR,
  { fieldFamily: "rsup", refractionResolutionScale: 1, adaptationCadenceHz: 15 },
  { fieldFamily: "rsup", refractionResolutionScale: 0.75, adaptationCadenceHz: 7.5 },
  { fieldFamily: "rsup", refractionResolutionScale: 0.5, adaptationCadenceHz: 4 },
];

export interface GovernorOptions {
  /**
   * Whether family C's WGSL has been through the f32 cross-check on real
   * hardware (Decision Log #20). Default false: an unverified family must not
   * ship because nobody said no.
   */
  readonly familyCVerified?: boolean;
  readonly onChange?: (knobs: GovernorKnobs) => void;
}

export interface Governor {
  readonly knobs: GovernorKnobs;
  /** True when `fieldFamily: "rsup"` is permitted to engage. */
  readonly familyCVerified: boolean;
  set(patch: Partial<GovernorKnobs>): GovernorKnobs;
  /** Move to a rung of the suggested ladder. Out-of-range clamps to the ends. */
  setLevel(level: number): GovernorKnobs;
  reset(): GovernorKnobs;
  /** Record that the cross-check passed, unlocking family C. */
  recordFamilyCVerified(): void;
}

const clampScale = (s: number): number => Math.min(1, Math.max(0.125, s));

export function createGovernor(options: GovernorOptions = {}): Governor {
  let knobs = NOMINAL_GOVERNOR;
  let verified = options.familyCVerified ?? false;

  const apply = (next: GovernorKnobs): GovernorKnobs => {
    const family: FieldFamily = next.fieldFamily === "rsup" && !verified ? "rsupn" : next.fieldFamily;
    knobs = {
      fieldFamily: family,
      refractionResolutionScale: clampScale(next.refractionResolutionScale),
      adaptationCadenceHz: Math.max(0, next.adaptationCadenceHz),
    };
    options.onChange?.(knobs);
    return knobs;
  };

  return {
    get knobs() {
      return knobs;
    },

    get familyCVerified() {
      return verified;
    },

    set(patch) {
      return apply({ ...knobs, ...patch });
    },

    setLevel(level) {
      const index = Math.min(GOVERNOR_LADDER.length - 1, Math.max(0, Math.round(level)));
      return apply(GOVERNOR_LADDER[index] as GovernorKnobs);
    },

    reset() {
      return apply(NOMINAL_GOVERNOR);
    },

    recordFamilyCVerified() {
      verified = true;
    },
  };
}
