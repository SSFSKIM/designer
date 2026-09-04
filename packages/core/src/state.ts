/**
 * X2 — the resolved-state model (§Backdrop & analysis contracts).
 *
 * Configuration and resolution are separate: an app *configures* a source, the
 * runtime *resolves* one of an enumerated set of states. Only enumerated states
 * are legal, every demotion names its reason, and `configuredSource` survives
 * demotion so an app can always see what it asked for versus what it got.
 *
 * C1 ships the shape; C4 ships the resolver.
 */

import type { RefractionQuality } from "@vitrea/policy";

/**
 * X2's refraction level, declared once for the whole workspace and re-exported
 * here so core's surface is what it always was.
 *
 * It moved to `@vitrea/policy` with Decision Log #23(d). The name is core's, but
 * the *ordering* of its three values — which one is "lower" when the dual cap of
 * Decision Log #19 asks — has to be legible to `@vitrea/renderer-webgpu`, and
 * that package sits below core and may never import it. A leaf below both is the
 * only module both tiers can read, so the ladder lives there and the type is
 * derived from it. Consumers see no difference: this is the same three-member
 * union under the same name, still exported from `vitrea`'s entry.
 */
export type { RefractionQuality };

export type ConfiguredSource = "texture" | "dom";
export type ActiveRenderer = "webgpu" | "css";
export type SamplingBackend = "gpu-texture" | "css-backdrop" | "none";
export type AnalysisQuality = "exact" | "hint" | "none";
export type GroupHealth = "ok" | "demoted";

export const DEMOTION_REASONS = [
  "no-webgpu",
  "no-backdrop-filter",
  "tainted-source",
  "incompatible-texture",
  "no-texture-supplied",
  "device-lost",
  "probe-failed",
  "governor",
] as const;

export type DemotionReason = (typeof DEMOTION_REASONS)[number];

export interface GlassGroupState {
  /** What the app declared — never mutated by the runtime. */
  readonly configuredSource: ConfiguredSource;
  /** What is actually drawing. */
  readonly activeRenderer: ActiveRenderer;
  readonly samplingBackend: SamplingBackend;
  readonly refraction: RefractionQuality;
  readonly analysis: AnalysisQuality;
  readonly health: GroupHealth;
  readonly demotionReason?: DemotionReason;
  /**
   * Which body the CSS tier drew for this group, where the CSS tier is the one
   * drawing (W16 G1).
   *
   * `two-layer` is the material: a sharp `backdrop-filter` and a heavy one over
   * it, mixed by the renderer's own depth ramp. `collapsed` is the declared
   * degradation the cost budget buys — the heavy layer folded into the single
   * mixed σ this tier drew before W16 — and it is named here for the same reason
   * every other field on this record is: a capture cell, a readout and a test
   * must read what actually drew rather than what was asked for. Absent on a
   * WebGPU-tier group, and on any group before the first frame has resolved one.
   *
   * Resolved by the platform rather than by core's resolver: the budget is a
   * measurement of the root's total filtered area, which core cannot see. The
   * platform folds it onto the state on the one function every consumer goes
   * through.
   */
  readonly cssBody?: "two-layer" | "collapsed";
}

export function isHealthy(state: GlassGroupState): boolean {
  return state.health === "ok" && state.demotionReason === undefined;
}
