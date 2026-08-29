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
 *
 * ## One channel, several code spaces
 *
 * The channel is generic over its code union and core's own union is only its
 * default instantiation. That is what lets the browser layer — which detects
 * things core cannot name, like a host placed outside its plane — have a code
 * space of its own without a second copy of the machinery, and it is why the
 * dedupe rule, the retention rule and the key separator have exactly one
 * definition in the workspace (Decision Log #21(b), #23(c)).
 *
 * Two properties are load-bearing and deliberately *not* generalised:
 *
 *  - **A diagnostic carries no origin tag.** Which code space a finding came
 *    from is the channel's business, added on the way out to a host's sink, not
 *    a field every emitter has to write. `platform-web`'s `layer-model.ts` is
 *    the proof: it is a pure function that takes a bare `report` callback, and
 *    an origin tag in the payload would have rewritten every emitter in it.
 *  - **`report` stays assignable to `(d) => void`.** Checkers take the
 *    capability to report, never the channel, so a module that emits findings
 *    knows nothing about retention or dedupe.
 */

export type DiagnosticSeverity = "warning" | "error";

/** Everything core can report. Owned here so a host can switch exhaustively. */
export const DIAGNOSTIC_CODES = [
  /** Two glass surfaces overlap inside one plane — the sandwich cannot express it (X1). */
  "same-plane-overlap",
  /** `regular` and `clear` nodes share one GlassGroup (§Material variants). */
  "variant-mixing",
  /** Two different author tint seeds share one GlassGroup, which is one optics pass (§Material tint). */
  "tint-mixing",
  /** A group's `mergeDistance` is below its `samplingPadding`, so proxies can double-filter (X1). */
  "merge-distance-below-padding",
  /** A group's padded proxy samples pixels a neighbouring group paints, so the filter applies twice (X1). */
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

/**
 * One finding, over whichever code space the channel was opened on.
 *
 * `Code` defaults to core's own union, so `Diagnostic` unqualified still means
 * exactly what it meant before the channel became generic and every existing
 * annotation of it still reads.
 */
export interface Diagnostic<Code extends string = DiagnosticCode> {
  readonly code: Code;
  readonly severity: DiagnosticSeverity;
  /**
   * The ids this finding is about — group, node, or source. Together with
   * `code` this is the dedupe key, so "these two nodes overlap" is one finding
   * however many frames it survives.
   */
  readonly subjects: readonly string[];
  readonly message: string;
}

export type DiagnosticSink<Code extends string = DiagnosticCode> = (
  diagnostic: Diagnostic<Code>,
) => void;

export interface DiagnosticsChannel<Code extends string = DiagnosticCode> {
  report(diagnostic: Diagnostic<Code>): void;
  /** Findings retained since construction or the last `clear()`. */
  readonly reported: readonly Diagnostic<Code>[];
  /** Forget what was seen, so a condition that returns is reported again. */
  clear(): void;
}

export interface DiagnosticsChannelOptions<Code extends string = DiagnosticCode> {
  /** Where findings go. Omitted in tests and in hosts that only read `reported`. */
  readonly sink?: DiagnosticSink<Code>;
  /** Collapse repeats of the same code+subjects. Default true. */
  readonly dedupe?: boolean;
}

/** Separator for the dedupe key — a unit separator, so no realistic id collides. */
const KEY_SEPARATOR = "␟";

const keyOf = (diagnostic: Diagnostic<string>): string =>
  [diagnostic.code, ...diagnostic.subjects].join(KEY_SEPARATOR);

export function createDiagnosticsChannel<Code extends string = DiagnosticCode>(
  options: DiagnosticsChannelOptions<Code> = {},
): DiagnosticsChannel<Code> {
  const { sink, dedupe = true } = options;
  const retained: Diagnostic<Code>[] = [];
  const seen = new Set<string>();

  return {
    report(diagnostic: Diagnostic<Code>): void {
      if (dedupe) {
        const key = keyOf(diagnostic);
        if (seen.has(key)) return;
        seen.add(key);
      }
      retained.push(diagnostic);
      sink?.(diagnostic);
    },
    get reported(): readonly Diagnostic<Code>[] {
      return retained;
    },
    clear(): void {
      retained.length = 0;
      seen.clear();
    },
  };
}
