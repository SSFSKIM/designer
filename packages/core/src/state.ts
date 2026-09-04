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
  /**
   * Which form the CSS tier's TINT drew (W17 G1; charter Decision Log 4 (c)).
   *
   * `linear` is the exact one — an encoded overlay at the tier's floor alpha with
   * the sharp layer's linear-light filter carrying the remainder, so the composite
   * is the renderer's per pixel. `encoded` is W16's single `rgba()`, whose
   * conversion is exact at one declared backdrop level, and the tier falls back to
   * it where the linear-light filter chain's eight-bit intermediate is coarser
   * than the page's own buffer — near black, where its quantum is 2 to 13 encoded
   * codes. Reported for the same reason `cssBody` is: a readout and a capture cell
   * have to be able to read which material drew rather than which was asked for.
   */
  readonly cssTint?: "linear" | "encoded";
  /**
   * Which element the CSS tier hung this group's OUTER SHADOW on (W18 G1;
   * charter Decision Log 2 (1)).
   *
   * The tier drew the shadow as a `box-shadow` on the host until W18, and the
   * host's three filter layers are that host's children — so every surface blurred
   * its own shadow into its own body and a later host blurred its earlier
   * neighbours' shadows in too, worth +0.0032 to +0.0096 of this tier's interior
   * level where the renderer moved by 0.00000 (claims §5.77 §3). The shadow now
   * leaves the sampled backdrop by one of two carriers, and which one a group got
   * is a property of the page rather than of the material, so it is reported here
   * for the same reason `cssBody` and `cssTint` are: a capture cell, a readout and
   * a test must read what actually drew.
   *
   * `layer` is the per-surface carrier: the shadow joins L3's `box-shadow` list,
   * which paints after L1 and L2, so a surface never samples its own shadow.
   * `group` is the per-group one: every member's shadow is painted after every
   * member's filter layers by one child per member inside the group's last-painted
   * host, clipped out of every member's body. `host` is the fallback the page
   * forces — a host whose own `overflow` clips its children would clip a shadow on
   * L3 away entirely, so there the shadow stays where it was and the sampling with
   * it. A group whose members did not all land on the same carrier reports the
   * weakest of them, because the field is a statement about the group's whole
   * interior. Absent on a WebGPU-tier group and before the first frame resolves one.
   */
  readonly cssShadow?: "layer" | "group" | "host";
}

export function isHealthy(state: GlassGroupState): boolean {
  return state.health === "ok" && state.demotionReason === undefined;
}
