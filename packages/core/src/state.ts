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

export type ConfiguredSource = "texture" | "dom";
export type ActiveRenderer = "webgpu" | "css";
export type SamplingBackend = "gpu-texture" | "css-backdrop" | "none";
export type RefractionQuality = "true" | "approximate" | "none";
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
}

export function isHealthy(state: GlassGroupState): boolean {
  return state.health === "ok" && state.demotionReason === undefined;
}
