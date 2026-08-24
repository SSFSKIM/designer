/**
 * Probe layer 3 — the per-engine conformance table, shipped as data.
 *
 * This layer records the properties that **cannot be measured at runtime**: does
 * the engine rasterise `backdrop-filter` at all, its edge mode, whether
 * reference filters work inside it, the proxy-area limit, and the 3D-transform
 * hazard. None of those are observable from inside a page — S1 closed four
 * candidate oracles with measurements, and `CSS.supports` and computed-style
 * readback both answer identically in builds that render nothing.
 *
 * ## Update path
 *
 * Every row must cite its `evidence` — a test asserts that, so a row cannot be
 * added on a hunch. Evidence comes from re-running S1's harness against the
 * engine in question:
 *
 * ```
 * cd spikes/s1-proxy-topology && npm install
 * node harness/gen-noise.mjs
 * node harness/engine-check.mjs        # does this build rasterise backdrop-filter?
 * node harness/run.mjs <engine>        # matrix + probe battery -> shots/report.json
 * ```
 *
 * `shots/report.json` is emitted in the shape these rows want; S1 recommends CI
 * generating this file from it rather than hand-maintaining it, and that remains
 * the intended end state (C9 owns the release-time gate). Until then, the rule
 * that keeps it from rotting is the one below it: **an engine or version that no
 * row covers gets `CONSERVATIVE_ROW`.** Failing closed means a stale table
 * under-promises rather than over-promises.
 *
 * Where an engine's behaviour was *not measurable* — Gecko and WebKit here,
 * where every automated capture path renders `backdrop-filter` as a no-op while
 * the engines render it live — the row says `"unverified"`. It does not say
 * `"no"`: capture-path blindness is not feature breakage (Decision Log #17), and
 * the honest record is an open gate, closed by
 * `spikes/s1-proxy-topology/pages/manual-check.html` in a real browser.
 */

export const ENGINE_FAMILIES = ["chromium", "gecko", "webkit", "unknown"] as const;

export type EngineFamily = (typeof ENGINE_FAMILIES)[number];

export interface EngineIdentity {
  readonly family: EngineFamily;
  /** Major version, or a major.minor where the engine versions that way (Safari). */
  readonly version: number;
}

export interface EngineConformanceRow {
  readonly family: EngineFamily;
  /** Inclusive lower bound of the versions this row claims to cover. */
  readonly minVersion: number;
  /** Whether the engine puts filtered pixels on screen at all. */
  readonly rasterisesBackdropFilter: "yes" | "no" | "unverified";
  /** Filter Effects 2 mandates `mirror` at the clipped border box. */
  readonly edgeMode: "mirror" | "unverified";
  /** `backdrop-filter: url(#f)` — the reserved displacement seam (Decision Log #11). */
  readonly referenceFilterInBackdrop: boolean;
  /** Device-pixel proxy area above which the filter may be dropped silently. */
  readonly maxProxyAreaDevicePx: number;
  /** Ancestor `perspective` / `preserve-3d`, which is not the plain-transform case. */
  readonly transform3dHazard: "none" | "perspective-preserve3d" | "unverified";
  /**
   * Whether the engine implements Filter Effects 2's full normative trigger set.
   * `partial` means layer 2 over-triggers there — the fail-safe direction, and
   * recorded so it can be relaxed per engine once measured.
   */
  readonly backdropRootTriggers: "normative" | "partial" | "unverified";
  /** Why each field above says what it says. Non-empty by test. */
  readonly evidence: readonly string[];
}

/**
 * The Chromium proxy-area ceiling is the **software-rasterisation** floor, not a
 * Chrome behaviour: S1 measured headless Chromium silently dropping the filter
 * between 1.75 and 3.0 Mpx of device-pixel proxy area, while retail Chrome never
 * dropped it at up to 7.20 Mpx. A page cannot tell which rasteriser it is on, so
 * the conservative number is the one that ships — and it is also the exact
 * configuration Playwright CI runs in.
 */
const CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT = 1_750_000;

export const CONFORMANCE_TABLE: readonly EngineConformanceRow[] = [
  {
    family: "chromium",
    minVersion: 113,
    rasterisesBackdropFilter: "yes",
    edgeMode: "mirror",
    referenceFilterInBackdrop: true,
    maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
    transform3dHazard: "none",
    backdropRootTriggers: "normative",
    evidence: [
      "S1: 122 capture variants across headless Chromium 151.0.7922.34 and retail Chrome 151.0.7922.172 — proxy topology confirmed byte-exact; samplingPadding >= 3σ byte-exact at blur(8px), blur(20px) and blur(40px).",
      "S1 Q5: all thirteen backdrop-root fixtures reproduce in both builds (97.77 clean / 0 re-rooted, and 97.58 / 0 in retail Chrome).",
      "S1 Q3: transform and translate3d on an ancestor are byte-identical to the untransformed case; WPT backdrop-filter-nested-3d-transform-perspective passes in Chrome.",
      "S1 Q3d: filter silently dropped above ~1.75-3.0 Mpx of device-pixel proxy area under software rasterisation; never dropped in GPU-composited retail Chrome up to 7.20 Mpx.",
      "S1 Q5: CSS.supports('backdrop-filter','url(#x)') is true in all three engines and only Chromium renders it (WebKit bug 245510, Gecko bug 1887451).",
    ],
  },
  {
    family: "gecko",
    minVersion: 103,
    rasterisesBackdropFilter: "unverified",
    edgeMode: "unverified",
    referenceFilterInBackdrop: false,
    maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
    transform3dHazard: "perspective-preserve3d",
    backdropRootTriggers: "partial",
    evidence: [
      "S1 §Environmental blocker: Firefox 153/154 renders backdrop-filter as a no-op in every capture path tried (Playwright headless and headed, retail --screenshot, WebDriver BiDi) while CSS filter, mix-blend-mode and opacity render correctly in the same images — so this machine cannot measure it, which is not the same as the engine not doing it.",
      "S1: WPT stable runs show Firefox 154 passing many backdrop-filter reftests, and -webkit-backdrop-filter has shipped for years, so live rendering is presumed functional pending the manual gate (spikes/s1-proxy-topology/pages/manual-check.html).",
      "Gecko bug 1887451: reference filters inside backdrop-filter are unsupported.",
      "Gecko bug 1816561 (open) and WPT backdrop-filter-nested-3d-transform-perspective failing in Firefox 154: ancestor perspective/preserve-3d is a live hazard.",
      "WPT backdrop-filter-backdrop-root-mask fails in Firefox 154, so an ancestor mask may not re-root there and layer 2 over-triggers — the fail-safe direction.",
    ],
  },
  {
    family: "webkit",
    minVersion: 9,
    rasterisesBackdropFilter: "unverified",
    edgeMode: "unverified",
    referenceFilterInBackdrop: false,
    maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
    transform3dHazard: "perspective-preserve3d",
    backdropRootTriggers: "partial",
    evidence: [
      "S1 §Environmental blocker: Playwright WebKit 26.5 and the system WKWebView on macOS 26.5.2 both render backdrop-filter as a no-op in every snapshot path (takeSnapshot with afterScreenUpdates, headless and headed) while the CSS filter control in the same image is correct. Real Safari 26 could not be driven at all.",
      "S1: -webkit-backdrop-filter has shipped since Safari 9 and is in wide production use; WPT stable runs show Safari 26.6 passing many backdrop-filter reftests. Live rendering is presumed functional pending the manual gate.",
      "WebKit bug 245510: reference filters inside backdrop-filter are refused.",
      "WebKit bugs 252181 and 201987 (both open): ancestor perspective/preserve-3d breaks backdrop-filter.",
      "WPT backdrop-filter-backdrop-root-mask and backdrop-filter-backdrop-root-clip-path-2 fail in Safari 26.6, so layer 2 over-triggers there — the fail-safe direction.",
    ],
  },
];

/**
 * The row an unrecognised engine, or a version below every recorded range, gets.
 * Conservative on every axis by construction, and a test holds it there.
 */
export const CONSERVATIVE_ROW: EngineConformanceRow = {
  family: "unknown",
  minVersion: 0,
  rasterisesBackdropFilter: "unverified",
  edgeMode: "unverified",
  referenceFilterInBackdrop: false,
  maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
  transform3dHazard: "unverified",
  backdropRootTriggers: "unverified",
  evidence: [
    "Not measured. S1's layer-3 design requires the runtime to fail closed: an engine or version no row covers gets the conservative answer on every axis rather than the nearest optimistic one.",
  ],
};

/**
 * Which engine family, and which version.
 *
 * Chromium is checked first because every Chromium derivative also carries
 * `Safari/537.36` in its UA string — reading Edge or Chrome as WebKit is the
 * classic sniffing mistake, and here it would hand a confirmed engine an
 * unverified row.
 */
export function detectEngine(userAgent: string): EngineIdentity {
  const chromium = /(?:Chrome|Chromium|CriOS)\/(\d+(?:\.\d+)?)/.exec(userAgent);
  if (chromium?.[1] !== undefined) {
    return { family: "chromium", version: Number.parseFloat(chromium[1]) };
  }

  const gecko = /Firefox\/(\d+(?:\.\d+)?)/.exec(userAgent);
  if (gecko?.[1] !== undefined) return { family: "gecko", version: Number.parseFloat(gecko[1]) };

  const webkit = /Version\/(\d+(?:\.\d+)?).*Safari/.exec(userAgent);
  if (webkit?.[1] !== undefined) return { family: "webkit", version: Number.parseFloat(webkit[1]) };

  // Playwright's WebKit build reports no `Version/` token in some
  // configurations; AppleWebKit without a Chromium marker is still WebKit.
  if (/AppleWebKit/.test(userAgent)) return { family: "webkit", version: 0 };

  return { family: "unknown", version: 0 };
}

/** The row for an engine, or `CONSERVATIVE_ROW`. Never undefined; never optimistic. */
export function conformanceRowFor(engine: EngineIdentity): EngineConformanceRow {
  const row = CONFORMANCE_TABLE.find(
    (candidate) => candidate.family === engine.family && engine.version >= candidate.minVersion,
  );
  return row ?? CONSERVATIVE_ROW;
}
