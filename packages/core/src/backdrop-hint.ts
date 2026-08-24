/**
 * X6 — the hint contract (§Backdrop & analysis contracts).
 *
 * A `dom` group has no pixels vitrea may read, so its adaptation data comes
 * from exactly one mechanism: an author-declared `backdrop` on the GlassGroup,
 * or an estimator provider that supplies the same shape. Three parallel hint
 * mechanisms were consolidated into this one on purpose (Decision Log #13).
 *
 * The word "estimator" is load-bearing. A built-in DOM estimator may read known
 * background colours and images where CORS permits, and it is documented as an
 * estimator everywhere it appears — never as pixel analysis, which vitrea does
 * not promise for arbitrary DOM and never will.
 */

import type { HintAvailability } from "./capability";
import type { DiagnosticsChannel } from "./diagnostics";

/** Coarse light/dark/mixed classification. The one field a hint must carry. */
export type BackdropTone = "light" | "dark" | "mixed";

export interface BackdropHint {
  readonly tone: BackdropTone;
  /** Relative luminance of the backdrop under the group, 0..1. */
  readonly luminance?: number;
  /** Busyness of the backdrop, 0..1 — how hard the foreground has to fight. */
  readonly complexity?: number;
}

/**
 * The provider form of the same contract. `kind` is a literal so the shape is
 * self-describing wherever it surfaces in developer tooling.
 */
export interface BackdropEstimatorProvider {
  readonly kind: "estimator";
  /** Names the estimator in diagnostics and developer output. */
  readonly id: string;
  /** Called per group. Returning `undefined` means "no opinion here". */
  estimate(groupId: string): BackdropHint | undefined;
}

export interface BackdropHintRequest {
  readonly groupId: string;
  readonly backdrop?: BackdropHint;
  readonly estimator?: BackdropEstimatorProvider;
  readonly diagnostics?: DiagnosticsChannel;
}

export interface ResolvedBackdropHint {
  readonly availability: HintAvailability;
  /** Absent exactly when `availability` is `"none"`. */
  readonly hint?: BackdropHint;
}

/**
 * Clamp a 0..1 channel, dropping a non-finite value outright: clamping NaN
 * would invent a number the author never supplied.
 */
function normalizeChannel(value: number | undefined): {
  readonly value?: number;
  readonly corrected: boolean;
} {
  if (value === undefined) return { corrected: false };
  if (!Number.isFinite(value)) return { corrected: true };
  if (value < 0) return { value: 0, corrected: true };
  if (value > 1) return { value: 1, corrected: true };
  return { value, corrected: false };
}

function normalizeHint(
  hint: BackdropHint,
  groupId: string,
  diagnostics: DiagnosticsChannel | undefined,
): BackdropHint {
  const luminance = normalizeChannel(hint.luminance);
  const complexity = normalizeChannel(hint.complexity);

  if (luminance.corrected || complexity.corrected) {
    diagnostics?.report({
      code: "backdrop-hint-out-of-range",
      severity: "warning",
      subjects: [groupId],
      message: `X6: the backdrop hint for group "${groupId}" carried a luminance or complexity outside 0..1. Both are normalised fractions; out-of-range values were clamped and non-finite ones dropped.`,
    });
  }

  return {
    tone: hint.tone,
    ...(luminance.value === undefined ? {} : { luminance: luminance.value }),
    ...(complexity.value === undefined ? {} : { complexity: complexity.value }),
  };
}

/**
 * Resolve a group's hint. An explicit `backdrop` beats an estimator: the author
 * stated a fact, the estimator guessed one. Configuring both is reported once,
 * because it usually means the author forgot they had a provider installed.
 */
export function resolveBackdropHint(request: BackdropHintRequest): ResolvedBackdropHint {
  const { groupId, backdrop, estimator, diagnostics } = request;

  if (backdrop !== undefined) {
    if (estimator !== undefined) {
      diagnostics?.report({
        code: "backdrop-hint-redundant-estimator",
        severity: "warning",
        subjects: [groupId],
        message: `X6: group "${groupId}" has both an explicit backdrop hint and the estimator "${estimator.id}". The explicit hint wins; remove one so the source of adaptation is unambiguous.`,
      });
    }
    return { availability: "author-hint", hint: normalizeHint(backdrop, groupId, diagnostics) };
  }

  const estimated = estimator?.estimate(groupId);
  if (estimated === undefined) return { availability: "none" };

  return { availability: "estimator", hint: normalizeHint(estimated, groupId, diagnostics) };
}
