/**
 * Platform-level findings, and one sink for both channels.
 *
 * core's `DiagnosticCode` is a closed union it owns, and rightly so — a host
 * switching on it exhaustively is the point. But the browser layer detects
 * things core cannot name: a host placed outside its plane, a padding below 3σ,
 * a proxy over the area cap, a re-rooted backdrop. Those need a code space of
 * their own rather than a widened union in core, so this module mirrors core's
 * channel with platform codes and the root fans both into a single sink.
 *
 * Recorded for the parent: making `DiagnosticsChannel` generic over its code
 * union would let both channels be one, and is the shape worth having if a
 * third package ever needs findings of its own.
 */

import type { Diagnostic, DiagnosticSeverity } from "@vitreajs/vitrea";

export const PLATFORM_DIAGNOSTIC_CODES = [
  /** A registered host is not inside its plane's host layer, so the sandwich cannot order it. */
  "host-outside-plane",
  /** The group's `samplingPadding` was below 3σ of its blur radius and was raised. */
  "sampling-padding-below-3-sigma",
  /** Raising the padding to 3σ pushed it past the group's `mergeDistance`. */
  "merge-distance-below-effective-padding",
  /** The proxy would exceed the engine's device-pixel area limit, where the filter may vanish. */
  "proxy-area-over-cap",
  /**
   * Two groups' proxies overlap once the 3σ floor has been applied. core checks
   * this against the *authored* padding, so only this layer can see the pairs
   * that enforcement created.
   */
  "proxy-overlap-after-enforcement",
  /** An ancestor of the group's proxy re-roots its backdrop; the group demoted. */
  "backdrop-root-broken",
  /** `backdrop-filter` is absent in this engine altogether. */
  "backdrop-filter-unsupported",
  /** The engine or version is not in the conformance table, so the conservative row applies. */
  "engine-unrecognised",
  /** A WebGPU device could not be obtained. */
  "webgpu-unavailable",
  /** The `GPUDevice` was lost; affected groups demoted while recovery runs. */
  "webgpu-device-lost",
  /** The renderer chunk failed to resolve, so there is no GPU tier to demote from. */
  "webgpu-renderer-load-failed",
  /** A plane's canvas refused a `"webgpu"` context, so X1's sandwich cannot be painted. */
  "webgpu-canvas-unavailable",
  /** A cross-plane promotion was requested for a node that is already there. */
  "redundant-promotion",
  /**
   * A host was registered carrying an inline `transform` vitrea did not write.
   * vitrea owns that property on a registered host and will overwrite and remove
   * it, so the app's value is destroyed rather than composed with.
   */
  "host-inline-transform",
] as const;

export type PlatformDiagnosticCode = (typeof PLATFORM_DIAGNOSTIC_CODES)[number];

export interface PlatformDiagnostic {
  readonly code: PlatformDiagnosticCode;
  readonly severity: DiagnosticSeverity;
  /** Group, node or plane ids. With `code`, the dedupe key. */
  readonly subjects: readonly string[];
  readonly message: string;
}

/** What a host sees. Tagged, because the two code spaces must stay tellable apart. */
export type VitreaDiagnostic =
  | { readonly origin: "core"; readonly diagnostic: Diagnostic }
  | { readonly origin: "platform"; readonly diagnostic: PlatformDiagnostic };

export type VitreaDiagnosticSink = (diagnostic: VitreaDiagnostic) => void;

export interface PlatformDiagnosticsChannel {
  report(diagnostic: PlatformDiagnostic): void;
  readonly reported: readonly PlatformDiagnostic[];
  clear(): void;
}

const KEY_SEPARATOR = "␟";

export function createPlatformDiagnosticsChannel(
  sink?: (diagnostic: PlatformDiagnostic) => void,
): PlatformDiagnosticsChannel {
  const retained: PlatformDiagnostic[] = [];
  const seen = new Set<string>();

  return {
    report(diagnostic) {
      const key = [diagnostic.code, ...diagnostic.subjects].join(KEY_SEPARATOR);
      if (seen.has(key)) return;
      seen.add(key);
      retained.push(diagnostic);
      sink?.(diagnostic);
    },
    get reported() {
      return retained;
    },
    clear() {
      retained.length = 0;
      seen.clear();
    },
  };
}

/**
 * The default sink: the console, in dev mode only.
 *
 * A library that logs in production is a library an app silences wholesale, and
 * a silenced channel reports nothing when it matters. So the default is loud in
 * development and mute otherwise, and an app that wants both supplies its own.
 */
export function consoleDiagnosticSink(): VitreaDiagnosticSink {
  return ({ origin, diagnostic }) => {
    const label = `[vitrea:${origin}] ${diagnostic.code}`;
    const subjects = diagnostic.subjects.length === 0 ? "" : ` (${diagnostic.subjects.join(", ")})`;
    const line = `${label}${subjects} — ${diagnostic.message}`;
    if (diagnostic.severity === "error") console.error(line);
    else console.warn(line);
  };
}
