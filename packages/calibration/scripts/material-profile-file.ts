/**
 * Reading a material profile document off disk, and the guard that refuses one
 * the renderer would not understand.
 *
 * Its own module rather than a section of `capture-web.ts` so the guard can be
 * pinned in the unit suite: the driver around it is browser code — it needs the
 * DOM lib and launches Chromium on import — and a key set that is only ever
 * exercised by launching a capture run is a key set whose staleness is found by
 * a failed sweep. Which is exactly how the last two gaps in it were found.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

/**
 * Every top-level key a `MaterialProfilePatch` may carry.
 *
 * Restated here on purpose, and it is the one place this tooling does hold a
 * second opinion about the renderer's shape. The reason is a measured trap: the
 * committed calibration profiles are *documents* that contain a patch under a
 * `patch` key, alongside their provenance — so handing one to `--material-profile`
 * used to produce a patch whose every key was unrecognised, which
 * `withMaterialOverrides` ignores by construction. The run then measured the
 * renderer's defaults while the cell's `capturePath` swore it had applied a
 * profile: plausible numbers, wrong configuration, and no error anywhere. Caught
 * only by re-deriving the committed matrix from clean and noticing the dark cells
 * come back at an interior mean of 0.797 where the tuned profile gives 0.069.
 *
 * So a patch that names nothing the renderer knows is refused rather than
 * applied. The failure mode this guards against is not a typo — it is a file that
 * is exactly right and one level too deep.
 */
export const MATERIAL_PATCH_KEYS = new Set([
  "optics",
  "adaptiveTintDark",
  "adaptiveTintLight",
  "adaptiveLuminanceLow",
  "adaptiveLuminanceHigh",
  "refractionScale",
  "sizeSpanMin",
  "sizeSpanMax",
  "lensSizeGainMax",
  "sizeScatterGainMax",
  "sizeOcclusionGain",
  "sizeShadowGainMax",
  // The scatter facet's frost and span curve (W11c) and the body's depth ramp
  // (W13 G1, claims 5.61): the span curve supplies the ramp's deep value and the
  // ramp is the near-contour excursion on it — the sharp share at the contour
  // and the reach at which it vanishes, each anchored at dpr 1 and dpr 2 so the
  // sweep can fit the two scales independently.
  "sizeScatterFloor",
  "sizeScatterSpanMax",
  // The body's second scale (W15 G1, claims 5.69 sections 1-2): the heavy
  // width's gain and the deep value's floor and span top, each read again at
  // dpr 2 and each defaulting to its 1x constant, so a sweep can name them as
  // axes without the 1x material moving.
  "sizeScatterGainMax2x",
  "sizeScatterFloor2x",
  "sizeScatterSpanMax2x",
  // The 2x gain's span grading (W15 G1's re-form, claims 5.70 sections 4 and 7):
  // the heavy width's gain at the top of the scatter span curve at dpr 2, which
  // the re-form's sweep names as `--axis sizeScatterGainFar2x=...`.
  "sizeScatterGainFar2x",
  "sizeScatterRampStartThin1x",
  "sizeScatterRampStartThick1x",
  "sizeScatterRampStartThin2x",
  "sizeScatterRampStartThick2x",
  "sizeScatterRampStartFar1x",
  "sizeScatterRampStartFar2x",
  "sizeScatterRampReach1xPx",
  "sizeScatterRampReach2xPx",
  // W25's three mechanisms (claims §5.113; W25 Decision Log 3). The along-side
  // field's slope is an `optics` leaf and this section does not enumerate those.
  "sizeScatterHeavyShareThick1x",
  "sizeScatterHeavyShareThick2x",
  "sizeToneLevelFar",
  // The heavy blur's width (W26; the measured cause in claims §5.116 §2 and the
  // mechanism in §5.119), inert at 0 and anchored at both scales because it is a
  // device-px quantity whose two readings do not halve into each other. G0's two
  // other candidates — a fractional pyramid level and a share of the next chain
  // level — were measured inert to the bit at dpr 1 and removed with the spike
  // (W26 Decision Log 2 (a)), so a rung naming either would silently do nothing.
  "sizeHeavyTapSigma",
  "sizeHeavyTapSigma2x",
  // The lens (W12 G2): the gain on the reference's amount law, the height and
  // amount laws themselves, the thickness they are read at, the profile's
  // extent and exponent, and the direction's ovalization with its knee.
  "lensRefractionGain",
  "lensHeightPerSpan",
  "lensHeightMax",
  "lensAmountPerSpan",
  "lensAmountMax",
  "lensThicknessReference",
  "lensExtentGain",
  "lensProfileExponent",
  "lensOvalization",
  "lensOvalizationSpanMin",
  "lensOvalizationSpanMax",
  "reducedTransparencyFrost",
  "increasedOcclusionLift",
  "strongBorderRim",
  "reducedTintAdaptation",
  // The author tint's tone map (W3) and the backdrop tone adaptation (W7). The
  // tint four were missed when they landed, so this set has been one child stale
  // since; the guard refuses rather than mis-measures, which is why it surfaced as
  // a failed sweep point instead of as plausible numbers. Added together.
  "tintShadeDark",
  "tintShadeLight",
  "tintShadeStrength",
  // The inactive endpoint's two tint terms (W27c, claims §5.130): how much of the
  // author tint's chroma survives the recede, and how much of its shade survives a
  // collapsed body. Both are `MaterialProfilePatch` keys the renderer reads and
  // the CSS tier mirrors, and the frozen receded endpoint sets both — so while
  // they were missing here, the one capture path that could have measured the
  // endpoint refused to run it.
  "tintChromaScale",
  "tintShadeCollapseRetention",
  "backdropToneMax",
  "backdropToneLow",
  "backdropToneHigh",
  "backdropToneSizeBias",
  // The transmission the collapse keeps (W24 G1): how far the collapse's target
  // moves from the group's mean backdrop colour to the per-pixel blurred sample.
  // A profile-level constant like `rimCollapsed`, and per SCALE rather than per
  // scheme — the collapsed appearance is one appearance in both schemes, and
  // what separates the rows is the width of the kernel the reference transmits
  // through, which is a different number at each scale.
  "collapseTransmission",
  // Its second anchor at dpr 2 (the same pattern as `sizeScatterGainMax2x`),
  // because one profile document serves both scales and the reference's
  // transmitted kernel is a different width at each of them.
  "collapseTransmission2x",
  // The rim that survives the collapse (W23): a profile-level constant, because
  // the collapsed appearance is one appearance in both schemes (the reference's
  // light and dark fixtures of the collapsed cells are byte-identical).
  "rimCollapsed",
  // The same rim at an author tint's full coverage (W23 G1, Decision Log 2 (c)):
  // a painted surface over black keeps a brighter rim than a bare one.
  "rimCollapsedTinted",
  // How much of an author tint's colour the rim's light is spent in (W23 G3).
  "rimTintChroma",
  // The backdrop tone response (W9): the anchors of R(encodedMean, thickness),
  // measured constants in the profile document like every other key here.
  "backdropToneAnchorX",
  "backdropToneResponseThin",
  "backdropToneResponseThick",
  "backdropToneResponseStrength",
  // The outer shadow (W8, re-read by W14 G1). One key, FIFTEEN constants under
  // it — a nested block like `strongBorderRim`, so the cascade's fit lands as
  // `{ outerShadow: { … } }` and a sweep axis names a dotted leaf inside it
  // (`--axis outerShadow.thickOcclusionAt96=0.34,0.379,0.42`). Its leaves get
  // their own guard below, because W14 G1 retired one of them and a document
  // still naming it would otherwise pass this set and render the defaults.
  "outerShadow",
  "lightDirection",
  // The lit edge's axis (W24): a profile-level constant beside `lightDirection`
  // because the rim's axis and the inner shadow's light are measured 22 degrees
  // apart, and the factor's exponent lives under `optics` with the rim's other
  // per-variant constants.
  "rimLitAxis",
  "sweepBandRadians",
  "glowRadiusCss",
  "glowGain",
  "sweepGain",
]);

/**
 * Every leaf the renderer's `MaterialOuterShadow` has.
 *
 * The nested half of the same guard. W8's `occlusion` — one span-flat amplitude
 * — is NOT here: W14 G1 replaced it with six anchors on two regimes plus the
 * lift's four constants (claims §5.62), and a saved document still naming it
 * would apply cleanly, hash itself into every cell as the configuration that
 * ran, and measure the default shadow. `withMaterialOverrides` refuses it at the
 * runtime boundary too; this refuses it here, where the file has a path and the
 * message can name it.
 */
export const OUTER_SHADOW_KEYS = new Set([
  "offsetPx",
  "sigmaPx",
  "spreadPx",
  "thinOcclusionDark",
  "thinOcclusionMid",
  "thinOcclusionBright",
  "thickOcclusionAt96",
  "thickOcclusionAt128",
  "thickOcclusionAt160",
  "liftAmplitude",
  "liftSpanMin",
  "liftSpanFull",
  "liftBlurSigmaCss",
  "reducedTransparencyOcclusion",
  "sizeGain",
]);

/**
 * Every key the CSS tier's `CssTierMapping` may be patched at (corrective K5).
 *
 * `shadowOffset`, `shadowBlur` and `shadowAlpha` were here until W8 and are not
 * any more: the outer shadow stopped being a CSS-only decoration and became a
 * material facet both tiers draw, so it moved into the renderer patch above. They
 * are removed rather than left as harmless spellings, because a key this set
 * accepts and nothing reads is exactly the silently-measured-the-defaults failure
 * the guard exists for.
 */
export const CSS_TIER_MAPPING_KEYS = new Set([
  "referenceBackdropLuminance",
  "minimumTintContrast",
  "blurSigmaScale",
  "saturation",
  "borderAlphaPerRimAlpha",
  "borderWidth",
]);

/**
 * A profile document's two sections as they came off disk, with the provenance a
 * cell has to record. The sections stay untyped here — the renderer's patch and
 * the CSS mapping types are the driver's business, and this module is the guard
 * plus the file, so that it stays Node code a unit test can import.
 */
export interface MaterialProfileSections {
  readonly path: string;
  readonly sha256: string;
  readonly patch: Record<string, unknown>;
  readonly cssTierMapping: Record<string, unknown> | undefined;
}

/**
 * Read a profile document off disk.
 *
 * Accepts either a bare renderer patch or a calibration-profile document
 * carrying one under `patch` — the committed profiles are the latter, and making
 * the caller unwrap them by hand is how the trap above gets re-set. A document
 * may also carry `cssTierMapping`, which is the CSS tier's side of the same
 * configuration; either section alone is enough to make the file a document.
 */
export function readMaterialProfileFile(path: string): MaterialProfileSections {
  const text = readFileSync(path, "utf8");
  const parsed: unknown = JSON.parse(text);
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error(`--material-profile ${path} is not a JSON object`);
  }

  const object = (value: unknown): Record<string, unknown> | undefined =>
    typeof value === "object" && value !== null && !Array.isArray(value)
      ? (value as Record<string, unknown>)
      : undefined;

  const document = parsed as Record<string, unknown>;
  // A document declares itself by carrying either section. Testing only for
  // `patch` would take a CSS-only document — one that tunes the mapping and
  // leaves the renderer at its defaults, which is exactly what a dom-tier sweep
  // writes — and treat `cssTierMapping` as an unknown renderer key.
  const isDocument = "patch" in document || "cssTierMapping" in document;
  const patch = (isDocument ? object(document["patch"]) ?? {} : document) as Record<string, unknown>;
  const cssTierMapping = isDocument ? object(document["cssTierMapping"]) : undefined;

  const reject = (section: string, keys: readonly string[], allowed: ReadonlySet<string>): void => {
    const unknown = keys.filter((key) => !allowed.has(key));
    if (unknown.length === 0) return;
    throw new Error(
      `--material-profile ${path} names ${unknown.length} key(s) ${section} does not have: ` +
        `${unknown.join(", ")}. Applying it would have silently measured the defaults. ` +
        `Known keys: ${[...allowed].join(", ")}.`,
    );
  };
  reject("the renderer's MaterialProfilePatch", Object.keys(patch), MATERIAL_PATCH_KEYS);
  const outerShadow = object(patch["outerShadow"]);
  if (outerShadow !== undefined) {
    reject("the renderer's MaterialOuterShadow", Object.keys(outerShadow), OUTER_SHADOW_KEYS);
  }
  if (cssTierMapping !== undefined) {
    reject("the CSS tier's CssTierMapping", Object.keys(cssTierMapping), CSS_TIER_MAPPING_KEYS);
  }

  if (Object.keys(patch).length === 0 && cssTierMapping === undefined) {
    throw new Error(`--material-profile ${path} is empty, so it would change nothing`);
  }

  return {
    path,
    // Hashed over the file, not the extracted sections: the cell should name the
    // artefact a human can go and read, provenance included.
    sha256: createHash("sha256").update(text).digest("hex").slice(0, 12),
    patch,
    cssTierMapping,
  };
}
