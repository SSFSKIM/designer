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
 * That generic channel now exists (Decision Log #23(c)): core's
 * `createDiagnosticsChannel` is parameterised by its code union, and everything
 * below is an instantiation of it. What stays here is what is genuinely this
 * layer's: the code registry, the two-space union a host sees, and the console
 * sink. The dedupe rule, the retention rule and the key separator have one
 * definition in the workspace and it is core's.
 *
 * `PlatformDiagnostic` and `PlatformDiagnosticsChannel` are kept as names rather
 * than inlined at their ~30 use sites: they are the vocabulary this package's
 * modules are written in, and an alias costs nothing.
 */

import {
  createDiagnosticsChannel,
  type Diagnostic,
  type DiagnosticsChannel,
} from "@vitreajs/vitrea";

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
   * One group's padded proxy box reaches into another group's painted region
   * once the 3σ floor has been applied, so the filter runs twice over those
   * pixels. core checks proxy proximity against the *authored* padding, so only
   * this layer can see the pairs that enforcement created.
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
  /**
   * A registered host sits inside another registered host's content — the
   * material applied to both layers, which Apple names a failure. Structural and
   * registration-time; core's `same-plane-overlap` is the geometric, per-frame
   * finding about X1's sandwich and says nothing across planes. See
   * `layer-model.ts`.
   */
  "glass-inside-glass",
  /**
   * A host was registered on a content-layer element — a list or table
   * structure. "Don't use Liquid Glass in the content layer."
   */
  "glass-in-content-layer",
  /**
   * This engine version has a recorded defect, and this group's proxy chain has
   * the structure that triggers it. Advisory, never a demotion: the failure is
   * unmeasurable from inside the page, so the runtime names it and the
   * workarounds rather than guessing. See `probe/engine-defects.ts`.
   */
  "engine-known-defect",
  /**
   * An author tint was declared in a colour syntax this engine could not
   * resolve, so the surface rendered untinted. Parsing is this layer's job (the
   * value is a CSS colour and the browser is the parser), so the finding is too.
   */
  "tint-unparseable",
  /**
   * A listener registered through `GlassRoot.subscribe` threw, and was
   * unsubscribed. A listener that throws once throws every frame, so keeping it
   * would turn one adapter's bug into an unbounded storm — and, on a root whose
   * frames are driven by hand, into a throwing `runFrame`.
   */
  "frame-listener-failed",
  /**
   * A host declared four different corner radii. v1's corner algebra is
   * mirror-symmetric by construction (X8 rider 3), so the two tiers answer
   * differently and neither answer is what the app asked for — the CSS tier
   * renders the four radii through `border-radius`, and the GPU tier resolves
   * the shape against the first one.
   *
   * A finding rather than a throw: the surface still draws, and refusing a
   * registration over a corner would take a page down for a rounding. It is
   * raised **here**, at the boundary, because the only other place that notices
   * is `@vitrea/geometry`'s own refusal — which fires per frame, from inside the
   * renderer, on a shape that no longer names the call that declared it.
   */
  "non-uniform-radii",
  /**
   * A texture backdrop was supplied with no box to place it by — an
   * `ImageBitmap`, an `OffscreenCanvas`, or an element outside the document,
   * and no `placement` declared — so the GPU tier maps it over the whole
   * viewport (cover fit) rather than where its pixels are. Claims §5.47 is the
   * measured cost of that mapping. Raised once per source, at supply.
   */
  "backdrop-texture-unplaced",
] as const;

export type PlatformDiagnosticCode = (typeof PLATFORM_DIAGNOSTIC_CODES)[number];

/**
 * One platform finding. Structurally what it always was — core's `Diagnostic`
 * over this package's code space rather than core's.
 */
export type PlatformDiagnostic = Diagnostic<PlatformDiagnosticCode>;

/** What a host sees. Tagged, because the two code spaces must stay tellable apart. */
export type VitreaDiagnostic =
  | { readonly origin: "core"; readonly diagnostic: Diagnostic }
  | { readonly origin: "platform"; readonly diagnostic: PlatformDiagnostic };

export type VitreaDiagnosticSink = (diagnostic: VitreaDiagnostic) => void;

export type PlatformDiagnosticsChannel = DiagnosticsChannel<PlatformDiagnosticCode>;

/**
 * This layer's channel.
 *
 * Dedupe is not optional here, and that is the one behavioural difference from
 * core's factory rather than an oversight: every platform finding is produced by
 * a check that re-runs on registration, on mutation or per frame, so a channel
 * that repeated them would drown its own console sink. The signature stays a
 * bare sink rather than core's options bag because that is what ~30 call sites
 * in this package pass.
 */
export function createPlatformDiagnosticsChannel(
  sink?: (diagnostic: PlatformDiagnostic) => void,
): PlatformDiagnosticsChannel {
  return createDiagnosticsChannel<PlatformDiagnosticCode>({
    dedupe: true,
    ...(sink === undefined ? {} : { sink }),
  });
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
