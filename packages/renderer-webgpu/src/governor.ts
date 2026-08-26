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
 *    **Conditional on the f32 cross-check** (Decision Log #20) — and the check
 *    has now been run, so the condition is met. See `FAMILY_C_CROSS_CHECK`.
 * 2. **`refractionResolutionScale`** — the group's **field** targets are
 *    rasterised at a fraction of device resolution, and the optics and highlight
 *    passes filter them instead of indexing them (`passes.ts`, and the
 *    `fieldUpsampled` flag both shaders branch on). Quadratic saving on the pass
 *    that evaluates the pseudo-SDF union per pixel per member, and the most
 *    visible step, so it comes second.
 *
 *    What it does **not** yet do is shrink the optics and highlight passes
 *    themselves: those still render at full device resolution into the plane
 *    canvases, because rendering them smaller means an offscreen target and a
 *    resolve pass rather than a change of extent. So rungs 2 and 3 deliver the
 *    field's quadratic saving and the cadence saving, not the full quadratic
 *    saving on both heavy passes. Recorded here rather than implied, because a
 *    ladder whose rungs are priced for savings they do not deliver is a ladder
 *    core's policy will walk too far down.
 * 3. **`adaptationCadenceHz`** — how often analysis is reduced and read back.
 *    Cheapest of the three in visual terms because the values it feeds are
 *    already low-passed over hundreds of milliseconds; dropping the cadence
 *    mostly changes how quickly a scroll's new backdrop is noticed.
 */

export type FieldFamily = "rsupn" | "rsup";

export interface GovernorKnobs {
  /** Which pseudo-SDF family the field pass compiles. */
  readonly fieldFamily: FieldFamily;
  /**
   * Device-resolution fraction the group's field targets are rasterised at,
   * 0 < s <= 1. The optics and highlight passes upsample what they read. See the
   * module note for what this does and does not save.
   */
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

/**
 * Decision Log #20's condition, and its answer.
 *
 * The spec makes family C's shipping "conditional on C6 running the f32
 * cross-check on its WGSL". C6 ran it, twice and independently:
 *
 *  - **On hardware** (`e2e/gpu/cross-check.spec.ts`, apple/metal-3): the shipped
 *    `sd_rsup` kernel against `@vitrea/geometry`'s f64 `rsupField` over 5535
 *    points on and around three shapes' contours — **3.042e-5 px max, 0.0053% of
 *    the declared 0.574 px bound.** The same run measured family D at 4.073e-5 px
 *    / 0.0240%, reproducing S2's own 4.08e-5 / 0.024% on that adapter class,
 *    which is what makes the two runs comparable at all.
 *  - **In the unit suite** (`test/f32-cross-check.test.ts`): the same arithmetic
 *    emulated in f32 through `Math.fround`, so the answer exists on a machine
 *    with no adapter. 3.523e-5 px, the same order.
 *
 * So the gate is open by default, and the option below is the opt-out rather than
 * the opt-in. What keeps that honest is that both checks run in CI and that
 * `@vitrea/geometry` fingerprints the kernel strings: editing `sd_rsup` trips the
 * fingerprint test, which says in as many words to re-run the cross-check.
 */
export const FAMILY_C_CROSS_CHECK = {
  ran: true,
  adapter: "apple/metal-3",
  points: 5535,
  maxAbsDiffPx: 3.042e-5,
  boundPx: 0.574,
} as const;

export interface GovernorOptions {
  /**
   * Whether family C's WGSL has been through the f32 cross-check (Decision Log
   * #20). Defaults to `FAMILY_C_CROSS_CHECK.ran` — see above. Pass `false` to
   * hold the governor to family D regardless.
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
  let verified = options.familyCVerified ?? FAMILY_C_CROSS_CHECK.ran;

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
