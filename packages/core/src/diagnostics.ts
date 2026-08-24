/**
 * The diagnostics channel — how core reports authoring problems it detects but
 * must not silently fix.
 *
 * Core is passive and DOM-free (X4), so it neither writes to a console nor
 * decides what a host does with a finding: the host supplies a sink. Findings
 * are deduplicated by default, because several of them are produced by checks
 * that run every frame (same-plane overlap, variant mixing) and a firehose is
 * worse than silence.
 *
 * Structural mistakes — an unknown id, a duplicate id, a still-referenced
 * source — are *not* diagnostics. Those throw `GlassSceneError`, because
 * continuing past them would leave a half-built scene. Diagnostics carry the
 * recoverable, per-frame, policy-level findings instead.
 */

export type DiagnosticSeverity = "warning" | "error";

/** Everything core can report. Owned here so a host can switch exhaustively. */
export const DIAGNOSTIC_CODES = [
  /** Two glass surfaces overlap inside one plane — the sandwich cannot express it (X1). */
  "same-plane-overlap",
  /** `regular` and `clear` nodes share one GlassGroup (§Material variants). */
  "variant-mixing",
  /** A group's `mergeDistance` is below its `samplingPadding`, so proxies can double-filter (X1). */
  "merge-distance-below-padding",
  /** Two groups' padded proxies cover the same pixels, so the filter applies twice (X1). */
  "group-proxy-overlap",
  /** A `clear` node has no dimming policy, so it resolved to `regular` instead. */
  "clear-variant-needs-dimming",
  /** A foreground mode the resolved state cannot support; the nearest legal mode was used. */
  "foreground-mode-illegal",
  /** A `sampled-async` rate or hysteresis outside the supported range was clamped. */
  "foreground-rate-clamped",
  /** A backdrop hint carried a luminance/complexity outside 0..1. */
  "backdrop-hint-out-of-range",
  /** Both an explicit hint and an estimator provider are configured; the explicit hint wins (X6). */
  "backdrop-hint-redundant-estimator",
  /** `reducedTransparency` is left on "system" where the platform cannot detect it. */
  "reduced-transparency-undetectable",
  /** A frame-phase operation was performed in the wrong phase. */
  "frame-phase-violation",
] as const;

export type DiagnosticCode = (typeof DIAGNOSTIC_CODES)[number];

export interface Diagnostic {
  readonly code: DiagnosticCode;
  readonly severity: DiagnosticSeverity;
  /**
   * The ids this finding is about — group, node, or source. Together with
   * `code` this is the dedupe key, so "these two nodes overlap" is one finding
   * however many frames it survives.
   */
  readonly subjects: readonly string[];
  readonly message: string;
}

export type DiagnosticSink = (diagnostic: Diagnostic) => void;

export interface DiagnosticsChannel {
  report(diagnostic: Diagnostic): void;
  /** Findings retained since construction or the last `clear()`. */
  readonly reported: readonly Diagnostic[];
  /** Forget what was seen, so a condition that returns is reported again. */
  clear(): void;
}

export interface DiagnosticsChannelOptions {
  /** Where findings go. Omitted in tests and in hosts that only read `reported`. */
  readonly sink?: DiagnosticSink;
  /** Collapse repeats of the same code+subjects. Default true. */
  readonly dedupe?: boolean;
}

/** Separator for the dedupe key — a unit separator, so no realistic id collides. */
const KEY_SEPARATOR = "␟";

const keyOf = (diagnostic: Diagnostic): string =>
  [diagnostic.code, ...diagnostic.subjects].join(KEY_SEPARATOR);

export function createDiagnosticsChannel(
  options: DiagnosticsChannelOptions = {},
): DiagnosticsChannel {
  const { sink, dedupe = true } = options;
  const retained: Diagnostic[] = [];
  const seen = new Set<string>();

  return {
    report(diagnostic: Diagnostic): void {
      if (dedupe) {
        const key = keyOf(diagnostic);
        if (seen.has(key)) return;
        seen.add(key);
      }
      retained.push(diagnostic);
      sink?.(diagnostic);
    },
    get reported(): readonly Diagnostic[] {
      return retained;
    },
    clear(): void {
      retained.length = 0;
      seen.clear();
    },
  };
}
