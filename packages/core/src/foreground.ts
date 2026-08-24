/**
 * §Foreground adaptation — the GPU → DOM data path's policy half.
 *
 * `ForegroundAdaptation = fixed | author-hint | sampled-async { rateHz,
 * hysteresis }`. The interesting part is legality: `sampled-async` needs GPU
 * classification results, so it is available only where `analysis: "exact"` —
 * "exactly", per the honesty doctrine. An illegal combination is neither
 * honoured nor silently dropped: it resolves to the nearest legal mode and the
 * downgrade is both returned and reported.
 *
 * Nothing here reads a clock or schedules anything. `rateHz` is a declared
 * cadence platform-web drives; core only validates it.
 */

import type { AnalysisQuality, GlassGroupState } from "./state";
import type { DiagnosticsChannel } from "./diagnostics";

/** The three modes, ordered most adaptive first — the order the fallback walks. */
export const FOREGROUND_MODES = ["sampled-async", "author-hint", "fixed"] as const;

export type ForegroundMode = (typeof FOREGROUND_MODES)[number];

export type ForegroundAdaptation =
  | { readonly mode: "fixed" }
  | { readonly mode: "author-hint" }
  | {
      readonly mode: "sampled-async";
      /** Readback cadence. Low-frequency by contract — never per-frame. */
      readonly rateHz: number;
      /** Threshold band, 0..1, that keeps scrolling from pumping the foreground. */
      readonly hysteresis: number;
    };

/**
 * Advisory bounds. `maxHz` exists to keep "low-frequency async readback" true
 * rather than aspirational: a quarter of a 60Hz frame budget is already far
 * more often than a foreground tone needs to change. Calibration (C7) may
 * replace these numbers; the invariant that readback is not per-frame is not
 * negotiable.
 */
export const SAMPLED_ASYNC_RATE_LIMITS = {
  minHz: 1,
  maxHz: 15,
  minHysteresis: 0.02,
  maxHysteresis: 0.5,
} as const;

/** Advisory defaults, replaced by calibration profiles (§Calibration). */
export const SAMPLED_ASYNC_DEFAULTS = { rateHz: 4, hysteresis: 0.06 } as const;

/** Which modes a state can honestly support, most adaptive first. */
function legalModes(analysis: AnalysisQuality): readonly ForegroundMode[] {
  switch (analysis) {
    case "exact":
      return FOREGROUND_MODES;
    case "hint":
      return ["author-hint", "fixed"];
    case "none":
      return ["fixed"];
  }
}

export interface ForegroundResolutionOptions {
  /**
   * What a finding is about — a group id, or a node id where a surface
   * overrides its group's mode. Also the dedupe subject, so a standing
   * downgrade is reported once rather than once per frame.
   */
  readonly subject?: string;
  readonly diagnostics?: DiagnosticsChannel;
}

export interface ResolvedForegroundAdaptation {
  readonly adaptation: ForegroundAdaptation;
  /** Present only when the requested mode was not legal for this state. */
  readonly downgraded?: { readonly from: ForegroundMode; readonly to: ForegroundMode };
}

const clamp = (value: number, min: number, max: number): number =>
  Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : min;

function validateSampled(
  requested: Extract<ForegroundAdaptation, { mode: "sampled-async" }>,
  options: ForegroundResolutionOptions,
): ForegroundAdaptation {
  const { minHz, maxHz, minHysteresis, maxHysteresis } = SAMPLED_ASYNC_RATE_LIMITS;
  const rateHz = clamp(requested.rateHz, minHz, maxHz);
  const hysteresis = clamp(requested.hysteresis, minHysteresis, maxHysteresis);

  if (rateHz !== requested.rateHz || hysteresis !== requested.hysteresis) {
    options.diagnostics?.report({
      code: "foreground-rate-clamped",
      severity: "warning",
      subjects: [options.subject ?? "*"],
      message: `Foreground sampled-async parameters were clamped to the supported range (rateHz ${minHz}..${maxHz}, hysteresis ${minHysteresis}..${maxHysteresis}). Readback is low-frequency by contract, never per-frame.`,
    });
  }

  return { mode: "sampled-async", rateHz, hysteresis };
}

/**
 * Resolve a requested mode against a resolved group state. Total: every
 * request produces a legal adaptation, because `fixed` is legal everywhere.
 */
export function resolveForegroundAdaptation(
  requested: ForegroundAdaptation,
  state: GlassGroupState,
  options: ForegroundResolutionOptions = {},
): ResolvedForegroundAdaptation {
  const legal = legalModes(state.analysis);

  if (legal.includes(requested.mode)) {
    return {
      adaptation:
        requested.mode === "sampled-async" ? validateSampled(requested, options) : requested,
    };
  }

  // Walk down from the requested mode to the first legal one. `fixed` is always
  // legal, so this cannot fall off the end.
  const from = requested.mode;
  const to = FOREGROUND_MODES.slice(FOREGROUND_MODES.indexOf(from) + 1).find((mode) =>
    legal.includes(mode),
  );
  const target: ForegroundMode = to ?? "fixed";

  options.diagnostics?.report({
    code: "foreground-mode-illegal",
    severity: "warning",
    subjects: [options.subject ?? "*"],
    message: `Foreground mode "${from}" needs a state this group does not have — sampled-async requires analysis: exact, author-hint requires a backdrop hint or estimator (X6). Resolved analysis is "${state.analysis}", so "${target}" was used instead.`,
  });

  return {
    adaptation: target === "sampled-async" ? { ...SAMPLED_ASYNC_DEFAULTS, mode: target } : { mode: target },
    downgraded: { from, to: target },
  };
}

/**
 * The mode a group gets when the app states none: adapt wherever that is
 * honest, hint where the author supplied one, fixed tones for arbitrary DOM.
 */
export function defaultForegroundAdaptation(state: GlassGroupState): ForegroundAdaptation {
  switch (state.analysis) {
    case "exact":
      return { mode: "sampled-async", ...SAMPLED_ASYNC_DEFAULTS };
    case "hint":
      return { mode: "author-hint" };
    case "none":
      return { mode: "fixed" };
  }
}
