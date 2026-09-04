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
 * Where an engine's behaviour was *not measurable* — Gecko, and WebKit below
 * 18.6, where every automated capture path renders `backdrop-filter` as a no-op
 * while the engines render it live — the row says `"unverified"`. It does not
 * say `"no"`: capture-path blindness is not feature breakage (Decision Log
 * #17), and the honest record is an open gate, closed by
 * `spikes/s1-proxy-topology/pages/manual-check.html` in a real browser. The
 * WebKit 18.6 row is exactly such a closure: the user's labeled manual pass of
 * 2026-08-28 on retail Safari 18.6 / macOS 15.7.7 (archived in
 * `spikes/s1-proxy-topology/manual-evidence/`). Gecko's gate is still open.
 *
 * ## Defects are a second axis, and they fail the other way
 *
 * A row's conformance fields say what an engine *can* do, and an unmeasured one
 * says `"unverified"` so the runtime under-promises. A row's `defects` say what
 * a named version does *wrong* in a shape vitrea builds, and an unmeasured
 * version claims none — because a defect is an accusation, and one made without
 * evidence is noise in a channel whose value is that it only speaks when it has
 * something. The two directions are deliberate and they are not in tension: the
 * conservative answer to "does this work?" is "we do not know"; the conservative
 * answer to "is this broken?" is also "we do not know", and only one of those
 * warrants a warning. `engine-defects.ts` holds the entries and their scan.
 */

import {
  CHROMIUM_152_PATH_CLIP_NO_OP,
  CHROMIUM_PATH_CLIP_DEFECT_MIN_VERSION,
  type EngineDefect,
} from "./engine-defects";

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
  /**
   * `backdrop-filter: url(#f)`, and since W16 G1 a **fidelity dependency** rather
   * than the reserved displacement seam Decision Log #11 opened it as.
   *
   * `backdrop-filter: blur()` is an operator on the page's ENCODED values while
   * the reference's body is linear in luminance, so the CSS tier's body blurred
   * with `blur()` reads 2.4–2.8× the GPU law's residual on the thick spans at any
   * σ, share or mask. An SVG `feGaussianBlur` at
   * `color-interpolation-filters="linearRGB"` blurs in linear light and closes
   * that to 1.10–1.50× at 1x and 0.97–1.03× at 2x, and its `sRGB` sibling is
   * bit-for-bit the `blur()` form, which was the control (claims §5.71 §2). So an
   * engine whose row says `false` still draws the two-layer body — it draws it in
   * the wrong colour space, with the measured residual, which is a fidelity loss
   * and not a broken surface.
   */
  readonly referenceFilterInBackdrop: boolean;
  /**
   * Whether a `mask-image` on a `backdrop-filter` layer composes with the filter
   * — the CSS tier's depth ramp depends on it (W16 G1).
   *
   * Measured `"yes"` in Chromium 151: a uniform mask on a filtered layer is
   * **bit-identical** to the same `opacity`, and a mask of 0.8 with `opacity: 0.5`
   * is bit-identical to `opacity: 0.40`, over the material's interior (claims
   * §5.71 §1). Ten carrier spellings compose on the element; the one that does not
   * is a mask on a *wrapper*, which is a backdrop root and makes the child's
   * filter inert — which is why the tier's mask sits on the filtered layer itself.
   *
   * Fails closed, and the failure is graded rather than total: an engine at
   * `"unverified"` draws the two layers with the heavy share as one `opacity` at
   * the ramp's area mean — the body's two components without the band — because
   * sibling `opacity` on `backdrop-filter` is ordinary CSS everywhere and needs no
   * gate of its own. The band is the only thing the labeled pass unlocks.
   */
  readonly maskOnBackdropFilter: "yes" | "no" | "unverified";
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
  /**
   * Known defects in this version range that vitrea's own construction can walk
   * into — reported per group, because whether one bites depends on where the
   * application mounted the plane root. Empty on every row that has none, which
   * is the honest default: unlike the conformance fields above, an *unmeasured*
   * version claims no defect rather than a conservative one, because a defect is
   * a claim that something is broken. See `engine-defects.ts`.
   */
  readonly defects: readonly EngineDefect[];
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

/**
 * Everything the Chromium 113 row measured, which 152 did not change.
 *
 * Split out rather than duplicated so that the newer row states its *one*
 * difference and nothing else: a re-measured conformance field would then be a
 * visible edit in one place, and a row that silently drifted from its parent
 * cannot happen.
 */
const CHROMIUM_MEASURED_CONFORMANCE = {
  rasterisesBackdropFilter: "yes",
  edgeMode: "mirror",
  referenceFilterInBackdrop: true,
  maskOnBackdropFilter: "yes",
  maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
  transform3dHazard: "none",
  backdropRootTriggers: "normative",
} as const satisfies Partial<EngineConformanceRow>;

const CHROMIUM_MEASURED_EVIDENCE: readonly string[] = [
  "S1: 122 capture variants across headless Chromium 151.0.7922.34 and retail Chrome 151.0.7922.172 — proxy topology confirmed byte-exact; samplingPadding >= 3σ byte-exact at blur(8px), blur(20px) and blur(40px).",
  "S1 Q5: all thirteen backdrop-root fixtures reproduce in both builds (97.77 clean / 0 re-rooted, and 97.58 / 0 in retail Chrome).",
  "S1 Q3: transform and translate3d on an ancestor are byte-identical to the untransformed case; WPT backdrop-filter-nested-3d-transform-perspective passes in Chrome.",
  "S1 Q3d: filter silently dropped above ~1.75-3.0 Mpx of device-pixel proxy area under software rasterisation; never dropped in GPU-composited retail Chrome up to 7.20 Mpx.",
  "S1 Q5: CSS.supports('backdrop-filter','url(#x)') is true in all three engines and only Chromium renders it (WebKit bug 245510, Gecko bug 1887451).",
  "W16 G0 §0 (claims §5.71 §1), Chromium 151.0.7922.34 under the calibration harness's own recipe: maskOnBackdropFilter — a uniform mask-image on a backdrop-filter layer is bit-identical to the same opacity over the material's interior (RMS 0.000000, max 0.000000), a mask of alpha 0.80 with opacity 0.5 is bit-identical to opacity 0.40, and ten carrier spellings compose on the element while a mask on a wrapper makes the child's filter inert.",
  "W16 G0 §1.3 (claims §5.71 §2): referenceFilterInBackdrop is a fidelity dependency, not a seam — two url(#f) layers at color-interpolation-filters=linearRGB reach 1.10-1.50x of the GPU law at 1x and 0.97-1.03x at 2x on W11's probe bed, where the same law through blur() reaches 2.39-2.89x, and the sRGB sibling of the same filter is bit-for-bit the blur() form.",
];

/**
 * Rows are matched in order by `version >= minVersion`, so a **narrower range
 * has to come first** — the WebKit pair below the Chromium pair works the same
 * way. Getting this order wrong is silent: 152 would take the 113 row and the
 * defect it carries would never be seen.
 */
export const CONFORMANCE_TABLE: readonly EngineConformanceRow[] = [
  {
    family: "chromium",
    minVersion: CHROMIUM_PATH_CLIP_DEFECT_MIN_VERSION,
    ...CHROMIUM_MEASURED_CONFORMANCE,
    defects: [CHROMIUM_152_PATH_CLIP_NO_OP],
    evidence: [
      ...CHROMIUM_MEASURED_EVIDENCE,
      "Every conformance field above is the 151 row's, unchanged: the 152 regression is a defect in one construction, not a change in what the engine can do, so it is recorded as a defect rather than by downgrading a field. Downgrading `rasterisesBackdropFilter` would demote every Chromium 152 session including the overwhelming majority that never build the failing shape.",
      "The regression itself: spikes/s1-proxy-topology/chrome152-regression/REPORT.md — 12-cell x 2-build matrix, verified repro, bug report drafted (parent Decision Log #39).",
    ],
  },
  {
    family: "chromium",
    minVersion: 113,
    ...CHROMIUM_MEASURED_CONFORMANCE,
    defects: [],
    evidence: CHROMIUM_MEASURED_EVIDENCE,
  },
  {
    family: "gecko",
    minVersion: 103,
    rasterisesBackdropFilter: "unverified",
    edgeMode: "unverified",
    referenceFilterInBackdrop: false,
    maskOnBackdropFilter: "unverified",
    maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
    transform3dHazard: "perspective-preserve3d",
    backdropRootTriggers: "partial",
    defects: [],
    evidence: [
      "S1 §Environmental blocker: Firefox 153/154 renders backdrop-filter as a no-op in every capture path tried (Playwright headless and headed, retail --screenshot, WebDriver BiDi) while CSS filter, mix-blend-mode and opacity render correctly in the same images — so this machine cannot measure it, which is not the same as the engine not doing it.",
      "S1: WPT stable runs show Firefox 154 passing many backdrop-filter reftests, and -webkit-backdrop-filter has shipped for years, so live rendering is presumed functional pending the manual gate (spikes/s1-proxy-topology/pages/manual-check.html).",
      "Gecko bug 1887451: reference filters inside backdrop-filter are unsupported.",
      "Gecko bug 1816561 (open) and WPT backdrop-filter-nested-3d-transform-perspective failing in Firefox 154: ancestor perspective/preserve-3d is a live hazard.",
      "WPT backdrop-filter-backdrop-root-mask fails in Firefox 154, so an ancestor mask may not re-root there and layer 2 over-triggers — the fail-safe direction.",
      "W16 G0 §7 (contract X9): maskOnBackdropFilter stays unverified here — a mask on a filtered layer is measured only in Chromium, and no automatable capture path on this engine renders backdrop-filter at all, so section H of spikes/s1-proxy-topology/pages/manual-check.html is its only oracle. The runtime draws the two layers with the heavy share as one opacity until that pass, which is ordinary CSS on every engine.",
    ],
  },
  {
    family: "webkit",
    minVersion: 18.6,
    rasterisesBackdropFilter: "yes",
    edgeMode: "unverified",
    referenceFilterInBackdrop: false,
    maskOnBackdropFilter: "unverified",
    maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
    transform3dHazard: "perspective-preserve3d",
    backdropRootTriggers: "normative",
    defects: [],
    evidence: [
      "Manual pass, retail Safari 18.6 on macOS 15.7.7 (user, 2026-08-28), spikes/s1-proxy-topology/pages/manual-check.html — the run Decision Log #17 said was the only oracle for this engine. Screenshots: manual-evidence/2026-08-28-safari-18.6-macos-15.7.7-{c1,d1}.png. The row claims 18.6 forward under the table's convention (every row claims its floor and newer until superseded); a retail Safari 26 spot-check would tighten it and remains cheap.",
      "rasterisesBackdropFilter: the D1 control tile renders blurred, so the portaled masked proxy paints in retail WebKit — the same construct every automated capture path renders as a no-op.",
      "backdropRootTriggers: D1 fully labeled. Root-forming: opacity 0.99, filter blur(0px), filter grayscale(0), mask-image, clip-path inset(0), mix-blend-mode multiply, will-change opacity. Harmless: control, filter none, contain paint, isolation isolate, will-change transform, translate3d(0,0,0). That is exactly the Filter Effects 2 normative membership — identity filter values still re-root (the value's presence matters, not its effect) and isolation: isolate does not re-root despite creating a stacking context — so layer 2's pinned trigger list is behavior-exact here, not an over-trigger.",
      "edgeMode stays unverified deliberately: the manual page's section C measures mask extent (the padded box stands proud as a blurred halo, confirming the panel-shaped mask is load-bearing), which is not an observation of the sampling edge mode.",
      "transform3dHazard: translate3d(0,0,0) measured harmless, consistent with the hazard being specifically ancestor perspective/preserve-3d — WebKit bugs 252181 and 201987 remain open.",
      "WebKit bug 245510: reference filters inside backdrop-filter are refused (unchanged by this run).",
      "W16 G0 §7 (contract X9): maskOnBackdropFilter stays unverified here — a mask on a filtered layer is measured only in Chromium, and no automatable capture path on this engine renders backdrop-filter at all, so section H of spikes/s1-proxy-topology/pages/manual-check.html is its only oracle. The runtime draws the two layers with the heavy share as one opacity until that pass, which is ordinary CSS on every engine.",
    ],
  },
  {
    family: "webkit",
    minVersion: 9,
    rasterisesBackdropFilter: "unverified",
    edgeMode: "unverified",
    referenceFilterInBackdrop: false,
    maskOnBackdropFilter: "unverified",
    maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
    transform3dHazard: "perspective-preserve3d",
    backdropRootTriggers: "partial",
    defects: [],
    evidence: [
      "S1 §Environmental blocker: Playwright WebKit 26.5 and the system WKWebView on macOS 26.5.2 both render backdrop-filter as a no-op in every snapshot path (takeSnapshot with afterScreenUpdates, headless and headed) while the CSS filter control in the same image is correct. Real Safari 26 could not be driven at all.",
      "S1: -webkit-backdrop-filter has shipped since Safari 9 and is in wide production use; WPT stable runs show Safari 26.6 passing many backdrop-filter reftests. Live rendering is presumed functional pending the manual gate.",
      "WebKit bug 245510: reference filters inside backdrop-filter are refused.",
      "WebKit bugs 252181 and 201987 (both open): ancestor perspective/preserve-3d breaks backdrop-filter.",
      "WPT backdrop-filter-backdrop-root-mask and backdrop-filter-backdrop-root-clip-path-2 fail in Safari 26.6, so layer 2 over-triggers there — the fail-safe direction.",
      "W16 G0 §7 (contract X9): maskOnBackdropFilter stays unverified here — a mask on a filtered layer is measured only in Chromium, and no automatable capture path on this engine renders backdrop-filter at all, so section H of spikes/s1-proxy-topology/pages/manual-check.html is its only oracle. The runtime draws the two layers with the heavy share as one opacity until that pass, which is ordinary CSS on every engine.",
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
  maskOnBackdropFilter: "unverified",
  maxProxyAreaDevicePx: CHROMIUM_SOFTWARE_RASTER_AREA_LIMIT,
  transform3dHazard: "unverified",
  backdropRootTriggers: "unverified",
  defects: [],
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
